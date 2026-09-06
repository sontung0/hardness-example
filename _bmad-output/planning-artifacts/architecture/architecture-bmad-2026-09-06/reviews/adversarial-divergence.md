# Adversarial Divergence Review — Architecture Spine

**Date:** 2026-09-06  
**Reviewer:** Adversarial AI  
**Target:** `ARCHITECTURE-SPINE.md` — Simple REST API Auth  
**Method:** For each AD, construct two hypothetical units that obey the rule to the letter yet build incompatibly. Flag gaps, missing ADs, and deferred-divergence risks.

---

## 1. AD-1 — Stateless Auth

### 1.1 Incompatible Shared-Data Shapes

**Finding 1a — JWT payload schema divergence (HIGH)**

| Unit A Implementation | Unit B Implementation |
|---|---|
| Extracts `sub` from JWT and calls `store.get_user(sub)` → returns full User dict including `name`, `username`, `password_hash` (then strips `password_hash` before response) | Extracts `sub` from JWT and calls `store.get_user(sub)` → returns only `username` and `name` (store helper designed to exclude `password_hash` at query time) |

Both obey AD-1 (stateless, token-only). But Unit A's store call returns a dict **with** `password_hash` — the stripping happens at the route layer. Unit B's store call returns a dict **without** it — the filtering happens at the store layer. If both approaches coexist in different endpoints or during a refactor, the in-memory dict shape returned by `store.get_user` is inconsistent: sometimes it has `password_hash`, sometimes it doesn't.

- **ADs involved:** AD-1, AD-3  
- **Divergence:** The `password_hash` field is included or excluded at different layers depending on which unit implements it. One unit trusts the route layer to strip; the other trusts the store layer to hide. A refactorer migrating an endpoint from one pattern to the other will introduce a bug where `password_hash` leaks or a KeyError occurs.  
- **Suggested fix:** Add **AD-6 — Password Hash Exclusion Boundary**. Rule: `store.py` never exposes `password_hash` in any return value. All store-facing functions return a sanitized view. This eliminates layer-ambiguity.

### 1.2 Ownership Ambiguity

**Finding 1b — Who owns the "current user" concept? (MEDIUM)**

Both `services.py` (via `get_current_user`) and `auth.py` (via JWT dependency) could each claim to be the authority on "who is the current user." AD-1 says identity comes from the token, but the spine's Capability Map assigns `Get Current User` to `routes.py → auth.py → services.py`. Neither AD-1 nor any other AD says whether `auth.py` resolves the username and passes it to `services.py`, or whether `services.py` receives the raw token and resolves it itself.

- **ADs involved:** AD-1, AD-4  
- **Divergence:** Unit A has `auth.py` decode the JWT and inject a `username` string into the route handler. Unit B has `auth.py` inject the full decoded JWT payload dict, and `services.py` extracts `sub`. Both are stateless. But Unit B's `services.py` now depends on JWT claim structure, coupling service logic to token format — violating the implicit layering where services don't know about transport concerns.  
- **Suggested fix:** Add **AD-7 — Auth Dependency Contract**. Rule: `auth.py` is the sole JWT decoder. It exposes a FastAPI `Depends` that returns a `username: str` to route handlers. Services receive only `username`, never raw tokens or JWT payloads.

---

## 2. AD-2 — Passwords Never in Plaintext

### 2.1 Incompatible Data Shapes

**Finding 2a — Hash format divergence (HIGH)**

| Unit A Implementation | Unit B Implementation |
|---|---|
| Uses `bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()` → stores as `str` | Uses `bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()` → stores as `bytes` (forgot `.decode()`) |

Both called `bcrypt.hashpw` with default work factor. Both obey AD-2. But Unit B stores the raw bytes. When `bcrypt.checkpw` is later called, it may work (bcrypt accepts both), but when the hash is serialized to a response or logged (debug mode), Unit A prints a clean string while Unit B prints `b'$2b$...'`.

- **ADs involved:** AD-2  
- **Divergence:** The hash is stored as `str` in one unit and `bytes` in the other. The `User` model in Consistency Conventions says `password_hash (str, never exposed)` — but the model doesn't enforce type at rest in a raw dict. Two builders could interpret "str" as "the string representation of bytes" vs "a proper str."  
- **Suggested fix:** Tighten AD-2 Rule to include: "The hash **must** be a Python `str` (not `bytes`). The store helper that writes the hash must call `.decode('utf-8')` before insertion."

