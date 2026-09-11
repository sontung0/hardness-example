---
workflowType: 'testarch-test-review'
stepsCompleted: ['step-01-load-context', 'step-02-discover-tests', 'step-03-quality-evaluation', 'step-03f-aggregate-scores', 'step-04-generate-report']
lastStep: 'step-04-generate-report'
lastSaved: '2025-09-22'
inputDocuments: []
---

# Test Quality Review: bmad-auth test suite

**Quality Score**: 88/100 (B - Good)
**Review Date**: 2025-09-22
**Review Scope**: suite
**Reviewer**: NST

---

Note: This review audits existing tests; it does not generate tests.
Coverage mapping and coverage gates are out of scope here. Use `trace` for coverage decisions.

## Executive Summary

**Overall Assessment**: Good

**Recommendation**: Request Changes

**Context Basis**: none

**Context Waivers Applied**: 0

### Key Strengths

✅ Excellent isolation — autouse fixture clears shared store before and after every test, zero shared mutable state leaks
✅ All 64 tests exercise real code paths with zero mocks — no mock-against-self risk (C5 structurally impossible)
✅ Comprehensive fixture architecture — dedicated `client`, `registered_user`, `auth_header`, and `delete_user_from_store` fixtures with clear docstrings
✅ Data factory adoption for registration payloads — `registration_payload()` used in 17 of 28 API tests
✅ Class-based test organization — all test files group tests into descriptive classes (`TestRegister`, `TestLogin`, `TestGetCurrentUser`, etc.)
✅ No hard waits, no disabled tests, no focused tests, no tautological assertions

### Key Weaknesses

❌ Two HIGH-severity wall-clock dependencies in JWT expiry assertions (H2) — tests can flake under CI load or clock skew
❌ Login payloads constructed inline 11+ times with no factory, despite a registration factory existing (M2)
❌ Two multi-concern tests (T-20, T-21) assert across 3 unrelated endpoints, reducing failure localization (M3)

### Summary

The test suite demonstrates strong engineering practices: excellent isolation via autouse fixtures, real code exercise without mocks, and a well-organized class-based structure. The 64 tests across 5 files cover registration, login, JWT auth, NFR scenarios, and risk-driven integration paths with clear test IDs mapping to a coverage matrix.

Two HIGH-severity findings require attention before merge: both involve `time.time()` used directly in assertions to verify JWT expiry, creating wall-clock dependencies that can flake under CI load or NTP adjustments. Three MEDIUM findings (missing login factory, two multi-concern tests) and one LOW finding (magic values) are worth addressing but do not block merge on their own.

The recommendation is **Request Changes** due to the HIGH-severity H2 violations. Fix the two wall-clock assertions by mocking `time.time()`, and address the M2/M3 findings to improve maintainability.

---

## Quality Criteria Assessment

