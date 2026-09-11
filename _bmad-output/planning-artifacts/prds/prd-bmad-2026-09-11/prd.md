---
title: Password Change API
status: draft
created: 2026-09-11
updated: 2026-09-11
---

# PRD: Password Change API

## 0. Document Purpose

This PRD defines a single new endpoint: change password for an authenticated user. It builds on the existing Simple REST API (`prd-bmad-2026-09-06`) — same JWT auth, same in-memory store, same framework. This document covers the API contract, validation rules, and edge cases at a level appropriate for a hobby/personal project.

## 1. Vision

A straightforward password change flow that lets authenticated users update their password by providing their current password and a new one. It follows the same minimal patterns as the rest of the API — one endpoint, clear input/output, no external dependencies.

## 2. Target User

### 2.1 Jobs To Be Done

- **As a developer**, I want a simple password change endpoint so users can update their credentials without needing a full account management system.

### 2.3 Key User Journeys

**UJ-1. Alex changes their password while logged in.**
Alex is authenticated and sends a POST request with their current password and a new password. The system validates the current password against the stored hash, validates the new password meets minimum requirements, hashes and stores the new password, and returns a success response. Alex's existing JWT remains valid.

**UJ-2. Alex tries to change their password with the wrong current password.**
Alex sends a POST request with an incorrect current password. The system rejects the request with HTTP 401. Alex is not told whether the username or password was wrong.

## 3. Glossary

- **User** — A registered account with a username, password (hashed), and display name. Each username is unique.
- **JWT** — JSON Web Token, a signed token containing the user's identity. Used for authenticating subsequent requests.
- **In-memory store** — A program-level data structure (e.g., a Python dict) that holds all user data for the lifetime of the process. Data is lost on restart.
- **Current password** — The password the User provided at registration or their most recent successful password change. Used to authorize a new password change.

## 4. Features

### 4.1 Password Change

**Description:** An authenticated User can change their password by providing their current password and a new password. The system validates the current password, applies minimum requirements to the new password, hashes it, stores the updated User, and returns a success response. The User's existing JWT remains valid after the change. Realizes UJ-1, UJ-2.

**Functional Requirements:**

#### FR-1: Change password with valid current password

The system accepts a POST request with a valid JWT in the Authorization header, a current password, and a new password. It validates the current password, hashes and stores the new password, and returns HTTP 200.

**Consequences (testable):**
- Request with valid JWT, correct current password, and new password meeting minimum requirements → HTTP 200 with a success message.
- The stored password is updated to the new hashed value.
- The old password can no longer be used to authenticate. `[ASSUMPTION: The system does not maintain a password history.]`
- The existing JWT remains valid (no token rotation). `[ASSUMPTION: This is intentional for simplicity; a production system would rotate the token.]`

#### FR-2: Reject change with wrong current password

The system rejects a password change request when the current password does not match the stored hash.

**Consequences (testable):**
- Request with valid JWT but wrong current password → HTTP 401 Unauthorized.
- The response does not reveal whether the username or password was incorrect.

#### FR-3: Reject change with weak new password

The system enforces a minimum password length for the new password.

**Consequences (testable):**
- New password shorter than 8 characters → HTTP 400 Bad Request with a message indicating minimum length. `[ASSUMPTION: 8 characters is the minimum; no complexity rules beyond length for this scope.]`
- New password is 8 or more characters → passes validation (proceeds to hash and store).

#### FR-4: Reject change without authentication

The system rejects password change requests that lack a valid JWT.

**Consequences (testable):**
- Request with no Authorization header → HTTP 401 Unauthorized.
- Request with an expired or invalid JWT → HTTP 401 Unauthorized.

**Out of Scope:**
- Password history or breach detection.
- Forcing re-authentication for sensitive operations.
- Password reset (forgot password flow).
- Token rotation after password change.

## 5. Non-Goals (Explicit)

- **No password reset** — users must know their current password.
- **No password history** — the system does not track previous passwords.
- **No token rotation** — the JWT issued at login/register remains valid after a password change.
- **No account lockout** — no limit on failed password change attempts beyond the general lack of rate limiting.
- **No email or notification** — the user is not notified when their password changes.

## 6. MVP Scope

### 6.1 In Scope

- POST `/change-password` — authenticated endpoint to change password
- Current password validation
- New password minimum length enforcement (8 characters)
- Password hashing (bcrypt or similar, consistent with existing API)
- Success/error responses

### 6.2 Out of Scope for MVP

- Password reset / forgot password flow
- Password strength meter or complexity rules
- Audit logging of password changes
- Token rotation after password change

## 7. Success Metrics

- **SM-1:** An authenticated user can change their password by providing the correct current password and a valid new password. Validates FR-1.
- **SM-2:** A request with the wrong current password is rejected with HTTP 401. Validates FR-2.
- **SM-3:** A new password shorter than 8 characters is rejected with HTTP 400. Validates FR-3.
- **SM-4:** After a successful password change, the old password can no longer be used to log in. Validates FR-1.

## 8. Open Questions

1. **Should the endpoint invalidate all other JWTs for the user after a password change?** `[ASSUMPTION: No — the existing JWT remains valid. This is simpler but means a stolen token stays usable until it expires.]`

## 9. Assumptions Index

- The API uses the same framework, JWT setup, and in-memory store as the existing Simple REST API. (§0)
- The current password is required — the user must prove they know it before changing. (§4.1)
- Minimum password length is 8 characters; no complexity rules. (§4.1, FR-3)
- No password history is maintained. (§4.1, FR-1)
- No token rotation after password change — existing JWT stays valid. (§4.1, FR-1)
- The response for wrong current password does not reveal which field was wrong. (§4.1, FR-2)
