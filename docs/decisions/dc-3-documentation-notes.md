# DC-3 documentation notes

## Current and target status

**Current implementation:** `electre3/ranking.py` transforms every normalized minimize column with `1.0 - g` before pairwise computation. DC-1 proves ordinary boundary translation for `g = 0`, `0.5`, and `1`.

**Target contract:** prove the approved `maximize=False -> 1-g` transformation against the former `-g` representation for normalized scores, including ordinary and IEEE-754 boundaries. The target also requires q/p/v boundary, veto, tie, mixed-direction, and raw-net-flow evidence.

**Status: blocked — not finalized.** DC-3 stopped before review, regression, and commit because the required IEEE-754 pairwise-difference invariance fails in the current implementation.

## Proof and failure evidence

In exact arithmetic,

`(1 - g_a) - (1 - g_b) = (-g_a) - (-g_b) = g_b - g_a`.

In binary64 arithmetic, subtraction of a subnormal score from `1.0` rounds to `1.0`. For `g = nextafter(0.0, 1.0)`, the transformed pairwise difference is `0.0`, while the former negative representation retains `5e-324`. The focused scientific test also observed a one-ULP raw-net-flow difference for `nextafter(0.25, 0.0)`.

The input validator additionally rejects non-finite values but does not itself enforce the claimed closed normalized interval `[0,1]`; `nextafter(0.0, -1.0)` and `nextafter(1.0, 2.0)` reach ranking without an exception.

## Tests by category

| Category | Evidence | Result |
|---|---|---|
| Positive | endpoints `g=0,0.5,1`; lower minimize score ranks first | Passed |
| Mixed directions | maximize and minimize criteria; raw net flow | Passed |
| q/p/v and veto | equality and adjacent values around `p=0.25`, `v=0.75`; ties | One q/p adjacent case failed exact raw-flow equality |
| Old `-g` invariance | independent pairwise/block reference | Failed at subnormal IEEE-754 endpoint |
| Negative | non-finite score rejection | Passed |
| Normalized boundary | values just below `0` and above `1` | Failed; no `ValueError` |

## Command and result

`python -m pytest tests/test_dc3_minimize_transform.py -q`

Result: `3 failed, 10 passed in 0.49s`.

Failures: exact old-`-g` raw-flow equality at `nextafter(0.25, 0.0)`; pairwise-difference equality at `nextafter(0.0, 1.0)`; rejection of just-outside `[0,1]` values.

## Tutorial notes

Do not publish a tutorial claim that `1-g` is bitwise equivalent to `-g` for all IEEE-754 normalized inputs. The ordinary mathematical identity remains valid, but the current floating-point implementation lacks the required subnormal invariant proof.

## Limitations and next action

No Scientific or Engineering approval was obtained, because the mandatory stop condition occurred before review. No UI/UX review is required: this chunk changes no user-facing output or layout. No relevant regression suite, compileall check, diff acceptance check, or commit was run after the failed focused acceptance test. A new approved recovery scope must decide whether to constrain accepted score granularity, reformulate pairwise computation, or revise the required IEEE-754 contract; this DC-3 scope must not expand unilaterally.
