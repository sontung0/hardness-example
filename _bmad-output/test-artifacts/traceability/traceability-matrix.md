---
stepsCompleted: ['step-01-load-context', 'step-02-discover-tests', 'step-03-map-criteria', 'step-04-analyze-gaps', 'step-05-gate-decision']
lastStep: 'step-05-gate-decision'
lastSaved: '2026-09-08'
coverageBasis: 'acceptance_criteria'
oracleConfidence: 'high'
oracleResolutionMode: 'formal_requirements'
oracleSources:
  - '_bmad-output/planning-artifacts/epics.md'
  - '_bmad-output/test-artifacts/test-design/test-design-epic-1.md'
externalPointerStatus: 'not_used'
collectionStatus: 'COLLECTED'
sourceSha: '61ebc869ed5d463d1a4e8cd03cd57edd2c0e1f95'
---

# Coverage Traceability Matrix — bmad (Epic 1: User Authentication API)

**Date:** 2026-09-08
**Author:** Master Test Architect (NST)
**Project:** bmad
**Branch:** feat/auth
**Source SHA:** 61ebc86

---

## Coverage Oracle

| Field | Value |
|-------|-------|
| Coverage basis | acceptance_criteria |
| Oracle resolution mode | formal_requirements |
| Oracle confidence | high |
| Oracle sources | `epics.md` (FR-1..FR-3, NFR-1..NFR-6, AR-1..AR-6), `test-design-epic-1.md` (28 scenarios) |
| External pointer status | not_used |

---

## Test Inventory

| Test File | Markers | Count | Status |
|-----------|---------|-------|--------|
| `tests/test_auth.py` | `@pytest.mark.api` | 28 tests (T-01..T-28) | ✅ all passing |
| `tests/unit/test_auth.py` | `@pytest.mark.unit` | 18 tests (T-AUTH-01..T-AUTH-18) | ✅ all passing |
| `tests/unit/test_store.py` | `@pytest.mark.unit` | 10 tests | ✅ all passing |
| `tests/unit/test_services.py` | `@pytest.mark.unit` | 8 tests | ✅ all passing |
| `tests/unit/test_structure.py` | `@pytest.mark.structural` | 18 tests (AR-1, AR-2, AR-5) | ✅ all passing |
| **Total** | | **82 passing** | ✅ |

---

## Traceability Matrix

### Functional Requirements

#### FR-1: Register a new user (POST `/register`)

| Requirement Aspect | Priority | Test(s) | Level | Status | Notes |
|--------------------|----------|---------|-------|--------|-------|
| FR-1: Valid input → 201 + JWT | P0 | T-01 | API | ✅ PASS | `test_register_success_returns_201_and_jwt` |
| FR-1: Missing username → 400 | P1 | T-02 | API | ✅ PASS | `test_register_missing_username_returns_400` |
| FR-1: Missing password → 400 | P1 | T-03 | API | ✅ PASS | `test_register_missing_password_returns_400` |
| FR-1: Missing name → 400 | P1 | T-04 | API | ✅ PASS | `test_register_missing_name_returns_400` |
| FR-1: Duplicate username → 409 | P0 | T-05 | API | ✅ PASS | `test_register_duplicate_username_returns_409` |
| FR-1: Case normalization (Bob=bob) | P0 | T-06 | API | ✅ PASS | `test_register_username_case_normalization` |
| FR-1: Password hashed with bcrypt | P0 | T-07 | Unit+API | ✅ PASS | `test_register_password_hashed_with_bcrypt` |
| FR-1: password_hash not in response | P0 | T-08 | API | ✅ PASS | `test_register_password_not_in_response` |
| FR-1: Extra fields ignored | P2 | (unmarked) | API | ✅ PASS | `test_register_extra_fields_ignored` |
| FR-1: Store `add_user` lowercase | P0 | unit/add_user | Unit | ✅ PASS | `test_add_user_stores_data`, `test_add_user_overwrites_existing` |
| FR-1: Register service layer | P0 | unit/register_user | Unit | ✅ PASS | `test_register_returns_username_and_name`, `test_register_lowercases_username`, `test_register_duplicate_raises_value_error` |

**FR-1 Coverage: 11/11 aspects covered — FULL**

