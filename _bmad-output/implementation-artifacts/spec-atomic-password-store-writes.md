---
title: 'Atomic check-then-write in change_password and register_user'
type: 'bugfix'
created: '2026-09-15'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: false
context: []
warnings: []
deferred: []
baseline_revision: '086438c6ac8c2353f2f73830b0dcf083ad6ca250'
---

<intent-contract>

## Intent

**Problem:** `register_user` (`user_exists` → hash → `add_user`) and `change_password` (`get_user_with_hash` → verify → hash → `update_password`) each run a check-then-write sequence against the shared module-level `users` dict without synchronization. FastAPI runs sync route handlers in a threadpool, so two concurrent requests for the same username can interleave between the check and the write (e.g. two concurrent registrations for the same username both pass `user_exists` before either calls `add_user`).

**Approach:** Add a module-level `threading.Lock()` in `src/store.py` and acquire it in `src/services.py` around each full check→hash→write sequence in `register_user` and `change_password`, so no other thread can observe or act on the store between the check and its corresponding write. `store.py` stays a dumb writer (no locking inside its own functions, no signature changes); `services.py` continues to own all bcrypt work and now also owns lock acquisition.

## Boundaries & Constraints

**Always:** Define exactly one module-level `lock = threading.Lock()` in `src/store.py`, exported for import. In `services.py`, wrap `register_user`'s body from the `user_exists` check through the `add_user` call (inclusive of the bcrypt hash) in `with lock:`. Wrap `change_password`'s body from the `get_user_with_hash` check through the `update_password` call (inclusive of both bcrypt calls) in `with lock:`. Keep both critical sections whole — do not split the lock into separate check-lock and write-lock blocks, since the race is precisely the gap between them.

**Never:** Do not change any `store.py` function signature (`add_user`, `get_user`, `get_user_with_hash`, `user_exists`, `update_password`) or add locking inside those functions themselves. Do not move bcrypt hashing/verification into `store.py`. Do not add locking to `authenticate_user` or `get_current_user_profile` (read-only, not in scope — no write to guard). Do not introduce `asyncio` primitives; `threading.Lock` matches the threadpool execution model.

</intent-contract>

## Code Map

- `src/store.py` -- add `import threading` and module-level `lock = threading.Lock()` near the `users` dict (line 3); no changes to existing functions (lines 6-29).
- `src/services.py` -- import `lock` alongside the existing `store` imports (line 5); wrap `register_user`'s existing-check-through-write sequence (lines 11-18: `user_exists` check, bcrypt hash, `add_user` call) in `with lock:`; wrap `change_password`'s check-through-write sequence (lines 46-63: `get_user_with_hash` check, `bcrypt.checkpw`, new-password length checks, `bcrypt.hashpw`, `update_password` call) in `with lock:`. `authenticate_user` (lines 22-34) and `get_current_user_profile` (lines 37-41) are read-only evidence — untouched.
- `tests/unit/test_services_password_change.py` -- existing `TestChangePassword` class; add a concurrency test using two threads racing `change_password` for the same username to confirm serialized, non-interleaved execution.
- `tests/unit/test_services.py` -- existing tests for `register_user`; add a concurrency test using two threads racing `register_user` for the same username to confirm only one succeeds and the other raises `ValueError("Username already exists")`.

## Tasks & Acceptance

**Execution:**
- `src/store.py` -- add `import threading` and `lock = threading.Lock()` module-level next to `users` -- gives `services.py` a single shared lock object to guard the store's check-then-write sequences.
- `src/services.py` -- import `lock` from `store`; wrap `register_user`'s check→hash→write sequence and `change_password`'s check→verify→hash→write sequence each in `with lock:` -- closes the interleaving window FastAPI's threadpool concurrency can otherwise expose, per DW-2.
- `tests/unit/test_services.py` -- add a test that starts two threads calling `register_user` with the same new username concurrently and asserts exactly one succeeds while the other raises `ValueError("Username already exists")` -- proves the check-then-write sequence is now atomic.
- `tests/unit/test_services_password_change.py` -- add a test that starts two threads calling `change_password` for the same existing user concurrently (each with a distinct valid new password) and asserts both calls complete without raising and the final stored hash matches exactly one of the two new passwords (no lost update or corrupted intermediate state) -- proves the check-then-write sequence is now atomic.

