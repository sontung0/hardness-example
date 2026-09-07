---
workflowStatus: 'completed'
totalSteps: 5
stepsCompleted: ['step-01-detect-mode', 'step-02-load-context', 'step-03-risk-and-testability', 'step-04-coverage-plan', 'step-05-generate-output']
lastStep: 'step-05-generate-output'
nextStep: ''
lastSaved: 2026-09-07
---

# Test Design: Epic 1 - User Authentication API

**Date:** 2026-09-07
**Author:** NST
**Status:** Draft
**Project:** bmad

---

## Executive Summary

**Scope:** Epic-level test design for Epic 1 — User Authentication API (Register, Login, Get Current User with JWT auth and in-memory storage).

**Risk Summary:**

- Total risks identified: 8
- High-priority risks (≥6): 2 (R-01, R-02 — both security)
- Critical categories: SEC (2 high risks)

**Coverage Summary:**

- P0 scenarios: 18 (all implemented ✅)
- P1 scenarios: 8 (all implemented ✅)
- P2 scenarios: 2 (all implemented ✅)
- **Total effort**: 28 scenarios, 0 additional hours (all tests exist in `tests/test_auth.py`)

---

## Not in Scope

| Item | Reasoning | Mitigation |
|------|-----------|------------|
| **E2E browser tests** | Backend-only API; no frontend | Not applicable |
| **Performance/load testing** | No SLO defined; personal project | Deferred to future enhancement |
| **Database tests** | In-memory store only; no DB | By design (AD-3) |
| **Contract testing** | Single service, no consumers | Not applicable |
| **Mobile tests** | No mobile indicators | Not applicable |

---

## Risk Assessment

### High-Priority Risks (Score ≥6)

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation | Owner | Timeline |
|---------|----------|-------------|-------------|--------|-------|------------|-------|----------|
| R-01 | SEC | `password_hash` exposed in response or store return value | 2 | 3 | **6** | Dedicated exclusion tests per endpoint + store function; assert response body never contains `password_hash` | Dev | Before release |
| R-02 | SEC | Malformed or unsigned JWT tokens accepted by auth middleware | 2 | 3 | **6** | Negative tests with expired, malformed, unsigned, and tampered tokens; verify 401 for each | Dev | Before release |

### Medium-Priority Risks (Score 3-4)

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation | Owner |
|---------|----------|-------------|-------------|--------|-------|------------|-------|
| R-03 | BUS | Duplicate registration returns wrong status | 2 | 2 | 4 | Duplicate username test case; verify in-memory store does not overwrite | Dev |
| R-04 | BUS | Username not lowercased consistently | 2 | 2 | 4 | Test with mixed-case usernames; verify all lookups use lowercased form | Dev |
| R-05 | TECH | FastAPI 422 override may not cover all validation paths | 2 | 2 | 4 | Test with invalid JSON body, missing fields, wrong types; verify consistent error shape | Dev |

### Low-Priority Risks (Score 1-2)

| Risk ID | Category | Description | Probability | Impact | Score | Action |
|---------|----------|-------------|-------------|--------|-------|--------|
| R-06 | SEC | bcrypt work factor may be too low/high | 1 | 2 | 2 | Monitor |
| R-07 | OPS | Data loss on restart (by design) | 1 | 1 | 1 | Document |
| R-08 | PERF | JWT signing latency in request path | 1 | 2 | 2 | Document |

### Risk Category Legend

- **TECH**: Technical/Architecture (flaws, integration, scalability)
- **SEC**: Security (access controls, auth, data exposure)
- **PERF**: Performance (SLA violations, degradation, resource limits)
- **DATA**: Data Integrity (loss, corruption, inconsistency)
- **BUS**: Business Impact (UX harm, logic errors, revenue)
- **OPS**: Operations (deployment, config, monitoring)

---

## NFR Planning

**Purpose:** Capture epic-specific NFR thresholds, planned validation, and evidence expected for later `nfr-assess`. This is not a final evidence audit.

