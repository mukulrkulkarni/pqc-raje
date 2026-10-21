# Chunk 2C Documentation Notes

**Purpose:** Record the runtime-control implementation and measured evidence. This note does not claim cache, downloads, split artifacts, or new routes.

## Implemented

- `electre3/runtime.py` defines the deterministic runtime model.
- The model uses the largest measured pair-cost coefficient and a 1.25 safety factor.
- The model includes complete runner time. The benchmark runner performs matrix creation, shared validation, ranking, and canonical JSON serialization.
- `require_feasible` rejects an estimated p95 runtime above 300 seconds.
- `compute_validated_ranking` activates the gate when its caller supplies a `RuntimeModel`.
- `compute_ranking` checks a monotonic deadline before every block and before return.
- The default hard deadline is 330 seconds.
- A deadline raises `ComputeTimeoutError`. It returns no `RankingResult`, so callers cannot serialize a partial result.
- The accumulator adds values in global scalar order. This removes block-dependent floating-point sum grouping.
- Canonical result metadata excludes the execution-only block size. Equivalent results serialize to identical bytes.

## Verified

The bounded benchmark request includes these points:

- <var>N</var> = 100, 500, 1,000, 5,000, 10,000, and 15,000.
- <var>C</var> = 4 and 8.
- Block size = 1,000, 5,000, and 10,000.

The harness records all 36 points in `out/chunk-2c-benchmark.json`.

It measures only bounded points. It rejects larger points instead of running them. The bound is 1,000 rows and 256 MiB temporary block memory. The temporary-memory estimate is <var>min</var>(<var>N</var>, <var>B</var>)<sup>2</sup> × <var>C</var> × 48 bytes.

Measured points include 100 and 500 rows for four and eight criteria, plus 1,000 rows for four criteria. The 1,000-row, eight-criterion cases reject on temporary memory. All 5,000-, 10,000-, and 15,000-row cases reject on the measured-row bound. The harness does not run a 100,000-row computation.

The resulting conservative model estimates 100,000 rows and eight criteria at 73,085.500 seconds on this host. The 300-second gate therefore rejects that request.

Focused tests prove byte-identical canonical JSON for block sizes 1, 7, 48, 1,000, 5,000, and 10,000. Tests also cover deterministic estimates, acceptance at the exact limit, rejection above the limit, bounded benchmark records, and timeout behavior.

Commands executed:

```text
python -m scripts.benchmark_runtime
python -m pytest tests/test_runtime.py tests/test_shared_contract.py tests/test_serialization.py tests/test_cli_run.py tests/test_accumulator.py tests/test_accumulator_deep.py -q
python -m compileall electre3 app scripts
git diff --check
```

Results: the benchmark artifact was written; 66 focused tests passed; compilation and diff checks passed.

## Planned

- A deployment profile must load host-specific measured benchmark records and pass the resulting `RuntimeModel` to the compute boundary.
- Chunk 2D owns cache, downloads, split artifacts, and their route integration.
- No new route or UI control exists in Chunk 2C.

## Debugging guidance

Run `python -m scripts.benchmark_runtime` from the repository root. The command writes the JSON record to `out/chunk-2c-benchmark.json`. Use `python -m scripts.benchmark_runtime`, not `python scripts/benchmark_runtime.py`, so Python can import the project package.

When a request is rejected, report the estimated p95 value and the 300-second limit. When computation times out, discard the accumulator and do not serialize it. Do not reduce rows or change a block size without a new user request.

## Tutorial-writing rules

Use existing server-rendered and accessible UI patterns. Use semantic HTML math notation such as `<var>N</var>`, `<var>C</var>`, and `<sup>2</sup>`. Do not add KaTeX, JavaScript, a build step, cache claims, download claims, split-artifact claims, or new route claims.
