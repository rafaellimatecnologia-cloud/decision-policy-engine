# Contributing

Thanks for your interest in contributing!

## Development setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Project expectations
- Keep the engine deterministic and auditable.
- Avoid external services, secrets, or network calls in examples/tests.
- Prefer small, focused changes with clear reasoning.

## Linting and tests
```bash
ruff check .
pytest
```

## Pull request guidance
- Add or update tests for behavior changes.
- Keep documentation concise and user-focused.
- Ensure new files use UTF-8 without BOM and LF line endings.

## Code style notes
- Follow existing naming patterns and module structure.
- Avoid introducing new runtime dependencies.