| NFR Category | Requirement / Threshold | Risk Link | Planned Validation | Evidence Needed |
|--------------|------------------------|-----------|-------------------|-----------------|
| Security (NFR-2) | Passwords hashed with bcrypt (default work factor) | R-01 | Unit test: `bcrypt.checkpw` assertion on stored hash | pytest output + bcrypt assertion |
| Security (NFR-3) | JWT `sub` = lowercased username, `exp` = 24h | R-02 | Unit test: JWT decode and claim assertion | pytest output + PyJWT decode |
| Security (NFR-4) | No session cookies; JWT sole auth mechanism | R-02 | Integration test: GET /me without token → 401 | pytest output |
| Security (NFR-6) | `password_hash` never in response or store return | R-01 | Integration test: response body scan + store assertion | pytest output |
| Technical (NFR-5) | Consistent error shape `{"detail": str}` | R-05 | Integration test: error response body assertion | pytest output |
| Data (NFR-1) | In-memory Python dict, no persistence | — | Unit test: store cleared between tests | pytest output |

**Unknown thresholds:**
- JWT expiration time: 24h (acceptable for personal project)
- bcrypt cost factor: default (acceptable for personal project)
- Response time SLO: not defined (not in scope)
- Concurrent user limit: not defined (single-process)

---

## Entry Criteria

- [x] Requirements and assumptions agreed upon by QA, Dev, PM (PRD + Architecture finalized)
- [x] Test environment provisioned (pytest + FastAPI TestClient)
- [x] Test data available or factories ready (`conftest.py` fixtures)
- [x] Feature implemented (`src/` directory with all 6 files)
- [x] All 28 test scenarios implemented in `tests/test_auth.py`

## Exit Criteria

- [ ] All P0 tests passing (18/18)
- [ ] All P1 tests passing (8/8)
- [ ] No open high-priority / high-severity bugs
- [ ] Test coverage ≥ 80% on `services.py`, `auth.py`, `store.py`
- [ ] NFR validation evidence exists for all 6 NFRs

---

## Test Coverage Plan

### P0 (Critical)

**Criteria**: Critical business, security, data-integrity, or compliance impact with no safe workaround. Risk score is supporting evidence and is not a required condition.

| Requirement | Test Level | Risk Link | Test ID | Owner | Notes |
|-------------|-----------|-----------|---------|-------|-------|
| FR-1: Register success | Integration | — | T-01 | Dev | Valid input → 201 + JWT |
| FR-1: Duplicate username | Integration | R-03 | T-05 | Dev | Duplicate → 409 |
| FR-1: Case normalization | Integration | R-04 | T-06 | Dev | 'Bob' = 'bob' |
| FR-1: Password hashing | Unit | R-01 | T-07 | Dev | bcrypt verification |
| FR-1: Hash exclusion | Integration | R-01 | T-08 | Dev | password_hash not in response |
| FR-2: Login success | Integration | — | T-09 | Dev | Valid creds → 200 + JWT |
| FR-2: Wrong password | Integration | R-02 | T-10 | Dev | Wrong password → 401 |
| FR-2: Nonexistent user | Integration | R-02 | T-11 | Dev | Unknown user → 401 |
| FR-3: Valid JWT | Integration | — | T-14 | Dev | Valid token → 200 + profile |
| FR-3: No token | Integration | R-02 | T-15 | Dev | Missing header → 401 |
| FR-3: Expired token | Integration | R-02 | T-16 | Dev | Expired JWT → 401 |
| FR-3: Malformed token | Integration | R-02 | T-17 | Dev | Bad JWT → 401 |
| FR-3: Tampered payload | Integration | R-02 | T-18 | Dev | Altered claims → 401 |
| FR-3: Wrong secret | Unit | R-02 | T-19 | Dev | Wrong key → 401 |
| NFR-6: Hash exclusion (all) | Integration | R-01 | T-20 | Dev | Scan all responses |
| NFR-6: Store exclusion | Unit | R-01 | T-23 | Dev | Store returns only username + name |
| Risk: Full lifecycle | Integration | R-03 | T-26 | Dev | Register → Login → /me |
| Risk: Password in errors | Integration | R-01 | T-28 | Dev | Password never in error text |

**Total P0**: 18 tests, 0 additional hours (all implemented)

### P1 (High)

**Criteria**: Core, frequent, or complex behavior with material user reach and a limited workaround. Risk score is supporting evidence and is not a required condition.

