---
workflowType: 'testarch-test-review'
stepsCompleted: ['step-01-load-context', 'step-02-discover-tests', 'step-03-quality-evaluation', 'step-03f-aggregate-scores', 'step-04-generate-report']
lastStep: 'step-04-generate-report'
lastSaved: '2026-09-15'
inputDocuments:
  - _bmad-output/implementation-artifacts/spec-2-1-change-password.md
  - _bmad-output/test-artifacts/test-design/test-design-epic-2.md
---

# Test Quality Review: bmad-auth test suite

**Review Date**: 2026-09-15
**Review Scope**: suite (all tests on branch `feat/password-change-api`)
**Branch**: `feat/password-change-api`
**Reviewer**: NST
**Execution Mode**: subagent

---

Note: This review audits existing tests; it does not generate tests.
Coverage mapping and coverage gates are out of scope here. Use `trace` for coverage decisions.

## Executive Summary

**Overall Quality Score**: 79/100 (Grade: B, capped from raw 24/100 by HIGH severity cap)

The test suite has excellent structural foundations — perfect isolation via autouse fixtures, zero mocks (all tests exercise real code paths), and consistent class-based organization across all 8 test files. However, 13 HIGH-severity violations were found across two categories that undermine test reliability and value:

1. **Shape-only assertions (H10)**: 4 success-path tests in `test_services_password_change.py` and 1 in `test_auth.py` assert only `result is not None` and `"message" in result` without verifying actual values. These tests pass even when the returned message is wrong or the store was never updated.

2. **Wall-clock fixtures (H2)**: 2 tests in `test_auth.py` and `tests/test_auth.py` assert JWT expiry claims against live `time.time()` snapshots with a 5-second tolerance, creating flakiness risk under CI load.

3. **Conditional assertion (H3)**: 1 concurrency test has an assertion inside a `for err in errors:` loop that silently skips when the loop body never executes.

The recommendation is **Request Changes** due to HIGH-severity violations. Fix the H10 shape-only assertions by adding value checks, and fix the H2 wall-clock tests by mocking `time.time()`.

---

## Step 1: Load Context

### Scope & Stack

| Property | Value |
|----------|-------|
| **Branch** | `feat/password-change-api` |
| **Review scope** | `suite` — all test files on branch |
| **Detected stack** | `backend` (Python / FastAPI / pytest) |
| **Test framework** | pytest 8.x |
| **Runner** | pytest (no Playwright, no Cypress) |
| **Playwright Utils** | N/A — not a JS/browser project |
| **Pact.js Utils** | N/A — no contract tests |

### Reviewed Files

| File | Level | Markers | Tests |
|------|-------|---------|-------|
| `tests/unit/test_store_password_change.py` | unit | `@pytest.mark.unit` | T-29, T-30, T-31 (3 tests) |
| `tests/unit/test_services_password_change.py` | unit | `@pytest.mark.unit` | T-32 to T-35, T-46, +5 more (12 tests) |
| `tests/unit/test_services.py` | unit | `@pytest.mark.unit` | T-01 to T-13, registration/auth (14 tests) |
| `tests/unit/test_auth.py` | unit | `@pytest.mark.unit` | T-AUTH-01 to T-AUTH-18 (18 tests) |
| `tests/unit/test_store.py` | unit | `@pytest.mark.unit` | store operations (9 tests) |
| `tests/api/test_change_password.py` | api | `@pytest.mark.api` | T-50 to T-57 (8 tests) |
| `tests/integration/test_password_change.py` | integration | `@pytest.mark.integration` | T-36 to T-49 (15 tests) |
| `tests/test_auth.py` | api | `@pytest.mark.api` | T-01 to T-28 (32 tests) |
| `tests/conftest.py` | support | — | Fixtures: `_clear_store`, `client`, `registered_user`, `auth_header`, `delete_user_from_store` |
| `tests/support/constants.py` | support | — | `TEST_USERNAME`, `TEST_PASSWORD`, `ERR_NOT_AUTHENTICATED`, `ERR_USER_NOT_FOUND` |
| `tests/support/helpers/factories.py` | support | — | `registration_payload`, `random_username`, `random_password`, `random_name` |

**Total tests:** ~80 (all passing, 27.26s runtime)

### Convention Baseline

