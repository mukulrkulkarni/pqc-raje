# Chunk 1: Shared validated-input contract and compute adapter

## Implemented scope

- `electre3.shared.validate_criteria` requires one through eight criteria.
- Each criterion requires a non-empty `name`, positive finite `weight`, finite `q`, `p`, and `v`, plus strict Boolean `maximize`.
- Criteria weights must sum to one within `1e-12`; thresholds require `0 <= q <= p <= v`.
- `validate_score_matrix` requires a two-dimensional, finite float64 matrix with two through 100,000 rows, exact criterion columns, and scores in `[0, 1]`.
- `validate_csv_headers` supports the approved identifier-column mapping: any non-empty identifier header followed by criterion names in exact order.
- `compute_validated_ranking` validates inputs, enforces a block size from 1 through 10,000 (default 1,000), calls `electre3.ranking.compute_ranking`, and returns ranking plus `accumulator.net_flow()`.
- `electre3.cli_run.run_ranking` now calls the adapter and retains its ranking-only return type.
- `app.services.security.validate_criteria_json` delegates to the strict shared criteria validator while retaining its error-string compatibility API.

## Compatibility change

The CLI helper now rejects historical permissive inputs: missing `name` or `maximize`, weights not summing to one, and score values outside `[0, 1]`. This explicitly implements the approved shared CLI/web policy. Existing legacy tests expecting permissive input require separate migration and are not changed in this chunk.

## Deliberate exclusions and dependency

This chunk does not implement routes, upload parsing, cache management, serializers, download endpoints, feasibility timing, or fixed-order reduction. The approved byte-identity requirement remains a later dependency because canonical serializers and block-size-invariant accumulation are explicitly out of scope.

## Security and resource bounds

Validation rejects non-finite values before core computation. It bounds criteria, rows, score domain, and block size. The adapter creates only an O(N) net-flow result in addition to the existing blockwise core's current-block intermediates; it does not persist N×N outputs.
