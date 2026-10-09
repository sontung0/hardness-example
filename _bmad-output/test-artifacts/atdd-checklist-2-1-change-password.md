---
stepsCompleted: ['step-01-preflight-and-context', 'step-02-generation-mode', 'step-03-test-strategy', 'step-04-generate-tests', 'step-04c-aggregate', 'step-05-validate-and-complete']
lastStep: 'step-05-validate-and-complete'
lastSaved: '2026-09-11'
lastSaved: '2026-09-11'
storyId: '2.1'
storyKey: '2-1-change-password'
storyFile: '_bmad-output/planning-artifacts/epics.md'
atddChecklistPath: '_bmad-output/test-artifacts/atdd-checklist-2-1-change-password.md'
generatedTestFiles:
  - tests/unit/test_store_password_change.py
  - tests/unit/test_services_password_change.py
  - tests/integration/test_password_change.py
inputDocuments:
  - _bmad-output/planning-artifacts/epics.md
  - _bmad-output/test-artifacts/test-design/test-design-epic-2.md
  - _bmad/tea/config.yaml
  - tests/conftest.py
  - tests/support/helpers/factories.py
  - tests/support/constants.py
  - pyproject.toml
---

# ATDD Checklist: Story 2.1 — Change Password

## Preflight Summary

- **Stack:** Backend (Python/FastAPI + pytest)
- **Test Framework:** pytest (configured in `pyproject.toml`)
- **Test Design:** `test-design-epic-2.md` — 21 scenarios (9 P0, 5 P1, 7 P2)
- **Branch:** `feat/password-change-api`
- **Story Status:** backlog → ready-for-dev (ATDD red phase)

## Key Requirements

| ID | Requirement | Priority | Risk |
|----|-------------|----------|------|
| FR-4 | Change password with valid current password → HTTP 200 | P0 | R-09, R-10 |
| FR-5 | Reject change with wrong current password → HTTP 401 | P0 | R-10, R-12 |
| FR-6 | Reject change with weak new password (< 8 chars) → HTTP 400 | P0 | R-11 |
| FR-7 | Reject change without authentication → HTTP 401 | P0 | — |
| NFR-7 | Current password gate + min 8 chars | P0 | R-10, R-11 |
| NFR-8 | Error semantics (same messages as login) | P0 | R-12 |
| NFR-9 | `store.update_password` as dumb writer | P0 | R-09 |
| AR-7 | Request/response shape | P1 | — |

## Existing Patterns

- **Fixtures:** `_clear_store`, `client`, `registered_user`, `auth_header`
- **Factories:** `registration_payload()` with optional overrides
- **Markers:** `@pytest.mark.unit`, `@pytest.mark.api`, `@pytest.mark.integration`
- **Error handling:** `{"detail": str}` shape, status codes (400, 401, 409)

## Red-Phase Test Plan

### Unit Tests (7 scenarios)

| ID | Scenario | Test Level | Risk Link | Req |
|----|----------|------------|-----------|-----|
| T-29 | `update_password` overwrites hash, keeps username/name | Unit | R-09 | NFR-9, AD-11 |
| T-30 | `update_password` on nonexistent user is no-op | Unit | — | — |
| T-31 | `get_user` after update returns no hash | Unit | R-09 | AD-6 |
| T-32 | `change_password` success → hashes new password | Unit | R-09 | FR-1, AD-2 |
| T-33 | `change_password` wrong current → raises ValueError | Unit | R-10 | FR-2, AD-10 |
| T-34 | `change_password` weak new (< 8 chars) → raises ValueError | Unit | R-11 | FR-3, NFR-7 |
| T-35 | `change_password` unknown user → raises ValueError | Unit | — | — |

### Integration Tests (14 scenarios)

| ID | Scenario | Test Level | Risk Link | Req |
|----|----------|------------|-----------|-----|
| T-36 | Valid change → HTTP 200 + success message | Integration | R-09 | FR-1 |
| T-37 | Old password no longer authenticates after change | Integration | R-10 | FR-1, SM-4 |
| T-38 | Weak new password (< 8 chars) → HTTP 400 | Integration | R-11 | FR-3, NFR-8 |
| T-39 | Boundary: new password exactly 8 chars → HTTP 200 | Integration | R-11 | FR-3 |
| T-40 | Missing Authorization header → HTTP 401 | Integration | — | FR-4, AD-4 |
| T-41 | Expired JWT → HTTP 401 | Integration | — | FR-4 |
| T-42 | Invalid JWT → HTTP 401 | Integration | — | FR-4 |
| T-43 | Wrong current password → HTTP 401 `"Invalid credentials"` | Integration | R-12 | FR-2, AD-10 |
| T-44 | Existing JWT remains valid after password change | Integration | R-16 | AD-4, AD-9 |
| T-45 | Error shape: all errors return `{"detail": str}` | Integration | R-13 | AD-5 |
| T-46 | Username case normalization in change-password | Integration | — | AR-6 |
| T-47 | Empty body → HTTP 400/422 | Integration | R-13 | — |
| T-48 | Missing `current_password` field → HTTP 400/422 | Integration | R-13 | — |
| T-49 | Missing `new_password` field → HTTP 400/422 | Integration | R-13 | — |

## Test Strategy

### Generation Mode
AI Generation (backend project — no browser recording needed)

