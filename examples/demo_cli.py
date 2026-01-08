"""Minimal demo CLI for the decision policy engine."""

from __future__ import annotations

import json

from decision_policy_engine.decision.router import Router
from decision_policy_engine.models import Context, CostVector, ExecutionRoute, ProposedAction
from decision_policy_engine.policy.policy_gate import PolicyGate


def _serialize_context(context: Context) -> dict[str, object]:
    return {
        "battery_level": context.battery_level,
        "locale": context.locale,
        "network_available": context.network_available,
        "rtt_ms": context.rtt_ms,
        "supervised_mode": context.supervised_mode,
        "user_present": context.user_present,
    }


def _serialize_action(action: ProposedAction) -> dict[str, object]:
    return {
        "metadata": dict(action.metadata),
        "risk_level": action.risk_level,
        "type": action.type,
    }


def _serialize_cost(cost: CostVector) -> dict[str, float]:
    return {
        "dollar_cost": cost.dollar_cost,
        "latency_ms": cost.latency_ms,
        "privacy_risk": cost.privacy_risk,
        "reliability_risk": cost.reliability_risk,
    }


def _serialize_candidates(
    candidates: dict[ExecutionRoute, CostVector],
) -> dict[str, dict[str, float]]:
    return {
        route.value: _serialize_cost(cost)
        for route, cost in sorted(candidates.items(), key=lambda item: item[0].value)
    }


def _serialize_scores(scores: dict[ExecutionRoute, float]) -> dict[str, float]:
    return {
        route.value: score
        for route, score in sorted(scores.items(), key=lambda item: item[0].value)
    }


def _serialize_normalized(
    normalized: dict[ExecutionRoute, dict[str, float]],
) -> dict[str, dict[str, float]]:
    return {
        route.value: {
            key: normalized[route][key] for key in sorted(normalized[route].keys())
        }
        for route in sorted(normalized.keys(), key=lambda item: item.value)
    }


def _build_trace(
    context: Context,
    action: ProposedAction,
    policy_decision: str,
    policy_reason: str,
    candidates: dict[ExecutionRoute, CostVector],
    chosen_route: ExecutionRoute,
    chosen_cost: CostVector,
    explanation,
) -> dict[str, object]:
    return {
        "action": _serialize_action(action),
        "context": _serialize_context(context),
        "policy": {
            "decision": policy_decision,
            "reason": policy_reason,
        },
        "routing": {
            "candidates": _serialize_candidates(candidates),
            "chosen_cost": _serialize_cost(chosen_cost),
            "chosen_route": chosen_route.value,
            "normalized": _serialize_normalized(explanation.normalized),
            "scores": _serialize_scores(explanation.scores),
            "weights": {key: explanation.weights[key] for key in sorted(explanation.weights)},
        },
    }


def main() -> None:
    context = Context(
        network_available=True,
        rtt_ms=85,
        battery_level=0.72,
        user_present=True,
        supervised_mode=True,
    )
    action = ProposedAction(
        type="DATA_LOOKUP",
        risk_level="MEDIUM",
        metadata={"request_id": "demo-001"},
    )
    candidates = {
        ExecutionRoute.LOCAL: CostVector(95, 0.05, 0.08, 0.02),
        ExecutionRoute.HYBRID: CostVector(120, 0.08, 0.12, 0.05),
        ExecutionRoute.CLOUD: CostVector(210, 0.22, 0.18, 0.12),
        ExecutionRoute.DEGRADED: CostVector(300, 0.02, 0.2, 0.0),
    }

    policy_decision, policy_reason = PolicyGate.evaluate(context, action)
    chosen_route, chosen_cost, explanation = Router.select_route(context, candidates)

    trace = _build_trace(
        context,
        action,
        policy_decision.value,
        policy_reason,
        candidates,
        chosen_route,
        chosen_cost,
        explanation,
    )

    print(f"decision: {policy_decision.value}")
    print(json.dumps(trace, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
