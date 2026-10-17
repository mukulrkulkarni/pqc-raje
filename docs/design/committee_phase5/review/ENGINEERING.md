# Engineering gate — N1 pilot (concordance)

## Decision: APPROVED

## Evidence read (pinned)
- docs/design/committee_phase5/review/REQUEST.md
- docs/design/committee_phase5/review/manifest.json
- docs/design/committee_phase5/review/pilot.diff
- Snapshot + live: docs/modules/concordance_tutorial_side_by_side.html
- Snapshot + live: tests/test_concordance_n1.py
- Snapshot + live: app/routes/docs.py
- Context: docs/design/committee_phase5/PILOT_STATUS.md

## Executed tests (local)
- `python -m pytest -q tests/test_concordance_n1.py tests/test_docs_routes.py` → **197 passed** (1.47s). (Tool output recorded in chat.)

## Scope / minimality
- Changes are scoped to 3 files in manifest: tutorial HTML, docs routes, N1 tests.
- Route addition is minimal: `linked_tutorial()` resolves sibling tutorial links via allow-list without exposing filesystem paths (app/routes/docs.py).

## Positive coverage (meaningful)
- Runnable example is extracted from HTML and executed; asserts match displayed values (0.85, 0.75) and validates reverse direction (tests/test_concordance_n1.py::test_runnable_example_matches_displayed_values).
- Explicit boundary case: q=p equality at diff=-q selects c=1 and just below selects 1; below -p gives 0 (tests/test_concordance_n1.py::test_equal_threshold_boundary_matches_tutorial).
- Offline and served-mode link integrity: validates local paths/fragments exist and that Flask serves each linked page with CSP + assets available (tests/test_concordance_n1.py::test_all_concept_links_exist_offline_and_served).

## Negative coverage (meaningful)
- Link checker rejects nonlocal schemes, missing fragments, missing pages, and traversal attempts (tests/test_concordance_n1.py::test_link_checker_rejects_bad_references).
- Route rejects unknown/missing/traversal targets for sibling tutorial resolver (tests/test_concordance_n1.py::test_sibling_route_rejects_unknown_missing_and_traversal).
- Existing broader traversal/allow-list tests remain in tests/test_docs_routes.py.

## Maintainability
- HTML: large inline CSS is expected for offline-doc constraints; no new JS added.
- Tests are focused, deterministic, and avoid browser assertions they cannot prove (explicitly documented in file header).

## Route/link integrity + file-mode behavior
- Tutorial uses relative `assets/theme.js` and `assets/highlight.js` (works in file:// and served mode).
- New `linked_tutorial` route supports sibling links like `discordance_tutorial_side_by_side.html#row-R2` under `/docs/modules/<name>/...` while keeping allow-list enforcement (app/routes/docs.py).

## Confirmed preserved JS wiring (static inspection)
- Tutorial includes only `assets/theme.js` and `assets/highlight.js` scripts, in that order (tests/test_concordance_n1.py::test_notation_before_io_and_real_controls).
- No inline script selection logic or CDN references detected by tests.

## Pre-existing / out-of-scope limitations (not treated as failures)
- No browser runner here: cannot verify pixel alignment, sticky offsets, or actual keyboard interaction beyond static DOM attributes.
- PILOT_STATUS.md notes a pre-existing highlight.js baseline offset (-64px) that may misalign; not introduced/verified in this gate.

## Findings
### Must-fix: none for engineering gate.

### Follow-ups (non-blocking)
- Add a browser-level test (Playwright) later if/when infra is approved, to validate click/keydown behavior and alignment visually.
- Consider adding a regression that `linked_tutorial` validates/normalizes `target` explicitly (it currently relies on `module_tutorial()`’s allow-list check).
