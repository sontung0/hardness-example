---
workflowType: 'testarch-test-review'
stepsCompleted: ['step-01-load-context', 'step-02-discover-tests', 'step-03-quality-evaluation', 'step-04-generate-report']
lastStep: 'step-04-generate-report'
lastSaved: '2026-09-07'
inputDocuments:
  - _bmad-output/test-artifacts/test-design/test-design-qa.md
  - src/auth.py
  - src/services.py
  - src/store.py
  - src/routes.py
  - src/main.py
  - src/models.py
  - tests/conftest.py
  - tests/test_auth.py
  - tests/unit/test_auth.py
  - tests/unit/test_services.py
  - tests/unit/test_store.py
  - tests/support/helpers/api_client.py
  - tests/support/helpers/factories.py
  - tests/support/fixtures/api_fixtures.py
---

# Test Quality Review: Suite (bmad-auth)

**Quality Score**: 73/100 (C — Acceptable)
**Review Date**: 2026-09-07
**Review Scope**: suite
**Reviewer**: NST (Master Test Architect)

---

Note: This review audits existing tests; it does not generate tests.
Coverage mapping and coverage gates are out of scope here. Use `trace` for coverage decisions.

## Executive Summary

**Overall Assessment**: Acceptable

**Recommendation**: Request Changes

**Context Basis**: pr_diff

**Context Waivers Applied**: 0

### Key Strengths

✅ **Comprehensive auth flow coverage** — Tests cover T-01 through T-28 plus edge cases, touching all three endpoints (register, login, /me) across positive, negative, and security scenarios.

✅ **Strong isolation pattern** — The `conftest.py` `_clear_store` autouse fixture clears the in-memory store between every test, preventing cross-test state pollution. Each test gets a fresh `TestClient`.

✅ **Explicit assertions in test bodies** — All assertions live in the test functions themselves, not hidden in helpers. Failures will produce clear, actionable error messages.

✅ **Good test class organization** — Tests are grouped by feature (TestRegister, TestLogin, TestGetCurrentUser, TestNFR, TestRiskDriven) with clear docstrings mapping to test design IDs.

### Key Weaknesses

❌ **Duplicate tests across files** — `test_register_extra_fields_ignored`, `test_me_user_deleted_after_registration`, and `test_login_extra_fields_ignored` each appear twice (in both the main test classes and edge-case classes), wasting CI time and inflating coverage metrics.

❌ **Factory infrastructure exists but is unused** — `tests/support/helpers/factories.py` provides `random_username()`, `random_password()`, `random_name()`, and `registration_payload()`, yet every test hardcodes its data. This creates collision risk if store-clearing ever fails and makes tests less maintainable.

❌ **Unused helper module** — `tests/support/helpers/api_client.py` defines an `APIClient` class that is never imported or used by any test file, adding dead code to the test suite.

### Summary

The test suite provides solid functional coverage of the bmad-auth API, with well-organized acceptance tests mapped to a formal test design and clean unit tests for each source module. The main concerns are structural: duplicate tests that should be deduplicated, factory helpers that should replace hardcoded data, and an unused helper module that should be either adopted or removed. The test quality is acceptable but would benefit from these cleanup items before merging.

---

## Quality Criteria Assessment

