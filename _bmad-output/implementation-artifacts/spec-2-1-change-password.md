---
title: 'Change password'
type: 'feature'
created: '2026-09-15'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: false
context: []
warnings: [oversized]
deferred:
  - summary: >-
      bcrypt raises ValueError for any password over 72 bytes, and the generic
      ValueError→400 mapping in routes.py leaks that internal bcrypt message
      to the client instead of a clean error.
    evidence: |-
      Confirmed empirically: bcrypt.hashpw/checkpw both raise
      "password cannot be longer than 72 bytes, truncate manually if
      necessary (e.g. my_password[:72])" for a 100-byte password. Applies to
      both current_password (bcrypt.checkpw) and new_password
      (bcrypt.hashpw) in services.change_password, but the identical
      unguarded pattern already exists in register_user/authenticate_user
      since Epic 1 — pre-existing, cross-cutting, not introduced by this
      story.
    location: >-
      src/services.py (change_password, register_user, authenticate_user)
    severity: medium
  - summary: >-
      change_password's read-verify-write sequence on the shared in-memory
      store dict is non-atomic under concurrent requests for the same
      username.
    evidence: |-
      FastAPI runs sync route handlers in a threadpool, so two concurrent
      /change-password (or /register) calls for the same user can interleave
      between the check and the write. The identical non-atomic
      check-then-write pattern already exists in register_user
      (user_exists → add_user) — a pre-existing architectural characteristic
      of the module-level dict store, not introduced by this story.
    location: >-
      src/services.py:change_password, src/services.py:register_user
    severity: medium
  - summary: >-
      DW-1 and DW-2 in deferred-work.md are filed under the unrelated
      2026-09-07 spec-1-1 review heading instead of a new dated heading for
      this story's review, and use a different entry schema than the
      pre-existing plain-bullet entries in that file, with no migration note.
    evidence: |-
      Confirmed by reading deferred-work.md: DW-1/DW-2 (source_spec
      spec-2-1-change-password.md) sit directly under "## Deferred from:
      code review of spec-1-1-project-scaffolding-data-layer (2026-09-07)",
      and use a structured origin/location/source_spec/severity/reason/status
      schema while every other entry in the file is an unstructured bullet.
      deferred-work.md is orchestrator-owned per this run's instructions
      (never modify existing ledger entries), so build-auto cannot correct
      the misfiling or format itself.
    location: >-
      _bmad-output/implementation-artifacts/deferred-work.md
    severity: low
  - summary: >-
      sprint-status.yaml still shows epic-2 as backlog and an unbumped
      last_updated even though 2-1-change-password (epic-2's only story)
      is done.
    evidence: |-
      Confirmed by reading sprint-status.yaml: development_status has
      epic-2: backlog alongside 2-1-change-password: done, and
      last_updated is still 09-11-2026 14:30. sprint-status.yaml is
      explicitly orchestrator-owned per this run's instructions (never
      write it), so build-auto cannot correct this itself.
    location: >-
      _bmad-output/implementation-artifacts/sprint-status.yaml
    severity: low
  - summary: >-
      tests/README.md documents only test_auth.py (T-01 to T-28) and still
      lists integration/ as a placeholder, undocumented for the T-29 to
      T-49 tests this story activated.
    evidence: |-
      Confirmed by reading tests/README.md. The file is absent from this
      story's diff entirely (not in `git diff --stat` output), and it
      already omitted Epic 1's unit/test_store.py and
      unit/test_services.py before this story, so the staleness
      pre-dates this change and is not introduced by it.
    location: >-
      tests/README.md
    severity: low
baseline_revision: 'dd42065cec97b7f76e40d8175ef99e597e0aa265'
---

<intent-contract>

## Intent

**Problem:** Authenticated users have no way to change their password. `POST /change-password` does not exist, so credentials set at registration can never be updated.

**Approach:** Add a `POST /change-password` endpoint that verifies the current password against the stored bcrypt hash, then hashes and stores the new password — following the existing layered architecture (routes → services → store) and reusing the existing JWT auth dependency, bcrypt patterns, and error-shape conventions from Epic 1.

## Boundaries & Constraints

**Always:** Require a valid JWT (via the existing `get_current_user` dependency) before any password-change logic runs. Verify the current password with bcrypt before accepting a new one. Hash the new password with bcrypt before storing. Keep all bcrypt/hashing work in `services.py`; `store.py` only overwrites `password_hash` with no validation. Lowercase the username the same way other flows do. Keep the existing JWT valid after a successful change (no rotation, no invalidation). Return the consistent `{"detail": str}` error shape for all failures.

