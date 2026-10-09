---
workflowType: 'testarch-nfr'
stepsCompleted: ['step-01-load-context', 'step-02-define-thresholds', 'step-03-gather-evidence', 'step-04-evaluate-and-score', 'step-04e-aggregate-nfr', 'step-05-generate-report']
lastStep: 'step-05-generate-report'
lastSaved: '2026-09-16'
inputDocuments:
  - test-design/test-design-architecture.md
  - test-design/test-design-epic-1.md
  - test-design/test-design-epic-2.md
  - architecture/architecture-bmad-2026-09-06/ARCHITECTURE-SPINE.md
  - test-review.md
  - automation-summary.md
  - prds/prd-bmad-2026-09-11/prd.md
---

# NFR Evidence Assessment — Simple REST API: Auth

**Date:** 2026-09-16
**Author:** NST (Master Test Architect)
**Project:** bmad
**Branch:** `feat/password-change-api`
**Status:** ✅ Complete

---

## Executive Summary

**Overall Risk Level: MEDIUM**

The Simple REST API Auth project (now including Password Management) has solid security fundamentals (JWT auth, bcrypt hashing, password exclusion, input validation) and excellent maintainability (97.70% coverage, 117 passing tests). The MEDIUM risk rating is driven by the JWT secret key weakness (30-byte default below RFC 7518 minimum). Performance and reliability are LOW risk — acceptable for a personal project but with observability gaps.

**Test Execution Evidence:**
- 117 tests passed, 0 failed (27.79s)
- Code coverage: 97.70% (170/174 statements covered, 4 missed in `main.py`)
- Test quality score: 79/100 (B grade)

**Gate Decision:** ⚠️ **CONCERNS** — not a hard BLOCK. The JWT secret key weakness (CONCERNS) and monitoring gaps (FAIL) are acceptable for a personal project but should be addressed before any production use. The test quality findings (79/100, below 80 threshold) should be fixed to improve CI confidence.

---

## NFR Threshold Matrix

### Security

| NFR ID | Requirement | Threshold | Source | Status |
|--------|-------------|-----------|--------|--------|
| SEC-1 | Password hashing | bcrypt (default work factor) | AD-2, test-design | Defined |
| SEC-2 | JWT claims | `sub` = lowercased username, `exp` = 24h | AD-1, test-design | Defined |
| SEC-3 | JWT sole auth mechanism | No session cookies; Bearer token only | AD-4, test-design | Defined |
| SEC-4 | Password hash exclusion | `password_hash` never in response or store return | AD-6, test-design | Defined |
| SEC-5 | Secret management | `os.environ.get` with hardcoded fallback | auth.py | Defined |
| SEC-6 | Input validation | Pydantic models; 422→400 custom handler | AD-5, main.py | Defined |

### Performance

| NFR ID | Requirement | Threshold | Source | Status |
|--------|-------------|-----------|--------|--------|
| PERF-1 | Response latency | Not defined | — | UNKNOWN |
| PERF-2 | Concurrent users | Not defined (single-process) | — | UNKNOWN |

### Reliability

| NFR ID | Requirement | Threshold | Source | Status |
|--------|-------------|-----------|--------|--------|
| REL-1 | Consistent error shape | `{"detail": str}` always (never list) | AD-5 | Defined |
| REL-2 | Store isolation | In-memory dict; cleared between tests | AD-3 | Defined |
| REL-3 | Token expiry handling | Expired/malformed/tampered → 401 | test-design R-02 | Defined |

### Maintainability

| NFR ID | Requirement | Threshold | Source | Status |
|--------|-------------|-----------|--------|--------|
| MAINT-1 | Test coverage | ≥ 80% on services, auth, store | test-design exit criteria | Defined |
| MAINT-2 | Test count | 28+ P0/P1/P2 scenarios | test-design | Defined |
| MAINT-3 | Test quality score | ≥ 80/100 | test-review | Defined |

### Scalability & Availability

| NFR ID | Requirement | Threshold | Source | Status |
|--------|-------------|-----------|--------|--------|
| SCAL-1 | Horizontal scaling | Not applicable (single-process, AD-3) | AD-3 | N/A |
| SCAL-2 | SLA target | Not defined | — | UNKNOWN |
| SCAL-3 | Circuit breakers | Not applicable (no external deps) | AD-3 | N/A |

### Monitorability / Debuggability

| NFR ID | Requirement | Threshold | Source | Status |
|--------|-------------|-----------|--------|--------|
| MON-1 | Structured logging | Not implemented | — | Gap |
| MON-2 | Metrics endpoint | Not implemented | — | Gap |
| MON-3 | Distributed tracing | Not applicable (single process) | — | N/A |