| Criterion                            | Status                                           | Violations | Basis                          | Notes                                                              |
| ------------------------------------ | ------------------------------------------------ | ---------- | ------------------------------ | ------------------------------------------------------------------ |
| BDD Format (Given-When-Then)         | ✅ PASS (n/a)                                     | 0          | Convention: bddNaming (unknown) | Corpus too small to establish convention; no deduction             |
| Test IDs                             | ✅ PASS (n/a)                                     | 0          | Convention: testIds (unknown)   | Corpus too small; T-XX/T-AUTH-XX IDs present in docstrings only   |
| Priority Markers (P0/P1/P2/P3)       | ✅ PASS (n/a)                                     | 0          | Convention: priorityMarkers (unknown) | Corpus too small; pytest markers used but not priority-based |
| Disabled or Focused Tests            | ✅ PASS                                           | 0          | Absolute                       | No .skip, .only, xit, or pytest.mark.skip found                   |
| Hard Waits (sleep, waitForTimeout)   | ✅ PASS                                           | 0          | Absolute                       | No time.sleep or equivalent found                                 |
| Determinism (no conditionals)        | ⚠️ WARN                                           | 2          | Absolute (H2)                  | Wall-clock dependency in JWT expiry assertions                    |
| Isolation (cleanup, no shared state) | ✅ PASS                                           | 0          | Absolute                       | Autouse fixture clears store before/after every test               |
| Fixture Patterns                     | ✅ PASS                                           | 0          | Applicability                   | Fixtures used for client, auth, user setup                        |
| Data Factories                       | ⚠️ WARN                                           | 1          | Applicability (M2)             | Login payloads bypass factory pattern                             |
| Network-First Pattern                | ✅ PASS (n/a)                                     | 0          | Applicability: browser navigation | Backend pytest/TestClient suite — no browser navigation       |
| Playwright Utils Adoption            | ✅ PASS (n/a)                                     | 0          | Precondition: playwrightUtilsActive | Package not installed; flag irrelevant                       |
| Pact.js Utils Adoption               | ✅ PASS (n/a)                                     | 0          | Precondition: pactjsUtilsActive    | Package not installed; no contract tests in scope             |
| Explicit Assertions                  | ✅ PASS                                           | 0          | Absolute                       | All 64 tests contain at least one assertion                       |
| Test Length (≤1000 lines)            | ✅ PASS                                           | 599 lines  | Absolute                       | Largest file (test_auth.py) is 599 lines                          |
| Test Duration (≤1.5 min)             | ✅ PASS                                           | ~2-3s est. | Absolute                       | In-memory store, no network — fast execution                      |
| Flakiness Patterns                   | ⚠️ WARN                                           | 2          | Absolute (H2)                  | Same wall-clock findings as Determinism                           |

**Total Violations**: 0 Critical, 2 High, 3 Medium, 1 Low

**Convention Baseline**: unavailable: all test files are within the review set; corpus outside review set has 0 files

---

## Quality Score Breakdown

```
Starting Score:          100
Critical Violations:     -0 × 10 = -0
High Violations:         -2 × 5 = -10
Medium Violations:       -3 × 2 = -6
Low Violations:          -1 × 1 = -1

Bonus Points:
  Excellent BDD:         +0
  Comprehensive Fixtures: +0
  Data Factories:        +0
  Network-First:         +0
  Perfect Isolation:     +5
  All Test IDs:          +0
                         --------
Total Bonus:             +5

Final Score:             88/100
Grade:                   B
```

---

## Critical Issues (Must Fix)

No critical issues detected. ✅

---

## Recommendations (Should Fix)

### 1. Mock time.time() in JWT expiry assertions (H2)

**Severity**: P1 (High)
**Location**: `tests/test_auth.py:311` and `tests/unit/test_auth.py:36`
**Row**: H2
**Criterion**: Wall-clock fixture

**Issue Description**:
Two tests assert that JWT `exp` claims fall within a tolerance window around `time.time()`. Under heavy CI load, NTP adjustments, or system clock skew, the captured `before`/`after` timestamps can drift enough to flip the assertion. H2 fires when a time-sensitive fixture is derived from the live clock and governs a token lifetime boundary.

**Current Code**:

```python
# ❌ tests/test_auth.py — T-25
def test_jwt_exp_is_24h_from_issuance(self, client):
    before = time.time()
    client.post("/register", json=registration_payload(...))
    login = client.post("/login", json={"username": "expcheck", "password": "pass"})
    after = time.time()
    from auth import SECRET_KEY
    token = login.json()["access_token"]
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    expected_exp_min = before + 86400 - 5
    expected_exp_max = after + 86400 + 5
    assert expected_exp_min <= payload["exp"] <= expected_exp_max
```

**Recommended Fix**:

```python
# ✅ Mock time.time() for deterministic assertion
from unittest.mock import patch

def test_jwt_exp_is_24h_from_issuance(self, client):
    FIXED_TS = 1700000000.0
    with patch("time.time", return_value=FIXED_TS):
        client.post("/register", json=registration_payload(
            username="expcheck", password="pass", name="EC"))
    login = client.post("/login", json={"username": "expcheck", "password": "pass"})
    from auth import SECRET_KEY
    token = login.json()["access_token"]
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    assert payload["exp"] == int(FIXED_TS + 86400)
```