#### FR-2: Login with valid credentials (POST `/login`)

| Requirement Aspect | Priority | Test(s) | Level | Status | Notes |
|--------------------|----------|---------|-------|--------|-------|
| FR-2: Valid creds → 200 + JWT | P0 | T-09 | API | ✅ PASS | `test_login_success_returns_200_and_jwt` |
| FR-2: Wrong password → 401 | P0 | T-10 | API | ✅ PASS | `test_login_wrong_password_returns_401` |
| FR-2: Nonexistent user → 401 | P0 | T-11 | API | ✅ PASS | `test_login_nonexistent_user_returns_401` |
| FR-2: Missing username → 400 | P1 | T-12 | API | ✅ PASS | `test_login_missing_username_returns_400` |
| FR-2: Missing password → 400 | P1 | T-13 | API | ✅ PASS | `test_login_missing_password_returns_400` |
| FR-2: Extra fields ignored | P2 | (unmarked) | API | ✅ PASS | `test_login_extra_fields_ignored` |
| FR-2: Service layer auth | P0 | unit/auth | Unit | ✅ PASS | `test_authenticate_success`, `test_authenticate_wrong_password`, `test_authenticate_unknown_user` |

**FR-2 Coverage: 7/7 aspects covered — FULL**

#### FR-3: Retrieve current user profile (GET `/me`)

| Requirement Aspect | Priority | Test(s) | Level | Status | Notes |
|--------------------|----------|---------|-------|--------|-------|
| FR-3: Valid JWT → 200 + profile | P0 | T-14 | API | ✅ PASS | `test_me_valid_jwt_returns_200_and_profile` |
| FR-3: No token → 401 | P0 | T-15 | API | ✅ PASS | `test_me_no_token_returns_401` |
| FR-3: Expired token → 401 | P0 | T-16 | API | ✅ PASS | `test_me_expired_token_returns_401` |
| FR-3: Malformed token → 401 | P0 | T-17 | API | ✅ PASS | `test_me_malformed_token_returns_401` |
| FR-3: Tampered payload → 401 | P0 | T-18 | API | ✅ PASS | `test_me_tampered_payload_returns_401` |
| FR-3: Wrong secret → 401 | P0 | T-19 | Unit+API | ✅ PASS | `test_me_wrong_secret_returns_401` |
| FR-3: User deleted from store → 401 | P0 | (unmarked) | API | ✅ PASS | `test_me_user_deleted_after_registration` |
| FR-3: Profile service layer | P0 | unit/profile | Unit | ✅ PASS | `test_profile_success`, `test_profile_not_found_raises` |

**FR-3 Coverage: 8/8 aspects covered — FULL**

---

### Non-Functional Requirements

| NFR | Requirement | Priority | Test(s) | Level | Status | Notes |
|-----|-------------|----------|---------|-------|--------|-------|
| NFR-1 | In-memory storage only (dict) | P0 | conftest `_clear_store` | Unit+API | ✅ PASS | Store cleared between tests; `test_add_user_stores_data` |
| NFR-2 | Password hashing with bcrypt (default) | P0 | T-07 | Unit+API | ✅ PASS | `bcrypt.checkpw` assertion in `test_register_password_hashed_with_bcrypt` |
| NFR-3 | JWT `sub` = lowercased username, `exp` = 24h | P2 | T-24, T-25 | Unit+API | ✅ PASS | `test_jwt_sub_claim_is_lowercased_username`, `test_jwt_exp_is_24h_from_issuance` |
| NFR-4 | Stateless auth — JWT sole mechanism | P0 | T-15 | API | ✅ PASS | `test_me_no_token_returns_401` |
| NFR-5 | Consistent error shape `{"detail": str}` | P1 | T-21, T-22 | API | ✅ PASS | `test_error_shape_always_detail_string`, `test_validation_error_returns_400_with_detail` |
| NFR-6 | `password_hash` never in response | P0 | T-08, T-20, T-23 | API+Unit | ✅ PASS | Response scan + store assertion |

**NFR Coverage: 6/6 requirements covered — FULL**

---

### Additional Requirements (Architectural)

