"""
Trust Engine & Bayesian Scoring Module.
Calculates the uncalibrated confidence score P* using logit accumulation,
applies the strict crowd-only cap (+2.6), and assigns decision thresholds.
"""

import math
from typing import Dict, Any, List, Tuple
from backend.evidence.schemas import (
    GroundedEvidence,
    EvidenceProvenance,
    TrustDecision,
    TrustScoreResult
)
from backend.evidence.freshness import FreshnessEngine
from backend.evidence.corroboration import CorroborationEngine
from backend.evidence.contradiction import ContradictionEngine
from backend.evidence.official import OfficialOverrideEngine


class TrustEngine:
    """Calculates evidence weights, enforces crowd-only cap, and produces Trust Decisions."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.prior_logit = config.get("prior_logit", -2.1972245773362196)
        self.crowd_cap = config.get("crowd_evidence_cap", 2.6)
        self.weights = config.get("weights", {})
        self.thresholds = config.get("thresholds", {
            "ignore_max": 0.30,
            "watch_max": 0.65,
            "confirmed_min": 0.65
        })

        decay_lambdas = config.get("freshness_decay_lambda_per_minute", {})
        self.freshness = FreshnessEngine(decay_lambdas=decay_lambdas)
        self.corroboration = CorroborationEngine(self.freshness, self.weights)

    def calculate_trust(
        self,
        evidence_items: List[GroundedEvidence],
        provenance_records: List[EvidenceProvenance]
    ) -> TrustScoreResult:
        """
        Executes full trust score calculation across grouped evidence items.
        """
        if not evidence_items:
            # Baseline prior with no evidence
            p_star = 1.0 / (1.0 + math.exp(-self.prior_logit))
            return TrustScoreResult(
                prior_logit=self.prior_logit,
                crowd_evidence_sum=0.0,
                crowd_cap_applied=False,
                total_logit=self.prior_logit,
                confidence_score=round(p_star, 4),
                decision=TrustDecision.IGNORE,
                evidence_weights={},
                contradiction_detected=False,
                official_override=False
            )

        # 1. Check Official Override
        has_override, override_dec, override_status, reason = OfficialOverrideEngine.evaluate_official_override(evidence_items)
        if has_override and override_dec == TrustDecision.CONFIRMED:
            return TrustScoreResult(
                prior_logit=self.prior_logit,
                crowd_evidence_sum=0.0,
                crowd_cap_applied=False,
                total_logit=4.0,  # High certainty
                confidence_score=0.98,
                decision=TrustDecision.CONFIRMED,
                evidence_weights={"official_override": 4.0},
                contradiction_detected=False,
                official_override=True
            )
        elif has_override and override_dec == TrustDecision.IGNORE:
            return TrustScoreResult(
                prior_logit=self.prior_logit,
                crowd_evidence_sum=0.0,
                crowd_cap_applied=False,
                total_logit=-4.0,
                confidence_score=0.02,
                decision=TrustDecision.IGNORE,
                evidence_weights={"official_restoration": -4.0},
                contradiction_detected=False,
                official_override=True
            )

        # 2. Corroboration & Freshness Weights Aggregation
        crowd_sum, non_crowd_sum, detailed_weights, indep_count = self.corroboration.aggregate_evidence_weights(
            evidence_items, provenance_records
        )

        # 3. Apply Crowd-Only Evidence Cap (+2.6)
        crowd_cap_applied = crowd_sum > self.crowd_cap
        effective_crowd_sum = min(crowd_sum, self.crowd_cap) if crowd_sum > 0 else crowd_sum

        # 4. Check for Contradictions
        has_contradiction, contra_notes = ContradictionEngine.evaluate_contradictions(evidence_items)
        contradiction_penalty = 0.0
        if has_contradiction:
            contradiction_penalty = self.weights.get("credible_contradiction", -1.2)
            detailed_weights["credible_contradiction_penalty"] = contradiction_penalty

        # 5. Logit Accumulation: L = L0 + crowd_capped_sum + non_crowd_sum + contradiction_penalty
        total_logit = self.prior_logit + effective_crowd_sum + non_crowd_sum + contradiction_penalty

        # 6. Uncalibrated Confidence Score: P* = 1 / (1 + exp(-L))
        # Clamp logit to prevent math overflow
        clamped_logit = max(min(total_logit, 30.0), -30.0)
        p_star = 1.0 / (1.0 + math.exp(-clamped_logit))

        # 7. Decision Threshold Mapping
        if p_star < self.thresholds.get("ignore_max", 0.30):
            decision = TrustDecision.IGNORE
        elif p_star < self.thresholds.get("confirmed_min", 0.65):
            decision = TrustDecision.WATCH
        else:
            decision = TrustDecision.CONFIRMED

        return TrustScoreResult(
            prior_logit=self.prior_logit,
            crowd_evidence_sum=round(crowd_sum, 4),
            crowd_cap_applied=crowd_cap_applied,
            total_logit=round(total_logit, 4),
            confidence_score=round(p_star, 4),
            decision=decision,
            evidence_weights=detailed_weights,
            contradiction_detected=has_contradiction,
            official_override=False
        )
