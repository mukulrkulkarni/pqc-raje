# Data-contract implementation test matrix

**Status:** required evidence plan for a future authorized implementation. No rows marked planned were executed in this assessment.

## Evidence completed during assessment

| Evidence | Command / method | Result | Scope limit |
|---|---|---|---|
| Existing focused regression | `python -m pytest tests/test_data.py tests/test_ranking.py tests/test_serialization.py tests/test_app_workflow.py tests/test_result_cache.py tests/test_cli_run.py tests/test_convert_matrix_csv.py tests/test_shared_contract.py -q` | **99 passed in 1.35s** | Establishes current behavior only; cannot validate unimplemented target changes. |
| Source inspection | Read core, workflow, cache, converter, tests, examples, and docs. | Current headered/download mismatch and `-g` transform identified. | Read-only; no browser/manual UI test. |

## Required tests by category

| ID | Category | Level | Positive case | Negative / edge case | Required assertions | Status |
|---|---|---|---|---|---|---|
| DC-T01 | Unit / data contract | Parser | Headered `(N,C+1)` input with source header and labels. | Empty identifier header; wrong criteria header ordering. | Preserve source header; score matrix is `(N,C)` float64; reject invalid headers. | Planned |
| DC-T02 | Unit / data contract | Parser | Headerless `(N,C+1)` input. | Legacy `(N,C)` row; ragged row; blank identifier. | Display header `Asset ID`; preserve column-0 labels; direct remediation error. | Planned |
| DC-T03 | Unit / validation | Parser | Numeric-looking identifier `0012`. | Non-numeric score, empty score, NaN/Inf/out-of-range score. | Identifier remains string; only score cells cast; error states row and score column. | Planned |
| DC-T04 | Unit / data contract | Model | Identifier tuple travels into `RankingResult`. | Count mismatch, non-string identifier, duplicate identifier if uniqueness adopted. | Immutable tuple and one label per score row. | Planned |
| DC-T05 | Scientific | Ranking | Mixed maximize/minimize fixture. | Scores at `0`, `1`, ties, adjacent float values. | `-g` baseline and `1-g` candidate pairwise differences, credibility, net flow, and ranking satisfy approved comparison rule. | Planned |
| DC-T06 | Scientific | Ranking | Multiple minimize criteria and nonzero `q,p,v`. | Exact tie and threshold-boundary difference. | Threshold meaning stays difference-based; stable tie policy documented. | Planned |
| DC-T07 | Integration | Web workflow | Headered preview → compute → page → download. | Headerless same flow. | Preview, top ten, JSON, CSV all resolve the same ranked source labels. | Planned |
| DC-T08 | End-to-end | CLI/input | Identifier-aware CSV through supported CLI path. | Explicit legacy numeric input. | New contract retains labels; legacy mode labels output as generated. | Planned |
| DC-T09 | Serialization | Canonical serializers | Result JSON/CSV contains Unicode and numeric-looking labels. | Embedded comma/quote/newline label; serializer byte limit. | Canonical JSON; CSV quoting; parse round-trip; labels map to ranked rows. | Planned |
| DC-T10 | Cache/download | Integration | Cache stores and returns identifier-bearing JSON exactly. | Expired token, foreign session, corrupted manifest, payload size limit. | Exact bytes/checksum; no cross-session disclosure; correct attachment headers. | Planned |
| DC-T11 | Security | Ingestion/export | Identifier such as `=2+2`, `<img...>`, Unicode, leading/trailing spaces. | NUL/control character and extremely long identifier. | No HTML execution; no path/token/header injection; chosen CSV-injection policy enforced. | Planned |
| DC-T12 | UI | Server-rendered pages | Labels with HTML metacharacters appear as text. | Empty/ambiguous labels; ranking with repeated-looking labels. | Escaping, semantic label header, user-visible mapping clarity. Browser keyboard/AT/reflow evidence remains separate. | Planned |
| DC-T13 | Performance | Parser and compute | 100,000 rows with valid short identifiers under configured block sizes. | Identifier length at stated limit; 100 MiB input boundary. | Bounded memory/runtime; feasibility gate still precedes compute; no accidental object matrix. | Planned |
| DC-T14 | Compatibility | Converter | New explicit preservation route. | Existing `--id-col` legacy drop route. | Never silently discard primary ID; migration message/docs match behavior. | Planned |
| DC-T15 | Reproducibility | Cross-block | Same identifier-bearing input at block sizes `1`, `1000`, `10000`. | Mixed minimize criteria. | Required numeric/ranking and canonical artifact byte-identity policy is met or discrepancy is explained. | Planned |
| DC-T16 | Negative end-to-end | All routes | Valid result then download. | Missing workflow, unpreviewed compute, malformed UTF-8, oversized upload. | Existing status-code and non-publication protections persist. | Planned |

## Acceptance gates

1. All planned tests pass, including explicit negative and edge cases.
2. A new test proves the current page/download identifier divergence cannot recur.
3. A scientific test proves the transform claim under defined IEEE-754 comparison rules.
4. Full suite passes without disabled, weakened, or quarantined existing tests.
5. Cache/checksum, serializer determinism, and download authorization evidence remains intact.
6. Documentation and examples describe headered/headerless mappings and NumPy policy accurately.

## Test data fixtures

```csv
Asset Ref,Quality,Cost
A-001,0.90,0.20
0012,0.50,0.80
=2+2,0.70,0.40
```

```csv
A-001,0.90,0.20
0012,0.50,0.80
=2+2,0.70,0.40
```

Use the first as headered and second as headerless. The formula-looking value tests export handling; it must never be opened automatically in a spreadsheet as evidence of safety.

## Evidence handling

Future tests must record exact commands, runtime, environment revision, passed/failed counts, and actual serializer bytes/checksums where relevant. A passing current regression is not substituted for a target-contract test. UI claims require browser evidence and should retain the existing documented D3 limitations.