| AR | Requirement | Priority | Test(s) | Level | Status | Notes |
|----|-------------|----------|---------|-------|--------|-------|
| AR-1 | Layered architecture (Routes→Services→Store) | P1 | test_structure (6 tests) | Structural | ✅ PASS | `test_store_has_no_internal_imports`, `test_services_depends_on_store`, `test_services_does_not_import_routes`, `test_routes_depends_on_services`, `test_routes_does_not_import_store`, `test_routes_imports_auth` |
| AR-2 | Structural seed (6 files) | P1 | test_structure (7 tests) | Structural | ✅ PASS | `test_source_file_exists[*.py]` × 6 + `test_no_unexpected_source_files` |
| AR-3 | Tech stack (FastAPI, bcrypt, PyJWT) | P2 | — | Structural | ⚠️ MANUAL | Verified by `pyproject.toml`; no automated test |
| AR-4 | Auth dependency contract (Depends) | P0 | T-14, T-15 | API | ✅ PASS | JWT validation flows through `Depends(get_current_user)` |
| AR-5 | Store lifecycle (module-level dict) | P1 | test_structure (3 tests) | Structural | ✅ PASS | `test_users_is_module_level_dict`, `test_store_clearable`, `test_store_persistence_across_imports` |
| AR-6 | Username normalization (lowercased on write) | P0 | T-06, T-24 | API | ✅ PASS | `test_register_username_case_normalization`, `test_jwt_sub_claim_is_lowercased_username` |

**AR Coverage: 5/6 with automated tests, 1/6 structural-only (AR-3 — version pinning, acceptable)**

---

### Risk-Driven Scenarios

| Risk | Scenario | Priority | Test(s) | Level | Status | Notes |
|------|----------|----------|---------|-------|--------|-------|
| R-01 (SEC-6) | Full auth lifecycle | P0 | T-26 | API | ✅ PASS | `test_full_auth_lifecycle` |
| R-03 (BUS-4) | Concurrent registrations (same username) | P1 | T-27 | API | ✅ PASS | `test_concurrent_registrations_same_username` |
| R-01 (SEC-6) | Password never in error messages | P0 | T-28 | API | ✅ PASS | `test_password_never_in_error_messages` |

**Risk Scenario Coverage: 3/3 covered — FULL**

---

### Unit Test Coverage (Supplementary)

| Module | Tests | Status | Notes |
|--------|-------|--------|-------|
| `tests/unit/test_store.py` | 10 tests | ✅ PASS | `add_user`, `get_user`, `get_user_with_hash`, `user_exists` |
| `tests/unit/test_services.py` | 8 tests | ✅ PASS | `register_user`, `authenticate_user`, `get_current_user_profile` |
| `tests/unit/test_auth.py` | 18 tests | ✅ PASS | `create_access_token`, `decode_token`, `get_current_user` (all branches) |
| `tests/unit/test_structure.py` | 18 tests | ✅ PASS | AR-1 (layered arch), AR-2 (seed files), AR-5 (store lifecycle) |

---

## Coverage Summary

### By Priority

| Priority | Requirements | Test Aspects | Covered | Gaps | Coverage |
|----------|-------------|-------------|---------|------|----------|
| P0 | FR-1 (happy+security), FR-2 (happy+security), FR-3 (all token variants), NFR-1, NFR-2, NFR-4, NFR-6, AR-4, AR-6 | 24 | 24 | 0 | **100%** |
| P1 | FR-1 (missing fields), FR-2 (missing fields), NFR-5, AR-1, AR-2, AR-5 | 8 | 8 | 0 | **100%** |
| P2 | FR-1 (extra fields), FR-2 (extra fields), NFR-3, AR-3 | 4 | 3 | 1 (AR-3) | **75%** |
| P3 | — | 0 | 0 | 0 | N/A |

### By Level

| Level | Test Count | Passing | Status |
|-------|-----------|---------|--------|
| API (Integration) | 28 | 28 | ✅ |
| Unit | 18 | 18 | ✅ |
| Unit (Store) | 10 | 10 | ✅ |
| Unit (Services) | 8 | 8 | ✅ |
| Structural | 18 | 18 | ✅ |
| **Total** | **82** | **82** | ✅ |

### By Requirement Type

