---
runScope: system
runKey: system
workflowStatus: completed
totalSteps: 5
stepsCompleted: ['step-01-detect-mode', 'step-02-load-context', 'step-03-risk-and-testability', 'step-04-coverage-plan', 'step-05-generate-output']
lastStep: 'step-05-generate-output'
nextStep: ''
lastSaved: 2026-09-06
---

# Test Design Progress — System Level

## Inputs

- PRD: `_bmad-output/planning-artifacts/prds/prd-bmad-2026-09-06/prd.md`
- Architecture: `_bmad-output/planning-artifacts/architecture/architecture-bmad-2026-09-06/ARCHITECTURE-SPINE.md`
- Architecture Reviews:
  - `adversarial-divergence.md`
  - `research-verification.md`
  - `rubric-walker.md`
- Epics: `_bmad-output/planning-artifacts/epics.md`

---

## Step 3: Testability & Risk Assessment

### 1. Testability Review

#### Controllability

| Aspect | Assessment | Evidence |
|--------|------------|----------|
| State seeding | **Strong** — In-memory Python dict trivially resettable | AD-3: module-level dict, no persistence |
| Mockability | **Strong** — No external services; JWT secret is a constant in `auth.py` | AD-4, AD-7: hardcoded secret, no DI needed |
| Fault injection | **Moderate** — FastAPI TestClient supports HTTP-level errors; no granular fault injection framework | No health check or circuit breaker pattern |
| Test isolation | **Strong** — Fresh server process = clean state; no shared mutable state across processes | AD-3: data lost on restart by design |

#### Observability

| Aspect | Assessment | Evidence |
|--------|------------|----------|
| Deterministic assertions | **Strong** — Consistent error shape `{"detail": str}`, well-defined status codes per endpoint | AD-5 |
| JWT inspection | **Strong** — Structured claims (`sub`, `exp`) verifiable with PyJWT | AD-4 |
| Logging | **Gap** — No structured logging or request tracing specified | No observability architecture defined |
| Health check | **Gap** — No `/health` or readiness endpoint for test setup verification | Not in PRD or architecture |

#### Reliability

| Aspect | Assessment | Evidence |
|--------|------------|----------|
| Parallel test safety | **Strong** — Stateless auth + isolated in-memory store per process | AD-1, AD-3 |
| Reproducibility | **Strong** — Deterministic inputs → deterministic outputs; no time-dependent logic except JWT `exp` | AD-4 |
| Concurrency | **N/A** — Single-process, single-dict; no concurrent access concerns | AD-8 |

#### 🚨 Testability Concerns

1. **No structured logging** — Failures in CI will lack context for debugging. Consider adding request ID or structured log output. *Severity: Medium*
2. **No health check endpoint** — Tests cannot verify server readiness before sending requests. FastAPI `TestClient` mitigates this for unit/integration tests, but E2E tests need a readiness probe. *Severity: Low*
3. **JWT expiration testing** — 24h token lifetime makes expiration testing require clock mocking or token manipulation. *Severity: Low (manageable)*

#### ✅ Testability Assessment Summary

The architecture is **highly testable**. The in-memory store, stateless auth, and consistent error shape create an ideal testing environment. The main gaps are observability-related (logging, health checks) and do not block test execution. FastAPI's built-in `TestClient` provides excellent controllability for all three endpoints.

#### ASRs (Architecturally Significant Requirements)

| ASR | Status | Rationale |
|-----|--------|-----------|
| AD-1: Stateless Auth | **FYI** | Standard JWT pattern, low risk |
| AD-2: Password Hashing (bcrypt) | **ACTIONABLE** | Timing-sensitive; hash verification needed |
| AD-3: Single In-Memory Store | **FYI** | Trivially testable |
| AD-4: JWT as Sole Auth | **ACTIONABLE** | Token validation, expiration, malformed tokens need coverage |
| AD-5: Consistent Error Shape | **ACTIONABLE** | Error handler override of FastAPI 422 needs verification |
| AD-6: Password Hash Exclusion | **ACTIONABLE** | Boundary leak detection across layers |
| AD-7: Auth Dependency Contract | **ACTIONABLE** | FastAPI `Depends` integration needs contract testing |
| AD-8: Store Lifecycle | **FYI** | Module-level dict, straightforward |