**Never:** Do not rotate, reissue, or invalidate the JWT on password change. Do not add password complexity rules beyond the 8-character minimum. Do not add rate limiting, audit logging, password history, or reset/forgot-password flows — out of scope for this story. Do not let `store.py` perform hashing or verification. Do not expose `password_hash` in any response.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Happy path | Valid JWT; correct current_password; new_password >= 8 chars | HTTP 200, `{"message": "Password changed successfully"}`; new hash stored | No error expected |
| Wrong current password | Valid JWT; incorrect current_password | HTTP 401 | `{"detail": "Invalid credentials"}` — same message as login; password unchanged |
| Weak new password | Valid JWT; correct current_password; new_password < 8 chars | HTTP 400 | `{"detail": "Password must be at least 8 characters"}`; password unchanged |
| Boundary new password | Valid JWT; new_password exactly 8 chars | HTTP 200 | No error expected |
| Missing/invalid/expired JWT | No Authorization header, or invalid/expired token | HTTP 401 | `{"detail": "..."}` via existing `get_current_user` dependency |
| Missing request fields | Valid JWT; body missing `current_password` and/or `new_password` | HTTP 400 (via existing validation handler) | `{"detail": "..."}` |
| Old password reuse after change | Password changed; login attempted with old password | HTTP 401 on `/login` | `{"detail": "Invalid credentials"}` |
| JWT reuse after change | Password changed; same pre-change JWT used on `/me` | HTTP 200, JWT still valid | No error expected |

</intent-contract>

## Code Map

- `src/routes.py` -- add `POST /change-password` handler; follows the same try/except-`ValueError`-to-`HTTPException` pattern as `login`/`register`; use `Depends(get_current_user)` like `me()`.
- `src/services.py` -- add `change_password(username, current_password, new_password) -> dict`; mirrors `authenticate_user`'s bcrypt verify (via `get_user_with_hash`) and `register_user`'s bcrypt hash pattern; raises `ValueError("Invalid credentials")` or `ValueError("Password must be at least 8 characters")`.
- `src/store.py` -- add `update_password(username, new_hash) -> None`; dumb writer, mirrors `add_user`'s dict-write style; no-op if user does not exist (mirrors `get_user`/`get_user_with_hash` returning `None` for unknown users — do not raise).
- `src/models.py` -- add `ChangePasswordRequest` (current_password: str, new_password: str) and `ChangePasswordResponse` (message: str), following `LoginRequest`/`TokenResponse` conventions.
- `src/main.py` -- read-only; existing `RequestValidationError` handler already maps missing-field 422s to `{"detail": str}` 400s, no change needed.
- `src/auth.py` -- read-only; `get_current_user` dependency reused as-is for auth gating.
- `tests/integration/test_password_change.py` -- remove `@pytest.mark.skip` and the red-phase docstring note from `TestChangePasswordEndpoint` (T-36 to T-49); tests already encode the full I/O matrix.
- `tests/unit/test_services_password_change.py` -- remove `pytest.mark.skip` from `pytestmark` (T-32 to T-35).
- `tests/unit/test_store_password_change.py` -- remove `pytest.mark.skip` from `pytestmark` (T-29 to T-31).
- `tests/conftest.py` -- read-only; `registered_user`/`auth_header`/`client` fixtures already support these tests as-is.

## Tasks & Acceptance

**Execution:**
- `src/store.py` -- add `update_password(username, new_hash)` -- store-layer primitive the service needs to persist the new hash.
- `src/services.py` -- add `change_password(username, current_password, new_password)` -- owns verify-then-hash-then-store business logic and validation ordering (auth already gated by route; verify current password before checking new-password length, so a wrong current password always wins over a weak new one).
- `src/models.py` -- add `ChangePasswordRequest`/`ChangePasswordResponse` -- typed request/response contract for the new endpoint.
- `src/routes.py` -- add `POST /change-password` -- wires auth dependency, request model, and service call into the HTTP layer; maps `ValueError` messages to 401 (`"Invalid credentials"`) or 400 (all other `ValueError`s).
- `tests/unit/test_store_password_change.py`, `tests/unit/test_services_password_change.py`, `tests/integration/test_password_change.py` -- un-skip -- flips the pre-written red-phase scaffolds to active tests (ATDD green phase).

