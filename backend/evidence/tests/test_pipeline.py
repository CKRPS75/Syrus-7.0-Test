"""
Unit and Integration tests for Master Evidence Pipeline.
Verifies end-to-end evidence processing and P3 DisruptionEvent contract compliance.
"""

from datetime import datetime, timezone
from backend.evidence.schemas import RawEvidenceInput, SourceType, TrustDecision, DisruptionStatus
from backend.evidence.pipeline import EvidencePipeline


def test_pipeline_end_to_end_official_alert():
    pipeline = EvidencePipeline()
    pipeline.reset()

    raw_input = RawEvidenceInput(
        source_id="WR_OFF_ALERT_10",
        source_type=SourceType.OFFICIAL,
        text="Western Railway: Signal fault at Dadar station on slow line. Services delayed by 25 minutes.",
        timestamp=datetime.now(timezone.utc)
    )

    response = pipeline.process_evidence(raw_input)
    assert response.event_id == "D01"
    assert response.status == TrustDecision.CONFIRMED
    assert response.lifecycle_status == DisruptionStatus.ACTIVE
    assert response.location == "Dadar"
    assert response.route_id == "SUB_WESTERN"

    # Verify P3 Event structure compliance
    p3_event = response.event
    assert p3_event.event_id == "D01"
    assert p3_event.decision == TrustDecision.CONFIRMED
    assert p3_event.location == "Dadar"
    assert p3_event.route_id == "SUB_WESTERN"
    assert p3_event.stop_id == "DADAR"
    assert p3_event.evidence_count == 1
    assert p3_event.independent_sources == 1
    assert len(p3_event.evidence_summary) > 0


def test_pipeline_crowd_clustering_and_watch_decision():
    pipeline = EvidencePipeline()
    pipeline.reset()

    r1 = RawEvidenceInput(
        source_id="CROWD_USER_1",
        source_type=SourceType.CROWD,
        text="Metro delayed near Andheri station",
        timestamp=datetime.now(timezone.utc)
    )
    res1 = pipeline.process_evidence(r1)
    assert res1.event_id == "D01"
    assert res1.status in (TrustDecision.WATCH, TrustDecision.IGNORE)

    r2 = RawEvidenceInput(
        source_id="CROWD_USER_2",
        source_type=SourceType.CROWD,
        text="Stuck on Metro Line 1 around Andheri",
        timestamp=datetime.now(timezone.utc)
    )
    res2 = pipeline.process_evidence(r2)
    # Deduplication groups into D01
    assert res2.event_id == "D01"
    assert res2.event.evidence_count == 2
    # Crowd-only cannot reach CONFIRMED
    assert res2.status != TrustDecision.CONFIRMED


def test_pipeline_config_hash_reproducibility():
    pipeline = EvidencePipeline()
    cfg_hash = pipeline.get_config_hash()
    assert isinstance(cfg_hash, str)
    assert len(cfg_hash) == 64  # Valid SHA-256 string
