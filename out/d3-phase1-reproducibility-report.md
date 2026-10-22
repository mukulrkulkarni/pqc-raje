# D3 Phase 1 independent reproducibility report

**Gate result: BLOCKED**

## Scope and non-modification statement

- Run date: 2026-10-22.
- Repository revision: `b1d594b0f5e59ce8290f556204e1546dd0763dd0` (`b1d594b reconcile-d3-gate-status`).
- OS/workspace: Windows workspace (`C:\Users\Mukul.Kulkarni\InnoviumAI\Projects\IP Address Analysis Plan`).
- Python: `Python 3.11.2`.
- Test runner: `pytest 9.1.1`.
- No application, documentation, or tracked files were edited. No commit was created. `review_snapshot/` was not read, altered, deleted, staged, or committed.
- This uncommitted report and generated `out/d3-repro-assets.npy` are gate artifacts.

## Authoritative instructions inspected

- `docs/decisions/d3-phase1-execution-notes.md`
- `docs/decisions/d3-phase1-content-draft.md`

The execution notes name `scripts/build_website.py` as the build authority and require compile, conversion/ranking, build, focused documentation/UI/link/security tests, and positive/negative/edge evidence.

## Positive results

| Command | Exit | Actual output / result |
|---|---:|---|
| `python -m compileall -q electre3 app` | 0 | No output. |
| `python scripts/convert_matrix_csv.py examples/assets_priority/matrix_with_headers.csv out/d3-repro-assets.npy --has-header --id-col Asset` | 0 | `OK: 3x3 float64 saved to out\d3-repro-assets.npy` |
| `python -m electre3.cli out/d3-repro-assets.npy examples/assets_priority/criteria.json -y` | 0 | `Computing ranking...`; `Done.`; ranking: `1. Alt 1`, `2. Alt 0`, `3. Alt 2`. |
| `python scripts/build_website.py` | 0 | No output. |
| `python -m pytest -q tests/test_d3_phase1_docs.py tests/test_docs_routes.py tests/test_local_document_links.py tests/test_ui_styles.py tests/test_website_static.py tests/test_security_headers.py tests/test_convert_matrix_csv.py tests/test_preview_gate.py tests/test_negative.py` | 0 | `283 passed in 2.59s`. |
| `python -m pytest -q tests/test_app_workflow.py tests/test_cli_run.py tests/test_shared_contract.py tests/test_serialization.py tests/test_result_cache.py` | 0 | `60 passed in 0.99s`. |

The conversion/ranking result agrees with the documented `Alt 1`, `Alt 0`, `Alt 2` sequence. These commands did not launch a persistent local service.

## Negative result

| Command | Exit | Actual output / result |
|---|---:|---|
| `python scripts/convert_matrix_csv.py examples/assets_priority/matrix_with_headers.csv out/d3-repro-invalid.npy --has-header --id-col MissingHeader` | 2 | stderr: `Error: ID column 'MissingHeader' not found in header` |

This confirms the invalid identifier-header path rejects the input. The failure did not produce a success artifact.

## Edge and scope results

- The focused suites include CSV conversion, preview-gate, negative, cache, serialization, and workflow coverage; all 343 selected tests passed.
- The command uses the documented three-row, three-criterion headered CSV input and removes its identifier column correctly.
- `git diff --check` exited 0 before and after runs.
- Initial and final repository status reported only `?? review_snapshot/`; this pre-existing untracked directory remains preserved.

## Stale, incorrect, or insufficient instructions

1. The execution-note recorded count, `focused 232`, is stale for current HEAD: the independently selected focused documentation/UI/link/security command passed **283**, not 232.
2. `docs/decisions/d3-phase1-content-draft.md` still says `Scientific and Engineering gates are pending` and `No user-facing pages changed`; these statements conflict with `docs/decisions/d3-phase1-execution-notes.md`, which reports placement/testing completed and approved UI/UX, Scientific, and Engineering gates. Its status language is stale.
3. The content draft instructs `python scripts/dev_local.py`; this starts persistent local services. It was deliberately not run under this gate instruction. The static/Flask test suites do not replace browser reflow, browser zoom, keyboard traversal, offline navigation, or screen-reader testing.
4. The execution notes name the website build authority but do not state its exact invocable build command. `python scripts/build_website.py` is executable at current HEAD and exited 0, but the notes should publish that command explicitly.

## Blocking limitation and conclusion

The repository cannot make a clean-tree final-gate claim: `review_snapshot/` remains untracked. The execution notes themselves say it must be resolved before a final clean-tree claim. Browser reflow, zoom, keyboard, offline, and screen-reader evidence also remain unverified as documented. Therefore the independent D3 Phase 1 reproducibility gate is **BLOCKED**, despite all executed compile, conversion/ranking, build, focused test, invalid-header, and selected edge coverage passing.
