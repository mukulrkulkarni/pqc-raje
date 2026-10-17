# Security review — Discordance tutorial (Phase 5)

## Decision
APPROVED

## Scope and limits
- In scope: `docs/modules/discordance_tutorial_side_by_side.html`, tutorial assets, and tests listed in `docs/design/committee_phase5/discordance_review/manifest.json`.
- Out of scope: UI rendering fidelity in a real browser; production deployment secret management.
- Snapshot manifest folder `manifest/snapshots` is not present in this workspace; verification used exact paths from `discordance_review/manifest.json`.

## Evidence: local-only assets and CSP
- Tutorial CSP is restrictive and local-only via meta tag:
  - `docs/modules/discordance_tutorial_side_by_side.html` contains:
    - `Content-Security-Policy` meta: `default-src 'none' ... script-src 'self'; style-src 'unsafe-inline';` (no `unsafe-eval`).
- Tutorial scripts are local and allow-listed:
  - HTML includes exactly:
    - `<script src="assets/theme.js" defer></script>`
    - `<script src="assets/highlight.js" defer></script>`
    - Evidence: `tests/test_discordance_deep.py::test_n1_structure_and_live_control_contract` asserts the script `src` list equals `['assets/theme.js','assets/highlight.js']`.
  - Served mode only exposes `theme.js` and `highlight.js`:
    - `app/routes/docs.py`: `ALLOWED_TUTORIAL_ASSETS = {"theme.js", "highlight.js"}` and `tutorial_asset()` enforces the allow-list.
- Docs routes apply CSP header matching the meta policy:
  - `app/__init__.py`: `CSP_DOCS` includes `script-src 'self'` and `default-src 'none'`.
  - Evidence: `tests/test_discordance_deep.py::test_local_links_and_served_assets` asserts the response header contains `script-src 'self'`.

## Evidence: links are local, non-escaping, and fragments exist
- Link validation rejects external schemes, protocol-relative URLs, and path traversal:
  - `tests/test_discordance_deep.py::check_links()` asserts:
    - `not url.scheme and not url.netloc` (blocks `https://` and `//example.com`).
    - `target.is_relative_to(PAGE.parent)` (blocks `../../outside.html`).
    - `target.is_file()` (blocks missing files).
    - Fragment, if present, must exist in the target document.
  - Negative coverage: `test_invalid_links_rejected` parametrizes `https://example.com`, `//example.com`, `../../outside.html`, and missing anchors.

## Evidence: execution examples do not add security risk
- The usage snippet executes local Python code only (no network, no file I/O):
  - `docs/modules/discordance_tutorial_side_by_side.html` “Run the sensitivity example” imports `numpy` and in-repo modules `electre3.*`.
  - `tests/test_discordance_deep.py::test_execute_usage_and_compare_visible_table` executes the snippet with `exec(compile(...))` and compares outputs to the rendered table.

## Evidence: negative checks for external references remain
- Static docs tests include explicit external-reference negative patterns:
  - `tests/test_module_docs.py` defines `EXTERNAL_PATTERNS` matching `href/src/url/@import` with `https?://` and asserts no matches.
  - It also enforces presence of the CSP meta tag and disallows `'unsafe-eval'` in the CSP content.

## Evidence: “routes/shared JS unchanged since prior N1 gate”
- This gate did not re-diff against prior N1 artifacts (not provided here).
- However, the Discordance manifest explicitly scopes changes to the tutorial HTML and tests:
  - `docs/design/committee_phase5/discordance_review/manifest.json` lists only:
    - `docs/modules/discordance_tutorial_side_by_side.html`
    - `tests/test_module_docs.py`
    - `tests/test_discordance_deep.py`
- Within reviewed code paths, the only served tutorial assets are unchanged allow-listed names (`theme.js`, `highlight.js`) and no new asset names are introduced.

## Findings
### Introduced in this change (Discordance tutorial)
- No new external resource loading paths.
- No relaxation of CSP.
- Added/updated deep tests that execute the tutorial snippet and enforce local link and CSP rules.

### Pre-existing (observed during review; not gate blockers)
- Docs CSP uses `style-src 'unsafe-inline'` (present in tutorial meta and docs CSP header). This is consistent with current architecture and not expanded by this change.

## Required follow-ups
- None for this security gate.