**Acceptance Criteria:**
- Given a registered user with a valid JWT, when they POST `/change-password` with the correct current password and an 8+ char new password, then the response is HTTP 200 with `{"message": "Password changed successfully"}` and the new password authenticates on `/login` while the old one no longer does.
- Given a registered user with a valid JWT, when they POST `/change-password` with the wrong current password, then the response is HTTP 401 with `{"detail": "Invalid credentials"}` and the stored password is unchanged.
- Given a registered user with a valid JWT, when they POST `/change-password` with a new password under 8 characters, then the response is HTTP 400 with `{"detail": "Password must be at least 8 characters"}` and the stored password is unchanged.
- Given no Authorization header or an invalid/expired JWT, when a client POSTs `/change-password`, then the response is HTTP 401, regardless of body content.
- Given a successful password change, when the pre-change JWT is used on `GET /me`, then it still returns HTTP 200 (no token rotation/invalidation).

## Spec Change Log

## Review Triage Log

### 2026-09-15 — Review pass
- verdicts: 13 findings — high 0, medium 7, low 5, false 1, maybe-false 0
- findings:
  - `[medium]` `[patch]` No test verifies the stored password stays unchanged after a rejected `/change-password` request (wrong current password or weak new password) — grouped with the identical gap filed by the verification-gap layer; fixed by asserting the original password still authenticates via `/login` after each rejection test.
  - `[low]` `[patch]` No test confirms the new password actually authenticates via `/login` after a successful change — fixed by adding a follow-up `/login` call with the new password to the happy-path test.
  - `[low]` `[patch]` `test_username_case_normalization_in_change_password` never exercises mixed-case input (uses the already-lowercase `testuser` fixture), so it doesn't test normalization at all — fixed by adding a unit-level test that registers a mixed-case username and calls `services.change_password` with mixed case, mirroring `test_register_lowercases_username`.
  - `[low]` `[patch]` No test covers a user removed from the store before a `/change-password` call, even though the existing `delete_user_from_store` fixture already supports this pattern for `/me` — fixed by adding an analogous test asserting HTTP 401 `"Invalid credentials"`.
  - `[low]` `[reject]` Spec frontmatter has `warnings: [oversized]` alongside `context: []` even though `epic-2-context.md` documents relevant cross-story dependencies — the only fix is editing this build's own spec, which is excluded from patching by rule.
  - `[low]` `[reject]` No spec guidance or test coverage for resubmitting the current password as the new password — unlikely to be hit in everyday use, and the only fix (an explicit equality guard rejecting or special-casing it) is more than a direct correction, so rejected per the low-finding rule.
  - `[medium]` `[defer]` `bcrypt.checkpw`/`bcrypt.hashpw` raise `ValueError` for any password over 72 bytes, and `routes.py`'s generic `ValueError`→400 mapping would leak that internal message to the client — confirmed empirically (`hashpw`/`checkpw` on a 100-byte password both raise `"password cannot be longer than 72 bytes..."`). The identical unguarded pattern already exists in `register_user`/`authenticate_user` since Epic 1, so this is a pre-existing gap, not introduced by this story.
  - `[medium]` `[defer]` Same 72-byte bcrypt limit applies to `current_password` in `services.change_password` — grouped with the above; same pre-existing, cross-cutting root cause.
  - `[medium]` `[defer]` Same 72-byte bcrypt limit applies to `new_password` in `services.change_password` — grouped with the above; same pre-existing, cross-cutting root cause.
  - `[medium]` `[defer]` `change_password`'s read-verify-write sequence on the shared in-memory dict is non-atomic under concurrent requests for the same username (sync handlers run in FastAPI's threadpool) — real, but the identical non-atomic check-then-write pattern already exists in `register_user` (`user_exists` → `add_user`); a pre-existing architectural characteristic of the in-memory store, not introduced by this story.
  - `[false]` `[reject]` Claimed: a user deleted from the store between `get_user_with_hash` and `update_password` within one request would return a false "success" message — disproven: grep of `src/` and `tests/` shows no production code path removes users from the store; the only removal mechanism is a test-only `delete_user_from_store` fixture, so this state is unreachable via any real request.
  - `[medium]` `[patch]` No test exercises both an invalid current password and a too-short new password in the same call, so the documented "auth failures outrank input-quality failures" ordering in `change_password` could silently regress (e.g. a guard-clause reorder) without any test catching it — fixed by adding a unit test asserting the combined case still raises `"Invalid credentials"`.
  - `[medium]` `[patch]` No test confirms the store is left unchanged when a `/change-password` request is rejected — grouped with the identical gap filed by the blind-hunter layer; fixed as described there.

