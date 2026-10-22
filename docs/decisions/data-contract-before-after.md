# Data-contract before/after specification

**Status:** approved target contract documented for future implementation; current code remains unchanged.

## Contract comparison

| Topic | Current verified behavior | Approved target behavior | Compatibility decision |
|---|---|---|---|
| CSV headered shape | Web parser accepts identifier plus scores: `(N,C+1)`. | `(N,C+1)` remains required. | Preserve. |
| CSV headerless shape | Web parser accepts only scores: `(N,C)` and creates positional labels. | Require identifier plus scores: `(N,C+1)`. | Breaking web-input change; reject old shape clearly. |
| CSV headered identifier heading | Validates non-empty column 0 and retains it for preview. | Preserve the supplied identifier header. | Preserve. |
| CSV headerless identifier heading | Uses `Asset ID` display header but has no source ID column. | Use `Asset ID`; column 0 supplies source labels. | Preserve heading; change mapping. |
| Core score matrix | `validate_score_matrix` requires numeric `(N,C)`. | Core continues to receive extracted numeric `(N,C)`. | Preserve interface boundary. |
| Result identifiers | Shared result creates positional strings. Web page uses state labels separately. | Construct results with parsed source labels; every artifact carries them. | Correct semantic mismatch. |
| Ranking representation | Ranking is row-index permutation. | Same. Resolve labels by row index. | Preserve. |
| Minimize transform | `-g`. | `1-g` for validated `g∈[0,1]`. | Scientifically invariant pairwise differences. |
| NumPy `.npy/.npz` | Numeric matrices; web uses `allow_pickle=False`. | Numeric-only scores plus explicit identifier mechanism or documented generated IDs. | No silent mixed/object arrays. |
| Generic CSV loader/converter | Numeric-only parser; converter can drop IDs. | Identifier-aware reader or explicit legacy conversion mode. | Never silently discard primary IDs. |

## Before: current mappings

```text
Headered web CSV
Asset ID,Quality,Cost
A,0.9,0.2
B,0.5,0.8

workflow parser -> matrix [[0.9,0.2],[0.5,0.8]], state.identifiers ["A","B"]
shared compute -> RankingResult.identifiers ["0","1"]
page top-ten -> state.identifiers[row]       # A/B
JSON download -> result.identifiers          # 0/1
```

```text
Headerless web CSV
0.9,0.2
0.5,0.8

workflow parser -> matrix [[0.9,0.2],[0.5,0.8]], state.identifiers ["1","2"]
```

The headerless mapping shown above is verified source behavior. It does **not** meet the approved identifier-column contract.

## After: required mappings

```text
Headered CSV
Source Asset,Quality,Cost
A-001,0.9,0.2
B-002,0.5,0.8

parsed input -> identifier_header "Source Asset"
             -> identifiers ("A-001", "B-002")
             -> scores [[0.9,0.2],[0.5,0.8]]
compute(scores, criteria, identifiers) -> RankingResult.identifiers unchanged
page / JSON / CSV download -> same identifiers resolved by ranked row index
```

```text
Headerless CSV
A-001,0.9,0.2
B-002,0.5,0.8

parsed input -> identifier_header "Asset ID"
             -> identifiers ("A-001", "B-002")
             -> scores [[0.9,0.2],[0.5,0.8]]
```

## Required invariants

1. `len(identifiers) == scores.shape[0] == len(result.ranking) == len(result.net_flow)`.
2. `scores.dtype` is C-contiguous `float64`; identifiers are immutable strings.
3. Every CSV data row has exactly `C+1` cells; only cells `1..C` undergo float conversion.
4. For headered input, `headers[1:]` equals criterion names in order; `headers[0]` is non-empty.
5. `ranking` remains a permutation of `0..N-1`; a ranked label is `identifiers[ranking[position]]`.
6. JSON and CSV result artifacts contain source labels exactly once per source row and in ranked-row order where applicable.
7. Data labels never affect numerical scores, weights, thresholds, comparator input, cache token, filesystem path, or URL.
8. Every minimize criterion has normalized validated scores in `[0,1]` before its `1-g` transformation.

## Pairwise-difference equivalence

For two alternatives `i,k` and a minimize criterion:

```text
old(i,k) = (-g_i) - (-g_k) = g_k - g_i
new(i,k) = (1-g_i) - (1-g_k) = g_k - g_i
```

Therefore old and new pairwise input differences equal each other. All downstream operations that depend only on these differences receive mathematically identical inputs. Ranking invariance follows when tie handling stays unchanged.

This is a mathematical proof under real arithmetic. The future implementation must add IEEE-754 boundary tests and must not present this document as executed proof.

## Migration messages and compatibility

Required headerless CSV rejection when an input row contains `C` rather than `C+1` cells:

```text
CSV row <n> has <C> columns; expected <C+1>: identifier in column 0 followed by <C> criterion scores.
```

Recommended identifier validation response:

```text
CSV row <n>, identifier column 0 is missing or blank.
```

A legacy numeric-only file must be selected through an explicit compatibility path. It obtains positional identifiers, and its output metadata/docs must state that source identifiers were unavailable. Do not allow headerless numeric CSV to be reinterpreted as identifiers automatically.

## Serialization/cache/download before-after impact

`RankingResult` and canonical serializers already contain an `identifiers` sequence. The target change is producer-side: populate it from parsed identifiers. Cache splitting and checksum validation operate on result bytes and require no new identifier side channel. A serialization-version policy remains an implementation decision: keep `SERIALIZER_VERSION="1"` only if formal compatibility review concludes that changed values are semantically valid within the version; otherwise increment version and test all clients/manifests. This is a recommendation, not an implemented version change.