### QoS / QoE

| NFR ID | Requirement | Threshold | Source | Status |
|--------|-------------|-----------|--------|--------|
| QOS-1 | Rate limiting | Not implemented | — | Gap |
| QOS-2 | Friendly error messages | `{"detail": str}` (no stack traces) | AD-5 | Defined |

### Deployability

| NFR ID | Requirement | Threshold | Source | Status |
|--------|-------------|-----------|--------|--------|
| DEP-1 | Zero downtime | Not applicable (single-process personal project) | — | N/A |
| DEP-2 | Rollback | Restart process (in-memory data loss by design) | AD-3 | N/A |

### Disaster Recovery

| NFR ID | Requirement | Threshold | Source | Status |
|--------|-------------|-----------|--------|--------|
| DR-1 | RTO/RPO | Not applicable (in-memory by design, AD-3) | AD-3 | N/A |
| DR-2 | Backups | Not applicable (no persistence) | AD-3 | N/A |

---

## Evidence Collected

**Collection date:** 2026-09-16
**Test execution:** 117 passed, 0 failed (27.79s)
**Code coverage:** 97.70% (170/174 statements, 4 missed in `main.py` L24, L34-35, L38)
**Test quality score:** 79/100 (from test-review.md)

### Security Evidence

| NFR ID | Evidence | Result | Source |
|--------|----------|--------|--------|
| SEC-1 | bcrypt hashing verified: `bcrypt.checkpw` assertion in T-07; hash stored as decoded UTF-8 string | ✅ PASS | tests/test_auth.py:99-117, src/services.py:13 |
| SEC-2 | JWT claims verified: `sub` = lowercased username (T-AUTH-02), `exp` = 24h (T-AUTH-03), HS256 algorithm (T-AUTH-05) | ✅ PASS | tests/unit/test_auth.py:29-35 |
| SEC-3 | JWT sole auth: No session cookies; Bearer token required; 401 for missing/malformed/expired/tampered tokens | ✅ PASS | src/auth.py:17-42, tests/unit/test_auth.py, tests/test_auth.py:237-280 |
| SEC-4 | Hash exclusion: `password_hash` never in register (T-08), login, `/me` (T-20), change-password (T-50); `get_user()` strips hash | ✅ PASS | tests/test_auth.py:119-125, src/store.py:11-14 |
| SEC-5 | Secret management: `os.environ.get("JWT_SECRET_KEY", "super-secret-key-do-not-commit")` — env override available but default is 30 bytes (below RFC 7518 SHA256 minimum of 32 bytes) | ⚠️ CONCERNS | src/auth.py:6, PyJWT InsecureKeyLengthWarning |
| SEC-6 | Input validation: Pydantic `RegisterRequest`/`LoginRequest`/`ChangePasswordRequest` models; custom 422→400 handler; tested in T-02 through T-04, T-12, T-13, T-52, T-57 | ✅ PASS | src/models.py, src/main.py:10-22 |

### Reliability Evidence

| NFR ID | Evidence | Result | Source |
|--------|----------|--------|--------|
| REL-1 | Error shape: All error responses use `{"detail": str}` — verified for register, login, `/me`, change-password, validation | ✅ PASS | tests/integration/test_password_change.py, src/routes.py |
| REL-2 | Store isolation: In-memory dict cleared before/after every test via autouse fixture; zero shared state leaks across 117 tests | ✅ PASS | tests/conftest.py (autouse fixture) |
| REL-3 | Token expiry handling: Expired → 401 (T-AUTH-16, T-41, T-55), malformed → 401 (T-AUTH-17), tampered → 401 (T-AUTH-10), wrong secret → 401 (T-AUTH-08) | ✅ PASS | tests/unit/test_auth.py, tests/api/test_change_password.py |

### Maintainability Evidence

| NFR ID | Evidence | Result | Source |
|--------|----------|--------|--------|
| MAINT-1 | Code coverage: 97.70% overall (170/174); auth.py 100%, services.py 100%, store.py 100%, routes.py 100%, models.py 100%, main.py 84% | ✅ PASS | coverage.xml |
| MAINT-2 | Test count: 117 tests across 8 test files (unit, integration, api, structural) | ✅ PASS | automation-summary.md |
| MAINT-3 | Test quality: 79/100 (B grade); HIGH findings: shape-only assertions (H10), wall-clock JWT assertions (H2), conditional assertion (H3) | ⚠️ CONCERNS | test-review.md |

### Performance Evidence

| NFR ID | Evidence | Result | Source |
|--------|----------|--------|--------|
| PERF-1 | No load tests; no SLO defined; test suite runs in 27.79s (fast but not system perf) | ❌ UNKNOWN | No evidence |
| PERF-2 | No concurrent user testing; single-process by design | ❌ UNKNOWN | No evidence |

