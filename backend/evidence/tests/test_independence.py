"""
Unit tests for Honest Duplicates vs Coordinated Copy-Rings.
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
    TimeGroundingStatus,
    IndependenceType
)
from backend.evidence.independence import IndependenceEngine


def create_grounded(src_id: str, text: str, minutes_offset: int) -> GroundedEvidence:
    t = datetime(2026, 10, 8, 18, 0, 0, tzinfo=timezone.utc) + timedelta(minutes=minutes_offset)
    extracted = ExtractedEvidence(
        source_id=src_id,
        source_type=SourceType.CROWD,
        raw_text=text,
        location="Andheri",
        route_id="METRO_1",
        stop_id="ANDHERI",
        disruption_type=DisruptionType.DELAY,
        severity=Severity.MEDIUM,
        timestamp=t,
        status=DisruptionStatus.ACTIVE
    )
    return GroundedEvidence(
        extracted=extracted,
        entity_status=EntityGroundingStatus.KNOWN,
        time_status=TimeGroundingStatus.GROUNDED,
        grounded_location="Andheri",
        grounded_route_id="METRO_1",
        grounded_stop_id="ANDHERI"
    )


def test_honest_independent_duplicates():
    engine = IndependenceEngine(burst_window_minutes=10)

    # Different people describing the same delay in different words
    r1 = create_grounded("COMMUTER_1", "Stuck in train outside Andheri for 15 minutes", 0)
    prov1 = engine.evaluate_independence(r1, [])
    assert prov1.independence == IndependenceType.INDEPENDENT

    r2 = create_grounded("COMMUTER_2", "Andheri metro platform is crowded due to delay", 3)
    prov2 = engine.evaluate_independence(r2, [r1])
    assert prov2.independence == IndependenceType.INDEPENDENT


def test_coordinated_copy_ring_detected():
    engine = IndependenceEngine(burst_window_minutes=10, similarity_threshold=0.80)

    exact_text = "ALERT: Metro 1 Versova is completely shut down due to major accident."

    # Origin report
    r1 = create_grounded("BOT_ORIGIN", exact_text, 0)
    prov1 = engine.evaluate_independence(r1, [])
    assert prov1.independence == IndependenceType.INDEPENDENT

    # Bot 1 repeats exact text 30 seconds later
    r2 = create_grounded("BOT_ECHO_1", exact_text, 0.5)
    prov2 = engine.evaluate_independence(r2, [r1])
    assert prov2.independence == IndependenceType.COPY_DERIVED
    assert prov2.burst_detected is True

    # Bot 2 repeats exact text 1 minute later
    r3 = create_grounded("BOT_ECHO_2", exact_text, 1.0)
    prov3 = engine.evaluate_independence(r3, [r1, r2])
    assert prov3.independence == IndependenceType.COPY_DERIVED
