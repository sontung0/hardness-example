---
title: 'Fix duplicate Epic 1 heading in epics.md'
type: 'chore'
created: '2026-09-15'
status: 'done'
baseline_revision: 'ec429b4edef742fd1efca8c6a8bb6aaf6d1f2d36'
review_loop_iteration: 0
followup_review_recommended: false
context: []
warnings: []
deferred:
  - summary: >-
      The epic description sentence is duplicated verbatim between the Epic
      List table's Summary column and the detailed Epic section paragraph
      below it.
    evidence: |-
      Pre-existing duplication, not introduced by this change: the same
      sentence appeared in both the old summary heading block and the
      detailed section before this diff, and still appears in both places
      (now the table cell and the detail paragraph) after it. DW-6 scoped
      only the duplicate *headings*, not duplicate *prose*, so fixing this
      is out of this story's scope; future edits to an epic's description
      risk drifting out of sync between the two locations.
    location: >-
      _bmad-output/planning-artifacts/epics.md (Epic List table Summary
      column vs. Epic N section intro paragraph)
    severity: low
---

<intent-contract>

## Intent

**Problem:** In `_bmad-output/planning-artifacts/epics.md`, the "## Epic List" section (line 83) and the detailed epic section (line 99) both use the identical heading text "Epic 1: User Authentication API" (and identically "Epic 2: Password Management" at lines 91/187), so a reader jumping via heading/TOC cannot tell the summary entry from the full section.

**Approach:** Convert the per-epic summary blocks inside "## Epic List" from headings into a table (reusing the tabular convention already established by the "FR Coverage Map" table earlier in the same document), so the summary no longer repeats the detailed section's heading text/level. The detailed "## Epic N: ..." sections lower in the document are untouched.

## Boundaries & Constraints

**Always:** Preserve every fact currently in the Epic List summaries (epic number, title, one-line description, FRs/NFRs/ARs covered) — this is a pure restructuring, not a content change. Keep the detailed `## Epic 1: ...` / `## Epic 2: ...` sections and everything under them exactly as-is.

**Never:** Do not rename, renumber, or reword the epics. Do not touch anything outside the `## Epic List` section (lines 81–97) of `epics.md`. Do not turn the detailed sections into anything other than `##` headings.

</intent-contract>

## Code Map

- `_bmad-output/planning-artifacts/epics.md` (lines 81–97) -- the `## Epic List` section to restructure. Contains two summary blocks:
  - Line 83 `### Epic 1: User Authentication API`, description line 85, `**FRs covered:**`/`**NFRs covered:**`/`**ARs covered:**` lines 87–89.
  - Line 91 `### Epic 2: Password Management`, description line 93, coverage lines 95–97.
- `_bmad-output/planning-artifacts/epics.md` (line 53) -- `### FR Coverage Map` table: the existing tabular convention in this doc to reuse for the new Epic List table (pipe-table, header row, `|---|---|` separator row).
- `_bmad-output/planning-artifacts/epics.md` (line 99, line 187) -- detailed `## Epic 1: User Authentication API` and `## Epic 2: Password Management` sections. Read-only: do not modify; these keep their `##` heading text unchanged, since after the fix they become the sole location using that exact heading text/level.

## Tasks & Acceptance

**Execution:**
- `_bmad-output/planning-artifacts/epics.md` -- Replace the two `### Epic N: ...` summary blocks under `## Epic List` (lines 83–97) with a single markdown table with columns `Epic | Title | Summary | FRs | NFRs | ARs`, one row per epic, preserving the existing text content (title, description sentence, FR/NFR/AR lists) verbatim -- removes the duplicate heading text/level while keeping the summary informative and scannable, consistent with the doc's existing `FR Coverage Map` table style.

**Acceptance Criteria:**
- Given `epics.md`, when searching for the literal heading `## Epic 1: User Authentication API` or `# Epic 1: User Authentication API` (any `#`-level heading with that exact text), then it appears exactly once in the whole file (in the detailed section), not twice.
- Given `epics.md`, when searching for `## Epic 2: Password Management` as a heading, then it likewise appears exactly once (in the detailed section).
- Given the `## Epic List` section, when read, then it still conveys, for each epic, the title, one-line summary, and FRs/NFRs/ARs covered, now as table rows instead of headings.
- Given the detailed `## Epic 1: ...` / `## Epic 2: ...` sections and everything below them (Story subsections, acceptance criteria, etc.), when compared to the original file, then they are byte-for-byte unchanged.

## Spec Change Log

## Review Triage Log