**Why This Matters**:
Wall-clock assertions are the #1 source of flaky tests in CI. The 5-second tolerance is fragile under load. Mocking eliminates the race entirely and makes the test deterministic.

**Related Violations**:
Same pattern in `tests/unit/test_auth.py` TestCreateAccessToken.test_expiry_is_24h_from_now (line ~36).

---

### 2. Add login_payload() factory (M2)

**Severity**: P2 (Medium)
**Location**: `tests/test_auth.py` (11 inline occurrences)
**Row**: M2
**Criterion**: Repeated literal payload

**Issue Description**:
Login payloads `{"username": "...", "password": "..."}` are constructed inline 11+ times across TestLogin, TestNFR, and TestRiskDriven. A `registration_payload()` factory already exists in `tests/support/helpers/factories.py` and is used consistently for registration. The login payload shape lacks a corresponding factory, creating inconsistency and making payload changes error-prone.

**Current Code**:

```python
# ❌ Inline login payloads repeated 11+ times
response = client.post("/login", json={"username": "loginuser", "password": "pass123"})
response = client.post("/login", json={"username": "wrongpw", "password": "incorrect"})
response = client.post("/login", json={"username": "nobody", "password": "pass"})
# ... 8 more occurrences
```

**Recommended Fix**:

```python
# ✅ Add login_payload factory to tests/support/helpers/factories.py
def login_payload(username=None, password=None) -> dict[str, str]:
    """Build a login payload with optional overrides."""
    return {
        "username": username or random_username(),
        "password": password or random_password(),
    }

# Use in tests:
response = client.post("/login", json=login_payload(username="loginuser", password="pass123"))
```

**Benefits**:
Single source of truth for login payload shape. Future changes (e.g., adding a `device_id` field) require one-line update instead of 11+ scattered edits.

**Priority**:
P2 — not blocking, but addresses a real maintainability gap.

---

### 3. Split multi-concern tests T-20 and T-21 (M3)

**Severity**: P2 (Medium)
**Location**: `tests/test_auth.py:236` (T-20) and `tests/test_auth.py:262` (T-21)
**Row**: M3
**Criterion**: Multi-concern test

**Issue Description**:
T-20 (test_password_hash_never_in_any_response) asserts across 3 endpoints (register, login, /me) with 8 assertions spanning 3 unrelated HTTP interactions. T-21 (test_error_shape_always_detail_string) asserts error shapes across 3 endpoints with 9 assertions. When either fails, the failure message does not localize to the offending endpoint.

**Current Code**:

```python
# ❌ T-20 tests 3 endpoints in one test
def test_password_hash_never_in_any_response(self, client):
    reg = client.post("/register", json=registration_payload(...))
    assert "password_hash" not in reg.json()
    login = client.post("/login", json={"username": "nfr20", "password": "pass"})
    assert "password_hash" not in login.json()
    token = login.json()["access_token"]
    me = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert "password_hash" not in me.json()
```

**Recommended Fix**:

```python
# ✅ Split into endpoint-focused tests
class TestPasswordNeverExposed:
    """Password hash must never appear in any API response."""

    def test_register_response_omits_password_hash(self, client):
        response = client.post("/register", json=registration_payload(...))
        assert "password_hash" not in response.json()
        assert "password" not in response.json()

    def test_login_response_omits_password_hash(self, client):
        client.post("/register", json=registration_payload(...))
        response = client.post("/login", json={"username": "nfr20", "password": "pass"})
        assert "password_hash" not in response.json()

    def test_me_response_omits_password_hash(self, client, registered_user, auth_header):
        response = client.get("/me", headers=auth_header)
        assert "password_hash" not in response.json()
        assert "password" not in response.json()
```

**Benefits**:
Each test name clearly identifies which endpoint's contract it validates. Failures localize instantly. The cross-cutting documentation intent is preserved via class grouping.

**Priority**:
P2 — improves failure localization without blocking merge.

---

### 4. Extract magic values in T-25 (L6)

**Severity**: P3 (Low)
**Location**: `tests/test_auth.py:350`
**Row**: L6
**Criterion**: Magic value

