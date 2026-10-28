# D8 Documentation Evidence

**Date:** 2026-10-28
**Scope:** Independent D3-D7 documentation release-audit evidence.
**Environment:** Python 3.11.2; pytest 9.1.1; commands run from repository root.

## Source manifest and reproducibility

| ID | Source | Authority | Verified use |
|---|---|---|---|
| S1 | `docs/decisions/d3-*` through `d7-*` | D3-D7 provenance | Status, ownership, labels, and prior evidence |
| S2 | `README.md`, `docs/tutorials/cli_quickstart.md`, `docs/runbook/debugging.md` | User-facing repository documentation | Commands and data-contract wording |
| S3 | `scripts/build_website.py`, `website/`, `docs/modules/` | Generation contract | Source/output ownership and routes |
| S4 | `tests/test_d4_fixture_correction.py`, `tests/test_d5_placement.py`, `tests/test_d6_placement.py`, `tests/test_d7_website_integration.py`, `tests/test_local_document_links.py`, `tests/test_website_static.py` | Executable verification | D4-D7 regressions, links, routes, ownership |
| S5 | `electre3/cli.py` and committed example inputs | Implementation and fixtures | CLI behavior and validation |

Inputs are repository-local. No external service, package installation, remote Git, tag creation, or application-code modification occurred. `out/d8_link_audit.py` is the deterministic local audit helper; it is a checkpoint artifact, not application code.

## Executed evidence

| Category | Command | Result |
|---|---|---|
| Environment | `python --version && python -m pytest --version && python -m pytest --collect-only -q` | Python 3.11.2; pytest 9.1.1; 1060 tests collected in 1.51s. |
| Compile/build/diff | `python -m compileall -q electre3 app scripts && python scripts/build_website.py && git diff --exit-code -- website docs` | Passed; build did not alter tracked website or documentation before D8 records. |
| Positive CLI | `python -m electre3.cli examples/assets_priority/matrix_with_headers.csv examples/assets_priority/criteria.json -y` | Exit 0; `B`, `A`, `C` ranking. |
| Negative CLI | `python -m electre3.cli examples/assets_priority/matrix_with_headers.csv examples/assets_priority/criteria.json -b 0 -y` | Exit 1; `Error: block_size must be between 1 and 10000`. |
| Edge converter | `python scripts/convert_matrix_csv.py examples/assets_priority/matrix_with_headers.csv out/d8-assets.npy --has-header --id-col Asset && python -m electre3.cli out/d8-assets.npy examples/assets_priority/criteria.json -y` | Exit 0; generated `3x3 float64`; output identifiers `1`, `0`, `2`, confirming documented positional NumPy IDs. Temporary output removed. |
| D4 reproduction | `python out/generate_d4_fixture_evidence.py && python -m pytest -q tests/test_d4_fixture_correction.py` | Exit 0; deterministic tie evidence printed; 8 passed in 4.56s. |
| D4-D7 focused tests | `python -m pytest -q tests/test_d4_fixture_correction.py tests/test_d5_placement.py tests/test_d6_placement.py tests/test_d7_website_integration.py tests/test_local_document_links.py tests/test_website_static.py tests/d5_checks/test_reproducibility.py` | Exit 0; 40 passed in 6.95s. Includes static/Flask route separation and traversal-shaped 404 assertions. |
| Full suite | `python -m pytest -q` | Exit 0; 1060 passed in 27.13s. |
| Static checks | `python -m json.tool out/d8-checkpoint.json > NUL && git diff --check && git diff --exit-code -- docs website` | Exit 0 before D8 document creation; checkpoint JSON valid and no whitespace/doc/website drift. |
| Cross-page audit | `python out/d8_link_audit.py` | Exit 1; audited 18 files and found six targets listed below. This is the release-blocking negative result. |

## Initial cross-page link audit result

`out/d8_link_audit.py` examines local Markdown targets and Markdown fragments for `README.md`, D3-D7 decision documents, the quickstart, and the debugging runbook. It intentionally ignores external URLs and anchor-only links. Its initial run found:

1. `d3-phase1-content-draft.md`: `docs/tutorials/cli_quickstart.md` missing relative to document directory.
2. `d3-phase1-content-draft.md`: `docs/modules/index.html` missing relative to document directory.
3. `d3-phase1-content-draft.md`: `docs/runbook/debugging.md` missing relative to document directory.
4. `d5-mental-model-draft.md`: `../../examples/d4_phase2/` is a directory, not a local file target.
5. `d5-mental-model-draft.md`: `../../electre3/` is a directory, not a local file target.
6. `d5-mental-model-draft.md`: `../../tests/d4_checks/` is a directory, not a local file target.

Existing `tests/test_local_document_links.py` initially passed and included positive, missing-file, missing-fragment, external-link, and anchor-only edge checks. Its scope initially excluded the full D3-D7 set audited here.

## Historical-link remediation evidence

The remediation preserves the initial negative result above. The current D3 and D5 changes, target classifications, regression expansion, review confirmations, and exact acceptance results are recorded in [D8 historical-link remediation notes](d8-historical-link-remediation-notes.md). The acceptance commands are rerun after these edits; their actual results are appended below.

## Remediation acceptance evidence

| Category | Command | Actual result |
|---|---|---|
| Local-link audit | `python out/d8_link_audit.py` | Exit 0; `audited_files=18 local_link_errors=0`. |
| D4-D7 focused suites | `python -m pytest -q tests/test_local_document_links.py tests/test_d4_fixture_correction.py tests/test_d5_placement.py tests/test_d6_placement.py tests/test_d7_website_integration.py tests/test_website_static.py tests/d5_checks/test_reproducibility.py` | Exit 0; 42 passed in 6.88s. Includes positive, missing-file, missing-fragment, external-link, anchor-only, and historic D3/D5 link cases. |
| Full suite | `python -m pytest -q` | Exit 0; 1062 passed in 27.08s. |
| Compile/build/diff/JSON | `python -m compileall -q electre3 app scripts && python scripts/build_website.py && git diff --check && git diff --exit-code -- website && python -m json.tool out/d8-checkpoint.json > NUL` | Exit 0. Build produced no website drift; diff and checkpoint JSON checks passed. |
| Independent reproducibility | `python out/d8_link_audit.py` in a separate command invocation after the focused suite | Exit 0; `audited_files=18 local_link_errors=0`. |

## Claim ledger

| Claim | Status | Evidence |
|---|---|---|
| D4-D7 focused documentation checks pass | verified | 42 passed remediation command above |
| Full repository suite passes | verified | 1062 passed remediation command above |
| Generated tutorial ownership remains intact | verified | Build, D7 tests, and no website drift |
| D3-D7 local Markdown targets all resolve | verified | Two zero-error independent local-link audits |
| D3 unavailable module-index target has a destination | explicitly unavailable | Historical/planned classification; no destination invented |
| Browser and assistive-technology behavior is verified | unresolved/deferred | Approved non-blocking limitation; no browser evidence executed |

## Review and release decision

Scientific, Engineering, and UI/UX confirmations are recorded in [D8 release audit](d8-documentation-release-audit.md#review-record) and [D8 historical-link remediation notes](d8-historical-link-remediation-notes.md#review-confirmation). The historical-link blocker is cleared. D8 is ready for the final documentation release gate. Browser limitations remain deferred and non-blocking.
