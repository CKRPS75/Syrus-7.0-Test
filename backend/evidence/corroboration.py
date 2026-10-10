"""
Corroboration & Evidence Aggregation Module.
Filters evidence by provenance, applies freshness decay, and evaluates
multi-source consistency bonuses without double-counting copy-rings.
"""

from typing import List, Dict, Tuple
from backend.evidence.schemas import (
    GroundedEvidence,
    EvidenceProvenance,
    SourceType,
    EntityGroundingStatus,
    TimeGroundingStatus,
    IndependenceType
)
from backend.evidence.freshness import FreshnessEngine


class CorroborationEngine:
    """Aggregates evidence weights based on provenance, freshness, and consistency."""

    def __init__(self, freshness_engine: FreshnessEngine, weights_config: Dict[str, float]):
        self.freshness = freshness_engine
        self.weights = weights_config

    def aggregate_evidence_weights(
        self,
        evidence_items: List[GroundedEvidence],
        provenance_records: List[EvidenceProvenance]
    ) -> Tuple[float, float, Dict[str, float], int]:
        """
        Calculates total crowd weight (before cap) and total non-crowd weight.
        Returns:
            (crowd_weight_sum, non_crowd_weight_sum, detailed_weights, independent_source_count)
        """
        crowd_sum = 0.0
        non_crowd_sum = 0.0
        detailed_weights: Dict[str, float] = {}

        independent_crowd_count = 0
        independent_sources_seen = set()

        for idx, item in enumerate(evidence_items):
            src_id = item.extracted.source_id
            src_type = item.extracted.source_type
            prov = provenance_records[idx] if idx < len(provenance_records) else None
            indep_status = prov.independence if prov else IndependenceType.INDEPENDENT

            # Ungroundable check
            if item.entity_status == EntityGroundingStatus.UNKNOWN or item.time_status == TimeGroundingStatus.UNGROUNDABLE:
                w_ungroundable = self.weights.get("weak_ungroundable", -2.0)
                detailed_weights[f"{src_id}_ungroundable"] = w_ungroundable
                if src_type == SourceType.CROWD:
                    crowd_sum += w_ungroundable
                else:
                    non_crowd_sum += w_ungroundable
                continue

            # Apply Redundancy Theorem: Copy-rings and duplicate echoes receive a redundancy discount / penalty
            if indep_status in (IndependenceType.COPY_DERIVED, IndependenceType.DUPLICATE):
                w_redundant = self.weights.get("redundant_duplicate_penalty", -0.4)
                detailed_weights[f"{src_id}_redundant_duplicate"] = w_redundant
                if src_type == SourceType.CROWD:
                    crowd_sum += w_redundant
                else:
                    non_crowd_sum += w_redundant
                continue

            # This is an independent report
            independent_sources_seen.add(src_id)

            if src_type == SourceType.OFFICIAL:
                base_w = self.weights.get("official_exact", 2.5) if item.entity_status == EntityGroundingStatus.KNOWN else self.weights.get("official_partial", 1.5)
                decayed_w = self.freshness.calculate_decayed_weight(base_w, src_type, item.age_minutes)
                detailed_weights[f"{src_id}_official"] = round(decayed_w, 4)
                non_crowd_sum += decayed_w

            elif src_type == SourceType.NEWS:
                base_w = self.weights.get("independent_news", 1.2)
                decayed_w = self.freshness.calculate_decayed_weight(base_w, src_type, item.age_minutes)
                detailed_weights[f"{src_id}_news"] = round(decayed_w, 4)
                non_crowd_sum += decayed_w

            elif src_type == SourceType.CROWD:
                independent_crowd_count += 1
                base_w = self.weights.get("independent_crowd", 0.8) if independent_crowd_count == 1 else self.weights.get("additional_independent_crowd", 0.8)
                decayed_w = self.freshness.calculate_decayed_weight(base_w, src_type, item.age_minutes)
                detailed_weights[f"{src_id}_crowd_{independent_crowd_count}"] = round(decayed_w, 4)
                crowd_sum += decayed_w

        # Location/Time Consistency Bonus
        if len(independent_sources_seen) >= 2:
            bonus = self.weights.get("location_time_consistency", 0.5)
            # If all are crowd, add to crowd sum; otherwise non-crowd sum
            if independent_crowd_count == len(independent_sources_seen):
                crowd_sum += bonus
                detailed_weights["crowd_consistency_bonus"] = bonus
            else:
                non_crowd_sum += bonus
                detailed_weights["multi_source_consistency_bonus"] = bonus

        return crowd_sum, non_crowd_sum, detailed_weights, len(independent_sources_seen)
