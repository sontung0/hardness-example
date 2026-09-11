---
stepsCompleted: ["step-01-validate-prerequisites", "step-02-design-epics", "step-03-create-stories"]
inputDocuments:
  - prds/prd-bmad-2026-09-06/prd.md
  - prds/prd-bmad-2026-09-11/prd.md
  - architecture/architecture-bmad-2026-09-06/ARCHITECTURE-SPINE.md
---

# bmad - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for bmad, decomposing the requirements from the PRD and Architecture into implementable stories.

## Requirements Inventory

### Functional Requirements

- **FR-1:** Register a new user — POST `/register` with username, password, and name. Validate input, hash password, store user, return JWT. Returns HTTP 201 on success, 409 on duplicate username, 400 on missing fields. Password is never stored as plaintext.
- **FR-2:** Login with valid credentials — POST `/login` with username and password. Validate against in-memory store, return JWT. Returns HTTP 200 on success, 401 on wrong credentials, 400 on missing fields.
- **FR-3:** Retrieve current user profile — GET `/me` with valid JWT in Authorization header. Return username and name (never password). Returns HTTP 200 on success, 401 for missing, expired, or invalid token.
- **FR-4:** Change password with valid current password — POST `/change-password` with valid JWT, current password, and new password. Validate current password, hash and store new password, return HTTP 200. Existing JWT remains valid after change.
- **FR-5:** Reject change with wrong current password — POST `/change-password` with valid JWT but wrong current password → HTTP 401 Unauthorized. Response does not reveal which field was wrong.
- **FR-6:** Reject change with weak new password — New password shorter than 8 characters → HTTP 400 Bad Request with message indicating minimum length.
- **FR-7:** Reject change without authentication — POST `/change-password` without valid JWT → HTTP 401 Unauthorized.

### NonFunctional Requirements

- **NFR-1:** In-memory storage only — one Python dict keyed by username. No database, no file I/O. Data lost on restart by design.
- **NFR-2:** Password hashing with bcrypt (default work factor). Hash stored as Python str (decode utf-8 before insertion). Store layer never sees or transforms plaintext.
- **NFR-3:** JWT signing and validation — `sub` claim = lowercased username, `exp` = 24h from issuance. Secret managed as constant in auth.py.
- **NFR-4:** Stateless auth — no session cookies, no server-side session store. JWT is sole authentication mechanism. No refresh tokens.
- **NFR-5:** Consistent error shape — all errors return `{"detail": str}`. Status codes: 400 bad input, 401 unauthenticated, 409 conflict. Custom handler overrides FastAPI's default 422.
- **NFR-6:** Password hash exclusion boundary — `password_hash` never exposed in any response or store return value. Store returns only username + name.
- **NFR-7:** Password change gate — Current password must be verified against stored hash before accepting new one. New password minimum 8 characters; no complexity rules. Existing JWT remains valid after change.
- **NFR-8:** Password change error semantics — Wrong current password returns HTTP 401 with same generic `{"detail": "Invalid credentials"}` message used by login. New password too short returns HTTP 400 with `{"detail": "Password must be at least 8 characters"}`.
- **NFR-9:** Store mutation for password change — `store.py` exposes `update_password(username, new_hash)` — a dumb writer that overwrites the `password_hash` field. All bcrypt work stays in `services.py`.

### Additional Requirements

- **AR-1:** Layered architecture — Routes → Services → Store, each layer calls only the one below. No skipping layers.
- **AR-2:** Structural seed — six files: `main.py` (app factory), `routes.py` (endpoints), `services.py` (business logic), `store.py` (in-memory dict), `models.py` (Pydantic models), `auth.py` (JWT + Depends).
- **AR-3:** Tech stack — Python ≥ 3.10, FastAPI 0.141.1, Uvicorn 0.52.4, bcrypt 5.0.0, PyJWT 2.13.0, Pydantic (via FastAPI).
- **AR-4:** Auth dependency contract — `auth.py` is sole JWT decoder. Exposes FastAPI `Depends` returning `username: str` to route handlers. Services receive only username, never raw tokens.
- **AR-5:** Store lifecycle — module-level dict in `store.py`. Services import directly. No dependency injection of the store.
- **AR-6:** Username normalization — always lowercased on write; all lookups use lowercased form.
- **AR-7:** Change password request/response — Request: `{"current_password": str, "new_password": str}`. Response: `{"message": "Password changed successfully"}`.

