"""Core models for the decision policy engine."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum


@dataclass(frozen=True)
class CostVector:
    """Cost signal inputs used for routing decisions."""

    latency_ms: int
    privacy_risk: float
    reliability_risk: float
    dollar_cost: float


class ExecutionRoute(str, Enum):
    """Possible execution routes."""

    LOCAL = "LOCAL"
    HYBRID = "HYBRID"
    CLOUD = "CLOUD"
    DEGRADED = "DEGRADED"


class PolicyDecision(str, Enum):
    """Policy gate outcomes."""

    ALLOW = "ALLOW"
    DENY = "DENY"
    SUPERVISED = "SUPERVISED"


@dataclass(frozen=True)
class ProposedAction:
    """Action proposal evaluated by the policy gate."""

    type: str
    risk_level: str
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        allowed = {"LOW", "MEDIUM", "HIGH"}
        if self.risk_level not in allowed:
            raise ValueError(f"risk_level must be one of {sorted(allowed)}")


@dataclass(frozen=True)
class Context:
    """Execution context for evaluating policy and routing decisions."""

    network_available: bool
    rtt_ms: int
    battery_level: float
    user_present: bool
    supervised_mode: bool
    locale: str = "en-US"
