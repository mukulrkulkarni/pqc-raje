# D3 Phase 1 Execution Notes

**Status:** Placement and testing complete. UI/UX review, Scientific/Engineering final checks, PI stage-end acceptance, and commit remain pending. No commit was created. UI/UX approval from the prior correction is not approval of the current corrected worktree; fresh UI/UX review remains required.

## Scope and authority

- Source authority followed: implementation and tests, then approved decisions, then tutorials/runbooks, then companion website summaries.
- Editable user-facing targets: `README.md`, `docs/GETTING_STARTED.html`, `website/index.html`, and `website/app/index.html`.
- `scripts/build_website.py` confirms these website landing files are source-owned and only normalizes configured domains. Module pages are generated from `docs/modules/` and were not edited.
- No install command was added. The original `pip install electre3` claim was removed from the edited landing sources because it is not an approved, reproducibly tested repository command.

## Placement and layout changes

- Added a root `README.md` Phase 1 entry with the verified Asset Priority CLI path, local-app route, recovery boundary, and documentation map.
- Rebuilt `docs/GETTING_STARTED.html` as an accessible Phase 1 entry with CLI and local-web tasks, semantic math, visible focus indicators, responsive layout, and an explicit review status.
- Rebuilt companion `website/index.html` as a concise orientation page using the same verified CLI path.
- Rebuilt `website/app/index.html` to describe the local app task and its evidence boundary.
- Used the MK-TII template’s Arial, purple `#6400FF`, navy `#253746`, and aqua `#7EDDD3` tokens. No scripts, external assets, or app templates changed.

## Independent verbatim command evidence

| Category | Command | Actual result | Limitation |
|---|---|---|---|
| Positive setup | `python -m compileall -q electre3 app` | Exit 0; no output. | Compilation does not run application behavior. |
| Positive CLI conversion | `python scripts/convert_matrix_csv.py examples/assets_priority/matrix_with_headers.csv out/assets_priority_cli.npy --has-header --id-col Asset` | Exit 0; `OK: 3x3 float64 saved to out\assets_priority_cli.npy`. | Creates a local derived `.npy` output. |
| Positive CLI ranking | `python -m electre3.cli out/assets_priority_cli.npy examples/assets_priority/criteria.json -y` | Exit 0; `Alt 1`, `Alt 0`, `Alt 2`. | Applies only to committed sample inputs. |
| Build/integration | `python scripts/build_website.py` | Exit 0; no output. | Static build only; no browser rendering. |
| Negative input | `python scripts/convert_matrix_csv.py examples/assets_priority/matrix_with_headers.csv out/assets_priority_invalid.npy --has-header --id-col Missing` | Exit 2; `Error: ID column 'Missing' not found in header`. | One invalid-header variant only. |
| Focused positive/negative/edge suite | `python -m pytest tests/test_convert_matrix_csv.py tests/test_cli_run.py tests/test_integration.py tests/test_docs_routes.py tests/test_website_static.py tests/test_security.py tests/test_security_headers.py tests/test_shared_contract.py tests/test_preview_gate.py tests/test_result_cache.py tests/test_serialization.py tests/test_local_document_links.py tests/test_ui_styles.py -q` | Exit 0; `340 passed in 3.59s`. | Includes existing coverage, not a live-browser test. |
| Scientific and negative suite | `python -m pytest tests/test_negative.py tests/test_validate.py tests/test_validate_deep.py tests/test_block.py tests/test_ranking.py tests/test_end_to_end_composition.py -q` | Exit 0; `77 passed in 0.55s`. | Does not independently prove every scientific assertion. |
| Full regression | `python -m pytest -q` | Initial exit 0: `928 passed in 8.22s`; final exit 0 after final placement: `932 passed in 8.95s`. | Test suite is not UI/UX approval. |
| Final documentation regression | `python -m pytest tests/test_d3_phase1_docs.py tests/test_docs_routes.py tests/test_website_static.py -q` | Exit 0; `194 passed in 2.28s`. | Static checks cannot verify browser reflow or assistive technology. |

