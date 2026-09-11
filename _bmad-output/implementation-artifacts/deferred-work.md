# Deferred Work

## Deferred from: code review (2026-09-06)

- **Epic 1 heading duplicated in epics.md** — Pre-existing planning doc issue. Summary block and detailed section both define "Epic 1: User Authentication API" without clear delineation.
- **Test design references non-existent AD-6/7/8** — Pre-existing planning doc issue. Test design documents trace to architecture decisions that were never added to the spine, breaking traceability.

## Deferred from: code review of spec-1-1-project-scaffolding-data-layer (2026-09-07)

- **`get_user_with_hash` leaks password_hash internally** — Internal-use-only function, properly scoped to services.py. AD-6 wording too broad for this design.
- **Synchronous bcrypt blocks event loop** — Acceptable for demo app; all routes and services synchronous by design.
- **Missing `sub`-claim-absent unit test** — Pre-existing test gap. Guard in auth.py:32-33 is correct; no regression risk.
