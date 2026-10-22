# ELECTRE III Ranking

Rank network assets from a performance matrix and criteria JSON. Each criterion needs a name, positive `weight`, `q`, `p`, `v`, and Boolean `maximize`. Thresholds satisfy `0 ≤ q ≤ p ≤ v`; weights sum to `1`; the shared CLI/web validator accepts at most eight criteria.

## Work in 10 minutes

Run commands from the repository root with Python 3.10 or newer. Use the repository environment. No external service is required.

```bash
python -m compileall -q electre3 app
python -m electre3.cli examples/assets_priority/matrix_with_headers.csv examples/assets_priority/criteria.json -y
```

The approved CSV input shape is `(N,C+1)`: string identifier in column zero and `C` normalized numeric scores. A headered CSV preserves its first-column heading; a headerless CSV labels it `Asset ID`. IDs must be nonempty, unique, at most 50 characters, and contain no control characters. `.npy`/`.npz` inputs contain only numeric `(N,C)` cores and receive positional IDs (`0`, `1`, ...).

Expected sample output:

```text
Ranking:
  1. B
  2. A
  3. C
```

Use the converter only when you need a numeric NumPy core. It validates and removes the specified identifier column; retaining source IDs requires keeping and using the original CSV.

```bash
python scripts/convert_matrix_csv.py examples/assets_priority/matrix_with_headers.csv out/assets_priority_cli.npy --has-header --id-col Asset
python -m electre3.cli out/assets_priority_cli.npy examples/assets_priority/criteria.json -y
```

The converted NumPy ranking prints positional IDs. The ranking uses raw net flow, <var>Φ</var>(a) = Σ<sub>b</sub> S(a,b) − Σ<sub>b</sub> S(b,a), ordered highest first. Scores are normalized to `[0,1]`. Minimize criteria have the approved `1-g` meaning; pairwise evaluation directly computes the equivalent `g(b)-g(a)` for numerical stability. Exact ties have no documented stable order.

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

The validator rejects missing criterion fields, invalid thresholds, missing or non-finite matrix values, values outside `[0,1]`, invalid identifiers, and header/criteria order mismatches. Correct the input or use the approved CSV missing-value replacement during preview; do not bypass validation.

## Documentation status

Phase 1 content is under D3 review. It is not a release claim. See `docs/decisions/d3-phase1-execution-notes.md` for execution evidence and limitations.