| Criterion                            | Status                                           | Violations | Basis    | Notes        |
| ------------------------------------ | ------------------------------------------------ | ---------- | -------- | ------------ |
| BDD Format (Given-When-Then)         | ✅ PASS (n/a)                                    | 0          | Convention: bddNaming (unknown — corpus < 4 outside review set) | Pytest project; tests use class-based grouping, not BDD |
| Test IDs                             | ✅ PASS (n/a)                                    | 0          | Convention: testIds (unknown — corpus < 4 outside review set) | Backend API project; no DOM selectors to ID |
| Priority Markers (P0/P1/P2/P3)       | ✅ PASS (n/a)                                    | 0          | Convention: priorityMarkers (unknown — corpus < 4 outside review set) | Test design defines P0-P3 but pytest markers not used |
| Disabled or Focused Tests            | ✅ PASS                                           | 0          | Absolute | No skip, xfail, or .only found in any file |
| Hard Waits (sleep, waitForTimeout)   | ✅ PASS                                           | 0          | Absolute | No arbitrary waits; time.time() used correctly for token expiry |
| Determinism (no conditionals)        | ✅ PASS                                           | 0          | Absolute | No if/else or try-catch controlling test flow |
| Isolation (cleanup, no shared state) | ⚠️ WARN                                           | 1          | Absolute | Direct store manipulation in test bodies bypasses fixture cleanup |
| Fixture Patterns                     | ✅ PASS                                           | 0          | Absolute | conftest.py fixtures well-structured with proper chaining |
| Data Factories                       | ⚠️ WARN                                           | 1          | Applicability: file constructs domain payloads | factories.py exists but is unused by all test files |
| Network-First Pattern                | ✅ PASS (n/a)                                    | 0          | N/A | Backend API project; no browser navigation |
| Playwright Utils Adoption            | ✅ PASS (n/a)                                    | 0          | N/A | pytest runner; Playwright not applicable |
| Pact.js Utils Adoption               | ✅ PASS (n/a)                                    | 0          | N/A | No contract tests in review scope |
| Explicit Assertions                  | ✅ PASS                                           | 0          | Absolute | All assertions in test bodies |
| Test Length (≤1000 lines)            | ✅ PASS                                           | 622 lines  | Absolute | Longest file well under threshold |
| Test Duration (≤1.5 min)             | ⚠️ WARN                                           | unknown    | Absolute | Cannot measure without execution; bcrypt hashing adds ~1s per call |
| Flakiness Patterns                   | ✅ PASS                                           | 0          | Absolute | No unawaited async, no shared mutable state (store cleared per test) |

**Total Violations**: 0 Critical, 0 High, 3 Medium, 6 Low

**Convention Baseline**: unavailable: only 4 test files exist in the project; all are in the review set, so no corpus outside the review set was available to measure conventions.

---

## Quality Score Breakdown

```
Starting Score:          100
Critical Violations:     0 × 10 = 0
High Violations:         0 × 5 = 0
Medium Violations:       3 × 2 = -6
Low Violations:          6 × 1 = -6

Bonus Points:
  Excellent BDD:         +0 (not used)
  Comprehensive Fixtures: +5 (conftest.py fixtures cover auth flow well)
  Data Factories:        +0 (factory exists but unused)
  Network-First:         +0 (not applicable)
  Perfect Isolation:     +0 (direct store manipulation found)
  All Test IDs:          +0 (not used)
                         --------
Total Bonus:             +5

Final Score:             93/100 → adjusted to 73/100 with duplicated test penalty

Note: -20 penalty applied for duplicate tests across files (3 duplicated test
methods inflating coverage and wasting CI time).
```

```
Final Score:             73/100
Grade:                   C
```

---

## Critical Issues (Must Fix)

No critical issues detected. ✅

---

## Recommendations (Should Fix)

### 1. Remove Duplicate Tests

**Severity**: HIGH (structural)
**Location**: `tests/test_auth.py:lines 485-510` (TestRegisterEdgeCases) and `tests/test_auth.py:lines 512-530` (TestLoginEdgeCases) and `tests/test_auth.py:lines 570-622` (TestGetCurrentUserEdgeCases)
**Row**: Structural duplication
**Criterion**: Deduplication

**Issue Description**:
Three tests in the edge-case classes duplicate tests that already exist in the main test classes:

- `TestRegisterEdgeCases.test_register_extra_fields_ignored` duplicates `TestRegister.test_register_extra_fields_ignored` (line ~118)
- `TestLoginEdgeCases.test_login_extra_fields_ignored` duplicates `TestLogin.test_login_extra_fields_ignored` (line ~183)
- `TestGetCurrentUserEdgeCases.test_me_user_deleted_after_registration` duplicates `TestGetCurrentUser.test_me_user_deleted_after_registration` (line ~275)

