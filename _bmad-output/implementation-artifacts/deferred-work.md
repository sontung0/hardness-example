# Deferred Work

## Deferred from: code review (2026-09-06)

- **Epic 1 heading duplicated in epics.md** — Pre-existing planning doc issue. Summary block and detailed section both define "Epic 1: User Authentication API" without clear delineation.
- **Test design references non-existent AD-6/7/8** — Pre-existing planning doc issue. Test design documents trace to architecture decisions that were never added to the spine, breaking traceability.

## Deferred from: code review of spec-1-1-project-scaffolding-data-layer (2026-09-07)

- **`get_user_with_hash` leaks password_hash internally** — Internal-use-only function, properly scoped to services.py. AD-6 wording too broad for this design.
- **Synchronous bcrypt blocks event loop** — Acceptable for demo app; all routes and services synchronous by design.
- **Missing `sub`-claim-absent unit test** — Pre-existing test gap. Guard in auth.py:32-33 is correct; no regression risk.

### DW-1: bcrypt raises ValueError for any password over 72 bytes, and the generic ValueError→400 mapping in routes.py leaks that internal bcrypt message to the client instead of a clean error.
origin: spec-deferred 1f31a4e6614a
location: src/services.py (change_password, register_user, authenticate_user)
source_spec: `spec-2-1-change-password.md`
severity: medium
reason: Confirmed empirically: bcrypt.hashpw/checkpw both raise "password cannot be longer than 72 bytes, truncate manually if necessary (e.g. my_password[:72])" for a 100-byte password. Applies to both current_password (bcrypt.checkpw) and new_password (bcrypt.hashpw) in services.change_password, but the identical unguarded pattern already exists in register_user/authenticate_user since Epic 1 — pre-existing, cross-cutting, not introduced by this story.
status: open

### DW-2: change_password's read-verify-write sequence on the shared in-memory store dict is non-atomic under concurrent requests for the same username.
origin: spec-deferred 92e885e07f15
location: src/services.py:change_password, src/services.py:register_user
source_spec: `spec-2-1-change-password.md`
severity: medium
reason: FastAPI runs sync route handlers in a threadpool, so two concurrent /change-password (or /register) calls for the same user can interleave between the check and the write. The identical non-atomic check-then-write pattern already exists in register_user (user_exists → add_user) — a pre-existing architectural characteristic of the module-level dict store, not introduced by this story.
status: open

### DW-3: DW-1 and DW-2 in deferred-work.md are filed under the unrelated 2026-09-07 spec-1-1 review heading instead of a new dated heading for this story's review, and use a different entry schema than the
origin: spec-deferred b05e3012e9cb
location: _bmad-output/implementation-artifacts/deferred-work.md
source_spec: `spec-2-1-change-password.md`
severity: low
reason: Confirmed by reading deferred-work.md: DW-1/DW-2 (source_spec spec-2-1-change-password.md) sit directly under "## Deferred from: code review of spec-1-1-project-scaffolding-data-layer (2026-09-07)", and use a structured origin/location/source_spec/severity/reason/status schema while every other entry in the file is an unstructured bullet. deferred-work.md is orchestrator-owned per this run's instructions (never modify existing ledger entries), so build-auto cannot correct the misfiling or format itself.
status: open

### DW-4: sprint-status.yaml still shows epic-2 as backlog and an unbumped last_updated even though 2-1-change-password (epic-2's only story) is done.
origin: spec-deferred 187fd30f7b0a
location: _bmad-output/implementation-artifacts/sprint-status.yaml
source_spec: `spec-2-1-change-password.md`
severity: low
reason: Confirmed by reading sprint-status.yaml: development_status has epic-2: backlog alongside 2-1-change-password: done, and last_updated is still 09-11-2026 14:30. sprint-status.yaml is explicitly orchestrator-owned per this run's instructions (never write it), so build-auto cannot correct this itself.
status: open

### DW-5: tests/README.md documents only test_auth.py (T-01 to T-28) and still lists integration/ as a placeholder, undocumented for the T-29 to T-49 tests this story activated.
origin: spec-deferred 91b58c4ad64e
location: tests/README.md
source_spec: `spec-2-1-change-password.md`
severity: low
reason: Confirmed by reading tests/README.md. The file is absent from this story's diff entirely (not in `git diff --stat` output), and it already omitted Epic 1's unit/test_store.py and unit/test_services.py before this story, so the staleness pre-dates this change and is not introduced by it.
status: open
