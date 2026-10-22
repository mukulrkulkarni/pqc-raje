# Data-contract impact assessment: identifier-bearing CSV and minimization transform

**Assessment status:** completed analysis only; no production code, templates, pages, examples, or tests were changed.

**Decision authority:** user-approved contract recorded in the task: CSV has shape `(N, C+1)`; column `0` is a string identifier; columns `1..C` are normalized numeric criteria; computation excludes column `0`; result artifacts preserve identifiers. For headerless CSV, the identifier heading is `Asset ID`. For headered CSV, preserve the supplied non-empty identifier heading. `maximize=false` uses `1-g` for normalized scores.

## Scope and method

This is a read-only impact assessment. Sources were inspected at workspace revision `b7fa080` (`reconcile-d3-final-gate-records`); the existing user worktree also contained the planned, untracked assessment checkpoint. The bounded existing-test command below passed before these assessment artifacts were written:

```text
python -m pytest tests/test_data.py tests/test_ranking.py tests/test_serialization.py tests/test_app_workflow.py tests/test_result_cache.py tests/test_cli_run.py tests/test_convert_matrix_csv.py tests/test_shared_contract.py -q
99 passed in 1.35s
```

Passing tests establish current behavior only. They do not establish the proposed contract.

## Current behavior verified from source

| Surface | Verified behavior | Contract impact |
|---|---|---|
| `electre3/shared.py:validate_score_matrix` | Accepts only numeric `(N,C)` input and converts the complete input with `np.asarray(..., float64)`. | Cannot receive the new mixed identifier-plus-score CSV representation directly. It should continue to validate the extracted score matrix only. |
| `electre3/shared.py:compute_validated_ranking` | Assigns identifiers `"0"..."N-1"` unconditionally. | Must accept separately parsed identifiers or a typed input model; otherwise serialized artifacts lose source identifiers. |
| `electre3/data.py:load_matrix` | Loads CSV with `np.loadtxt(..., float64)`. | Rejects headers and string identifiers. The generic numeric loader needs a compatibility boundary or a new identifier-aware CSV reader. |
| `electre3/ranking.py:compute_ranking` | Copies score matrix, then changes minimize columns with `G_adj[:, j] = -G_adj[:, j]`. | Replace with the approved normalized transform after score-range validation. |
| `electre3/config.py:CriterionConfig` | Holds `maximize`; thresholds and weight checks are independent of identifier handling. | No schema field change required. Document that thresholds remain normalized-score difference units. |
| `electre3/serialization.py:RankingResult` | Validates one string identifier per row; JSON and CSV serializers emit them deterministically. | The result model already supports propagation. Producer call sites must supply source identifiers. |
| `app/routes/workflow.py:_parse_csv` | Headered input parses `(N,C+1)`, retains row labels in workflow state, and validates headers. Headerless input currently expects only `C` cells and fabricates row-number identifiers. | Headerless parsing must instead require identifier plus `C` scores. Both modes must pass stored identifiers into the shared compute result. |
| `app/routes/workflow.py:compute` | Uses state identifiers to render the top-ten page, but serializes `compute_validated_ranking` output with generated numeric identifiers. | UI and download currently diverge. Result download must preserve the source identifiers. |
| `app/services/result_cache.py` / download route | Caches exact serializer bytes, checksum validates parts, binds token to session, and returns an attachment. | No cache format change is necessary if canonical result serialization changes only through correct identifiers. Cache invalidation/versioning is required for mixed old/new artifacts. |
| `scripts/convert_matrix_csv.py` | Can drop a chosen ID column but returns only the numeric matrix and writes numeric-only output. | Its current purpose conflicts with identifier preservation. It needs an explicit compatibility mode or a new result-preserving conversion artifact. |
| `electre3/cli.py`, `electre3/cli_run.py` | CLI loads numeric arrays, prints `Alt <index>`, and returns ranking indices. | CLI requires an identifier-aware input path and a compatibility mode for legacy numeric-only arrays. |
| examples and docs | `matrix_with_headers.csv` has `Asset,E,X,O`; numeric example has `(N,C)` values. | Replace or supplement numeric-only examples; all ingestion instructions must explain identifier-column and header mapping. |

## Required target contract

### CSV ingestion

| Mode | Required first row / column | Required shape | Identifier mapping |
|---|---|---|---|
| Headered | Row 0 has `identifier_header, criterion_1, ..., criterion_C`. | Each data row has exactly `C+1` cells. | Preserve `identifier_header` exactly after non-empty validation. Preserve each column-0 text identifier exactly; do not parse as a float. |
| Headerless | No header row. | Each row has exactly `C+1` cells. | Treat column 0 as its string identifier. Present its display/header label as `Asset ID`. |

Recommended validation: require every identifier to be a string after UTF-8 CSV decoding, non-empty after `strip()`, unique within the input, and bounded by a documented length. Preserve the original identifier string rather than stripping it, but reject values that become empty after stripping. Uniqueness is a **recommendation**, not verified existing behavior; it prevents ambiguous rankings and downloads. Numeric cells must remain finite float64 values in `[0,1]`. The computation matrix is `scores = rows[:, 1:]` conceptually, not a cast of the full CSV row.

CSV formula: `raw shape = (N, C+1)`, `identifiers[i] = raw[i][0]`, `G[i,j] = float(raw[i][j+1])`. The core ranking receives only `G.shape == (N,C)`.

### NumPy input policy

**Recommendation:** `.npy` and `.npz` remain numeric-only `float64` score matrices of shape `(N,C)` because NumPy homogeneous arrays cannot safely preserve arbitrary string identifiers beside numeric values without an object/string dtype. Require identifiers through one of these explicit, versioned mechanisms:

