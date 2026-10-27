# D4 line-policy remediation notes

**State:** D4 review-recovery evidence is complete; required independent Scientific and Engineering reviews are pending.  
**Scope:** D4 converter and regressions only. No production pages, remote Git, or commit.

## Line-count rule

The audit uses nonblank, non-comment physical source lines and excludes module, class, and function docstring lines through AST parsing.

| Path | Executable lines | Result |
|---|---:|---|
| `scripts/convert_matrix_csv.py` | 20 | Pass |
| `scripts/matrix_csv/cli.py` | 36 | Pass |
| `scripts/matrix_csv/core.py` | 50 | Pass |
| `scripts/matrix_csv/errors.py` | 2 | Pass |
| `scripts/matrix_csv/input.py` | 25 | Pass |
| `tests/test_d4_fixture_correction.py` | 3 | Pass |
| `tests/d4_checks/test_edges.py` | 29 | Pass |
| `tests/d4_checks/test_evidence.py` | 29 | Pass |
| `tests/d4_checks/test_parity.py` | 18 | Pass |
| `tests/d4_checks/test_raw_flow.py` | 31 | Pass |
| `out/generate_d4_fixture_evidence.py` | 50 | Pass |
| `out/d4_line_policy_audit.py` | 37 | Pass |
| `scripts/build_website.py` | 112 | Existing exception; unchanged |

`build_website.py` is outside this remediation scope. Its 112 executable lines exceed the strict policy, but this work neither modified nor relied on it. A separate approved remediation is required before any future edit to that module.

## Evidence

| Category | Command | Actual result |
|---|---|---|
| Line policy | `python out\d4_line_policy_audit.py` | All D4 changed/added Python paths pass at 50 lines or fewer; `scripts/build_website.py` is the unchanged documented exception. |
| Positive and parity | `python -m pytest -q tests\test_d4_fixture_correction.py tests\test_convert_matrix_csv.py tests\test_dc4_cli_converter_migration.py tests\test_local_document_links.py` | `37 passed` in the final recovery run; the earlier pre-recovery run had 36 passed. |
| Negative | Same focused command | Covers nonnumeric cells, missing files, malformed header, missing link target, and missing fragment. |
| Edge | Same focused command | Covers empty fills, NaN/Inf rejection, CR line endings, exact/near ties, threshold boundaries, and veto. |
| Full suite | `python -m pytest -q tests` | `968 passed` in the final recovery run; the earlier pre-recovery run had 966 passed. |
| Compilation | `python -m compileall -q electre3 app scripts out\generate_d4_fixture_evidence.py out\d4_line_policy_audit.py` | Exit 0. |
| Diff integrity | `git diff --check` | Exit 0. |

## Design

The public converter facade remains at `scripts/convert_matrix_csv.py`. Cohesive CSV input, numeric validation, and CLI output helpers moved into `scripts/matrix_csv/`. The D4 test facade continues to collect the same checks while fixture evidence, parity, and edge/link checks each occupy bounded modules. The converter inserts the repository root for documented direct-script invocation; parity tests exercise direct CSV and converter/NumPy ranking paths.

## Reviews and limitations

- **Engineering Critic:** pending independent review of the recovery correction.
- **Scientific Critic:** pending independent review of raw-flow recomputation and tutorial claims.
- No commit occurred because both reviews are mandatory gates.
- Test, compilation, and diff evidence must be rerun after review approval.
- Browser, accessibility, zoom, reflow, offline, and load evidence remain deferred and non-blocking.