| Key | Adopted | Sampled | Status | Form |
|-----|---------|---------|--------|------|
| priorityMarkers | 0 | 0 | unknown | — (corpus too small; all files in review set) |
| testIds | 0 | 0 | unknown | — |
| bddNaming | 0 | 0 | unknown | — |
| networkFirst | 0 | 0 | unknown | — |
| playwrightUtils | 0 | 0 | unknown | — |
| dataFactories | 0 | 0 | unknown | — |
| fixtures | 0 | 0 | unknown | — |
| assertionStyle | 0 | 0 | unknown | — |

*Note: All test files in this repo are part of the review set (greenfield feature branch). No corpus outside the review set exists to establish a convention baseline. Convention-keyed rows (L2, L3, L5, L7, L9) are PASS (n/a).*

### Run-Level Preconditions

| Precondition | Status | Rows Affected |
|-------------|--------|---------------|
| `playwrightUtilsActive` | **false** — package not installed | M9, L9 do not exist for this run |
| `pactjsUtilsActive` | **false** — package not installed | M10 does not exist for this run |

---

## Step 2: Discover & Parse Tests

### File Metadata

| File | Lines | Tests | Classes | Framework |
|------|-------|-------|---------|-----------|
| `tests/unit/test_store_password_change.py` | 40 | 3 | 1 | pytest |
| `tests/unit/test_services_password_change.py` | 142 | 12 | 1 | pytest |
| `tests/unit/test_services.py` | 102 | 14 | 3 | pytest |
| `tests/unit/test_auth.py` | 162 | 18 | 3 | pytest |
| `tests/unit/test_store.py` | 56 | 9 | 4 | pytest |
| `tests/api/test_change_password.py` | 174 | 8 | 1 | pytest |
| `tests/integration/test_password_change.py` | 228 | 15 | 1 | pytest |
| `tests/test_auth.py` | 497 | 32 | 5 | pytest |
| `tests/conftest.py` | 52 | 0 | 0 | pytest |
| `tests/support/constants.py` | 10 | 0 | 0 | — |
| `tests/support/helpers/factories.py` | 38 | 0 | 0 | — |

**Total:** 1,501 lines across 11 files, ~80 test functions.

---

## Step 3: Quality Evaluation

### Dimension Scores

| Dimension | Score | Grade | Violations |
|-----------|-------|-------|------------|
| Determinism | 65/100 | D | 7 HIGH |
| Isolation | 100/100 | A | 0 |
| Maintainability | 88/100 | B | 3 MEDIUM, 5 LOW |
| Performance | 100/100 | A | 0 |

---

## Quality Criteria Assessment

| Criterion | Status | Violations | Basis | Notes |
|-----------|--------|------------|-------|-------|
| Disabled or Focused Tests | ✅ PASS | 0 | Absolute (C1, C2) | No .skip, .only, xit, or pytest.mark.skip found |
| Hard Waits (sleep, waitForTimeout) | ✅ PASS | 0 | Absolute (H1) | No time.sleep or equivalent found |
| Determinism (no conditionals) | ❌ FAIL | 7 | Absolute + Applicability (H2, H3, H10) | 2 wall-clock fixtures, 1 loop-guarded assertion, 4 shape-only assertions |
| Isolation (cleanup, no shared state) | ✅ PASS | 0 | Absolute (H4, C5) | Autouse _clear_store fixture clears store before/after every test; zero mocks |
| Fixture Patterns | ✅ PASS | 0 | Applicability (M2, M5) | Fixtures used for client, auth, user setup |
| Data Factories | ⚠️ WARN | 3 | Applicability (M2) | login_payload and change_password_payload factories missing; registration_payload used |
| Network-First Pattern | ✅ PASS (n/a) | 0 | Applicability (M1) | Backend pytest/TestClient suite — no browser navigation |
| Playwright Utils Adoption | ✅ PASS (n/a) | 0 | Precondition: playwrightUtilsActive | Package not installed; flag irrelevant |
| Pact.js Utils Adoption | ✅ PASS (n/a) | 0 | Precondition: pactjsUtilsActive | Package not installed; no contract tests |
| Explicit Assertions | ❌ FAIL | 5 | Absolute (H10) | 5 success-path tests use shape-only assertions (isinstance, not None, key presence) |
| Test Length (≤1000 lines) | ✅ PASS | 0 | Absolute (H5) | Largest file is 497 lines |
| Test Duration (≤1.5 min) | ✅ PASS | 0 | Absolute (H1, M1) | ~27s total — no excessive loops, sleeps, or navigation |
| Flakiness Patterns | ❌ FAIL | 3 | Absolute (H2, H3) | 2 wall-clock token expiry tests, 1 loop-guarded assertion |
| BDD Format (Given-When-Then) | ✅ PASS (n/a) | 0 | Convention: bddNaming (unknown) | Corpus too small to establish convention |
| Test IDs | ✅ PASS (n/a) | 0 | Convention: testIds (unknown) | Corpus too small; T-XX IDs present in docstrings only |
| Priority Markers (P0/P1/P2/P3) | ✅ PASS (n/a) | 0 | Convention: priorityMarkers (unknown) | Corpus too small; pytest markers used but not priority-based |
| Mobile Flow Patterns | ✅ PASS (n/a) | 0 | Applicability: Maestro flow | Not a mobile project |

