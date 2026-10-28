# D8 Documentation Release Audit

**Date:** 2026-10-28
**Scope:** D3 through D7 documentation and generated companion website boundaries.
**Audit status:** Complete; final documentation release gate is **blocked** on the findings below. D8 does not change application code, website source, generated output, or remote state.

## Authority and source ownership

- D3-D7 decisions, repository documentation, implementation, and tests are the audit sources.
- `docs/tutorials/cli_quickstart.md` owns the CLI, input-contract, scientific, and reference guidance.
- `docs/runbook/debugging.md` owns diagnostics, recovery, runtime limits, migration, and reproducibility.
- `docs/modules/*_tutorial_side_by_side.html` is the source for generated `website/modules/*/tutorial/index.html` output.
- `scripts/build_website.py` owns tutorial generation. D7 static navigation and `website/reference/index.html` are manually owned.
- Static routes are current at `/index.html`, `/app/index.html`, `/modules/index.html`, and `/reference/index.html`. Flask documentation routes remain `/docs/modules` and `/docs/modules/<name>/tutorial`.
- Repository reference hosting remains planned. No static `/docs/...` hosting route is claimed.

## Verified documentation contract

The current CLI/web contract accepts identifier-bearing CSV `(N,C+1)` or numeric NumPy `(N,C)` data. CSV identifiers are nonempty, unique, at most 50 characters, and free of control characters. Scores are finite values in `[0,1]`. Criteria provide `name`, positive `weight`, `q`, `p`, `v`, and Boolean `maximize`; one through eight criteria are allowed; weights sum to one; and `0 <= q <= p <= v`. Raw net flow ranks descending after credibility evaluation. Exact ties have no documented stable order.

The audited D6 quickstart and runbook describe these rules consistently with the CLI, focused tests, and executed examples. Current/deferred labels distinguish current static and Flask paths from planned hosted references. Browser rendering, keyboard, assistive-technology, zoom, reflow, offline, and load evidence remain deferred and non-blocking by the approved release limitation.

## Findings

### Blocking documentation defects

1. `docs/decisions/d3-phase1-content-draft.md` has three unresolved local Markdown targets: `docs/tutorials/cli_quickstart.md`, `docs/modules/index.html`, and `docs/runbook/debugging.md`. They resolve from repository root, but not from the decision document directory.
2. `docs/decisions/d5-mental-model-draft.md` has three unresolved directory targets: `../../examples/d4_phase2/`, `../../electre3/`, and `../../tests/d4_checks/`. The audit checker requires local file targets, so these directory references lack a local-document resolution contract.
3. D3 and D5 label themselves drafts and are not user-facing release pages. They are nevertheless D3-D7 audit inputs and must be corrected or explicitly excluded from the final release documentation set before the final documentation gate can pass.

### Non-blocking observations

- `README.md` retains a historical D3-review status label. It does not assert a current release status, but it is stale relative to the approved D4-D7 completion sequence.
- D3 historical notes retain pending-review and pinned-revision statements. They are provenance records, not current status sources.
- No source-owned generated tutorial output was hand-edited. Rebuild and ownership checks passed.

## Review record

- **Scientific review:** Approved for the current CLI/input/scientific contract. D3/D5 draft findings are documentation-location defects, not a mathematical contradiction. No scientific claim is promoted from a draft record.
- **Engineering review:** Approved for audit method and evidence. The six unresolved local targets block the final documentation release gate until disposition.
- **UI/UX review:** Approved for static navigation, ownership labels, current/planned distinction, semantic no-script scope, and route separation. Browser/AT/zoom/reflow/keyboard/offline/load evidence remains deferred and non-blocking.

## Reproduction

Use the commands and results in [D8 documentation evidence](d8-documentation-evidence.md). Run from the repository root using Python 3.11.2 and pytest 9.1.1.

## Release decision

**D8 audit execution is complete. Final documentation release status: `release_blocked`.** The required remediation is limited to resolving or formally excluding the six historic draft links, then rerunning the local-link audit and documentation-focused regression checks. Browser limitations remain deferred and non-blocking.
