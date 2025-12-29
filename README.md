# Decision Policy Engine

## What it is
A deterministic, auditable Decision + Policy Engine for choosing execution routes (LOCAL / HYBRID /
CLOUD / DEGRADED) based on explicit cost vectors and a policy gate.

## Why it matters
Clear, reproducible decisioning makes systems easier to trust, debug, and audit. This project
illustrates how to keep routing logic transparent and safe to publish.

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
python examples/demo_cli.py --scenario network_off
pytest
```

## Design principles
- **Determinism:** same inputs yield the same decision, route, and audit hash.
- **Explicit cost vectors:** routing is driven by named, weighted signals.
- **Auditability:** canonical JSON and optional chained hashing for traceability.
- **Safe to publish:** no external API calls or secrets.

## Limitations
- Cost normalization uses fixed bounds suited to demo scenarios.
- Routing is based on a single scoring function and static weights.
- The audit log is local JSONL for simplicity.
