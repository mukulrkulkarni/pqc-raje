# Chunk 1 documentation notes for Technical Document Writer

**Purpose:** Durable source notes for future technical documentation. This file records verified current behavior and approved target behavior. It does not authorize implementation.

## Setup and installation

### Current implementation

- Use the repository Python environment and run commands from the repository root.
- Verify imports and bytecode compilation: `python -m compileall -q electre3 app`.
- Run focused strict-contract checks: `python -m pytest tests/test_shared_contract.py tests/test_cli_run.py tests/test_security.py -q`.
- The project currently has no new `/app` workflow installation procedure because that workflow is not implemented.

### Source evidence

- CLI entry point description: `web-app-requirements.txt`.
- Shared validator and adapter: `electre3/shared.py:validate_criteria`, `validate_score_matrix`, `compute_validated_ranking`.
- Existing CLI helper: `electre3/cli_run.py:run_ranking`.

## Matrix and criteria data contract

### Current implementation

- Criteria are a JSON-compatible list with one through eight entries.
- Every entry requires `name`, `weight`, `q`, `p`, `v`, and strict Boolean `maximize`.
- Weights must sum to `1` within `1e-12`.
- `CriterionConfig` enforces `weight > 0` and `0 <= q <= p <= v`.
- The compute matrix has two through 100,000 rows and exactly one column per criterion.
- Scores must be finite and normalized to `[0, 1]`.
- The adapter converts accepted matrices to contiguous `float64` before core ranking.

### Source evidence

- `electre3/shared.py:MAX_CRITERIA`, `MAX_ROWS`, `validate_criteria`, `validate_score_matrix`.
- `electre3/config.py:CriterionConfig`.
- Requirements contract: `web-app-requirements.txt`, “Data Model”.

## Converter-first CSV workflow

### Current implementation

- Convert CSV data before shared ranking validation with `scripts.convert_matrix_csv.convert_csv_to_matrix`.
- Numeric-only CSV conversion uses `convert_csv_to_matrix(path)`.
- For a headered CSV with an identifier column, use `convert_csv_to_matrix(path, has_header=True, id_col="id")`.
- The converter rejects non-rectangular rows, non-numeric cells, and empty cells unless an explicit finite `fill_empty` value is supplied.
- Converter output still requires shared score-domain validation before ranking.

### Headered CSV target contract

- A headered user matrix has one non-empty identifier header followed by criterion headers.
- Criterion headers must exactly match criteria names in criteria-list order.
- `electre3.shared.validate_csv_headers(headers, criteria)` enforces this mapping.
- The planned web preview shows the mapping before compute.

### Source evidence

- `scripts/convert_matrix_csv.py:convert_csv_to_matrix`.
- `tests/test_convert_matrix_csv.py`.
- `electre3/shared.py:validate_csv_headers`.
- `web-app-requirements.txt`, “CSV header policy”.

## CLI use, flags, and output semantics

### Current implementation

- The documented command shape is `python -m electre3.cli matrix.(csv|npy) criteria.json [options]`.
- `electre3.cli_run.run_ranking(matrix, criteria_data, block_size=1000, quiet=False)` is the verified helper API.
- It validates through the shared contract and returns ranking indices only.
- `electre3.shared.compute_validated_ranking(...)` returns both ranking indices and the raw net-flow vector.
- `block_size` defaults to 1,000 and must be an integer from 1 through 10,000.
- `quiet=False` prints “Computing ranking...” and “Done.”; it does not define a serialized result format.

### Ranking and net-flow interpretation

- Ranking is a permutation of zero-based alternative indices, ordered by the core ranking implementation.
- The canonical score vector is `accumulator.net_flow()` exposed as `ComputeResult.net_flow`.
- Higher or lower business desirability must be interpreted with the criterion `maximize` setting and domain context; do not label a net-flow value as a probability.
- Tied-item ordering has no specified guarantee.

### Source evidence

- `electre3/cli_run.py:run_ranking`, `format_preview`.
- `electre3/shared.py:ComputeResult`, `compute_validated_ranking`.
- `web-app-requirements.txt`, “Problem Statement” and invariant 1.

## Validation errors and debugging

### Current implementation

- Start with the validator error. It reports missing fields, bad types, bad weight totals, malformed thresholds, matrix shape mismatches, non-finite values, out-of-range scores, and invalid block sizes.
- Use `validate_criteria_json` only where an error string is required; it delegates to the same strict validator.
- Use `python -m pytest tests/test_shared_contract.py tests/test_cli_run.py tests/test_security.py -q` after a contract-related change.
- Use `python -m compileall -q electre3 app` after Python changes.
- For headered CSV, verify identifier header presence and exact ordered criterion names before conversion and compute.
- Do not bypass validators to debug core computation. First reduce to a two-row, normalized fixture with valid criteria.

### Source evidence

- `app/services/security.py:validate_criteria_json`.
- `electre3/shared.py` validation functions.
- `tests/test_shared_contract.py`, `tests/test_cli_run.py`, `tests/test_security.py`.

## Web workflow: current status and approved target

### Current implementation

- No approved new `/app` routes are implemented in this chunk.
- Do not document `/app/`, `/app/confirm-inputs`, `/app/preview`, or `/app/compute` as available endpoints.
- No new cache, serializer, download, session-result, or split-artifact implementation exists in this chunk.
- Existing JSON/AJAX-shaped routes are not the approved replacement workflow.

### Approved future target

- The intended local, server-rendered, no-JavaScript workflow is `/app/` → `/app/confirm-inputs` → `/app/preview` → `/app/compute`.
- It must use semantic HTML math notation, not KaTeX.
- Preview validates criteria, CSV mapping, matrix values, and confirmation before compute.
- The planned compute step uses the same shared adapter as CLI.
- Planned limits include 100 MiB uploads, 100,000 rows, eight criteria, a 300-second feasibility gate, and a 330-second hard timeout.
- Planned session/cache behavior is latest-only process memory, single worker, 30-minute TTL and session lifetime, 32 MiB total cache, 16 MiB per artifact, and no matrix/result/token data in cookies.

### CLI-versus-web caveats

- Shared validation and core computation are current; byte-identical CLI/web serialization remains future work.
- CLI helper output is a Python ranking array; the approved web result page, download formats, manifests, checksums, and rate limit are unimplemented.
- Header mapping UI, missing-value approval UI, preview gate, and result downloads are target behavior, not current behavior.

### Source evidence

- `web-app-requirements.txt`, “Workflow”, invariants 1–4, and data model.
- `docs/decisions/web-app-design-meeting-report.md`.
- `docs/decisions/web-app-implementation-milestones.md`, milestones 2–4.
- `electre3/shared.py:compute_validated_ranking`.

## Documentation constraints

- State “current implementation” and “approved target” separately.
- Do not claim implemented routes, cache, serializers, downloads, byte identity, feasibility timing, or split artifacts before verified implementation evidence exists.
- Describe app math with semantic HTML (`var`, `sub`, `sup`, and entities); do not introduce JavaScript or a build step.
