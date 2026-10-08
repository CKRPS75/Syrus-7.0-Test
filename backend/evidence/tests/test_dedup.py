"""
Unit tests for Event Deduplication and Incident Clustering.
"""

from datetime import datetime, timezone, timedelta
from backend.evidence.schemas import (
    ExtractedEvidence,
    GroundedEvidence,
    SourceType,
    Severity,
    DisruptionType,
    DisruptionStatus,
    EntityGroundingStatus,
    TimeGroundingStatus
)
from backend.evidence.dedup import DeduplicationEngine


def make_grounded_item(src_id: str, location: str, route_id: str, minutes_offset: int = 0) -> GroundedEvidence:
    t = datetime(2026, 10, 8, 18, 0, 0, tzinfo=timezone.utc) + timedelta(minutes=minutes_offset)
    extracted = ExtractedEvidence(
        source_id=src_id,
        source_type=SourceType.CROWD,
        raw_text=f"Metro delayed near {location}",
        location=location,
        route_id=route_id,
        stop_id=location.upper(),
        disruption_type=DisruptionType.DELAY,
        severity=Severity.MEDIUM,
        timestamp=t,
        status=DisruptionStatus.ACTIVE
    )
    return GroundedEvidence(
        extracted=extracted,
        entity_status=EntityGroundingStatus.KNOWN,
        time_status=TimeGroundingStatus.GROUNDED,
        grounded_location=location,
        grounded_route_id=route_id,
        grounded_stop_id=location.upper()
    )


def test_multiple_reports_cluster_into_single_event():
    engine = DeduplicationEngine(dedup_window_minutes=60)

    # R1: Metro delayed at Andheri
    r1 = make_grounded_item("R1", "Andheri", "METRO_1", minutes_offset=0)
    e1_id, cluster1, is_new1 = engine.assign_event(r1)
    assert is_new1 is True
    assert e1_id == "D01"

    # R2: Trains delayed near Andheri (5 mins later)
    r2 = make_grounded_item("R2", "Andheri", "METRO_1", minutes_offset=5)
    e2_id, cluster2, is_new2 = engine.assign_event(r2)
    assert is_new2 is False
    assert e2_id == "D01"

    # R3: Metro Line 1 delayed around Andheri (10 mins later)
    r3 = make_grounded_item("R3", "Andheri", "METRO_1", minutes_offset=10)
    e3_id, cluster3, is_new3 = engine.assign_event(r3)
    assert is_new3 is False
    assert e3_id == "D01"
    assert len(cluster3.evidence_items) == 3


def test_distinct_location_creates_separate_event():
    engine = DeduplicationEngine(dedup_window_minutes=60)

    r1 = make_grounded_item("R1", "Andheri", "METRO_1", minutes_offset=0)
    e1_id, _, is_new1 = engine.assign_event(r1)
    assert e1_id == "D01"

    # Unrelated incident at Churchgate on Western Line
    r2 = make_grounded_item("R2", "Churchgate", "SUB_WESTERN", minutes_offset=5)
    e2_id, _, is_new2 = engine.assign_event(r2)
    assert is_new2 is True
    assert e2_id == "D02"