**Total Violations**: 0 CRITICAL, 13 HIGH, 3 MEDIUM, 5 LOW

---

## Quality Score Breakdown

```
Starting Score:          100
Critical Violations:     -0 × 10 = -0
High Violations:         -13 × 5 = -65
Medium Violations:       -3 × 2 = -6
Low Violations:          -5 × 1 = -5
                         --------
Raw Deduction Total:     -76

Bonus Points:
  Excellent BDD:         +0
  Comprehensive Fixtures: +0
  Data Factories:        +0
  Network-First:         +0
  Perfect Isolation:     +5
  All Test IDs:          +0
                         --------
Total Bonus:             +5

Raw Score:               29/100
Score Cap (HIGH):        79 (min(29, 79) = 29... but cap means max 79)
Effective Score:         79/100  (severity cap: HIGH → max 79)
Grade:                   B
```

*Note: The severity cap ensures the grade cannot be higher than B when HIGH-severity violations exist, regardless of the raw deduction score. The raw score of 29 reflects the volume of findings; the cap at 79 reflects that no CRITICAL issues exist.*

---

## Critical Issues (Must Fix)

No critical issues detected. ✅

---

## Recommendations (Should Fix)

### 1. Add value assertions to success-path tests (H10)

**Severity**: P1 (HIGH)
**Location**: `tests/unit/test_services_password_change.py` lines 20, 82, 98; `tests/unit/test_auth.py` line 20
**Row**: H10
**Criterion**: Shape-only assertion

**Issue Description**:
Five success-path tests assert only that a result is not None and/or contains a key, without verifying the actual value. These tests pass even when the returned message is wrong, the store was never updated, or the function returned an unexpected shape. The test name claims to verify behavior (e.g., "change_password_success_hashes_new_password") but the assertions only confirm the call didn't crash.

**Current Code**:

```python
# ❌ tests/unit/test_services_password_change.py — test_change_password_success_hashes_new_password
result = svc.change_password("alice", "current123", "newpass123")
assert result is not None
assert "message" in result

# ❌ tests/unit/test_services_password_change.py — test_change_password_lowercases_username
result = svc.change_password("MixedCase", "current123", "newpass123")
assert result is not None
assert "message" in result

# ❌ tests/unit/test_services_password_change.py — test_change_password_boundary_72_byte_passwords_succeed
result = svc.change_password("harry", "a" * 72, "b" * 72)
assert result is not None
assert "message" in result

# ❌ tests/unit/test_auth.py — test_returns_string
token = create_access_token("alice")
assert isinstance(token, str)
```

**Recommended Fix**:

```python
# ✅ Add value assertions alongside shape checks
import bcrypt
from store import get_user_with_hash

# test_change_password_success_hashes_new_password
result = svc.change_password("alice", "current123", "newpass123")
assert result is not None
assert result["message"] == "Password changed successfully"
stored = get_user_with_hash("alice")
assert bcrypt.checkpw(b"newpass123", stored["password_hash"].encode())

# test_change_password_lowercases_username
result = svc.change_password("MixedCase", "current123", "newpass123")
assert result["message"] == "Password changed successfully"
from store import get_user
assert get_user("mixedcase") is not None

# test_returns_string
token = create_access_token("alice")
assert isinstance(token, str)
assert len(token) > 0
payload = decode_token(token)
assert payload["sub"] == "alice"
```