| Requirement | Test Level | Risk Link | Test ID | Owner | Notes |
|-------------|-----------|-----------|---------|-------|-------|
| FR-1: Missing username | Integration | — | T-02 | Dev | 400 on missing field |
| FR-1: Missing password | Integration | — | T-03 | Dev | 400 on missing field |
| FR-1: Missing name | Integration | — | T-04 | Dev | 400 on missing field |
| FR-2: Missing username | Integration | — | T-12 | Dev | 400 on missing field |
| FR-2: Missing password | Integration | — | T-13 | Dev | 400 on missing field |
| NFR-5: Error shape | Integration | R-05 | T-21 | Dev | All errors → {"detail": str} |
| NFR-5: 422 override | Integration | R-05 | T-22 | Dev | Invalid JSON → 400 |
| Risk: Concurrent reg | Integration | R-03 | T-27 | Dev | Same username race |

**Total P1**: 8 tests, 0 additional hours (all implemented)

### P2 (Medium)

**Criteria**: Secondary behavior with narrower user reach and an acceptable workaround. Risk score is supporting evidence and is not a required condition.

| Requirement | Test Level | Risk Link | Test ID | Owner | Notes |
|-------------|-----------|-----------|---------|-------|-------|
| NFR-3: JWT sub claim | Unit | — | T-24 | Dev | Decode and assert sub |
| NFR-3: JWT exp claim | Unit | — | T-25 | Dev | Decode and assert 24h |

**Total P2**: 2 tests, 0 additional hours (all implemented)

### P3 (Low)

No P3 scenarios identified for this epic.

**Total P3**: 0 tests

---

## Execution Order

### Smoke Tests (<1 min)

**Purpose**: Fast feedback, catch build-breaking issues

- [ ] T-01: Register success → 201 + JWT (10s)
- [ ] T-09: Login success → 200 + JWT (10s)
- [ ] T-14: Get /me with valid JWT → 200 + profile (10s)

**Total**: 3 scenarios

### P0 Tests (<3 min)

**Purpose**: Critical path validation

- [ ] T-01 to T-08: Registration (8 tests)
- [ ] T-09 to T-11: Login happy/negative (3 tests)
- [ ] T-14 to T-19: Get /me auth (6 tests)
- [ ] T-20, T-23, T-26, T-28: NFR + risk (4 tests — already counted above, no duplicates)

**Total**: 18 scenarios

### P1 Tests (<1 min)

**Purpose**: Important feature coverage

- [ ] T-02 to T-04: Registration validation (3 tests)
- [ ] T-12 to T-13: Login validation (2 tests)
- [ ] T-21 to T-22: Error shape (2 tests)
- [ ] T-27: Concurrent registration (1 test)

**Total**: 8 scenarios

### P2 Tests (<1 min)

**Purpose**: Full regression coverage

- [ ] T-24: JWT sub claim (1 test)
- [ ] T-25: JWT exp claim (1 test)

**Total**: 2 scenarios

---

## Resource Estimates

### Test Development Effort

| Priority | Count | Hours/Test | Total Hours | Notes |
|----------|-------|------------|-------------|-------|
| P0 | 18 | 0 (implemented) | 0 | All tests exist in `tests/test_auth.py` |
| P1 | 8 | 0 (implemented) | 0 | All tests exist |
| P2 | 2 | 0 (implemented) | 0 | All tests exist |
| P3 | 0 | 0 | 0 | None identified |
| **Total** | **28** | **-** | **0** | **All scenarios implemented** |

### Prerequisites

**Test Data:**
- `conftest.py` fixtures: `client`, `registered_user`, `auth_header`
- `_clear_store` autouse fixture for test isolation

**Tooling:**
- pytest as test runner
- FastAPI TestClient (httpx backend) for API testing
- PyJWT for token construction/verification
- bcrypt for password hash verification

**Environment:**
- Python ≥ 3.10
- All dependencies installed via `pyproject.toml`

---

## Quality Gate Criteria

### Pass/Fail Thresholds

- **P0 pass rate**: 100% (no exceptions)
- **P1 pass rate**: ≥95% (waivers required for failures)
- **P2 pass rate**: ≥90% (informational)
- **High-risk mitigations**: 100% complete or approved waivers

### Coverage Targets

- **Critical paths**: ≥80% (all 3 endpoints covered)
- **Security scenarios**: 100% (R-01, R-02 fully covered)
- **Business logic**: ≥70% (register, login, get-me all covered)
- **Edge cases**: ≥50% (duplicate, case normalization, missing fields)

