---
title: 'Story 1.1 — Project Scaffolding & Data Layer'
type: 'feature'
created: '2026-09-07'
status: 'ready-for-dev'
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
