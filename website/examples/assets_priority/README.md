# Assets priority example (CLI)

## Files

- `matrix_with_headers.csv` — approved headered `(N,C+1)` CSV: `Asset` plus E, X, O scores.
- `matrix_numeric_only.csv` — numeric `(N,C)` core in criterion order (E, X, O).
- `criteria.json` — weights and thresholds for E, X, O.
- `ranking.txt` — expected ranking for the supplied CSV: B, A, C.

Identifiers are required for CSV. Headered CSV preserves its first heading (`Asset` here). Headerless CSV uses `Asset ID`; in both forms identifiers must be nonempty, unique, control-character-free, and no longer than 50 characters.

## Run the identifier-bearing CSV directly

```bash
python -m electre3.cli examples/assets_priority/matrix_with_headers.csv examples/assets_priority/criteria.json -y
```

Expected output:

```text
Ranking:
  1. B
  2. A
  3. C
```

## Run the numeric core

```bash
python -m electre3.cli examples/assets_priority/matrix_numeric_only.csv examples/assets_priority/criteria.json -y
```

Numeric matrices intentionally use positional identifiers, so the same result prints `1`, `0`, `2` rather than source names.

## Convert to NumPy deliberately

```bash
python scripts/convert_matrix_csv.py examples/assets_priority/matrix_with_headers.csv out/assets_priority.npy --has-header --id-col Asset
python -m electre3.cli out/assets_priority.npy examples/assets_priority/criteria.json -y
```

The converter validates and removes the source identifier column. A `.npy` file contains numeric scores only and therefore has positional identifiers. Keep the original CSV to retain source identifiers.

Minimize criteria retain the approved normalized `1-g` semantics. The implementation evaluates pairwise differences directly as `g(b)-g(a)` for numerical stability.
