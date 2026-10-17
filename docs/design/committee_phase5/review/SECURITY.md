# Security gate — N1 pilot

**Result:** APPROVED

## Scope and evidence inspected (static)
- Request and constraints: `docs/design/committee_phase5/review/REQUEST.md`.
- Manifest pinset: `docs/design/committee_phase5/review/manifest.json`.
- Introduced code delta: `docs/design/committee_phase5/review/pilot.diff`.
- Served route implementation: `app/routes/docs.py`.
- Security headers / CSP policy source: `app/__init__.py`.
- Tutorial HTML (live + snapshot copy):
  - `docs/modules/concordance_tutorial_side_by_side.html`
  - `docs/design/committee_phase5/review/snapshot/docs/modules/concordance_tutorial_side_by_side.html`
- Pilot tests (read only; not executed here): `tests/test_concordance_n1.py`.

**Not executed:** no browser, no HTTP server, no pytest run. Any “test” statements below refer to *code present*, not results I ran.

## Gate checks

### 1) Route allow-listing and traversal resistance (introduced)
- New sibling-link route:
  - `app/routes/docs.py`: `@bp.route("/docs/modules/<name>/<target>_tutorial_side_by_side.html")`.
  - Validation: checks `_validate_doc_name(name)` (strict regex + allow-list) then serves `module_tutorial(target)`.
- Allow-list enforcement for `target`:
  - `module_tutorial(target)` re-validates via `_validate_doc_name(target)` and aborts 404 on failure.
- Traversal attempts:
  - Any `target` containing `.` or `/` fails regex `^[a-z_]+$`.
  - Percent-encoded traversal in path segment does not match allow-list names.

**Net:** Introduced route is allow-list gated; no file-path joins; traversal impact is low.

### 2) CSP and script execution surface
- HTTP-level CSP (authoritative): `app/__init__.py` sets `Content-Security-Policy` on every response.
  - Docs routes use `CSP_DOCS`: `default-src 'none' ... script-src 'self'; style-src 'unsafe-inline'; img-src 'self' data:; font-src 'self';`.
- Page-level CSP meta also present (defense-in-depth):
  - `docs/modules/concordance_tutorial_side_by_side.html` contains `<meta http-equiv="Content-Security-Policy" content="... script-src 'self' ...">`.
- Inline scripts:
  - Tutorial HTML includes **no inline `<script>` blocks**; only external, same-origin scripts:
    - `<script src="assets/theme.js" defer></script>`
    - `<script src="assets/highlight.js" defer></script>`
- Network requests:
  - No `http(s)://` URLs, no protocol-relative URLs, and no obvious fetch/XHR code in the HTML.

**Net:** CSP is restrictive; no new remote script or remote resource references introduced.

### 3) Local links and assets
- Internal links use relative paths (e.g., `discordance_tutorial_side_by_side.html#row-R2`).
- Assets are served through strict allow-list:
  - `ALLOWED_TUTORIAL_ASSETS = {"theme.js", "highlight.js"}` in `app/routes/docs.py`.
  - Asset resolution includes `resolve()` + prefix check against assets dir.

**Net:** Asset surface is tightly bounded.

### 4) Documentation integrity vs. manifest / snapshot
- `manifest.json` pins `app/routes/docs.py`, `docs/modules/concordance_tutorial_side_by_side.html`, `tests/test_concordance_n1.py`.
- Snapshot directory issue (pre-existing or process issue):
  - Directory listing tool returned 0 files for `docs/design/committee_phase5/review/snapshot/`, yet the file `docs/design/committee_phase5/review/snapshot/docs/modules/concordance_tutorial_side_by_side.html` exists and matches live tutorial content.

**Action (process):** Fix/verify snapshot directory enumeration in the review packaging pipeline to preserve chain-of-custody guarantees.

## Findings summary

### Introduced issues
- None found that block security gate.

### Pre-existing / out-of-scope notes
- `app/__init__.py` contains `SECRET_KEY = "dev-secret-key-change-in-production"` (expected for dev; ensure production override).

## Rationale
**Chosen:**
- APPROVED — Allow-lists, CSP, and no new network/inline script risks in reviewed delta.

**Near-miss:**
- NEEDS WORK — Snapshot packaging inconsistency weakens provenance evidence, but content present.

**Disqualified:**
- BLOCKED — No traversal, CSP, or remote-code-exec regression observed in static review.
