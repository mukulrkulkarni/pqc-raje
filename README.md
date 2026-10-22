# ELECTRE III Ranking

Rank network assets from a performance matrix and criteria JSON. Each criterion needs a name, positive `weight`, `q`, `p`, `v`, and Boolean `maximize`. Thresholds satisfy `0 ≤ q ≤ p ≤ v`; weights sum to `1`; the shared CLI/web validator accepts at most eight criteria.

## Work in 10 minutes

Run commands from the repository root with Python 3.10 or newer. Use the repository environment. No external service is required.

```bash
python -m compileall -q electre3 app
python scripts/convert_matrix_csv.py examples/assets_priority/matrix_with_headers.csv out/assets_priority_cli.npy --has-header --id-col Asset
python -m electre3.cli out/assets_priority_cli.npy examples/assets_priority/criteria.json -y
```

The ranking output contains:

```text
1. Alt 1
2. Alt 0
3. Alt 2
```

The CLI prints zero-based indices. `examples/assets_priority/asset_names.txt` maps this example to `B > A > C`. This ordering is evidence for the committed sample data, not a universal result. The ranking uses raw net flow, <var>Φ</var>(a) = Σ<sub>b</sub> S(a,b) − Σ<sub>b</sub> S(b,a), ordered highest first. Scores are not normalized. Exact ties have no documented stable order.

## Choose a path

- [Getting Started](docs/GETTING_STARTED.html): CLI and local web paths.
- [CLI quickstart](docs/tutorials/cli_quickstart.md): input contract, converter, flags, outputs, and errors.
- [Local web app](http://127.0.0.1:5000/app/): guided workflow after local launch.
- [Module tutorials](docs/modules/index.html): concepts and implementation detail.
- [Debugging](docs/runbook/debugging.md): recovery and diagnostics.

## Local web workflow

```bash
python scripts/dev_local.py
```

Open `http://127.0.0.1:5000/app/`. Provide criteria and a matrix, review the preview, confirm the input, and compute the ranking. The app serves HTML without JavaScript. Browser reflow, browser zoom, keyboard, offline, and screen-reader evidence remain unverified as documented.

## Validation and recovery

The validator rejects missing criterion fields, invalid thresholds, missing or non-finite matrix values, values outside `[0,1]`, and header/criteria order mismatches. Correct the input or use the approved CSV missing-value replacement during preview; do not bypass validation.

## Documentation status

Phase 1 content is under D3 review. It is not a release claim. See `docs/decisions/d3-phase1-execution-notes.md` for execution evidence and limitations.
