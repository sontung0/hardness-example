---
title: 'TEA Test Design → BMAD Handoff Document'
version: '1.0'
workflowType: 'testarch-test-design-handoff'
inputDocuments:
  - prds/prd-bmad-2026-09-06/prd.md
  - architecture/architecture-bmad-2026-09-06/ARCHITECTURE-SPINE.md
  - planning-artifacts/epics.md
sourceWorkflow: 'testarch-test-design'
generatedBy: 'TEA Master Test Architect'
generatedAt: '2026-09-06'
projectName: 'bmad'
---

# TEA → BMAD Integration Handoff

## Purpose

This document bridges TEA's test design outputs with BMAD's epic/story decomposition workflow (`create-epics-and-stories`). It provides structured integration guidance so that quality requirements, risk assessments, and test strategies flow into implementation planning.

## TEA Artifacts Inventory

| Artifact | Path | BMAD Integration Point |
|----------|------|----------------------|
| Test Design (Architecture) | `_bmad-output/test-artifacts/test-design/test-design-architecture.md` | Epic quality requirements, story acceptance criteria |
| Test Design (QA) | `_bmad-output/test-artifacts/test-design/test-design-qa.md` | Story test requirements, execution strategy |
| Risk Assessment | (embedded in both documents) | Epic risk classification, story priority |
| Coverage Strategy | (embedded in QA document) | Story test requirements |

## Epic-Level Integration Guidance

### Risk References

| Risk ID | Category | Score | Recommendation for Epic |
|---------|----------|-------|------------------------|
| R-01 | SEC | **6** | Password hash exclusion must be validated in Epic 1 (Stories 1.2, 1.4) |
| R-02 | SEC | **6** | JWT token validation must be validated in Epic 1 (Story 1.4) |
| R-03 | BUS | 4 | Duplicate registration handling in Epic 1 (Story 1.2) |
| R-04 | BUS | 4 | Username normalization in Epic 1 (Story 1.1) |
| R-05 | TECH | 4 | Error handler override in Epic 1 (Story 1.4) |

### Quality Gates

- **P0 pass rate**: 100% before any release
- **P1 pass rate**: ≥ 95% before any release
- **High-risk mitigations**: R-01 and R-02 must be complete before release
- **Code coverage**: ≥ 80% on `services.py`, `auth.py`, `store.py`

## Story-Level Integration Guidance

### P0/P1 Test Scenarios → Story Acceptance Criteria

| Story | P0 Scenarios | P1 Scenarios |
|-------|-------------|-------------|
| **Story 1.1: Project scaffolding & data layer** | T-07 (bcrypt hashing) | T-23 (store returns only username+name), T-24 (JWT sub claim) |
| **Story 1.2: User registration** | T-01, T-02, T-03, T-05, T-08 | T-04, T-06 |
| **Story 1.3: User login** | T-09, T-10, T-11 | T-12, T-13 |
| **Story 1.4: Get current user** | T-14, T-15, T-16, T-17, T-18, T-19, T-20, T-26, T-28 | T-21, T-22, T-27 |

### Data-TestId Requirements

- Not applicable for backend-only API (no DOM elements to test)

## Risk-to-Story Mapping

| Risk ID | Category | P×I | Recommended Story | Test Level |
|---------|----------|-----|-------------------|------------|
| R-01 | SEC | 6 | Story 1.2, Story 1.4 | Unit + Integration |
| R-02 | SEC | 6 | Story 1.4 | Unit + Integration |
| R-03 | BUS | 4 | Story 1.2 | Integration |
| R-04 | BUS | 4 | Story 1.1 | Integration |
| R-05 | TECH | 4 | Story 1.4 | Integration |
| R-06 | SEC | 2 | Story 1.1 | Unit |
| R-07 | OPS | 1 | Story 1.1 | N/A (by design) |
| R-08 | PERF | 2 | Future | N/A (no SLO) |

## Recommended BMAD → TEA Workflow Sequence

1. **TEA Test Design** (`TD`) → produces this handoff document ✅
2. **BMAD Create Epics & Stories** → consumes this handoff, embeds quality requirements
3. **TEA ATDD** (`AT`) → generates acceptance tests per story
4. **BMAD Implementation** → developers implement with test-first guidance
5. **TEA Automate** (`TA`) → generates full test suite
6. **TEA Trace** (`TR`) → validates coverage completeness

## Phase Transition Quality Gates

| From Phase | To Phase | Gate Criteria |
|------------|----------|---------------|
| Test Design | Epic/Story Creation | All P0 risks have mitigation strategy ✅ |
| Epic/Story Creation | ATDD | Stories have acceptance criteria from test design |
| ATDD | Implementation | Failing acceptance tests exist for all P0/P1 scenarios |
| Implementation | Test Automation | All acceptance tests pass |
| Test Automation | Release | Trace matrix shows ≥80% coverage of P0/P1 requirements |
