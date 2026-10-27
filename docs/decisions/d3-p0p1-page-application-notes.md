# D3 P0/P1 Page Application Notes

**Status:** Applied and locally verified; Engineering and Scientific reviews approved for this bounded documentation scope.
**Base revision:** `d3d11bb` (`checkpoint-d3-p0p1-approved-draft`).
**Scope:** Documentation and documentation tests only. No application code or DC4.5 edits occurred.

## Applied corrections

- `docs/runbook/debugging.md` now identifies `/app/` as the supported server-rendered workflow.
- The runbook documents that a missing successful preview or `confirm_compute` at `POST /app/compute` returns HTTP 400.
- The runbook labels `/preview/<upload_id>`, its confirm/cancel variants, `/compute/start`, `/compute/status/<job_id>`, `preview.html`, and `config.html` as legacy compatibility-only surfaces.
- The runbook retains the legacy conditional: an unconfirmed valid JSON upload at `POST /compute/start` returns HTTP 403.
- `docs/tutorials/cli_quickstart.md`, `docs/GETTING_STARTED.html`, and `website/index.html` explain that direct CSV labels (`B`, `A`, `C`) and converted NumPy identifiers (`1`, `0`, `2`) describe the same committed-sample ordering.
- The pages state that `1`, `0`, and `2` are zero-based identifiers, not one-based rank positions.

## Source basis

- `app/routes/workflow.py` implements the `/app/` preview and confirmation gate.
- `app/routes/compute.py::start_computation` returns HTTP 403 after a supplied but unconfirmed legacy upload identifier.
- `app/routes/preview.py` owns the legacy preview confirmation route.
- `electre3/data.py::load_input` distinguishes identifier-bearing CSV from numeric NumPy input.
- `scripts/convert_matrix_csv.py::convert_csv_to_matrix` removes the selected identifier column.
- `electre3/ranking.py::compute_ranking`, `electre3/accumulator.py::NetFlowAccumulator`, and `electre3/block.py::compute_block` support the documented ranking method.

## Executed evidence

| Category | Command | Result |
|---|---|---|
| Positive/reproducibility | `python -m compileall -q electre3 app` | Exit 0 |
| Positive/reproducibility | `python -m electre3.cli examples/assets_priority/matrix_with_headers.csv examples/assets_priority/criteria.json -y` | Exit 0; direct CSV output ranks `B`, `A`, `C` |
| Positive/reproducibility | `python scripts/convert_matrix_csv.py examples/assets_priority/matrix_with_headers.csv out\d3-p0p1-matrix.npy --has-header --id-col Asset` | Exit 0 |
| Positive/reproducibility | `python -m electre3.cli out\d3-p0p1-matrix.npy examples/assets_priority/criteria.json -y` | Exit 0; converted NumPy output ranks `1`, `0`, `2` |
| Positive/negative/edge/link | `python -m pytest -q tests/test_d3_p0p1_page_application.py tests/test_d3_phase1_docs.py tests/test_app_workflow.py tests/test_convert_matrix_csv.py tests/test_cli_run.py tests/test_docs_routes.py` | Exit 0; 230 passed in 2.13s |
| Focused documentation contract | `python -m pytest -q tests/test_d3_p0p1_page_application.py` | Exit 0; 5 passed in 0.52s |
| Full deterministic regression | `python -m pytest -q tests/` | Exit 0; 952 passed in 16.40s |

`tests/test_d3_p0p1_page_application.py` covers supported and legacy status codes, direct/converted label reconciliation, tie and browser-evidence wording, local in-page links, and reproducibility citations. Existing workflow, converter, CLI, and documentation suites cover malformed inputs, missing preview/confirmation, invalid headers and values, conversion failures, and route security cases.

## Required reviews

### Engineering review — APPROVED

- The diff is documentation plus one focused documentation-contract test; it does not edit application code.
- Test-client assertions confirm the supported `/app/compute` missing-preview gate returns 400 and an unconfirmed legacy JSON flow returns 403.
- The focused and full suites passed as recorded above.
- `git diff --check` exited 0 before commit.

### Scientific review — APPROVED

- Direct CSV preserves the committed source labels `B`, `A`, `C`; converted numeric NumPy input uses positional identifiers `1`, `0`, `2` for that ordering.
- The text distinguishes identifiers from rank positions and avoids presenting tied alternatives as scientifically distinct.
- The method remains ELECTRE III credibility followed by descending raw net flow; scores are not normalized after input validation.

## Limitations

- Browser rendering, keyboard execution, zoom, reflow, offline navigation, load, and screen-reader evidence remain deferred and non-blocking.
- The static and Flask test-client checks do not establish browser or assistive-technology behavior.
- No remote Git operation, persistent service, UI/UX review, or DC4.5 change was performed. UI/UX review was not required because navigation and layout were unchanged.
