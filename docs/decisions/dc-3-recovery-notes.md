# DC-3 recovery notes

## Current and target labels

**Current before recovery:** `compute_ranking` materialized the approved normalized minimize transform `1-g`, then subtracted stored transformed values. This fulfilled ordinary mathematical semantics but lost a positive binary64 subnormal near zero because `1.0 - 5e-324` rounds to `1.0`.

**Target implemented:** the public minimize semantic remains `maximize=False -> 1-g` for normalized scores. The ranking pipeline now computes the equivalent pairwise value directly: maximize uses `g(a)-g(b)` and minimize uses `g(b)-g(a)`. The shared CLI/web contract continues to reject every non-finite or out-of-range score at `validate_score_matrix` before ranking, using the closed interval `[0,1]`.

## Proof and IEEE-754 finding

For normalized scores, exact arithmetic gives:

`(1-g(a))-(1-g(b)) = g(b)-g(a) = (-g(a))-(-g(b))`.

The direct form evaluates the right-hand expression from original scores, rather than subtracting two rounded `1-g` values. With `s = nextafter(0.0, 1.0)`, stored-transform subtraction yields `(1-s)-1 = 0`, while direct minimize evaluation `s-0 = 5e-324`, exactly matching the former negative-score representation. The recovery test covers this subnormal case and exact raw net flow. Adjacent binary64 values at thresholds `p=0.25` and `v=0.75` also match the independent negative-score reference.

## Implementation and scope

- `electre3/ranking.py` passes a `+1/-1` direction vector with raw score blocks.
- `electre3/block.py` applies that direction vector to raw pairwise differences.
- No transformed score matrix is stored or serialized.
- The approved semantic documentation of `1-g` remains true; only the numerically stable evaluation changes.
- `electre3/shared.py` remains the strict shared CLI/web validation boundary. It converts input to contiguous `float64`, rejects non-finite scores, then rejects values outside closed `[0,1]`.

## Evidence by category

| Category | Coverage | Result |
|---|---|---|
| Positive | endpoint minimize ranking; input preservation | Passed |
| Negative | below-zero, above-one, NaN, and infinities at shared boundary | Passed |
| Edge | q/p/v equality and adjacent ULP values | Passed |
| Scientific | subnormal direct difference and former `-g` reference raw flow | Passed |
| Regression | ranking, block, validation, shared contract, app workflow | Passed |
| Serialization/cache/download | canonical JSON/CSV, cache, authenticated app download | Passed |
| End-to-end | preview, compute, result download with subnormal score | Passed |

## Commands and results

| Command | Result |
|---|---|
| `python -m pytest tests/test_dc3_minimize_transform.py -q` | `16 passed in 0.51s` |
| `python -m pytest tests/test_dc3_minimize_transform.py tests/test_validate.py tests/test_ranking.py tests/test_ranking_deep.py tests/test_block.py tests/test_block_deep.py tests/test_shared_contract.py tests/test_serialization.py tests/test_result_cache.py tests/test_app_workflow.py tests/test_end_to_end_composition.py -q` | `152 passed in 1.61s` |
| `python -m pytest tests -q` | `907 passed in 7.56s` |
| `python -m compileall electre3 app tests` | Passed |
| `git diff --check` | Passed; no whitespace errors |

## Reviews

- **Scientific review: approved.** The direct formula is algebraically identical to `1-g` and avoids endpoint cancellation. Focused subnormal, threshold-ULP, mixed-direction, veto/tie, and raw-net-flow reference evidence passed.
- **Engineering review: approved.** The diff is confined to raw pairwise calculation, preserves public configuration and serializers, retains the shared CLI/web validator, and passes cache/download and full-suite regressions.
- **UI/UX review: not required.** This recovery changes no output, layout, navigation, or interaction.

## Tutorial notes and limitations

Tutorials should say that minimize semantics are `1-g` on normalized inputs, while implementation evaluates pairwise differences directly for IEEE-754 stability. Do not claim that explicitly materialized `1-g` values preserve every subnormal difference. Local tests do not establish production performance, deployment behavior, or external-client compatibility. Direct callers of low-level `compute_ranking` retain its historical non-normalized API; CLI/web users use `compute_validated_ranking` and its strict `[0,1]` contract.
