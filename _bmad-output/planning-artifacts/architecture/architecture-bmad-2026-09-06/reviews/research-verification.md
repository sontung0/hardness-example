# Research Verification Review

**Artifact:** `ARCHITECTURE-SPINE.md` — Simple REST API Auth  
**Reviewer:** Automated verification  
**Date:** 2026-09-06  
**Method:** Live PyPI JSON API queries + GitHub release pages + documentation checks  

---

## Summary

All four named library versions were verified against live PyPI data. All exist, are actively maintained, have current releases, and fit their stated roles. No deprecated or defunct libraries found. No incorrect version numbers found.

**Verdict: PASS**

---

## Per-Library Findings

### 1. FastAPI 0.141.1

| Field | Value |
|-------|-------|
| Claimed version | 0.141.1 |
| Latest on PyPI | 0.141.1 |
| Status | ✅ Correct |
| Still maintained | Yes — active development, frequent releases |
| Fits use case | Yes — standard choice for Python REST APIs |
| Python requirement | `>=3.10` |
| Severity | None |

### 2. Uvicorn 0.52.4

| Field | Value |
|-------|-------|
| Claimed version | 0.52.4 |
| Latest on PyPI | 0.52.4 |
| Status | ✅ Correct |
| Still maintained | Yes — maintained by Marcelo Trylesinski (Kludex), formerly Tom Christie |
| Fits use case | Yes — the standard ASGI server for FastAPI |
| Note | PyPI classifier still says "Beta" but this is a labeling quirk; it is production-grade and widely used |
| Severity | None |

### 3. bcrypt 5.0.0

| Field | Value |
|-------|-------|
| Claimed version | 5.0.0 |
| Latest on PyPI | 5.0.0 |
| Status | ✅ Correct |
| Still maintained | Yes — maintained by pyca (Python Cryptographic Authority) |
| Fits use case | Yes — the standard Python password-hashing library |
| Note | Since v4.0, bcrypt is implemented in Rust; no functional API change |
| Severity | None |

**Default work factor claim:** The spine says "default work factor." bcrypt's `gensalt()` defaults to 12 rounds, which aligns with current NIST/recommendations for 2024+ hardware. This is correct.

### 4. PyJWT 2.13.0

| Field | Value |
|-------|-------|
| Claimed version | 2.13.0 |
| Latest on PyPI | 2.13.0 (security release, May 2025) |
| Status | ✅ Correct |
| Still maintained | Yes — active, recent security fixes |
| Fits use case | Yes — the standard Python JWT library |
| Severity | None |

**Note:** PyJWT 2.13.0 is a security release with 5 fixes. The spine should use this exact version to get those patches.

### 5. Pydantic (via FastAPI)

| Field | Value |
|-------|-------|
| Claimed version | "(via FastAPI)" |
| Actual dependency | Pydantic v2 (>=2.9.0 required by FastAPI 0.141.1) |
| Status | ✅ Correct — Pydantic v2 is current and actively maintained |
| Fits use case | Yes — built-in request/response validation for FastAPI |
| Severity | None |

---

## Cross-Cutting Checks

### Library Existence & Fit

| Library | Exists? | Actively maintained? | Fits use case? |
|---------|---------|---------------------|----------------|
| FastAPI | ✅ Yes | ✅ Yes | ✅ REST API framework |
| Uvicorn | ✅ Yes | ✅ Yes | ✅ ASGI server |
| bcrypt | ✅ Yes | ✅ Yes | ✅ Password hashing |
| PyJWT | ✅ Yes | ✅ Yes | ✅ JWT encode/decode |
| Pydantic | ✅ Yes | ✅ Yes | ✅ Request/response validation |

### Version Currency

| Library | Spine version | Latest (2026-09-06) | Delta |
|---------|--------------|---------------------|-------|
| FastAPI | 0.141.1 | 0.141.1 | None |
| Uvicorn | 0.52.4 | 0.52.4 | None |
| bcrypt | 5.0.0 | 5.0.0 | None |
| PyJWT | 2.13.0 | 2.13.0 | None |

### Outdated / Deprecated / Deprecated-in-Transit

No libraries are deprecated or approaching end-of-life. All are actively maintained with recent releases.

### Greenfield Defaults

- **bcrypt `gensalt()` default:** 12 rounds — correct per source and current recommendations.
- **FastAPI `requires_python`:** `>=3.10` — matches the spine's `Python ≥ 3.10` claim.
- **Pydantic v2:** Ships with FastAPI 0.141.1 — no manual pinning needed, correctly listed as "(via FastAPI)."

---

## Findings Table

| # | Severity | Claim | Finding | Suggested Fix |
|---|----------|-------|---------|---------------|
| — | — | — | All checks pass | No fixes needed |

---

## Methodology

- Fetched `https://pypi.org/pypi/{package}/json` for each library and extracted the `info.version` field.
- Cross-referenced GitHub release pages for PyJWT (2.13.0 confirmed as latest).
- Checked bcrypt default work factor via PyPI documentation and source repository.
- Verified Python version requirements against PyPI `requires_python` metadata.

All data sourced from live, authoritative registries (PyPI, GitHub) — not from training data.
