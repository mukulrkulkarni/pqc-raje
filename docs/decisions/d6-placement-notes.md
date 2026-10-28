# D6 placement notes

## Scope and ownership

D6 places approved reference and debugging material in existing user-facing repository documentation. `docs/tutorials/cli_quickstart.md` owns CLI, input, scientific, and module-reference guidance. `docs/runbook/debugging.md` owns supported versus legacy workflow diagnosis, runtime/cache/download/session limits, migration, and reproducibility instructions. The approved source draft remains `docs/decisions/d6-reference-debugging-draft.md`.

No companion-website page is added or changed in D6. Website integration, navigation, and generated-site ownership are D7 work. The existing generator continues to own `website/` tutorial outputs; do not hand-edit generated pages.

## Placement decisions

- Retained the quickstart as the CLI input-contract surface and appended the complete option and scientific reference.
- Retained the runbook as the recovery surface and added HTTP diagnosis, process-local cache behavior, legacy-route migration, and evidence requirements.
- Linked users between the quickstart and debugging runbook rather than duplicating procedural recovery steps.
- Did not change application logic, routes, templates, generated website files, or Python modules.

## Evidence and deferred work

D6 requires positive, negative, edge, link, semantic, no-JavaScript, and strict-line evidence through tests and static inspection. Browser rendering, keyboard/focus, zoom/reflow, offline, assistive technology, screen-reader, and load/performance checks remain deferred and non-blocking. The strict 50-executable-line audit is not applicable because D6 adds no Python.

## Reproducibility commands

Run from the repository root at the committed revision:

```text
python -m pytest -q tests/test_d6_placement.py
python -m pytest -q tests/
python scripts/build_website.py
python -m pytest -q tests/test_website_static.py tests/test_local_document_links.py
python -m electre3.cli examples/assets_priority/matrix_with_headers.csv examples/assets_priority/criteria.json -y
python -c "from electre3.validate import validate_thresholds; from electre3.config import CriterionConfig; validate_thresholds([CriterionConfig('x', 1, .3, .2, .4, True)])"
```

The last command is intentionally negative and must return nonzero with the threshold-order diagnostic.
