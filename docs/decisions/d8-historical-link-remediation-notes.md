# D8 Historical-Link Remediation Notes

**Date:** 2026-10-28  
**Scope:** Six local targets reported by the D8 audit in historical D3 and D5 drafts.  
**Preservation rule:** The source documents remain explicitly labelled drafts. This remediation changes only their local-link disposition. It creates no application, website, generated-output, remote, or tag change.

## Disposition

| Draft | Original target | Disposition | Current target or classification |
|---|---|---|---|
| D3 | `docs/tutorials/cli_quickstart.md` | Resolved | `../tutorials/cli_quickstart.md` |
| D3 | `docs/modules/index.html` | Historical planned / unavailable | No file exists. The draft now records this fact and does not substitute a destination. |
| D3 | `docs/runbook/debugging.md` | Resolved | `../runbook/debugging.md` |
| D5 | `../../examples/d4_phase2/` | Resolved | `../../examples/d4_phase2/scenario-3/criteria_balanced.json` |
| D5 | `../../electre3/` | Resolved | `../../electre3/ranking.py` |
| D5 | `../../tests/d4_checks/` | Resolved | `../../tests/d4_checks/test_evidence.py` |

The D3 unavailable target remains a textual historical/planned classification, not a Markdown link. This preserves history without inventing a local module-index page.

## Regression coverage

`tests/test_local_document_links.py` now includes both D3 and D5 drafts in the existing local file and Markdown-fragment checker. Its existing negative test confirms missing-file and missing-fragment detection. Its edge test confirms external and anchor-only links remain outside local-file resolution.

## Review confirmation

- **Engineering:** Confirmed every retained Markdown local target is a file-relative target and the planned D3 target is not represented as a false link.
- **Scientific:** Confirmed D5 target substitutions point to existing evidence, implementation, and test sources without changing the draft’s ELECTRE III or raw-net-flow claims.
- **UI/UX:** Confirmed the draft labels, current/planned distinction, and no-script/static scope remain intact. Deferred browser, AT, zoom, reflow, keyboard, offline, and load evidence remain non-blocking.

## Acceptance boundary

Acceptance requires zero errors from `python out/d8_link_audit.py`, passing D4-D7 focused documentation tests, the full repository suite, compile/build/diff checks, valid checkpoint JSON, and an independent second link-audit run. Exact execution results are recorded in [D8 documentation evidence](d8-documentation-evidence.md).
