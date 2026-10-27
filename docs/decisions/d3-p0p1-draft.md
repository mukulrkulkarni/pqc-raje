# D3 P0/P1 Documentation Correction Draft

**Status:** Draft only. PI acceptance is deferred until the D3 stage ends.
**Base:** Current local release state; no user-facing edits are authorized by this draft.

## Legacy compatibility routes

The supported user journey is the server-rendered `/app/` workflow:

1. Enter criteria.
2. Provide a matrix.
3. Review and confirm the preview.
4. Compute and inspect results.

The following routes are **legacy compatibility surfaces**, not the primary browser workflow:

- `/preview/<upload_id>`
- `/preview/<upload_id>/confirm`
- `/preview/<upload_id>/cancel`
- `/compute/start`
- `/compute/status/<job_id>`
- `app/templates/preview.html`
- `app/templates/config.html`

Do not direct new users to these routes. Keep their compatibility tests and label them clearly in maintainer documentation.

## Debugging correction

For the supported `/app/` workflow, computation requires a successful preview and explicit confirmation. A missing preview or confirmation returns **HTTP 400**. Inspect the response message and return to the relevant form.

The legacy JSON flow has separate confirmation behavior: an unconfirmed upload at `/compute/start` returns **HTTP 403**. Treat it as compatibility-only. Do not use its errors as the instructions for `/app/` users.

## CLI output reconciliation

The direct CSV path and converter-first NumPy path use different identifier handling:

- Identifier-bearing CSV preserves source identifiers.
- Numeric `.npy` input uses positional identifiers such as `0`, `1`, and `2`.
- The ranking order can be the same while printed labels differ.

For the committed Asset Priority example, the direct CSV path preserves source identifiers and ranks `B`, `A`, `C`; this is recorded in `examples/assets_priority/ranking.txt`. The converted NumPy path uses zero-based row identifiers and prints `1`, `0`, `2`; verify this path with the command below rather than citing `ranking.txt`. These are identifiers, not one-based rank positions.

The method computes ELECTRE III credibility followed by descending raw net-flow ranking. In a block, row entries contain `a` alternatives and column entries contain comparison-group `b` alternatives. For alternative objects `a` and `b`, `Φ(a)=Σ_b S(a,b)−Σ_b S(b,a)`. Scores are not normalized, and `np.argsort(-net_flow)` provides no explicit stable tie policy; tied alternatives must not be presented as scientifically distinct or guaranteed in source order.

Reproduction commands at the pinned revision:

```cmd
set PYTHONPATH=.
python scripts/convert_matrix_csv.py examples/assets_priority/matrix_with_headers.csv out/d3-p0p1-matrix.npy --has-header --id-col Asset
python -m electre3.cli out/d3-p0p1-matrix.npy examples/assets_priority/criteria.json -y
```

Expected converted-path ranking identifiers: `1`, `0`, `2`. Source evidence: `electre3/data.py::load_input`, `electre3/ranking.py::compute_ranking`, `electre3/accumulator.py::NetFlowAccumulator`, `electre3/block.py::compute_block`, and `scripts/convert_matrix_csv.py::convert_csv_to_matrix`.

## Evidence required before publication

Record the exact revision, command, exit status, output, source path, and limitation. Cover positive, negative, and edge cases for:

- valid CLI and web workflows;
- malformed criteria, matrix, headers, and missing values;
- legacy-route and missing-target behavior;
- identifier, eight-criteria, block-size, and score boundaries;
- security headers, session, tokens, cache, and downloads;
- semantic forms, tables, math, and no-script output;
- local links, deliberate broken links, and generated website paths.

Browser rendering, keyboard, zoom, reflow, offline, screen-reader, and load evidence remain deferred and non-blocking. Do not claim those checks passed.

## Source evidence

Pinned revision: `69f2c24`. Current command/test evidence is required before publication; this draft records planned evidence, not newly executed results.

- `app/routes/workflow.py`
- `app/routes/preview.py`
- `app/routes/compute.py`
- `docs/runbook/debugging.md`
- `docs/tutorials/cli_quickstart.md`
- `docs/GETTING_STARTED.html`
- `website/index.html`
- `electre3/cli.py`
- `electre3/shared.py`
- `examples/assets_priority/`
- `tests/test_app_workflow.py`
- `tests/test_docs_routes.py`
- `tests/test_convert_matrix_csv.py`
- `tests/test_cli_run.py`
