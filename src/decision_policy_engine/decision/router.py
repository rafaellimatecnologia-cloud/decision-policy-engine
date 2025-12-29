"""Route selection based on cost vectors."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from decision_policy_engine.decision.cost import norm_cost, norm_latency
from decision_policy_engine.models import Context, CostVector, ExecutionRoute

WEIGHTS = {
    "latency_ms": 0.45,
    "privacy_risk": 0.25,
    "reliability_risk": 0.20,
    "dollar_cost": 0.10,
}

TIE_BREAK_ORDER = [
    ExecutionRoute.LOCAL,
    ExecutionRoute.HYBRID,
    ExecutionRoute.CLOUD,
    ExecutionRoute.DEGRADED,
]


@dataclass(frozen=True)
class RouteExplanation:
    weights: Mapping[str, float]
    normalized: Mapping[ExecutionRoute, Mapping[str, float]]
    scores: Mapping[ExecutionRoute, float]


class Router:
    """Select an execution route based on weighted cost vectors."""

    @staticmethod
    def _score(cost: CostVector) -> tuple[float, dict[str, float]]:
        normalized = {
            "latency_ms": norm_latency(cost.latency_ms),
            "privacy_risk": cost.privacy_risk,
            "reliability_risk": cost.reliability_risk,
            "dollar_cost": norm_cost(cost.dollar_cost),
        }
        score = sum(WEIGHTS[key] * value for key, value in normalized.items())
        return score, normalized

    @staticmethod
    def select_route(
        context: Context,
        candidates: Mapping[ExecutionRoute, CostVector],
    ) -> tuple[ExecutionRoute, CostVector, RouteExplanation]:
        """Select a route given the context and candidates."""

        filtered: dict[ExecutionRoute, CostVector] = dict(candidates)
        if not context.network_available:
            filtered.pop(ExecutionRoute.CLOUD, None)

        if not filtered:
            raise ValueError("No candidates available for routing.")

        scores: dict[ExecutionRoute, float] = {}
        normalized_values: dict[ExecutionRoute, dict[str, float]] = {}
        for route, cost in filtered.items():
            score, normalized = Router._score(cost)
            scores[route] = score
            normalized_values[route] = normalized

        def _tie_break(route: ExecutionRoute) -> int:
            return TIE_BREAK_ORDER.index(route)

        if not context.network_available and ExecutionRoute.LOCAL in filtered:
            chosen_route = ExecutionRoute.LOCAL
        elif (
            not context.network_available
            and ExecutionRoute.LOCAL not in filtered
            and ExecutionRoute.DEGRADED in filtered
        ):
            chosen_route = ExecutionRoute.DEGRADED
        else:
            chosen_route = min(
                scores,
                key=lambda route: (scores[route], _tie_break(route)),
            )

        explanation = RouteExplanation(
            weights=WEIGHTS,
            normalized=normalized_values,
            scores=scores,
        )
        return chosen_route, filtered[chosen_route], explanation