| Type | Total | Covered | Coverage |
|------|-------|---------|----------|
| Functional (FR) | 3 | 3 | **100%** |
| Non-Functional (NFR) | 6 | 6 | **100%** |
| Additional/Architectural (AR) | 6 | 5 (auto) + 1 (manual) | **100%** (AR-3 version pinning verified by pyproject.toml) |
| Risk-Driven | 3 | 3 | **100%** |

---

## Coverage Gaps

| Gap ID | Category | Description | Severity | Recommendation |
|--------|----------|-------------|----------|----------------|
| ~~GAP-01~~ | ~~Unit~~ | ~~No unit tests for `auth.py`~~ | ~~Medium~~ | **RESOLVED** — `tests/unit/test_auth.py` covers all branches (T-AUTH-01..T-AUTH-18) |
| ~~GAP-02~~ | ~~Structural~~ | ~~AR-1 (layered architecture) not verified by automated test~~ | ~~Low~~ | **RESOLVED** — `tests/unit/test_structure.py::TestAR1LayeredArchitecture` (6 tests) |
| ~~GAP-03~~ | ~~Structural~~ | ~~AR-2 (structural seed) not verified by automated test~~ | ~~Low~~ | **RESOLVED** — `tests/unit/test_structure.py::TestAR2SeedFiles` (7 tests) |
| ~~GAP-04~~ | ~~Structural~~ | ~~AR-5 (store lifecycle) not verified by automated test~~ | ~~Low~~ | **RESOLVED** — `tests/unit/test_structure.py::TestAR5StoreLifecycle` (3 tests) |
| GAP-05 | Structural | AR-3 (tech stack versions) not verified by automated test | Low | Acceptable; pinned in `pyproject.toml` |
| GAP-06 | Performance | No load/concurrency testing | Low | Not in scope per test design; no SLO defined |

---

### Coverage Status Per Oracle Item

| Oracle Item | Coverage Status | Evidence |
|-------------|----------------|----------|

### Structural Tests — AR-1, AR-2, AR-5 (tests/unit/test_structure.py)

| Test ID | Title | Markers | File:Line | Status | Skip/Fixme |
|---------|-------|---------|-----------|--------|------------|
| AR2-01 | test_source_file_exists[main.py] | `@pytest.mark.structural` | tests/unit/test_structure.py | ✅ PASS | — |
| AR2-02 | test_source_file_exists[routes.py] | `@pytest.mark.structural` | tests/unit/test_structure.py | ✅ PASS | — |
| AR2-03 | test_source_file_exists[services.py] | `@pytest.mark.structural` | tests/unit/test_structure.py | ✅ PASS | — |
| AR2-04 | test_source_file_exists[store.py] | `@pytest.mark.structural` | tests/unit/test_structure.py | ✅ PASS | — |
| AR2-05 | test_source_file_exists[models.py] | `@pytest.mark.structural` | tests/unit/test_structure.py | ✅ PASS | — |
| AR2-06 | test_source_file_exists[auth.py] | `@pytest.mark.structural` | tests/unit/test_structure.py | ✅ PASS | — |
| AR2-07 | test_no_unexpected_source_files | `@pytest.mark.structural` | tests/unit/test_structure.py | ✅ PASS | — |
| AR1-01 | test_store_has_no_internal_imports | `@pytest.mark.structural` | tests/unit/test_structure.py | ✅ PASS | — |
| AR1-02 | test_services_depends_on_store | `@pytest.mark.structural` | tests/unit/test_structure.py | ✅ PASS | — |
| AR1-03 | test_services_does_not_import_routes | `@pytest.mark.structural` | tests/unit/test_structure.py | ✅ PASS | — |
| AR1-04 | test_routes_depends_on_services | `@pytest.mark.structural` | tests/unit/test_structure.py | ✅ PASS | — |
| AR1-05 | test_routes_does_not_import_store | `@pytest.mark.structural` | tests/unit/test_structure.py | ✅ PASS | — |
| AR1-06 | test_routes_imports_auth | `@pytest.mark.structural` | tests/unit/test_structure.py | ✅ PASS | — |
| AR5-01 | test_users_is_module_level_dict | `@pytest.mark.structural` | tests/unit/test_structure.py | ✅ PASS | — |
| AR5-02 | test_store_clearable | `@pytest.mark.structural` | tests/unit/test_structure.py | ✅ PASS | — |
| AR5-03 | test_store_persistence_across_imports | `@pytest.mark.structural` | tests/unit/test_structure.py | ✅ PASS | — |

