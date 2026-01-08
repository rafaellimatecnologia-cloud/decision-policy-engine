from __future__ import annotations

"""Cost normalization utilities."""

LATENCY_MIN_MS = 0
LATENCY_MAX_MS = 2000
COST_MIN = 0.0
COST_MAX = 10.0


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def norm_latency(latency_ms: int) -> float:
    """Normalize latency into [0, 1] range with clamping."""

    span = LATENCY_MAX_MS - LATENCY_MIN_MS
    if span <= 0:
        return 0.0
    return _clamp((latency_ms - LATENCY_MIN_MS) / span, 0.0, 1.0)


def norm_cost(dollar_cost: float) -> float:
    """Normalize dollar cost into [0, 1] range with clamping."""

    span = COST_MAX - COST_MIN
    if span <= 0:
        return 0.0
    return _clamp((dollar_cost - COST_MIN) / span, 0.0, 1.0)
