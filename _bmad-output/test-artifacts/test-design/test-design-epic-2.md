# Test Design: Epic 2 — Password Management

**Date:** 2026-09-11
**Author:** NST
**Status:** Draft
**Branch:** `feat/password-change-api`

---

## Executive Summary

**Scope:** Epic-level test design for Epic 2 — Password Management (Story 2.1: Change Password)

**Risk Summary:**

- Total risks identified: 8 (R-09 through R-16)
- High-priority risks (≥6): 3 (R-09, R-10, R-11)
- Critical categories: SEC (3), BUS (2), TECH (1), OPS (1)

**Coverage Summary:**

- P0 scenarios: 9 (~4–6 hours)
- P1 scenarios: 5 (~2–3 hours)
- P2 scenarios: 7 (~2–3 hours)
- **Total effort**: ~21 tests, ~8–12 hours

---

## Not in Scope

| Item | Reasoning | Mitigation |
|------|-----------|------------|
| Password reset / forgot password | Explicitly deferred in PRD §5 | Out of scope per product decision |
| Password history / breach detection | Explicitly deferred in PRD §5 | Out of scope per product decision |
| Token rotation after password change | Explicitly deferred in PRD §5; existing JWT stays valid (AD-4) | Documented as assumption |
| Rate limiting on failed attempts | Not in scope for personal project | Documented as assumption (R-15) |
| Audit logging of password changes | Out of scope per PRD §6.2 | Not needed at hobby scale |
| CORS, logging, observability | Out of scope per PRD | Out of scope per architecture |

---

## Risk Assessment

### High-Priority Risks (Score ≥6)

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation | Owner | Timeline |
|---------|----------|-------------|-------------|--------|-------|------------|-------|----------|
| R-09 | SEC | Password hash leak during update — `update_password` could expose hash in response or store return | 2 | 3 | **6** | T-29, T-30, T-31: assert hash never in response; T-36: integration response shape check | Dev | Before merge |
| R-10 | BUS | Old password still works after change — user thinks they changed password but old credentials work | 2 | 3 | **6** | T-37: login with old password must return 401 after successful change | Dev | Before merge |
| R-11 | SEC | Weak password accepted — password < 8 chars stored without validation | 2 | 3 | **6** | T-34, T-38: enforce min 8 chars; T-39: boundary at exactly 8 chars | Dev | Before merge |

### Medium-Priority Risks (Score 3-5)

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation | Owner |
|---------|----------|-------------|-------------|--------|-------|------------|-------|
| R-12 | SEC | User enumeration via differential error messages — wrong password reveals whether username exists | 2 | 2 | 4 | T-43: verify same `"Invalid credentials"` message as login (AD-10) | Dev |
| R-13 | BUS | Missing fields not validated — empty or malformed request body returns unclear error | 2 | 2 | 4 | T-45, T-47, T-48, T-49: validate error shape and status codes | Dev |

### Low-Priority Risks (Score 1-2)

| Risk ID | Category | Description | Probability | Impact | Score | Action |
|---------|----------|-------------|-------------|--------|-------|--------|
| R-14 | SEC | bcrypt work factor unchanged — default cost factor is acceptable for personal project | 1 | 2 | 2 | Document |
| R-15 | OPS | No rate limiting on failed attempts — brute force possible but out of scope | 1 | 2 | 2 | Document |
| R-16 | TECH | JWT not rotated after change — stolen token stays usable until expiry | 1 | 2 | 2 | Document (by design, AD-4) |

---

## NFR Planning

| NFR | Requirement / Threshold | Risk Link | Planned Validation | Evidence Needed |
|-----|------------------------|-----------|-------------------|-----------------|
| **NFR-7** | Current password verified before accepting new one; new password ≥ 8 chars | R-10, R-11 | T-32, T-33, T-34, T-36, T-38, T-39 | pytest output: unit + integration |
| **NFR-8** | Wrong current password → 401 with `"Invalid credentials"`; weak password → 400 with length message | R-11, R-12 | T-38, T-43, T-45 | pytest: status codes + response bodies |
| **NFR-9** | `store.update_password(username, new_hash)` — dumb writer; all bcrypt in services | R-09 | T-29, T-30, T-31, T-32 | pytest: store state assertions |
| **AD-2** | Passwords hashed with bcrypt in services.py only; store never sees plaintext | R-09 | T-32, T-36 | pytest: store receives hash, not plaintext |
| **AD-5** | Consistent error shape `{"detail": str}` for all errors | R-13 | T-45 | pytest: response body shape assertions |
| **AD-9** | Current password gate; min 8 chars; no token rotation | R-10, R-11 | T-32, T-34, T-36 | pytest: full gate flow |
| **AD-10** | Wrong password → same generic message as login; no user enumeration | R-12 | T-43 | pytest: error message identical to login |
| **AD-11** | Store `update_password` is a dumb writer; bcrypt stays in services | R-09 | T-29 | pytest: store mutation is minimal |