---

### 2. Risk Assessment

| ID | Category | Title | Description | P | I | Score | Action | Mitigation | Owner |
|----|----------|-------|-------------|---|---|-------|--------|------------|-------|
| R-01 | SEC | Password hash leak | `password_hash` exposed in response or store return value | 2 | 3 | **6** | MITIGATE | Dedicated exclusion tests per endpoint + store function; assert response body never contains `password_hash` | TA |
| R-02 | SEC | JWT token forgery | Malformed or unsigned tokens accepted by auth middleware | 2 | 3 | **6** | MITIGATE | Negative tests with expired, malformed, unsigned, and tampered tokens; verify 401 for each | TA |
| R-03 | BUS | Duplicate registration | Second registration with same username returns 409, not 200 or 500 | 2 | 2 | 4 | MONITOR | Duplicate username test case; verify in-memory store does not overwrite | Dev |
| R-04 | BUS | Case-sensitive username | Username not lowercased consistently, leading to duplicate accounts | 2 | 2 | 4 | MONITOR | Test with mixed-case usernames; verify all lookups use lowercased form | Dev |
| R-05 | TECH | FastAPI 422 override | Custom error handler for 422 → `{"detail": str}` may not cover all validation paths | 2 | 2 | 4 | MONITOR | Test with invalid JSON body, missing fields, wrong types; verify consistent error shape | Dev |
| R-06 | SEC | bcrypt work factor | bcrypt default work factor may be too low or too high for production | 1 | 2 | 2 | DOCUMENT | Verify bcrypt cost factor in config; note as NFR evidence | TA |
| R-07 | OPS | Data loss on restart | In-memory store loses all data on process restart | 1 | 1 | 1 | DOCUMENT | By design (AD-3); document in test setup notes | Dev |
| R-08 | PERF | JWT signing latency | bcrypt + JWT signing in request path may slow response times | 1 | 2 | 2 | DOCUMENT | No performance SLO defined; note as UNKNOWN threshold | TA |

**High-risk items (score ≥ 6):** R-01, R-02 — require documented mitigation before implementation.

---

### 3. NFR Planning Assessment

| NFR | Category | Threshold | Evidence Source | Status |
|-----|----------|-----------|-----------------|--------|
| NFR-1: In-memory storage | DATA | One Python dict keyed by username | Unit test: store.py | **DEFINED** |
| NFR-2: Password hashing (bcrypt) | SEC | Default work factor; hash as Python str (decode utf-8) | Integration test: services.py | **DEFINED** |
| NFR-3: JWT signing/validation | SEC | `sub` = lowercased username, `exp` = 24h | Integration test: auth.py | **DEFINED** |
| NFR-4: Stateless auth | SEC | No session cookies; JWT sole mechanism | Integration test: GET /me without token | **DEFINED** |
| NFR-5: Consistent error shape | TECH | `{"detail": str}` for all errors; status codes per REST convention | Unit test: error handler | **DEFINED** |
| NFR-6: Password hash exclusion | SEC | `password_hash` never in response or store return | Integration test: response body assertion | **DEFINED** |

**Missing Thresholds (UNKNOWN):**

| Item | Category | Question | Risk Category |
|------|----------|----------|---------------|
| JWT expiration time | SEC | Is 24h the correct production value? | SEC |
| bcrypt cost factor | SEC | What is the acceptable bcrypt work factor? | SEC |
| Response time SLO | PERF | What is the maximum acceptable response time? | PERF |
| Concurrent user limit | PERF | What is the expected concurrent user load? | PERF |
| Memory usage ceiling | PERF | What is the maximum in-memory store size before degradation? | PERF |