**Issue Description**:
The literal `86400` (24h in seconds) and `5` (tolerance) appear without named constants. While 86400 is recognizable, the tolerance value is arbitrary and unexplained.

**Current Code**:

```python
# ❌ Magic numbers
expected_exp_min = before + 86400 - 5
expected_exp_max = after + 86400 + 5
```

**Recommended Fix**:

```python
# ✅ Named constants
TOKEN_TTL_SECONDS = 86400   # 24 hours
EXPIRY_TOLERANCE_SECONDS = 5  # clock-skew tolerance

expected_exp_min = before + TOKEN_TTL_SECONDS - EXPIRY_TOLERANCE_SECONDS
expected_exp_max = after + TOKEN_TTL_SECONDS + EXPIRY_TOLERANCE_SECONDS
```

**Benefits**:
Self-documenting code. The purpose of each literal is clear without reading surrounding context.

**Priority**:
P3 — cosmetic, no functional impact.

---

## Best Practices Found

### 1. Autouse Store Cleanup Fixture

**Location**: `tests/conftest.py:5`
**Pattern**: Dual-clear autouse fixture

**Why This Is Good**:
The `_clear_store` fixture clears `store.users` both before AND after each test via `yield`. This belt-and-suspenders approach prevents state leakage from failed tests (where teardown still runs) and ensures every test starts with a clean slate.

**Code Example**:

```python
# ✅ Excellent isolation pattern
@pytest.fixture(autouse=True)
def _clear_store():
    """Clear in-memory store between tests to prevent cross-test pollution."""
    import store
    store.users.clear()
    yield
    store.users.clear()
```

**Use as Reference**:
This pattern should be adopted for any shared mutable state in future test fixtures.

---

### 2. Test ID Traceability Matrix

**Location**: `tests/test_auth.py:1-9` (docstring)
**Pattern**: Test IDs mapped to requirements

**Why This Is Good**:
The test file header maps test IDs (T-01 to T-28) to functional requirements (FR-1, FR-2, FR-3, NFR, Risk-driven). This creates traceability from requirements to test execution without external tooling.

**Code Example**:

```python
"""
Test IDs map to coverage matrix in test-design-qa.md:
  T-01 to T-08:  FR-1 — Registration
  T-09 to T-13:  FR-2 — Login
  T-14 to T-19:  FR-3 — Get current user
  T-20 to T-25:  NFR scenarios
  T-26 to T-28:  Risk-driven scenarios
"""
```

**Use as Reference**:
Maintain this mapping as tests evolve. It's the fastest way to answer "do we have a test for X?" during code review.

---

### 3. Zero-Mock Architecture

**Location**: All test files
**Pattern**: Real code execution without mocks

**Why This Is Good**:
Every test exercises real code paths: API tests use `TestClient` hitting the actual FastAPI app; unit tests call `create_access_token`, `decode_token`, `register_user` directly. No `unittest.mock`, `monkeypatch`, or `pytest-mock` usage anywhere. This eliminates the C5 risk class entirely and ensures tests validate actual behavior, not mock configuration.

**Use as Reference**:
Continue this approach for the auth domain. Mocks should only be introduced when external dependencies (databases, APIs, filesystem) cannot be avoided.

---

## Test File Analysis

### File Metadata

| File                          | Lines | Tests | Classes | Framework   |
| ----------------------------- | ----- | ----- | ------- | ----------- |
| `tests/conftest.py`           | 51    | 0     | 0       | pytest      |
| `tests/test_auth.py`          | 599   | 28    | 5       | pytest      |
| `tests/unit/test_auth.py`     | 188   | 18    | 3       | pytest      |
| `tests/unit/test_services.py` | 54    | 8     | 3       | pytest      |
| `tests/unit/test_store.py`    | 55    | 10    | 4       | pytest      |
| `tests/support/constants.py`  | 6     | 0     | 0       | —           |
| `tests/support/helpers/factories.py` | 45 | 0 | 0    | —           |

### Test Structure

