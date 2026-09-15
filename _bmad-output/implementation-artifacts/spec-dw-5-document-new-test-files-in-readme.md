---
title: 'Document password-change test files in tests/README.md'
type: 'chore'
created: '2026-09-15'
status: 'done'
baseline_revision: 'ac60de4cfbe2a2c41c4fe0440b2bc337cd7b40ad'
review_loop_iteration: 0
followup_review_recommended: false
context: []
warnings: []
deferred:
  - summary: >-
      tests/README.md's Architecture tree and Test IDs section still omit
      tests/unit/test_auth.py (unit tests for JWT creation/decoding/auth
      dependency) and tests/unit/test_structure.py (AR-1/AR-2/AR-5
      structural tests), and the "Best Practices → Markers" bullet omits
      the `structural` pytest marker registered in pyproject.toml and used
      by test_structure.py.
    evidence: |-
      Verified both files exist on disk and are absent from the README's
      Architecture tree and Test IDs section, both before and after this
      diff. DW-5's ledger entry and bundle intent name five specific files
      to add (the three T-29-T-49 files plus Epic 1's test_store.py and
      test_services.py); neither test_auth.py's unit-test twin nor
      test_structure.py is named, so this pre-existing gap is not within
      this story's named scope, though it is real under the bundle
      intent's broader "accurately reflects the current tests/ directory
      structure" phrasing. The `structural` marker (pyproject.toml line 33)
      predates this change and is likewise outside the Architecture
      tree/Test IDs scope this ledger entry names.
    location: >-
      tests/README.md (Architecture tree, Test IDs section, and Best
      Practices → Markers bullet)
    severity: low
---

<intent-contract>

## Intent

**Problem:** `tests/README.md`'s Architecture tree and Test IDs section only document `test_auth.py` (T-01 to T-28) and still show `integration/` as a placeholder and omit `unit/test_store.py` / `unit/test_services.py`, even though the codebase now has `tests/unit/test_store_password_change.py`, `tests/unit/test_services_password_change.py`, and `tests/integration/test_password_change.py` (T-29 to T-49) fully implemented.

**Approach:** Update the Architecture tree to list all current `unit/` and `integration/` test files (including the two previously-omitted Epic 1 files), and add a Test IDs entry describing the T-29–T-49 range, mirroring the existing `test_auth.py` entry's style.

## Boundaries & Constraints

**Always:** Keep this a documentation-only change to `tests/README.md`. Reuse the existing tree/table formatting conventions already in the file (aligned `#` comments in the tree, bullet-list ranges in Test IDs). Only describe files that currently exist under `tests/`.

**Never:** Do not modify any test file, source file, or other doc. Do not touch the `api/` placeholder line (out of scope — no `api/` tests exist yet). Do not add `tests/unit/test_structure.py` (out of scope for this ledger entry — DW-5 only names `test_store.py`, `test_services.py`, `test_store_password_change.py`, `test_services_password_change.py`, and `test_password_change.py`).

</intent-contract>

## Code Map

- `tests/README.md` (lines 32–51) -- Architecture tree. `unit/` block (lines 36–38) lists only `test_store.py`/`test_services.py`; `integration/` (line 39) is a one-line placeholder comment. Both need updating to reflect the current directory contents.
- `tests/README.md` (lines 83–91) -- "Test IDs" section. Only documents `test_auth.py` (T-01 to T-28) against `test-design-qa.md`; needs a new entry for the password-change files against `test-design-epic-2.md`.
- `tests/unit/test_store_password_change.py` (docstring line 12) -- `"""T-29, T-30, T-31: Store-level password update operations."""`
- `tests/unit/test_services_password_change.py` (docstring line 14, plus line 45) -- `"""T-32, T-33, T-34, T-35: Service-level password change logic."""`; a separate test at line 45 covers T-46 (`"""T-46: Username is lowercased during change-password flow."""`).
- `tests/integration/test_password_change.py` (docstring line 8) -- `"""T-36 to T-49: API-level password change tests."""` (T-46 is not in this file — it lives in `test_services_password_change.py` per above).
- `_bmad-output/test-artifacts/test-design/test-design-epic-2.md` (lines 116–154) -- authoritative T-29–T-49 coverage matrix; confirms the T-29/T-32/T-36 groupings and that T-46 is the one integration-numbered ID implemented as a unit test.
- `tests/unit/test_store.py`, `tests/unit/test_services.py` -- existing Epic 1 unit test files, already on disk, currently missing from the Architecture tree per the ledger's note (pre-existing gap, in scope for this fix per the bundle intent).

## Tasks & Acceptance

