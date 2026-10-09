"""
Unit tests for Freshness and Exponential Evidence Decay.
"""

import math
from backend.evidence.freshness import FreshnessEngine
from backend.evidence.schemas import SourceType


def test_fresh_evidence_no_decay():
    engine = FreshnessEngine({"crowd": 0.02, "news": 0.005, "official": 0.001})
    weight = engine.calculate_decayed_weight(base_weight=0.8, source_type=SourceType.CROWD, age_minutes=0.0)
    assert weight == 0.8


def test_exponential_decay_crowd():
    engine = FreshnessEngine({"crowd": 0.02})
    base_weight = 0.8
    age_minutes = 35.0  # Approx one half-life (0.02 * 35 = 0.70 -> exp(-0.70) ≈ 0.4965)
    
    decayed = engine.calculate_decayed_weight(base_weight, SourceType.CROWD, age_minutes)
    expected = base_weight * math.exp(-0.02 * 35.0)
    assert abs(decayed - expected) < 1e-6
    assert decayed < base_weight


def test_source_specific_decay_rates():
    engine = FreshnessEngine({"crowd": 0.02, "news": 0.005, "official": 0.001})
    age = 60.0  # 1 hour
    
    w_crowd = engine.calculate_decay_multiplier(SourceType.CROWD, age)
    w_news = engine.calculate_decay_multiplier(SourceType.NEWS, age)
    w_official = engine.calculate_decay_multiplier(SourceType.OFFICIAL, age)

    # Crowd decays fastest, official decays slowest
    assert w_crowd < w_news < w_official
