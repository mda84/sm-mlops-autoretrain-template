from __future__ import annotations

import math
from typing import Dict


def compute_simple_drift(old_stats: Dict, new_stats: Dict) -> float:
    """Compute a naive drift score based on mean differences."""
    score = 0.0
    for key, old_val in old_stats.items():
        if key in new_stats and isinstance(old_val, (int, float)) and isinstance(new_stats[key], (int, float)):
            denom = abs(old_val) + 1e-6
            score += abs(new_stats[key] - old_val) / denom
    return score


def decide_retrain(drift_score: float, threshold: float = 0.2) -> bool:
    return drift_score > threshold
