---
runScope: 'epic-level'
runKey: 'epic-2'
workflowStatus: 'completed'
totalSteps: 5
stepsCompleted: ['step-01-detect-mode', 'step-02-load-context', 'step-03-risk-and-testability', 'step-04-coverage-plan', 'step-05-generate-output']
lastStep: 'step-05-generate-output'
nextStep: ''
lastSaved: '2026-09-11'
---

# Test Design Progress — Epic 2: Password Management

## Inputs

- Epic: `_bmad-output/planning-artifacts/epics.md` (Epic 2: Story 2.1 — Change Password)
- Architecture: `_bmad-output/planning-artifacts/architecture/architecture-bmad-2026-09-06/ARCHITECTURE-SPINE.md`
- System-Level Test Design: `_bmad-output/test-artifacts/test-design-progress-system.md`
- Epic-1 Test Design: `_bmad-output/test-artifacts/test-design-progress-epic-1.md`

## Step 1: Mode Detection

- **Mode**: Epic-Level
- **Run Key**: epic-2
- **Branch**: `feat/password-change-api`
- **Epic**: Epic 2 — Password Management (Story 2.1)
- **Requirements Covered**: FR-4 through FR-7, NFR-7 through NFR-9, AR-7
- **No prior checkpoint** — fresh run

## Step 2: Context & Knowledge Base Loaded

### Configuration

| Flag | Value |
|------|-------|
| `tea_use_playwright_utils` | true |
| `tea_use_pactjs_utils` | true |
| `tea_pact_mcp` | mcp |
| `tea_browser_automation` | auto |
| `test_stack_type` | auto → **backend** (pyproject.toml, FastAPI) |
| `test_artifacts` | `_bmad-output/test-artifacts` |
| `risk_threshold` | p1 |

### Project Artifacts Loaded

- **PRD**: `_bmad-output/planning-artifacts/prds/prd-bmad-2026-09-11/prd.md` — Password Change API (FR-1 through FR-4)
- **Architecture**: `_bmad-output/planning-artifacts/architecture/architecture-bmad-2026-09-06/ARCHITECTURE-SPINE.md` — AD-1 through AD-11
- **Epics**: `_bmad-output/planning-artifacts/epics.md` — Epic 2: Password Management (Story 2.1)
- **System-Level Test Design**: `_bmad-output/test-artifacts/test-design-progress-system.md` — prior NFR planning, risk assessment
- **Epic-1 Test Design**: `_bmad-output/test-artifacts/test-design-progress-epic-1.md` — 28 scenarios, R-01 through R-08

### Existing Source Files

- `src/services.py` — `register_user`, `authenticate_user`, `get_current_user_profile` (no `change_password` yet)
- `src/store.py` — `add_user`, `get_user`, `get_user_with_hash`, `user_exists` (no `update_password` yet)
- `src/routes.py` — `/register`, `/login`, `/me` (no `/change-password` yet)
- `src/auth.py` — JWT creation/verification, `get_current_user` dependency
- `src/models.py` — Pydantic request/response models

### Existing Test Coverage

| Test File | Scenarios | Coverage |
|-----------|-----------|----------|
| `tests/unit/test_services.py` | 8 | register, authenticate, get_current_user_profile |
| `tests/unit/test_store.py` | 8 | add_user, get_user, get_user_with_hash, user_exists |
| `tests/unit/test_auth.py` | 18 | create_access_token, decode_token, get_current_user |
| `tests/unit/test_structure.py` | — | Project structure validation |
| `tests/conftest.py` | — | Store clearing fixture |

**Gap**: No tests for `change_password` — feature not yet implemented on this branch.

### Knowledge Fragments Loaded (Core Tier)

- `risk-governance.md` — Risk scoring matrix, gate decision rules
- `probability-impact.md` — P×I scale definitions
- `test-levels-framework.md` — Unit vs integration vs E2E selection
- `test-priorities-matrix.md` — P0–P3 criteria, coverage targets
- `nfr-criteria.md` — NFR review criteria (security, performance, reliability)

### Confirmed Inputs

