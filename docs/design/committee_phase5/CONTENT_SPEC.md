# Phase 5 — CONTENT_SPEC (scientific content, bounded)

Scope: concordance + discordance + credibility inputs/arrays and notation for UI layouts (N1 vs N2). Evidence base: `electre3/concordance.py`, `electre3/discordance.py`, `electre3/credibility.py`, `electre3/ranking.py`, `electre3/validate.py`, and the Phase 5 verified artifacts.

Limitations: static code inspection only. I did not execute Python or render HTML in a browser. Numeric values are either (a) taken from `docs/design/committee_phase5/example_results.json` (explicitly verified elsewhere), or (b) illustrative.

---

## A) Content meta-template (compact)

Use this table as the “content blocks” contract for UI/UX prototypes.

| Section name | Content style | Goal | Prerequisites |
|---|---|---|---|
| 0. Module header | Text | Identify module/function and what it computes | None |
| 1. I/O Summary | Balanced (text + shapes) | Show inputs/outputs and array shapes (B1,B2,C) | Know “object/alternative” |
| 2. Notation contract | Math-first, short | Fix symbol meanings; prevent C collisions; fix direction a→b | None (may appear before or after I/O) |
| 3. Shape + broadcasting notes | Text + mini-diagram | Explain why `diff` is 3D; interpret triple brackets | Notation contract |
| 4. Threshold conventions | Math + boundary bullets | State inequalities for q/p/v; include exact boundary behavior | Notation contract |
| 5. Worked example (collapsible) | Balanced (table + math) | One directed pair: diff → c_j → C → d_j → S; mark verified vs illustrative | Sections 1–4 |
| 6. Implementation notes | Code-adjacent | Map formulas to exact code branches; state who validates inputs | Sections 1–4 |
| 7. Common pitfalls | Text bullets | Prevent sign mistakes; axis confusion; weight validity | Sections 1–4 |
| 8. Cross-links / next steps | Text | Point to ranking (net-flow) and validation modules | None |

---

## B) Notation contract (must match code)

### Objects and direction
- **a** and **b** are **objects** (a.k.a. alternatives).
- The arrow **a → b** denotes the **directed assertion being assessed**: “a is at least as good as b”.
- Direction matters: values for (a,b) differ from values for (b,a).

### Sets and counts
- **N**: number of objects in the full dataset.
- **C**: number of criteria (count only).
- **B1**: number of row objects in a block (the “a” group).
- **B2**: number of column objects in a block (the “b” group).

Collision rule:
- Use **C(a,b)** (or `C_ab`) for **global concordance values**.
- Do not use plain “C” for concordance; reserve it for the criterion count.

### Difference tensor and triple brackets
- Input differences use the sign convention: `diff = g(a) - g(b)`.
- Shapes:
  - `diff`: **(B1, B2, C)**
  - `c_j`: **(B1, B2, C)**
  - `C(a,b)`: **(B1, B2)**
  - `d_j`: **(B1, B2, C)**
  - `S(a,b)`: **(B1, B2)**
- Triple brackets: `[[[d1,d2,d3]]]` means B1=1 (outer), B2=1 (middle), C=3 (inner).

---

## C) Threshold conventions and exact boundaries (audited)

### Concordance (partial) c_j(a,b) — `electre3/concordance.py`
Given `diff = g(a) - g(b)`:
- `c_j = 1` if `diff >= -q_j`
- `c_j = 0` if `diff <= -p_j`
- else `c_j = (diff + p_j)/(p_j - q_j)` and then clip to [0,1]

**Branch precedence guarantee (q = p case):**
- Code computes `c_interp` with a denominator guard.
- The *outer* `diff >= -q` branch wins first; so when **q=p**, the function is a **step**:
  - `c_j = 1` at `diff = -q` and above
  - `c_j = 0` below `diff = -q`

### Discordance d_j(a,b) — `electre3/discordance.py`
Given the same `diff`:
- `d_j = 1` if `diff <= -v_j`
- `d_j = 0` if `diff >= -p_j`
- else `d_j = (-diff - p_j)/(v_j - p_j)` and then clip to [0,1]

**Branch precedence guarantee (p = v case):**
- When **p=v**, the *outer* `diff <= -v` branch wins; so `d_j = 1` at equality and below.

---

## D) Credibility S(a,b) — `electre3/credibility.py` (ELECTRE III credibility, not distillation)

Inputs:
- `C_ab`: global concordance, shape (B1,B2)
- `d_j`: discordance per criterion, shape (B1,B2,C)

Computation:
- Start `S = C_ab`.
- For each criterion:
  - **Full veto:** if `d >= 1`, then set `S = 0` at those (a,b).
  - **Reduction:** where `(d > C_ab) & (d < 1)`, multiply by `(1-d)/(1-C_ab)`.

**Full-veto exception at C_ab = 1:**
- For valid `d in [0,1]`, the reduction mask `d > C_ab` cannot hold when `C_ab = 1`.
- Therefore the denominator guard (`1e-10`) is not normally used at `C_ab = 1`.
- Full veto still applies and forces `S=0` when `d>=1`.

---

## E) Ranking — net-flow (not ELECTRE III distillation)

Governing implementation: `electre3/ranking.py`.

- The pipeline computes credibility blocks S(a,b) and accumulates **net flow** via `NetFlowAccumulator`.
- **Minimization handling (orientation):** `compute_ranking` copies G and negates each criterion column where `CriterionConfig.maximize` is false.
  - Direct callers of `partial_concordance` / `compute_block` must supply **already oriented** data.
- The returned order uses `np.argsort(-acc.net_flow())` (descending net flow).

---

## F) Diagonal convention (conditional interpretation)

`compute_block(..., is_diagonal=True)` clears self-comparisons with `np.fill_diagonal(S, 0.0)`.

Interpretation constraint:
- “Diagonal means a==b” is valid only when the row-block and col-block index the **same object order**.
- The code does not validate this correspondence; it is a caller responsibility.

---

## G) Weight validity and guarantees

- `global_concordance` is a weighted sum of partial concordances.
- Guarantee `C(a,b) in [0,1]` requires:
  - partial values are finite and in [0,1] (enforced by clip),
  - **weights are nonnegative**, and
  - weights are **normalized** to sum to 1.
- Validation/normalization ownership: `ranking.compute_ranking` calls `normalize_weights(criteria)`; `global_concordance` itself does not.

---

## H) Worked example: verified vs illustrative

- Inputs may be illustrative.
- Outputs must be tagged as either:
  - **verified** (present in `docs/design/committee_phase5/example_results.json`), or
  - **illustrative** (computed by hand; not PI-checked).

Current verified pair example values:
- A→B: C = S = **0.85**
- B→A: C = S = **0.75**
