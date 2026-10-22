# DC-1 documentation notes

## Status

**Current before DC-1:** CSV parsing was split: the `/app` headered path retained row labels for display, but the shared ranking result generated positional identifiers. Headerless `/app` CSV accepted numeric `(N,C)` rows and fabricated positions. Core minimization negated scores (`-g`). Canonical artifacts used serializer version `1`.

**Target implemented in DC-1:** CSV has raw shape `(N,C+1)`: column 0 is an identifier and columns 1..C are finite normalized scores. Headerless displays `Asset ID`; headered preserves a non-empty source identifier heading. Identifiers must be strings, non-empty after trim, unique, and at most 50 characters. Core ranking receives numeric `(N,C)` scores only. `RankingResult` carries the source identifiers into JSON and CSV serializers. NumPy input remains numeric-only and receives positional `"0"..."N-1"` identifiers. Serializer version is `2`. Valid minimization uses `1-g` after normalized-score validation.

## Source evidence

- User-approved DC-1 task and shared scratch-pad contract, 2026-10-22.
- `docs/decisions/data-contract-impact-assessment.md`: pre-change source inspection and migration scope.
- `docs/decisions/data-contract-test-matrix.md`: required positive, negative, edge, scientific, cache, UI, and end-to-end coverage.
- `electre3/shared.py`, `electre3/data.py`, `app/routes/workflow.py`, and `electre3/serialization.py`: implementation sources.

## Migration

1. CSV producers must add a string identifier in column 0. Headered producers must provide `identifier_header,criterion_1,...,criterion_C`; criterion headers must match the configured criterion names in order.
2. Headerless CSV producers must provide `identifier,score_1,...,score_C`; the UI displays the first heading as `Asset ID`.
3. Existing numeric `.npy` and one-array `.npz` input remains supported and uses positional identifiers. Object arrays and pickle loading remain disallowed.
4. Consumers must accept serializer version `2`; version `1` manifests are intentionally rejected by current-version reassembly.

## Tutorial notes

A headered CSV example:

```csv
Asset ID,quality,cost
asset-A,0.9,0.2
asset-B,0.4,0.8
```

The ranking stores `("asset-A", "asset-B")` by source row. A ranking index resolves to an identifier with `result.identifiers[index]`; rank position is not an identifier. For a minimizing normalized criterion, `g=0` becomes `1`, `g=1` becomes `0`, and pairwise score differences are preserved because `(1-a)-(1-b)=b-a`.

## Commands and results

| Category | Command | Result |
|---|---|---|
| Unit, integration, serialization, cache/download, security, UI, end-to-end | `python -m pytest tests/test_dc1_contract.py tests/test_data.py tests/test_shared_contract.py tests/test_serialization.py tests/test_app_workflow.py tests/test_cli_run.py tests/test_result_cache.py tests/test_security.py tests/test_end_to_end_composition.py -q` | `110 passed in 1.59s` |
| Scientific/ranking and relevant regressions | `python -m pytest tests/test_ranking.py tests/test_ranking_deep.py tests/test_integration.py tests/test_convert_matrix_csv.py tests/test_negative.py tests/test_ui_styles.py -q` | `114 passed in 1.45s` |
| Compilation and diff whitespace | `python -m compileall electre3 app tests && git diff --check` | Passed; compilation completed and `git diff --check` produced no errors. |

The dedicated DC-1 tests cover positive headered/headerless identifiers, positional NumPy identifiers, empty/duplicate/overlength identifier rejection, v2 serialization, minimized-score translation invariance at `0`, `0.5`, and `1`, and a full `/app` preview/compute/download flow.

## Limitations

- DC-1 does not perform the broader CSV migration, rewrite examples, create user-facing pages, or alter D3 documentation.
- Legacy `load_matrix` remains numeric-only for compatibility; identifier CSV ingestion uses `load_input` or the `/app` workflow.
- Testing is local Python/Flask coverage only. No browser accessibility, external deployment, or performance load verification occurred.
