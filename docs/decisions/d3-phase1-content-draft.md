# D3 Phase 1 Content Draft

**Status:** Draft only. PI acceptance is deferred until the D3 stage ends. Scientific and Engineering gates are recorded separately; no final publication claim is made here.

## Root entry

# ELECTRE III Ranking

Rank network assets from a performance matrix and criteria JSON. Each criterion has a name, positive weight, `q`, `p`, `v`, and Boolean `maximize`, with `0 ≤ q ≤ p ≤ v`; weights sum to `1`, and the shared CLI/web validator allows at most eight criteria. In pairwise comparisons, `a` and `b` are alternative objects; block rows and columns are comparison groups. Use the CLI for scripted work or the local web app for a guided workflow.

Running scenario: rank the committed objects `A`, `B`, and `C` from `examples/assets_priority/`. The web presentation may display an identifier field as `Asset ID / IP`; this committed CLI example has identifiers `A`, `B`, and `C`, not IP values. In HTML pages, place notation before the I/O Summary. Use semantic `<var>`, `<sub>`, `<sup>`, and text operators; do not require a math renderer.

**Current implementation:** strict shared validation, blockwise ELECTRE III credibility, raw net-flow ranking, canonical result output, and local `/app/` workflow are implemented. Browser reflow, keyboard, offline, and screen-reader evidence remain limited as documented.

### Choose a path

- [Work in 10 minutes](#work-in-10-minutes)
- [CLI quickstart](../tutorials/cli_quickstart.md)
- [Local web app](http://127.0.0.1:5000/app/)
- **Mental model:** historical planned target; `docs/modules/index.html` was never created. This draft does not invent a replacement destination.
- [Reference and debugging](../runbook/debugging.md)

## Work in 10 minutes

### Prerequisites

- Python 3.10 or newer.
- Run commands from the repository root.
- Use the repository environment. No external service is required.

### Setup check

```bash
python -m compileall -q electre3 app
```

Expected result: the command exits with code `0` and prints no error.

### First real task

Use the committed Asset Priority example:

```bash
python scripts/convert_matrix_csv.py examples/assets_priority/matrix_with_headers.csv out/assets_priority_cli.npy --has-header --id-col Asset
python -m electre3.cli out/assets_priority_cli.npy examples/assets_priority/criteria.json -y
```

Expected ranking output contains:

```text
1. Alt 1
2. Alt 0
3. Alt 2
```

The CLI output contains zero-based alternative indices. Use `examples/assets_priority/asset_names.txt` to map them to asset names. At commit `27c8c4b` (evidence artifact: `examples/assets_priority/ranking.txt`), the independently generated output is `Alt 1`, `Alt 0`, `Alt 2`, which maps to `B > A > C`; this is evidence for that revision, not a universal ordering. Raw net flow is `Φ(a)=Σ_b S(a,b)−Σ_b S(b,a)`, ranked highest first. Scores are not normalized, and exact ties have no documented stable order.

### Local web task

Start the local app:

```bash
python scripts/dev_local.py
```

Open `http://127.0.0.1:5000/app/`. Select criteria JSON or the structured form. Provide the matrix. Review the preview. Confirm the input. Compute the ranking. The results page shows the top alternatives and raw net-flow scores.

The app uses server-rendered HTML. It does not use JavaScript. In HTML pages, math uses semantic `<var>`, `<sub>`, `<sup>`, and text operators. The browser download is canonical JSON. Cache entries expire after 30 minutes and are replaced by a later result. See `app/routes/workflow.py`, `app/services/result_cache.py`, and `electre3/serialization.py` for these contracts.

## Negative example and recovery

If a criteria file omits `weight`, `q`, `p`, `v`, or `maximize`, the validator rejects it. If matrix values are missing, non-finite, outside `[0,1]`, or headers do not match criteria order, preview fails. For a missing CSV value, select the approval checkbox and use the default `0` or another value in `[0,1]`; criteria JSON missing values are rejected. Correct the input or apply the approved CSV replacement, then repeat the preview. Do not bypass validation.

## Four phases

- **Phase 1:** this page and the quickstart.
- **Phase 2:** build a full scenario with custom criteria, identifiers, output mapping, and one failure recovery.
- **Phase 3:** learn ELECTRE III credibility, blockwise shapes, thresholds, raw net flow, and ties.
- **Phase 4:** use CLI flags, API/module reference, testing, limits, debugging, and changelog.

## Test evidence required for this draft

This draft is not publication evidence. Independent verbatim execution is required before publication. The evidence report must record the exact command, exit status, actual output, limitation, source location, and revision (D2 test-evidence plan: `e8790ae`). Required positive, negative, and edge evidence covers: valid CLI/web/module-path runs; malformed criteria/matrix and missing routes/targets; eight-criteria and block-size boundaries; header variants; missing-value approval; preview/confirmation gate; scientific threshold/direction/tie and determinism rejection; session/path/format failures; security headers/tokens; semantic forms/tables/math; keyboard workflow, error focus, zoom, reflow, and screen-reader limitation; performance benchmark method and timeout; serialization/cache/download limits; artifact tampering/order; 100 MiB and 100,000-row boundaries; end-to-end recovery; local links, deliberate broken-link detection, and network-disabled route/assets checks. Source evidence includes `electre3/shared.py`, `electre3/cli.py`, `scripts/convert_matrix_csv.py`, `scripts/dev_local.py`, `app/routes/workflow.py`, `app/services/result_cache.py`, `electre3/serialization.py`, `examples/assets_priority/`, and `tests/test_app_workflow.py`.

**Planned:** exact Python installation command, browser reflow evidence, keyboard/AT evidence, and full cross-surface byte comparison require stage-specific verification.