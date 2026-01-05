from __future__ import annotations

"""Audit event definitions."""

from collections.abc import Mapping
from dataclasses import dataclass

from decision_policy_engine.models import CostVector, ExecutionRoute, PolicyDecision


@dataclass(frozen=True)
class AuditEvent:
    """Immutable audit record for decisions and routing."""

    timestamp_iso: str
    trace_id: str
    decision_id: str
    action_type: str
    policy_decision: PolicyDecision
    route_selected: ExecutionRoute
    cost_vector: CostVector
    reason: str
    inputs_redacted: Mapping[str, object]
    prev_hash: str | None = None
    hash: str | None = None
