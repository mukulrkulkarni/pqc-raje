# D7 companion website integration notes

## Source ownership

[`docs/tutorials/cli_quickstart.md`](../tutorials/cli_quickstart.md) and [`docs/runbook/debugging.md`](../runbook/debugging.md) remain the D6 repository-owned reference sources. [D6 placement notes](d6-placement-notes.md#scope-and-ownership) record the earlier ownership boundary. D7 adds a static reference orientation page at `website/reference/index.html`; it identifies those sources but does not copy their content.

`docs/modules/*_tutorial_side_by_side.html` remains the source for generated tutorial output in `website/modules/*/tutorial/index.html`. `scripts/build_website.py` owns that generation and is unchanged. D7 changes only static navigation pages and its new manually owned reference page.

## Current and planned paths

**Current:** Static navigation uses `/index.html`, `/app/index.html`, `/modules/index.html`, and `/reference/index.html`. Flask module documentation remains at `/docs/modules` and `/docs/modules/<name>/tutorial` on the Flask documentation host.

**Planned:** Repository reference pages require an owning documentation host and stable routes before publishing. No static `/docs/...` route is claimed or added.

## Evidence and reproduction

Run from the repository root at the D7 commit:

```text
python scripts/build_website.py
python -m pytest -q tests/test_d7_website_integration.py tests/test_website_static.py tests/test_local_document_links.py
python -m pytest -q tests/
```

Positive evidence checks static navigation, Flask documentation routes, generated rebuild, and local documentation links. Negative evidence checks a Flask traversal-shaped path returns HTTP 404. Edge evidence checks tutorial routes remain distinct from static reference paths.

D7 changes no Python production files; the strict 50-line policy applies to the new focused test and is satisfied. Browser rendering, keyboard, zoom, reflow, offline, assistive-technology, screen-reader, and load evidence remain deferred and non-blocking.
