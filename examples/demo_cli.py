"""CLI demo for the decision policy engine."""

from __future__ import annotations

import argparse
import json
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from decision_policy_engine.audit.events import AuditEvent
from decision_policy_engine.audit.trace import append_jsonl, hash_event, redact_inputs
from decision_policy_engine.decision.router import Router
from decision_policy_engine.models import (
    Context,
    CostVector,
    ExecutionRoute,
    ProposedAction,
)
from decision_policy_engine.policy.policy_gate import PolicyGate

SCENARIOS = {
    "network_off": {
        "context": Context(
            network_available=False,
            rtt_ms=0,
            battery_level=0.75,
            user_present=True,
            supervised_mode=False,
        ),
        "action": ProposedAction(type="NETWORK_CALL", risk_level="LOW"),
    },
    "high_latency": {
        "context": Context(
            network_available=True,
            rtt_ms=1200,
            battery_level=0.55,
            user_present=True,
            supervised_mode=False,
        ),
        "action": ProposedAction(type="DATA_PROCESS", risk_level="MEDIUM"),
    },
    "low_battery": {
        "context": Context(
            network_available=True,
            rtt_ms=120,
            battery_level=0.05,
            user_present=True,
            supervised_mode=False,
        ),
        "action": ProposedAction(type="NETWORK_CALL", risk_level="LOW"),
    },
    "supervised_high_risk": {
        "context": Context(
            network_available=True,
            rtt_ms=80,
            battery_level=0.80,
            user_present=True,
            supervised_mode=True,
        ),
        "action": ProposedAction(type="DATA_EXPORT", risk_level="HIGH"),
    },
}


def build_candidates(context: Context) -> dict[ExecutionRoute, CostVector]:
    """Build candidate cost vectors for demo scenarios."""

    return {
        ExecutionRoute.LOCAL: CostVector(
            latency_ms=120,
            privacy_risk=0.05,
            reliability_risk=0.10,
            dollar_cost=0.02,
        ),
        ExecutionRoute.HYBRID: CostVector(
            latency_ms=max(200, context.rtt_ms),
            privacy_risk=0.15,
            reliability_risk=0.20,
            dollar_cost=0.20,
        ),
        ExecutionRoute.CLOUD: CostVector(
            latency_ms=max(300, context.rtt_ms + 80),
            privacy_risk=0.35,
            reliability_risk=0.30,
            dollar_cost=0.45,
        ),
        ExecutionRoute.DEGRADED: CostVector(
            latency_ms=600,
            privacy_risk=0.02,
            reliability_risk=0.40,
            dollar_cost=0.00,
        ),
    }


def _read_last_hash(path: Path) -> str | None:
    if not path.exists():
        return None
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    if not lines:
        return None
    payload = json.loads(lines[-1])
    value = payload.get("hash")
    return str(value) if value else None


def run_scenario(name: str) -> None:
    """Run a demo scenario and append an audit log."""

    scenario = SCENARIOS[name]
    context = scenario["context"]
    action = scenario["action"]

    policy_decision, reason = PolicyGate.evaluate(context, action)
    candidates = build_candidates(context)
    chosen_route, chosen_cost, explanation = Router.select_route(context, candidates)

    trace_id = str(uuid4())
    decision_id = str(uuid4())
    timestamp_iso = datetime.now(timezone.utc).isoformat()

    output_path = Path("out") / "audit_log.jsonl"
    prev_hash = _read_last_hash(output_path)

    event = AuditEvent(
        timestamp_iso=timestamp_iso,
        trace_id=trace_id,
        decision_id=decision_id,
        action_type=action.type,
        policy_decision=policy_decision,
        route_selected=chosen_route,
        cost_vector=chosen_cost,
        reason=reason,
        inputs_redacted=redact_inputs(context, action),
        prev_hash=prev_hash,
    )
    event_hash = hash_event(event, prev_hash=prev_hash)
    event = replace(event, hash=event_hash)

    append_jsonl(output_path, event)

    print(f"Scenario: {name}")
    print(f"Policy decision: {policy_decision} ({reason})")
    print(f"Route selected: {chosen_route}")
    print(f"Score breakdown: {explanation.scores}")
    print(f"Audit hash: {event_hash}")
    print(f"Audit log appended: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scenario",
        choices=SCENARIOS.keys(),
        default="network_off",
    )
    args = parser.parse_args()
    run_scenario(args.scenario)


if __name__ == "__main__":
    main()