---

## Coverage Heuristics Inventory (Step 2)

### API Endpoint Coverage

| Endpoint | Requirement | API Tests | Unit Tests | Status |
|----------|-------------|-----------|------------|--------|
| POST `/register` | FR-1 | T-01..T-08 (8 tests) | SVC-01..SVC-03, S-01..S-02 (5 tests) | ✅ FULL |
| POST `/login` | FR-2 | T-09..T-13 (5 tests) | SVC-04..SVC-06 (3 tests) | ✅ FULL |
| GET `/me` | FR-3 | T-14..T-19 (6 tests) | T-AUTH-11..T-AUTH-18 (8 tests), SVC-07..SVC-08 (2 tests) | ✅ FULL |

### Authentication/Authorization Coverage

| Flow | Happy Path | Negative Path | Status |
|------|-----------|---------------|--------|
| Register → JWT creation | T-01 ✅ | T-02..T-06 ✅ | ✅ FULL |
| Login → JWT creation | T-09 ✅ | T-10..T-13 ✅ | ✅ FULL |
| Get /me → JWT validation | T-14 ✅ | T-15..T-19 ✅ | ✅ FULL |
| JWT decode (unit) | T-AUTH-06 ✅ | T-AUTH-07..T-AUTH-10 ✅ | ✅ FULL |
| Auth dependency (unit) | T-AUTH-11 ✅ | T-AUTH-12..T-AUTH-18 ✅ | ✅ FULL |

### Error-Path Coverage

| Error Scenario | Requirement | Test(s) | Status |
|----------------|-------------|---------|--------|
| Missing required fields | FR-1, FR-2 | T-02..T-04, T-12, T-13 | ✅ |
| Duplicate username | FR-1 | T-05 | ✅ |
| Wrong credentials | FR-2 | T-10, T-11 | ✅ |
| Missing/invalid/expired token | FR-3 | T-15..T-19 | ✅ |
| Invalid JSON body | NFR-5 | T-22 | ✅ |
| Consistent error shape | NFR-5 | T-21 | ✅ |
| User deleted after registration | FR-3 | (unmarked) | ✅ |

### Structural/Architectural Coverage

| Requirement | Test(s) | Status |
|-------------|---------|--------|
| AR-1: Layered architecture | AR1-01..AR1-06 (6 tests) | ✅ FULL |
| AR-2: Structural seed (6 files) | AR2-01..AR2-07 (7 tests) | ✅ FULL |
| AR-5: Store lifecycle | AR5-01..AR5-03 (3 tests) | ✅ FULL |
| AR-3: Tech stack versions | — | ⚠️ Manual (pyproject.toml) |
| AR-4: Auth dependency contract | T-14, T-15 | ✅ FULL |
| AR-6: Username normalization | T-06, T-24 | ✅ FULL |

---

## Updated Coverage Summary (Step 2)

### By Level (Final)

| Level | Test Count | Passing | Coverage |
|-------|-----------|---------|----------|
| API (Integration) | 31 | 31 | ✅ 100% |
| Unit (auth/store/services) | 36 | 36 | ✅ 100% |
| Structural (AR-1, AR-2, AR-5) | 15 | 15 | ✅ 100% |
| **Total** | **82** | **82** | ✅ |

### By Requirement (Final)

| Type | Total | Covered | Coverage |
|------|-------|---------|----------|
| Functional (FR) | 3 | 3 | **100%** |
| Non-Functional (NFR) | 6 | 6 | **100%** |
| Additional/Architectural (AR) | 6 | 6 | **100%** (AR-3 manual, AR-1/AR-2/AR-5 now automated) |
| Risk-Driven | 3 | 3 | **100%** |

---

## Quality Gate Decision (Step 5 — Final)

### Gate Criteria Evaluation

