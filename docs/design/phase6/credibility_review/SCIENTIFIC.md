# Scientific gate — ELECTRE III credibility + net-flow ranking

**Scope (requested):**
- Snapshot docs/tests:
  - `docs/design/phase6/credibility_review/snapshot/docs/modules/credibility_tutorial_side_by_side.html`
  - `docs/design/phase6/credibility_review/snapshot/tests/test_credibility_deep.py`
  - Credibility-relevant section of `snapshot/tests/test_module_docs.py` (deep content tests C1).
- Live code audit (production sources):
  - `electre3/credibility.py`, `electre3/concordance.py`, `electre3/discordance.py`, `electre3/ranking.py`.

**Evidence limits:**
- No code executed in this review.
- Prior run evidence referenced in `REQUEST.md` ("88 targeted tests passed") is not re-verified here.
- Browser rendering, alignment, and responsive layout claims remain unverified by runtime inspection.

## Decision
NEEDS WORK.

## Key verified facts (matches implementation)
- **Credibility definition used:** `S` starts as `C_ab.copy()` then multiplies reduction factors for criteria where `(d > C_ab) & (d < 1)`; full veto is enforced by `S[d >= 1] = 0` per criterion. Source: `electre3/credibility.py`.
- **Strictness at boundary:** reduction uses **strict** `d > C_ab` (no reduction when `d == C_ab`) and `d < 1` (full veto handled separately). Source: `electre3/credibility.py`.
- **Full-veto override precedence:** `d >= 1` sets `S=0` even when `C_ab==1`. This is explicitly documented in the snapshot tutorial I/O Summary and implemented in code. Sources: snapshot HTML “Full veto takes precedence”; `electre3/credibility.py`.
- **Uses original concordance, not running S:** mask compares to `C_ab`, and denominator uses `1 - C_ab[mask]`. The deep test `test_masks_use_original_concordance_not_running_score` asserts this property. Sources: `electre3/credibility.py`; `snapshot/tests/test_credibility_deep.py`.
- **Net-flow ranking distinction:** ranking pipeline uses `NetFlowAccumulator` over blocks and returns `argsort(-acc.net_flow())`; no ELECTRE III distillation is present in the audited file. Source: `electre3/ranking.py`.
- **Sign convention is coherent across modules:** both concordance and discordance take `diff = g(a)-g(b)`; discordance opposes the assertion `a -> b` when `diff` is sufficiently negative (`<= -v`). Sources: `electre3/concordance.py`, `electre3/discordance.py`, snapshot tutorial notation.

## Findings (batched)

### Introduced / snapshot-documented behavior that is correct
- **Docs correctly explain objects/axes:** tutorial explicitly states “a and b are objects” and clarifies B1 row objects vs B2 column objects as comparison groups (not criteria). Source: snapshot HTML Notation section.
- **Docs separate illustrative vs computed values:** tutorial includes an explicit disclaimer and deep test executes the embedded code and matches table values, preventing “prewritten output” drift. Source: `snapshot/tests/test_credibility_deep.py::test_execute_example_matches_displayed_table`.

### Pre-existing implementation risks (scientific/contract)
- **Finite / bounds / dtype are not validated in `credibility()`:** NaN in `d_j` can bypass both masks and leave `S` unchanged (test asserts `NaN` discordance returns `.7`). Clipping at end can also hide invalid `C_ab` values. Sources: `electre3/credibility.py`; `snapshot/tests/test_credibility_deep.py::test_lowlevel_invalid_inputs_are_not_silently_called_valid`.
- **Criterion-axis emptiness is accepted at low level:** `d_j.shape[2]` loop runs zero iterations for shape `(B1,B2,0)` and returns `C_ab` unchanged (test asserts this). This is fine as a low-level function, but the tutorial I/O Summary currently says “at least one criterion” as a precondition while also saying “Preconditions are not validated here.” The contract needs one clear owner. Sources: snapshot HTML I/O Summary; `test_lowlevel_invalid_inputs...`.
- **Denominator guard `1e-10` is dead for valid masked entries:** for entries in `mask`, `d > C_ab` implies `C_ab < 1`, so `1-C_ab` cannot be zero. The guard is harmless, but documentation should not imply it is required for the valid `C=1` boundary; the snapshot grounding mostly gets this right.

### Pipeline ownership / diagonal clearing
- **No diagonal enforcement in `credibility()`:** deep test confirms diagonal stays as input concordance (e.g., diag of ones remains ones). Tutorial states diagonal is cleared downstream (`compute_block`). This is consistent. Sources: snapshot HTML; `snapshot/tests/test_credibility_deep.py`.

## What blocks approval (actionable)
- **One contract inconsistency:** tutorial I/O Summary states “finite values in [0,1]… at least one criterion” as input requirements, but tests explicitly demonstrate empty-criterion and NaN handling is allowed/undefined at low level. Choose one:
  - declare these as *pipeline-level* requirements (validated elsewhere), or
  - narrow tutorial language to “expected in normal pipeline; not enforced here; direct callers must enforce.”

## Test reuse and limitations
- Reused snapshot tests as evidence only; no execution.
- The deep test suite provides strong guarantees about veto precedence, strict inequalities, and use of original `C_ab`, but does not prove upstream validators always run for all entry points.
