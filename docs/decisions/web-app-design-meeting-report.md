# Local ELECTRE III Web-App Design Meeting Report

**Status:** Planning meeting completed; implementation is blocked pending contract decisions.
**Inputs:** `web-app-requirements.txt`, pre-read brief, gap register, repository evidence, four specialist reviews.

## Executive recommendation

**NO-GO for implementation.** The target is feasible, but implementation must follow the approved contracts below and preserve the listed evidence gaps.

**Recommended direction:** shared adapter, server-rendered `/app` workflow, semantic HTML math notation, bounded single-worker in-memory result cache, and no separate browser computation.

## Approved contracts

- Route scope: ranking app under `/app`; documentation routes remain separately governed.
- No JavaScript: ranking app only. Use semantic HTML math notation. Reject live or pre-rendered KaTeX for this scope.
- Shared CLI/web policy: weights must sum to `1`; matrix scores must be finite, complete, and normalized to `[0,1]`.
- Matrix bounds: maximum upload `100 MiB`; maximum rows `100,000`; maximum criteria `8`.
- Block size: integer range `1..10,000`; default `1,000`.
- Runtime feasibility: benchmark `N = 100, 500, 1,000, 5,000, 10,000, 15,000`, `C = 4, 8`, and block sizes `1,000, 5,000, 10,000`. Use measured p95 plus safety margin; reject estimates above `300` seconds.
- Hard timeout: `330` seconds. Do not cache partial results.
- Byte identity: required across repeated runs, CLI/web serializers, and supported block sizes. Engineering must implement fixed-order accumulation and canonical serialization.
- Result cache: latest result only, process memory, single worker, `32 MiB` total, `16 MiB` per artifact, `30` minute TTL, `30` successful downloads per session per minute. Split larger logical results into ordered parts with a manifest and SHA-256 checksums.
- Session: 30-minute lifetime; small signed metadata only. Never store matrices, criteria, results, artifacts, raw uploads, or download tokens in cookies.

## Technical architecture

Use one shared adapter between CLI and web routes:

```text
CLI ─────────┐
             ├── shared input contract → compute_ranking → ResultBundle → serializers → cache
Web routes ──┘
```

Keep `electre3/ranking.py::compute_ranking` framework-free. Add strict web/shared input parsing, an immutable result model, canonical serializers, and a cache lifecycle module. Routes must not duplicate criteria defaults, computation, or serialization.

Target routes:

| Route | Contract |
|---|---|
| `GET /app/` | Criteria entry form. |
| `POST /app/confirm-inputs` | Strict criteria validation and matrix-entry form. |
| `POST /app/preview` | Bounded parsing, header mapping, value validation, missing-value approval, feasibility report, and confirmation. |
| `POST /app/compute` | Confirmation-gated shared computation, cache insertion, and top-ten result view. |
| `GET /app/downloads/<token>/<artifact>` | Exact cached bytes; no recomputation or client paths. |

Retain current JSON routes only as temporary compatibility adapters if tests or consumers require them. Current `/compute/start` is a placeholder and `/compute/status/<job_id>` reports synthetic completion.

## Evidence-backed gaps and compatibility constraints

- Web compute does not call the core: `app/routes/compute.py::start_computation`.
- Web preview loads and summarizes full matrices but does not enforce the target contract: `app/services/preview.py::get_matrix_preview`.
- Criteria validator lacks strict name/maximize/max-count checks: `app/services/security.py::validate_criteria_json`.
- Existing CSP split: `app/__init__.py::CSP_APP`, `CSP_DOCS`.
- `app/templates/config.html` contains a conflicting `script-src 'unsafe-inline'` policy and must be fixed for the app scope.
- Current CLI saves ranking indices only: `electre3/cli.py::main`, `electre3/cli_run.py::run_ranking`; shared score serializers must be added.
- Block-size tests currently use numerical tolerance, not byte identity: `tests/test_ranking_deep.py`.
- Existing upload registry and session confirmation need lifecycle and cookie-policy implementation: `app/services/security.py`, `app/routes/preview.py`.

## Milestone stop conditions

- Stop if scientific or security contracts are contradicted by evidence.
- Stop if fixed-order accumulation cannot prove byte identity across supported block sizes.
- Stop if any bound, serializer format, token policy, or session rule is undefined.
- Stop if route migration breaks existing tests without a rollback or compatibility plan.
- Stop if a required security, scientific, accessibility, or exact-byte test fails.
- Stop if runtime estimates exceed 300 seconds or hard timeout reaches 330 seconds.