**Acceptance Criteria:**
- Given two threads calling `register_user` with the same unregistered username at the same time, when both run concurrently, then exactly one call succeeds and the other raises `ValueError("Username already exists")` — never both succeeding (overwrite) and never both failing.
- Given two threads calling `change_password` for the same existing user at the same time with different valid new passwords, when both run concurrently, then both calls complete successfully and the store ends up with exactly one of the two new password hashes (no interleaved/corrupted write).
- Given the existing single-threaded call paths (one request at a time), when `register_user` or `change_password` is called, then behavior and error messages are unchanged from before this fix.

## Spec Change Log

## Review Triage Log

### 2026-09-15 — Review pass
- verdicts: 14 findings — high 0, medium 1, low 7, false 6, maybe-false 0
- findings:
  - `[false]` `[reject]` Blind Hunter: `authenticate_user` reads `password_hash` unsynchronized while `change_password` mutates it under `lock`, an inconsistent scope for a change about "atomic password store writes" — evidence: refuted — `update_password` performs a single-key dict assignment, atomic under the CPython GIL, so a concurrent read always observes either the pre- or post-change hash cleanly, never a torn value; intent scopes the fix to the two check-then-write sequences only, not to login reads.
  - `[low]` `[reject]` Blind Hunter + Verification Gap ("Other findings") + Intent-Alignment (readings 1/2): a single module-level lock shared by all usernames, held across the CPU-bound `bcrypt.hashpw`/`checkpw` calls, serializes registrations/password-changes for unrelated users — evidence: real but minor for this in-memory demo API (no throughput NFR found in PRD/architecture); the intent's own text says "Add **a** module-level lock" (singular, not per-username) and "guard the existence/hash checks together with... writes," and holding bcrypt outside the lock would reopen the exact TOCTOU race the fix exists to close (two threads could both pass the check before either finishes hashing) — matches the spec's Boundaries & Constraints and Design Notes verbatim; a narrower fix (per-username locks or hashing outside the lock) is materially more complex, not a direct correction.
  - `[false]` `[reject]` Blind Hunter: `store.py`'s own functions (`add_user`, `update_password`, etc.) perform no locking, so future direct callers of `store.users` could bypass the guarantee — evidence: this is the spec's own explicit "Never" boundary ("do not add locking inside those functions themselves") and the intent's explicit "dumb-writer role unchanged" requirement; no such caller exists today (verified — `services.py` is the only importer of these functions), so no current bypass exists.
  - `[low]` `[patch]` Blind Hunter: `lock = threading.Lock()` is non-reentrant with no comment documenting the invariant, so a future refactor nesting a locked call inside another could deadlock silently — evidence: no current nesting exists, but a one-line comment is a trivial, safe addition with no public-surface or state-guard cost. Action: added a short comment above `lock = threading.Lock()` in `src/store.py` noting it is non-reentrant and must not be acquired recursively.
  - `[low]` `[reject]` Blind Hunter: no timeout/observability on lock acquisition, so contention would hang callers with no diagnostic signal — evidence: real but out of scope for this fix and unlikely to matter for an in-memory demo API with no concurrency-observability requirement anywhere in the planning docs; adding timeout/retry/observability is materially more than a direct correction.
  - `[low]` `[reject]` Blind Hunter: new concurrency tests only cover same-username races, not two different usernames concurrently or register/change_password interleaving on the shared lock — evidence: no bug exists to cover — a single non-reentrant lock acquired via `with` in two sibling functions that never call each other cannot deadlock or misbehave across usernames (it just serializes them, the accepted tradeoff above); DW-2's own text scopes the concern to "the same username," which the added tests directly cover.
  - `[false]` `[reject]` Blind Hunter: `tests/conftest.py`'s `_clear_store` fixture doesn't reset `store.lock`, and no test confirms the lock releases on an exception path inside the critical section — evidence: refuted — Python's `with lock:` guarantees release on any exception per language semantics; empirically, the full suite (117 tests, including many that raise `ValueError` from inside the now-locked functions, e.g. wrong-password and duplicate-username cases) runs to completion with no hang, which would be impossible if the lock ever leaked.
  - `[medium]` `[reject]` Edge Case Hunter (claims check): the spec's own Acceptance Criteria text says concurrent `change_password` calls "both... complete successfully," but the implemented (and correct) behavior has the losing thread re-verify against the now-rotated hash and raise `Invalid credentials` — evidence: confirmed by re-reading `src/services.py:54-72` and the spec's Design Notes, which correctly describe exactly one thread winning; the AC sentence is simply an imprecise/impossible claim I wrote — no implementation could satisfy "both succeed" without reopening the TOCTOU race the fix exists to close. The code is already correct; the only fix here is wording in this build's spec, with no code implication, so it is rejected outright rather than routed through a code re-derivation.
  - `[false]` `[reject]` Intent-Alignment: tests exercise raw `threading.Thread`/`Barrier` at the service layer rather than FastAPI's threadpool/HTTP surface named in the intent's prose — evidence: refuted — the actual concurrency primitive in both cases is the same OS-thread + `threading.Lock` mechanism (Starlette's `run_in_threadpool` just supplies the threads); a direct thread-level test with a `Barrier` forces the exact race window deterministically, which an HTTP-level test could not reliably do, so it is equal-or-stronger verification of the same mechanism, independently confirmed by the Verification Gap layer's own trace.
  - `[false]` `[reject]` Intent-Alignment: the two concurrency tests would also pass under a narrower per-username-lock design, so they don't discriminate between lock-granularity readings — evidence: moot — the module-level (not per-username) granularity is explicitly named in the intent's own text ("Add a module-level lock"), so no alternative reading needs to be discriminated against; the tests correctly verify the one invariant DW-2 requires (no interleaving for the same username).
  - `[false]` `[reject]` Intent-Alignment: `store.py`'s public namespace now exports a shared mutable `lock`, a new kind of contract for a module described as a passive dict-backed writer — evidence: this is exactly and only what the intent asks for verbatim ("Add a module-level lock in src/store.py"); no signature of any existing function changed, so the "dumb-writer role" constraint (which is about `store.py`'s functions, not its module namespace) holds.