## Test inventory and evidence interpretation

- **Unit/examples:** Verified compilation, CSV conversion, CLI result, and D3 page command consistency.
- **Integration:** Website build and CLI pipeline passed; focused tests cover docs routes and preview gates.
- **Scientific:** Existing threshold, ranking, block, validation, and end-to-end tests passed (`77`). Raw net flow and tie wording are conservative.
- **Security:** Focused suite passed security headers and route/path controls. New pages retain restrictive meta CSP and add no scripts or external assets.
- **UI/accessibility:** Static checks verify viewport, primary navigation labels, semantic `<var>`/`<sub>`, CSP, and focus-visible styling. A dedicated UI/UX review is still mandatory.
- **Links/offline:** Existing focused link/static suite passed. Browser network-disabled route/assets testing was not performed in this chunk.
- **Performance/cache/serialization:** Existing focused tests passed. No new runtime, cache, download, or serialization behavior was introduced.
- **Reproducibility:** Every documented command listed above was executed verbatim. The `dev_local.py` server command was not run to avoid starting a persistent local service; its local-app guidance therefore has source-and-test, but not live-server, evidence in this chunk.

## Failures and recovery

1. The first focused suite failed because the rewritten landing lacked the pre-existing `Quick Start` marker.
2. After restoring it, the suite failed because it lacked the pre-existing `multi-criteria` wording.
3. Both defects were fixed in page content; no assertions were weakened. The rerun passed `340` tests.

## D3 UI/UX correction gate

This bounded correction implements exactly five UI/UX gate items without modifying app templates, routes, JavaScript contracts, or generated module sources.

1. Changed the three overview-card headings in `website/index.html` from `<h2>` to `<h3>` and matched the card selector.
2. Removed the placeholder external `https://app.pqcmig.scoring.draft/` link from `website/app/index.html`; the documented repository-local route remains.
3. Added explicit `Review status` text to `website/app/index.html`: Phase 1 app guidance is under D3 review and makes no release-readiness claim.
4. Replaced the `Chosen` and `Near-miss` headings in `docs/tutorials/cli_quickstart.md` with one plain rationale paragraph.
5. Standardized the inline CSS token vocabulary and spacing names across `docs/GETTING_STARTED.html`, `website/index.html`, and `website/app/index.html`: `--color-*`, `--font-*`, and `--space-*`.

| Category | Command | Actual result | Limitation |
|---|---|---|---|
| Focused positive/link/UI | `python -m pytest tests/test_d3_phase1_docs.py tests/test_docs_routes.py tests/test_website_static.py tests/test_local_document_links.py -q` | Exit 0; `200 passed in 1.91s`. | Static tests do not render pages. |
| Static build | `python scripts/build_website.py` | Exit 0; no output. | Build does not launch a service or validate browser interaction. |
| Negative/edge regression | `python -m pytest tests/test_negative.py tests/test_validate.py tests/test_validate_deep.py tests/test_block.py tests/test_ranking.py tests/test_end_to_end_composition.py -q` | Exit 0; `77 passed in 0.52s`. | Existing scientific coverage does not prove rendered layout. |
| UI/security regression | `python -m pytest tests/test_d3_phase1_docs.py tests/test_ui_styles.py tests/test_website_static.py tests/test_local_document_links.py tests/test_security_headers.py -q` | Exit 0; `49 passed in 0.92s`. | No browser or assistive-technology session occurred. |
| Diff hygiene | `git diff --check` | Exit 0. | Git reported existing LF-to-CRLF warnings for two edited documentation files. |
| Placeholder negative check | `findstr /S /I /N /C:"app.pqcmig.scoring.draft" website\\app\\index.html && exit /b 1 || exit /b 0` | Exit 0; no match. | Checks only the specified placeholder domain. |