**Unknown thresholds:** bcrypt cost factor (default), response time SLO (not defined), concurrent user limit (single-process).

---

## Entry Criteria

- [ ] PRD agreed upon by QA, Dev, PM
- [ ] Architecture document (AD-9, AD-10, AD-11) finalized
- [ ] `update_password` implemented in `store.py`
- [ ] `change_password` implemented in `services.py`
- [ ] `/change-password` route registered in `routes.py`
- [ ] `ChangePasswordRequest` model added to `models.py`
- [ ] Test environment: FastAPI TestClient available (local dev)

## Exit Criteria

- [ ] All P0 tests passing (9/9)
- [ ] All P1 tests passing (or failures triaged)
- [ ] No open high-priority / high-severity bugs
- [ ] Code coverage ≥ 80% for `services.py`, `store.py`, `routes.py`
- [ ] NFR-7, NFR-8, NFR-9 validated with evidence

---

## Test Coverage Plan

> **Note:** P0/P1/P2/P3 indicate priority, not execution timing. See Execution Strategy for when tests run.

### P0 (Critical)

**Criteria:** Security-critical paths, data integrity operations, core functionality with no workaround. Risk score is supporting evidence.

| ID | Scenario | Test Level | Risk Link | Req |
|----|----------|------------|-----------|-----|
| T-29 | `update_password` overwrites hash, keeps username/name | Unit | R-09 | NFR-9, AD-11 |
| T-32 | `change_password` success → hashes new password | Unit | R-09 | FR-1, AD-2 |
| T-33 | `change_password` wrong current → raises ValueError | Unit | R-10 | FR-2, AD-10 |
| T-34 | `change_password` weak new (< 8 chars) → raises ValueError | Unit | R-11 | FR-3, NFR-7 |
| T-36 | Valid change → HTTP 200 + success message | Integration | R-09 | FR-1 |
| T-37 | Old password no longer authenticates after change | Integration | R-10 | FR-1, SM-4 |
| T-38 | Weak new password (< 8 chars) → HTTP 400 | Integration | R-11 | FR-3, NFR-8 |
| T-40 | Missing Authorization header → HTTP 401 | Integration | — | FR-4, AD-4 |
| T-43 | Wrong current password → HTTP 401 `"Invalid credentials"` | Integration | R-12 | FR-2, AD-10 |

**Total P0:** 9 tests

### P1 (High)

**Criteria:** Core user journeys, important edge cases, boundary conditions. Material user reach.

| ID | Scenario | Test Level | Risk Link | Req |
|----|----------|------------|-----------|-----|
| T-31 | `get_user` after update returns no hash | Unit | R-09 | AD-6 |
| T-39 | Boundary: new password exactly 8 chars → HTTP 200 | Integration | R-11 | FR-3 |
| T-41 | Expired JWT → HTTP 401 | Integration | — | FR-4 |
| T-42 | Invalid JWT → HTTP 401 | Integration | — | FR-4 |
| T-44 | Existing JWT remains valid after password change | Integration | R-16 | AD-4, AD-9 |

**Total P1:** 5 tests

### P2 (Medium)

**Criteria:** Secondary flows, input validation edge cases, error shape consistency.

| ID | Scenario | Test Level | Risk Link | Req |
|----|----------|------------|-----------|-----|
| T-30 | `update_password` on nonexistent user is no-op | Unit | — | — |
| T-35 | `change_password` unknown user → raises ValueError | Unit | — | — |
| T-45 | Error shape: all errors return `{"detail": str}` | Integration | R-13 | AD-5 |
| T-46 | Username case normalization in change-password | Integration | — | AR-6 |
| T-47 | Empty body → HTTP 400/422 | Integration | R-13 | — |
| T-48 | Missing `current_password` field → HTTP 400/422 | Integration | R-13 | — |
| T-49 | Missing `new_password` field → HTTP 400/422 | Integration | R-13 | — |

**Total P2:** 7 tests

### Summary by Level

| Test Level | Count | P0 | P1 | P2 |
|------------|-------|----|----|-----|
| Unit | 7 | 4 | 1 | 2 |
| Integration | 14 | 5 | 4 | 5 |
| **Total** | **21** | **9** | **5** | **7** |

