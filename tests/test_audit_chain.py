from dataclasses import replace

from decision_policy_engine.audit.events import AuditEvent
from decision_policy_engine.audit.trace import hash_event, redact_inputs
from decision_policy_engine.models import (
    Context,
    CostVector,
    ExecutionRoute,
    PolicyDecision,
    ProposedAction,
)


def _base_event() -> AuditEvent:
    context = Context(
        network_available=True,
        rtt_ms=50,
        battery_level=0.8,
        user_present=True,
        supervised_mode=True,
    )
    action = ProposedAction(type="DATA_PROCESS", risk_level="LOW")
    return AuditEvent(
        timestamp_iso="2024-01-01T00:00:00+00:00",
        trace_id="trace-1",
        decision_id="decision-1",
        action_type=action.type,
        policy_decision=PolicyDecision.ALLOW,
        route_selected=ExecutionRoute.LOCAL,
        cost_vector=CostVector(100, 0.1, 0.1, 0.1),
        reason="ok",
        inputs_redacted=redact_inputs(context, action),
    )


def test_hash_changes_with_field_change() -> None:
    event = _base_event()
    original_hash = hash_event(event)

    updated = replace(event, reason="changed")
    updated_hash = hash_event(updated)

    assert original_hash != updated_hash


def test_chained_hash_is_stable() -> None:
    event1 = _base_event()
    hash1 = hash_event(event1, prev_hash=None)
    event1 = replace(event1, hash=hash1)

    event2 = replace(
        event1,
        decision_id="decision-2",
        prev_hash=hash1,
        hash=None,
    )
    hash2 = hash_event(event2, prev_hash=hash1)

    assert hash1 == hash_event(event1, prev_hash=None)
    assert hash2 == hash_event(event2, prev_hash=hash1)