### Scalability & Availability Evidence

| NFR ID | Evidence | Result | Source |
|--------|----------|--------|--------|
| SCAL-1 | N/A — single-process, in-memory (AD-3) | N/A | ARCHITECTURE-SPINE.md |
| SCAL-2 | No SLA defined | UNKNOWN | No evidence |
| SCAL-3 | N/A — no external dependencies to circuit-break | N/A | ARCHITECTURE-SPINE.md |

### Monitorability Evidence

| NFR ID | Evidence | Result | Source |
|--------|----------|--------|--------|
| MON-1 | No structured logging (no `logging` module usage in src/) | ❌ FAIL | src/*.py — no logging imports |
| MON-2 | No `/metrics` endpoint or Prometheus/Datadog integration | ❌ FAIL | src/main.py — no metrics |
| MON-3 | N/A — single process, no distributed tracing needed | N/A | — |

### QoS Evidence

| NFR ID | Evidence | Result | Source |
|--------|----------|--------|--------|
| QOS-1 | No rate limiting on any endpoint | ❌ FAIL | src/routes.py — no rate limit middleware |
| QOS-2 | Consistent error responses: no stack traces exposed, `{"detail": str}` shape always | ✅ PASS | AD-5, test-auth T-21 |

### Testability Evidence

| NFR ID | Evidence | Result | Source |
|--------|----------|--------|--------|
| TEST-1 | Isolation: autouse `_clear_store` fixture clears store between all tests | ✅ PASS | conftest.py |
| TEST-2 | Headless interaction: All logic accessible via FastAPI TestClient | ✅ PASS | Architecture AD-2 |
| TEST-3 | State control: In-memory dict manipulation + test factories (`random_username`, `random_password`, `registration_payload`) | ✅ PASS | factories.py, conftest.py |
| TEST-4 | Sample requests: Pydantic models define request/response contract | ✅ PASS | models.py |

### Deployability & Disaster Recovery Evidence

| NFR ID | Evidence | Result | Source |
|--------|----------|--------|--------|
| DEP-1 | N/A — single-process personal project | N/A | — |
| DEP-2 | N/A — restart = rollback; data loss by design (AD-3) | N/A | AD-3 |
| DR-1 | N/A — in-memory by design; no persistence to recover | N/A | AD-3 |
| DR-2 | N/A — no backups needed (no persistence) | N/A | AD-3 |

### Deployability Evidence

| NFR ID | Evidence | Result | Source |
|--------|----------|--------|--------|
| DEP-1 | N/A — single-process personal project | N/A | — |
| DEP-2 | N/A — restart = rollback; data loss by design (AD-3) | N/A | AD-3 |

### Disaster Recovery Evidence

| NFR ID | Evidence | Result | Source |
|--------|----------|--------|--------|
| DR-1 | N/A — in-memory by design; no persistence to recover | N/A | AD-3 |
| DR-2 | N/A — no backups needed (no persistence) | N/A | AD-3 |

---

## Domain Risk Assessment

| Domain | Risk Level | PASS | CONCERNS | FAIL | N/A |
|--------|-----------|------|----------|------|-----|
| **Security** | **MEDIUM** | 4 | 2 | 0 | 0 |
| **Performance** | LOW | 0 | 2 | 0 | 0 |
| **Reliability** | LOW | 1 | 0 | 0 | 2 |
| **Maintainability** | LOW | 2 | 2 | 1 | 0 |

### Security Domain (MEDIUM)

| Category | Status | Finding |
|----------|--------|--------|
| Authentication & Authorization | ✅ PASS | JWT Bearer token auth with comprehensive negative tests (T-AUTH-11 through T-AUTH-18, T-14 through T-19) |
| Data Protection — Password Hashing | ✅ PASS | bcrypt with default work factor, verified by T-07 |
| Data Protection — Hash Exclusion | ✅ PASS | `password_hash` never in response (T-08, T-20, T-50); `get_user()` strips hash |
| Input Validation | ✅ PASS | Pydantic models + 422→400 custom handler (T-02, T-03, T-22, T-52, T-57) |
| API Security — Rate Limiting | ⚠️ CONCERNS | No rate limiting on any endpoint; brute-force risk on /login |
| API Security — CORS & Headers | ⚠️ CONCERNS | No CORS or security headers configured |
| Secrets Management | ⚠️ CONCERNS | Hardcoded 30-byte fallback key (below RFC 7518 SHA256 minimum of 32 bytes) |

### Performance Domain (LOW)

| Category | Status | Finding |
|----------|--------|---------|
| Response Times | ⚠️ CONCERNS | No SLOs defined, no load tests (UNKNOWN threshold) |
| Throughput | ⚠️ CONCERNS | No concurrent user testing, single-process |
| Resource Usage | N/A | Not applicable for personal project |
| Optimization | N/A | No database, no external calls |

### Reliability Domain (LOW)

| Category | Status | Finding |
|----------|--------|---------|
| Error Handling | ✅ PASS | Consistent `{"detail": str}` shape; comprehensive auth error paths |
| Fault Tolerance | N/A | No external dependencies |
| Monitoring & Observability | ❌ FAIL | No structured logging, no health check endpoint |
| Uptime & Availability | N/A | No SLA defined |

### Maintainability Domain (LOW)

| Category | Status | Finding |
|----------|--------|---------|
| Test Coverage | ✅ PASS | 97.70% (170/174); all critical modules at 100% |
| Test Quality | ⚠️ CONCERNS | 79/100 score (below 80 threshold); 13 HIGH flakiness findings |
| Code Duplication | ✅ PASS | Small codebase, no significant duplication |
| Dependency Health | ⚠️ CONCERNS | PyJWT InsecureKeyLengthWarning |
| Observability (Code) | ❌ FAIL | No structured logging in source code |

---

## Cross-Domain Risks

| Domains | Risk | Impact | Description |
|---------|------|--------|-------------|
| Security + Reliability | ⚠️ | MEDIUM | No rate limiting (QOS-1 FAIL) + no monitoring (MON-1, MON-2 FAIL) = brute-force attacks undetected |
| Reliability + Maintainability | ⚠️ | MEDIUM | No structured logging in either domain = production issues hard to diagnose; test quality (79/100) below 80 target |

---

## Compliance Summary

| Standard | Status | Notes |
|----------|--------|-------|
| SOC2 | PARTIAL | Auth controls present; monitoring/logging gaps |
| GDPR | N/A | No PII processing beyond username/password |
| HIPAA | N/A | Not applicable |
| PCI-DSS | N/A | Not applicable |
| ISO 27001 | PARTIAL | Security controls present; operational gaps |

---

## Priority Actions

| # | Domain | Action | Urgency | Effort |
|---|--------|--------|---------|--------|
| 1 | Security | Enforce JWT_SECRET_KEY ≥ 32 bytes; remove hardcoded fallback in production | HIGH | ~30m |
| 2 | Security | Implement rate limiting on /login endpoint (anti-brute-force) | HIGH | ~2h |
| 3 | Maintainability | Fix 13 HIGH-severity test quality findings (shape-only assertions, wall-clock JWT tests) | MEDIUM | ~2h |
| 4 | Reliability | Add structured logging (Python logging module with JSON format) | MEDIUM | ~2h |
| 5 | Security | Add CORS configuration before frontend integration | LOW | ~1h |
| 6 | Reliability | Add `/health` endpoint for monitoring | LOW | ~30m |

---

## Gate-Ready YAML

```yaml
nfr_assessment:
  date: 2026-09-16
  branch: feat/password-change-api
  overall_risk: MEDIUM
  gate_decision: CONCERNS
  
  domain_scores:
    security: MEDIUM
    performance: LOW
    reliability: LOW
    maintainability: LOW
  
  pass_count: 7
  concerns_count: 6
  fail_count: 3
  na_count: 8
  
  test_evidence:
    tests_passed: 117
    tests_failed: 0
    coverage_percent: 97.70
    test_quality_score: 79
  
  blocking_issues: []
  
  required_before_release:
    - "JWT key ≥ 32 bytes (security CONCERNS)"
    - "Rate limiting on /login (security CONCERNS)"
  
  recommended_before_release:
    - "Structured logging (reliability FAIL)"
    - "Fix 13 HIGH-severity test quality findings (maintainability CONCERNS)"
    - "Add /health endpoint (reliability)"
  
  next_workflow: "trace (test traceability matrix)"
```

---

## Completion Summary

**Workflow:** NFR Evidence Audit (Create mode)
**Status:** ✅ Complete
**Date:** 2026-09-16

**Key Findings:**
- Security is the primary concern area (MEDIUM risk) — JWT key strength and rate limiting need attention
- Maintainability is strong (97.70% coverage, 117 tests) but test quality (79/100) falls below the 80 threshold due to 13 HIGH-severity findings
- Performance and reliability are acceptable for personal project scope, but monitoring gaps (no logging, no metrics, no health check) should be addressed before any production use
- No critical blockers for a personal project; 2 items recommended before any production use

**Next Recommended Workflow:**
- `trace` — generate test traceability matrix to validate coverage alignment with requirements
- Or address the priority actions above and re-run the NFR audit
