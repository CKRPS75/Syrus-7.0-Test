"""
Unit tests for Bayesian Trust Math, Crowd-Only Cap, and Decision Thresholds.
"""

from datetime import datetime, timezone
from backend.evidence.schemas import (
    ExtractedEvidence,
    GroundedEvidence,
    EvidenceProvenance,
    SourceType,
    Severity,
    DisruptionType,
    DisruptionStatus,
    EntityGroundingStatus,
    TimeGroundingStatus,
    IndependenceType,
    TrustDecision
)
from backend.evidence.trust import TrustEngine


def get_test_config():
    return {
        "prior_logit": -2.1972245773362196,  # logit(0.10)
        "crowd_evidence_cap": 2.6,
        "weights": {
            "official_exact": 2.5,
            "official_partial": 1.5,
            "independent_news": 1.2,
            "independent_crowd": 0.8,
            "additional_independent_crowd": 0.8,
            "location_time_consistency": 0.5,
            "credible_contradiction": -1.2,
            "weak_ungroundable": -2.0
        },
        "thresholds": {
            "ignore_max": 0.30,
            "watch_max": 0.65,
            "confirmed_min": 0.65
        },
        "freshness_decay_lambda_per_minute": {
            "crowd": 0.02,
            "news": 0.005,
            "official": 0.001
        }
    }


def make_item(src_id: str, src_type: SourceType, disruption_type=DisruptionType.DELAY) -> GroundedEvidence:
    extracted = ExtractedEvidence(
        source_id=src_id,
        source_type=src_type,
        raw_text=f"Transit issue on line at {src_id}",
        location="Andheri",
        route_id="METRO_1",
        stop_id="ANDHERI",
        disruption_type=disruption_type,
        severity=Severity.MEDIUM,
        timestamp=datetime.now(timezone.utc),
        status=DisruptionStatus.ACTIVE
    )
    return GroundedEvidence(
        extracted=extracted,
        entity_status=EntityGroundingStatus.KNOWN,
        time_status=TimeGroundingStatus.GROUNDED,
        grounded_location="Andheri",
        grounded_route_id="METRO_1",
        grounded_stop_id="ANDHERI",
        age_minutes=0.0
    )


def test_single_weak_crowd_cannot_reach_confirmed():
    engine = TrustEngine(get_test_config())
    item = make_item("CROWD_1", SourceType.CROWD)
    prov = EvidenceProvenance(
        evidence_id="CROWD_1",
        source_id="CROWD_1",
        source_type=SourceType.CROWD,
        independence=IndependenceType.INDEPENDENT
    )

    result = engine.calculate_trust([item], [prov])
    # Prior logit (-2.197) + 0.8 = -1.397 -> P* ≈ 0.198 -> IGNORE or single item
    assert result.decision != TrustDecision.CONFIRMED
    assert result.confidence_score < 0.65


def test_crowd_only_cap_prevents_confirmed_status():
    """
    Critical requirement: Crowd-only reports (even 10 independent reports)
    must be capped at +2.6 and CANNOT reach CONFIRMED (>= 0.65).
    """
    engine = TrustEngine(get_test_config())
    
    items = []
    provenances = []
    for i in range(10):
        src_id = f"CROWD_INDEP_{i+1}"
        item = make_item(src_id, SourceType.CROWD)
        prov = EvidenceProvenance(
            evidence_id=src_id,
            source_id=src_id,
            source_type=SourceType.CROWD,
            independence=IndependenceType.INDEPENDENT
        )
        items.append(item)
        provenances.append(prov)

    result = engine.calculate_trust(items, provenances)
    assert result.crowd_cap_applied is True
    # Max logit = -2.197 + 2.6 = 0.403 -> P* ≈ 0.5994 < 0.65
    assert result.confidence_score < 0.65
    assert result.decision == TrustDecision.WATCH
    assert result.decision != TrustDecision.CONFIRMED


def test_official_plus_news_reaches_confirmed():
    engine = TrustEngine(get_test_config())

    off_item = make_item("OFF_1", SourceType.OFFICIAL)
    news_item = make_item("NEWS_1", SourceType.NEWS)

    prov_off = EvidenceProvenance(evidence_id="OFF_1", source_id="OFF_1", source_type=SourceType.OFFICIAL, independence=IndependenceType.INDEPENDENT)
    prov_news = EvidenceProvenance(evidence_id="NEWS_1", source_id="NEWS_1", source_type=SourceType.NEWS, independence=IndependenceType.INDEPENDENT)

    result = engine.calculate_trust([off_item, news_item], [prov_off, prov_news])
    assert result.decision == TrustDecision.CONFIRMED
    assert result.confidence_score >= 0.65


def test_contradiction_applies_penalty():
    engine = TrustEngine(get_test_config())

    disrupt_item = make_item("NEWS_1", SourceType.NEWS, DisruptionType.DELAY)
    prov1 = EvidenceProvenance(evidence_id="NEWS_1", source_id="NEWS_1", source_type=SourceType.NEWS, independence=IndependenceType.INDEPENDENT)

    # Contradictory report claiming normal operation
    normal_item = make_item("CROWD_CLEAR", SourceType.CROWD, DisruptionType.NORMAL_OPERATION)
    normal_item.extracted.raw_text = "Trains running normally and on time now."
    prov2 = EvidenceProvenance(evidence_id="CROWD_CLEAR", source_id="CROWD_CLEAR", source_type=SourceType.CROWD, independence=IndependenceType.INDEPENDENT)

    result = engine.calculate_trust([disrupt_item, normal_item], [prov1, prov2])
    assert result.contradiction_detected is True
    assert "credible_contradiction_penalty" in result.evidence_weights
    assert result.evidence_weights["credible_contradiction_penalty"] == -1.2