### 2026-09-15 — Review pass
- verdicts: 9 findings — high 0, medium 0, low 3, false 6, maybe-false 0
- findings:
  - `[low]` `[defer]` Epic description sentence is duplicated verbatim between the new Epic List table's Summary column and the detailed `## Epic N` section paragraph below — pre-existing duplication (the description already appeared in both the old summary block and the detail section before this diff); this diff preserved but did not introduce it. Not this story's problem — DW-6 scoped only to duplicate *headings*, not duplicate *prose*.
  - `[false]` `[reject]` Claimed loss of in-document navigability/anchors from removing per-epic summary headings — refuted: this is the requested restructuring itself (intent asked for a table row in place of the duplicate heading); the doc's existing FR Coverage Map table likewise carries no per-row anchors, so this matches established convention, not a regression.
  - `[low]` `[reject]` Claimed wide/wrapping table rows on narrow viewports from long Summary-column prose — rejected: unlikely to be hit in everyday use (GitHub/VS Code markdown tables wrap cell text), and the only fix (rewording the summary sentences) is more than a trivial correction.
  - `[false]` `[reject]` Claimed the table is less informative for lacking epic size/scope indicators (e.g. story counts) — refuted: the original summary headings never carried story-count/scope info either; the spec's boundary required preserving existing facts only, and this diff does so without regression.
  - `[false]` `[reject]` Claimed no check was made for other files linking to the old per-epic summary anchor — refuted: the reviewer's own repo-wide grep found zero cross-references to the affected anchors, so no link breakage occurs.
  - `[false]` `[reject]` Claimed the diff sidesteps the intent's "sub-heading style already used elsewhere in the Epic List section" alternative by importing the FR Coverage Map's table convention from outside that section — refuted: the intent's parenthetical names "a table row" as an independently sufficient example, and the Epic List section had no other heading style to reuse in the first place, so the table-row reading is directly licensed by the intent text.
  - `[false]` `[reject]` Claimed the diff is more structurally invasive than a "relabel" would imply — refuted: the intent explicitly offers "restructure" as an equal alternative to "relabel," with "table row" as its named example, so removing the duplicate headings in favor of a table follows the intent literally.
  - `[false]` `[reject]` Claimed the fix's success criterion ("a reader cannot confuse one for the other") is unfalsifiable because no automated heading-uniqueness check exists — refuted: this is a non-behavioral documentation change (the dedicated verification-gap layer independently screened it out as such); no markdown-structure lint/test infrastructure exists anywhere else in this repo, and the spec's manual grep-based verification (run and passed) is the established check for this class of change.
  - `[low]` `[defer]` (grouped with row 1) Intent-alignment layer separately flagged the same Summary-column/detail-paragraph description duplication as a residual, out-of-scope repetition — same root cause and disposition as row 1.

## Design Notes

Use a GitHub-flavored markdown pipe table:

```
| Epic | Title | Summary | FRs | NFRs | ARs |
|------|-------|---------|-----|------|-----|
| Epic 1 | User Authentication API | Users can register an account, log in, and retrieve their own profile — a complete, stateless auth system with JWT. | FR-1, FR-2, FR-3 | NFR-1, NFR-2, NFR-3, NFR-4, NFR-5, NFR-6 | AR-1, AR-2, AR-3, AR-4, AR-5, AR-6 |
| Epic 2 | Password Management | Users can change their password after authentication — validating current credentials and enforcing minimum password requirements. | FR-4, FR-5, FR-6, FR-7 | NFR-7, NFR-8, NFR-9 | AR-7 |
```

## Verification

**Manual checks (if no CLI):**
- Run `grep -n '^#\{1,6\} Epic 1: User Authentication API'` and `grep -n '^#\{1,6\} Epic 2: Password Management'` against `epics.md` — each must return exactly one match (the detailed section).
- Diff the detailed sections (from `## Epic 1: User Authentication API` at the old line 99 onward) against the pre-change file to confirm no unintended changes.

## Auto Run Result

**Summary of implemented change:** In `_bmad-output/planning-artifacts/epics.md`, replaced the two `### Epic N: ...` summary blocks under `## Epic List` (previously duplicating the detailed `## Epic 1: User Authentication API` / `## Epic 2: Password Management` headings verbatim) with a single markdown table (`Epic | Title | Summary | FRs | NFRs | ARs`), reusing the doc's existing `FR Coverage Map` table convention. The detailed `## Epic N` sections and everything under them are untouched.

**Files changed:**
- `_bmad-output/planning-artifacts/epics.md` -- Epic List section (lines 81–97) restructured from two duplicate-heading blocks into a table; no other lines touched.

**Review findings breakdown:**
- Patches applied: 0
- Items deferred: 1 — pre-existing duplication of the epic description sentence between the Epic List table's Summary column and the detailed section's intro paragraph (out of DW-6's scope, which covers duplicate headings, not duplicate prose). Recorded in frontmatter `deferred`.
- Rejected findings (8, all from the same review pass):
  - Claimed loss of in-document navigability/anchors from dropping the per-epic summary headings — refuted: this was the intended, requested outcome, and matches the doc's existing FR Coverage Map table convention (no per-row anchors there either).
  - Claimed wide/wrapping table rows on narrow viewports — rejected as low: unlikely in everyday use, and the only fix is more than a trivial correction.
  - Claimed the table is less informative for lacking epic size/scope indicators — refuted: the original headings never carried that info either; no regression.
  - Claimed no check was made for other files linking to the old anchors — refuted: the reviewer's own repo-wide grep found zero cross-references.
  - Claimed the diff sidesteps the intent's "sub-heading style already used elsewhere in the Epic List section" alternative — refuted: the intent's "table row" example was independently sufficient, and the Epic List section had no other heading style to draw from.
  - Claimed the diff is more structurally invasive than "relabel" alone would imply — refuted: the intent explicitly offers "restructure" (table row) as an equal alternative to "relabel."
  - Claimed the fix's success criterion is unfalsifiable for lacking an automated heading-uniqueness check — refuted: non-behavioral documentation change, independently screened out by the verification-gap layer; manual grep verification (run and passed) is the established check for this class of change.

**Follow-up review recommendation:** `false` — no patched entries this pass (0 high, 0 medium, 0 low patched); nothing to re-verify.

**Verification performed:**
- `grep -n '^#\{1,6\} Epic 1: User Authentication API' epics.md` → exactly one match (line 88, the detailed section).
- `grep -n '^#\{1,6\} Epic 2: Password Management' epics.md` → exactly one match (line 176, the detailed section).
- Diffed the detailed sections (from the old `## Epic 1: ...` heading onward) against the pre-change (`ec429b4`) blob — byte-for-byte identical.
- Full `git diff` against baseline reviewed — single hunk, touches only the Epic List block.

**Residual risks:** None beyond the deferred, pre-existing description-duplication item above; this is a documentation-only, non-behavioral change.