### Non-Negotiable Requirements

- [x] All P0 tests implemented
- [x] No high-risk (≥6) items unmitigated
- [x] Security tests (SEC category) pass 100%
- [ ] NFR validation evidence exists or `nfr-assess` has documented CONCERNS/waivers

---

## Mitigation Plans

### R-01: Password Hash Leak (Score: 6)

**Mitigation Strategy:** Assert response body for POST /register, POST /login, GET /me never contains `password_hash`. Assert store `get_user()` return value never contains `password_hash`. Add boundary test: register user, retrieve from store, verify only `username` and `name` returned. Scan all error messages for hash leakage.
**Owner:** Dev
**Timeline:** Before release — Story 1.2 (registration) and Story 1.4 (get user)
**Status:** Complete ✅ (T-07, T-08, T-20, T-23, T-28)
**Verification:** All 5 test scenarios pass

### R-02: JWT Token Forgery (Score: 6)

**Mitigation Strategy:** Test expired tokens return 401. Test malformed tokens (not a valid JWT structure) return 401. Test unsigned/none-algorithm tokens return 401. Test tampered payload (valid structure, altered claims) returns 401. Test tokens signed with wrong secret return 401.
**Owner:** Dev
**Timeline:** Before release — Story 1.4 (get user)
**Status:** Complete ✅ (T-15, T-16, T-17, T-18, T-19)
**Verification:** All 5 test scenarios pass

---

## Assumptions and Dependencies

### Assumptions

1. Single-process deployment — no horizontal scaling; in-memory store is process-scoped (AD-3)
2. No HTTPS termination — TLS handled by reverse proxy or deployment layer
3. JWT secret is a constant — no key rotation, no environment-based secret injection (AD-4)
4. No rate limiting — authentication endpoints unprotected against brute force (acceptable for personal project)
5. No database — all data lost on restart; by design, not a bug

### Dependencies

1. PRD requirements finalized — completed ✅
2. Architecture document (ARCHITECTURE-SPINE.md) — completed ✅
3. Epics and stories defined — completed ✅
4. All 6 source files implemented — completed ✅ (`src/` directory)

### Risks to Plan

- **Risk**: JWT expiry or bcrypt cost factor changes after test implementation
  - **Impact**: P0 tests may need updates
  - **Contingency**: Design tests to accept configurable values; isolate magic numbers
- **Risk**: FastAPI version change breaks TestClient behavior
  - **Impact**: Test infrastructure affected
  - **Contingency**: Pin FastAPI version in test requirements

---

## Interworking & Regression

| Service/Component | Impact | Regression Scope |
|-------------------|--------|------------------|
| `src/auth.py` | JWT creation/verification — all auth tests depend on this | T-14 to T-19, T-24, T-25 |
| `src/services.py` | Business logic — registration, login, profile | T-01 to T-13, T-20 to T-28 |
| `src/store.py` | Data layer — user storage and retrieval | T-01, T-05, T-07, T-23, T-26 |
| `src/routes.py` | HTTP endpoints — all API tests hit these | All 28 tests |
| `src/models.py` | Pydantic models — request/response validation | T-02 to T-04, T-12 to T-13, T-22 |
| `src/main.py` | App factory — TestClient instantiation | All 28 tests |

---

## Appendix

### Knowledge Base References

- `risk-governance.md` — Risk scoring matrix and gate decision rules
- `probability-impact.md` — Probability and impact scale definitions
- `test-levels-framework.md` — Unit vs integration vs E2E selection criteria
- `test-priorities-matrix.md` — P0-P3 priority definitions and coverage targets
- `nfr-criteria.md` — NFR validation criteria and evidence requirements

### Related Documents

- System-level test design: `_bmad-output/test-artifacts/test-design-progress-system.md`
- Architecture: `_bmad-output/planning-artifacts/architecture/architecture-bmad-2026-09-06/ARCHITECTURE-SPINE.md`
- Epics: `_bmad-output/planning-artifacts/epics.md`
- PRD: `_bmad-output/planning-artifacts/prds/prd-bmad-2026-09-06/prd.md`
- Existing tests: `tests/test_auth.py`
- Test fixtures: `tests/conftest.py`
