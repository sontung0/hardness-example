---
workflowType: 'testarch-nfr'
stepsCompleted: ['step-01-load-context', 'step-02-define-thresholds', 'step-03-gather-evidence', 'step-04-evaluate-and-score', 'step-04e-aggregate-nfr', 'step-05-generate-report']
lastStep: 'step-05-generate-report'
lastSaved: '2026-09-08'
inputDocuments:
  - test-design/test-design-epic-1.md
  - test-design/test-design-architecture.md
  - architecture/architecture-bmad-2026-09-06/ARCHITECTURE-SPINE.md
  - test-review.md
  - automation-summary.md
---

# NFR Evidence Assessment — Simple REST API: Auth

**Date:** 2026-09-08
**Author:** NST (Master Test Architect)
**Project:** bmad
**Branch:** feat/auth
**Status:** ✅ Complete

---

## Executive Summary

**Overall Risk Level: MEDIUM**

The Simple REST API Auth project has solid security fundamentals (JWT auth, bcrypt hashing, password exclusion, input validation) and excellent maintainability (97% coverage, 66 passing tests). The MEDIUM risk rating is driven by two security findings: missing rate limiting on the login endpoint (FAIL) and a weak default JWT secret key (CONCERNS). Performance and reliability are LOW risk — acceptable for a personal project but with observability gaps.

**Test Execution Evidence:**
- 66 tests passed, 0 failed (8.59s)
- Code coverage: 97.0% (128/132 statements)
- Test quality score: 88/100 (B grade)

**Gate Decision:** ⚠️ **CONCERNS** — not a hard BLOCK. The2 FAIL findings (rate limiting, monitoring) are acceptable for a personal project but should be addressed before any production use. The2 HIGH test quality findings (wall-clock JWT assertions) should be fixed to prevent CI flakiness.

---

## NFR Threshold Matrix

### Security

| NFR ID | Requirement | Threshold | Source | Status |
|--------|-------------|-----------|--------|--------|
| SEC-1 | Password hashing | bcrypt (default work factor) | AD-2, test-design | Defined |
| SEC-2 | JWT claims | `sub` = lowercased username, `exp` = 24h | AD-1, test-design | Defined |
| SEC-3 | JWT sole auth mechanism | No session cookies; Bearer token only | AD-4, test-design | Defined |
| SEC-4 | Password hash exclusion | `password_hash` never in response or store return | AD-2, test-design | Defined |
| SEC-5 | Secret management | `os.environ.get` with hardcoded fallback | auth.py | Defined |
| SEC-6 | Input validation | Pydantic models; 422→400 custom handler | AD-5, main.py | Defined |

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
| MAINT-2 | Test count | 28 P0/P1/P2 scenarios implemented | test-design | Defined |
| MAINT-3 | Test quality score | ≥ 80/100 | test-review | Defined |

### Performance

| NFR ID | Requirement | Threshold | Source | Status |
|--------|-------------|-----------|--------|--------|
| PERF-1 | Response latency | Not defined | — | UNKNOWN |
| PERF-2 | Concurrent users | Not defined (single-process) | — | UNKNOWN |

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
| QOS-2 | Friendly error messages | `{"detail": str}` (consistent, no stack traces) | AD-5 | Defined |

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

**Collection date:** 2026-09-08
**Test execution:** 66 passed, 0 failed, 54 warnings (8.59s)
**Code coverage:** 97.0% (128/132 statements)
**Test quality score:** 88/100 (from test-review.md)

### Security Evidence

| NFR ID | Evidence | Result | Source |
|--------|----------|--------|--------|
| SEC-1 | bcrypt hashing verified: `bcrypt.checkpw` assertion in T-07; hash stored as decoded UTF-8 string | ✅ PASS | tests/test_auth.py:99-117, src/services.py:13 |
| SEC-2 | JWT claims verified: `sub` = lowercased username, `exp` = 24h from issuance; decode and assert in T-24, T-25 | ✅ PASS | tests/test_auth.py:305-325, tests/unit/test_auth.py |
| SEC-3 | JWT sole auth: No session cookies; Bearer token required; 401 for missing/malformed/expired/tampered tokens (T-15 through T-19) | ✅ PASS | src/auth.py:17-38, tests/test_auth.py:237-280 |
| SEC-4 | Hash exclusion: `password_hash` never in register response (T-08), login response, `/me` response (T-20); `get_user()` strips hash (store.py:11-14) | ✅ PASS | tests/test_auth.py:119-125, 326-341, src/store.py:11-14 |
| SEC-5 | Secret management: `os.environ.get("JWT_SECRET_KEY", "super-secret-key-do-not-commit")` — env override available but default is 30 bytes (below RFC 7518 SHA256 minimum of 32 bytes) | ⚠️ CONCERNS | src/auth.py:8, PyJWT InsecureKeyLengthWarning in test output |
| SEC-6 | Input validation: Pydantic `RegisterRequest`/`LoginRequest` models; custom 422→400 handler in main.py; tested in T-02 through T-04, T-12, T-13, T-22 | ✅ PASS | src/models.py, src/main.py:10-22, tests/test_auth.py |

### Reliability Evidence

