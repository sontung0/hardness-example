---
title: 'Guard bcrypt 72-byte password limit in services.py'
type: 'bugfix'
created: '2026-09-15'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: false
context: []
warnings: []
deferred: []
baseline_revision: '250426034c23f6851b1471c1d4c6d3b301f80a74'
---

<intent-contract>

## Intent

**Problem:** bcrypt raises a raw internal `ValueError` ("password cannot be longer than 72 bytes...") whenever a UTF-8 encoded password exceeds 72 bytes. In `register_user` and `authenticate_user` this has existed since Epic 1; `change_password` (Epic 2) has the identical unguarded pattern for both `current_password` and `new_password`. Callers in `routes.py` map generic `ValueError` straight to a 4xx `detail`, so bcrypt's internal message leaks to the client.

**Approach:** In `src/services.py`, before every `bcrypt.hashpw`/`bcrypt.checkpw` call, check whether the UTF-8 encoded password exceeds 72 bytes and raise a clean `ValueError("Password must be at most 72 bytes")` instead of letting bcrypt raise. Fix stays entirely inside `services.py` (AD-2 "exactly one layer" rule); `routes.py`'s existing `ValueError`→4xx mapping needs no change.

## Boundaries & Constraints

**Always:** Check byte length (`len(password.encode("utf-8"))`) against 72 for every password passed to `bcrypt.hashpw`/`bcrypt.checkpw`: `register_user`'s `password`, `authenticate_user`'s `password`, `change_password`'s `current_password` and `new_password`. Raise `ValueError("Password must be at most 72 bytes")` verbatim for each. Preserve existing check ordering in `change_password` (current-password verification still precedes the new-password length/strength checks).

**Never:** Do not modify `routes.py`, `store.py`, or any model/schema. Do not add a length guard to `get_current_user_profile` (no password involved). Do not truncate passwords — reject them instead. Do not change the 8-character minimum check or its message in `change_password`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Register, oversized password | `register_user(username, "a"*73, name)` | No user created | `ValueError("Password must be at most 72 bytes")` |
| Register, 72-byte password (boundary) | `register_user(username, "a"*72, name)` | User created normally | No error expected |
| Authenticate, oversized password | `authenticate_user(username, "a"*73)` | No auth attempt against stored hash | `ValueError("Password must be at most 72 bytes")` |
| Change password, oversized current_password | `change_password(username, "a"*73, "newpass123")` | No `bcrypt.checkpw` call made | `ValueError("Password must be at most 72 bytes")` |
| Change password, oversized new_password (current valid) | `change_password(username, valid_current, "a"*73)` | No `bcrypt.hashpw` call made, password unchanged | `ValueError("Password must be at most 72 bytes")` |
| Change password, multi-byte UTF-8 password over 72 bytes but ≤72 chars | `change_password(username, valid_current, "é"*40)` (80 bytes, 40 chars) | Rejected by byte length, not char length | `ValueError("Password must be at most 72 bytes")` |

</intent-contract>

## Code Map

- `src/services.py` -- all four guard insertion points: `register_user` (line ~14, before `bcrypt.hashpw`), `authenticate_user` (line ~25, before `bcrypt.checkpw`), `change_password` (line ~44, before `bcrypt.checkpw` on `current_password`; line ~50, before `bcrypt.hashpw` on `new_password`, after the existing 8-char check at line ~47-48).
- `src/routes.py` -- read-only evidence: generic `ValueError`→4xx mapping already forwards `str(e)` for `/register` (line 28-30) and `/change-password` (line 61-63), so a clean service-layer message reaches the client unmodified; `/login` (line 40-41) always returns a fixed "Invalid credentials" regardless of the `ValueError` message, so no client-facing change there, but the guard still prevents bcrypt's raw message from being raised at all. No routes.py changes needed.
- `tests/unit/test_services.py` -- existing tests for `register_user`/`authenticate_user`; add new length-guard cases here, following existing class structure (`TestRegisterUser`, `TestAuthenticateUser`).
- `tests/unit/test_services_password_change.py` -- existing tests for `change_password`; add new length-guard cases here, following existing `TestChangePassword` class and `pytest.raises(ValueError, match=...)` style. Note existing precedence test (`test_change_password_wrong_current_with_short_new_raises_invalid_credentials`) establishes current-password check runs before new-password checks — mirror this for the length guard.

