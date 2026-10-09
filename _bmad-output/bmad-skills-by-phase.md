# BMad Skills — In Order of Use

Source: `_bmad/_config/bmad-help.csv` (installed skills). ⭐ = required in the catalog; everything else is optional.

## 1. Idea & research (optional)

| Code | Skill | What it's for |
|---|---|---|
| BP | `bmad-brainstorming` | Come up with ideas |
| FI | `bmad-forge-idea` | Test a rough idea with hard questions until you can act on it or drop it |
| RS | `bmad-deep-recon` | Research the market, the domain, the technology or competitors |
| CB | `bmad-product-brief` | Write the idea down as a short brief |
| WB | `bmad-prfaq` | Another way to write the brief: start from the launch press release, then answer hard questions |

## 2. Planning

| Code | Skill | What it's for |
|---|---|---|
| ⭐ PRD | `bmad-prd` | Write the product requirements (what to build) |
| SPC | `bmad-spec` | A shorter, lighter alternative to a PRD (a SPEC.md file) |
| CU | `bmad-ux` | UX design. Strongly recommended if the product has a real UI. |

## 3. Solutioning (how to build it)

| Code | Skill | What it's for |
|---|---|---|
| ⭐ CA | `bmad-architecture` | The main technical decisions |
| TD | `bmad-testarch-test-design` | Test plan for the whole system, based on risk |
| TF | `bmad-testarch-framework` | Set up the test framework |
| CI | `bmad-testarch-ci` | Set up the CI pipeline that runs the tests |
| ⭐ CE | `bmad-create-epics-and-stories` | Split the work into epics and stories with acceptance criteria |
| TD | `bmad-testarch-test-design` (again, per epic) | Test plan for one epic |
| ⭐ SP | `bmad-sprint-planning` | Check the plan is ready, then create `sprint-status.yaml` |

## 4. Build: repeat for each story

| Code | Skill | What it's for |
|---|---|---|
| AT | `bmad-testarch-atdd` | Write failing acceptance tests before the code |
| ⭐ BD | `bmad-build` | Build the story: plan, code, review |
| CR | `bmad-code-review` | An extra code review on top of the one Build already does |
| WT | `bmad-walkthrough` | Walk a person through a change so they can review it |
| TA / QA | `bmad-testarch-automate` / `bmad-qa-generate-e2e-tests` | Add more tests. TA is the fuller TEA version; QA is quicker. |
| RV | `bmad-testarch-test-review` | Score test quality from 0 to 100 |

## 5. Release gate & end of epic

| Code | Skill | What it's for |
|---|---|---|
| NR | `bmad-testarch-nfr` | Check performance and security evidence |
| TR | `bmad-testarch-trace` | Requirements-to-tests map and a PASS/FAIL verdict |
| ER | `bmad-retrospective` | Look back at the finished epic and plan the next one |

## Any time

| Code | Skill | When |
|---|---|---|
| BH | `bmad-help` | When you're unsure what comes next |
| SS | `bmad-sprint-planning` (status) | To see sprint progress |
| CC | `bmad-correct-course` | When a big change happens mid-sprint |
| RV | `bmad-review` | To review a document or a diff |
| AE | `bmad-advanced-elicitation` | To push a draft to a better version |
| PM | `bmad-party-mode` | To discuss something with several agents at once |
| PC | `bmad-project-context` | To set up or refresh the instructions AI agents follow in this repo |
| BC | `bmad-customize` | To change how an agent or workflow behaves |
| TMT | `bmad-teach-me-testing` | To learn testing |

## Agents

Mary (analyst), John (PM), Sally (UX), Winston (architect), Amelia (dev) and Murat (TEA). Each one gives you a menu of the skills above for their area.

## Automation (only if you use the loop)

`bmad-loop-setup`, `bmad-loop-sweep`, `bmad-loop-resolve` and `bmad-build-auto` let builds run unattended.

## Note

The catalog says ATDD comes after `bmad-create-story` and before `bmad-dev-story`. Neither of those skills is installed. In this version, `bmad-build` covers both jobs.

Tip: start each skill in a fresh chat.
