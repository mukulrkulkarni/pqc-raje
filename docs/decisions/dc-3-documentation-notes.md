# DC-3 documentation notes — superseded

> **Superseded on 2026-10-22 by [DC-3 recovery notes](dc-3-recovery-notes.md).**
> The recovery implements stable direct pairwise evaluation, restores the shared
> closed `[0,1]` validation boundary, and records passing scientific and
> regression evidence. This retained record describes the pre-recovery failure
> only. Do not use it as current implementation, validation, or release status.

## Historical pre-recovery status

**Current implementation at the time:** `electre3/ranking.py` transformed every normalized minimize column with `1.0 - g` before pairwise computation. DC-1 proved ordinary boundary translation for `g = 0`, `0.5`, and `1`.

**Target contract at the time:** prove the approved `maximize=False -> 1-g` transformation against the former `-g` representation for normalized scores, including ordinary and IEEE-754 boundaries. The target also required q/p/v boundary, veto, tie, mixed-direction, and raw-net-flow evidence.

**Historical status: blocked — not finalized.** DC-3 stopped before review, regression, and commit because the required IEEE-754 pairwise-difference invariance failed in that implementation.

## Historical proof and failure evidence

In exact arithmetic,

`(1 - g_a) - (1 - g_b) = (-g_a) - (-g_b) = g_b - g_a`.

In binary64 arithmetic, subtraction of a subnormal score from `1.0` rounds to `1.0`. For `g = nextafter(0.0, 1.0)`, the transformed pairwise difference was `0.0`, while the former negative representation retained `5e-324`. The focused scientific test also observed a one-ULP raw-net-flow difference for `nextafter(0.25, 0.0)`.

The input validator at that time additionally rejected non-finite values but did not itself enforce the claimed closed normalized interval `[0,1]`; `nextafter(0.0, -1.0)` and `nextafter(1.0, 2.0)` reached ranking without an exception.

## Historical tests by category

| Category | Evidence | Result |
|---|---|---|
| Positive | endpoints `g=0,0.5,1`; lower minimize score ranks first | Passed |
| Mixed directions | maximize and minimize criteria; raw net flow | Passed |
| q/p/v and veto | equality and adjacent values around `p=0.25`, `v=0.75`; ties | One q/p adjacent case failed exact raw-flow equality |
| Old `-g` invariance | independent pairwise/block reference | Failed at subnormal IEEE-754 endpoint |
| Negative | non-finite score rejection | Passed |
| Normalized boundary | values just below `0` and above `1` | Failed; no `ValueError` |

## Historical command and result

`python -m pytest tests/test_dc3_minimize_transform.py -q`

Historical result: `3 failed, 10 passed in 0.49s`.

Failures: exact old-`-g` raw-flow equality at `nextafter(0.25, 0.0)`; pairwise-difference equality at `nextafter(0.0, 1.0)`; rejection of just-outside `[0,1]` values.

## Historical tutorial warning

Do not publish a tutorial claim that explicitly materialized `1-g` is bitwise equivalent to `-g` for all IEEE-754 normalized inputs. The ordinary mathematical identity remained valid, but that floating-point implementation lacked the required subnormal invariant proof.

## Historical limitation and next action

No Scientific or Engineering approval was obtained at this historical checkpoint because the mandatory stop condition occurred before review. No UI/UX review was required: that chunk changed no user-facing output or layout. No relevant regression suite, compileall check, diff acceptance check, or commit was run after the failed focused acceptance test.

**Current authority:** [DC-3 recovery notes](dc-3-recovery-notes.md).