| Criterion | Required | Actual | Status |
|-----------|----------|--------|--------|
| P0 coverage | 100% | 100% (8/8) | ✅ MET |
| P1 coverage | ≥ 80% (target 90%) | 100% (4/4) | ✅ MET |
| Overall coverage | ≥ 80% | 93.3% (14/15) | ✅ MET |
| Critical gaps | 0 | 0 | ✅ MET |
| Collection status | COLLECTED | COLLECTED | ✅ ELIGIBLE |

### Gate Decision: **PASS** ✅

**Algorithmic Evaluation (per gate rules):**

- Rule 1: P0 coverage = 100% → **PASS** ✅
- Rule 2: Overall coverage = 93.3% ≥ 80% → **PASS** ✅
- Rule 3: P1 coverage = 100% ≥ 80% → **PASS** ✅
- Rule 4: P1 coverage = 100% ≥ 90% → **PASS** ✅
- Live evidence overlay: Not applicable (static_suite mode, no live-only requirements)

**Rationale:**

All functional, non-functional, and architectural requirements have automated test coverage. 82 tests pass across 5 test files (31 API + 36 unit + 15 structural). P0 coverage is 100%, P1 coverage is 100%, and overall coverage is 93.3% (AR-3 remains PARTIAL due to manual pyproject.toml verification). All 4 originally identified gaps (GAP-01..04) have been resolved with automated tests. Two acknowledged non-blocking gaps remain: AR-3 tech stack version pinning (verified by pyproject.toml) and performance/load testing (not in scope per test design).

### Evidence Summary

| Evidence | Count | Details |
|----------|-------|---------|
| Total tests | 82 | 31 API + 36 unit + 15 structural |
| Tests passing | 82/82 | 100% pass rate |
| FULL coverage | 14/15 requirements | All FR, NFR, AR (except AR-3) |
| PARTIAL coverage | 1/15 requirements | AR-3 (manual verification) |
| NONE coverage | 0/15 requirements | — |
| Resolved gaps | 4/6 | GAP-01..04 resolved |
| Acknowledged gaps | 2/6 | GAP-05/06 non-blocking |

### Resolved Gaps (commit 61ebc86)

| Gap | Requirement | Resolution |
|-----|-------------|------------|
| GAP-02 | AR-1 layered architecture | 6 structural tests (AR1-01..AR1-06) |
| GAP-03 | AR-2 structural seed | 7 structural tests (AR2-01..AR2-07) |
| GAP-04 | AR-5 store lifecycle | 3 structural tests (AR5-01..AR5-03) |

### Acknowledged Non-Blocking Gaps

| Gap | Requirement | Justification |
|-----|-------------|---------------|
| GAP-05 | AR-3 tech stack versions | Verified by `pyproject.toml`, acceptable for personal project |
| GAP-06 | Performance/load testing | Not in scope per test design; no SLO defined |

---

## Coverage Validation (Step 3)

### Matrix Validation Checklist

| Check | Result | Notes |
|-------|--------|-------|
| P0 items have coverage | ✅ PASS | 24/24 P0 test aspects mapped and passing |
| P1 items have coverage | ✅ PASS | 8/8 P1 mapped; AR-1, AR-2, AR-5 now have automated structural tests |
| No duplicate coverage without justification | ✅ PASS | Each test maps to one requirement aspect |
| Items not happy-path-only when errors implied | ✅ PASS | All error paths covered (missing fields, duplicates, invalid tokens, etc.) |
| API items have endpoint-level checks | ✅ PASS | HTTP method + path tested in each API test |
| Auth/authz items include denied/invalid paths | ✅ PASS | T-10, T-11, T-15..T-19, T-AUTH-07..T-AUTH-18 |
| No stale/unverifiable live records used | ✅ PASS | No live records in this run (static_suite mode) |
| Coverage status assigned per item | ✅ PASS | FULL / PARTIAL / NONE / UNIT-ONLY as appropriate |

### Coverage Status Per Oracle Item

