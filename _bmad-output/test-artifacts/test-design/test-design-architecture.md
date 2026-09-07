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

# Test Design for Architecture: Simple REST API — Auth

**Purpose:** Architectural concerns, testability gaps, and NFR requirements for review by Architecture/Dev teams. Serves as a contract between QA and Engineering on what must be addressed before test development begins.

**Date:** 2026-09-06
**Author:** NST (Master Test Architect)
**Status:** Architecture Review Pending
**Project:** bmad
**PRD Reference:** `prd-bmad-2026-09-06/prd.md`
**ADR Reference:** `architecture-bmad-2026-09-06/ARCHITECTURE-SPINE.md`

---

## Executive Summary

**Scope:** User authentication API — register, login, and get current user endpoints with JWT auth and in-memory storage.

**Business Context** (from PRD):

- **Revenue/Impact:** Hobby/personal project building block for auth without database dependencies
- **Problem:** Developers need a dead-simple REST API that handles the full auth lifecycle with zero external dependencies
- **GA Launch:** Not specified (personal project)

**Architecture** (from ARCHITECTURE-SPINE):

- **Key Decision 1:** Layered architecture — Routes → Services → Store, each layer calls only the one below
- **Key Decision 2:** Stateless auth via JWT (AD-1), passwords never in plaintext (AD-2), single in-memory store (AD-3)
- **Key Decision 3:** Stack: Python ≥ 3.10, FastAPI 0.141.1, Uvicorn, bcrypt, PyJWT, Pydantic

**Expected Scale:**

- Single-process, in-memory storage; no scale requirements defined

**Risk Summary:**

- **Total risks**: 8
- **High-priority (≥6)**: 2 risks requiring immediate mitigation
- **Test effort**: ~28 scenarios (~1–2 weeks for 1 QA)

---

## Quick Guide

### 🚨 BLOCKERS - Team Must Decide (Can't Proceed Without)

**Pre-Implementation Critical Path** — These MUST be completed before QA can write integration tests:

1. **UNKNOWN: JWT expiration time** — Is 24h the correct production value? (recommended owner: Dev)
2. **UNKNOWN: bcrypt cost factor** — What is the acceptable work factor? (recommended owner: Dev)

**What we need from team:** Clarify these 2 items or accept defaults as-is.

---

### ⚠️ HIGH PRIORITY - Team Should Validate (We Provide Recommendation, You Approve)

1. **R-01: Password hash leak (Score 6)** — Recommend dedicated exclusion tests across all layers; owner: Dev during implementation of Story 1.2
2. **R-02: JWT token forgery (Score 6)** — Recommend comprehensive negative token tests; owner: Dev during implementation of Story 1.4

**What we need from team:** Review recommendations and approve (or suggest changes).

---

### 📋 INFO ONLY - Solutions Provided (Review, No Decisions Needed)

1. **Test strategy**: Integration tests via FastAPI TestClient as primary level; Unit tests for pure functions (in-memory store, no external deps)
2. **Tooling**: pytest + httpx (FastAPI TestClient backend)
3. **Tiered CI/CD**: PR gate (~2–4 min), Nightly (~5–8 min), Weekly stress (~10–15 min)
4. **Coverage**: ~28 test scenarios prioritized P0–P3 with risk-based classification
5. **Quality gates**: P0 pass = 100%, P1 pass ≥ 95%, coverage ≥ 80%

**What we need from team:** Just review and acknowledge (we already have the solution).

---

## For Architects and Devs - Open Topics 👷

### Risk Assessment

**Total risks identified**: 8 (2 high-priority score ≥6, 4 medium, 2 low)

#### High-Priority Risks (Score ≥6) - IMMEDIATE ATTENTION

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation | Owner | Timeline |
|---------|----------|-------------|-------------|--------|-------|------------|-------|----------|
| **R-01** | **SEC** | `password_hash` exposed in response or store return value | 2 | 3 | **6** | Dedicated exclusion tests per endpoint + store function; assert response body never contains `password_hash` | TA | Before release |
| **R-02** | **SEC** | Malformed or unsigned JWT tokens accepted by auth middleware | 2 | 3 | **6** | Negative tests with expired, malformed, unsigned, and tampered tokens; verify 401 for each | TA | Before release |

#### Medium-Priority Risks (Score 3-5)

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation | Owner |
|---------|----------|-------------|-------------|--------|-------|------------|-------|
| R-03 | BUS | Duplicate registration returns wrong status | 2 | 2 | 4 | Duplicate username test case; verify in-memory store does not overwrite | Dev |
| R-04 | BUS | Username not lowercased consistently | 2 | 2 | 4 | Test with mixed-case usernames; verify all lookups use lowercased form | Dev |
| R-05 | TECH | FastAPI 422 override may not cover all validation paths | 2 | 2 | 4 | Test with invalid JSON body, missing fields, wrong types; verify consistent error shape | Dev |
| R-08 | PERF | JWT signing latency in request path | 1 | 2 | 2 | No performance SLO defined; note as UNKNOWN threshold | TA |

#### Low-Priority Risks (Score 1-2)

| Risk ID | Category | Description | Probability | Impact | Score | Action |
|---------|----------|-------------|-------------|--------|-------|--------|
| R-06 | SEC | bcrypt work factor may be too low/high | 1 | 2 | 2 | Monitor |
| R-07 | OPS | Data loss on restart (by design) | 1 | 1 | 1 | Document |

#### Risk Category Legend