### 2.2 State-Mutation Path

**Finding 2b — Double-hashing risk (MEDIUM)**

If Unit A's `services.py` hashes the password before calling `store.add_user(hashed_password)`, and Unit B's `store.py` also applies `bcrypt.hashpw` internally for "safety," a user registered through Unit B's code path ends up with a double-hashed password that can never be verified. AD-2 says "hashed with bcrypt before storage" but doesn't say *which layer* does the hashing.

- **ADs involved:** AD-2, AD-3  
- **Divergence:** The hashing boundary is ambiguous. Services could hash then pass to store, or pass plaintext to store which hashes. Both obey "passwords never in plaintext at rest." But if both layers hash, the password is unrecoverable.  
- **Suggested fix:** Add explicit rule to AD-2: "Hashing happens in exactly one layer: `services.py`. The store layer never sees or transforms plaintext passwords and never re-hashes hashes."

---

## 3. AD-3 — Single In-Memory Store

### 3.1 Incompatible Data Shapes

**Finding 3a — Dict key type divergence (HIGH)**

| Unit A Implementation | Unit B Implementation |
|---|---|
| Store keyed by `username` (string): `users = {"alice": {...}}` | Store keyed by `username` (lowercased string): `users = {"alice": {...}}` but Unit B lowercases on insert, so `Alice` → `alice` |

Both use a single Python dict. Both are in-memory. But AD-3 doesn't specify whether keys are case-sensitive. Unit A treats `Alice` and `alice` as different users. Unit B treats them as the same. When an endpoint implemented by Unit A writes `{"Alice": {...}}` and an endpoint implemented by Unit B reads with `users.get("alice")`, it gets `None` — silent data loss.

- **ADs involved:** AD-3, AD-5  
- **Divergence:** Case normalization of the username key is unspecified. Two units create a store where the same logical user has two entries, or where a lookup fails unexpectedly.  
- **Suggested fix:** Add to Consistency Conventions or a new AD: "Username keys in the store are always lowercased on write. All lookups use the lowercased form."

### 3.2 Ownership Ambiguity

**Finding 3b — Who initializes the store? (MEDIUM)**

AD-3 says "one Python dict." But the spine doesn't say whether `store.py` owns the dict instance (module-level global), whether `main.py` creates it and injects it, or whether each service module imports it directly.

- **ADs involved:** AD-3  
- **Divergence:** Unit A uses a module-level `users: dict = {}` in `store.py` imported everywhere. Unit B creates the dict in `main.py` and passes it via dependency injection. Both have one dict. But Unit A's approach makes testing harder (global state) and Unit B's requires an additional plumbing contract not described in the spine.  
- **Suggested fix:** Add **AD-8 — Store Lifecycle**. Rule: `store.py` owns a module-level dict. Services import from `store.py` directly. No dependency injection of the store. This is consistent with "simple local dev" scope.

---

## 4. AD-4 — JWT as Sole Auth Mechanism

### 4.1 Conflicting State-Mutation Paths

**Finding 4a — Token expiry handling divergence (MEDIUM)**

AD-4 says "no refresh tokens, no token rotation." But it doesn't say what happens when a token expires. Unit A returns a `401` with `{"detail": "Token expired"}`. Unit B returns a generic `401` with `{"detail": "Not authenticated"}`. Both obey AD-4. But the error shape differs.

- **ADs involved:** AD-4, AD-5  
- **Divergence:** The specific error message for an expired vs. missing token is unspecified. Two units produce different `detail` strings for the same logical failure.  
- **Suggested fix:** Extend AD-5 to require that 401 errors use the message `"Not authenticated"` uniformly, regardless of whether the cause is missing, malformed, or expired tokens. AD-4 should state: "Expired tokens are treated identically to missing tokens — no distinction exposed to callers."

### 4.2 Ownership Ambiguity

**Finding 4b — Who validates the token? (HIGH)**

AD-4 says JWT is the sole mechanism. The Capability Map assigns `Get Current User` to `routes.py → auth.py → services.py`. But AD-4 doesn't say whether `auth.py` validates the token signature *and* expiry, or whether `services.py` also validates. 