### UX Design Requirements

N/A — No UX design document exists for this project.

### FR Coverage Map

| Requirement | Epic | Story |
|-------------|------|-------|
| FR-1 | Epic 1 | Story 1.2 — User registration |
| FR-2 | Epic 1 | Story 1.3 — User login |
| FR-3 | Epic 1 | Story 1.4 — Get current user |
| FR-4 | Epic 2 | Story 2.1 — Change password |
| FR-5 | Epic 2 | Story 2.1 — Change password |
| FR-6 | Epic 2 | Story 2.1 — Change password |
| FR-7 | Epic 2 | Story 2.1 — Change password |
| NFR-1 | Epic 1 | Story 1.1 — Project scaffolding & data layer |
| NFR-2 | Epic 1 | Stories 1.2, 1.3 — bcrypt hashing |
| NFR-3 | Epic 1 | Story 1.4 — JWT validation |
| NFR-4 | Epic 1 | Story 1.4 — Stateless auth |
| NFR-5 | Epic 1 | Story 1.4 — Consistent error shape |
| NFR-6 | Epic 1 | Story 1.2 — Password hash exclusion |
| NFR-7 | Epic 2 | Story 2.1 — Password change gate |
| NFR-8 | Epic 2 | Story 2.1 — Password change error semantics |
| NFR-9 | Epic 2 | Story 2.1 — Store mutation for password change |
| AR-1 | Epic 1 | Story 1.1 — Layered architecture |
| AR-2 | Epic 1 | Story 1.1 — Structural seed |
| AR-3 | Epic 1 | Story 1.1 — Tech stack setup |
| AR-4 | Epic 1 | Story 1.4 — Auth dependency contract |
| AR-5 | Epic 1 | Story 1.1 — Store lifecycle |
| AR-6 | Epic 1 | Story 1.1 — Username normalization |
| AR-7 | Epic 2 | Story 2.1 — Change password request/response |

## Epic List

### Epic 1: User Authentication API

Users can register an account, log in, and retrieve their own profile — a complete, stateless auth system with JWT.

**FRs covered:** FR-1, FR-2, FR-3
**NFRs covered:** NFR-1, NFR-2, NFR-3, NFR-4, NFR-5, NFR-6
**ARs covered:** AR-1, AR-2, AR-3, AR-4, AR-5, AR-6

### Epic 2: Password Management

Users can change their password after authentication — validating current credentials and enforcing minimum password requirements.

**FRs covered:** FR-4, FR-5, FR-6, FR-7
**NFRs covered:** NFR-7, NFR-8, NFR-9
**ARs covered:** AR-7

## Epic 1: User Authentication API

Users can register an account, log in, and retrieve their own profile — a complete, stateless auth system with JWT.

### Story 1.1: Project scaffolding & data layer

As a developer,
I want the project structure, data layer, and app factory set up with the layered architecture,
So that all subsequent stories can build on a solid foundation.

**Acceptance Criteria:**

**Given** the project root is empty (or has only planning docs)
**When** the developer runs the scaffolding story
**Then** the following files exist under `src/`: `main.py`, `routes.py`, `services.py`, `store.py`, `models.py`, `auth.py`
**And** `main.py` creates a FastAPI app and includes the router from `routes.py`
**And** `store.py` exposes a module-level dict keyed by username and helper functions: `add_user(username, user_dict)`, `get_user(username) -> dict | None`
**And** `models.py` defines Pydantic models: `UserRegister` (username, password, name), `UserLogin` (username, password), `UserResponse` (username, name), `TokenResponse` (access_token, token_type)
**And** `auth.py` defines a JWT secret constant, `create_token(username) -> str`, and a FastAPI `Depends` function `get_current_user(request) -> str` that extracts and validates the username from the Authorization header
**And** `routes.py` defines placeholder route handlers for `POST /register`, `POST /login`, `GET /me` that return appropriate placeholder responses
**And** store helper functions always lowercase the username on write
**And** `add_user` and `get_user` never expose `password_hash` in any return value
**And** the app starts with `uvicorn src.main:app` without errors

