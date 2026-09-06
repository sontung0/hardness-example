---
workflowStatus: 'completed'
totalSteps: 5
stepsCompleted: ['step-01-detect-mode', 'step-02-load-context', 'step-03-risk-and-testability', 'step-04-coverage-plan', 'step-05-generate-output']
lastStep: 'step-05-generate-output'
nextStep: ''
lastSaved: '2026-09-06'
workflowType: 'testarch-test-design'
inputDocuments:
  - prds/prd-bmad-2026-09-06/prd.md
  - architecture/architecture-bmad-2026-09-06/ARCHITECTURE-SPINE.md
  - planning-artifacts/epics.md
---

# Test Design for QA: Simple REST API — Auth

**Purpose:** Test execution recipe for QA team. Defines what to test, how to test it, and what QA needs from other teams.

**Date:** 2026-09-06
**Author:** NST (Master Test Architect)
**Status:** Draft
**Project:** bmad

**Related:** See Architecture doc (`test-design-architecture.md`) for testability concerns and architectural blockers.

---

## Executive Summary

**Scope:** 3 endpoints (POST /register, POST /login, GET /me) with JWT auth and in-memory storage.

**Risk Summary:**

- Total Risks: 8 (2 high-priority score ≥6, 4 medium, 2 low)
- Critical Categories: SEC (2 high risks)

**Coverage Summary:**

- P0 tests: ~18 (critical paths, security)
- P1 tests: ~8 (important features, integration)
- P2 tests: ~2 (edge cases, regression)
- P3 tests: 0
- **Total**: ~28 tests (~1–2 weeks with 1 QA)

---

## Not in Scope

| Item | Reasoning | Mitigation |
|------|-----------|------------|
| **E2E browser tests** | Backend-only API; no frontend | Not applicable |
| **Performance/load testing** | No SLO defined; personal project | Deferred to future enhancement |
| **Database tests** | In-memory store only; no DB | By design (AD-3) |
| **Mobile tests** | No mobile indicators in project | Not applicable |

---

## Dependencies & Test Blockers

### Backend/Architecture Dependencies (Pre-Implementation)

1. **Project scaffolding (Story 1.1)** — Dev
   - `src/` directory with all 6 files: `main.py`, `routes.py`, `services.py`, `store.py`, `models.py`, `auth.py`
   - Blocks all integration tests
2. **FastAPI TestClient availability** — Dev
   - FastAPI's built-in `TestClient` must be importable and configured
   - Blocks all API-level tests

### QA Infrastructure Setup (Pre-Implementation)

1. **pytest + httpx** — QA
   - Install `pytest` and `httpx` (httpx is FastAPI TestClient backend)
   - Configure test runner
2. **Test fixtures** — QA
   - Fresh `TestClient` fixture per test (in-memory store isolation)
   - User factory: `create_user(username, password, name)` helper

**Example fixture pattern:**

```python
import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def registered_user(client):
    response = client.post("/register", json={
        "username": "testuser",
        "password": "testpass123",
        "name": "Test User"
    })
    return response.json()
```

---

## Risk Assessment

### High-Priority Risks (Score ≥6)

| Risk ID | Category | Description | Score | QA Test Coverage |
|---------|----------|-------------|-------|------------------|
| **R-01** | **SEC** | `password_hash` exposed in response or store | **6** | T-08, T-20, T-23, T-28 |
| **R-02** | **SEC** | Malformed/unsigned JWT accepted | **6** | T-15, T-16, T-17, T-18, T-19 |

### Medium/Low-Priority Risks

| Risk ID | Category | Description | Score | QA Test Coverage |
|---------|----------|-------------|-------|------------------|
| R-03 | BUS | Duplicate registration returns wrong status | 4 | T-05, T-26, T-27 |
| R-04 | BUS | Username not lowercased consistently | 4 | T-06 |
| R-05 | TECH | FastAPI 422 override may not cover all paths | 4 | T-22 |
| R-06 | SEC | bcrypt work factor too low/high | 2 | T-07 |
| R-07 | OPS | Data loss on restart (by design) | 1 | T-26 (implicit) |
| R-08 | PERF | JWT signing latency | 2 | Not in scope (no SLO) |

---

## NFR Test Coverage Plan

| NFR Category | Requirement / Threshold | Planned Validation | Tool / Level | Evidence Artifact | Priority |
|--------------|------------------------|-------------------|--------------|-------------------|----------|
| Security | Passwords hashed with bcrypt (default) | Verify hash stored in store, not plaintext | Unit: services.py | Test output | P0 |
| Security | JWT `sub` = lowercased username, `exp` = 24h | Decode JWT and assert claims | Unit: auth.py | Test output | P1 |
| Security | No session cookies; JWT sole auth | 401 without token, 200 with valid token | Integration: GET /me | Test output | P0 |
| Security | `password_hash` never in response | Scan all response bodies for `password_hash` | Integration: all endpoints | Test output | P0 |
| Technical | `{"detail": str}` for all errors | Assert error response shape across all error cases | Integration: all endpoints | Test output | P1 |
| Data | One Python dict keyed by username | Verify store state after operations | Unit: store.py | Test output | P1 |

**Missing thresholds:**
- JWT expiration: 24h (confirm or accept default)
- bcrypt cost factor: default (confirm or accept default)
- Response time SLO: UNKNOWN
- Concurrent user limit: UNKNOWN
- Memory usage ceiling: UNKNOWN

