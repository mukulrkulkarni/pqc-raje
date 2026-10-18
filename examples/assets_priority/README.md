# Assets priority example (CLI)

## Files

- `matrix_with_headers.csv` — includes asset names + column headers (Asset,E,X,O)
- `matrix_numeric_only.csv` — numeric-only 3×3 matrix in criterion order (E,X,O)
- `criteria.json` — weights + thresholds for E,X,O
- `asset_names.txt` — preserves mapping from row index to asset name

## Run (numeric-only CSV)

```bash
python -m electre3.cli examples/assets_priority/matrix_numeric_only.csv examples/assets_priority/criteria.json -y
```

The CLI prints the top-ranked alternatives as indices. Map indices to names using:

- 0 → A
- 1 → B
- 2 → C

## Run (header + ID CSV)

First convert to `.npy` using the converter:

```bash
python scripts/convert_matrix_csv.py examples/assets_priority/matrix_with_headers.csv out/assets_priority.npy --has-header --id-col Asset
python -m electre3.cli out/assets_priority.npy examples/assets_priority/criteria.json -y
```