## Tasks & Acceptance

**Execution:**
- `src/services.py` -- add a length check (`len(password.encode("utf-8")) > 72`) raising `ValueError("Password must be at most 72 bytes")` immediately before each of the four `bcrypt.hashpw`/`bcrypt.checkpw` calls in `register_user`, `authenticate_user`, and `change_password` -- stops bcrypt's raw internal message from ever being raised, per DW-1.
- `tests/unit/test_services.py` -- add unit tests asserting `register_user` and `authenticate_user` raise the clean message for a 73-byte password and succeed for exactly 72 bytes -- covers the I/O matrix boundary cases for those two functions.
- `tests/unit/test_services_password_change.py` -- add unit tests asserting `change_password` raises the clean message when `current_password` exceeds 72 bytes (before reaching the current-password check) and when `new_password` exceeds 72 bytes (after the current-password check succeeds), including a multi-byte UTF-8 case -- covers the I/O matrix cases for `change_password`.

**Acceptance Criteria:**
- Given a password whose UTF-8 encoding exceeds 72 bytes, when `register_user` is called, then it raises `ValueError("Password must be at most 72 bytes")` and no user is added to the store.
- Given a password whose UTF-8 encoding exceeds 72 bytes, when `authenticate_user` is called, then it raises `ValueError("Password must be at most 72 bytes")` without invoking `bcrypt.checkpw`.
- Given a `current_password` whose UTF-8 encoding exceeds 72 bytes, when `change_password` is called, then it raises `ValueError("Password must be at most 72 bytes")` without invoking `bcrypt.checkpw`.
- Given a valid `current_password` and a `new_password` whose UTF-8 encoding exceeds 72 bytes, when `change_password` is called, then it raises `ValueError("Password must be at most 72 bytes")` without invoking `bcrypt.hashpw`, and the stored password hash is unchanged.
- Given a password exactly 72 bytes, when passed to any of the three functions, then no length-guard error is raised and the existing bcrypt flow proceeds normally.

## Spec Change Log

## Review Triage Log

### 2026-09-15 — Review pass
- verdicts: 8 findings — high 0, medium 2, low 2, false 4, maybe-false 0
- findings:
  - `[low]` `[reject]` Four near-identical `len(x.encode("utf-8")) > 72` guard blocks are duplicated across `register_user`/`authenticate_user`/`change_password` instead of a shared helper — future limit/message changes must be kept consistent by hand — evidence: verified duplication is real, but the fix (extracting a helper) is more than a direct correction and unlikely to be hit in everyday use; rejected in favor of the codebase's existing minimal-diff style.
  - `[false]` `[reject]` bcrypt also raises a raw internal `ValueError` for passwords containing a NUL byte, leaving that leak path unguarded — evidence: empirically disproved — `bcrypt.hashpw(b"abc\x00def", bcrypt.gensalt())` succeeds without error on bcrypt 5.0.0 (the pinned version), so no NUL-byte leak exists at these call sites.
  - `[medium]` `[patch]` No test confirms the HTTP-level behavior the fix exists for — a client hitting `POST /register` or `POST /change-password` with an oversized password actually receives 400 with the clean detail message — only service-function-level unit tests were added — evidence: confirmed by search — no occurrence of "72" bytes in `tests/integration/` or `tests/test_auth.py` before this pass. Action: re-engaged the implementation subagent, which added `test_oversized_new_password_returns_400` (tests/integration/test_password_change.py) and `test_register_oversized_password_returns_400` (tests/test_auth.py); full suite now 115 passed.
  - `[medium]` `[patch]` Intent-alignment auditor: diff/tests implement the fix only at the service-function surface, while the intent's own motivating language ("so a ValueError never reaches... routes.py carrying bcrypt's raw internal message") anchors the claim at the client/HTTP surface, which no test in the original diff exercised — evidence: same root cause and same fix as the finding above; grouped with it. Action: same patch as above.
  - `[false]` `[reject]` Acceptance criteria phrased as "...without invoking `bcrypt.checkpw`/`bcrypt.hashpw`" aren't verified with a mock/spy — evidence: refuted — the guard unconditionally `raise`s before the bcrypt call on the same straight-line path (no branch skips it), so non-invocation is structurally guaranteed by control flow, and side-effect tests (e.g. re-authenticating with the old password after a rejected `new_password`) already confirm no mutation occurred; a mock would add complexity with no added confidence.
  - `[false]` `[reject]` No test covers precedence between the new length guard and existing identity checks (e.g. unknown user, or already-registered username, combined with an oversized password) — evidence: refuted by reading the code — `user_exists`/`user is None` checks unconditionally precede the length guard in both `register_user` (line 11 vs 14) and `authenticate_user` (line 22-23 vs 25-26), so no username-enumeration or precedence regression is introduced; behavior for those combinations is unchanged from pre-existing code.
  - `[low]` `[reject]` New guard message is phrased in bytes ("at most 72 bytes") while the sibling check is phrased in characters ("at least 8 characters"), which could confuse a user typing a multi-byte password — evidence: real but minor; the intent itself proposes this exact wording ("such as 'Password must be at most 72 bytes'"), the scenario is rare in everyday use, and unifying units would ripple across 4 guard sites and 6+ test assertions for a cosmetic nit not mandated by intent.
  - `[false]` `[reject]` Spec's `Spec Change Log` and `Review Triage Log` sections were empty despite `status: in-review` — evidence: refuted — both sections are append-only and explicitly populated during review passes per the spec template; this was the first review pass, so both were legitimately empty until this entry.

