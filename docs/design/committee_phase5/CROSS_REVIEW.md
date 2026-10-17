# Phase 5 — ONE cross-review (prototype scientific content)

Decision: **APPROVED** (bounded to N1/N2 prototype scientific content).

Evidence base (static inspection only):
- Prototypes: `docs/design/committee_phase5/N1.html`, `docs/design/committee_phase5/N2.html`
- Verified notes: `docs/design/committee_phase5/VERIFIED_CORRECTIONS.md`, `docs/design/committee_phase5/example_results.json`
- Governing code: `electre3/concordance.py`, `electre3/discordance.py`, `electre3/credibility.py`, `electre3/ranking.py`

## What matches the verified corrections
- **a and b are objects**; **a→b is the directed assertion under assessment** (both prototypes state this explicitly).
- **B1 (rows) / B2 (cols) are comparison groups of objects**, not data fields; `diff` axes interpreted as (B1,B2,C).
- **Sign convention**: `diff = g(a) − g(b)`; reversing direction flips sign; example uses this.
- **Boundary behavior**:
  - Concordance uses `diff >= -q ⇒ 1` and `diff <= -p ⇒ 0`.
  - **q=p step semantics** are correctly described as “outer branch wins”.
- **Weights**: prototypes state “nonnegative, sum 1” and that `global_concordance` does not validate/normalize.
- **Orientation ownership**: prototypes correctly assign minimization handling to `ranking.compute_ranking` and require direct callers to pre-orient.
- **Verified example vs illustrative inputs**: prototypes label inputs “illustrative” and outputs “verified”; values match `example_results.json` (A→B 0.85, B→A 0.75).

## Actionable issues (prototype-content only)
- None found in the requested scope (concordance content + verified example + notation contract).

## Test / execution limitations
- I did **not** execute `verify_example.py`, import the package, or render HTML; I only checked stated results against the committed `example_results.json` and inspected code paths.
