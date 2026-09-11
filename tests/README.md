# Test Suite — bmad-auth

## Setup

```bash
# Install dependencies (including test extras)
uv pip install -e ".[test]"
```

## Running Tests

```bash
# All tests
uv run python -m pytest tests/ -v

# Unit tests only (fast, no I/O)
uv run python -m pytest tests/unit/ -v

# API acceptance tests
uv run python -m pytest tests/test_auth.py -v

# With coverage
uv run python -m pytest tests/ --cov=src --cov-report=term-missing

# By marker
uv run python -m pytest -m unit
uv run python -m pytest -m "not slow"
```

## Architecture

```
tests/
├── conftest.py                    # Core fixtures (client, auth_header, _clear_store)
├── test_auth.py                   # API acceptance tests (T-01 to T-28)
├── unit/
│   ├── test_store.py              # Unit tests for in-memory store
│   └── test_services.py           # Unit tests for business logic
├── integration/                   # Integration tests (placeholder)
├── api/                           # Additional API tests (placeholder)
├── support/
│   ├── fixtures/
│   │   └── api_fixtures.py        # API-level fixtures (payloads)
│   └── helpers/
│       ├── api_client.py          # APIClient wrapper class
│       └── factories.py           # Faker-based data factories
└── README.md                      # This file
```

### Fixtures

| Fixture | Scope | Source | Purpose |
|---------|-------|--------|---------|
| `_clear_store` | function | `conftest.py` | Clears in-memory store between tests (autouse) |
| `client` | function | `conftest.py` | Fresh `TestClient` per test |
| `registered_user` | function | `conftest.py` | Registers a user and returns response data |
| `auth_header` | function | `conftest.py` | Returns `Authorization` header dict |
| `register_payload` | function | `api_fixtures.py` | Default registration payload |
| `login_payload` | function | `api_fixtures.py` | Default login payload |

### Helpers

- **`APIClient`** — Thin wrapper around `TestClient` with `register()`, `login()`, `get_current_user()` convenience methods and auto-token management.
- **`factories`** — Functions for generating random test data: `random_username()`, `random_password()`, `random_name()`, `registration_payload()`.

## Best Practices

- **Isolation**: Every test gets a fresh store state via the `_clear_store` autouse fixture.
- **Markers**: Use `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.api`, `@pytest.mark.slow` to categorize tests.
- **Parametrize**: Use `@pytest.mark.parametrize` for data-driven tests.
- **Factories**: Use `tests/support/helpers/factories.py` for generating test data instead of hardcoding values.

## CI Integration

```bash
# PR gate: unit tests only (fast feedback)
uv run python -m pytest tests/unit/ -v --tb=short

# Full suite: all tests with coverage
uv run python -m pytest tests/ --cov=src --cov-report=xml --cov-report=term-missing
```

## Test IDs

Test IDs in `test_auth.py` map to the coverage matrix in `test-design-qa.md`:
- T-01 to T-08: FR-1 — Registration
- T-09 to T-13: FR-2 — Login
- T-14 to T-19: FR-3 — Get current user
- T-20 to T-25: NFR scenarios
- T-26 to T-28: Risk-driven scenarios
