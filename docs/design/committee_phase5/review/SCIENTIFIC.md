# Scientific gate — N1 concordance pilot

**Verdict:** NEEDS WORK

**Chosen:**
- NEEDS WORK — Core math matches implementation, but credibility docs edge-case claim is incorrect.

**Near-miss:**
- APPROVED — Concordance/discordance notation, dimensions, and q=p boundary tests are consistent.

**Disqualified:**
- ELECTRE III distillation review — Out of scope; project uses net-flow ranking.

## Verified (implementation ↔ examples/tests)
- **Sign convention:** `diff = g(a) - g(b)` (see `electre3/block.py`) and concordance/discordance thresholds are applied to **negative** differences (`-q,-p,-v`) consistently (`electre3/concordance.py`, `electre3/discordance.py`).
- **Shapes:** `diff (B1,B2,C)`, `c_j (B1,B2,C)`, `C_ab (B1,B2)`, `d_j (B1,B2,C)`, `S (B1,B2)` consistent in code and tests.
- **q=p precedence/boundary:** When `q==p`, `partial_concordance` gives a step: `diff >= -q → 1`, else `diff <= -p → 0`. N1 test asserts `diff=-1.01→0, -1→1, -0.99→1` for `q=p=1` (`tests/test_concordance_n1.py`). This matches `np.where(diff >= -q, 1, np.where(diff <= -p, 0, ...))`.
- **Illustrative vs computed:** N1 tutorial example is executed in tests (`exec(...)`) and numerically asserted: `C_ab=[[0.85]]`, reverse direction gives `0.75` (`tests/test_concordance_n1.py`).
- **“a” and “b” meaning:** Tutorial includes the required clarification (“a and b are objects … not groups of data fields … [[[d1,d2,d3]]]”) and is enforced by a content test.

## Actionable scientific findings (batched)
### Introduced / N1-scope
1) **Incorrect credibility doc edge case.**
   - Evidence: `electre3/credibility.py` docstring says: “If C(a,b) = 1 and d_j > 1: S = 0 (veto overrides perfect concordance)”.
   - Problem: By construction `discordance()` clips to `[0,1]`, so `d_j > 1` cannot occur. The real edge is `C=1` and `d=1` ⇒ veto sets `S=0` (current code does this with `S[d >= 1.0] = 0.0`).
   - Fix: Adjust docstring to reflect achievable conditions (`d==1`), or remove the unreachable `d_j>1` claim.

2) **Weight/finite contracts are enforced, but not fully tested at ranking-pipeline level.**
   - Evidence: `normalize_weights()` rejects NaN/inf and requires `sum>0` (`electre3/validate.py`). `validate_matrix()` rejects NaN/inf (`electre3/validate.py`).
   - Gap: Existing tests cover matrix NaN/inf and weight normalization properties, but I did not see a test that `compute_ranking()` rejects **NaN/inf weights** via criteria input (only through direct `normalize_weights` tests). Consider adding a small negative test at pipeline level.

### Pre-existing (not N1-specific)
- None identified that block N1 scientific pilot, aside from the credibility docstring mismatch above.

## Evidence pointers
- Tutorial/example executable assertions: `tests/test_concordance_n1.py`.
- Core math: `electre3/concordance.py`, `electre3/discordance.py`, `electre3/block.py`.
- Credibility mismatch: `electre3/credibility.py` docstring vs code.
- Net-flow ranking (not distillation): `electre3/ranking.py`, `electre3/accumulator.py`.

## Test/verification limitations
- I did not execute tests; I only inspected assertions and source.
- No numerical audit of full ranking outcomes beyond ordering-by-net-flow invariant in tests.