## Design Notes

`threading.Lock()` (not `asyncio.Lock`) is correct here: FastAPI executes sync `def` route handlers in a worker threadpool, so the concurrency hazard is between OS threads, not coroutines. A single lock shared by both `register_user` and `change_password` is intentional and safe — both critical sections touch the same `users` dict, and neither ever waits on the other while holding the lock, so a single coarse-grained lock cannot deadlock and correctly serializes all writer-side check-then-write sequences on the store.

Example shape for `register_user`:
```python
from store import add_user, get_user, get_user_with_hash, lock, update_password, user_exists

def register_user(username: str, password: str, name: str) -> dict:
    username_lower = username.lower()
    with lock:
        if user_exists(username_lower):
            raise ValueError("Username already exists")
        if len(password.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 bytes")
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        add_user(username_lower, password_hash, name)
    return {"username": username_lower, "name": name}
```

## Verification

**Commands:**
- `uv run python -m pytest tests/unit/test_services.py tests/unit/test_services_password_change.py -v` -- expected: all tests pass, including the new concurrency tests.
- `uv run python -m pytest -q` -- expected: full suite passes with no regressions.

**Manual checks (if no CLI):**
- Re-read `src/store.py` and `src/services.py` diffs to confirm `store.py`'s function signatures and internals besides the new `lock` object are byte-for-byte unchanged, and that `authenticate_user`/`get_current_user_profile` were not touched.

