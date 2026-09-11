# Rubric Walker Review — Architecture Spine

**Spine:** `architecture-bmad-2026-09-06/ARCHITECTURE-SPINE.md`
**PRD:** `prd-bmad-2026-09-06/prd.md`
**Reviewer:** rubric-walker
**Date:** 2026-09-06

---

## Findings

### F-1 — Stack table has `[ASSUMPTION]` marker in version column

| Field | Value |
| --- | --- |
| **Severity** | Medium |
| **Checklist** | #4 (named tech verified-current) / #9 (empty sections / template comments) |
| **Location** | Stack table, FastAPI row: `0.141.1 \| [ASSUMPTION]` |
| **Issue** | The `[ASSUMPTION]` tag sits in the Role column but reads like a template artifact carried from the PRD's open question. It muddies the table's purpose. FastAPI 0.141.1 is verified as current on PyPI (released 2026-07-30). |
| **Suggested fix** | Replace `[ASSUMPTION]` with the actual role: `Web framework`. The assumption was resolved when the spine chose FastAPI. |

### F-2 — Deferred: JWT secret management could cause unit divergence

| Field | Value |
| --- | --- |
| **Severity** | High |
| **Checklist** | #3 (Deferred divergence) |
| **Location** | Deferred section, first bullet |
| **Issue** | "env var vs hardcoded" is explicitly left open. If `main.py` hardcodes the secret but `auth.py` reads `os.getenv("JWT_SECRET")`, two units diverge on how the secret is sourced — and the mismatch may only surface at runtime when one path gets `None` and the other gets a literal. At this altitude it should be pinned. |
| **Suggested fix** | Fix the decision now: e.g. "JWT secret is a constant in `auth.py` (`SECRET = "dev-secret-do-not-deploy"`). No env-var lookup. Appropriate for single-process local dev." This removes the divergence surface entirely. |

### F-3 — Deferred items are silently fine-grained except #2

| Field | Value |
| --- | --- |
| **Severity** | Low |
| **Checklist** | #3 (Deferred divergence) |
| **Location** | Deferred section, bullets 3-5 |
| **Issue** | "Input validation beyond required fields", "CORS, logging, observability", and "Deployment & environments" are all correctly deferred — the PRD explicitly scopes them out, and none of them create cross-unit divergence. This is clean. |
| **Suggested fix** | No action needed. Noted for completeness. |

### F-4 — All stack versions verified-current

| Field | Value |
| --- | --- |
| **Severity** | — (Pass) |
| **Checklist** | #4 (named tech verified-current) |
| **Location** | Stack table |
| **Issue** | Verified against PyPI on 2026-09-06: FastAPI 0.141.1 (latest), Uvicorn 0.52.4 (latest), bcrypt 5.0.0 (latest), PyJWT 2.13.0 (latest), Pydantic (bundled with FastAPI). All current. |
| **Suggested fix** | None. |

### F-5 — PRD coverage is complete for FR-1, FR-2, FR-3

| Field | Value |
| --- | --- |
| **Severity** | — (Pass) |
| **Checklist** | #5 (spec capability coverage) |
| **Location** | Capability → Architecture Map table |
| **Issue** | Every PRD consequence is traceable: FR-1 (register → 201/JWT, 409 conflict, 400 bad input, no plaintext in store, JWT contains username) is covered by AD-1, AD-2, AD-3. FR-2 (login → 200/JWT, 401 wrong creds, 400 missing fields) is covered by AD-1, AD-2, AD-4. FR-3 (get profile → 200 user data, 401 no/expired token) is covered by AD-1, AD-4, AD-5. No gaps. |
| **Suggested fix** | None. |

### F-6 — Every dimension at feature altitude is decided or explicitly deferred

| Field | Value |
| --- | --- |
| **Severity** | — (Pass) |
| **Checklist** | #6 (dimensions decided/deferred/open) |
| **Location** | Full spine |
| **Issue** | The feature-altitude envelope is well-bounded: HTTP contract (Consistency Conventions), error shape (AD-5), auth mechanism (AD-1, AD-4), storage model (AD-3), security posture (AD-2). Operational/environmental envelope (deployment, environments, infra) is deferred with an explicit note that the scope is "single-process local dev only" — appropriate for this altitude. Nothing is silently left open. |
| **Suggested fix** | None. |

