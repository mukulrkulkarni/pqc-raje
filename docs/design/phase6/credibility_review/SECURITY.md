# Security gate — Credibility tutorial (phase6)

Status: **NEEDS WORK**

Scope reviewed (per manifest.json)
- docs/modules/credibility_tutorial_side_by_side.html (snapshot path)
- tests/test_credibility_deep.py (snapshot path)
- tests/test_module_docs.py (snapshot path; relevant checks only)

## Findings

### 1) CSP / external assets policy
- **Pass (CSP present):** The tutorial HTML includes a CSP meta tag:
  - `default-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'; img-src 'self' data:; font-src 'self'; script-src 'self'; style-src 'unsafe-inline';`
  - Evidence: snapshot HTML head contains `<meta http-equiv="Content-Security-Policy" ...>` (see snapshot file in manifest).
- **Fail (toolchain completeness for local scripts):** The tutorial references local scripts that are not present in the provided snapshot:
  - `<script src="assets/theme.js" defer></script>`
  - `<script src="assets/highlight.js" defer></script>`
  - Evidence: HTML tail includes those tags.
  - Evidence of absence in snapshot: searches under `docs/design/phase6/credibility_review/snapshot/` returned no `theme.js` or `highlight.js`.

Impact
- If the snapshot is meant to be self-contained proof, it is incomplete. Review cannot confirm the referenced scripts are local-only, non-networking, and unchanged.

### 2) “Local compute only” examples
- **Pass:** The tutorial’s runnable example uses only local Python + NumPy and local package imports:
  - `import numpy as np`
  - `from electre3...`
  - No network or filesystem writes observed in the example snippet.
  - Evidence: `<section class="usage" ...>` code block.

### 3) Link negatives / route assumptions unchanged
- **Pass (test coverage exists):** `snapshot/tests/test_credibility_deep.py` asserts:
  - No external links (`assert not url.scheme and not url.netloc, 'External link'`).
  - Relative targets exist and fragments resolve.
  - HTTP GET for each docs link returns 200 and response contains `script-src 'self'` in CSP.
  - Negative link tests cover external URLs and path traversal.

Limitation
- These are snapshot tests; this gate did not execute them. The route base is assumed in-test:
  - `urljoin('/docs/modules/credibility/tutorial', a['href'])`

### 4) No app/shared JS changes
- **Not verifiable from provided artifacts:** Only snapshot HTML and tests were provided. This gate did not diff or inspect application code.

## Pre-existing vs introduced
- **Potentially pre-existing:** Missing `assets/theme.js` and `assets/highlight.js` in this snapshot may be an artifact of snapshot packaging, not a new regression.
- **Introduced in this phase’s snapshot (cannot disambiguate):** The new tutorial includes two local script references; without the asset files, supply-chain/provenance review of these scripts is blocked.

## Required remediation to reach APPROVED
- Include the referenced `assets/theme.js` and `assets/highlight.js` in the snapshot set (or update manifest scope) so this gate can:
  - verify they are local files,
  - verify they do not load external resources,
  - verify they do not relax CSP via inline/eval patterns.

## Evidence pointers
- manifest: docs/design/phase6/credibility_review/manifest.json
- tutorial snapshot: docs/design/phase6/credibility_review/snapshot/docs/modules/credibility_tutorial_side_by_side.html
- deep tests snapshot: docs/design/phase6/credibility_review/snapshot/tests/test_credibility_deep.py
- module docs tests snapshot: docs/design/phase6/credibility_review/snapshot/tests/test_module_docs.py