All required inputs for Epic-Level mode are loaded. No missing artifacts. Proceeding to Step 3.

---

## Step 3: Testability & Risk Assessment

### 1. Testability Review (Epic-Level)

System-level testability review confirmed **highly testable** architecture. Epic-level assessment maps testability to Story 2.1:

#### Story-Level Testability

| Aspect | Assessment | Evidence |
|--------|------------|----------|
| **Controllability** | **Strong** — In-memory store trivially resettable; FastAPI TestClient supports full HTTP lifecycle | AD-3: module-level dict, conftest clears between tests |
| **Mockability** | **Strong** — No external services; bcrypt is deterministic; JWT secret is a constant | AD-4: hardcoded secret, no DI needed |
| **Fault injection** | **Moderate** — TestClient supports HTTP-level errors; no granular fault injection framework | No health check or circuit breaker pattern |
| **Observability** | **Strong** — Consistent `{"detail": str}` error shape; well-defined status codes per scenario | AD-5, AD-10: error semantics defined |
| **Reproducibility** | **Strong** — Deterministic inputs → deterministic outputs; no time-dependent logic except JWT exp | AD-4: JWT claims are deterministic |
| **Isolation** | **Strong** — Fresh store per test; no shared mutable state across tests | conftest autouse fixture |

#### 🚨 Testability Concerns

1. **Password change store mutation** — `update_password` function does not yet exist in `store.py`. Must be implemented before tests can run. *Severity: Low (straightforward implementation).*  
2. **JWT expiration after password change** — Testing that the old JWT still works post-change requires constructing valid tokens. *Severity: Low (pattern already established in Epic 1 tests).*  
3. **Old password login verification** — Testing that the old password no longer works requires a full login flow after change. *Severity: Low (integration test covers this).*  

#### ✅ Testability Summary

Story 2.1 is **fully testable** at all levels. The only prerequisite is implementing `update_password` in `store.py` and `change_password` in `services.py`. No architectural blockers.

---

### 2. Risk Assessment

Risks mapped from system-level assessment to Epic 2, with new risks identified:

#### High-Priority Risks (Score ≥6) — Require Mitigation Before Release

| ID | Category | Title | P | I | Score | Action | Mitigation | Status |
|----|----------|-------|---|---|-------|--------|------------|--------|
| **R-09** | **SEC** | Password hash leak during update | 2 | 3 | **6** | MITIGATE | T-01, T-02: assert `password_hash` never in response; T-03: verify store mutation only overwrites hash field | 🔲 Planned |
| **R-10** | **BUS** | Old password still works after change | 2 | 3 | **6** | MITIGATE | T-05: login with old password must return 401 after successful change | 🔲 Planned |
| **R-11** | **SEC** | Weak password accepted | 2 | 3 | **6** | MITIGATE | T-04: password < 8 chars → 400; boundary test at exactly 8 chars | 🔲 Planned |

#### Medium-Priority Risks (Score 3-5)

| ID | Category | Title | P | I | Score | Action | Mitigation | Status |
|----|----------|-------|---|---|-------|--------|------------|--------|
| R-12 | SEC | User enumeration via error messages | 2 | 2 | 4 | MONITOR | T-06: wrong current password → same `"Invalid credentials"` as login | 🔲 Planned |
| R-13 | BUS | Missing fields not validated | 2 | 2 | 4 | MONITOR | T-07, T-08: empty body, missing fields → 400/422 | 🔲 Planned |

#### Low-Priority Risks (Score 1-2)

| ID | Category | Title | P | I | Score | Action | Status |
|----|----------|-------|---|---|-------|--------|--------|
| R-14 | SEC | bcrypt work factor unchanged | 1 | 2 | 2 | DOCUMENT | ✅ Noted |
| R-15 | OPS | No rate limiting on failed attempts | 1 | 2 | 2 | DOCUMENT | ✅ Out of scope |
| R-16 | TECH | JWT not rotated after change | 1 | 2 | 2 | DOCUMENT | ✅ By design (AD-4) |

---