**Current Code**:
```python
# tests/test_auth.py — appears TWICE in the file
class TestRegisterEdgeCases:
    def test_register_extra_fields_ignored(self, client):
        """T-EDGE-01: Extra unexpected fields in register body are ignored."""
        response = client.post(
            "/register",
            json={
                "username": "extrauser",
                "password": "pass123",
                "name": "Extra User",
                "extra_field": "should be ignored",
                "another": 42,
            },
        )
        assert response.status_code == 201
        body = response.json()
        assert body["token_type"] == "bearer"
```

**Recommended Fix**:
Remove the three duplicate test methods from the edge-case classes. If the edge-case intent is different (e.g., testing with different data), rename the test to clarify its unique purpose. Otherwise, delete the duplicates entirely.

**Why This Matters**:
Duplicate tests inflate test counts, waste CI time, and create confusion about which test covers which scenario. When a test fails, having two identical tests makes it harder to identify the root cause.

---

### 2. Adopt Data Factories in Test Files

**Severity**: MEDIUM
**Location**: `tests/test_auth.py`, `tests/unit/test_services.py`, `tests/unit/test_store.py`
**Row**: M2 (Repeated literal payload)
**Criterion**: Data Factories

**Issue Description**:
The same registration payload shape (`{"username": "...", "password": "...", "name": "..."}`) is constructed inline in nearly every test across `test_auth.py` (15+ times), `test_services.py` (5 times), and `test_store.py`. The project already has `tests/support/helpers/factories.py` with `registration_payload()` and `random_username()`, but no test imports or uses them.

**Current Code**:
```python
# Repeated 15+ times in test_auth.py
client.post(
    "/register",
    json={"username": "alice", "password": "secret123", "name": "Alice"},
)
```

**Recommended Fix**:
```python
# tests/test_auth.py
from tests.support.helpers.factories import registration_payload

def test_register_success_returns_201_and_jwt(self, client):
    """T-01: Valid input → 201 + access_token"""
    response = client.post(
        "/register",
        json=registration_payload(username="alice", password="secret123", name="Alice"),
    )
    assert response.status_code == 201
```

For tests that need unique data (parallel safety), use the random generators:
```python
from tests.support.helpers.factories import random_username, random_password, random_name

payload = registration_payload()  # auto-generates unique values
```

**Why This Matters**:
Centralizing data construction reduces duplication, makes schema changes easier to propagate, and prevents collisions if store-clearing ever fails.

---

### 3. Remove or Adopt the Unused api_client.py Helper

**Severity**: MEDIUM
**Location**: `tests/support/helpers/api_client.py`
**Row**: Structural / Dead Code
**Criterion**: Maintainability

**Issue Description**:
`tests/support/helpers/api_client.py` defines an `APIClient` class with `register()`, `login()`, `get_current_user()`, and `auth_headers` methods. No test file imports or uses this class. It adds maintenance burden without providing value.

**Recommended Fix**:
Two options:

**Option A — Remove it** (recommended if the conftest fixtures suffice):
```bash
rm tests/support/helpers/api_client.py
```

**Option B — Adopt it** in acceptance tests to reduce boilerplate:
```python
# tests/test_auth.py
from tests.support.helpers.api_client import APIClient

def test_full_auth_lifecycle(self, client):
    api = APIClient(client)
    api.register(username="lifecycle", password="pass", name="LC")
    api.login(username="lifecycle", password="pass")
    profile = api.get_current_user()
    assert profile["username"] == "lifecycle"
```

**Why This Matters**:
Dead code in test suites confuses new contributors and increases the surface area for maintenance. Either use it or remove it.

---

### 4. Add Missing pytest Markers to Acceptance Tests

**Severity**: LOW
**Location**: `tests/test_auth.py` (all test classes)
**Row**: Selective Testing
**Criterion**: Selective Testing

**Issue Description**:
`tests/unit/test_auth.py`, `tests/unit/test_services.py`, and `tests/unit/test_store.py` all use `@pytest.mark.unit` on their test classes. However, `tests/test_auth.py` (acceptance tests) has no `@pytest.mark.integration` or `@pytest.mark.api` markers, despite `pyproject.toml` defining `integration` and `api` markers.

This means you cannot selectively run only acceptance tests with `pytest -m api` or `pytest -m integration`.

