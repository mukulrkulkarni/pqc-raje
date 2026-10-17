# Scientific review — Discordance scoped gates (ELECTRE III)

## Decision
**NEEDS WORK** — core discordance/credibility math is consistent with ELECTRE III (veto-first, p=v handled), but the Phase-5 tutorial/spec evidence does not yet prove the required guarantees (net-flow integration, veto cases, reverse/sensitivity table) and the snapshot evidence is incomplete in this workspace.

## Evidence read (pinned + live)
- Pinned manifest: `docs/design/committee_phase5/discordance_review/manifest.json`
- Pinned snapshot (via paths in manifest):
  - `docs/design/committee_phase5/discordance_review/snapshot/docs/modules/discordance_tutorial_side_by_side.html`
  - `docs/design/committee_phase5/discordance_review/snapshot/tests/test_module_docs.py`
  - `docs/design/committee_phase5/discordance_review/snapshot/tests/test_discordance_deep.py`
- Live implementation:
  - `electre3/discordance.py`, `electre3/credibility.py`, `electre3/concordance.py`, `electre3/ranking.py`

## Verified implementation properties (with excerpts)
### 1) Sign convention and meaning of (a,b)
- Code consistently defines `diff = g(a) - g(b)`.
  - `electre3/discordance.py`: “`diff: Performance differences g(a) - g(b)`”
  - `electre3/concordance.py`: same wording.
- Interpretation: rows are the left alternative group **a** (B1), columns are the right group **b** (B2). The 3rd axis is criteria (C). This should be stated explicitly in the tutorial: **a and b are objects (alternatives)**; row/column are comparison groups.

### 2) Discordance gate is veto-first and supports p=v
- Implementation:
  - `denom = v - p; denom = np.where(denom == 0, 1.0, denom)` (avoids divide-by-zero)
  - `d = np.where(diff <= -v, 1.0, np.where(diff >= -p, 0.0, d_interp))`
  - `return np.clip(d, 0.0, 1.0)`
- Guarantees (verified from code logic):
  - **Veto-first boundary:** at `diff <= -v` discordance is exactly 1, even if `p=v`.
  - **No-discordance boundary:** at `diff >= -p` discordance is exactly 0.
  - **p=v special case:** if `p_j == v_j`, then for values not captured by the two inequalities, `d_interp` uses denom=1, and final `clip` keeps values in [0,1]. This is numerically safe but creates a “jump” behavior; the tutorial must describe this explicitly as a degenerate threshold case.

### 3) Credibility uses discordance reduction (not 1-concordance)
- Implementation follows the ELECTRE III multiplicative reduction:
  - `S = C_ab.copy()`
  - Full veto: `S[d >= 1.0] = 0.0`
  - Partial veto: for `d > C_ab` and `d < 1`, multiply by `(1-d)/(1-C)`.
- This is **not** “`1 - C(a,b)`”; it is criterion-wise reduction applied only when discordance exceeds global concordance.

### 4) Partial vs full veto behavior is present
- Full veto: `d == 1` forces `S=0` regardless of C.
- Partial veto: if `C < d < 1`, then factor in (0,1) reduces S.

## Gaps vs requested scope (batched)
### A) Pinned evidence completeness (BLOCKING FOR APPROVAL)
- The directory listing shows `docs/design/committee_phase5/discordance_review/snapshot/` empty, but the manifest references files under it. This indicates the pinned snapshot is not present as normal files in this workspace view, so I cannot verify hashes or exact HTML/test contents from the on-disk snapshot directory.
  - Evidence: `filesystem__list_directory` shows only `manifest.json`, `REQUEST.md`, `snapshot/` and `filesystem__read_directory` reports 0 files.

### B) Tutorial/spec requirements not proven by code excerpts shown
The request requires tutorial/scientific content to include:
- “credibility plus net-flow ranking” linkage (not distillation).
- Graduate-level explanation of **p=v** equality, **veto-first**, **partial/full veto**, and that a/b are alternatives.
- A numerical sensitivity table and a reverse-case example.

From the live Python, these behaviors exist, but I cannot confirm the pinned tutorial HTML and pinned tests actually demonstrate them because I did not reliably access the snapshot contents as files (see gap A). If the tutorial exists in `docs/modules/discordance_tutorial_side_by_side.html`, it should be audited explicitly in a follow-up once the pinned snapshot is available.

### C) Shape/finite contracts and validation ownership
- `ranking.compute_ranking` validates thresholds and arrays (`validate_thresholds`, `validate_arrays_match`, `validate_matrix`).
- `discordance()` and `credibility()` themselves do not validate shapes or finiteness.
- The tutorial should clearly assign ownership:
  - “These functions assume diff has shape (B1,B2,C), thresholds have shape (C,), and values are finite; validation happens in pipeline.”

## Static review limitations
- No tests were executed in this review.
- No browser rendering verification was performed.
- Snapshot hash verification cannot be completed because the snapshot directory was not readable as populated files in this workspace view.

## Introduced vs pre-existing findings
- Likely introduced in Phase 5: tutorial/spec completeness issues (needs explicit p=v / veto-first / net-flow linkage).
- Pre-existing design choice: validation happens in ranking/pipeline, not inside low-level math functions.
