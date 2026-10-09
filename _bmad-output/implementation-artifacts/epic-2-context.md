# Epic 2 Context: Password Management

<!-- Generated from planning artifacts. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Authenticated users can change their password by proving they know the current one and supplying a new one that meets a minimum length requirement. This closes a basic account-security gap in the API: without it, users have no way to update credentials after registration, and the endpoint must reject unauthorized, incorrect, or weak-password attempts without leaking information about which check failed.

## Stories

- Story 2.1: Change password

## Requirements & Constraints

- Endpoint accepts a valid JWT, the current password, and a new password; on success it verifies the current password, hashes and stores the new one, and returns success — the previous password can no longer authenticate.
- Wrong current password → 401 Unauthorized, using the exact same generic message as login failure (`{"detail": "Invalid credentials"}`), so the response never reveals whether the username or the password was the problem (no user enumeration).
- New password shorter than 8 characters → 400 Bad Request with `{"detail": "Password must be at least 8 characters"}`. No complexity rules beyond length.
- Missing/invalid/expired JWT → 401 Unauthorized, same as other authenticated endpoints.
- A rejected request (wrong current password or weak new password) must leave the stored password unchanged.
- The existing JWT stays valid after a successful change — no token rotation, no invalidation, no forced re-authentication. This is an intentional simplification, not an oversight.
- Out of scope: password reset/forgot-password flow, password history or breach detection, complexity rules, rate limiting on attempts, audit logging, email/notification on change.

## Technical Decisions

- Layering is strict: routes.py (HTTP contract only) → services.py (owns all password-change business logic, including bcrypt verify/hash) → store.py (dumb writer only).
- `store.py` exposes `update_password(username, new_hash)`, which only overwrites the `password_hash` field — no validation, no hashing, no bcrypt work at this layer (same pattern as `add_user`).
- All bcrypt work — verifying the current password against the stored hash and hashing the new password — happens exclusively in `services.py`. Store never sees or transforms plaintext.
- `password_hash` must never be exposed to the route layer or in any response; only privileged, explicitly-named service/store functions may touch it.
- Auth is via the existing shared JWT dependency (`auth.py`'s `Depends`), which yields only `username: str` to the route/service — never raw tokens or claims.
- Request body shape: `{"current_password": str, "new_password": str}`. Success response: `{"message": "Password changed successfully"}`, HTTP 200.
- Error responses follow the project-wide consistent shape: `{"detail": str}`, with 400/401 status codes as specified above.

## Cross-Story Dependencies

- Depends on Epic 1, Story 1.1 for the project scaffold, the shared in-memory store, and `auth.py`'s JWT dependency.
- Depends on Epic 1, Story 1.2's bcrypt hashing pattern (same hashing approach reused here for the new password).
- Depends on Epic 1, Story 1.4's `get_current_user` auth dependency to authenticate the request before any password-change logic runs.
