# D4 Phase 2 Tutorial Draft — Three Controlled Preference Scenarios

**Status:** Draft only. No user-facing page edits. Scientific and Engineering re-review required.
**Base revision:** `4e47749` for current D3 documentation pages and source behavior.

## Contract and notation

The method computes **ELECTRE III credibility with raw net-flow ranking**, not ELECTRE III distillation. The performance matrix has shape `(N,C)` after identifier extraction. CSV input has shape `(N,C+1)`: identifier in column 0 and normalized criterion scores in columns 1..C.

Each criterion has `name`, positive `weight`, `q`, `p`, `v`, and Boolean `maximize`, with `0 ≤ q ≤ p ≤ v`; weights sum to `1`. The shared validator supports at most eight criteria. `a` and `b` are alternative objects. In a block, rows contain `a` alternatives and columns contain comparison-group `b` alternatives.

Raw net flow is:

`Φ(a) = Σ_b S(a,b) − Σ_b S(b,a)`.

Higher raw net flow ranks first. Raw scores are not probabilities. Equal raw flows are ties; near-ties are not ties, and tied order has no documented stable policy.

## Controlled comparison design

All three scenarios use the same four criteria, score matrix scale, thresholds, maximize directions, and asset order where comparison is claimed. Only the weight priorities change between controlled runs. Each scenario has a separate dataset size to demonstrate workflow scale; do not compare ranks across different datasets as causal evidence.

Required criteria names:

- Quantum-Vulnerability
- Migration-Complexity
- Business-Criticality
- Data-Sensitivity

The four-criterion fixtures, criteria JSON files, hashes, and generated outputs must be created and independently executed before publication. This draft does not invent rankings.

## Scenario 1 — Three assets, balanced priority

**Purpose:** Complete the smallest workflow.

- Assets: `A-001 / 10.0.0.5`, `A-002 / 10.0.0.9`, `A-003 / 10.0.0.12`.
- Weights: `0.25` for each criterion.
- Thresholds and directions: fixed in the scenario criteria JSON.
- Files: `fixtures/d4/scenario-3/criteria.json`, `matrix_headered.csv`, `matrix_headerless.csv`.

Run both header modes after fixture creation. Verify identifiers remain attached to ranked rows.

## Scenario 2 — Five assets, Business-Criticality priority

**Purpose:** Show a changed preference policy.

- Five assets.
- Use the same five-row score matrix, thresholds, directions, and criterion order for both balanced and priority runs.
- Priority weights assign the largest weight to `Business-Criticality`; exact values must be recorded in the criteria JSON.
- Compare the two outputs only after recording both criteria-file hashes.

A changed ranking demonstrates a changed preference policy, not a changed algorithm.

## Scenario 3 — Eight assets, Data-Sensitivity priority

**Purpose:** Demonstrate a larger scenario and a different priority axis.

- Eight assets.
- Use a fixed eight-row matrix and the same thresholds/directions for balanced and priority runs.
- Priority weights assign the largest weight to `Data-Sensitivity`; exact values must be recorded in the criteria JSON.
- Add a deterministic tie fixture separately. Do not claim a tie unless the executed raw flows are exactly equal.

## CLI execution

Run from the repository root in Windows Command Prompt:

```cmd
set PYTHONPATH=.
python scripts/convert_matrix_csv.py fixtures/d4/scenario-3/matrix_headered.csv out/d4-s3.npy --has-header --id-col "Asset ID / IP"
python -m electre3.cli out/d4-s3.npy fixtures/d4/scenario-3/criteria.json -y
```

For direct identifier-bearing CSV, use the supported `load_input` path where documented. For converted NumPy, positional identifiers are used. Record exact output, exit code, revision, file hashes, and limitation.

## Web execution

Run the local launcher:

```cmd
python scripts/dev_local.py
```

Open `http://127.0.0.1:5000/app/`. Enter criteria, provide the matrix, review the preview, approve any missing score replacement, confirm, and compute. The app uses server-rendered HTML without JavaScript. Browser rendering, zoom, reflow, keyboard, offline, screen-reader, and load evidence remain deferred and non-blocking.

## Recovery example

Use a wrong header order, blank identifier, duplicate identifier, or score outside `[0,1]`. Preview must reject the input with an actionable message. For a missing CSV score only, use the approval checkbox and a replacement in `[0,1]`; missing criteria JSON values remain rejected.

## Evidence before publication

Record exact commands, exit codes, actual output, file hashes, source paths, environment, revision, and limitations. Required evidence:

- positive: all three scenarios through CLI and `/app`;
- negative: malformed headers, identifiers, scores, criteria, and missing routes;
- edge: 2/8 criteria, 100 MiB/100,000-row limits, block sizes, thresholds, ties, Unicode and formula-looking identifiers;
- scientific: raw flows, direction handling, exact ties versus near-ties;
- integration: rendered and downloaded identifiers match;
- serialization/cache/security: v2 bytes, checksums, expiry, token/session rules;
- links: local paths, fragments, and planned Phase 3/4 targets.

This draft is not publication evidence until the fixture creation and independent verbatim runs pass.

## Related phases

- Phase 1: `README.md`, `docs/GETTING_STARTED.html`, `docs/tutorials/cli_quickstart.md`.
- Phase 3: planned mental model, blockwise computation, thresholds, net flow, and gotchas.
- Phase 4: planned CLI/module reference, limits, debugging, and migration notes.
