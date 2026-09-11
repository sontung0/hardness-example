---
name: 'Simple REST API — Auth'
type: architecture-spine
purpose: build-substrate
altitude: feature
paradigm: 'layered — route → service → store'
scope: 'Register, Login, Get Current User endpoints with JWT auth and in-memory storage'
status: final
created: '2026-09-06'
updated: '2026-09-06'
binds: ['FR-1', 'FR-2', 'FR-3']
sources: ['prd-bmad-2026-09-06']
companions: []
---

# Architecture Spine — Simple REST API Auth

## Design Paradigm

**Layered** — three tiers, each calling only the one below:

```mermaid
graph TD
    Routes["Routes<br/>(FastAPI endpoints)"] --> Services["Services<br/>(business logic)"]
    Services --> Store["Store<br/>(in-memory dict)"]
    Routes -.-> AuthMiddleware["Auth Middleware<br/>(JWT verification)"]
    AuthMiddleware --> Services
```

- **Routes** — HTTP contract: request parsing, response shaping, status codes. No business logic.
- **Services** — auth logic: registration, login, token creation, credential verification. Owns the rules.
- **Store** — thin data-access layer over a Python dict. No logic, no validation.

## Invariants & Rules

### AD-1 — Stateless Auth

- **Binds:** all endpoints, auth middleware
- **Prevents:** server-side session state that couples requests to a process
- **Rule:** All authentication state is carried in the JWT. No session cookies, no server-side session store. The `GET /me` endpoint extracts identity from the token alone.

### AD-2 — Passwords Never in Plaintext

- **Binds:** `POST /register`, `POST /login`, services layer
- **Prevents:** plaintext credential storage, leakage in responses/logs, double-hashing
- **Rule:** Passwords are hashed with bcrypt (default work factor) in `services.py` — exactly one layer. The hash must be a Python `str` (not `bytes`); call `.decode('utf-8')` before insertion. The store layer never sees or transforms plaintext passwords and never re-hashes. No endpoint response ever includes a password field.

### AD-3 — Single In-Memory Store

- **Binds:** all endpoints
- **Prevents:** hidden persistence assumptions, mixed storage backends
- **Rule:** One Python dict keyed by username holds all user data for the process lifetime. No database, no file I/O, no external state. Data is lost on restart — this is intentional.

### AD-4 — JWT as Sole Auth Mechanism

- **Binds:** `GET /me`, auth middleware
- **Prevents:** mixed auth strategies (cookies + tokens + API keys)
- **Rule:** A signed JWT in the `Authorization: Bearer <token>` header is the only way to authenticate. No refresh tokens, no token rotation, no refresh endpoint.

### AD-5 — Consistent Error Shape

- **Binds:** all endpoints
- **Prevents:** ad-hoc error responses across units
- **Rule:** Errors return a JSON body with a `detail` field (always a `str`, never a list). HTTP status codes follow REST convention: `400` for bad input, `401` for unauthenticated, `409` for conflict. Custom error handler overrides FastAPI's default `422` validation errors to use the same `{"detail": str}` shape.

## Consistency Conventions

| Concern | Convention |
| --- | --- |
| Entity naming | `User` model with fields: `username` (str, unique key), `name` (str), `password_hash` (str, never exposed) |
| API responses | Success: JSON with relevant fields. Error: `{"detail": "message"}` |
| JWT claims | `sub` = username (lowercased), `exp` = 24h from issuance |
| HTTP methods | `POST` for create/authenticate, `GET` for read. No `PUT`/`PATCH`/`DELETE` in scope |
| Status codes | `201` on register, `200` on login/me, `400` bad input, `401` unauthenticated, `409` duplicate |
| Username keys | Always lowercased on write; all lookups use lowercased form |
| Register response | `{"access_token": str, "token_type": "bearer"}` |
| Login response | `{"access_token": str, "token_type": "bearer"}` |
| Me response | `{"username": str, "name": str}` |

## Stack

| Name | Version | Role |
| --- | --- | --- |
| Python | ≥ 3.10 | Language runtime |
| FastAPI | 0.141.1 | Web framework |
| Uvicorn | 0.52.4 | ASGI server |
| bcrypt | 5.0.0 | Password hashing |
| PyJWT | 2.13.0 | JWT encode/decode |
| Pydantic | (via FastAPI) | Request/response validation |

## Structural Seed

```text
src/
  main.py          # app factory, route registration, startup
  routes.py         # /register, /login, /me endpoint handlers
  services.py       # register_user, authenticate, get_current_user logic
  store.py          # in-memory user dict + helpers
  models.py         # Pydantic request/response models
  auth.py           # JWT creation, verification, dependency
```

## Capability → Architecture Map

| Capability | Lives in | Governed by |
| --- | --- | --- |
| User Registration (FR-1) | `routes.py` → `services.py` → `store.py` | AD-1, AD-2, AD-3, AD-6 |
| User Login (FR-2) | `routes.py` → `services.py` | AD-1, AD-2, AD-4 |
| Get Current User (FR-3) | `routes.py` → `auth.py` → `services.py` | AD-1, AD-4, AD-5, AD-6, AD-7 |

### AD-6 — Password Hash Exclusion Boundary

- **Binds:** store layer, all endpoints reading user data
- **Prevents:** `password_hash` leaking through inconsistent layer boundaries
- **Rule:** `store.py` never exposes `password_hash` in any return value. All store-facing functions return a sanitized view (username + name only). The route layer never needs to strip it.

### AD-7 — Auth Dependency Contract

- **Binds:** `auth.py`, `routes.py`, `services.py`
- **Prevents:** services coupling to JWT claim structure
- **Rule:** `auth.py` is the sole JWT decoder. It exposes a FastAPI `Depends` that returns `username: str` to route handlers. Services receive only `username`, never raw tokens or JWT payloads. JWT secret is a constant string in `auth.py`.

### AD-8 — Store Lifecycle

- **Binds:** `store.py`, `main.py`
- **Prevents:** ambiguous store ownership, testing difficulties from DI plumbing
- **Rule:** `store.py` owns a module-level dict. Services import from `store.py` directly. No dependency injection of the store. Consistent with the simple local-dev scope.

## Deferred

- **Password hashing algorithm alternatives** (argon2id, scrypt) — bcrypt is fine at this scale; revisit if migrating to production.
- **Input validation beyond required fields** — PRD explicitly defers this.
- **CORS, logging, observability** — out of scope per PRD.
- **Deployment & environments** — single-process local dev only; no infra decisions needed at this altitude.
