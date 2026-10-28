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

## Findings and historical-link remediation

The six historical D3/D5 targets reported by the initial audit have been remediated without changing the drafts' status or publishing them. See [D8 historical-link remediation notes](d8-historical-link-remediation-notes.md).

1. D3's quickstart and debugging links now resolve relative to the decision-document directory.
2. D3's absent `docs/modules/index.html` target is explicitly classified as historical/planned and unavailable. It is no longer represented as a Markdown destination; no replacement page was invented.
3. D5's three directory targets now resolve to their existing, specific evidence, implementation, and test files.
4. The local-link audit and its regression test cover both historical draft records. D3 and D5 remain drafts and are not user-facing release pages.

### Non-blocking observations

- `README.md` retains a historical D3-review status label. It does not assert a current release status, but it is stale relative to the approved D4-D7 completion sequence.
- D3 historical notes retain pending-review and pinned-revision statements. They are provenance records, not current status sources.
- No source-owned generated tutorial output was hand-edited. Rebuild and ownership checks passed.

## Review record

- **Scientific review:** Confirmed the D5 links now name existing evidence, implementation, and test files. No mathematical claim changed or was promoted from a draft.
- **Engineering review:** Confirmed the two D3 file links and three D5 file links resolve locally; the unavailable D3 target is classified rather than fabricated.
- **UI/UX review:** Confirmed draft labels and current/planned distinction remain clear. Browser/AT/zoom/reflow/keyboard/offline/load evidence remains deferred and non-blocking.

## Reproduction

Use the commands and results in [D8 documentation evidence](d8-documentation-evidence.md). Run from the repository root using Python 3.11.2 and pytest 9.1.1.

## Release decision

**D8 historical-link remediation is complete. Final documentation release status: `ready_for_final_documentation_release_gate`.** The six historical targets are resolved or explicitly classified without inventing a destination. Required link, focused, full-suite, build, compile, diff, JSON, and independent reproducibility evidence is recorded in [D8 documentation evidence](d8-documentation-evidence.md). Browser limitations remain deferred and non-blocking.