### Story 1.2: User registration

As a developer,
I want to register a new user via POST `/register`,
So that new accounts can be created with hashed passwords and a JWT is returned.

**Acceptance Criteria:**

**Given** a request with a unique username, valid password, and name
**When** the client sends `POST /register` with JSON body `{"username": "...", "password": "...", "name": "..."}`
**Then** the response is HTTP 201 with body `{"access_token": "<jwt>", "token_type": "bearer"}`
**And** the stored user has the password hashed with bcrypt (not plaintext)
**And** the JWT contains the lowercased username in the `sub` claim and a 24h expiry

**Given** a request with a username that already exists
**When** the client sends `POST /register` with a duplicate username
**Then** the response is HTTP 409 with body `{"detail": "Username already exists"}`

**Given** a request with missing required fields (username, password, or name)
**When** the client sends `POST /register` with an incomplete body
**Then** the response is HTTP 400 with body `{"detail": "..."}` describing the missing field

### Story 1.3: User login

As a developer,
I want to log in via POST `/login`,
So that existing users can authenticate and receive a JWT.

**Acceptance Criteria:**

**Given** a user has been registered
**When** the client sends `POST /login` with the correct username and password
**Then** the response is HTTP 200 with body `{"access_token": "<jwt>", "token_type": "bearer"}`
**And** the JWT contains the lowercased username in the `sub` claim and a 24h expiry

**Given** a registered user provides wrong credentials (wrong password or non-existent username)
**When** the client sends `POST /login` with incorrect username or password
**Then** the response is HTTP 401 with body `{"detail": "Invalid credentials"}`

**Given** a request with missing required fields (username or password)
**When** the client sends `POST /login` with an incomplete body
**Then** the response is HTTP 400 with body `{"detail": "..."}` describing the missing field

### Story 1.4: Get current user

As a developer,
I want to retrieve my own profile via GET `/me`,
So that I can confirm my identity and access my user info after authentication.

**Acceptance Criteria:**

**Given** a user has registered or logged in and has a valid JWT
**When** the client sends `GET /me` with `Authorization: Bearer <token>`
**Then** the response is HTTP 200 with body `{"username": "...", "name": "..."}`
**And** the password hash is never included in the response

**Given** a request with no Authorization header
**When** the client sends `GET /me` without the header
**Then** the response is HTTP 401 with body `{"detail": "..."}`

**Given** a request with an expired or invalid JWT
**When** the client sends `GET /me` with a bad token
**Then** the response is HTTP 401 with body `{"detail": "..."}`

## Epic 2: Password Management

Users can change their password after authentication — validating current credentials and enforcing minimum password requirements.

### Story 2.1: Change password

As a developer,
I want to change my password via POST `/change-password`,
So that I can update my credentials while maintaining account security.

**Acceptance Criteria:**

**Given** a user has a valid JWT and knows their current password
**When** the client sends `POST /change-password` with `Authorization: Bearer <token>` and body `{"current_password": "...", "new_password": "..."}`
**Then** the response is HTTP 200 with body `{"message": "Password changed successfully"}`
**And** the new password is hashed with bcrypt and stored (replacing the old hash)
**And** the old password can no longer be used to authenticate
**And** the existing JWT remains valid (no token rotation)

**Given** a user provides the wrong current password
**When** the client sends `POST /change-password` with an incorrect current password
**Then** the response is HTTP 401 with body `{"detail": "Invalid credentials"}`
**And** the stored password is NOT changed

**Given** a user provides a new password shorter than 8 characters
**When** the client sends `POST /change-password` with a weak new password
**Then** the response is HTTP 400 with body `{"detail": "Password must be at least 8 characters"}`
**And** the stored password is NOT changed

**Given** a request without a valid JWT
**When** the client sends `POST /change-password` without an Authorization header or with an invalid/expired token
**Then** the response is HTTP 401 with body `{"detail": "..."}`
