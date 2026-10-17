# Phase 6 Credibility Review — Engineering Gate

Decision: **NEEDS WORK**

## Evidence used (snapshots required)
- docs/design/phase6/credibility_review/REQUEST.md
- docs/design/phase6/credibility_review/manifest.json
- docs/design/phase6/credibility_review/snapshot/docs/modules/credibility_tutorial_side_by_side.html
- docs/design/phase6/credibility_review/snapshot/tests/test_credibility_deep.py
- docs/design/phase6/credibility_review/snapshot/tests/test_module_docs.py

## Executed tests (this review)
Static inspection is separated from executed evidence.

Executed (pytest):
- `docs/design/phase6/credibility_review/snapshot/tests/test_credibility_deep.py::test_execute_example_matches_displayed_table` — PASS
- `...::test_formula_contract_boundaries` — PASS
- `...::test_lowlevel_invalid_inputs_are_not_silently_called_valid` — PASS
- `...::test_link_validation_negatives` — PASS

Not executed:
- Full suite / “88-test” preflight: only referenced from REQUEST.md; not re-run here.

## Key findings (batched)

### 1) Snapshot tests are not self-contained (BLOCKER for snapshot fidelity)
File: docs/design/phase6/credibility_review/snapshot/tests/test_credibility_deep.py
- `test_style_notation_and_sample_remain_consistent` fails in snapshot-only context because it reads:
  - `snapshot/docs/modules/concordance_tutorial_side_by_side.html` (missing)
  - `snapshot/docs/modules/discordance_tutorial_side_by_side.html` (missing)
- `test_source_excerpts_and_highlights_are_exact` fails because it reads `snapshot/electre3/credibility.py` (missing).
- `test_all_local_links_and_http_targets` fails because it requires linked module files like `snapshot/docs/modules/block_tutorial_side_by_side.html` (missing).

Impact:
- The pinned snapshot set cannot be validated end-to-end as provided.
- Review must fall back to **live** docs/modules and live electre3 sources for those checks, which violates the “EXACT snapshots” intent.

### 2) Example execution vs visible table parity exists and is enforced
File: snapshot/tests/test_credibility_deep.py
- `test_execute_example_matches_displayed_table` executes the tutorial’s embedded code and compares to the HTML table (including Fraction parsing for “7/18 ≈ ...”).
- This test passed when run.

### 3) Positive + negative link validation present, but snapshot link integrity cannot be proven
File: snapshot/tests/test_credibility_deep.py
- Positive: `test_all_local_links_and_http_targets` checks:
  - no external links
  - local file targets exist
  - fragments match IDs
  - HTTP GET via Flask test client returns 200 and has CSP header
- Negative: `test_link_validation_negatives` asserts failures for missing fragments, external schemes, and path traversal.

Limitation:
- The positive link test fails under snapshots due to missing linked targets (see finding 1). Only the negative link test was executed.

### 4) Scoped docs/tests alignment is strong, but relies on cross-module parity
Files:
- snapshot/docs/modules/credibility_tutorial_side_by_side.html
- snapshot/tests/test_credibility_deep.py

Observations:
- Tutorial embeds internal runnable code; tests ensure it still runs and matches the rendered table.
- Tests also assert no placeholders and presence of interactive controls (details, theme buttons, ARIA).

Risk:
- Style/notation parity assertions require concordance/discordance tutorial snapshots to exist in the pinned snapshot set.

## What to change (minimal scope)
- Add the missing snapshot dependencies referenced by the snapshot tests:
  - snapshot/docs/modules/{concordance,discordance,block,ranking}_tutorial_side_by_side.html
  - snapshot/electre3/credibility.py (and any other source files referenced)
- Or, change snapshot tests to explicitly target live files when snapshots are incomplete, and document that limitation (but this weakens snapshot pinning).

## Decision rationale
NEEDS WORK because snapshot-pinned validation cannot complete with the provided snapshot file set; parity and contract tests that do not require missing files are passing.
