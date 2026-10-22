# D3 Phase 1 Execution Notes

**Status:** D3 Phase 1 placement and testing complete. UI/UX, Scientific, and Engineering gates approved. PI stage-end acceptance is deferred until D3 completion. No final publication claim is made here.

**Pinned state:** checkpoint commit `5e9072d`; current correction evidence is recorded in the working tree before final reconciliation. Execution environment: Windows workspace, Python 3.11.2. Browser reflow, zoom, keyboard, offline, and screen-reader behavior remain unverified.

## Scope and authority

- Source authority: implementation/tests, approved decisions, tutorials/runbooks, then website summaries.
- User-facing targets: `README.md`, `docs/GETTING_STARTED.html`, `docs/tutorials/cli_quickstart.md`, `website/index.html`, and `website/app/index.html`.
- `scripts/build_website.py` remains the website build authority. Module pages were not edited.
- No install command was published without reproducible packaging evidence.

## Placement and styling

- Added Phase 1 entry content and CLI/web quickstart using committed `examples/assets_priority/` inputs.
- Used MK-TII tokens: Arial, purple `#6400FF`, navy `#253746`, aqua `#7EDDD3`.
- App landing styling matches the website landing-page source contract.
- No app JavaScript, KaTeX, external assets, or application behavior changes.
- Browser evidence is limited to no app scripts, stylesheet presence, and one screenshot supplied by the user.

## Evidence

- Positive: compile, converter, CLI ranking, website build, focused documentation/UI/link/security tests.
- Negative: missing identifier header, invalid criteria/matrix, missing preview/confirmation, and invalid routes.
- Edge: criteria and block-size boundaries, missing-value approval, cache/serialization boundaries, fewer results, and tie-related existing tests.
- Recorded test results: placement 4; focused 232; negative/edge 77; prior full regression 932. These are recorded results; later final rerun must verify them.
- Reproducibility records exact command, exit status, output, limitation, source path, and revision.

## Review gates

- UI/UX gate: **APPROVED** after five corrections and final styling-parity review.
- Engineering gate: final rerun required after checkpoint metadata reconciliation.
- Scientific gate: final rerun required after checkpoint metadata reconciliation.
- PI stage-end acceptance: pending.

## Preserved work

`out/engineering-tree.txt` was preserved intact at `out/audit/preserved-unrelated/engineering-tree.txt`. `review_snapshot/` remains preserved and must be resolved before a final clean-tree claim.

## Limitations

No browser reflow, browser zoom, keyboard traversal, offline navigation, or screen-reader evidence was collected. Semantic HTML and static/Flask tests do not replace those checks. The D3 stage must not claim those results.