---

### 4. Risk Findings Summary

**Highest Risks:**
- **R-01 (Password Hash Leak, Score 6):** Critical security boundary. Mitigation: dedicated exclusion tests across all layers.
- **R-02 (JWT Token Forgery, Score 6):** Auth mechanism integrity. Mitigation: comprehensive negative token tests.

**Mitigation Priorities:**
1. Implement R-01 and R-02 mitigation tests as part of Story 1.2 and 1.4
2. Monitor R-03 and R-04 during Story 1.1 scaffolding
3. Document R-08 performance thresholds (UNKNOWN) for future NFR validation

---

## Step 4: Coverage Plan & Execution Strategy

### 1. Coverage Matrix

**Test Level Decision:** Backend-only project with in-memory storage, no external services → **Integration tests via FastAPI TestClient** are the primary level. Unit tests for isolated pure functions. No E2E tests needed (single process, no browser, no external systems).

#### Functional Requirement Scenarios

| ID | Scenario | Req | Level | Priority | Risk Link | Notes |
|----|----------|-----|-------|----------|-----------|-------|
| T-01 | Register: valid input returns 201 + JWT | FR-1 | Integration | **P0** | R-03 | Happy path |
| T-02 | Register: missing username → 400 | FR-1 | Integration | **P0** | — | Input validation |
| T-03 | Register: missing password → 400 | FR-1 | Integration | **P0** | — | Input validation |
| T-04 | Register: missing name → 400 | FR-1 | Integration | **P1** | — | Input validation |
| T-05 | Register: duplicate username → 409 | FR-1 | Integration | **P0** | R-03 | Conflict handling |
| T-06 | Register: username case normalization | FR-1 | Integration | **P1** | R-04 | "Bob" and "bob" → same user |
| T-07 | Register: password hashed with bcrypt | FR-1 | Unit | **P0** | R-01 | Verify hash in store |
| T-08 | Register: password_hash not in response | FR-1 | Integration | **P0** | R-01 | Exclusion boundary |
| T-09 | Login: valid credentials → 200 + JWT | FR-2 | Integration | **P0** | — | Happy path |
| T-10 | Login: wrong password → 401 | FR-2 | Integration | **P0** | R-02 | Negative auth |
| T-11 | Login: nonexistent user → 401 | FR-2 | Integration | **P0** | R-02 | Negative auth |
| T-12 | Login: missing username → 400 | FR-2 | Integration | **P1** | — | Input validation |
| T-13 | Login: missing password → 400 | FR-2 | Integration | **P1** | — | Input validation |
| T-14 | Get /me: valid JWT → 200 + profile | FR-3 | Integration | **P0** | — | Happy path |
| T-15 | Get /me: no token → 401 | FR-3 | Integration | **P0** | R-02 | Missing auth |
| T-16 | Get /me: expired token → 401 | FR-3 | Integration | **P0** | R-02 | Token expiry |
| T-17 | Get /me: malformed token → 401 | FR-3 | Integration | **P0** | R-02 | Token forgery |
| T-18 | Get /me: tampered payload → 401 | FR-3 | Integration | **P0** | R-02 | Token tampering |
| T-19 | Get /me: wrong secret → 401 | FR-3 | Unit | **P0** | R-02 | JWT verification |

#### Non-Functional Requirement Scenarios

| ID | Scenario | NFR | Level | Priority | Risk Link | Evidence |
|----|----------|-----|-------|----------|-----------|----------|
| T-20 | Password hash never in any response | NFR-6 | Integration | **P0** | R-01 | Response body scan |
| T-21 | Error shape is always `{"detail": str}` | NFR-5 | Integration | **P1** | R-05 | All error responses |
| T-22 | 422 overridden to `{"detail": str}` | NFR-5 | Integration | **P1** | R-05 | Invalid JSON body |
| T-23 | Store returns only username + name | NFR-6 | Unit | **P1** | R-01 | Store function output |
| T-24 | JWT `sub` claim = lowercased username | NFR-3 | Unit | **P1** | — | JWT decode assertion |
| T-25 | JWT `exp` = 24h from issuance | NFR-3 | Unit | **P2** | — | Token decode assertion |

