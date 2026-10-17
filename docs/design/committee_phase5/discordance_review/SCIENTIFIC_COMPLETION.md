# Phase 5 — Discordance scientific gate completion

Status: **APPROVED**

Scope: ELECTRE III **discordance**, its role in **credibility**, and linkage to **net-flow ranking** (not distillation). Evidence is taken from the pinned snapshot files whose hashes were verified in `docs/design/committee_phase5/discordance_review/snapshot_verification.json`.

## Evidence reviewed (snapshot, hash-verified)
- `docs/design/committee_phase5/discordance_review/snapshot/docs/modules/discordance_tutorial_side_by_side.html`
- `docs/design/committee_phase5/discordance_review/snapshot/tests/test_discordance_deep.py`
- `docs/design/committee_phase5/discordance_review/snapshot/tests/test_module_docs.py` (discordance section only)

Implementation cross-checks used live sources:
- `electre3/discordance.py`
- `electre3/credibility.py`
- `electre3/concordance.py`
- `electre3/ranking.py`

## Scientific/notation audit findings

### 1) Notation correctness: a,b are objects; row/column are comparison groups
Verified in tutorial Notation block:
- “**a and b are objects** … alternatives … not criteria.”
- “**B1 row objects** vs **B2 column objects** … comparison groups … may overlap … B1 need not equal B2.”
- Shape semantics: `diff[i,j,k] = g(row i, crit k) - g(col j, crit k)` and triple-bracket example `[[[d1,d2,d3]]]`.

This matches the implementation contracts in `electre3/discordance.py` and the deep test expectations.

### 2) Sign convention and boundaries (piecewise) match implementation
Implementation (`electre3/discordance.py`):
- veto-first precedence: `np.where(diff <= -v, 1.0, np.where(diff >= -p, 0.0, d_interp))`
- interpolation: `d_interp = (-diff - p) / (v - p)` with `denom==0` guarded.

Tutorial I/O Summary and rows R3–R5 state the same inequalities and interpolation, plus the key edge rule:
- **p=v: equality gives 1** (because veto-first branch wins at `diff == -p == -v`).

Deep tests confirm endpoints and p=v semantics:
- `test_strict_threshold_endpoints_and_interpolation`: diff=-6→1, diff=-3→0, diff=-5.5→5/6.
- `test_equal_threshold_veto_first`: diff=-3→1 when p=v=3; diff=-2.999→0.

### 3) Validation ownership and shape/finite contracts are correctly assigned
Tutorial explicitly assigns validation upstream:
- “Preconditions … caller responsibilities, **not validated here**.”
- “CriterionConfig checks finite thresholds at construction. The ranking entry point validates the performance matrix. … NumPy broadcasting can conceal a length-one vector mismatch.”

Deep test `test_lowlevel_nonfinite_and_mismatch_are_not_validation` matches current behavior:
- NaN propagates; ±inf saturate via comparisons/clipping.
- ValueError on mismatched lengths, but **length-one thresholds broadcast** (must not be documented as rejection).

### 4) Credibility linkage (veto sets S=0; reduction only when d > C)
Implementation (`electre3/credibility.py`) enforces:
- full veto: `S[d >= 1.0] = 0.0` (even when `C_ab == 1`).
- reduction factor only for `d > C_ab` and `d < 1`: multiply by `(1-d)/(1-C)`.

Tutorial row R5 states the same rule (“any d≥1 sets S(a,b)=0 … only criteria with d>C reduce S”).
Deep test `test_no_reduction_below_global_concordance_and_veto_at_one` matches this exact behavior.

### 5) Net-flow linkage (ranking uses credibility matrix blocks)
`electre3/ranking.py` shows the pipeline:
- negate non-maximize criteria before computing differences.
- compute block credibility `S = compute_block(...)` then update `NetFlowAccumulator`.
- final ranking: `np.argsort(-acc.net_flow())`.

Tutorial correctly states: “repository then uses **net-flow ranking**, not ELECTRE III distillation.”

### 6) Sensitivity example and reverse direction are computed, not pre-baked
Deep test `test_execute_usage_and_compare_visible_table` executes the tutorial’s embedded Python and compares computed results to the visible HTML table (including `7/18 ≈ 0.388889`). It also independently checks the reverse direction claim (B→A) and verifies `C=S=0.75` for that specific reverse diff.

This satisfies the requirement to distinguish illustrative inputs from computed, verified results.

## Limitations
- I did **not** run the test suite; conclusions are from static inspection of source and snapshot tests.
- Distillation procedures are out of scope by request; review covers credibility + net-flow ranking only.

## Decision
**APPROVED** — Notation, sign conventions, p=v veto-first equality, validation ownership, shape contracts, sensitivity and reverse-case examples all align between tutorial, tests, and implementations.
