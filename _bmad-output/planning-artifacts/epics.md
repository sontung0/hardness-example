---
stepsCompleted: ["step-01-validate-prerequisites", "step-02-design-epics", "step-03-create-stories"]
inputDocuments:
  - prds/prd-bmad-2026-09-06/prd.md
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

### NonFunctional Requirements

- **NFR-1:** In-memory storage only — one Python dict keyed by username. No database, no file I/O. Data lost on restart by design.
- **NFR-2:** Password hashing with bcrypt (default work factor). Hash stored as Python str (decode utf-8 before insertion). Store layer never sees or transforms plaintext.
- **NFR-3:** JWT signing and validation — `sub` claim = lowercased username, `exp` = 24h from issuance. Secret managed as constant in auth.py.
- **NFR-4:** Stateless auth — no session cookies, no server-side session store. JWT is sole authentication mechanism. No refresh tokens.
- **NFR-5:** Consistent error shape — all errors return `{"detail": str}`. Status codes: 400 bad input, 401 unauthenticated, 409 conflict. Custom handler overrides FastAPI's default 422.
- **NFR-6:** Password hash exclusion boundary — `password_hash` never exposed in any response or store return value. Store returns only username + name.

### Additional Requirements

- **AR-1:** Layered architecture — Routes → Services → Store, each layer calls only the one below. No skipping layers.
- **AR-2:** Structural seed — six files: `main.py` (app factory), `routes.py` (endpoints), `services.py` (business logic), `store.py` (in-memory dict), `models.py` (Pydantic models), `auth.py` (JWT + Depends).
- **AR-3:** Tech stack — Python ≥ 3.10, FastAPI 0.141.1, Uvicorn 0.52.4, bcrypt 5.0.0, PyJWT 2.13.0, Pydantic (via FastAPI).
- **AR-4:** Auth dependency contract — `auth.py` is sole JWT decoder. Exposes FastAPI `Depends` returning `username: str` to route handlers. Services receive only username, never raw tokens.
- **AR-5:** Store lifecycle — module-level dict in `store.py`. Services import directly. No dependency injection of the store.
- **AR-6:** Username normalization — always lowercased on write; all lookups use lowercased form.

### UX Design Requirements

N/A — No UX design document exists for this project.

### FR Coverage Map

| Requirement | Epic | Story |
|-------------|------|-------|
| FR-1 | Epic 1 | Story 1.2 — User registration |
| FR-2 | Epic 1 | Story 1.3 — User login |
| FR-3 | Epic 1 | Story 1.4 — Get current user |
| NFR-1 | Epic 1 | Story 1.1 — Project scaffolding & data layer |
| NFR-2 | Epic 1 | Stories 1.2, 1.3 — bcrypt hashing |
| NFR-3 | Epic 1 | Story 1.4 — JWT validation |
| NFR-4 | Epic 1 | Story 1.4 — Stateless auth |
| NFR-5 | Epic 1 | Story 1.4 — Consistent error shape |
| NFR-6 | Epic 1 | Story 1.2 — Password hash exclusion |
| AR-1 | Epic 1 | Story 1.1 — Layered architecture |
| AR-2 | Epic 1 | Story 1.1 — Structural seed |
| AR-3 | Epic 1 | Story 1.1 — Tech stack setup |
| AR-4 | Epic 1 | Story 1.4 — Auth dependency contract |
| AR-5 | Epic 1 | Story 1.1 — Store lifecycle |
| AR-6 | Epic 1 | Story 1.1 — Username normalization |

## Epic List

### Epic 1: User Authentication API

Users can register an account, log in, and retrieve their own profile — a complete, stateless auth system with JWT.

**Story 1.1: Project scaffolding & data layer**
Sets up the project structure, in-memory store, Pydantic models, and app factory. Establishes the layered architecture (Routes → Services → Store), tech stack (FastAPI, bcrypt, PyJWT), and all foundational patterns.

**Story 1.2: User registration**
Implements POST `/register` — accepts username, password, and name, validates input, hashes the password with bcrypt, stores the user, and returns a JWT. Handles duplicate username (409) and missing fields (400).

**Story 1.3: User login**
Implements POST `/login` — accepts username and password, validates credentials against the in-memory store, and returns a JWT. Handles wrong credentials (401) and missing fields (400).

**Story 1.4: Get current user**
Implements GET `/me` — extracts username from JWT via auth dependency, returns the user's profile (username and name, never password). Handles missing/invalid/expired tokens (401). Establishes consistent error shape (`{"detail": str}`) across all endpoints.

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