1. default generated identifiers (`"0"..."N-1"`) for existing CLI/API compatibility; or
2. a companion UTF-8 identifier file with exactly `N` validated entries; or
3. a new named structured input artifact that carries `identifiers` and `scores` separately.

Reject object-dtype and pickle-requiring NumPy inputs. Preserve `allow_pickle=False` in web parsing, and extend it to generic `data.py` loader paths. Do not infer identifiers from array values, paths, or a structured dtype silently. This is a migration recommendation, not existing verified behavior.

## Identifier propagation path

The implementation must preserve one immutable `tuple[str, ...]` from parser to `RankingResult`, indexed by source row. Ranking continues to be an index permutation. Consumers resolve a ranked item as `identifiers[int(ranking[position])]`; they must not assume rank position or array index is the identifier.

Affected artifact fields:

- `RankingResult.identifiers` already represents the required field.
- `serialize_ranking_json`, `serialize_scores_json`, and `serialize_result_json` already include `identifiers`.
- `serialize_result_csv` already writes `identifier` in row order induced by `ranking`.
- `/app` rendered top-ten labels use workflow-state labels today; switch to the result labels or assert they agree before rendering.
- Cache manifests checksum serializer bytes only. They do not need to hold identifiers separately.
- Download payload must use a result constructed with the source identifiers.

Security requirements: continue CSV decoding as UTF-8; escape identifiers only through Flask/Jinja autoescape and `csv.writer`; never place an identifier in a filesystem path, cache key, response header, or route token. Reject NUL/control characters if any downstream display/export policy cannot encode them safely. Test a spreadsheet-formula-looking identifier (for example `=HYPERLINK(...)`) in CSV output and document an export-cell protection policy before claiming spreadsheet safety.

## Minimize transformation: proof and numerical boundary

Let normalized scores satisfy `g_i,g_k in [0,1]`. Current code derives values `a_i=-g_i`. The approved transform derives `b_i=1-g_i`. For every pair:

```text
b_i - b_k = (1-g_i) - (1-g_k) = g_k-g_i = (-g_i)-(-g_k) = a_i-a_k.
```

Thus each pairwise difference supplied to concordance, discordance, credibility, and net-flow accumulation is equal in real arithmetic. Because all criterion-level pairwise values are equal, each credibility matrix entry and every net flow are equal; therefore `argsort(-net_flow)` returns the same ranking, including ties, provided its tie behavior is unchanged. The transformation also keeps adjusted values in `[0,1]`, which makes the approved normalized-score domain explicit. Thresholds `q`, `p`, and `v` remain differences and need no offset.

**Precision limitation:** IEEE-754 evaluation of two subtraction expressions can differ by a rounding unit in pathological cases. The implementation evidence must compare pairwise differences and complete outputs using exact equality where demonstrated, then strict tolerance and deterministic ranking equality across boundary values (`0`, `1`, adjacent representable values) if exact equality is not universal. No current test proves this proposed equivalence.

## Compatibility and migration strategy

1. Introduce an explicit identifier-aware parsed-input model before modifying callers. Keep the core numeric score validator and core ranking signature numeric.
2. Make CSV `(N,C+1)` mandatory in the web workflow for both header modes. Reject legacy headerless `(N,C)` CSV with a direct remediation message; do not fabricate identifiers there.
3. Preserve a clearly named legacy numeric-only loader/CLI path for `.npy`, `.npz`, and numeric-only CSV only if compatibility is a release requirement. It must generate documented positional identifiers and never claim source identifiers were retained.
4. Version input/output metadata if result semantics or required input mapping changes. Serializer version currently equals `"1"`; changing the value requires byte-identity, cache, manifest, and client compatibility tests. New artifacts must not be served under old semantic assumptions.
5. Invalidate process-memory entries on deployment. Existing process-memory cache already disappears on restart; add integration evidence for the altered payload and its checksum.
6. Update converter behavior deliberately. The existing `--id-col` drop mode should remain explicitly legacy or gain a companion identifiers output. Do not silently discard the primary identifier column under the new contract.

## Revised implementation chunks (not executed)

| Chunk | Boundary and acceptance | Dependencies / stop condition |
|---|---|---|
| DC-1 | Define parsed-input and identifier validation; adapt shared result creation without changing ranking math. Tests prove `N` labels preserve order and invalid labels reject. | Stop on unresolved identifier uniqueness or NumPy sidecar format. |
| DC-2 | Update CSV web parser, preview, compute, and result construction for headered/headerless `(N,C+1)`. Tests prove rendered and downloaded labels agree. | Stop on any label loss or cache payload mismatch. |
| DC-3 | Replace minimize `-g` with `1-g`; add scientific invariance test fixture and boundary values. | Stop if numerical output/ranking evidence differs outside declared tolerance. |
| DC-4 | Update CLI/data/converter compatibility boundary, examples, and documentation. Tests prove legacy numeric flow is explicit and new CSV retains IDs. | Stop if migration changes numeric-only behavior without a documented switch. |
| DC-5 | Run focused then full regression, byte-stability checks across block sizes, security/export checks, and performance measurements. | Stop on failing baseline, artifact size limit, timeout, or undocumented serializer change. |

## Verified findings versus recommendations

Verified findings are source observations and the 99-passing bounded regression listed above. The target contract, uniqueness rule, NumPy companion strategy, control-character policy, serializer version decision, and all chunks are recommendations for separately authorized implementation. This assessment neither changes code nor establishes production readiness.
