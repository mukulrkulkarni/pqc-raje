# Chunk 2A Documentation Notes for Technical Document Writer

**Purpose:** Durable notes for future CLI and web tutorials. These notes record verified Chunk 2A behavior and approved target boundaries. They do not authorize later implementation.

## Current Chunk 2A workflow

Implemented server-rendered routes:

- `GET /app/` — criteria entry.
- `POST /app/confirm-inputs` — criteria validation and matrix-entry transition.
- `POST /app/preview` — matrix parsing, header mapping, value validation, and preview confirmation.
- `POST /app/compute` — confirmation-gated computation and top-ten result display.

Evidence:
- `app/routes/workflow.py`
- `app/templates/app_input.html`
- `app/templates/app_matrix.html`
- `app/templates/app_preview.html`
- `app/templates/app_results.html`
- `tests/test_app_workflow.py`
- `docs/decisions/chunk-2a-evidence.md`

## User journey

1. Open `/app/`.
2. Select criteria JSON or structured criteria form.
3. Submit criteria and provide a matrix.
4. Review header mapping, shape, validation messages, and sample rows.
5. Approve missing-cell replacement when needed.
6. Confirm the preview.
7. Submit compute and inspect the top-ten ranking with raw net-flow scores.

The app uses server-rendered HTML and no JavaScript. Math guidance uses semantic HTML notation. Documentation routes and compatibility JSON routes remain separate.

## Validation behavior

The shared contract is in `electre3/shared.py`:

- Criteria are a top-level list with one to eight records.
- Required fields: `name`, `weight`, `q`, `p`, `v`, `maximize`.
- `maximize` must be a strict Boolean.
- Weights must sum to one.
- Thresholds satisfy `0 ≤ q ≤ p ≤ v`.
- Matrix values are finite and normalized to `[0,1]`.
- Matrix row count is bounded at 100,000.
- Block size is an integer from 1 through 10,000; default 1,000.

Missing CSV values require explicit checkbox approval. The replacement value is bounded to `[0,1]` and defaults to `0`. Criteria JSON missing values are rejected.

## Current versus future behavior

Implemented in Chunk 2A:

- Server-rendered `/app` workflow.
- Preview and confirmation gate.
- Strict shared validation.
- Top-ten result view with raw net-flow scores.
- App no-JavaScript policy and CSP correction.

Not implemented in Chunk 2A:

- Canonical serializers and byte-identical artifacts.
- Result cache, download tokens, TTL, or downloads.
- Split artifacts and checksum manifests.
- Runtime feasibility benchmarking or 300/330-second enforcement.
- Production upload lifecycle and final cache controls.

Do not document these future features as available until their checkpoints and tests exist.

## CLI and web relationship

Both entry points are intended to use the shared contract and adapter:

- `electre3/shared.py::compute_validated_ranking`
- `electre3/cli_run.py::run_ranking`
- `electre3/ranking.py::compute_ranking`

The adapter returns ranking indices and `accumulator.net_flow()`. CLI output and web serialization are not yet byte-identical because canonical serializers are a later chunk.

## Debugging and verification

Run the focused Chunk 2A suite:

```bash
python -m pytest tests/test_app_workflow.py tests/test_preview_gate.py tests/test_security.py tests/test_security_headers.py tests/test_docs_routes.py -q
python -m compileall app electre3
```

Expected focused result at the Chunk 2A checkpoint: **235 passed**. The no-script scan found no `<script>` tags or inline event handlers in `app/templates/app_*.html`.

For failures, inspect the actionable validation message first. Then verify criteria order, matrix shape, finite values, score bounds, missing-value approval, and preview confirmation state. Do not bypass the shared validator.

## Tutorial-writing rules

- Label current Chunk 2A behavior separately from planned cache/serialization behavior.
- Use `/app/` routes only for the implemented workflow.
- Do not claim downloads, byte identity, split files, or runtime gates yet.
- Explain ranking indices and raw net-flow scores separately.
- Preserve the `Asset ID` display-label policy and header alignment rules.
- Cite source paths and test evidence in tutorial drafts.