### Test Level Mapping

| Level | Count | Purpose |
|-------|-------|---------|
| **Unit** | 7 | Pure functions (store.update_password, services.change_password) |
| **Integration** | 14 | API endpoints, middleware (auth), request/response validation |
| **E2E** | 0 | N/A (pure backend, no browser) |

### Priority Mapping

| Priority | Count | Criteria |
|----------|-------|----------|
| **P0** | 9 | Security-critical paths, data integrity, core functionality |
| **P1** | 5 | Core user journeys, boundary conditions, auth edge cases |
| **P2** | 7 | Secondary flows, input validation, error shape consistency |

### Red Phase Requirements

All tests designed to **fail before implementation**:
- Store functions (`update_password`) don't exist yet
- Service function (`change_password`) doesn't exist yet
- Route (`/change-password`) doesn't exist yet
- Model (`ChangePasswordRequest`) doesn't exist yet
- Tests import from modules that don't have the new functions

---

## Validation Summary

### Prerequisites ✅
- Story approved with clear acceptance criteria
- Development environment ready (.venv exists)
- Test framework configured (pytest in pyproject.toml)
- conftest.py with fixtures (_clear_store, client, registered_user, auth_header)

### Test Files Created ✅
| File | Tests | Level | Status |
|------|-------|-------|--------|
| `tests/unit/test_store_password_change.py` | 3 | Unit | Red-phase (skipped) |
| `tests/unit/test_services_password_change.py` | 4 | Unit | Red-phase (skipped) |
| `tests/integration/test_password_change.py` | 14 | Integration | Red-phase (skipped) |
| **Total** | **21** | — | **All red-phase** |

### Red-Phase Verification ✅
- All tests marked with `@pytest.mark.skip(reason="Red phase: ...")`
- Tests import from modules that don't have the new functions yet
- Confirmed: `ImportError: cannot import name 'update_password'` (expected)
- Confirmed: `ImportError: cannot import name 'change_password'` (expected)

### Test Coverage Mapping
| Test ID | Scenario | Priority | File |
|---------|----------|----------|------|
| T-29 | update_password overwrites hash | P0 | unit/test_store_password_change.py |
| T-30 | update_password nonexistent user noop | P2 | unit/test_store_password_change.py |
| T-31 | get_user after update returns no hash | P1 | unit/test_store_password_change.py |
| T-32 | change_password success | P0 | unit/test_services_password_change.py |
| T-33 | change_password wrong current | P0 | unit/test_services_password_change.py |
| T-34 | change_password weak new | P0 | unit/test_services_password_change.py |
| T-35 | change_password unknown user | P2 | unit/test_services_password_change.py |
| T-36 | Valid change → HTTP 200 | P0 | integration/test_password_change.py |
| T-37 | Old password fails after change | P0 | integration/test_password_change.py |
| T-38 | Weak new password → HTTP 400 | P0 | integration/test_password_change.py |
| T-39 | Boundary 8 chars → HTTP 200 | P1 | integration/test_password_change.py |
| T-40 | Missing auth → HTTP 401 | P0 | integration/test_password_change.py |
| T-41 | Expired JWT → HTTP 401 | P1 | integration/test_password_change.py |
| T-42 | Invalid JWT → HTTP 401 | P1 | integration/test_password_change.py |
| T-43 | Wrong current → HTTP 401 | P0 | integration/test_password_change.py |
| T-44 | JWT remains valid after change | P1 | integration/test_password_change.py |
| T-45 | Error shape consistency | P2 | integration/test_password_change.py |
| T-46 | Username case normalization | P2 | integration/test_password_change.py |
| T-47 | Empty body → HTTP 400/422 | P2 | integration/test_password_change.py |
| T-48 | Missing current_password → HTTP 400/422 | P2 | integration/test_password_change.py |
| T-49 | Missing new_password → HTTP 400/422 | P2 | integration/test_password_change.py |

### Key Risks & Assumptions
- **R-09 (Score 6):** Password hash leak — mitigated by T-29, T-30, T-31, T-36
- **R-10 (Score 6):** Old password still works — mitigated by T-37
- **R-11 (Score 6):** Weak password accepted — mitigated by T-34, T-38, T-39
- **Assumption:** `store.update_password(username, new_hash)` will be implemented as a dumb writer
- **Assumption:** `services.change_password` will handle all validation and bcrypt work
- **Assumption:** `/change-password` route will use existing `get_current_user` dependency

### Handoff Paths
| Artifact | Path |
|----------|------|
| Checklist | `_bmad-output/test-artifacts/atdd-checklist-2-1-change-password.md` |
| Story | `_bmad-output/planning-artifacts/epics.md` (Epic 2, Story 2.1) |
| Test Design | `_bmad-output/test-artifacts/test-design/test-design-epic-2.md` |
| Sprint Status | `_bmad-output/implementation-artifacts/sprint-status.yaml` |

### Next Recommended Workflow
1. **`dev-story`** — Implement Story 2.1 (Change Password)
   - Add `update_password` to `store.py`
   - Add `change_password` to `services.py`
   - Add `ChangePasswordRequest` to `models.py`
   - Add `/change-password` route to `routes.py`
   - Remove `@pytest.mark.skip` from test files
   - Run tests to verify green phase
2. **`automate`** — After implementation, expand test coverage if needed
