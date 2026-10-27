# D4 Phase 2 tutorial draft — controlled migration-priority fixtures

**Status:** D4 review-recovery draft. Fixture evidence is regenerated locally; Scientific and Engineering approval remains required before commit. No user-facing page changed.
**Pinned behavior revision:** `7beb15e` (D4 draft baseline); this recovery correction is uncommitted.
**Evidence revision:** generated locally by `out/generate_d4_fixture_evidence.py` on Python 3.11; `tests/d4_checks/test_raw_flow.py` independently recomputes tie flows from raw CSV and criteria inputs.
**Current vs planned:** The paths below exist now. D5 mental-model and D6 reference targets are planned; no target page exists. Browser evidence remains deferred and non-blocking.

## Fixture contract

The executable fixtures are under `examples/d4_phase2/`:

- `scenario-3/matrix_headered.csv` and `criteria_balanced.json` — 3 assets, balanced weights.
- `scenario-5/matrix_headered.csv`, `criteria_balanced.json`, and `criteria_business-criticality-priority.json` — controlled 5-asset comparison.
- `scenario-8/matrix_headered.csv`, `criteria_balanced.json`, and `criteria_data-sensitivity-priority.json` — controlled 8-asset comparison.
- `exact-tie/` and `near-tie/` — deterministic three-asset comparison fixtures.
- `out/d4-fixture-evidence.json` — generated hashes, CLI output, credibility matrices, and binary64 hexadecimal flows.

Every fixture has these criteria, in this order: `Quantum-Vulnerability`, `Migration-Complexity`, `Business-Criticality`, `Data-Sensitivity`.

```json
[
  {"name":"Quantum-Vulnerability","weight":0.25,"q":0.03,"p":0.12,"v":0.35,"maximize":true},
  {"name":"Migration-Complexity","weight":0.25,"q":0.03,"p":0.12,"v":0.35,"maximize":true},
  {"name":"Business-Criticality","weight":0.25,"q":0.03,"p":0.12,"v":0.35,"maximize":true},
  {"name":"Data-Sensitivity","weight":0.25,"q":0.03,"p":0.12,"v":0.35,"maximize":true}
]
```

Scores are normalized to `[0,1]`. Higher scores mean greater migration priority: quantum exposure, difficulty/complexity, business impact, and data exposure. Thus every criterion sets `maximize: true`. All fixtures use `q=0.03`, `p=0.12`, `v=0.35` and the identifier-first header `Asset ID / IP`, followed by the ordered criterion names. The 5- and 8-asset comparisons hold the **identical matrix, threshold values, directions, criterion order, and asset order** fixed; only weights change. Their priority files use `[0.15,0.15,0.55,0.15]` and `[0.15,0.15,0.15,0.55]` respectively.

SHA-256 values are in `out/d4-fixture-evidence.json`; regenerate them rather than transcribing stale values:

```cmd
python out\generate_d4_fixture_evidence.py
python -m pytest -q tests\test_d4_fixture_correction.py
```

## Method semantics

The implementation computes ELECTRE III credibility, then ranks by descending raw net flow. It does not implement ELECTRE III distillation. An alternative object is one asset record: `a` is the row alternative under evaluation and `b` is a comparison-group alternative in the columns. For each credibility block `S[a,b]`, rows enumerate the `a` comparison group and columns enumerate the `b` comparison group; `S[a,b]` states support for `a` outranking `b`. The diagonal `S[a,a]` is zeroed and does not express a self-comparison. For an assertion that `a` outranks `b`, direction-adjusted `diff_j(a,b)` is `g_j(a)-g_j(b)` for maximize; minimize uses its equivalent `g_j(b)-g_j(a)` calculation.

| Block notation | Meaning |
| --- | --- |
| row `a` | evaluated alternative object |
| column `b` | comparison-group alternative object |
| cell `S[a,b]` | credibility that row `a` outranks column `b` |
| diagonal `S[a,a]` | forced to zero; excluded self-comparison |

Partial concordance is `c_j=1` when `diff >= -q`, `c_j=0` when `diff <= -p`, else `(diff+p)/(p-q)`. When `q=p`, the ordered conditions take precedence: `diff >= -q` returns `1`, then `diff <= -p` returns `0`; interpolation is never selected. Global concordance is `C=sum(w_j*c_j)`.

Discordance is `d_j=1` when `diff <= -v`, `d_j=0` when `diff >= -p`, else `(-diff-p)/(v-p)`. With `p=v`, veto precedence applies first: `diff <= -v` returns `1`, then `diff >= -p` returns `0`; interpolation is never selected.

Credibility starts as `S=C`. For each criterion where `d_j>C` and `d_j<1`, it multiplies by `(1-d_j)/(1-C)`. Where `d_j<=C`, that criterion leaves credibility unchanged. Any `d_j>=1` sets `S=0`, including `C=1`; `C=1` with every finite `d_j<1` remains `1`. Diagonal credibility is zeroed. Raw flow is `Phi(a)=sum_b S(a,b)-sum_b S(b,a)`; higher ranks first.

`exact-tie` gives identical full-precision flows for T-001 and T-002: `0x1.4aac3cd964020p-2`. `near-tie` gives distinct flows for N-001 and N-002: `0x1.4aac3cd964020p-2` and `0x1.4aac3cd964028p-2`. Hexadecimal binary64 strings, all credibility entries, outflow, inflow, hashes, stdout, and commands appear in `out/d4-fixture-evidence.json`. A displayed order for equal flows is not a tie-breaking policy.

## Direct and converter CLI paths

Run from repository root. This direct CSV path retains source identifiers:

```cmd
python -m electre3.cli examples\d4_phase2\scenario-3\matrix_headered.csv examples\d4_phase2\scenario-3\criteria_balanced.json -y -b 2
```

The converter path deliberately removes identifiers; NumPy input prints positional identifiers:

```cmd
python scripts\convert_matrix_csv.py examples\d4_phase2\scenario-3\matrix_headered.csv out\d4-s3.npy --has-header --id-col "Asset ID / IP"
python -m electre3.cli out\d4-s3.npy examples\d4_phase2\scenario-3\criteria_balanced.json -y -b 2
```

Actual direct-CSV stdout for every fixture is stored in `out/d4-fixture-evidence.json`. The CLI validates 1–8 criteria, 2–100,000 rows, normalized finite scores, ordered headers, and safe unique identifiers. `/app` additionally has a 100 MiB request upload cap. Its feasibility gate is deployment-profile dependent and can reject a computation before ranking; do not describe this as a CLI cap.

## `/app` path and recovery

**Current:** start `python scripts\dev_local.py`, then open `http://127.0.0.1:5000/app/`. Enter criteria, upload or enter the matrix, review, approve permitted missing-score replacement, confirm, and compute. The path is server-rendered HTML.

**Current recovery checks:** wrong criterion order, blank or duplicate identifier, or a score outside `[0,1]` must fail validation. A missing CSV score needs the explicit preview approval and a `[0,1]` replacement. Criteria JSON omissions remain invalid.

**Deferred:** browser rendering, zoom, reflow, keyboard, assistive technology, offline, and load evidence. These are non-blocking for this correction.

## Links and planned targets

**Current:** [repository README](../../README.md), [Getting Started](../GETTING_STARTED.html), [CLI quickstart](../tutorials/cli_quickstart.md), and [debugging runbook](../runbook/debugging.md).

**Planned D5:** mental model, blockwise computation, thresholds, net flow, and gotchas. **Planned D6:** CLI/module reference, limits, debugging, and migration notes. These are labels, not links, because targets do not exist.