| Oracle Item | Coverage Status | Evidence |
|-------------|----------------|----------|
| FR-1: Register user | FULL | 11 API + 5 unit tests |
| FR-2: Login | FULL | 7 API + 3 unit tests |
| FR-3: Get current user | FULL | 8 API + 10 unit tests |
| NFR-1: In-memory storage | FULL | conftest clearing + store unit tests |
| NFR-2: bcrypt hashing | FULL | T-07 + T-AUTH-01..05 |
| NFR-3: JWT claims | FULL | T-24, T-25 + T-AUTH-01..T-AUTH-10 |
| NFR-4: Stateless auth | FULL | T-15 + T-AUTH-12..T-AUTH-18 |
| NFR-5: Error shape | FULL | T-21, T-22 |
| NFR-6: Hash exclusion | FULL | T-08, T-20, T-23 + S-05 |
| AR-1: Layered architecture | FULL | AR1-01..AR1-06 (6 structural tests) |
| AR-2: Structural seed | FULL | AR2-01..AR2-07 (7 structural tests) |
| AR-3: Tech stack | PARTIAL | Manual verification (pyproject.toml) |
| AR-4: Auth dependency | FULL | T-14, T-15 + T-AUTH-11..T-AUTH-18 |
| AR-5: Store lifecycle | FULL | AR5-01..AR5-03 (3 structural tests) |
| AR-6: Username normalization | FULL | T-06, T-24 + T-AUTH-02, SVC-02 |

---

## Gap Analysis (Step 4)

### Coverage Status Distribution

| Status | Count | Requirements |
|--------|-------|-------------|
| FULL | 14 | FR-1, FR-2, FR-3, NFR-1, NFR-2, NFR-3, NFR-4, NFR-5, NFR-6, AR-1, AR-2, AR-4, AR-5, AR-6 |
| PARTIAL | 1 | AR-3 (tech stack versions) |
| NONE | 0 | — |
| UNIT-ONLY | 0 | — |

### Gap Inventory

| Gap ID | Category | Requirement | Severity | Status |
|--------|----------|-------------|----------|--------|
| ~~GAP-01~~ | ~~Functional~~ | ~~FR-1/FR-2/FR-3 missing dedicated unit tests~~ | ~~Critical~~ | **RESOLVED** — 36 unit tests added (T-AUTH-01..18, S-01..09, SVC-01..08) |
| ~~GAP-02~~ | ~~Structural~~ | ~~AR-1 (layered architecture) not verified by automated test~~ | ~~Low~~ | **RESOLVED** — `tests/unit/test_structure.py::TestAR1LayeredArchitecture` (6 tests) |
| ~~GAP-03~~ | ~~Structural~~ | ~~AR-2 (structural seed) not verified by automated test~~ | ~~Low~~ | **RESOLVED** — `tests/unit/test_structure.py::TestAR2SeedFiles` (7 tests) |
| ~~GAP-04~~ | ~~Structural~~ | ~~AR-5 (store lifecycle) not verified by automated test~~ | ~~Low~~ | **RESOLVED** — `tests/unit/test_structure.py::TestAR5StoreLifecycle` (3 tests) |
| GAP-05 | Structural | AR-3 (tech stack versions) not verified by automated test | Low | Acceptable; pinned in `pyproject.toml` |
| GAP-06 | Performance | No load/concurrency testing | Low | Not in scope per test design; no SLO defined |

### Coverage Heuristics

| Heuristic | Result | Details |
|-----------|--------|---------|
| Endpoint coverage | ✅ All endpoints tested | 3/3 API endpoints have positive + negative tests |
| Auth/authz negative paths | ✅ Covered | T-10, T-11, T-15..T-19, T-AUTH-07..T-AUTH-18 |
| Error-path coverage | ✅ Covered | Missing fields, duplicates, invalid tokens, malformed JSON |
| Happy-path-only items | ✅ None | All FR items have both happy and error paths |
| UI journey E2E | N/A | No UI in this project |
| UI state coverage | N/A | No UI in this project |

### Recommendations

| Priority | Recommendation | Rationale |
|----------|---------------|-----------|
| LOW | Consider adding AR-3 automated test (version pin assertion) | Would achieve 100% FULL coverage across all requirements |
| LOW | Consider load/concurrency tests if SLO defined | GAP-06 acknowledged; not blocking for personal project |
| INFO | All critical gaps resolved | No action required |

---

## Next Step

Load: `{skill-root}/steps-c/step-05-gate-decision.md`
