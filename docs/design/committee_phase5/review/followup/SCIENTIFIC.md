# Scientific gate — N1 concordance pilot (follow-up)

**Verdict:** APPROVED

**Chosen:**
- APPROVED — Credibility edge-case doc now matches reachable values and is regression tested.

**Near-miss:**
- NEEDS WORK — Snapshot folder missing two-line docstring delta; only current source shows fix.

**Disqualified:**
- ELECTRE III distillation review — Out of scope; project uses credibility + net-flow ranking.

## Delta scope reviewed
- `docs/design/committee_phase5/review/followup/manifest.json`
- `electre3/credibility.py` (two corrected docstring lines)
- `tests/test_n1_scientific_followup.py` (follow-up regression tests)

## Verified deltas (evidence)
- **Docstring blocker resolved (reachable edge case):**
  - `electre3/credibility.py` now states: “If any `d_j >= 1`: `S=0` …” and “If `C(a,b)=1` and all finite `d_j < 1`: `S=1`”.
  - This matches implementation: `S[d >= 1.0] = 0.0` and no other factor applies when `C=1` and `d<1`.
- **Regression test covers both sides of the boundary at `d=1`:**
  - `tests/test_n1_scientific_followup.py::test_full_veto_at_perfect_concordance` asserts:
    - `d = nextafter(1,0)` yields `S=1` when `C=1`.
    - `d = 1` yields `S=0` (veto).
- **Ranking pipeline rejects non-finite weights before any block computation:**
  - `tests/test_n1_scientific_followup.py::test_ranking_rejects_nonfinite_mutated_weights_before_compute` mutates the (public, mutable) `CriterionConfig.weight` to `NaN/+Inf/-Inf`, monkeypatches `compute_block` to fail if called, and asserts `compute_ranking()` raises.
  - Implementation path: `compute_ranking()` calls `normalize_weights(criteria)` before `compute_block` (`electre3/ranking.py`), and `normalize_weights` raises on NaN/Inf (`electre3/validate.py`).
- **Computation unchanged claim is supported by recorded artifact:**
  - `manifest.json` records `computation_AST_unchanged: true` and “diff check passed”.

## Clarification carried forward (notation)
- “a” and “b” denote **objects / alternatives** being compared. Rows/columns index comparison groups `(B1,B2)`.

## Test/verification limitations
- I did not execute tests. Evidence for “659 tests passed; preflight passed” is taken from `docs/design/committee_phase5/review/followup/manifest.json`.
- Follow-up snapshot contains only the test file; it does not include the docstring-line snapshot.