---

## Execution Strategy

**Philosophy:** Run everything in PRs if < 15 min; defer only if expensive/long.

| Gate | Tests | Est. Time | Trigger |
|------|-------|-----------|---------|
| **PR** | All P0 + P1 (T-29 through T-45) | ~2–4 min | Every push to `feat/password-change-api` |
| **Merge** | All P0 + P1 + P2 (full suite) | ~3–5 min | Before merge to `main` |
| **Nightly** | Full regression (Epic 1 + Epic 2) | ~5–8 min | Nightly CI |

---

## Resource Estimates

### Test Development Effort

| Priority | Count | Hours/Test | Total Hours | Notes |
|----------|-------|------------|-------------|-------|
| P0 | 9 | ~0.5 | ~4–6 hours | Security + core path, unit + integration |
| P1 | 5 | ~0.5 | ~2–3 hours | Boundary + auth edge cases |
| P2 | 7 | ~0.3 | ~2–3 hours | Input validation, error shapes |
| **Total** | **21** | **—** | **~8–12 hours** | **~1.5–2 days** |

### Prerequisites

**Test Data:**
- Registered user factory (register via API, return credentials + JWT)
- `conftest.py` `_clear_store` fixture (auto-cleanup between tests)

**Tooling:**
- FastAPI TestClient (already used in Epic 1 tests)
- pytest (already configured)

**Environment:**
- Local dev only; no external services

---

## Quality Gate Criteria

### Pass/Fail Thresholds

- **P0 pass rate**: 100% (no exceptions)
- **P1 pass rate**: ≥ 95% (waivers required for failures)
- **P2 pass rate**: ≥ 90% (informational)
- **High-risk mitigations**: 100% complete (R-09, R-10, R-11)

### Coverage Targets

- **Critical paths**: ≥ 80%
- **Security scenarios**: 100%
- **Business logic**: ≥ 70%
- **Edge cases**: ≥ 50%

### Non-Negotiable Requirements

- [ ] All P0 tests pass
- [ ] No high-risk (≥6) items unmitigated
- [ ] Security tests (SEC category) pass 100%
- [ ] NFR-7, NFR-8, NFR-9 validated with evidence

---

## Mitigation Plans

### R-09: Password hash leak during update (Score: 6)

**Mitigation Strategy:** Implement `update_password` as a dumb writer that only overwrites `password_hash`. Add unit tests (T-29, T-30, T-31) asserting hash never leaks in response/store return. Add integration test (T-36) asserting response contains only `{"message": ...}`.
**Owner:** Dev
**Timeline:** Before merge to `main`
**Status:** Planned
**Verification:** T-29, T-30, T-31, T-36 all pass

### R-10: Old password still works after change (Score: 6)

**Mitigation Strategy:** After successful password change (T-36), immediately attempt login with old credentials (T-37). Assert HTTP 401. This verifies the bcrypt hash was actually overwritten.
**Owner:** Dev
**Timeline:** Before merge to `main`
**Status:** Planned
**Verification:** T-37 passes

### R-11: Weak password accepted (Score: 6)

**Mitigation Strategy:** Validate new password length in `services.py` before hashing. Test at boundary (8 chars → accept, 7 chars → reject). Unit test (T-34) and integration test (T-38, T-39) cover both sides.
**Owner:** Dev
**Timeline:** Before merge to `main`
**Status:** Planned
**Verification:** T-34, T-38, T-39 all pass

---

## Assumptions and Dependencies

### Assumptions

1. Same framework, JWT setup, and in-memory store as existing API (PRD §0)
2. Current password required — user must prove knowledge before changing (PRD §4.1)
3. Minimum password length is 8 characters; no complexity rules (PRD §4.1, FR-3)
4. No password history maintained (PRD §4.1, FR-1)
5. No token rotation after password change — existing JWT stays valid (PRD §4.1, FR-1, AD-4)
6. Wrong password response does not reveal which field was wrong (PRD §4.1, FR-2, AD-10)
7. bcrypt cost factor: default (acceptable for personal project)

### Dependencies

1. `store.py` — `update_password(username, new_hash)` must be implemented
2. `services.py` — `change_password(username, current_password, new_password)` must be implemented
3. `routes.py` — `POST /change-password` endpoint must be registered
4. `models.py` — `ChangePasswordRequest` model must be defined
5. Epic 1 (Registration, Login, Get Current User) must be implemented and tested