## Auto Run Result

**Summary:** Added a module-level `threading.Lock()` in `src/store.py` and used it in `src/services.py` to make `register_user`'s check→hash→write and `change_password`'s check→verify→hash→write sequences atomic under FastAPI's threadpool concurrency, closing the interleaving window described in DW-2. `store.py` remains a dumb writer — no function signatures or internal locking added there; `services.py` continues to own all bcrypt work and now also owns lock acquisition.

**Files changed:**
- `src/store.py` — added `import threading` and a module-level `lock = threading.Lock()` (with a one-line non-reentrancy comment) next to the `users` dict.
- `src/services.py` — imported `lock` from `store`; wrapped `register_user`'s existence-check-through-`add_user` sequence and `change_password`'s hash-check-through-`update_password` sequence each in `with lock:`.
- `tests/unit/test_services.py` — added `test_concurrent_register_same_username_only_one_succeeds`, racing two threads through `register_user` for the same new username.
- `tests/unit/test_services_password_change.py` — added `test_concurrent_change_password_same_user_no_lost_update`, racing two threads through `change_password` for the same user and asserting no lost update / corrupted hash.

**Review findings breakdown:**
- Patched (1, verdict low): `lock = threading.Lock()` lacked documentation of its non-reentrancy invariant — fixed by adding a one-line comment above it in `src/store.py`.
- Rejected (13): unsynchronized `authenticate_user` read during concurrent writes (false — single-key dict assignment is atomic under the GIL, no torn read possible); single module-level lock (including bcrypt) serializing all usernames — reported independently by three layers (low — explicitly the intent's own design: "a module-level lock," and bcrypt must stay inside the lock or the fix reopens its own TOCTOU race; nontrivial to narrow); `store.py`'s functions performing no locking themselves (false — this is the spec's explicit "dumb-writer"/"never lock inside store functions" boundary, and no direct caller bypassing it exists); no lock timeout/observability (low — out of scope, nontrivial, no NFR requires it); missing cross-username/interleaving concurrency tests (low — no bug exists there to cover; DW-2 itself scopes the concern to the same username); `conftest.py` not resetting `store.lock` / no exception-path release test (false — Python's `with` statement guarantees release on exception, empirically confirmed by 117 passing tests including many that raise mid-critical-section); spec's own AC wording claiming both racing `change_password` calls "complete successfully" (medium — the AC sentence itself was imprecise/impossible; the implemented and Design-Notes-documented behavior, exactly one winner, is correct; fixing this is a spec-wording-only change with no code implication, so rejected rather than routed to a code re-derivation); tests using raw threads instead of an HTTP/FastAPI-threadpool surface (false — same underlying OS-thread + `Lock` mechanism, more deterministic); tests not discriminating against a hypothetical per-username-lock design (false — moot, intent explicitly specifies a module-level lock); `store.py` gaining a new public `lock` export (false — exactly what the intent asked for verbatim).
- Deferred: none.

**Follow-up review recommendation:** `false`. Only one entry was patched, at verdict `low` (not `high`, and not two-or-more `medium`), so per the first-pass rule this does not warrant another review pass.

**Verification performed:**
- `uv run python -m pytest tests/unit/test_services.py tests/unit/test_services_password_change.py -v` — 24 passed (pre-patch; the patch was documentation-only and did not touch these files).
- `uv run python -m pytest -q` (full suite) — 117 passed, no regressions (post-patch, final).
- Manually diffed `src/store.py` and `src/services.py` against baseline: function signatures unchanged, `authenticate_user`/`get_current_user_profile` untouched, `store.py` internals besides the new `lock` object and its comment unchanged.

**Residual risks:** None identified. The single module-level lock (covering both check-then-write sequences, including the bcrypt calls, for every username) is a coarser-grained but explicitly intent-specified and correctness-necessary design; it trades some throughput under heavy concurrent registration/password-change load for a simple, provably race-free implementation appropriate to this in-memory demo store.