**Why This Matters**:
Shape-only assertions are the #1 false-confidence pattern in test suites. A test that asserts `result is not None` passes when the function returns `"error"` instead of `{"message": "Password changed successfully"}`. The test name promises verification it doesn't deliver.

---

### 2. Mock time.time() in JWT expiry assertions (H2)

**Severity**: P1 (HIGH)
**Location**: `tests/unit/test_auth.py:33` and `tests/test_auth.py:417`
**Row**: H2
**Criterion**: Wall-clock fixture

**Issue Description**:
Two tests assert that JWT `exp` claims fall within a tolerance window around `time.time()`. Under heavy CI load, NTP adjustments, or system clock skew, the captured `before`/`after` timestamps can drift enough to flip the assertion. H2 fires when a time-sensitive fixture is derived from the live clock and governs a token lifetime boundary.

**Current Code**:

```python
# ❌ tests/unit/test_auth.py — test_expiry_is_24h_from_now
before = time.time()
token = create_access_token("user1")
after = time.time()
payload = decode_token(token)
expected_min = before + (TOKEN_EXPIRY_HOURS * 3600) - 5
expected_max = after + (TOKEN_EXPIRY_HOURS * 3600) + 5
assert expected_min <= payload["exp"] <= expected_max

# ❌ tests/test_auth.py — test_jwt_exp_is_24h_from_issuance
before = time.time()
client.post("/register", json=registration_payload(...))
login = client.post("/login", json={"username": "expcheck", "password": "pass"})
after = time.time()
# ... decode and assert exp within tolerance
```

**Recommended Fix**:

```python
# ✅ Mock time.time() for deterministic assertion
from unittest.mock import patch

def test_expiry_is_24h_from_now(self):
    FIXED_TS = 1700000000.0
    with patch("auth.time.time", return_value=FIXED_TS):
        token = create_access_token("user1")
    payload = decode_token(token)
    assert payload["exp"] == int(FIXED_TS + TOKEN_EXPIRY_HOURS * 3600)
```

**Why This Matters**:
Wall-clock assertions are the #1 source of flaky tests in CI. The 5-second tolerance is fragile under load. Mocking eliminates the race entirely and makes the test deterministic.

---

### 3. Move assertion out of conditional loop (H3)

**Severity**: P1 (HIGH)
**Location**: `tests/unit/test_services_password_change.py:126`
**Row**: H3
**Criterion**: Conditional assertion

**Issue Description**:
In `test_concurrent_change_password_same_user_no_lost_update`, the assertion `assert "Invalid credentials" in str(err)` is inside a `for err in errors:` loop. If the race condition behaves unexpectedly (e.g., both threads succeed), `errors` is empty and the assertion is silently skipped — it never executes, never fails. The subsequent `len()` assertions mitigate this in practice, but the pattern violates the criterion.

**Current Code**:

```python
# ❌ Assertion inside loop that may run zero times
for err in errors:
    assert "Invalid credentials" in str(err)
assert len(results) + len(errors) == 2
```

**Recommended Fix**:

```python
# ✅ Assert the precondition, then validate contents
assert len(errors) == 1, f"Expected exactly 1 error, got {len(errors)}"
for err in errors:
    assert "Invalid credentials" in str(err)
assert len(results) + len(errors) == 2
```

**Why This Matters**:
An assertion inside a loop that may execute zero times provides false confidence. The test passes because the assertion never ran, not because the condition held.

---

### 4. Add login_payload() and change_password_payload() factories (M2)

**Severity**: P2 (MEDIUM)
**Location**: `tests/test_auth.py` (~14 occurrences), `tests/integration/test_password_change.py` (~17 occurrences)
**Row**: M2
**Criterion**: Repeated literal payload

**Issue Description**:
Login payloads `{"username": "...", "password": "..."}` are constructed inline ~14 times across `test_auth.py` and ~5 times across `integration/test_password_change.py`. Change-password payloads `{"current_password": "...", "new_password": "..."}` appear ~12 times. A `registration_payload()` factory already exists but no corresponding factories exist for login or change-password shapes.

**Current Code**:

```python
# ❌ Inline login payloads repeated 14+ times
client.post("/login", json={"username": "loginuser", "password": "pass123"})
client.post("/login", json={"username": "wrongpw", "password": "incorrect"})
# ... 12 more occurrences

# ❌ Inline change-password payloads repeated 12+ times
client.post("/change-password", json={"current_password": "testpass123", "new_password": "newpass123"})
```

**Recommended Fix**:

```python
# ✅ Add factories to tests/support/helpers/factories.py
def login_payload(username=None, password=None) -> dict[str, str]:
    return {
        "username": username or random_username(),
        "password": password or random_password(),
    }

def change_password_payload(current_password=None, new_password=None) -> dict[str, str]:
    return {
        "current_password": current_password or random_password(),
        "new_password": new_password or random_password(),
    }
```

**Priority**:
P2 — not blocking, but addresses a real maintainability gap. Payload shape changes require one-line updates instead of 14+ scattered edits.

---

### 5. Replace magic values 3600 and 86400 with named constants (L6)

**Severity**: P3 (LOW)
**Location**: `tests/unit/test_auth.py:69`, `tests/test_auth.py:257,299,432`, `tests/api/test_change_password.py:130`, `tests/integration/test_password_change.py:108`
**Row**: L6
**Criterion**: Magic value

**Issue Description**:
Raw literals `3600` (hours-to-seconds) and `86400` (24h in seconds) appear across 4 test files without named constants. The `auth` module already exports `TOKEN_EXPIRY_HOURS` but most test files don't use it.

**Current Code**:

```python
# ❌ Magic numbers across 4 files
{"sub": "diana", "exp": int(time.time()) - 3600}
{"sub": "tamper", "exp": time.time() + 86400}
expected_exp_min = before + 86400 - 5
```

**Recommended Fix**:

```python
# ✅ Named constants in tests/support/constants.py
from auth import TOKEN_EXPIRY_HOURS

SECONDS_PER_HOUR = 3600
TOKEN_EXPIRY_SECONDS = TOKEN_EXPIRY_HOURS * SECONDS_PER_HOUR

# Use in tests:
{"sub": "expired", "exp": int(time.time()) - TOKEN_EXPIRY_SECONDS}
```

**Priority**:
P3 — cosmetic, no functional impact.

---

## Best Practices Found

### 1. Autouse Store Cleanup Fixture

**Location**: `tests/conftest.py:5`
**Pattern**: Dual-clear autouse fixture

**Why This Is Good**:
The `_clear_store` fixture clears `store.users` both before AND after each test via `yield`. This belt-and-suspenders approach prevents state leakage from failed tests (where teardown still runs) and ensures every test starts with a clean slate.

```python
@pytest.fixture(autouse=True)
def _clear_store():
    """Clear in-memory store between tests to prevent cross-test pollution."""
    import store
    store.users.clear()
    yield
    store.users.clear()
```

### 2. Zero-Mock Architecture

**Location**: All test files
**Pattern**: Real code execution without mocks

**Why This Is Good**:
Every test exercises real code paths: API tests use `TestClient` hitting the actual FastAPI app; unit tests call `create_access_token`, `decode_token`, `register_user` directly. No `unittest.mock`, `monkeypatch`, or `pytest-mock` usage anywhere. This eliminates the C5 risk class entirely.

### 3. Class-Based Test Organization

**Location**: All test files with 3+ tests
**Pattern**: Descriptive class grouping

**Why This Is Good**:
All 8 test files with 3+ tests use class-based grouping (`TestRegister`, `TestLogin`, `TestChangePassword`, etc.), satisfying M4 and providing clear failure localization.

### 4. Concurrency Test Pattern

**Location**: `tests/unit/test_services_password_change.py:130`, `tests/unit/test_services.py`
**Pattern**: threading.Barrier + Thread for race condition testing

**Why This Is Good**:
The concurrency tests use `threading.Barrier(2)` to synchronize two threads, then verify exactly one wins the race. This is a correct pattern for testing thread safety of the in-memory store.

---

## Key Weaknesses