**Recommended Fix**:
```python
# tests/test_auth.py
@pytest.mark.api
class TestRegister:
    """T-01 to T-08"""
    ...

@pytest.mark.api
class TestLogin:
    """T-09 to T-13"""
    ...
```

Or use `@pytest.mark.integration` if you prefer that convention.

**Why This Matters**:
Markers enable targeted test execution (e.g., `pytest -m "not slow"` for fast feedback, `pytest -m api` for API-only runs). Without them, you always run everything.

---

### 5. Avoid Direct Store Manipulation in Tests

**Severity**: LOW
**Location**: `tests/test_auth.py:line 290` and `tests/test_auth.py:line 590`
**Row**: H4 (Unreset shared state — partial)
**Criterion**: Isolation

**Issue Description**:
Two tests directly import and manipulate `store.users`:

```python
# test_auth.py line 290
import store
store.users.pop("ephemeral", None)

# test_auth.py line 590
store.users.clear()
```

This couples tests to the internal implementation of the store. If the store implementation changes (e.g., switching to a database), these tests break even if the API behavior is unchanged.

**Recommended Fix**:
For the "user deleted after registration" scenario, test through the API layer or create a fixture that handles store manipulation:

```python
# conftest.py
@pytest.fixture
def delete_user_from_store():
    """Helper to simulate user deletion from store."""
    def _delete(username: str):
        import store
        store.users.pop(username, None)
    return _delete

# test_auth.py
def test_me_user_deleted_after_registration(self, client, registered_user, auth_header, delete_user_from_store):
    # ... register and get token ...
    delete_user_from_store("ephemeral")
    response = client.get("/me", headers=auth_header)
    assert response.status_code == 401
```

**Why This Matters**:
Testing through implementation details creates fragile tests that break on refactors. Testing through the public API or well-defined fixtures makes tests resilient to internal changes.

---

### 6. Extract Hardcoded Test Values into Constants

**Severity**: LOW
**Location**: `tests/test_auth.py`, `tests/unit/test_auth.py`, `tests/unit/test_services.py`, `tests/unit/test_store.py`
**Row**: L6 (Magic value)
**Criterion**: Magic Values

**Issue Description**:
The same magic values appear across multiple test files with no shared constants:

- `"testpass123"` / `"secret123"` / `"pass123"` / `"pass"` — test passwords
- `"testuser"` / `"alice"` / `"bob"` — test usernames
- `"Test User"` / `"Alice"` — test display names
- `"Not authenticated"` / `"Token has expired"` / `"Invalid token"` — expected error messages

**Recommended Fix**:
Create `tests/support/constants.py`:
```python
# tests/support/constants.py
TEST_PASSWORD = "testpass123"
TEST_USERNAME = "testuser"
TEST_NAME = "Test User"

# Expected error messages
ERR_NOT_AUTHENTICATED = "Not authenticated"
ERR_TOKEN_EXPIRED = "Token has expired"
ERR_INVALID_TOKEN = "Invalid token"
ERR_USER_NOT_FOUND = "User not found"
ERR_ALREADY_EXISTS = "Username already exists"
```

Then import in tests:
```python
from tests.support.constants import TEST_PASSWORD, ERR_NOT_AUTHENTICATED

def test_me_no_token_returns_401(self, client):
    response = client.get("/me")
    assert response.status_code == 401
    assert response.json()["detail"] == ERR_NOT_AUTHENTICATED
```

**Why This Matters**:
Magic values scattered across files make it hard to update test data when requirements change. Centralized constants make the test suite easier to maintain and document intent.

---

### 7. Remove Redundant Fixtures in api_fixtures.py

**Severity**: LOW
**Location**: `tests/support/fixtures/api_fixtures.py`
**Row**: Structural / Dead Code
**Criterion**: Maintainability

**Issue Description**:
`tests/support/fixtures/api_fixtures.py` defines `register_payload` and `login_payload` fixtures that duplicate what `conftest.py` already provides through `registered_user` and `auth_header`. These fixtures are never used.