### 2026-09-15 — Review pass
- verdicts: 14 findings — high 0, medium 4, low 6, false 4, maybe-false 0
- findings:
  - `[low]` `[patch]` `src/routes.py` and `src/services.py` module docstrings still read "…/register, /login, /me" and "…registration, login, and user retrieval," not mentioning the new `/change-password` endpoint or `change_password` function this diff adds — fixed by updating both docstrings to mention change-password.
  - `[low]` `[defer]` DW-1 and DW-2 in `deferred-work.md` are filed under the unrelated 2026-09-07 spec-1-1 review heading instead of a new dated heading for this story, with no migration note — verified true; `deferred-work.md` is orchestrator-owned per this run's explicit instructions (never modify existing ledger entries), so build-auto cannot fix the misfiling; recorded in this spec's `deferred` frontmatter for the orchestrator instead.
  - `[low]` `[defer]` grouped with the above: DW-1/DW-2 use a new structured schema while the rest of `deferred-work.md` is plain bullets, with no format-migration note — same orchestrator-ownership constraint; recorded in `deferred` frontmatter.
  - `[low]` `[defer]` `sprint-status.yaml` still shows `epic-2: backlog` even though `2-1-change-password` — epic-2's only story — is `done` — verified true; `sprint-status.yaml` is explicitly orchestrator-owned per this run's instructions (never write it), so build-auto cannot correct it; recorded in `deferred` frontmatter for the orchestrator.
  - `[low]` `[defer]` grouped with the above: `sprint-status.yaml`'s `last_updated` (09-11-2026) was not bumped even though `development_status` changed — same orchestrator-ownership constraint; recorded in `deferred` frontmatter.
  - `[low]` `[defer]` `tests/README.md`'s architecture section still lists `integration/` as a placeholder and its Test IDs table stops at T-28, not documenting T-29–T-49 or the new test files this story activated — verified true, but `tests/README.md` is absent from this story's diff entirely and already omitted Epic 1's `unit/test_store.py`/`unit/test_services.py` before this story, so the staleness pre-dates this change; recorded in `deferred` frontmatter as pre-existing.
  - `[medium]` `[defer]` `carried` — same claim as the 2026-09-15 (prior) pass's first row: `routes.py`'s exact-string `ValueError`→401/400 mapping still echoes any other `ValueError` message verbatim as `detail`, including bcrypt's raw 72-byte message; code unchanged, already recorded in `deferred` frontmatter and `deferred-work.md` DW-1.
  - `[medium]` `[defer]` `carried` — grouped with the above; same claim as the prior pass's row for `current_password` in `services.change_password` reaching `bcrypt.checkpw` unguarded past 72 bytes; code unchanged.
  - `[medium]` `[defer]` `carried` — grouped with the above; same claim as the prior pass's row for `new_password` in `services.change_password` reaching `bcrypt.hashpw` unguarded past 72 bytes; code unchanged.
  - `[false]` `[reject]` `carried` — same claim as the prior pass's row (a user deleted from the store between `get_user_with_hash` and `update_password` within one request would return a false "success"); re-checked `src/` and `tests/`: still no production code path removes users between those two calls within a single request — the only removal mechanism remains the test-only `delete_user_from_store` fixture; disproven as before.
  - `[false]` `[reject]` Claimed: case-normalization is now proven only at the service layer (`test_change_password_lowercases_username` calls `services.change_password` directly, bypassing the route), diverging from the HTTP surface the intent's I/O matrix is framed in — disproven: `routes.py`'s `change_password_route` performs no casing logic of its own and passes `username` straight through to `change_password`, the sole locus of lowercasing; the unit test can only pass if that lowercasing matches the store's lowercased key, so the guarantee is equally proven regardless of which layer asserts it.
  - `[false]` `[reject]` Claimed: the combined wrong-current+weak-new ordering is asserted only via the service's raised message, not via `routes.py`'s HTTP status/body — disproven: `change_password_route`'s mapping is one generic rule (`"Invalid credentials"` → 401, else → 400) already exercised end-to-end by other HTTP-level tests for the "Invalid credentials" case, so a message verified at the service layer is sufficient to guarantee the HTTP outcome for the combined case too.
  - `[false]` `[reject]` Claimed: choosing `"Invalid credentials"` over `/me`'s `"User not found"` for a deleted user diverges from precedent — disproven as a defect: the intent's matrix pairs `"Invalid credentials"` with every credential-verification failure on this endpoint, and not leaking account existence on a credential-verification endpoint is the more defensible, more secure choice; no harm demonstrated.
  - `[medium]` `[defer]` `carried` — grouped with the bcrypt-72-byte entries above; restates the same already-deferred issue and notes the intent's "consistent `{"detail": str}` error shape" guarantee is technically unproven for oversized passwords — same root cause, already recorded.

