# Standard Workflow: Idea to Ship (BMM + TEA)

> Required steps are marked with ✅, optional with ⚪.

---

## Phase 0 — Idea & Ideation ⚪

| Skill | Code | Required | Output |
|-------|------|----------|--------|
| `bmad-brainstorming` | `[BP]` | ⚪ | `_bmad-output/brainstorming/` |
| `bmad-forge-idea` | `[FI]` | ⚪ | `_bmad-output/forge/` |
| `bmad-deep-recon` | `[RS]` | ⚪ | `_bmad-output/planning-artifacts/research/` |

**Pick one** to flesh out your idea: brainstorm for breadth, forge for pressure-testing, or deep recon for evidence.

---

## Phase 1 — Product Definition ⚪

**Pick one path** to capture your product concept:

| Skill | Code | Required | Output |
|-------|------|----------|--------|
| `bmad-product-brief` | `[CB]` | ⚪ | `planning-artifacts/` — product brief |
| `bmad-prfaq` | `[WB]` | ⚪ | `planning-artifacts/` — PRFAQ doc |
| `bmad-spec` | `[SPC]` | ⚪ | `_bmad-output/specs/spec-{slug}/` |

Brief is gentler; PRFAQ is more rigorous; spec if you're defining something non-software.

---

## Phase 2 — Requirements ✅

| Skill | Code | Required | Output |
|-------|------|----------|--------|
| `bmad-prd` | `[PRD]` | ✅ | `planning-artifacts/prds/` |
| `bmad-ux` | `[CU]` | ⚪ | `planning-artifacts/` — UX docs |

**PRD is the gate** — nothing downstream works without it.

---

## Phase 3 — Solutioning (BMM) ✅

| Skill | Code | Required | Output |
|-------|------|----------|--------|
| `bmad-architecture` | `[CA]` | ✅ | `planning-artifacts/architecture/` |
| `bmad-create-epics-and-stories` | `[CE]` | ✅ | `planning-artifacts/epics.md` |
| `bmad-sprint-planning` | `[SP]` | ✅ | `implementation-artifacts/sprint-status.yaml` |

**Sequence is strict**: architecture → epics/stories → sprint planning. Sprint planning is the final readiness gate — it must return PASS to proceed.

---

## Phase 4 — Solutioning (TEA) ⚪

Runs in parallel with or after BMM solutioning. **Test design** is the entry point:

| Skill | Code | Required | Output |
|-------|------|----------|--------|
| `bmad-testarch-test-design` | `[TD]` | ⚪ | `test-artifacts/test-design/` |
| `bmad-testarch-framework` | `[TF]` | ⚪ | `test-artifacts/` — framework scaffold |
| `bmad-testarch-ci` | `[CI]` | ⚪ | `test-artifacts/` — CI config |

**Sequence**: test design → framework → CI. All three are optional but strongly recommended — they set up your quality infrastructure before any code is written.

---

## Phase 5 — Implementation ✅

This is where **BMM Build** and **TEA implementation skills** interleave:

| Skill | Code | Required | Output |
|-------|------|----------|--------|
| `bmad-build` | `[BD]` | ✅ | project code |
| `bmad-testarch-atdd` | `[AT]` | ⚪ | `test-artifacts/` — red-phase acceptance tests |
| `bmad-testarch-automate` | `[TA]` | ⚪ | `test-artifacts/` — expanded test suite |

**The flow per story**:
1. **ATDD** (`[AT]`) — write acceptance test scaffolds *before* implementation (red phase)
2. **Build** (`[BD]`) — clarify, plan, implement, review, present (green phase)
3. **Test Automation** (`[TA]`) — expand coverage as implementation solidifies

---

## Phase 6 — Quality Gate ⚪

After build completes, run quality checks:

| Skill | Code | Required | Output |
|-------|------|----------|--------|
| `bmad-code-review` | `[CR]` | ⚪ | — |
| `bmad-testarch-test-review` | `[RV]` | ⚪ | `test-artifacts/test-reviews/` — 0–100 score |
| `bmad-testarch-nfr` | `[NR]` | ⚪ | `test-artifacts/` — NFR audit |
| `bmad-testarch-trace` | `[TR]` | ⚪ | `test-artifacts/traceability/` — matrix + gate |

**Sequence**: code review + test review → NFR audit → traceability. Traceability is the final quality gate — it gives you a pass/fail on coverage completeness.

---

## Phase 7 — Closing ⚪

| Skill | Code | Required | Output |
|-------|------|----------|--------|
| `bmad-retrospective` | `[ER]` | ⚪ | `implementation-artifacts/` — retro doc |
| `bmad-walkthrough` | `[WT]` | ⚪ | — |

---

## Quick Reference: Required Steps Only

```
[PRD] → [CA] → [CE] → [SP] → [BD]
```

## Full Flow with All Optional Steps

```
[BP]/[FI]/[RS] → [CB]/[WB]/[SPC] → [PRD] → [CU]
  → [CA] → [CE] → [SP] → [TD] → [TF] → [CI]
    → [AT] → [BD] → [TA] → [CR] → [RV] → [NR] → [TR]
      → [ER] → [WT]
```
