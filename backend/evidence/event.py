"""
Disruption Event Lifecycle & P3 Contract Formatter.
Manages event status transitions (ACTIVE, RESOLVED, EXPIRED) and constructs
the final DisruptionEvent payload consumed by Person 3 (Impact Engine).
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional
from backend.evidence.schemas import (
    DisruptionEvent,
    DisruptionStatus,
    TrustDecision,
    GroundedEvidence,
    EvidenceProvenance,
    IndependenceType,
    SourceType,
    TrustScoreResult
)


class EventLifecycleManager:
    """Manages event lifecycles and builds compliant P3 Event contracts."""

    def __init__(self, expiry_minutes: int = 180):
        self.expiry_minutes = expiry_minutes

    def determine_lifecycle_status(
        self,
        evidence_items: List[GroundedEvidence],
        reference_now: Optional[datetime] = None
    ) -> DisruptionStatus:
        """
        Determines if the event is ACTIVE, RESOLVED, or EXPIRED.
        """
        if not evidence_items:
            return DisruptionStatus.EXPIRED

        now = reference_now or datetime.now(timezone.utc)

        # Check if latest official or strong report states RESOLVED / NORMAL_OPERATION
        sorted_items = sorted(evidence_items, key=lambda x: x.extracted.timestamp, reverse=True)
        latest = sorted_items[0]

        if latest.extracted.status == DisruptionStatus.RESOLVED:
            return DisruptionStatus.RESOLVED
        if latest.extracted.disruption_type.value == "NORMAL_OPERATION":
            return DisruptionStatus.RESOLVED

        # Check for expiry based on last update age
        last_time = latest.extracted.timestamp
        if last_time.tzinfo is None and now.tzinfo is not None:
            now = now.replace(tzinfo=None)
        elif last_time.tzinfo is not None and now.tzinfo is None:
            last_time = last_time.replace(tzinfo=None)

        age_since_last_update = (now - last_time).total_seconds() / 60.0
        if age_since_last_update > self.expiry_minutes:
            return DisruptionStatus.EXPIRED

        return DisruptionStatus.ACTIVE

    def build_p3_event(
        self,
        event_id: str,
        evidence_items: List[GroundedEvidence],
        provenance_records: List[EvidenceProvenance],
        trust_result: TrustScoreResult,
        reference_now: Optional[datetime] = None
    ) -> DisruptionEvent:
        """
        Constructs the authoritative DisruptionEvent payload for Person 3.
        """
        lifecycle = self.determine_lifecycle_status(evidence_items, reference_now)

        # Determine dominant attributes
        sorted_by_time = sorted(evidence_items, key=lambda x: x.extracted.timestamp)
        valid_from = sorted_by_time[0].extracted.timestamp
        valid_until = valid_from + timedelta(minutes=self.expiry_minutes)

        # Select best grounded location and route
        location = None
        route_id = None
        stop_id = None
        disruption_type = sorted_by_time[-1].extracted.disruption_type
        severity = sorted_by_time[-1].extracted.severity

        for item in reversed(sorted_by_time):
            if item.grounded_location and not location:
                location = item.grounded_location
            if item.grounded_route_id and not route_id:
                route_id = item.grounded_route_id
            if item.grounded_stop_id and not stop_id:
                stop_id = item.grounded_stop_id
            if item.extracted.severity.value != "UNKNOWN":
                severity = item.extracted.severity

        # Build evidence summaries
        evidence_summaries = []
        raw_ids = []
        indep_count = 0

        prov_map = {p.source_id: p for p in provenance_records}
        for item in evidence_items:
            src_id = item.extracted.source_id
            raw_ids.append(src_id)
            src_type = item.extracted.source_type
            prov = prov_map.get(src_id)
            indep_status = prov.independence.value if prov else "independent"

            if indep_status == IndependenceType.INDEPENDENT.value:
                indep_count += 1
                evidence_summaries.append(f"Independent {src_type.value} report ({src_id})")
            elif indep_status == IndependenceType.COPY_DERIVED.value:
                evidence_summaries.append(f"Copy-derived report ({src_id})")
            elif indep_status == IndependenceType.DUPLICATE.value:
                evidence_summaries.append(f"Duplicate report ({src_id})")
            else:
                evidence_summaries.append(f"{src_type.value.capitalize()} report ({src_id})")

        return DisruptionEvent(
            event_id=event_id,
            status=lifecycle,
            decision=trust_result.decision,
            location=location,
            route_id=route_id,
            stop_id=stop_id,
            disruption_type=disruption_type,
            severity=severity,
            confidence_score=trust_result.confidence_score,
            valid_from=valid_from,
            valid_until=valid_until,
            evidence_count=len(evidence_items),
            independent_sources=indep_count,
            evidence_summary=evidence_summaries,
            raw_evidence_ids=raw_ids
        )
