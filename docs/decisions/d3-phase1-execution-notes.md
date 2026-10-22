# D3 Phase 1 Execution Notes

**Status:** Placement and testing complete. UI/UX approved. Scientific and Engineering final reruns are pending status reconciliation. PI stage-end acceptance is pending. Current reconciled commit: `b1d594b`.

## Scope and authority

- Source authority: implementation/tests, approved decisions, tutorials/runbooks, then companion website summaries.
- Editable user-facing targets: `README.md`, `docs/GETTING_STARTED.html`, `docs/tutorials/cli_quickstart.md`, `website/index.html`, and `website/app/index.html`.
- `scripts/build_website.py` confirms website source ownership. Module pages were not edited.
- No install command was added without packaging evidence.

## Placement and layout

- Added Phase 1 entry content and CLI/web quickstart using committed `examples/assets_priority/` inputs.
- Used MK-TII tokens: Arial, purple `#6400FF`, navy `#253746`, aqua `#7EDDD3`.
- App landing styling matches the website landing-page source contract.
- No app JavaScript, KaTeX, external assets, or application behavior changes.
- Browser evidence is limited to no app scripts, stylesheet presence, and one screenshot supplied by the user.

## Evidence

- Positive: compile, converter, CLI ranking, website build, focused documentation/UI/link/security tests.
- Negative: missing identifier header, invalid criteria/matrix, missing preview/confirmation, and invalid routes.
- Edge: criteria and block-size boundaries, missing-value approval, cache/serialization boundaries, fewer results, and tie-related existing tests.
- Independent reproducibility report: `out/d3-phase1-reproducibility-report.md`.
- Current rerun evidence: 283 focused documentation/UI/security tests and 60 workflow/CLI/cache/serialization tests; compile, build, CLI, and invalid-header checks passed.

## Review gates

- UI/UX gate: approved after styling parity correction.
- Engineering gate: rerun required after status reconciliation.
- Scientific gate: rerun required after status reconciliation.
- PI stage-end acceptance: pending.

## Preserved work

`out/audit/preserved-unrelated/engineering-tree.txt` and `out/audit/preserved-unrelated/review_snapshot/` are preserved intact and excluded from D3 content scope.

## Limitations

No verified browser reflow, browser zoom, keyboard traversal, offline navigation, or screen-reader evidence exists. The pages state these limits. Semantic HTML and static/Flask tests do not replace browser or assistive-technology checks.
