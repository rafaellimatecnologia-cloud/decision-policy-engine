from __future__ import annotations

"""Policy gate implementation."""

from decision_policy_engine.models import Context, PolicyDecision, ProposedAction


class PolicyGate:
    """Evaluates policy decisions for proposed actions."""

    @staticmethod
    def evaluate(context: Context, action: ProposedAction) -> tuple[PolicyDecision, str]:
        """Evaluate a proposed action against policy rules."""

        if action.risk_level == "HIGH" and not context.supervised_mode:
            return PolicyDecision.SUPERVISED, "High risk action requires supervision."

        if action.type == "NETWORK_CALL" and not context.network_available:
            return PolicyDecision.DENY, "Network unavailable for network call."

        if context.battery_level < 0.10 and action.type == "NETWORK_CALL":
            return PolicyDecision.DENY, "Battery too low for network call."

        return PolicyDecision.ALLOW, "Action permitted."
