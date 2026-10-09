# Rubric Walker Review — Architecture Spine

**Reviewed:** `ARCHITECTURE-SPINE.md` (updated 2026-09-11)
**Reviewed against:** PRD 09-06, PRD 09-11, source files in `src/`
**Date:** 2026-09-11

---

## Checklist Results

### 1. Fixes real divergence points — PASS
All major boundaries in the layered model (route ↔ service ↔ store) are governed by at least one AD. Cross-cutting concerns (stateless auth, password handling, error shape) are also covered. No unguarded divergence point identified.

### 2. Every AD's Rule is enforceable and prevents its stated divergence — PASS
All 11 ADs specify concrete, testable rules with clear scope. Each rule maps directly to a code-level invariant that can be verified in tests or code review.

### 3. Nothing under Deferred lets two units diverge — PASS
All deferred items (argon2id, CORS, deployment, token rotation, password history, rate limiting) are either explicitly out-of-scope per the PRD or are future production concerns that don't create ambiguity about current behavior. No deferred item straddles a layer boundary.

### 4. Named tech is verified-current — PASS (minor note)
Stack versions (FastAPI 0.141.1, Uvicorn 0.52.4, bcrypt 5.0.0, PyJWT 2.13.0, Python ≥3.10) are consistent with the `>=` constraints in `pyproject.toml`. Exact versions are plausible but cannot be confirmed as the absolute latest releases from pinned references alone. No version in the spine contradicts the lockfile or pyproject constraints.

### 5. Ratifies rather than contradicts brownfield codebase — FAIL

**F1 — AD-6 rule contradicts existing `store.py`:**
AD-6 states: *"store.py never exposes `password_hash` in any return value."*
`store.py` already contains `get_user_with_hash()`, which returns the full user dict including `password_hash`. This function is actively called by `services.py::authenticate_user()`. The AD rule as written is factually false for the current codebase.

**Remediation:** Rephrase AD-6 to scope the exclusion boundary correctly. For example: *"No function called from the route layer exposes `password_hash`. The store may expose it to the service layer via explicit internal functions (e.g., `get_user_with_hash`), but such functions must be named to signal their privileged nature and must never be called directly from routes."*

**F2 — AD-7 minor tension with `auth.py`:**
AD-7 says *"JWT secret is a constant string in auth.py."* In practice, `auth.py` reads `os.environ.get("JWT_SECRET_KEY", "super-secret-key-do-not-commit")`, so the secret is a constant-with-env-override, not a hardcoded constant. This is a minor mismatch — not a hard contradiction, but the AD should acknowledge the env override to stay accurate.

**Other brownfield checks (all pass):**
- `get_user()` correctly strips `password_hash` — consistent with AD-6 intent.
- `add_user()` stores all fields in a module-level dict — consistent with AD-3, AD-8.
- Services import from store, routes import from services and auth — layered pattern holds.
- `main.py` custom validation handler maps 422→400 with `{"detail": str}` — consistent with AD-5.
- `auth.py` exposes `get_current_user` as a FastAPI `Depends` returning `username: str` — consistent with AD-7.
- No `change_password` or `update_password` exists yet — spine is correctly prescriptive for the new feature.

### 6. Covers the spec's capabilities — FAIL (minor)

**F3 — FR numbering diverges from PRD 09-11:**
The spine's `binds` field lists `FR-1.1, FR-1.2, FR-1.3, FR-1.4` for the password change feature, and the Capability → Architecture Map references "Change Password (FR-1.1–1.4)." However, the PRD 09-11 numbers its functional requirements as `FR-1` through `FR-4` (change password, reject wrong current password, reject weak new password, reject no auth). The spine's sub-FR numbering (`1.1–1.4`) does not match the PRD's flat numbering (`1–4`). This breaks traceability between the spine and the PRD.

**Remediation:** Either adopt the PRD's FR numbering in the spine's `binds` field, or add a mapping note that explicitly translates between the two schemes.

**PRD 09-06 coverage:** FR-1 (register), FR-2 (login), FR-3 (get current user) are covered by the original ADs and the Capability → Architecture Map. No gaps.

### 7. Parent spine inheritance — N/A
No parent spine is referenced. The spine is at `altitude: feature` and stands alone.

### 8. All dimensions decided, deferred, or open — PASS
Every dimension relevant to a feature-altitude spine is accounted for:

| Dimension | Status |
|---|---|
| Architecture pattern | Decided (layered) |
| Auth mechanism | Decided (JWT) |
| Data storage | Decided (in-memory dict) |
| Password policy | Decided (8 chars, no complexity) |
| Error handling | Decided (AD-5, AD-10) |
| API contract | Decided (Consistency Conventions table) |
| Tech stack | Decided (Stack table) |
| JWT config | Decided (24h, HS256, sub=username.lower) |
| Token rotation | Deferred (PRD defers explicitly) |
| Password history | Deferred (PRD defers explicitly) |
| Rate limiting | Deferred |
| CORS / logging / observability | Deferred |
| Deployment | Deferred |

No dimension is silently missing.

---

## Document Structure Note

The Capability → Architecture Map table references AD-6, AD-7, AD-9, AD-10, and AD-11 before they are formally defined later in the document. This creates forward references that break the document's internal ordering. Consider moving the AD definitions before the capability map, or adding a brief note that the map references ADs defined in the following sections.

---

## Summary

| # | Finding | Severity | Checklist Item |
|---|---------|----------|---------------|
| F1 | AD-6 rule ("never exposes `password_hash`") contradicts existing `get_user_with_hash()` in `store.py` | High | #5 (brownfield) |
| F2 | AD-7 says "constant string" but `auth.py` uses env override | Low | #5 (brownfield) |
| F3 | Spine FR numbering (FR-1.1–1.4) diverges from PRD 09-11 numbering (FR-1–4) | Medium | #6 (spec coverage) |
| — | Capability map references ADs defined later in document | Low | Structure |

**Verdict: FAIL**

Two high/medium issues must be resolved: AD-6's contradiction with the existing `get_user_with_hash` function, and the FR traceability mismatch with PRD 09-11. The AD-7 tension is low severity and can be resolved with a clarifying phrase.
