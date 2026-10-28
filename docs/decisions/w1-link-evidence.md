# W1 Link Audit Evidence

## Reproducibility

- Revision: `36fce43bbb7c4075f4852b99763f2f5729710a16`
- Audit program: `python out/w1_link_audit.py`
- Inventory: `out/w1-link-inventory.json`
- Condensed failures/probes: `out/w1-link-summary.txt`
- Captured audit output: `out/w1-link-audit-run.txt`
- Preflight/final checkpoint: `out/w1-link-audit-checkpoint.json`

## Executed static and route audit

`python out/w1_link_audit.py` completed inventory generation and intentionally exited 1 because broken links exist.

```text
static_files=14
generated_files=10
template_files=4
references=270
valid=241
broken=12
planned=1
external=16
probes=52
```

The 52 Flask probes cover:

- `/`, `/docs/modules`, and `/app/`.
- Every allow-listed module document and tutorial route.
- Both allow-listed assets under every module route.
- Three invalid trailing-slash docs variants.
- Eight missing or malformed route cases.
- One workflow-created `/app/download/<token>` URL, returning 200.

## Executed tests

```text
pytest -q tests\test_app_workflow.py tests\test_docs_routes.py tests\test_local_document_links.py
199 passed in 1.71s
```

Coverage includes positive routes, missing targets, malformed/traversal inputs, fragments, keyboard-oriented static assertions, missing workflow/download tokens, and valid dynamic downloads.

## Compile and clean-scope checks

```text
python -m py_compile out\w1_link_audit.py out\w1_summarize.py app\routes\docs.py app\routes\workflow.py scripts\build_website.py
git diff --check
git diff --exit-code -- website app docs scripts tests
```

All commands exited 0 when run before W1 documentation creation. This proves no production change occurred; it does not prove browser behavior.

## Generated diff check

```text
git diff --no-index --exit-code docs\modules website\modules
```

Exited 1 as expected because static derivatives relocate paths and add website navigation. Output is preserved at `out/w1-generated-diff.txt`. Review tied the six static failures to `scripts/build_website.py::normalize_tutorial_assets`.

## Static inspection versus execution

- **Static inspection:** source HTML attributes, fragment IDs, Flask rule map, build ownership, template `url_for` endpoint names.
- **Executed:** Flask test-client GETs, complete workflow posts, generated download GET, pytest, Python compile, Git whitespace check, scoped production diff.
- **Not executed:** browser navigation, JavaScript event behavior, remote external URLs, network/offline simulation, assistive technology, visual rendering.

## Failure list

Twelve occurrences represent six unique targets duplicated across:

1. `website/modules/ranking/tutorial/index.html` at its actual static depth.
2. `docs/modules/ranking_tutorial_side_by_side.html` served as `/docs/modules/ranking/tutorial`.

Targets: README, CLI quickstart, debugging runbook, balanced criteria JSON, `electre3/ranking.py`, and D4 evidence test.

## Limitations

- Browser tests were explicitly excluded and remain deferred/non-blocking.
- External links were classified but not remotely validated.
- URL decoding and redirect semantics rely on Flask's test client, not a production proxy.
- Dynamic download token is nondeterministic; only status and route shape are asserted.
- No math renderer appears in scope; renderer-failure testing is not applicable.