## Design Notes

Validation order inside `change_password` matters: verify current password first (raises `"Invalid credentials"` on mismatch), only then check new-password length (raises `"Password must be at least 8 characters"`). This matches the spec's implicit priority (auth/identity failures outrank input-quality failures) and keeps route-layer error mapping simple: catch `ValueError`, map `"Invalid credentials"` → 401, anything else → 400.

## Verification

**Commands:**
- `pytest tests/unit/test_store_password_change.py tests/unit/test_services_password_change.py tests/integration/test_password_change.py -v` -- expected: all previously-skipped tests (T-29 to T-49) now pass.
- `pytest` -- expected: full suite passes, no regressions in Epic 1 tests.
- `ruff check src/` -- expected: no lint errors.

## Auto Run Result

Status: done (follow-up review pass)

**Summary:** This was a follow-up review pass on an already-`done` spec (per `followup_review_recommended: true`), not a new implementation. Four review layers (blind-hunter, edge-case-hunter, verification-gap, intent-alignment) ran against the full diff since `baseline_revision`. One trivial patch was applied directly (no step-03 subagent handle existed in this session); everything else was deferred, carried, or rejected on verification.

**Files changed this pass:**
- `src/routes.py` -- module docstring updated to mention `/change-password`.
- `src/services.py` -- module docstring updated to mention password change.
- `_bmad-output/implementation-artifacts/spec-2-1-change-password.md` -- status transitioned `done` → `in-review` → `done`; 3 new `deferred` frontmatter entries added; new Review Triage Log entry appended.

**Review findings breakdown (14 findings, 9 grouped entries):**
- Patched (1): stale `routes.py`/`services.py` module docstrings not mentioning the new endpoint — low severity, fixed directly.
- Deferred (4 entries, 9 rows): (1) bcrypt 72-byte limit leaking via `routes.py`'s generic `ValueError`→400 mapping, restated by 4 of this pass's findings — `carried` from the prior pass's already-open `deferred` entry and `deferred-work.md` DW-1, no new record needed; (2) `deferred-work.md` DW-1/DW-2 misfiled under the wrong dated heading and using an inconsistent schema — new finding, recorded in this spec's `deferred` frontmatter since `deferred-work.md` itself is orchestrator-owned and out of scope for build-auto to edit; (3) `sprint-status.yaml`'s `epic-2` status and `last_updated` left stale — new finding, recorded in `deferred` frontmatter since `sprint-status.yaml` is orchestrator-owned and build-auto must never write it; (4) `tests/README.md` undocumented for the new test files/IDs — new finding, recorded in `deferred` frontmatter as pre-existing (file untouched by this story's diff).
- Rejected (4, all `false`): a mid-request user-deletion race between `get_user_with_hash` and `update_password` (`carried`, still unreachable — no production deletion path exists); case-normalization tested only at the service layer (disproven — the route adds no casing logic of its own, so the unit test equally proves the guarantee); combined-failure ordering tested only at the service layer (disproven — the route's exception mapping is a single generic rule already exercised end-to-end elsewhere); the deleted-user error message diverging from `/me`'s precedent (disproven — no harm shown, and the chosen message is the more secure, defensible choice).

**Follow-up review recommendation: false.** This is a follow-up pass (`followup_pass: true`); per the convergence rule, a further pass is warranted only if this pass patched a `high`-verdict finding. Only one entry was patched, and it was `low`. Work has converged.

**Verification performed:**
- `pytest tests/unit/test_store_password_change.py tests/unit/test_services_password_change.py tests/integration/test_password_change.py -v` -- 23 passed.
- `pytest` (full suite) -- 105 passed, no regressions.
- `ruff check src/` -- all checks passed.

**Residual risks:** None newly introduced by this pass's docstring patch. Pre-existing, already-deferred risks remain open by design: bcrypt's 72-byte limit can leak an internal error message via `/change-password`, `/register`, and `/login`; and `change_password`/`register_user`'s read-verify-write sequence on the shared in-memory dict is non-atomic under concurrent requests for the same username. Newly recorded but not fixed: `deferred-work.md`'s DW-1/DW-2 misfiling/format inconsistency, `sprint-status.yaml`'s stale `epic-2`/`last_updated` fields, and `tests/README.md`'s undocumented new test files — all three are out of build-auto's scope to correct (orchestrator-owned files or pre-existing doc debt) and are left for the orchestrator/a separate documentation pass.