| Unit A | Unit B |
|---|---|
| `auth.py` validates signature + expiry, injects `username` | `auth.py` validates signature only, `services.py` checks expiry separately |

Both use JWT as sole auth. But Unit B has service-layer expiry logic that Unit A doesn't. If the JWT library's default behavior changes (e.g., `verify_exp` default), Unit A is unaffected (auth.py handles it) while Unit B breaks silently.

- **ADs involved:** AD-4  
- **Divergence:** Token validation responsibility is split differently. Two units build two different validation pipelines for the same token.  
- **Suggested fix:** Strengthen AD-4: "`auth.py` is the single point of JWT validation. It verifies signature, expiry, and claim presence. No other module may call `jwt.decode` or inspect token internals."

---

## 5. AD-5 — Consistent Error Shape

### 5.1 Incompatible Data Shapes

**Finding 5a — Error `detail` field type divergence (HIGH)**

AD-5 says errors return `{"detail": "message"}`. But:

| Unit A | Unit B |
|---|---|
| `{"detail": "Username already exists"}` — always a string | `{"detail": ["Username already exists", "Pick a different name"]}` — a list of strings for compound errors |

Both have a `detail` field. Both are JSON. But Unit B uses a list, violating the spirit ("string"). FastAPI's own `HTTPException` defaults to a string or a list depending on how it's raised.

- **ADs involved:** AD-5  
- **Divergence:** The type of `detail` (string vs. list) is not enforced by the spine. Two builders produce incompatible client-facing shapes.  
- **Suggested fix:** Tighten AD-5: "`detail` must always be a plain string, not a list or nested object. For compound errors, concatenate into a single string."

### 5.2 Gap: Missing Error Cases

**Finding 5b — 400 vs 422 ambiguity (MEDIUM)**

FastAPI automatically returns `422 Unprocessable Entity` for Pydantic validation errors. AD-5 says "400 for bad input." But FastAPI's default validation error shape is `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}` — which is neither a plain string nor a 400 status.

- **ADs involved:** AD-5  
- **Divergence:** Unit A catches Pydantic errors globally and re-raises as `400` with a string `detail`. Unit B lets FastAPI's default handler run, producing `422` with a list `detail`. Both claim to follow AD-5. Clients see two different error shapes for "bad input."  
- **Suggested fix:** Add to AD-5: "A global exception handler converts all validation errors to `400` with a string `detail`. FastAPI's default `422` handler is overridden."

---

## 6. Consistency Conventions — Gaps

### 6.1 Response Shape for Register

**Finding 6a — Register response body unspecified (HIGH)**

The Consistency Conventions say "Success: JSON with relevant fields" and status `201` on register. But they don't specify **which fields** the register response includes.

| Unit A | Unit B |
|---|---|
| Returns `{"username": "alice", "name": "Alice"}` | Returns `{"username": "alice", "name": "Alice", "token": "eyJ..."}` |

Unit B adds a JWT token in the register response (obeying AD-1 — stateless auth, token-based). Unit A does not (user must call `/login` separately). Both are valid interpretations. But the client contract diverges.

- **ADs involved:** AD-1, AD-5  
- **Divergence:** Register response shape is unspecified. Two units produce different JSON payloads for the same `201` response.  
- **Suggested fix:** Add to Consistency Conventions: "Register returns `{"username": "<str>", "name": "<str>"}` — no token. Login returns `{"token": "<str>"}`."

### 6.2 Login Response Shape

**Finding 6b — Login response body unspecified (MEDIUM)**

Similarly, login returns `200` but the response body isn't defined.

| Unit A | Unit B |
|---|---|
| `{"token": "eyJ..."}` | `{"access_token": "eyJ...", "token_type": "bearer"}` |

Both are common JWT conventions. Both are valid. But they're incompatible.

- **ADs involved:** AD-5  
- **Suggested fix:** Add to Consistency Conventions: "Login returns `{"token": "<str>"}`. No `token_type` field."

---

## 7. Deferred Items — Divergence Risks

### 7.1 JWT Secret Management

**Finding 7a — Secret source divergence (MEDIUM)**

Deferred says "env var vs hardcoded; appropriate for this scope." But if Unit A hardcodes `SECRET = "supersecret"` and Unit B reads `os.environ["JWT_SECRET"]`, they produce tokens signed with different secrets. In a single-process app this works, but if the codebase is later split or tested across modules, tokens from one path can't be verified by the other.

