"""
Unit tests for Official Alert Override and Restoration Processing.
"""

from datetime import datetime, timezone
from backend.evidence.schemas import (
    ExtractedEvidence,
    GroundedEvidence,
    SourceType,
    Severity,
    DisruptionType,
    DisruptionStatus,
    EntityGroundingStatus,
    TimeGroundingStatus,
    TrustDecision
)
from backend.evidence.official import OfficialOverrideEngine


def test_official_active_alert_override():
    extracted = ExtractedEvidence(
        source_id="WR_OFFICIAL_01",
        source_type=SourceType.OFFICIAL,
        raw_text="Western Railway: Signal failure at Dadar. Fast trains suspended.",
        location="Dadar",
        route_id="SUB_WESTERN",
        stop_id="DADAR",
        disruption_type=DisruptionType.SUSPENSION,
        severity=Severity.HIGH,
        timestamp=datetime.now(timezone.utc),
        status=DisruptionStatus.ACTIVE
    )
    grounded = GroundedEvidence(
        extracted=extracted,
        entity_status=EntityGroundingStatus.KNOWN,
        time_status=TimeGroundingStatus.GROUNDED,
        grounded_location="Dadar",
        grounded_route_id="SUB_WESTERN",
        grounded_stop_id="DADAR"
    )

    has_override, decision, lifecycle, reason = OfficialOverrideEngine.evaluate_official_override([grounded])
    assert has_override is True
    assert decision == TrustDecision.CONFIRMED
    assert lifecycle == DisruptionStatus.ACTIVE
    assert "Exact entity match" in reason


def test_official_restoration_notice_override():
    extracted = ExtractedEvidence(
        source_id="MMOPL_OFFICIAL_RESTORE",
        source_type=SourceType.OFFICIAL,
        raw_text="Mumbai Metro One: Snag rectified at Andheri. Services restored to normal schedule.",
        location="Andheri",
        route_id="METRO_1",
        stop_id="ANDHERI",
        disruption_type=DisruptionType.NORMAL_OPERATION,
        severity=Severity.LOW,
        timestamp=datetime.now(timezone.utc),
        status=DisruptionStatus.RESOLVED
    )
    grounded = GroundedEvidence(
        extracted=extracted,
        entity_status=EntityGroundingStatus.KNOWN,
        time_status=TimeGroundingStatus.GROUNDED,
        grounded_location="Andheri",
        grounded_route_id="METRO_1",
        grounded_stop_id="ANDHERI"
    )

    has_override, decision, lifecycle, reason = OfficialOverrideEngine.evaluate_official_override([grounded])
    assert has_override is True
    assert decision == TrustDecision.IGNORE
    assert lifecycle == DisruptionStatus.RESOLVED
    assert "restoration notice" in reason
