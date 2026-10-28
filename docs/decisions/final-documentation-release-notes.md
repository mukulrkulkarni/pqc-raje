# Final documentation release notes

**Date:** 2026-10-28
**Status:** `released with limitations`
**Scope:** Final local documentation-release gate for D4 through D8. No application feature, remote Git, or `v0.1` tag change occurred.

## Authority, version, and ownership

- D4, D5, D6, D7, and D8 records are complete at `2c38c7c`, `aa85c5c`, `a90f274`, `a327e68`, and `79e3e15`.
- `v0.1` remains the existing local tag at `adbd5ffcffd721c61e419f0e03b4f51cb960efe5` (`record-v0-1-tag-evidence`); this gate neither moved nor recreated it.
- `docs/tutorials/cli_quickstart.md` and `docs/runbook/debugging.md` own repository reference content.
- `docs/modules/*_tutorial_side_by_side.html` is generated-input source; `scripts/build_website.py` owns `website/modules/*/tutorial/index.html`.
- Static paths `/index.html`, `/app/index.html`, `/modules/index.html`, and `/reference/index.html` are current. Flask paths `/docs/modules` and `/docs/modules/<name>/tutorial` are current. Hosted repository references remain planned.

## Executed evidence

Run from the repository root using Python 3.11.2 and pytest 9.1.1:

```text
python -m compileall -q electre3 app scripts
python -m pytest -q
python -m pytest -q tests/test_d4_fixture_correction.py tests/test_d5_placement.py tests/test_d6_placement.py tests/test_d7_website_integration.py tests/test_local_document_links.py tests/test_website_static.py tests/d5_checks/test_reproducibility.py
python out/d8_link_audit.py
python scripts/build_website.py
git diff --check
git diff --exit-code -- website
git diff --exit-code -- docs
python -m json.tool out/final-documentation-gate-checkpoint.json > NUL
```

Results: compile passed; full suite passed **1062 tests in 25.28s**; focused D4-D8 suite passed **42 tests in 7.44s**; local audit reported `audited_files=18 local_link_errors=0`; build created no website drift; whitespace, docs, website, and checkpoint-JSON checks passed. Existing focused coverage includes positive local links, negative missing-file and missing-fragment cases, external/anchor-only edge cases, Flask traversal-shaped 404, and static/Flask route separation. Focused D4-D8 test files meet the strict 50-line policy where applicable; `tests/test_d4_fixture_correction.py` is the documented legacy exception (177 lines).

## Reviews and decision

- **Scientific:** accepted D5 evidence/implementation/test targets; no scientific claim changed.
- **Engineering:** accepted D4-D8 test, route, link, ownership, build, and reproducibility evidence.
- **UI/UX:** accepted labeling, styling/branding consistency, and current/planned/deferred distinctions. Browser limitations remain deferred and non-blocking.
- **PI:** accepted this bounded final-gate scope through the approved invocation and recorded the release decision below.

D4 fixtures, the D5 placed tutorial, and D6 quickstart/runbook reference content are available in their repository paths, as re-verified after release-record recovery; see [documentation artifact recovery notes](documentation-artifact-recovery-notes.md). D5 targets retain draft provenance. D8 remediated five links and explicitly classified one unavailable historical/planned D3 target without inventing a route. Repository-hosted `/docs/...` references remain planned and unavailable; no website reference page is claimed for D6.

## Limitations

Browser-rendered styling, keyboard, zoom, reflow, offline, load, screen-reader, and assistive-technology behavior were not executed. These remain deferred, non-blocking release limitations. Remote Git and upstream release actions remain user-only.
