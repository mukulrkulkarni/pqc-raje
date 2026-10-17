# Decision memo: Flask vs FastAPI (docs/UI server layer)

**Status:** Informational (no implementation work approved by this memo)

**Context:** This repository serves interactive documentation pages (module tutorials) and a small UI. It currently uses **Flask** with strict allow-lists, canonical-path checks, and CSP/security-header enforcement. A future migration to **FastAPI** is being considered.

---

## Executive recommendation

**Decision:** **NO-GO now**. Reassess after **Phase 7** is complete or when a clear API/concurrency requirement exists.

**Rationale:** The current Flask layer is small, stable, and already encodes security-critical invariants. Migration has meaningful parity risk with limited near-term benefit.

---

## Benefits (if/when you switch)

- Strong typed request/response models (Pydantic) for future API expansion.
- Async support for higher concurrency or long-running I/O workloads.
- Router-based structure that can be easier to scale in larger services.

---

## Top risks and impacts

### Security risks (highest priority)

- **Path traversal regression (High):** FastAPI path parameters and `StaticFiles` mounts can reintroduce `..` and encoded-slash issues unless you keep strict allow-lists and containment checks.
- **Allow-list / prefix-collision drift (High):** A rewrite can accidentally broaden what module names and assets are reachable.
- **Static serving over-exposure (High):** Directory mounts can expose unintended artifacts under `docs/`.
- **CSP/security headers parity (Med–High):** Flask `after_request` behavior must be replicated with middleware that also covers 404/500 responses.
- **OpenAPI/docs endpoint exposure (Med–High):** FastAPI defaults (`/openapi.json`, `/docs`, `/redoc`) must be disabled or protected.
- **Supply-chain expansion (Med):** Starlette + Pydantic (+ usually Uvicorn) increases dependency surface and increases the value of strict pinning.
- **Test coverage drift (Med):** Framework refactors often break tests mechanically; teams sometimes relax assertions, losing guarantees.

### Engineering redesign impact

- **Medium scope:** ~**3–5 engineering days** for a parity-preserving staged migration.
- Changes required: routers, middleware for headers/CSP parity, allow-list routing, static assets policy, test harness adjustments.

### Review workload impact (rough)

- **Security Lead:**
  - **Low (0.5–1 day)** if you preserve URL surface + keep allow-lists + port tests without weakening.
  - **Medium (1.5–3 days)** if you introduce `StaticFiles` mounts or refactor routing/URL shapes.
  - **High (3–5+ days)** if OpenAPI/docs endpoints are exposed publicly or path handling becomes dynamic.

- **Engineering Critic:** ~**0.5–1 day** review time if migration is staged into small, test-backed PRs.

---

## Non-negotiable invariants (must not regress)

- Explicit allow-lists for **module docs** and **tutorial assets**.
- Strict module name validation before file access (pattern + membership).
- Canonical-path containment checks for any filesystem-derived path.
- Route-scoped CSP/security headers present on **200/404/500** responses.
- Offline-safe docs pages: relative links only; no external loads.

---

## Safe staging plan (high level)

1) Write a parity contract: route matrix (status code, headers, CSP, content-type) + negative tests (traversal, external URLs).
2) Add/port tests first. Require green tests before any route cutover.
3) Route-by-route migration with a rollback window.
4) Disable FastAPI schema/docs endpoints by default (`openapi_url=None`, `docs_url=None`, `redoc_url=None`) unless explicitly required.

---

## Decision triggers (when to revisit)

Reassess FastAPI migration only when at least one trigger is true:

- API surface grows materially (multiple endpoints, typed inputs/outputs needed).
- Concurrency/latency requirements exceed Flask’s suitability for this project.
- A measured operational need exists (deployment, scalability, or integrations) that outweighs parity risk.

---

## Evidence basis (meeting inputs)

- Security Lead: migration risks (traversal, allow-list drift, static serving exposure, CSP parity, OpenAPI exposure) and mitigation requirements.
- Engineering Critic: staged migration recommendation; estimated 3–5 engineering days to reach parity safely.

**Note:** This memo uses user-supplied model pricing for cost estimates elsewhere. It does not claim alignment with Innovium billing.