### F-7 — Mermaid diagram is valid and conveys structure

| Field | Value |
| --- | --- |
| **Severity** | — (Pass) |
| **Checklist** | #7 (valid mermaid, conveys structure) |
| **Location** | Design Paradigm section |
| **Issue** | `graph TD` with three solid edges (Routes → Services → Store) and one dashed edge (Routes -.-> AuthMiddleware, AuthMiddleware → Services) is syntactically valid. The diagram clearly shows the three-tier layered architecture and the middleware's cross-cutting concern. HTML labels (`<br/>`) render correctly in Mermaid. |
| **Suggested fix** | None. |

### F-8 — Seed is minimal and correct

| Field | Value |
| --- | --- |
| **Severity** | — (Pass) |
| **Checklist** | #8 (seed minimal) |
| **Location** | Structural Seed section |
| **Issue** | Six files, each with a one-line comment explaining its role. Maps directly to the layered architecture: `main.py` (app factory), `routes.py` (HTTP layer), `services.py` (business logic), `store.py` (data), `models.py` (Pydantic schemas), `auth.py` (JWT concern). Nothing extraneous. |
| **Suggested fix** | None. |

### F-9 — No empty sections or leftover template comments

| Field | Value |
| --- | --- |
| **Severity** | — (Pass, with caveat on F-1) |
| **Checklist** | #9 (empty sections / template comments) |
| **Location** | Full spine |
| **Issue** | All sections are populated with concrete content. No `<!-- TODO -->`, `{placeholder}`, or empty subsections. The only artifact is the `[ASSUMPTION]` in the Stack table (covered by F-1). |
| **Suggested fix** | See F-1. |

### F-10 — AD Rules are enforceable and prevent stated divergence

| Field | Value |
| --- | --- |
| **Severity** | — (Pass) |
| **Checklist** | #2 (Rule enforceable / prevents divergence) |
| **Location** | Invariants & Rules section |
| **Issue** | Each AD Rule is concrete and testable: AD-1 ("All authentication state is carried in the JWT") — enforceable by inspecting session/cookie usage. AD-2 ("Passwords are hashed with bcrypt… immediately discarded") — enforceable by inspecting store writes and response bodies. AD-3 ("One Python dict… No database, no file I/O") — enforceable by inspecting imports and store implementation. AD-4 ("A signed JWT in the Authorization header is the only way") — enforceable by inspecting auth dependencies. AD-5 ("Errors return JSON with a `detail` field… status codes follow REST convention") — enforceable by inspecting response shapes. All Rules directly prevent their stated divergence. |
| **Suggested fix** | None. |

### F-11 — Divergence points for the level below are covered

| Field | Value |
| --- | --- |
| **Severity** | — (Pass) |
| **Checklist** | #1 (real divergence points) |
| **Location** | Invariants & Rules section |
| **Issue** | At feature altitude, the real divergence risks for the implementing units are: (a) mixed auth strategies, (b) plaintext passwords, (c) inconsistent error shapes, (d) mixed storage backends, (e) session state leaking into endpoints. All five are directly addressed by AD-1 through AD-5. No significant divergence point is missed. |
| **Suggested fix** | None. |

---

## Summary

| Metric | Value |
| --- | --- |
| **Verdict** | **Pass** |
| **Total findings** | 11 (2 actionable, 9 clean) |
| **Critical** | 0 |
| **High** | 1 (F-2: deferred JWT secret management risks unit divergence) |
| **Medium** | 1 (F-1: `[ASSUMPTION]` artifact in Stack table) |
| **Low** | 0 |

### Top findings

1. **High — F-2:** Deferred JWT secret management ("env var vs hardcoded") creates a real divergence surface between `main.py` and `auth.py`. Fix the decision now — pin to a constant in `auth.py` for local-dev scope.
2. **Medium — F-1:** `[ASSUMPTION]` in the Stack table is a leftover template marker. Replace with the resolved role (`Web framework`).

### Verdict

**Pass.** The spine is solid. Two clean-up items, zero blockers.