## Verification

**Commands:**
- `python -m pytest tests/unit/test_services.py tests/unit/test_services_password_change.py -v` -- expected: all tests pass, including new length-guard cases.
- `python -m pytest -q` -- expected: full suite passes with no regressions.

## Auto Run Result

**Summary:** Guarded bcrypt's 72-byte UTF-8 password limit in `src/services.py` across `register_user`, `authenticate_user`, and `change_password` (both `current_password` and `new_password`), raising a clean `ValueError("Password must be at most 72 bytes")` before every `bcrypt.hashpw`/`bcrypt.checkpw` call instead of letting bcrypt's raw internal message propagate. `routes.py`'s existing `ValueError`→4xx mapping needed no changes and now forwards the clean message unmodified. Resolves DW-1.

**Files changed:**
- `src/services.py` — added a byte-length guard immediately before each of the four `bcrypt.hashpw`/`bcrypt.checkpw` calls.
- `tests/unit/test_services.py` — added oversized/72-byte-boundary unit tests for `register_user` and `authenticate_user`.
- `tests/unit/test_services_password_change.py` — added oversized `current_password`/`new_password`, multi-byte UTF-8, and 72-byte-boundary unit tests for `change_password`.
- `tests/integration/test_password_change.py` — added `test_oversized_new_password_returns_400`, confirming `POST /change-password` returns 400 with the clean message and the old password still authenticates afterward.
- `tests/test_auth.py` — added `test_register_oversized_password_returns_400`, confirming `POST /register` returns 400 with the clean message.

**Review findings breakdown:**
- Patched (1 entry, verdict medium, 2 members): missing HTTP/integration-level verification of the client-facing behavior — fixed by adding the two integration tests above.
- Rejected (5): duplicated guard logic across 4 sites (low — matches minimalist codebase style, fix is more than a direct correction); NUL-byte leak claim (false — empirically disproved on bcrypt 5.0.0); AC "without invoking bcrypt" not mock-verified (false — structurally guaranteed by control flow, confirmed by side-effect tests); missing precedence test vs. identity checks (false — identity checks unconditionally precede the guard, no regression); message phrased in bytes vs. characters (low — intent itself proposed this exact wording, rare in everyday use); empty Spec/Review logs at time of first review (false — expected, append-only sections).
- Deferred: none.

**Follow-up review recommendation:** `false`. Only one entry was patched at `medium` (not two or more), and none was `high`, so per the first-pass rule this does not warrant another review pass. No unverified high-risk item remains to name.

**Verification performed:**
- `uv run python -m pytest tests/unit/test_services.py tests/unit/test_services_password_change.py -v` — 22 passed (pre-patch).
- `uv run python -m pytest tests/integration/test_password_change.py tests/test_auth.py -q` — 47 passed (post-patch, subagent-run).
- `uv run python -m pytest -q` (full suite) — 115 passed, no regressions (post-patch, final).

**Residual risks:** None identified. The fix is confined to `services.py` per AD-2's single-layer rule; `routes.py`, `store.py`, and all models are untouched.
