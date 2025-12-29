from dataclasses import replace

from decision_policy_engine.audit.events import AuditEvent
from decision_policy_engine.audit.trace import hash_event, redact_inputs
from decision_policy_engine.decision.router import Router
from decision_policy_engine.models import Context, CostVector, ExecutionRoute, ProposedAction
from decision_policy_engine.policy.policy_gate import PolicyGate


def test_determinism_across_components() -> None:
    context = Context(
        network_available=True,
        rtt_ms=100,
        battery_level=0.5,
        user_present=True,
        supervised_mode=True,
    )
    action = ProposedAction(type="DATA_PROCESS", risk_level="LOW")

    policy_decision, reason = PolicyGate.evaluate(context, action)
    policy_decision_again, reason_again = PolicyGate.evaluate(context, action)

    assert policy_decision == policy_decision_again
    assert reason == reason_again

    candidates = {
        ExecutionRoute.LOCAL: CostVector(100, 0.1, 0.1, 0.1),
        ExecutionRoute.HYBRID: CostVector(120, 0.2, 0.2, 0.2),
    }

    route, cost, _ = Router.select_route(context, candidates)
    route_again, cost_again, _ = Router.select_route(context, candidates)

    assert route == route_again
    assert cost == cost_again

    event = AuditEvent(
        timestamp_iso="2024-01-01T00:00:00+00:00",
        trace_id="trace-1",
        decision_id="decision-1",
        action_type=action.type,
        policy_decision=policy_decision,
        route_selected=route,
        cost_vector=cost,
        reason=reason,
        inputs_redacted=redact_inputs(context, action),
    )
    event_hash = hash_event(event, prev_hash=None)
    event_again = replace(event, hash=None)
    event_hash_again = hash_event(event_again, prev_hash=None)

    assert event_hash == event_hash_again
