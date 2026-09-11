# Epic 1 Context: User Authentication API

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Deliver a complete, stateless user authentication system with three endpoints — register, login, and get current user — using FastAPI, JWT tokens, bcrypt password hashing, and in-memory storage. This is the project's foundation: a working auth API that can be stood up and tested with curl.

## Stories

- Story 1.1: Project scaffolding & data layer
- Story 1.2: User registration
- Story 1.3: User login
- Story 1.4: Get current user

## Requirements & Constraints

- **FR-1:** POST `/register` — validate input, hash password, store user, return JWT. 201 success, 409 duplicate, 400 missing fields.
- **FR-2:** POST `/login` — validate credentials, return JWT. 200 success, 401 wrong credentials, 400 missing fields.
- **FR-3:** GET `/me` — extract username from JWT, return profile (username + name). 200 success, 401 missing/invalid/expired token.
- **NFR-1:** In-memory dict only. No database, no file I/O. Data lost on restart.
- **NFR-2:** bcrypt hashing (default work factor). Hash stored as Python str (decode utf-8). Store never sees plaintext.
- **NFR-3:** JWT `sub` = lowercased username, `exp` = 24h. Secret as constant in auth.py.
- **NFR-4:** Stateless auth — no session cookies, no refresh tokens.
- **NFR-5:** Consistent error shape: `{"detail": str}`. Custom handler overrides FastAPI's 422.
- **NFR-6:** `password_hash` never exposed in any response or store return value.

## Technical Decisions

- **Layered architecture:** Routes → Services → Store. Each layer calls only the one below. No skipping layers.
- **Structural seed:** Six files — `main.py` (app factory), `routes.py` (endpoints), `services.py` (business logic), `store.py` (in-memory dict), `models.py` (Pydantic models), `auth.py` (JWT + Depends).
- **Store lifecycle:** Module-level dict in `store.py`. Services import directly. No dependency injection.
- **Auth dependency contract:** `auth.py` is sole JWT decoder. Exposes FastAPI `Depends` returning `username: str`. Services receive only username, never raw tokens.
- **Password hash exclusion boundary:** `store.py` never exposes `password_hash` in any return value.
- **Username normalization:** Always lowercased on write; all lookups use lowercased form.
- **Tech stack:** Python ≥ 3.10, FastAPI 0.141.1, Uvicorn 0.52.4, bcrypt 5.0.0, PyJWT 2.13.0, Pydantic (via FastAPI).

## Cross-Story Dependencies

Stories build sequentially: 1.1 scaffolds the structure, 1.2 adds registration, 1.3 adds login, 1.4 completes the auth flow with profile retrieval.
