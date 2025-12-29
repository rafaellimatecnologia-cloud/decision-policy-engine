from decision_policy_engine.models import Context, PolicyDecision, ProposedAction
from decision_policy_engine.policy.policy_gate import PolicyGate


def test_policy_gate_supervised_for_high_risk() -> None:
    context = Context(
        network_available=True,
        rtt_ms=50,
        battery_level=0.8,
        user_present=True,
        supervised_mode=False,
    )
    action = ProposedAction(type="DATA_EXPORT", risk_level="HIGH")

    decision, reason = PolicyGate.evaluate(context, action)

    assert decision == PolicyDecision.SUPERVISED
    assert "supervision" in reason.lower()


def test_policy_gate_denies_without_network() -> None:
    context = Context(
        network_available=False,
        rtt_ms=0,
        battery_level=0.9,
        user_present=True,
        supervised_mode=True,
    )
    action = ProposedAction(type="NETWORK_CALL", risk_level="LOW")

    decision, reason = PolicyGate.evaluate(context, action)

    assert decision == PolicyDecision.DENY
    assert "network" in reason.lower()


def test_policy_gate_denies_low_battery() -> None:
    context = Context(
        network_available=True,
        rtt_ms=50,
        battery_level=0.05,
        user_present=True,
        supervised_mode=True,
    )
    action = ProposedAction(type="NETWORK_CALL", risk_level="LOW")

    decision, reason = PolicyGate.evaluate(context, action)

    assert decision == PolicyDecision.DENY
    assert "battery" in reason.lower()


def test_policy_gate_allows_safe_action() -> None:
    context = Context(
        network_available=True,
        rtt_ms=50,
        battery_level=0.5,
        user_present=True,
        supervised_mode=True,
    )
    action = ProposedAction(type="DATA_PROCESS", risk_level="LOW")

    decision, reason = PolicyGate.evaluate(context, action)

    assert decision == PolicyDecision.ALLOW
    assert "permitted" in reason.lower()


def test_proposed_action_rejects_invalid_risk_level() -> None:
    try:
        ProposedAction(type="DATA_PROCESS", risk_level="UNKNOWN")
    except ValueError as exc:
        assert "risk_level" in str(exc)
    else:
        raise AssertionError("Expected ValueError for invalid risk_level")