### 3. NFR Planning Assessment

| NFR | Category | Threshold | Evidence Source | Epic Coverage | Status |
|-----|----------|-----------|----------------|---------------|--------|
| **NFR-7** | SEC | Current password verified before accepting new one; new password ≥ 8 chars | T-01, T-04, T-05 | Story 2.1 | ✅ Planned |
| **NFR-8** | SEC | Wrong current password → 400 with `"Invalid credentials"`; weak password → 400 with length message | T-04, T-06 | Story 2.1 | ✅ Planned |
| **NFR-9** | TECH | `store.update_password(username, new_hash)` — dumb writer; all bcrypt in services | T-02, T-03 | Story 2.1 | ✅ Planned |
| **AD-2** | SEC | Passwords hashed with bcrypt in services.py only; store never sees plaintext | T-01, T-02, T-03 | Story 2.1 | ✅ Planned |
| **AD-5** | TECH | Consistent error shape `{"detail": str}` for all errors | T-04, T-06, T-07, T-08 | Story 2.1 | ✅ Planned |
| **AD-9** | SEC | Current password gate; min 8 chars; no token rotation | T-01, T-04, T-05 | Story 2.1 | ✅ Planned |
| **AD-10** | SEC | Wrong password → same generic message as login; no user enumeration | T-06 | Story 2.1 | ✅ Planned |
| **AD-11** | TECH | Store update_password is a dumb writer; bcrypt stays in services | T-02, T-03 | Story 2.1 | ✅ Planned |

**UNKNOWN thresholds (carried from system-level):**
- bcrypt cost factor: default (acceptable for personal project)
- Response time SLO: not defined (not in scope)
- Concurrent user limit: not defined (single-process)

---

### 4. Summary of Risk Findings

| Metric | Value |
|--------|-------|
| Total risks identified | 8 (R-09 through R-16) |
| High-priority (score ≥6) | 3 (R-09, R-10, R-11) — all have planned test mitigations |
| Medium-priority (score 3-5) | 2 (R-12, R-13) — monitored with planned tests |
| Low-priority (score 1-2) | 3 (R-14, R-15, R-16) — documented, no action needed |
| NFR coverage gaps | 0 — all 4 NFRs (NFR-7, NFR-8, NFR-9) + 4 ADs have planned validation |
| Testability blockers | 0 — architecture is fully testable |

**Conclusion:** Epic 2 has **no unmitigated high risks**. All 3 high-priority risks (R-09, R-10, R-11) have planned test mitigations. The epic is ready for test design and implementation.

---

## Step 4: Coverage Plan & Execution Strategy

### 1. Coverage Matrix — Epic 2

All scenarios mapped to test levels, priorities, and risk links:

#### Store Layer (`store.py`)

| ID | Scenario | Level | Priority | Risk | Req |
|----|----------|-------|----------|------|-----|
| T-29 | `update_password` overwrites hash, keeps username/name | Unit | **P0** | R-09 | NFR-9, AD-11 |
| T-30 | `update_password` on nonexistent user is no-op | Unit | **P2** | — | — |
| T-31 | `get_user` after update returns no hash | Unit | **P1** | R-09 | AD-6 |

#### Services Layer (`services.py`)

| ID | Scenario | Level | Priority | Risk | Req |
|----|----------|-------|----------|------|-----|
| T-32 | `change_password` success → hashes new password | Unit | **P0** | R-09 | FR-1, AD-2 |
| T-33 | `change_password` wrong current → raises ValueError | Unit | **P0** | R-10 | FR-2, AD-10 |
| T-34 | `change_password` weak new (< 8 chars) → raises ValueError | Unit | **P0** | R-11 | FR-3, NFR-7 |
| T-35 | `change_password` unknown user → raises ValueError | Unit | **P2** | — | — |

#### API Integration (`routes.py` via TestClient)

