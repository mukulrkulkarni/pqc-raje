# CLI Quickstart (identifier CSV → ELECTRE III ranking)

This tutorial runs the ranking pipeline using an approved identifier-bearing CSV and a criteria JSON file.

**What you get:** a deterministic ranking of source identifiers. The CLI validates finite normalized scores in `[0,1]`, CSV identifier rules, and ordered header names. It prints the first ten ranked identifiers and saves ranking row indices when `-o` is used. It does not save net-flow scores. Equal internal net-flow values have no documented stable relative order.

## Phase 1: verify the committed Asset Priority scenario

Run commands from the repository root with Python 3.10 or newer and the repository environment.

```bash
python -m compileall -q electre3 app
python -m electre3.cli examples/assets_priority/matrix_with_headers.csv examples/assets_priority/criteria.json -y
```

Expected output is `B`, then `A`, then `C`. This applies only to the committed sample data. Exact ties have no documented stable order.

## Data contract

### Identifier-bearing CSV

CLI CSV input has shape **`(N,C+1)`**:

- Column zero is the string identifier for each alternative.
- The remaining `C` columns are numeric criterion scores in criteria JSON order.
- Headered CSV preserves its first heading and must list criterion names in exact order.
- Headerless CSV has no heading and uses the display label `Asset ID`.
- Identifiers must be nonempty, unique, at most 50 characters, and contain no control characters.
- Scores must be numeric, finite, and in `[0,1]`.

### Numeric NumPy core

`.npy` and `.npz` inputs have shape **`(N,C)`** and have no source identifiers. The CLI assigns positional identifiers `0`, `1`, ..., `N-1`. Use the original CSV whenever source identifiers must remain visible.

### Criteria JSON

A JSON list of length `C`. Each criterion has `name`, `weight`, `q`, `p`, `v`, and Boolean `maximize`. Thresholds satisfy `0 ≤ q ≤ p ≤ v`; weights sum to `1`.

## Prepare inputs

### Headered CSV

```csv
Asset,E,X,O
A,0.90,0.40,0.60
B,0.60,0.90,0.70
C,0.70,0.60,0.50
```

Run it directly:

```bash
python -m electre3.cli matrix.csv criteria.json -y
```

### Headerless CSV

Remove the header but retain identifier column zero:

```csv
A,0.90,0.40,0.60
B,0.60,0.90,0.70
```

The loader labels its identifier column `Asset ID`. Header detection is automatic only when the first row exactly matches the criteria names after its identifier heading; callers that use `load_input` can select `header_mode` explicitly.

### Convert deliberately to NumPy

```bash
python scripts/convert_matrix_csv.py matrix.csv out/matrix.npy --has-header --id-col Asset
python -m electre3.cli out/matrix.npy criteria.json -y
```

The converter validates then removes IDs and emits only the numeric core. The subsequent NumPy CLI run prints zero-based positional identifiers, not source IDs or one-based rank positions. For the committed Asset Priority sample, direct CSV ranks `B`, `A`, `C`, while the converted NumPy path prints `1`, `0`, `2`; both describe the same ordering. Verify the converted path with the commands above rather than citing `examples/assets_priority/ranking.txt`, which records the direct CSV labels. Empty numeric cells fail unless `--fill-empty` supplies a finite model-approved value.

## CLI options

```bash
python -m electre3.cli matrix.csv criteria.json -b 1000
python -m electre3.cli matrix.csv criteria.json -b 1000 -y
python -m electre3.cli matrix.csv criteria.json -b 1000 -y -o out/ranking.npy
```

- Without `-y`, the CLI prints a preview and asks for confirmation.
- `-b/--block-size` controls blockwise memory.
- `-o` saves ranking row indices, ordered best to worst.

## Direction and interpretation

Net flow is `φ(a) = Σ_b S(a,b) − Σ_b S(b,a)`, ranked descending. The diagonal is excluded. Minimize criteria have the approved normalized `1-g` meaning. The implementation evaluates pairwise values directly as `g(b)-g(a)` for numerical stability, including subnormal binary64 inputs.

## Complete CLI reference

```text
python -m electre3.cli matrix_file criteria_file [-o OUTPUT] [-b BLOCK_SIZE] [-y] [-q]
```

- `matrix_file` accepts an identifier-bearing CSV, numeric `.npy`, or one-array `.npz`.
- `criteria_file` is a UTF-8 JSON criteria list.
- `-b`/`--block-size` accepts an integer from 1 through 10000; the default is 1000.
- `-y`/`--yes` skips confirmation prompts.
- `-q`/`--quiet` suppresses computation, status, and save messages. It does not suppress prompts or ranking output when `--output` is absent.
- `-o`/`--output` saves zero-based ranking row indices with NumPy serialization. It does not save identifiers or raw net-flow scores.

Errors print to standard error and return a nonzero exit code. The ranking deadline covers ranking computation; parsing, request handling, and response serialization are separate work.

## Reference and source ownership

The CLI ranks by descending raw net flow after ELECTRE III credibility. This is not ELECTRE III distillation. Raw flow excludes the diagonal: `φ(a) = Σ(b≠a) S(a,b) − Σ(b≠a) S(b,a)`. `NetFlowAccumulator.normalize()` is not used for ranking. Exact equal flows are ties; `np.argsort(-net_flow)` has no documented stable relative order within a tie.

Validated minimize criteria compare `g(b)-g(a)`, which is equivalent to normalized `1-g` without storing rounded transformed values. Shared CLI/web entry points validate scores in `[0,1]`, one through eight criteria, positive weights summing to one, and `0 ≤ q ≤ p ≤ v`. At equal thresholds, the full-concordance branch has priority when `q=p`, and the full-veto branch has priority when `p=v`.

- CLI entrypoint: `electre3/cli.py`
- CSV/NumPy loader: `electre3/data.py` (`load_input`)
- Shared validator and result builder: `electre3/shared.py`
- Ranking pipeline: `electre3/ranking.py`
- Concordance, discordance, credibility: `electre3/concordance.py`, `electre3/discordance.py`, `electre3/credibility.py`
- Flow accumulator: `electre3/accumulator.py`
- CSV converter: `scripts/convert_matrix_csv.py`
- App workflow and cache: `app/routes/workflow.py`, `app/services/result_cache.py`
- [Debugging, runtime, migration, and reproducibility](../runbook/debugging.md)
