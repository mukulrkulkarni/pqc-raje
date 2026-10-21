# Chunk 2E Documentation Notes

## Purpose

This chunk completes the approved `/app` integration. It does not change ELECTRE III math, add JavaScript, or change deployment scope.

## Current and target status

- **Implemented and verified:** `/app` uses the shared strict adapter before it creates a `RankingResult`.
- **Implemented and verified:** The app rejects a measured estimate above 300 seconds before ranking starts.
- **Implemented and verified:** The shared adapter uses the approved 330-second deadline. A timeout returns no result page or download token.
- **Implemented and verified:** The app serializes canonical JSON, validates split parts, and publishes one bounded cache entry through the existing locked cache.
- **Implemented and verified:** The signed Flask cookie has a 30-minute lifetime. It stores opaque workflow and download-session identifiers only.
- **Implemented and verified:** Docs routes and compatibility JSON routes remain registered.
- **Target limitation:** The runtime profile is a conservative local baseline. A deployment must replace it with measured p95 records for its hardware.
- **Target limitation:** The cache remains process-memory and single-worker. It does not provide persistent or multi-worker sharing.

## User journey

1. Open `/app/` and enter up to eight strict criteria.
2. Submit the matrix and preview headers, values, and missing-value choice.
3. Confirm input and run compute. The server checks feasibility before compute.
4. Read the top results and use the standard HTML download link for canonical JSON.

No app JavaScript is used. The app CSP omits `script-src`. Pages use semantic HTML and existing labels, headings, tables, and forms.

## Module and source evidence

- `app/routes/workflow.py` owns the server-rendered route sequence, preview requirement, 300-second feasibility call, 330-second timeout response, `RankingResult` download publication, and exact download headers.
- `app/services/runtime_profile.py` supplies the conservative local `RuntimeModel` used only by `/app`.
- `electre3/shared.py` validates criteria and matrices, calls the feasibility gate, enforces the hard deadline, and returns immutable `RankingResult` objects.
- `electre3/runtime.py` defines the 300-second feasibility rule, 330-second deadline, p95 model, and bounded benchmark helpers.
- `electre3/serialization.py` writes canonical UTF-8/LF JSON and validates ordered split artifacts and SHA-256 checksums.
- `app/services/result_cache.py` provides latest-only atomic replacement, 32 MiB total bound, 16 MiB part bound, 30-minute TTL, session-bound opaque tokens, and successful-only rate control.
- `app/__init__.py` sets the 30-minute signed session lifetime and route-specific CSP headers.

## Setup, use, and debugging

Run from the repository root with the existing Python environment:

```text
python -m pytest tests/test_app_workflow.py -q
```

Use `/app/` in a Flask test or configured local server. A 400 response means validation, preview, or confirmation failed. A 422 response means the conservative estimate exceeds 300 seconds. A 504 response means the 330-second deadline expired; no partial result is published. A 404 download response means the opaque token is invalid, expired, replaced, foreign-session, or lost after restart. A 410 response means checksum validation failed. A 429 response means 30 successful downloads occurred in one rolling minute.

## Test methodology and inventory

All categories include positive, negative, and edge coverage where meaningful. Tests use Flask's local test client and local NumPy fixtures. No external service ran.

| Category | Modules and purpose | Positive, negative, and edge evidence |
|---|---|---|
| Unit | `tests/test_shared_contract.py`, `tests/test_runtime.py` | Strict criteria, matrix shape/range/rows, header order, block limits, feasibility acceptance/rejection, deadline, and block-size byte identity. |
| Integration | `tests/test_app_workflow.py` | Four-step route flow, preview gate, missing-value approval, feasibility rejection, timeout without download, timed session metadata, compatibility routes. |
| Scientific correctness | `tests/test_end_to_end_composition.py`, `tests/test_n1_scientific_followup.py`, `tests/test_ranking*.py` | Minimize direction, veto threshold behavior, diagonal rule, raw net-flow sorting, invalid weights, and ties/regressions. |
| Security | `tests/test_result_cache.py`, `tests/test_security_headers.py`, `tests/test_security.py` | Opaque token/session binding, restart, TTL, rate, integrity rejection, concurrent limit, safe headers, upload validation. |
| UI/accessibility | `tests/test_app_workflow.py`, `tests/test_ui_styles.py` | Labels and criteria modes, server-rendered pages, no scripts or inline handler, CSP without app `script-src`. |
| Performance/benchmark | `tests/test_runtime.py` | Deterministic conservative p95 model, bounded harness records 10,000 and 15,000 requested points as explicit rejected measurements under local bounds. This is not a hardware performance claim. |
| Serialization/cache | `tests/test_serialization.py`, `tests/test_result_cache.py` | Unicode, LF-only JSON/CSV, dtype and shape, split order/checksums, exact reassembly, cache capacity, latest replacement, and expiry. |
| End-to-end | `tests/test_app_workflow.py`, `tests/test_end_to_end_composition.py` | CLI/web ranking equivalence, workflow-to-download exact bytes, and block pipeline reference equivalence. |

Commands executed and results:

```text
python -m pytest tests/test_app_workflow.py tests/test_runtime.py tests/test_shared_contract.py tests/test_serialization.py tests/test_result_cache.py -q
56 passed in 1.42s

python -m compileall app electre3 tests
Exit code 0
```

The final verification commands, full pytest result, diff check, and commit record appear in `out/chunk-2e-checkpoint.json`.

## Limits

- Do not treat the embedded baseline as a production hardware benchmark.
- The code cannot forcibly terminate a non-cooperative Python compute thread at exactly 330 seconds. The shared block loop checks the monotonic deadline and prevents result publication after expiry.
- Flask's default signed cookie needs a deployment-secret configuration. The cookie remains readable by the client; it contains only bounded opaque identifiers.
- Split manifests are internal cache metadata. The current download route serves canonical JSON, not individual parts.