**Execution:**
- `tests/README.md` -- In the Architecture tree, under `unit/`, keep `test_store.py` and `test_services.py` and add `test_store_password_change.py` and `test_services_password_change.py` with short descriptive comments; replace the `integration/  # Integration tests (placeholder)` line with `integration/` containing `test_password_change.py` and its comment -- makes the tree match the actual `tests/unit/` and `tests/integration/` contents.
- `tests/README.md` -- In the "Test IDs" section, add a new bullet list (after the existing `test_auth.py` one) mapping `test_store_password_change.py` / `test_services_password_change.py` / `integration/test_password_change.py` to `test-design-epic-2.md`, with ranges T-29 to T-31 (store), T-32 to T-35 + T-46 (services), and T-36 to T-45 + T-47 to T-49 (integration) -- documents the new test IDs using the same range-listing convention as the existing entry.

**Acceptance Criteria:**
- Given `tests/README.md`'s Architecture tree, when read, then it lists `test_store_password_change.py`, `test_services_password_change.py` (under `unit/`) and `test_password_change.py` (under `integration/`), and no longer describes `integration/` as a placeholder.
- Given `tests/README.md`'s Test IDs section, when read, then it documents that T-29 to T-49 map to the password-change test files, consistent with the docstrings in those files and with `test-design-epic-2.md`.
- Given the diff, when reviewed, then it touches only `tests/README.md` and does not add `test_structure.py` or modify the `api/` placeholder line.

## Spec Change Log

## Review Triage Log

### 2026-09-15 — Review pass
- verdicts: 10 findings — high 0, medium 0, low 8, false 2, maybe-false 0
- findings:
  - `[low]` `[patch]` Architecture tree comment columns no longer align across sibling blocks (`unit/` items align at a different column than `integration/` and `api/` lines) — the whole tree was uniformly column-aligned before this diff; smallest fix is to re-align the `#` comments to a single column across the tree.
  - `[low]` `[defer]` (grouped) `tests/unit/test_structure.py` (AR-1/AR-2/AR-5 structural tests) remains undocumented in the Architecture tree and Test IDs section — pre-existing gap, not named in DW-5's ledger entry or bundle intent (which lists five specific files), so out of this story's named scope.
  - `[low]` `[defer]` Best Practices → Markers bullet still lists only `unit`/`integration`/`api`/`slow`, omitting the `structural` marker registered in `pyproject.toml` and used by `test_structure.py` — pre-existing, unrelated section of the file, not part of DW-5's named scope (Architecture tree + Test IDs).
  - `[low]` `[reject]` Missing an example `pytest tests/integration/` command in "Running Tests" — not worth adding: the existing generic `pytest tests/` and `pytest tests/unit/` examples already establish the pattern, and this is a nice-to-have beyond the intent's named scope (Architecture tree + Test IDs), not a documentation inaccuracy.
  - `[false]` `[reject]` Claimed ambiguous/inconsistent treatment between `api/` and `integration/` placeholder labels — refuted: `tests/api/` still contains only `__init__.py`, so its "(placeholder)" label remains accurate; no inconsistency introduced.
  - `[low]` `[reject]` Test IDs section doesn't state a total test count or a story/epic cross-link — stylistic suggestion with no named inaccuracy; the existing `test_auth.py` entry doesn't do this either, so no inconsistency was introduced, and it isn't required by the intent.
  - `[false]` `[reject]` Claimed inconsistent phrasing between the tree comment ("password update in store") and the Test IDs bullet ("password update operations") for `test_store_password_change.py` — refuted: this mirrors the file's existing convention (the `test_auth.py` tree comment and its Test IDs prose already use different wording for the same file without being treated as an error).
  - `[low]` `[defer]` (grouped) `tests/unit/test_auth.py` (unit tests for JWT creation/decoding/auth dependency) exists but is omitted from the Architecture tree entirely — pre-existing gap, not named in DW-5's ledger entry or bundle intent, so out of this story's named scope.
  - `[low]` `[defer]` (grouped) Under the bundle intent's broader "accurately reflects the current tests/ directory structure" language, `tests/unit/test_auth.py` and `tests/unit/test_structure.py` remain undocumented — the diff implements the narrower reading (the five explicitly-named files), which the ledger's own causal framing (files "this story activated" plus two explicitly-named Epic 1 omissions) supports over the broader reading; not re-litigated here.
  - `[low]` `[patch]` The Architecture tree's comment on `integration/test_password_change.py` says "(T-36 to T-49)" though T-46 of that range is actually implemented in `test_services_password_change.py`, not this file (per the Test IDs section directly below, which correctly excludes it) — smallest fix is to change the tree comment to the precise range, matching the breakdown already present in the Test IDs section.

## Design Notes

Match the existing tree's comment-alignment style (comments roughly column-aligned within each block) and the existing Test IDs bullet style (`- T-XX to T-YY: description`), e.g.:

```
├── unit/
│   ├── test_store.py                    # Unit tests for in-memory store
│   ├── test_services.py                 # Unit tests for business logic
│   ├── test_store_password_change.py    # Unit tests for password update in store (T-29 to T-31)
│   └── test_services_password_change.py # Unit tests for password change service logic (T-32 to T-35, T-46)
├── integration/
│   └── test_password_change.py    # API-level password change tests (T-36 to T-49)
```

## Verification

**Manual checks (if no CLI):**
- `grep -n "test_store_password_change\|test_services_password_change\|test_password_change" tests/README.md` -- each of the three files appears in the Architecture tree.
- `grep -n "placeholder" tests/README.md` -- `integration/` no longer appears next to "placeholder" (only `api/` should remain, if anything).
- Confirm `git diff --stat` shows only `tests/README.md` changed.

## Auto Run Result

**Summary of implemented change:** In `tests/README.md`, updated the Architecture tree to list `test_store_password_change.py` and `test_services_password_change.py` under `unit/` (alongside the pre-existing `test_store.py`/`test_services.py`), and replaced the stale `integration/ (placeholder)` line with a real entry for `test_password_change.py`. Added a new "Test IDs" block mapping T-29 to T-49 (store/services/integration password-change tests) to `test-design-epic-2.md`, mirroring the existing `test_auth.py` entry's style. A review pass then patched two cosmetic/accuracy issues: re-aligned the tree's `#` comment columns, and corrected the `integration/test_password_change.py` tree comment from an over-broad "(T-36 to T-49)" to the precise "(T-36 to T-45, T-47 to T-49)" (T-46 lives in the services file, not this one).

**Files changed:**
- `tests/README.md` -- Architecture tree (`unit/`/`integration/` blocks) and "Test IDs" section updated to document the three new password-change test files plus the two previously-omitted Epic 1 unit files; no other lines touched.

**Review findings breakdown:**
- Patches applied: 2 (both low) — re-aligned Architecture-tree comment columns across the `unit/`/`integration/`/`api/` blocks; corrected the `integration/test_password_change.py` tree comment's T-ID range to exclude T-46.
- Items deferred: 1 (low, covering 3 related findings) — `tests/unit/test_auth.py` and `tests/unit/test_structure.py` remain undocumented in the Architecture tree/Test IDs section, and the Best Practices → Markers bullet omits the `structural` marker; all pre-existing, not named in DW-5's ledger entry or bundle intent, so out of this story's scope. Recorded in frontmatter `deferred`.
- Rejected findings (4):
  - Missing an example `pytest tests/integration/` command in "Running Tests" — rejected as low: not required by intent, and the existing generic examples already establish the pattern.
  - Claimed ambiguous/inconsistent treatment of `api/` vs `integration/` placeholder labels — refuted: `tests/api/` still contains only `__init__.py`, so its "(placeholder)" label remains accurate.
  - Test IDs section lacks a total test count or story/epic cross-link — rejected as low: stylistic suggestion, no inaccuracy, and the existing `test_auth.py` entry doesn't do this either.
  - Claimed inconsistent phrasing between the tree comment and Test IDs bullet for `test_store_password_change.py` — refuted: matches the file's existing convention (the `test_auth.py` tree comment and its Test IDs prose already differ in wording without being an error).

**Follow-up review recommendation:** `false` — both patched entries this pass were `low` (0 high, 0 medium patched), so the work has converged; nothing further to re-verify.

**Verification performed:**
- `grep -n "test_store_password_change\|test_services_password_change\|test_password_change" tests/README.md` → all three files appear in the Architecture tree.
- `grep -n "placeholder" tests/README.md` → only `api/` remains labeled "(placeholder)"; `integration/` no longer is.
- `git diff --stat` (against baseline `ac60de4`) → only `tests/README.md` changed (16 lines: 12 insertions, 4 deletions).
- Cross-checked the new Test IDs ranges (T-29–T-31, T-32–T-35 + T-46, T-36–T-45 + T-47–T-49) against the docstrings in `tests/unit/test_store_password_change.py`, `tests/unit/test_services_password_change.py`, and `tests/integration/test_password_change.py`, and against `_bmad-output/test-artifacts/test-design/test-design-epic-2.md`'s coverage matrix — all consistent.
- Four review layers (blind-hunter, edge-case-hunter, verification-gap, intent-alignment) run in parallel against the diff; verification-gap reported no gaps (documentation-only, non-behavioral change with no test surface).

**Residual risks:** None beyond the deferred, pre-existing documentation gaps above (unit `test_auth.py`, `test_structure.py`, and the `structural` marker); this is a documentation-only, non-behavioral change.
