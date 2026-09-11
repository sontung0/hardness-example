---
title: Simple REST API — Register, Login, Get Current User
status: final
created: 2026-09-06
updated: 2026-09-06
---

# PRD: Simple REST API — Register, Login, Get Current User

## 0. Document Purpose

This PRD defines a minimal REST API with three endpoints: user registration, login, and retrieving the currently authenticated user. It is intended for a developer building a small, stateless API with in-memory storage. The document covers the API contract, data model, and authentication flow at a level appropriate for a hobby/personal project.

## 1. Vision

A dead-simple REST API that handles the full auth lifecycle — register, log in, and fetch your own profile — with zero external dependencies beyond a framework. Data lives in memory, the auth token is a signed JWT, and the entire thing can be stood up in a single file. This is a building block: a starting point for projects that need basic user auth without a database.

## 2. Target User

### 2.1 Jobs To Be Done

- **As a developer**, I want to spin up a working auth API quickly so I can build on top of it without wiring up a database or third-party auth service.
- **As a developer**, I want a clean, standard REST contract so I can test it with any HTTP client or integrate it into a frontend.

### 2.3 Key User Journeys

**UJ-1. Alex registers a new account.**
Alex sends a POST request with username, password, and name. The system validates the input, stores the user in memory, and returns a success response with a JWT. Alex is now authenticated.

**UJ-2. Alex logs in with their credentials.**
Alex sends a POST request with username and password. The system validates the credentials against the in-memory store and returns a JWT. Alex is now authenticated.

**UJ-3. Alex fetches their own profile.**
Alex sends a GET request with the JWT in the Authorization header. The system validates the token and returns the current user's profile (username and name, never the password).

## 3. Glossary

- **User** — A registered account with a username, password (hashed), and display name. Each username is unique.
- **JWT** — JSON Web Token, a signed token containing the user's identity. Used for authenticating subsequent requests.
- **In-memory store** — A program-level data structure (e.g., a Python dict) that holds all user data for the lifetime of the process. Data is lost on restart.

## 4. Features

### 4.1 User Registration

**Description:** A new user can create an account by providing a username, password, and display name. The system validates uniqueness of the username, hashes the password, stores the user, and returns a signed JWT. Realizes UJ-1.

**Functional Requirements:**

#### FR-1: Register a new user

The system accepts a POST request with username, password, and name, validates the input, creates a User, and returns a JWT.

**Consequences (testable):**
- Request with valid, unique username → HTTP 201 with a JWT in the response body.
- Request with a username that already exists → HTTP 409 Conflict.
- Request with missing required fields → HTTP 400 Bad Request.
- The stored password is never the plaintext value sent by the client.
- The returned JWT contains the user's username as a claim.

**Out of Scope:**
- Email verification, password reset, profile editing.

### 4.2 User Login

**Description:** An existing user can log in by providing their username and password. The system validates the credentials and returns a signed JWT. Realizes UJ-2.

**Functional Requirements:**

#### FR-2: Login with valid credentials

The system accepts a POST request with username and password, validates against the in-memory store, and returns a JWT.

**Consequences (testable):**
- Request with correct username and password → HTTP 200 with a JWT in the response body.
- Request with wrong username or password → HTTP 401 Unauthorized.
- Request with missing fields → HTTP 400 Bad Request.

**Out of Scope:**
- Rate limiting, account lockout, refresh tokens.

### 4.3 Get Current User

**Description:** An authenticated user can retrieve their own profile by providing a valid JWT in the request header. The system validates the token and returns the user's username and name. Password is never returned. Realizes UJ-3.

**Functional Requirements:**

#### FR-3: Retrieve current user profile

The system accepts a GET request with a valid JWT in the Authorization header and returns the current user's profile.

**Consequences (testable):**
- Request with valid JWT → HTTP 200 with username and name (no password) in the response body.
- Request with no Authorization header → HTTP 401 Unauthorized.
- Request with an expired or invalid JWT → HTTP 401 Unauthorized.

**Out of Scope:**
- Updating profile fields, listing other users, pagination.

## 5. Non-Goals (Explicit)

- **No persistence** — data is lost when the process restarts. This is by design.
- **No database** — in-memory dict only.
- **No refresh tokens** — single JWT per login/register, no token rotation.
- **No rate limiting or brute-force protection.**
- **No HTTPS enforcement** — assumed handled at a reverse proxy or load balancer layer.
- **No role-based access control or multi-user permissions.**

## 6. MVP Scope

### 6.1 In Scope

- POST `/register` — create a new user, return JWT
- POST `/login` — authenticate, return JWT
- GET `/me` — return current user from JWT
- Password hashing with bcrypt (or similar)
- JWT signing and validation
- In-memory user storage

### 6.2 Out of Scope for MVP

- Token refresh / revocation
- Input validation beyond required-field checks
- API documentation (Swagger/OpenAPI)
- CORS configuration
- Logging and observability

## 7. Success Metrics

- **SM-1:** A user can register, log in, and fetch their profile using only `curl` or Postman. Validates FR-1, FR-2, FR-3.
- **SM-2:** Passwords are never stored in plaintext in the in-memory store. Validates FR-1.
- **SM-3:** Expired or missing tokens are rejected with HTTP 401. Validates FR-3.

## 8. Open Questions

1. **Which framework?** `[ASSUMPTION: FastAPI (Python) or Express (Node.js) — developer's choice, not locked in here.]`
2. **JWT secret key management?** `[ASSUMPTION: Hardcoded or environment-variable based; appropriate for this scope.]`
3. **Password hashing algorithm?** `[ASSUMPTION: bcrypt with default work factor.]`

## 9. Assumptions Index

- Framework choice is developer's preference — FRs are framework-agnostic. (§8.1)
- JWT secret is managed via environment variable or hardcoded constant. (§8.2)
- bcrypt for password hashing with default cost. (§8.3)
- No input sanitization beyond required-field presence checks. (§6.2)
- No HTTPS — TLS termination assumed at infrastructure layer. (§5)