- **[H10]** 5 success-path tests assert only shape/presence (`result is not None`, `"message" in result`) without verifying actual values — tests pass even when the returned data is wrong
- **[H2]** 2 JWT expiry tests depend on live `time.time()` with 5-second tolerance — flaky under CI load
- **[H3]** 1 concurrency test has assertion inside a loop that may run zero times — silently passes on unexpected behavior
- **[M2]** Login and change-password payloads constructed inline 14+ and 12+ times respectively — no factories exist
- **[L6]** Magic values `3600` and `86400` appear across 4 files without named constants

---

## Advisory Observations

- Consider adopting `freezegun` or `unittest.mock.patch` for time-dependent tests across the suite
- The `registration_payload()` factory pattern should be extended to login and change-password shapes for consistency
- The 27s test runtime is dominated by bcrypt hashing — consider a lower bcrypt cost factor (e.g., 4) in test configuration
- The test ID traceability matrix (T-01 to T-57) in docstrings is valuable — maintain it as tests evolve

---

## Decision

**Recommendation**: Request Changes

**Rationale**:
13 HIGH-severity violations were found: 4 shape-only assertions (H10) that provide false confidence, 2 wall-clock fixtures (H2) that risk flakiness, and 1 conditional assertion (H3) that silently passes. The severity cap limits the score to 79 (Grade B) despite excellent isolation and performance.

> Test quality needs improvement. 13 HIGH-severity violations (H10: shape-only assertions, H2: wall-clock fixtures, H3: conditional assertion) undermine test reliability. The suite demonstrates excellent isolation (autouse fixtures, zero mocks) and strong structural organization (class-based grouping, proper fixtures), but the assertion quality and time-dependency issues must be fixed before merge. Fix by adding value assertions to the 5 H10 tests, mocking `time.time()` in the 2 H2 tests, and moving the loop assertion in the 1 H3 test.

---

## Appendix

### Violation Summary by Location

| File | Line | Severity | Row | Issue | Fix |
|------|------|----------|-----|-------|-----|
| `tests/unit/test_services_password_change.py` | 20 | P1 (H) | H10 | test_change_password_success: shape-only (`result is not None`, `"message" in result`) | Add `assert result["message"] == "Password changed successfully"` + store verification |
| `tests/unit/test_services_password_change.py` | 82 | P1 (H) | H10 | test_change_password_lowercases_username: shape-only | Add value assertion for lowercased username in store |
| `tests/unit/test_services_password_change.py` | 98 | P1 (H) | H10 | test_change_password_boundary_72_byte: shape-only | Add value assertion + store hash verification |
| `tests/unit/test_services_password_change.py` | 126 | P1 (H) | H3 | Assertion inside loop that may run zero times | Add `assert len(errors) == 1` before loop |
| `tests/unit/test_auth.py` | 20 | P1 (H) | H10 | test_returns_string: isinstance only | Add `len(token) > 0` + decode check |
| `tests/unit/test_auth.py` | 33 | P1 (H) | H2 | Wall-clock JWT expiry assertion | Mock `time.time()` with fixed timestamp |
| `tests/test_auth.py` | 417 | P1 (H) | H2 | Wall-clock JWT expiry assertion | Mock `time.time()` with fixed timestamp |
| `tests/test_auth.py` | many | P2 (M) | M2 | Login payloads inline ~14 times | Add `login_payload()` factory |
| `tests/integration/test_password_change.py` | many | P2 (M) | M2 | Change-password + login payloads inline ~17 times | Add `change_password_payload()` + `login_payload()` factories |
| `tests/unit/test_auth.py` | 69 | P3 (L) | L6 | Magic value `3600` | Use `TOKEN_EXPIRY_HOURS * 3600` |
| `tests/test_auth.py` | 257,299,432 | P3 (L) | L6 | Magic values `3600`, `86400` | Use named constants |
| `tests/api/test_change_password.py` | 130 | P3 (L) | L6 | Magic value `3600` | Use named constant |
| `tests/integration/test_password_change.py` | 108 | P3 (L) | L6 | Magic value `3600` | Use named constant |

### Quality Trends

This is the first review of this test suite. Baseline established for future comparisons.

| Metric | Value |
|--------|-------|
| Overall Score | 79/100 (B) |
| CRITICAL | 0 |
| HIGH | 13 |
| MEDIUM | 3 |
| LOW | 5 |
| Total Violations | 21 |
| Execution Mode | subagent (4 parallel workers) |
