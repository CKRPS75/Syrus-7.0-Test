"""
Master Evidence & Trust Engine Pipeline.
Orchestrates raw ingestion through extraction, validation, grounding, deduplication,
independence, freshness, corroboration, contradiction, official overrides,
and Bayesian trust scoring to produce P3-compatible Disruption Events.
"""

import os
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from backend.evidence.schemas import (
    RawEvidenceInput,
    ExtractedEvidence,
    GroundedEvidence,
    EvidenceProvenance,
    DisruptionEvent,
    ProcessEvidenceResponse,
    TrustDecision
)
from backend.evidence.validator import EvidenceValidator
from backend.evidence.extractor import EvidenceExtractor
from backend.evidence.grounding import MumbaiGroundingEngine
from backend.evidence.dedup import DeduplicationEngine
from backend.evidence.independence import IndependenceEngine
from backend.evidence.trust import TrustEngine
from backend.evidence.event import EventLifecycleManager


class EvidencePipeline:
    """End-to-end evidence processing pipeline for Person 2."""

    def __init__(
        self,
        config_path: Optional[str] = None,
        reference_path: Optional[str] = None,
        prompt_path: Optional[str] = None
    ):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        self.config_path = config_path or os.getenv("TRUST_CONFIG_PATH") or os.path.join(base_dir, "config", "trust.json")
        self.reference_path = reference_path or os.getenv("REFERENCE_DATA_PATH") or os.path.join(base_dir, "data", "mumbai_reference.json")
        self.prompt_path = prompt_path or os.getenv("PROMPT_PATH") or os.path.join(base_dir, "prompts", "evidence_extraction.txt")

        # Load config
        self.config = self._load_config()

        # Initialize subcomponents
        self.extractor = EvidenceExtractor(prompt_path=self.prompt_path, reference_path=self.reference_path)
        self.grounding = MumbaiGroundingEngine(reference_path=self.reference_path)
        
        dedup_window = self.config.get("time_windows_minutes", {}).get("event_dedup_window", 60)
        self.dedup = DeduplicationEngine(dedup_window_minutes=dedup_window)
        
        burst_window = self.config.get("time_windows_minutes", {}).get("copy_ring_burst_window", 10)
        self.independence = IndependenceEngine(burst_window_minutes=burst_window)
        
        self.trust_engine = TrustEngine(self.config)
        
        expiry_minutes = self.config.get("time_windows_minutes", {}).get("event_expiry_minutes", 180)
        self.lifecycle_mgr = EventLifecycleManager(expiry_minutes=expiry_minutes)

        # In-memory store for provenance and final events
        self.provenance_store: Dict[str, List[EvidenceProvenance]] = {}  # event_id -> list of provenance
        self.events_store: Dict[str, DisruptionEvent] = {}

    def _load_config(self) -> Dict[str, Any]:
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "version": "1.0.0",
            "prior_logit": -2.1972245773362196,
            "crowd_evidence_cap": 2.6,
            "weights": {
                "official_exact": 2.5,
                "official_partial": 1.5,
                "independent_news": 1.2,
                "independent_crowd": 0.8,
                "additional_independent_crowd": 0.8,
                "location_time_consistency": 0.5,
                "credible_contradiction": -1.2,
                "weak_ungroundable": -2.0
            },
            "thresholds": {"ignore_max": 0.30, "confirmed_min": 0.65}
        }

    def get_config_hash(self) -> str:
        """Returns SHA-256 hash of trust configuration for reproducibility auditing."""
        config_str = json.dumps(self.config, sort_keys=True)
        return hashlib.sha256(config_str.encode("utf-8")).hexdigest()

    def process_evidence(
        self,
        raw_input: RawEvidenceInput,
        reference_now: Optional[datetime] = None
    ) -> ProcessEvidenceResponse:
        """
        Executes complete Person 2 pipeline for a single incoming evidence item.
        """
        ref_now = reference_now or raw_input.timestamp

        # 1. LLM / NLP Extraction
        extracted = self.extractor.extract(raw_input)

        # 2. Pydantic Validation
        is_valid, validated_extracted, err = EvidenceValidator.validate_extracted_evidence(extracted.model_dump())
        if not is_valid or not validated_extracted:
            raise ValueError(f"Extracted evidence validation failed: {err}")

        # 3 & 4. Entity & Time Grounding
        grounded = self.grounding.ground_evidence(validated_extracted, reference_now=ref_now)

        # 5. Deduplication & Cluster Assignment
        event_id, cluster, is_new_event = self.dedup.assign_event(grounded)

        # 6. Independence & Copy-Ring Check
        existing_items = cluster.evidence_items[:-1]
        provenance = self.independence.evaluate_independence(grounded, existing_items)

        if event_id not in self.provenance_store:
            self.provenance_store[event_id] = []
        self.provenance_store[event_id].append(provenance)

        # 7, 8, 9, 10. Freshness, Corroboration, Contradiction, Official Override & Trust Score
        all_cluster_items = cluster.evidence_items
        all_provenance = self.provenance_store[event_id]
        
        trust_result = self.trust_engine.calculate_trust(all_cluster_items, all_provenance)

        # 11. Event Lifecycle & P3 Event Object
        p3_event = self.lifecycle_mgr.build_p3_event(
            event_id=event_id,
            evidence_items=all_cluster_items,
            provenance_records=all_provenance,
            trust_result=trust_result,
            reference_now=ref_now
        )
        self.events_store[event_id] = p3_event

        return ProcessEvidenceResponse(
            event_id=event_id,
            status=trust_result.decision,
            lifecycle_status=p3_event.status,
            confidence_score=trust_result.confidence_score,
            severity=p3_event.severity,
            location=p3_event.location,
            route_id=p3_event.route_id,
            event=p3_event
        )

    def process_raw_dict(self, data: Dict[str, Any], reference_now: Optional[datetime] = None) -> Dict[str, Any]:
        """Convenience method for FastAPI and JSON payloads."""
        is_valid, validated_raw, err = EvidenceValidator.validate_raw_input(data)
        if not is_valid or not validated_raw:
            raise ValueError(f"Invalid input data: {err}")
        response = self.process_evidence(validated_raw, reference_now=reference_now)
        return response.model_dump(mode="json")

    def get_event(self, event_id: str) -> Optional[DisruptionEvent]:
        return self.events_store.get(event_id)

    def get_all_events(self) -> List[DisruptionEvent]:
        return list(self.events_store.values())

    def reset(self) -> None:
        """Resets cluster state and stored events (for tests and benchmarks)."""
        self.dedup.reset()
        self.provenance_store.clear()
        self.events_store.clear()
