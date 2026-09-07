---
title: 'Story 1.1 — Project Scaffolding & Data Layer'
type: 'feature'
created: '2026-09-07'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The project scaffolding and data layer for the User Authentication API need to be verified as correctly implemented. The codebase already contains all 6 source files (main.py, routes.py, services.py, store.py, models.py, auth.py) with working business logic, bcrypt hashing, JWT auth, and in-memory storage.

**Approach:** Validate the existing implementation against the architecture and requirements. Address two minor gaps: (1) move the hardcoded JWT secret key to an environment variable with fallback, and (2) add a uvicorn entrypoint. Confirm layered architecture (Routes → Services → Store) holds and the in-memory store behaves correctly.

</frozen-after-approval>

## Implementation Notes

The codebase investigation revealed a fully implemented project:

**Source files (all complete):**
- `src/main.py` — App factory with FastAPI, custom 422→400 handler, router inclusion
- `src/routes.py` — Three endpoints: POST /register, POST /login, GET /me
- `src/services.py` — Business logic: register_user, authenticate_user, get_current_user_profile with bcrypt
- `src/store.py` — In-memory dict: add_user, get_user, get_user_with_hash, user_exists. Module-level dict, services import directly
- `src/models.py` — 5 Pydantic models: RegisterRequest, LoginRequest, TokenResponse, UserResponse, ErrorResponse
- `src/auth.py` — JWT create/decode, get_current_user FastAPI dependency. SECRET_KEY hardcoded, ALGORITHM=HS256, TOKEN_EXPIRY_HOURS=24

**Tests (comprehensive):**
- `tests/test_auth.py` — 28+ acceptance tests (T-01 to T-28) covering FR-1, FR-2, FR-3
- `tests/unit/test_store.py` — 8 tests for all 4 store functions
- `tests/unit/test_services.py` — 8 tests for all 3 service functions
- `tests/unit/test_auth.py` — ~18 tests for JWT and auth dependency
- `tests/conftest.py` — 4 fixtures (_clear_store autouse, client, registered_user, auth_header)

**Minor gaps to address:**
1. `auth.py` — `SECRET_KEY = "super-secret-key-do-not-commit"` should read from env with fallback
2. `pyproject.toml` — No `[project.scripts]` entry or `__main__` block for uvicorn
3. `models.py` — `ErrorResponse` model defined but unused by any route/handler (low priority)

### Review Findings

**Code review completed:** 2026-09-07. Source-only diff (6 files, 243 lines). Review layers: Blind Hunter, Edge Case Hunter, Verification Gap Reviewer, Acceptance Auditor.

#### Deferred

- [x] [Review][Defer] `get_user_with_hash` leaks password_hash internally [src/store.py:17] — deferred: internal-use-only function, properly scoped to services.py. AD-6 wording too broad.
- [x] [Review][Defer] Synchronous bcrypt blocks event loop [src/services.py] — deferred: acceptable for demo app; all routes and services synchronous by design.
- [x] [Review][Defer] Missing `sub`-claim-absent unit test [tests/unit/test_auth.py] — deferred: pre-existing test gap, not introduced by this diff. Guard in auth.py:32-33 is correct.

#### Rejected

- false — JWT login case mismatch: `create_access_token` lowercases internally (auth.py:14); `authenticate_user` lowercases for store lookup (services.py:15). No functional bug.
- false — JWT secret hardcoded fallback: `os.environ.get` with `or` handles empty strings; spec Implementation Notes mandate this behavior.
- false — Empty username accepted: `Field(...)` has implicit `min_length=1`; Pydantic rejects empty strings with 400.
- false — Store dict not thread-safe: CPython GIL + single-threaded uvicorn asyncio = no interleaving. Not a real issue.
- false — user_exists + add_user non-atomic: same reasoning — single-threaded event loop, no interleaving.
- false — main.py module-level app: standard FastAPI pattern (`uvicorn main:app`).
- false — Validation handler first error only: explicit design choice for readable 400 responses.
- low — Rate limiting missing: design choice for demo app, not a defect.
- low — token_type in response body: design choice, not a defect.