A final ad hoc Python static assertion command failed before executing because the Windows shell passed a malformed quoted `-c` argument (`SyntaxError: unterminated string literal`). It was not retried because the equivalent assertions are covered by the passing focused test suite. No tests were weakened.

## D3 final-gate correction (current checkpoint)

- **UI/UX approval record:** The preceding UI/UX static review approved the five earlier correction items with no must-fix findings. This correction changes app-landing styling and evidence wording, so a fresh UI/UX re-review is mandatory and pending. Do not treat the prior approval as approval of this corrected worktree.
- **Execution environment:** Windows workspace; Python `3.11.2`; repository revision `054678ef4d5f3f721c7e3d7cc5b6ada155812089` before this uncommitted correction. No persistent local application was launched.
- Corrected `docs/tutorials/cli_quickstart.md`: the CLI validates finite matrix scores in `[0,1]`, prints ranking indices only, and saves ranking indices only. It does not print or save net-flow scores.
- Matched `website/app/index.html` to `website/index.html` landing-page style rules for width, navigation/actions, hero, heading scale, responsive breakpoint, tokens, focus treatment, and no-JavaScript delivery.
- Named browser zoom explicitly: browser reflow, browser zoom, keyboard, offline, and screen-reader evidence remain **unverified**.
- Preserved unrelated `out/engineering-tree.txt` without deletion at `out/audit/preserved-unrelated/engineering-tree.txt`; it remains outside the D3 content scope.

| Category | Command | Actual result | Limitation |
|---|---|---|---|
| Positive/UI/link/static | `python -m pytest tests/test_d3_phase1_docs.py tests/test_docs_routes.py tests/test_website_static.py tests/test_local_document_links.py tests/test_ui_styles.py tests/test_security_headers.py -q` | Exit 0; `232 passed in 2.50s`. | Static checks do not render a browser page. |
| Negative/edge score contract | `python -m pytest tests/test_shared_contract.py tests/test_cli_run.py tests/test_negative.py tests/test_validate.py tests/test_validate_deep.py -q` | Exit 0; `77 passed in 0.61s`. | Does not replace a live-app session. |
| Compile/diff | `python -m compileall -q electre3 app && git diff --check` | Exit 0; no errors. | Git emitted existing LF-to-CRLF warnings for two documentation files. |
| Static build | `python scripts/build_website.py` | Exit 0; no output. | Does not launch a local service. |
| Independent positive verbatim commands | `python scripts/convert_matrix_csv.py examples/assets_priority/matrix_with_headers.csv out/assets_priority_cli.npy --has-header --id-col Asset && python -m electre3.cli out/assets_priority_cli.npy examples/assets_priority/criteria.json -y` | Exit 0; converted `3x3`; ranked `Alt 1`, `Alt 0`, `Alt 2`. | Sample-only evidence. |
| Independent negative command | `python scripts/convert_matrix_csv.py examples/assets_priority/matrix_with_headers.csv out/assets_priority_invalid.npy --has-header --id-col Missing` | Exit 2; `Error: ID column 'Missing' not found in header`. | Tests one invalid header. |
| Independent repeat | `python -m pytest tests/test_d3_phase1_docs.py -q && python -m compileall -q electre3 app && python scripts/build_website.py` | Exit 0; `9 passed in 0.09s`; compile/build silent. | Static evidence only. |

## Evidence limits and blockers

- No verified browser reflow, browser zoom, keyboard traversal, offline, or screen-reader evidence exists. The pages state this limit and do not claim those checks passed.
- UI/UX re-review of this corrected worktree is the mandatory next gate. Do not commit before its approval.
- Scientific and Engineering final gates remain required after UI/UX re-review. PI stage-end acceptance remains required after those gates.
- `out/audit/preserved-unrelated/engineering-tree.txt` is unrelated, preserved, and outside the approved D3 content scope.
- This execution created `out/assets_priority_cli.npy` and `out/assets_priority_invalid.npy` as ignored derived command outputs. They are not staged or committed.