#### Risk-Driven Scenarios

| ID | Scenario | Risk | Level | Priority | Notes |
|----|----------|------|-------|----------|-------|
| T-26 | Register → Login → Get /me full flow | R-03 | Integration | **P0** | End-to-end auth lifecycle |
| T-27 | Concurrent registrations same username | R-03 | Integration | **P1** | Race condition test |
| T-28 | Password never logged or in error messages | R-01 | Integration | **P0** | Security boundary |

**Total scenarios:** 28
- **P0:** 18 scenarios
- **P1:** 8 scenarios
- **P2:** 2 scenarios

---

### 2. NFR Coverage and Evidence Plan

| NFR | Category | Validation Scenarios | Evidence Artifact | Status |
|-----|----------|---------------------|-------------------|--------|
| NFR-1: In-memory storage | DATA | T-01, T-05, T-26 | Unit/integration test output | ✅ Planned |
| NFR-2: Password hashing (bcrypt) | SEC | T-07, T-20 | Test output + bcrypt cost assertion | ✅ Planned |
| NFR-3: JWT signing/validation | SEC | T-14, T-16, T-17, T-18, T-19, T-24, T-25 | JWT decode test output | ✅ Planned |
| NFR-4: Stateless auth | SEC | T-15, T-16, T-17, T-18 | 401 response assertions | ✅ Planned |
| NFR-5: Consistent error shape | TECH | T-21, T-22 | Error response body assertions | ✅ Planned |
| NFR-6: Password hash exclusion | SEC | T-08, T-20, T-23, T-28 | Response body scan + store output assertion | ✅ Planned |

**UNKNOWN thresholds (blockers for final NFR assessment):**
- JWT expiration time: 24h (verify against security requirements)
- bcrypt cost factor: default (verify acceptable)
- Response time SLO: not defined
- Concurrent user limit: not defined
- Memory usage ceiling: not defined

---

### 3. Execution Strategy

| Tier | Scope | Trigger | Estimated Duration |
|------|-------|---------|-------------------|
| **PR Gate** | All P0 + P1 scenarios (T-01 through T-25) | Every PR | ~2–4 minutes |
| **Nightly** | Full suite (all 28 scenarios) + performance baseline | Nightly cron | ~5–8 minutes |
| **Weekly** | Stress test: concurrent registrations, memory ceiling | Weekly cron | ~10–15 minutes |

**Framework:** FastAPI `TestClient` (via `pytest` + `httpx` backend)

---

### 4. Resource Estimates

| Priority | Scenarios | Estimated Effort |
|----------|-----------|-----------------|
| P0 | 18 | ~8–14 hours |
| P1 | 8 | ~5–10 hours |
| P2 | 2 | ~1–3 hours |
| **Total** | **28** | **~14–27 hours** |

**Timeline:** ~1–2 sprints (assuming 1 developer dedicated to test implementation)

---

### 5. Quality Gates

| Gate | Threshold | Status |
|------|-----------|--------|
| P0 pass rate | **100%** | All P0 tests must pass before any release |
| P1 pass rate | **≥ 95%** | At most 1 P1 failure allowed with documented waiver |
| High-risk mitigations | **Complete** | R-01 and R-02 mitigations (T-07, T-08, T-16, T-17, T-18, T-19, T-20, T-28) must be implemented before release |
| Code coverage | **≥ 80%** | Branch coverage on `services.py`, `auth.py`, `store.py` |
| NFR validation | **Evidence identified** | All 6 NFRs have planned validation scenarios and evidence artifacts |
| Full NFR status | **Deferred** | PASS/CONCERNS/FAIL to be determined in `nfr-assess` after implementation evidence exists |
