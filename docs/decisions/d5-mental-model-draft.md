# D5 Mental Model Draft — ELECTRE III Credibility and Raw Net Flow

**Status:** Draft only. No user-facing page edit. Scientific and Engineering review required.

## 1. The model

The performance matrix `G` has shape `(N,C)`: `N` alternatives and `C` criteria. Each criterion has a name, positive weight, thresholds `q ≤ p ≤ v`, and a Boolean `maximize` direction. The shared web/CLI contract validates normalized scores in `[0,1]`, supports one to eight criteria, and requires weights to sum to `1`. The low-level `electre3/ranking.py` API renormalizes positive weights and has a broader historical matrix contract; do not confuse that low-level behavior with the shared entry contract.

This project implements **ELECTRE III credibility followed by descending raw-net-flow ranking**. It does not implement ELECTRE III distillation.

`a` and `b` are alternative objects. In a block, rows contain `a` alternatives and columns contain comparison-group `b` alternatives. A pair asks whether `a` outranks `b`.

## 2. Blockwise computation

The core receives numeric `G(N,C)`. It compares row and column groups without storing a full `N×N` matrix.

- `(B1,B2,C)`: criterion-level pairwise intermediates.
- `(B1,B2)`: one credibility value for each pair after reducing criteria.
- The accumulator stores outgoing and incoming flow vectors of length `N`.

```text
G(N,C)
   │ split rows and columns
   ▼
(B1,B2,C) ── concordance/discordance ──► (B1,B2) credibility
   │                                             │
   └──────────── O(N) flow accumulator ◄────────┘
                         │
                         ▼
                 raw net-flow ranking
```

## 3. Credibility mental model

For criterion `j`, use direction-adjusted differences. The current implementation computes maximize differences as `g(a)-g(b)` and minimize differences directly as `g(b)-g(a)` after `[0,1]` validation. This is numerically equivalent to comparing `1-g`, without storing rounded transformed values.

Partial concordance uses the inclusive boundaries:

- `c=1` when `diff ≥ -q`;
- `c=0` when `diff ≤ -p`;
- linear interpolation between those limits otherwise.

If `q=p`, the full-concordance branch takes priority at the overlap.

Discordance uses:

- `d=0` when `diff ≥ -p`;
- `d=1` when `diff ≤ -v`;
- linear interpolation between those limits otherwise.

If `p=v`, the full-veto branch takes priority at the overlap.

Global concordance is the weighted sum of partial concordances after weight normalization. Credibility starts at concordance. For each `d > C`, the implementation applies `(1-d)/(1-C)`. If `d ≥ 1`, credibility is zero. If `C=1` without a full veto, credibility remains one.

Source evidence: `electre3/concordance.py`, `electre3/discordance.py`, `electre3/credibility.py`, `electre3/block.py`, and `electre3/ranking.py` at D4 commit `2c38c7c`. For the formal method, cite the project-approved ELECTRE III reference before publication; repository files establish implementation behavior, not independent scientific authority. Raw net flow is the project’s ranking layer after credibility, not ELECTRE III distillation.

## 4. Raw net flow and ties

For alternative object `a`:

`Φ(a) = Σ_b S(a,b) − Σ_b S(b,a)`.

Higher raw net flow ranks first. Raw scores are not probabilities and are not normalized after accumulation. Equal full-precision raw flows are ties. Near-ties with a nonzero full-precision difference are not ties. The implementation uses `np.argsort(-net_flow)` and documents no stable order within ties.

## 5. Daily operations

1. Validate criteria and matrix shape.
2. Check direction and threshold units.
3. Inspect `(B1,B2,C)` and `(B1,B2)` shapes when debugging.
4. Compare raw net flows, not normalized display scores.
5. Map ranking indices through `RankingResult.identifiers`.

## 6. Gotchas

- Rows and columns are ordered comparison groups; do not transpose `S(a,b)`.
- Veto is per criterion and can defeat strong concordance.
- `q=p` and `p=v` require branch-priority checks.
- Numeric NumPy inputs use positional identifiers.
- CSV identifier values are separate from numeric computation columns.
- Exact ties do not imply a stable order.
- Browser rendering, zoom, keyboard, offline, AT, and load evidence are deferred and non-blocking.

## Evidence, links, and publication gate

Current source links:

- [README](../../README.md)
- [CLI quickstart](../tutorials/cli_quickstart.md)
- [Debugging runbook](../runbook/debugging.md)
- [D4 fixture evidence](../../examples/d4_phase2/scenario-3/criteria_balanced.json)
- [Raw net-flow implementation](../../electre3/ranking.py)
- [D4 evidence tests](../../tests/d4_checks/test_evidence.py)

D4 fixtures provide controlled balanced/priority, exact-tie, and near-tie evidence. Before publication, run exact commands that reproduce a positive example, malformed-input rejection, threshold edge, exact tie, and near-tie. Record outputs, hashes, revision, and limitations. Add local target/fragment link regression coverage.

When transferred to HTML, use semantic `<var>`, `<sub>`, `<sup>`, and text operators. The explanation must remain readable without JavaScript and must not require KaTeX. A math-renderer failure must leave the source notation and meaning available.

Any D5 Python addition must pass the strict 50-executable-line audit. Browser rendering, keyboard, zoom, offline, screen-reader, and load evidence remain deferred and non-blocking.

Planned targets:

- Phase 4 reference and debugging pages: planned, not yet created.
- Companion website mental-model page: planned, not yet created.
