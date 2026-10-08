"""
Unit tests for Mumbai Entity and Temporal Grounding.
"""

from datetime import datetime, timezone, timedelta
from backend.evidence.schemas import (
    ExtractedEvidence,
    SourceType,
    Severity,
    DisruptionType,
    DisruptionStatus,
    EntityGroundingStatus,
    TimeGroundingStatus
)
from backend.evidence.grounding import MumbaiGroundingEngine


def test_known_mumbai_entity_grounding():
    engine = MumbaiGroundingEngine()
    extracted = ExtractedEvidence(
        source_id="T_G1",
        source_type=SourceType.CROWD,
        raw_text="Delay at Andheri metro",
        location="Andheri",
        route_id="METRO_1",
        stop_id="ANDHERI",
        disruption_type=DisruptionType.DELAY,
        severity=Severity.MEDIUM,
        timestamp=datetime.now(timezone.utc),
        status=DisruptionStatus.ACTIVE
    )
    grounded = engine.ground_evidence(extracted)
    assert grounded.entity_status == EntityGroundingStatus.KNOWN
    assert grounded.grounded_stop_id == "ANDHERI"
    assert grounded.grounded_route_id == "METRO_1"


def test_unknown_entity_grounding():
    engine = MumbaiGroundingEngine()
    extracted = ExtractedEvidence(
        source_id="T_G2",
        source_type=SourceType.CROWD,
        raw_text="Derailment at XYZ Fantasy Land",
        location="XYZ Fantasy Land",
        route_id="LINE_999",
        stop_id="XYZ_STATION",
        disruption_type=DisruptionType.ACCIDENT,
        severity=Severity.HIGH,
        timestamp=datetime.now(timezone.utc),
        status=DisruptionStatus.ACTIVE
    )
    grounded = engine.ground_evidence(extracted)
    assert grounded.entity_status == EntityGroundingStatus.UNKNOWN


def test_impossible_future_time_grounding():
    engine = MumbaiGroundingEngine()
    now = datetime(2026, 10, 8, 18, 0, 0, tzinfo=timezone.utc)
    future_time = now + timedelta(hours=5)  # 5 hours in future

    extracted = ExtractedEvidence(
        source_id="T_TIME_1",
        source_type=SourceType.CROWD,
        raw_text="Metro delayed at Ghatkopar",
        location="Ghatkopar",
        disruption_type=DisruptionType.DELAY,
        severity=Severity.MEDIUM,
        timestamp=future_time,
        status=DisruptionStatus.ACTIVE
    )
    grounded = engine.ground_evidence(extracted, reference_now=now)
    assert grounded.time_status == TimeGroundingStatus.UNGROUNDABLE
    assert "Impossible future timestamp" in grounded.grounding_notes


def test_excessively_stale_time_grounding():
    engine = MumbaiGroundingEngine()
    now = datetime(2026, 10, 8, 18, 0, 0, tzinfo=timezone.utc)
    old_time = now - timedelta(days=5)  # 5 days in past

    extracted = ExtractedEvidence(
        source_id="T_TIME_2",
        source_type=SourceType.CROWD,
        raw_text="Metro delayed at Ghatkopar",
        location="Ghatkopar",
        disruption_type=DisruptionType.DELAY,
        severity=Severity.MEDIUM,
        timestamp=old_time,
        status=DisruptionStatus.ACTIVE
    )
    grounded = engine.ground_evidence(extracted, reference_now=now)
    assert grounded.time_status == TimeGroundingStatus.UNGROUNDABLE
    assert "Excessively stale" in grounded.grounding_notes
