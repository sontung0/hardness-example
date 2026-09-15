# Deferred Work

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
status: done 2026-09-15
resolution: already resolved: deferred-work.md now uses a uniform '### DW-<n>:' schema throughout with no legacy '## Deferred from:' headings, per commit 397d7c6 (chore(sweep): migrate legacy deferred-work entries to DW format); DW-1/DW-2 sit consistently formatted alongside every other entry.

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

### DW-6: Epic 1 heading duplicated in epics.md
origin: migrated from legacy ledger ("Deferred from: code review (2026-09-06)"), 2026-09-15
location: _bmad-output/planning-artifacts/epics.md
reason: Pre-existing planning doc issue. The summary block and the detailed section both define "Epic 1: User Authentication API" without clear delineation between the two.
status: open

### DW-7: Test design references non-existent AD-6/7/8
origin: migrated from legacy ledger ("Deferred from: code review (2026-09-06)"), 2026-09-15
location: _bmad-output/test-artifacts/test-design/test-design-architecture.md
reason: Pre-existing planning doc issue. Test design documents trace to architecture decisions (AD-6/7/8) that were never added to the architecture spine, breaking traceability.
status: done 2026-09-15
resolution: already resolved: ARCHITECTURE-SPINE.md:114,120,126 now define AD-6, AD-7, and AD-8; test-design-architecture.md:188 is the only AD-6/7/8 reference in that file (no AD-7/AD-8 references exist there to be dangling) and it correctly resolves to the now-existing AD-6.

### DW-8: `get_user_with_hash` leaks password_hash internally
origin: migrated from legacy ledger ("Deferred from: code review of spec-1-1-project-scaffolding-data-layer (2026-09-07)"), 2026-09-15
location: src/store.py:get_user_with_hash
reason: Internal-use-only function, properly scoped to callers within services.py. AD-6 wording was flagged as too broad for this design, but the function itself is not a violation.
status: open

### DW-9: Synchronous bcrypt blocks event loop
origin: migrated from legacy ledger ("Deferred from: code review of spec-1-1-project-scaffolding-data-layer (2026-09-07)"), 2026-09-15
location: src/services.py (bcrypt.hashpw/checkpw calls)
reason: Acceptable for this demo app; all routes and services are synchronous by design, so the blocking call is consistent with the rest of the stack.
status: open

### DW-10: Missing `sub`-claim-absent unit test
origin: migrated from legacy ledger ("Deferred from: code review of spec-1-1-project-scaffolding-data-layer (2026-09-07)"), 2026-09-15
location: src/auth.py:32-33
reason: Pre-existing test gap. The guard in auth.py:32-33 that rejects a token with no `sub` claim is correct, but no unit test exercises that path, so there is no regression risk currently, only missing coverage.
status: done 2026-09-15
resolution: already resolved: tests/unit/test_auth.py:152-159 (test_missing_sub_claim_raises_401) exercises a valid JWT with no 'sub' claim and asserts the 401 'Invalid token' response from auth.py:38-40.
