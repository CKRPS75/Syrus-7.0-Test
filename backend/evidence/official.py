"""
Official Source Override & Verification Module.
Implements authoritative override rules for validated official transit alerts.
"""

from typing import List, Tuple, Optional
from backend.evidence.schemas import (
    GroundedEvidence,
    SourceType,
    EntityGroundingStatus,
    DisruptionStatus,
    DisruptionType,
    TrustDecision
)


class OfficialOverrideEngine:
    """Evaluates official authority alerts for direct verification or resolution."""

    OFFICIAL_DISRUPTION_TYPES = {
        DisruptionType.CANCELLATION,
        DisruptionType.SUSPENSION,
        DisruptionType.CLOSURE,
        DisruptionType.DELAY,
        DisruptionType.ACCIDENT,
        DisruptionType.MAINTENANCE,
        DisruptionType.CONGESTION
    }

    @classmethod
    def evaluate_official_override(
        cls,
        evidence_items: List[GroundedEvidence]
    ) -> Tuple[bool, Optional[TrustDecision], Optional[DisruptionStatus], Optional[str]]:
        """
        Checks if any grounded official alert overrides the Bayesian calculation.
        Returns:
            (has_override, trust_decision, lifecycle_status, reason)
        """
        # Look for the latest official items
        official_items = [
            item for item in evidence_items
            if item.extracted.source_type == SourceType.OFFICIAL
        ]

        if not official_items:
            return False, None, None, None

        # Sort by timestamp descending (most recent first)
        official_items.sort(key=lambda x: x.extracted.timestamp, reverse=True)
        latest_official = official_items[0]

        # Check entity grounding
        is_grounded = latest_official.entity_status == EntityGroundingStatus.KNOWN

        # Check if official notice announces restoration/resolution
        is_restoration = (
            latest_official.extracted.status == DisruptionStatus.RESOLVED
            or latest_official.extracted.disruption_type == DisruptionType.NORMAL_OPERATION
            or "restor" in latest_official.extracted.raw_text.lower()
            or "normal" in latest_official.extracted.raw_text.lower()
            or "cleared" in latest_official.extracted.raw_text.lower()
        )

        if is_restoration:
            return (
                True,
                TrustDecision.IGNORE,
                DisruptionStatus.RESOLVED,
                f"Official restoration notice from {latest_official.extracted.source_id}"
            )

        # Check active official disruption
        if is_grounded and latest_official.extracted.disruption_type in cls.OFFICIAL_DISRUPTION_TYPES:
            return (
                True,
                TrustDecision.CONFIRMED,
                DisruptionStatus.ACTIVE,
                f"Authoritative official alert from {latest_official.extracted.source_id} (Exact entity match)"
            )

        return False, None, None, None
