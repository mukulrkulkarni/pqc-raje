# D5 placement correction and re-review notes

**State:** Review gates passed locally; ready for focused commit.

## Placement and ownership

- Editable source: `docs/modules/ranking_tutorial_side_by_side.html`.
- Generated output: `website/modules/ranking/tutorial/index.html`.
- `scripts/build_website.py` generates the website output. Do not edit generated tutorial pages directly.
- Generation resolves tutorial assets and repository-reference links relative to `website/modules/ranking/tutorial/`.

## Corrected findings

- The document h1 now precedes the Mental Model h2.
- Tie text now states computed binary64 flows.
- Memory text states `(B1·B2·C)` criterion intermediates, `(B1·B2)` credibility, and `O(N)` accumulation.
- Source and generated links have separate target-resolution checks.
- Generated tutorial pages now participate in static style and local-link checks.

## Executed evidence

Run from repository root:

```text
python -m pytest -q tests\d5_checks\test_reproducibility.py
# 1 passed in 1.17s
python -m pytest -q tests\test_d5_placement.py tests\test_style_corrections.py tests\test_website_static.py
# 25 passed in 1.72s
python scripts\build_website.py
# exit 0
python -m compileall -q electre3 app scripts tests
# exit 0
git diff --check
# exit 0
```

The 25-pass placement suite contains positive semantic, source/generated target-resolution, generator-idempotence, static style/link, malformed-threshold negative, and equal-threshold edge coverage. The independent reproduction test separately invokes the generator and D5 suite.

## Re-review results

- **Scientific — pass:** `ranking.py`, `block.py`, `credibility.py`, and `accumulator.py` match the tutorial claims: direction-aware binary64 pairwise differences, credibility veto handling, raw (not normalized) net flow, and no ELECTRE III distillation claim.
- **Engineering — pass:** Generator remains the only generated-page writer; source ownership is preserved; generated target and asset paths resolve; no ranking or application logic changed.
- **UI/UX — pass (static):** The h1 precedes the Mental Model h2. The page retains Arial and MK-TII tokens, semantic HTML math, diagram, table, focus styles, and source/generated static-link coverage.
- **Independent reproducibility — pass:** `tests/d5_checks/test_reproducibility.py` ran the build and D5 suite in subprocesses successfully.

## Deferred limitations

Browser rendering, assistive technology, keyboard, zoom, reflow, offline, and load evidence remain deferred and non-blocking. No browser test, remote Git operation, or formal ELECTRE III publication review was performed.