- **Risk:** Medium (deferred items are explicitly out of scope, but this one has runtime consequences even in single-process mode if two modules pick different paths).  
- **Suggested fix:** Pin the deferred decision now: "JWT secret is a hardcoded constant in `auth.py`. No env var." It's simpler and unambiguous for this scope.

### 7.2 Input Validation

**Finding 7b — Validation scope divergence (LOW)**

Deferred says "input validation beyond required fields" is deferred. But one unit might add `min_length=3` on `username` while another accepts any non-empty string. Both obey the PRD (which defers this), but the data shape entering the store differs.

- **Risk:** Low for this scope. Noted for completeness.

---

## 8. Missing ADs

| Missing AD | Why It's Needed | Suggested Title |
|---|---|---|
| Password hash exclusion boundary | Who strips `password_hash` from return values is ambiguous | AD-6 — Store Returns Never Include Password Hash |
| Auth dependency contract | What `auth.py` injects into routes is unspecified | AD-7 — Auth Dependency Returns `username: str` Only |
| Store lifecycle | Store ownership and initialization is unspecified | AD-8 — Store Owns Module-Level Dict |
| Register/Login response shapes | Success response bodies are undefined | AD-9 — Success Response Schemas (or add to Consistency Conventions) |
| Validation error handling | FastAPI's 422 vs AD-5's 400 is unaddressed | AD-10 — Global Validation Error Handler |

---

## 9. Capability → Architecture Map Completeness

The map covers three capabilities: Registration (FR-1), Login (FR-2), Get Current User (FR-3).

**Gap:** The map doesn't address:
- **JWT token creation** — lives in `auth.py` but is called by `services.py` during login and (optionally) registration. Not mapped to any capability explicitly. Two builders could put token creation in `services.py` (Unit A) or `auth.py` (Unit B).
- **Error handling** — cross-cutting, not mapped. The global exception handler (if it exists) isn't assigned to any capability or module.

**Suggested fix:** Add rows for "JWT Token Creation" → `auth.py` (called by `services.py`) and "Error Handling" → `routes.py` (global exception handler).

---

## Summary Table

| # | Finding | Severity | ADs | Divergence |
|---|---|---|---|---|
| 1a | `password_hash` stripped at different layers | HIGH | AD-1, AD-3 | Store return shape includes/excludes hash |
| 1b | "Current user" ownership ambiguous | MEDIUM | AD-1, AD-4 | Token decoded in auth vs service layer |
| 2a | Hash stored as `str` vs `bytes` | HIGH | AD-2 | `User` dict `password_hash` type differs |
| 2b | Double-hashing risk (hashing boundary) | MEDIUM | AD-2, AD-3 | Both layers hash → unrecoverable password |
| 3a | Dict key case sensitivity unspecified | HIGH | AD-3, AD-5 | `Alice` ≠ `alice` across units |
| 3b | Store initialization ownership | MEDIUM | AD-3 | Global dict vs injected dict |
| 4a | Expired token error message differs | MEDIUM | AD-4, AD-5 | Different 401 `detail` strings |
| 4b | Token validation responsibility split | HIGH | AD-4 | Dual `jwt.decode` callsites |
| 5a | `detail` field type (string vs list) | HIGH | AD-5 | Incompatible error JSON shapes |
| 5b | 400 vs 422 for validation errors | MEDIUM | AD-5 | FastAPI default vs custom handler |
| 6a | Register response body unspecified | HIGH | AD-1, AD-5 | With-token vs without-token response |
| 6b | Login response body unspecified | MEDIUM | AD-5 | `token` vs `access_token`+`token_type` |
| 7a | JWT secret source diverges | MEDIUM | Deferred | Hardcoded vs env var — different secrets |
| 7b | Input validation scope diverges | LOW | Deferred | Min-length constraints differ |

---

## Verdict

**FAIL** — The spine has **5 high-severity** and **6 medium-severity** divergences that would allow two compliant builders to produce incompatible implementations. The most critical gaps are: (1) undefined success response shapes for register/login, (2) unspecified `password_hash` exclusion boundary, (3) ambiguous JWT validation ownership, (4) untyped error `detail` field, and (5) case-sensitive store keys. The spine needs 5–6 additional ADs or tightened rules before it can serve as a reliable build substrate.
