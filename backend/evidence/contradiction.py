"""
Contradiction Detection Module.
Detects conflicting reports (e.g., disruption vs normal operations/restoration claims)
and computes contradiction penalties.
"""

from typing import List, Tuple
from backend.evidence.schemas import GroundedEvidence, DisruptionType, DisruptionStatus


NORMAL_OPERATION_KEYWORDS = {
    "normal", "operating normally", "on time", "all clear", "running smoothly",
    "cleared", "restored", "no delay", "no issues", "regular schedule"
}


class ContradictionEngine:
    """Identifies contradictory evidence within an incident cluster."""

    @staticmethod
    def is_normal_operation_report(item: GroundedEvidence) -> bool:
        """Determines if the report claims normal service or resolution."""
        if item.extracted.disruption_type == DisruptionType.NORMAL_OPERATION:
            return True
        if item.extracted.status == DisruptionStatus.RESOLVED:
            return True
        text = item.extracted.raw_text.lower()
        return any(kw in text for kw in NORMAL_OPERATION_KEYWORDS)

    @classmethod
    def evaluate_contradictions(
        cls,
        evidence_items: List[GroundedEvidence]
    ) -> Tuple[bool, List[str]]:
        """
        Checks if the cluster contains both active disruption reports and normal operation reports.
        Returns (has_contradiction, contradiction_descriptions).
        """
        disruption_reports = []
        normal_reports = []

        for item in evidence_items:
            if cls.is_normal_operation_report(item):
                normal_reports.append(item)
            else:
                disruption_reports.append(item)

        if disruption_reports and normal_reports:
            notes = [
                f"Contradiction detected: {len(disruption_reports)} disruption report(s) "
                f"conflict with {len(normal_reports)} normal operation report(s)."
            ]
            return True, notes

        return False, []
