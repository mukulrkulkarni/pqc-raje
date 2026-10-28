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

## Cross-page link audit result

`out/d8_link_audit.py` examines local Markdown targets and Markdown fragments for `README.md`, D3-D7 decision documents, the quickstart, and the debugging runbook. It intentionally ignores external URLs and anchor-only links. It found:

1. `d3-phase1-content-draft.md`: `docs/tutorials/cli_quickstart.md` missing relative to document directory.
2. `d3-phase1-content-draft.md`: `docs/modules/index.html` missing relative to document directory.
3. `d3-phase1-content-draft.md`: `docs/runbook/debugging.md` missing relative to document directory.
4. `d5-mental-model-draft.md`: `../../examples/d4_phase2/` is a directory, not a local file target.
5. `d5-mental-model-draft.md`: `../../electre3/` is a directory, not a local file target.
6. `d5-mental-model-draft.md`: `../../tests/d4_checks/` is a directory, not a local file target.

Existing `tests/test_local_document_links.py` passes and includes positive, missing-file, missing-fragment, external-link, and anchor-only edge checks. Its scope is remediation records plus D7, so it does not cover the full D3-D7 set audited here.

## Claim ledger

| Claim | Status | Evidence |
|---|---|---|
| D4-D7 focused documentation checks pass | verified | 40 passed command above |
| Full repository suite passes | verified | 1060 passed command above |
| CLI contract produces documented example ranking | verified | Positive CLI command |
| Invalid block size is rejected | verified | Negative CLI command |
| Converted NumPy data uses positional IDs | verified | Edge converter command |
| Generated tutorial ownership remains intact | verified | Website build, D7 tests, source/output review |
| Browser and assistive-technology behavior is verified | unresolved/deferred | Approved non-blocking limitation; no browser evidence executed |
| D3-D7 local Markdown targets all resolve | rejected | Six failures from D8 link audit |

## Review and release decision

Scientific, Engineering, and UI/UX reviews are recorded in [D8 release audit](d8-documentation-release-audit.md#review-record). The final documentation release gate is blocked only by the six historic draft-link defects or a formal exclusion decision. Browser limitations remain deferred and non-blocking.