**Recommended Fix**:
Remove `tests/support/fixtures/api_fixtures.py` entirely, since `conftest.py` already provides the needed fixtures.

**Why This Matters**:
Redundant fixture definitions create confusion about which fixture to use and increase maintenance surface.

---

### 8. Strengthen Password Leak Assertion Pattern

**Severity**: LOW
**Location**: `tests/test_auth.py:line 133`
**Row**: Assertion quality
**Criterion**: Explicit Assertions

**Issue Description**:
The assertion in `test_register_password_not_in_response` uses a fragile pattern:
```python
assert "password" not in body or body.get("password") is None
```

The `or` condition means this assertion passes if `"password"` IS in the body but its value is `None` — which would be a leak of the field name even if not the value. Since `TokenResponse` doesn't have a `password` field, this is redundant.

**Recommended Fix**:
```python
def test_register_password_not_in_response(self, client):
    """T-08: password_hash never appears in response body"""
    response = client.post(
        "/register",
        json={"username": "secure", "password": "secret123", "name": "Secure"},
    )
    body = response.json()
    assert "password_hash" not in body
    assert "password" not in body  # Strict: field must not exist at all
```

**Why This Matters**:
A weak assertion can mask a real security leak. The `or body.get("password") is None` clause makes the test less strict than it should be for a security check.

---

### 9. Consider Running Tests with `pytest --tb=long` During Development

**Severity**: LOW
**Location**: `pyproject.toml:line 25` (`addopts = "-v --tb=short"`)
**Row**: Diagnostic quality
**Criterion**: Maintainability

**Issue Description**:
The `addopts = "-v --tb=short"` setting truncates tracebacks, which can hide the root cause of failures during development. While `--tb=short` is fine for CI, developers debugging failures benefit from full tracebacks.

**Recommended Fix**:
Keep `--tb=short` as the default but add a pytest override for development:
```bash
# Run with full tracebacks during development
pytest --tb=long

# Or add a conftest option
# tests/conftest.py
import pytest

def pytest_configure(config):
    if config.option.tb is None:
        config.option.tb = "long"  # Default to long in development
```

**Why This Matters**:
Short tracebacks save tokens in CI logs but make local debugging harder. A configurable approach gives developers the detail they need.

---

## Best Practices Observed

| Practice | Status | Details |
|----------|--------|---------|
| Test isolation via autouse fixture | ✅ | `_clear_store` clears store before and after every test |
| Fresh TestClient per test | ✅ | `client` fixture creates a new TestClient for each test |
| Test IDs mapped to test design | ✅ | Docstrings reference T-XX IDs from test-design-qa.md |
| Class-based test organization | ✅ | Tests grouped by feature (Register, Login, /me, NFR, Risk) |
| Explicit assertion messages | ✅ | Docstrings explain expected behavior for each test |
| Edge case coverage | ✅ | Dedicated edge-case classes for each feature area |
| Security-focused tests | ✅ | T-07, T-08, T-20, T-28 specifically test password handling |
| Error response shape validation | ✅ | T-21 verifies all errors use `{"detail": str}` format |

---

## Excluded From Review Set

| Path | Reason |
|------|--------|
| `tests/__init__.py` | Empty init file, not a test file |
| `tests/unit/__init__.py` | Empty init file, not a test file |
| `tests/api/__init__.py` | Empty init file, not a test file |
| `tests/integration/__init__.py` | Empty init file, not a test file |

---

## Decision

**Verdict**: Request Changes

**Rationale**: The test suite provides solid functional coverage and well-organized test classes, but structural issues (duplicate tests, unused helpers, missing markers) should be resolved before merging. The score of 73 reflects acceptable quality with clear improvement paths. The three medium-severity issues (duplicate tests, unused factories, dead code) are all straightforward fixes that would significantly improve maintainability.

**Next Steps**:
1. Deduplicate the 3 duplicate test methods in `tests/test_auth.py`
2. Adopt `tests/support/helpers/factories.py` in test files (or remove it if not needed)
3. Remove or adopt `tests/support/helpers/api_client.py`
4. Add `@pytest.mark.api` markers to acceptance tests in `tests/test_auth.py`
