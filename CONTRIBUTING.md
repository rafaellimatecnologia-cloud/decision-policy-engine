# Contributing

Thanks for your interest in contributing!

## Development setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Linting and tests
```bash
ruff check .
pytest
```

## Guidelines
- Keep changes deterministic and auditable.
- Avoid external services or secrets.
- Add or update tests for new behavior.
- Keep documentation concise and user-focused.
