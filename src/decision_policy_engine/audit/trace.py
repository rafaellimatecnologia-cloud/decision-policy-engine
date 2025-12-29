"""Audit trace helpers."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path

from decision_policy_engine.audit.events import AuditEvent
from decision_policy_engine.models import Context, ProposedAction


def _normalize(value: object) -> object:
    if isinstance(value, dict):
        return {key: _normalize(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    if hasattr(value, "value") and not isinstance(value, (str, bytes)):
        return value.value
    return value


def canonical_event_json(event: AuditEvent, *, include_hash_fields: bool = False) -> str:
    """Return canonical JSON representation of an audit event."""

    data = asdict(event)
    if not include_hash_fields:
        data.pop("hash", None)
        data.pop("prev_hash", None)
    normalized = _normalize(data)
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def hash_event(event: AuditEvent, prev_hash: str | None = None) -> str:
    """Generate a chained hash for the event."""

    base = prev_hash or ""
    payload = base + canonical_event_json(event, include_hash_fields=False)
    return sha256(payload.encode("utf-8")).hexdigest()


def append_jsonl(path: str | Path, event: AuditEvent) -> None:
    """Append an audit event to a JSONL file."""

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    line = canonical_event_json(event, include_hash_fields=True)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def redact_inputs(context: Context, action: ProposedAction) -> Mapping[str, object]:
    """Return a safe subset of inputs for audit logging."""

    return {
        "action": {
            "type": action.type,
            "risk_level": action.risk_level,
            "metadata": dict(action.metadata),
        },
        "context": {
            "network_available": context.network_available,
            "rtt_ms": context.rtt_ms,
            "battery_level": context.battery_level,
            "user_present": context.user_present,
            "supervised_mode": context.supervised_mode,
            "locale": context.locale,
        },
    }