- **TECH**: Technical/Architecture (flaws, integration, scalability)
- **SEC**: Security (access controls, auth, data exposure)
- **PERF**: Performance (SLA violations, degradation, resource limits)
- **DATA**: Data Integrity (loss, corruption, inconsistency)
- **BUS**: Business Impact (UX harm, logic errors, revenue)
- **OPS**: Operations (deployment, config, monitoring)

### Risk Mitigation Plans (High-Priority Risks)

#### R-01: Password Hash Leak (Score 6)

| Field | Detail |
|-------|--------|
| **Strategy** | 1. Assert response body for POST /register, POST /login, GET /me never contains `password_hash`\n2. Assert store `get_user()` return value never contains `password_hash`\n3. Add boundary test: register user, retrieve from store, verify only `username` and `name` returned\n4. Scan all error messages for hash leakage |
| **Owner** | Dev (implementation) + TA (test validation) |
| **Timeline** | Before release — Story 1.2 (registration) and Story 1.4 (get user) |
| **Status** | Planned |
| **Verification** | All T-08, T-20, T-23, T-28 scenarios pass |

#### R-02: JWT Token Forgery (Score 6)

| Field | Detail |
|-------|--------|
| **Strategy** | 1. Test expired tokens return 401\n2. Test malformed tokens (not a valid JWT structure) return 401\n3. Test unsigned/none-algorithm tokens return 401\n4. Test tampered payload (valid structure, altered claims) returns 401\n5. Test tokens signed with wrong secret return 401 |
| **Owner** | Dev (implementation) + TA (test validation) |
| **Timeline** | Before release — Story 1.4 (get user) |
| **Status** | Planned |
| **Verification** | All T-15, T-16, T-17, T-18, T-19 scenarios pass |

---

### Assumptions and Dependencies

#### Architectural Assumptions

1. **Single-process deployment** — No horizontal scaling; in-memory store is process-scoped (AD-3)
2. **No HTTPS termination** — TLS handled by reverse proxy or deployment layer; API server receives plain HTTP
3. **JWT secret is a constant** — No key rotation, no environment-based secret injection (AD-4)
4. **No rate limiting** — Authentication endpoints are unprotected against brute force (acceptable for personal project)
5. **No database** — All data lost on restart; this is by design, not a bug

#### Dependencies

| Dependency | Required By | Status |
|-----------|-------------|--------|
| PRD requirements finalized | Test design start | ✅ Complete |
| Architecture document (ARCHITECTURE-SPINE.md) | Test design start | ✅ Complete |
| Epics and stories defined | Epic-level test design | ✅ Complete |
| UNKNOWN: JWT expiration time confirmed | Before P0 test implementation | ⏳ Pending |
| UNKNOWN: bcrypt cost factor confirmed | Before P0 test implementation | ⏳ Pending |

#### Risks to Plan

| Risk | Impact | Contingency |
|------|--------|-------------|
| JWT expiry or bcrypt cost factor changes after test implementation | P0 tests may need updates | Design tests to accept configurable values; isolate magic numbers |
| FastAPI version change breaks TestClient behavior | Test infrastructure affected | Pin FastAPI version in test requirements |

---

### NFR Testability Requirements

| NFR Category | Threshold / Requirement | Current Design Support | Gap / Decision Needed | Planned Evidence |
|--------------|------------------------|----------------------|----------------------|-----------------|
| Security | Passwords hashed with bcrypt (default work factor) | ✅ Supported (AD-2) | Verify cost factor is acceptable | Integration test: services.py |
| Security | JWT `sub` = lowercased username, `exp` = 24h | ✅ Supported (AD-4) | Confirm 24h expiry is correct | Unit test: auth.py |
| Security | No session cookies; JWT sole auth mechanism | ✅ Supported (AD-1, AD-4) | None | Integration test: GET /me without token |
| Security | `password_hash` never in response or store return | ✅ Supported (AD-6) | None | Integration test: response body assertion |
| Technical | Consistent error shape `{"detail": str}` | ✅ Supported (AD-5) | Verify 422 override covers all paths | Integration test: error handler |
| Data | In-memory Python dict keyed by username | ✅ Supported (AD-3) | None | Unit test: store.py |

**Unknown thresholds:**

- JWT expiration time: 24h (verify against security requirements)
- bcrypt cost factor: default (verify acceptable)
- Response time SLO: not defined
- Concurrent user limit: not defined
- Memory usage ceiling: not defined

**Assessment boundary:** Final PASS/CONCERNS/FAIL status belongs in `nfr-assess` after implementation evidence exists.

---

### Testability Concerns and Architectural Gaps

**No critical testability concerns identified.**

The architecture is highly testable. The in-memory store, stateless auth, and consistent error shape create an ideal testing environment.

#### Minor Concerns (Non-Blocking)

| Concern | Impact | What Architecture Must Provide | Owner | Timeline |
|---------|--------|-------------------------------|-------|----------|
| No structured logging | Failures in CI lack debugging context | Consider adding request ID or structured log output | Dev | Future enhancement |
| No health check endpoint | E2E tests cannot verify server readiness | FastAPI TestClient mitigates for unit/integration tests | Dev | Future enhancement |
| JWT 24h expiry | Expiration testing requires clock mocking | Use `freezegun` or manual token manipulation | Dev/TA | During test implementation |

#### Testability Assessment Summary

- ✅ **Controllability**: Excellent — in-memory store trivially resettable, JWT secret is a constant, no external services
- ✅ **Observability**: Good — consistent error shape, defined status codes, structured JWT claims
- ✅ **Reliability**: Strong — stateless auth, isolated in-memory store, no concurrency concerns
- ⚠️ **Minor gaps**: No structured logging, no health check (non-blocking)