- **Total Test Cases**: 64
- **Average Test Length**: ~10 lines per test
- **Fixtures Used**: 5 (`_clear_store`, `client`, `registered_user`, `auth_header`, `delete_user_from_store`)
- **Data Factories**: 1 (`registration_payload`) — login factory missing

### Test Scope

- **Test IDs**: T-01 to T-28 (API), T-AUTH-01 to T-AUTH-18 (unit auth), unnumbered (unit services/store)
- **pytest Markers**: `@pytest.mark.api` (28 tests), `@pytest.mark.unit` (36 tests)

### Assertions Analysis

- **Total Assertions**: ~130+
- **Assertions per Test**: ~2 (avg)
- **Assertion Types**: `assert ... ==`, `assert ... in`, `assert ... not in`, `pytest.raises`, `isinstance`

---

## Context and Integration

### What the Context Said

No context was supplied. This review judged the tests on their construction quality, not on whether they match a specific requirement. The test ID traceability matrix (T-01 to T-28) maps to a test design document, but that document was not provided for this review.

---

## Knowledge Base References

This review consulted the following knowledge base fragments:

- **test-quality.md** — Definition of Done for tests (no hard waits, ≤1000 lines, <1.5 min, self-cleaning)
- **data-factories.md** — Factory functions with overrides, API-first setup
- **test-levels-framework.md** — E2E vs API vs Unit test appropriateness
- **selective-testing.md** — Duplicate coverage detection

See [tea-index.csv](../../../.claude/skills/bmad-testarch-test-review/resources/tea-index.csv) for complete knowledge base.

---

## Next Steps

### Immediate Actions (Before Merge)

1. **Mock time.time() in JWT expiry assertions** — Fix H2 violations in T-25 and test_expiry_is_24h_from_now
   - Priority: P1
   - Owner: Developer
   - Estimated Effort: 30 minutes

2. **Add login_payload() factory** — Eliminate 11 inline login payload constructions
   - Priority: P2
   - Owner: Developer
   - Estimated Effort: 15 minutes

### Follow-up Actions (Future PRs)

1. **Split multi-concern tests T-20 and T-21** — Improve failure localization
   - Priority: P2
   - Target: Next sprint

2. **Extract magic values in T-25** — Named constants for 86400 and 5
   - Priority: P3
   - Target: Backlog

### Re-Review Needed?

⚠️ Re-review after P1 fixes — request changes for H2 violations, then re-review

---

## Decision

**Recommendation**: Request Changes

**Rationale**:
Two HIGH-severity (H2) wall-clock dependencies in JWT expiry assertions create flakiness risk under CI load or clock skew. These must be fixed before merge. Three MEDIUM findings (missing login factory, two multi-concern tests) and one LOW finding (magic values) are worth addressing but do not block merge independently.

> Test quality needs improvement with 88/100 score. Two HIGH-severity violations (H2 — wall-clock fixture) pose flakiness risks and must be fixed before merge. The suite demonstrates excellent isolation and real-code execution practices, but the time-dependent assertions undermine reliability. Fix by mocking `time.time()` in the two affected tests, then re-review.

---

## Appendix

### Violation Summary by Location

| Line   | Severity | Criterion | Issue                                    | Fix                                        |
| ------ | -------- | --------- | ---------------------------------------- | ------------------------------------------ |
| ~311   | P1 (H)   | H2        | T-25: wall-clock JWT expiry assertion    | Mock time.time() for deterministic check   |
| ~36    | P1 (H)   | H2        | test_expiry: wall-clock JWT expiry assertion | Mock time.time() for deterministic check |
| 113+   | P2 (M)   | M2        | Login payloads repeated inline 11x       | Add login_payload() factory                |
| 236    | P2 (M)   | M3        | T-20: multi-concern (3 endpoints)        | Split into endpoint-focused tests          |
| 262    | P2 (M)   | M3        | T-21: multi-concern (3 endpoints)        | Split into endpoint-focused tests          |
| 350    | P3 (L)   | L6        | Magic values 86400 and 5                 | Extract to named constants                 |

### Quality Trends

This is the first review of this test suite. Establish a baseline for future comparisons.
