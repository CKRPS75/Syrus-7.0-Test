"""
Freshness & Temporal Decay Module.
Implements exponential evidence decay:
    e(t) = e(0) * exp(-lambda * delta_t)
Configured per source-type (crowd, news, official).
"""

import math
from typing import Dict
from backend.evidence.schemas import SourceType


class FreshnessEngine:
    """Calculates continuous exponential freshness decay for evidence items."""

    def __init__(self, decay_lambdas: Dict[str, float] | None = None):
        # Default decay lambdas per minute if not provided
        self.decay_lambdas = decay_lambdas or {
            "crowd": 0.02,     # Half-life ≈ 35 mins
            "news": 0.005,     # Half-life ≈ 138 mins (2.3 hrs)
            "official": 0.001  # Half-life ≈ 693 mins (11.5 hrs)
        }

    def get_decay_lambda(self, source_type: SourceType | str) -> float:
        """Returns the lambda decay factor for a given source type."""
        key = source_type.value.lower() if isinstance(source_type, SourceType) else str(source_type).lower()
        return self.decay_lambdas.get(key, 0.01)

    def calculate_decay_multiplier(self, source_type: SourceType | str, age_minutes: float) -> float:
        """
        Computes exp(-lambda * delta_t).
        Multiplier ranges from 1.0 (fresh) down towards 0.0 (aged).
        """
        if age_minutes <= 0:
            return 1.0
        lam = self.get_decay_lambda(source_type)
        return math.exp(-lam * age_minutes)

    def calculate_decayed_weight(
        self,
        base_weight: float,
        source_type: SourceType | str,
        age_minutes: float
    ) -> float:
        """Calculates decayed weight e(t) = e(0) * exp(-lambda * delta_t)."""
        multiplier = self.calculate_decay_multiplier(source_type, age_minutes)
        return base_weight * multiplier
