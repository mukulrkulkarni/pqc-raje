# Engineering review — follow-up (committee_phase5)

**Verdict:** APPROVED

## Scope
- `docs/design/committee_phase5/review/followup/manifest.json`
- `electre3/credibility.py` (two credibility docstring corrections)
- `tests/test_n1_scientific_followup.py` (7 follow-up regression tests)

## Evidence (static inspection)
- Credibility docstring matches implementation in `electre3/credibility.py`:
  - Edge case now states `d_j >= 1` forces `S = 0` even when `C(a,b)=1`.
  - Edge case now states `C(a,b)=1` and all finite `d_j < 1` yields `S = 1`.
  - Code enforces: `S[d >= 1.0] = 0.0` and no other reduction applies for `C=1` when `d<1`.

- Ranking pipeline rejection is before block computation:
  - `electre3/ranking.py::compute_ranking` calls `normalize_weights(criteria)` before `compute_block`.
  - `tests/test_n1_scientific_followup.py::test_ranking_rejects_nonfinite_mutated_weights_before_compute` mutates a valid `CriterionConfig.weight` to `NaN/+Inf/-Inf`, monkeypatches `ranking_module.compute_block` to fail if called, and asserts `compute_ranking()` raises `ValueError` with the expected message.

- Boundary and order coverage for full veto:
  - `test_full_veto_at_perfect_concordance` checks:
    - `d = nextafter(1,0)` keeps `S=1` when `C=1`.
    - `d = 1` or a permuted order with `1` present yields `S=0`.
  - Also asserts inputs `C` and `d` are not mutated.

## Evidence (executed tests)
- Ran targeted file only: `pytest -q tests/test_n1_scientific_followup.py`
  - Result: `7 passed in 0.28s`.

## Non-goals / constraints
- No production code edits performed in this review.
- No claim about full-suite status beyond what `manifest.json` records (`computation_AST_unchanged: true`).