| NFR ID | Evidence | Result | Source |
|--------|----------|--------|--------|
| REL-1 | Error shape: All error responses use `{"detail": str}` — verified for register (409/400), login (401), `/me` (401), validation (400) in T-21, T-22 | ✅ PASS | tests/test_auth.py:348-381, src/routes.py |
| REL-2 | Store isolation: In-memory dict cleared before/after every test via autouse fixture; zero shared state leaks across 66 tests | ✅ PASS | tests/conftest.py (autouse fixture), test-review.md isolation rating |
| REL-3 | Token expiry handling: Expired → 401 (T-16), malformed → 401 (T-17), tampered → 401 (T-18), wrong secret → 401 (T-19) | ✅ PASS | tests/test_auth.py:242-280, tests/unit/test_auth.py |

### Maintainability Evidence

| NFR ID | Evidence | Result | Source |
|--------|----------|--------|--------|
| MAINT-1 | Code coverage: 97.0% overall (128/132); auth.py 100%, services.py 100%, store.py 100%, routes.py 100%, models.py 100%, main.py 84% | ✅ PASS | coverage.json, pytest-cov output |
| MAINT-2 | Test count: 28 P0/P1/P2 scenarios all implemented; 66 total tests across 4 test files | ✅ PASS | tests/test_auth.py, tests/unit/*.py |
| MAINT-3 | Test quality: 88/100 (B grade);2 HIGH findings (wall-clock JWT assertions),3 MEDIUM,1 LOW | ⚠️ CONCERNS | test-review.md |

### Performance Evidence

| NFR ID | Evidence | Result | Source |
|--------|----------|--------|--------|
| PERF-1 | No load tests; no SLO defined; test suite runs in ~8.59s (fast but not system perf) | ❌ UNKNOWN | No evidence |
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
| **Security** | **MEDIUM** | 4 | 2 | 1 | 0 |
| **Performance** | LOW | 0 | 2 | 0 | 2 |
| **Reliability** | LOW | 1 | 0 | 1 | 2 |
| **Maintainability** | LOW | 2 | 2 | 1 | 0 |
| **Overall** | **MEDIUM** | — | — | — | — |

### Security Domain (MEDIUM)

| Category | Status | Finding |
|----------|--------|---------|
| Authentication & Authorization | ✅ PASS | JWT Bearer token auth with comprehensive negative tests (T-14 through T-19) |
| Data Protection — Password Hashing | ✅ PASS | bcrypt with default work factor, verified by T-07 |
| Data Protection — Hash Exclusion | ✅ PASS | `password_hash` never in response (T-08, T-20, T-23) |
| Input Validation | ✅ PASS | Pydantic models + 422→400 custom handler (T-02, T-03, T-22) |
| API Security — Rate Limiting | ❌ FAIL | No rate limiting on any endpoint; brute-force risk on /login |
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
| Test Coverage | ✅ PASS | 97.0% (128/132); all critical modules at 100% |
| Test Quality | ⚠️ CONCERNS | 88/100 score;2 HIGH flakiness findings (wall-clock JWT assertions) |
| Code Duplication | ✅ PASS | Small codebase, no significant duplication |
| Dependency Health | ⚠️ CONCERNS | PyJWT InsecureKeyLengthWarning; httpx deprecation |
| Observability (Code) | ❌ FAIL | No structured logging in source code |

---

## Cross-Domain Risks

| Domains | Risk | Impact | Description |
|---------|------|--------|-------------|
| Security + Reliability | ⚠️ | MEDIUM | Missing rate limiting (security FAIL) + no monitoring (reliability FAIL) = brute-force attacks undetected |
| Reliability + Maintainability | ⚠️ | MEDIUM | No structured logging in either domain = production issues hard to diagnose |

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
| 1 | Security | Implement rate limiting on /login endpoint (anti-brute-force) | HIGH | ~2h |
| 2 | Security | Enforce JWT_SECRET_KEY ≥ 32 bytes; remove hardcoded fallback in production | HIGH | ~30m |
| 3 | Reliability | Add structured logging (Python logging module with JSON format) | MEDIUM | ~2h |
| 4 | Maintainability | Mock `time.time()` in JWT expiry assertions (fix H2 flakiness) | MEDIUM | ~30m |
| 5 | Maintainability | Add `login_payload()` factory to test helpers | LOW | ~15m |
| 6 | Security | Add CORS configuration before frontend integration | LOW | ~1h |

---

## Gate-Ready YAML

```yaml
nfr_assessment:
  date: 2026-09-08
  branch: feat/auth
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
  na_count: 6
  
  test_evidence:
    tests_passed: 66
    tests_failed: 0
    coverage_percent: 97.0
    test_quality_score: 88
  
  blocking_issues: []
  
  required_before_release:
    - "Rate limiting on /login (security FAIL)"
    - "JWT key ≥ 32 bytes (security CONCERNS)"
  
  recommended_before_release:
    - "Structured logging (reliability FAIL)"
    - "Fix wall-clock JWT test assertions (maintainability CONCERNS)"
  
  next_workflow: "trace (test traceability matrix)"
```

---

## Completion Summary

**Workflow:** NFR Evidence Audit (Create mode)
**Status:** ✅ Complete
**Date:** 2026-09-08

**Key Findings:**
- Security is the primary concern area (MEDIUM risk) — rate limiting and secret management need attention
- Maintainability is strong (97% coverage) but test quality has flakiness risks
- Performance and reliability are acceptable for personal project scope
- No critical blockers for a personal project;2 items recommended before any production use

**Next Recommended Workflow:**
- `trace` — generate test traceability matrix to validate coverage alignment with requirements
- Or address the priority actions above and re-run the NFR audit