---

## Test Coverage Matrix

### Functional Requirement Scenarios

| ID | Scenario | Req | Level | Priority | Risk Link |
|----|----------|-----|-------|----------|-----------|
| T-01 | Register: valid input → 201 + JWT | FR-1 | Integration | **P0** | R-03 |
| T-02 | Register: missing username → 400 | FR-1 | Integration | **P0** | — |
| T-03 | Register: missing password → 400 | FR-1 | Integration | **P0** | — |
| T-04 | Register: missing name → 400 | FR-1 | Integration | **P1** | — |
| T-05 | Register: duplicate username → 409 | FR-1 | Integration | **P0** | R-03 |
| T-06 | Register: username case normalization | FR-1 | Integration | **P1** | R-04 |
| T-07 | Register: password hashed with bcrypt | FR-1 | Unit | **P0** | R-01 |
| T-08 | Register: password_hash not in response | FR-1 | Integration | **P0** | R-01 |
| T-09 | Login: valid credentials → 200 + JWT | FR-2 | Integration | **P0** | — |
| T-10 | Login: wrong password → 401 | FR-2 | Integration | **P0** | R-02 |
| T-11 | Login: nonexistent user → 401 | FR-2 | Integration | **P0** | R-02 |
| T-12 | Login: missing username → 400 | FR-2 | Integration | **P1** | — |
| T-13 | Login: missing password → 400 | FR-2 | Integration | **P1** | — |
| T-14 | Get /me: valid JWT → 200 + profile | FR-3 | Integration | **P0** | — |
| T-15 | Get /me: no token → 401 | FR-3 | Integration | **P0** | R-02 |
| T-16 | Get /me: expired token → 401 | FR-3 | Integration | **P0** | R-02 |
| T-17 | Get /me: malformed token → 401 | FR-3 | Integration | **P0** | R-02 |
| T-18 | Get /me: tampered payload → 401 | FR-3 | Integration | **P0** | R-02 |
| T-19 | Get /me: wrong secret → 401 | FR-3 | Unit | **P0** | R-02 |

### NFR Scenarios

| ID | Scenario | NFR | Level | Priority | Risk Link |
|----|----------|-----|-------|----------|-----------|
| T-20 | Password hash never in any response | NFR-6 | Integration | **P0** | R-01 |
| T-21 | Error shape is always `{"detail": str}` | NFR-5 | Integration | **P1** | R-05 |
| T-22 | 422 overridden to `{"detail": str}` | NFR-5 | Integration | **P1** | R-05 |
| T-23 | Store returns only username + name | NFR-6 | Unit | **P1** | R-01 |
| T-24 | JWT `sub` claim = lowercased username | NFR-3 | Unit | **P1** | — |
| T-25 | JWT `exp` = 24h from issuance | NFR-3 | Unit | **P2** | — |

### Risk-Driven Scenarios

| ID | Scenario | Risk | Level | Priority | Notes |
|----|----------|------|-------|----------|-------|
| T-26 | Register → Login → Get /me full flow | R-03 | Integration | **P0** | End-to-end auth lifecycle |
| T-27 | Concurrent registrations same username | R-03 | Integration | **P1** | Race condition test |
| T-28 | Password never logged or in error messages | R-01 | Integration | **P0** | Security boundary |

---

## Execution Strategy

| Tier | Scope | Trigger | Estimated Duration |
|------|-------|---------|-------------------|
| **PR Gate** | All P0 + P1 scenarios (T-01 through T-25) | Every PR | ~2–4 minutes |
| **Nightly** | Full suite (all 28 scenarios) + performance baseline | Nightly cron | ~5–8 minutes |
| **Weekly** | Stress test: concurrent registrations, memory ceiling | Weekly cron | ~10–15 minutes |

**Framework:** pytest + httpx (FastAPI TestClient backend)

---

## Resource Estimates

| Priority | Scenarios | Estimated Effort |
|----------|-----------|-----------------|
| P0 | 18 | ~8–14 hours |
| P1 | 8 | ~5–10 hours |
| P2 | 2 | ~1–3 hours |
| **Total** | **28** | **~14–27 hours** |

**Timeline:** ~1–2 sprints (assuming 1 developer dedicated to test implementation)

---

## Entry Criteria

- [ ] PRD requirements agreed upon by QA, Dev, PM
- [ ] Architecture document reviewed and approved
- [ ] pytest + httpx installed and configured
- [ ] Test fixtures created (fresh TestClient per test)
- [ ] Story 1.1 scaffolding complete (all 6 source files in `src/`)
- [ ] UNKNOWN thresholds confirmed or defaults accepted (JWT expiry, bcrypt cost)

---

## Quality Gates

| Gate | Threshold |
|------|-----------|
| P0 pass rate | **100%** — All P0 tests must pass before any release |
| P1 pass rate | **≥ 95%** — At most 1 P1 failure allowed with documented waiver |
| High-risk mitigations | **Complete** — R-01 and R-02 mitigations implemented before release |
| Code coverage | **≥ 80%** — Branch coverage on `services.py`, `auth.py`, `store.py` |
| NFR validation | **Evidence identified** — All 6 NFRs have planned validation scenarios |
| Full NFR status | **Deferred** — PASS/CONCERNS/FAIL in `nfr-assess` after implementation |