| ID | Scenario | Level | Priority | Risk | Req |
|----|----------|-------|----------|------|-----|
| T-36 | Valid change → HTTP 200 + `{"message": "Password changed successfully"}` | Integration | **P0** | R-09 | FR-1, AD-7 |
| T-37 | Old password no longer authenticates after change | Integration | **P0** | R-10 | FR-1, SM-4 |
| T-38 | Weak new password (< 8 chars) → HTTP 400 | Integration | **P0** | R-11 | FR-3, NFR-8 |
| T-39 | Boundary: new password exactly 8 chars → HTTP 200 | Integration | **P1** | R-11 | FR-3 |
| T-40 | Missing Authorization header → HTTP 401 | Integration | **P0** | — | FR-4, AD-4 |
| T-41 | Expired JWT → HTTP 401 | Integration | **P1** | — | FR-4 |
| T-42 | Invalid JWT → HTTP 401 | Integration | **P1** | — | FR-4 |
| T-43 | Wrong current password → HTTP 401 `"Invalid credentials"` | Integration | **P0** | R-12 | FR-2, AD-10 |
| T-44 | Existing JWT remains valid after password change | Integration | **P1** | R-16 | AD-4, AD-9 |
| T-45 | Error shape: all errors return `{"detail": str}` | Integration | **P1** | R-13 | AD-5, NFR-5 |
| T-46 | Username case normalization in change-password | Integration | **P2** | — | AR-6 |
| T-47 | Empty body → HTTP 400/422 | Integration | **P2** | R-13 | — |
| T-48 | Missing `current_password` field → HTTP 400/422 | Integration | **P2** | R-13 | — |
| T-49 | Missing `new_password` field → HTTP 400/422 | Integration | **P2** | R-13 | — |

### Summary

| Test Level | Count | P0 | P1 | P2 |
|------------|-------|----|----|-----|
| Unit | 7 | 4 | 1 | 2 |
| Integration | 14 | 5 | 4 | 5 |
| **Total** | **21** | **9** | **5** | **7** |

---

### 2. NFR Coverage & Evidence Plan

| NFR | Validation Scenarios | Evidence Artifact |
|-----|---------------------|-------------------|
| **NFR-7** (Password gate) | T-32, T-33, T-34, T-36, T-38, T-39 | pytest output (unit + integration) |
| **NFR-8** (Error semantics) | T-38, T-43, T-45 | pytest output: status codes + response bodies |
| **NFR-9** (Store mutation) | T-29, T-30, T-31, T-32 | pytest output: store state assertions |
| **AD-2** (Hashing in services) | T-32, T-36 | pytest: store receives hash, not plaintext |
| **AD-5** (Error shape) | T-45 | pytest: response body shape assertions |
| **AD-9** (Password gate) | T-32, T-34, T-36 | pytest: full gate flow |
| **AD-10** (No enumeration) | T-43 | pytest: error message identical to login |
| **AD-11** (Dumb writer) | T-29 | pytest: store mutation is minimal |

---

### 3. Execution Strategy

| Gate | Tests | Est. Time | Trigger |
|------|-------|-----------|---------|
| **PR** | All P0 + P1 (T-29 through T-45) | ~2–4 min | Every push to `feat/password-change-api` |
| **Merge** | All P0 + P1 + P2 (full suite) | ~3–5 min | Before merge to `main` |
| **Nightly** | Full regression (Epic 1 + Epic 2) | ~5–8 min | Nightly CI |

---

### 4. Resource Estimates

| Priority | Estimated Effort |
|----------|-----------------|
| P0 (9 tests) | ~4–6 hours (unit + integration implementation) |
| P1 (5 tests) | ~2–3 hours |
| P2 (7 tests) | ~2–3 hours |
| **Total** | **~8–12 hours** |

---

### 5. Quality Gates

| Gate | Threshold |
|------|-----------|
| P0 pass rate | **100%** |
| P1 pass rate | **≥ 95%** |
| High-risk mitigations (R-09, R-10, R-11) | **All complete** before release |
| Code coverage (statements) | **≥ 80%** for `services.py`, `store.py`, `routes.py` |
| NFR evidence | All 8 NFR/AD items have planned evidence |
| Full NFR status | Deferred to `nfr-assess` when implementation evidence exists |
