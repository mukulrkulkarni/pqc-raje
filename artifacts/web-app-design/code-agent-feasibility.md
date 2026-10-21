# Code Agent feasibility recommendation — local ELECTRE III web app

**Status:** Planning only; no application code changed.  
**Evidence date:** 2026-10-21.  
**Recommendation:** Feasible in phased delivery, but do not start compute/cache implementation until the contracts marked **BLOCKER** are resolved.

## Executive recommendation

Build a new, server-rendered workflow beside the existing upload-preview endpoints. Use one framework-free `app.services.compute_adapter` to transform a locked validated-input object into the existing `electre3.ranking.compute_ranking()` call, then serialize the returned raw net-flow results exactly once. Keep results only in a session-bound, process-memory cache.

Reject KaTeX for the app and docs under the stated no-JavaScript/no-build constraints. Use semantic HTML notation (`var`, `sub`, `sup`, text, and entities); it is compatible with the existing no-script app CSP. Do **not** claim CLI/web byte identity until a shared serializer and a block-size reproducibility design pass byte-comparison tests.

**Immediate meeting decision:** authorize a contract-definition milestone only. Stop before implementation if scientific validation, cache limits, or CLI/output scope remain unresolved.

---

## Current behavior versus target behavior

| Topic | Current behavior | Target behavior | Evidence |
|---|---|---|---|
| Core computation | `compute_ranking()` validates, direction-adjusts minimize criteria, computes blocks, accumulates raw net flow, and sorts descending. | Web and CLI invoke the same adapter/core path on one validated data object. | `electre3/ranking.py:10-33` (`compute_ranking`) |
| O(N) accumulation | Two `float64` vectors retain outflow/inflow; a current credibility block is summed. | Preserve no NxN persistence in web orchestration. | `electre3/accumulator.py:11-23`; `electre3/block.py:9-54` |
| CLI | Loads numeric matrix files; `run_ranking()` returns only ranking; `-o` stores only ranking through `np.save`. Criteria defaults can fill missing values. | Full ranking, score vector, identifiers, and downloads use a canonical serializer shared with web. | `electre3/cli.py:8-42`; `electre3/cli_run.py:19-27`; `electre3/data.py:7-25` |
| Preview | Loads file through `load_matrix`, shows rows/statistics and reports NaN/Inf. It does not reject all target-invalid data. | Parse identifiers/header mode, enforce all matrix/criteria policies, produce a validation report, and require a confirmation nonce. | `app/services/preview.py:11-40`; `app/routes/preview.py:35-72` |
| Compute route | JSON-only `/compute/start` confirms registry entry and criteria, then returns a synthetic job ID. `/compute/status/<job_id>` always says complete. | `POST /compute` executes synchronously after confirmed server-side validation, renders result HTML, and writes cache bytes. | `app/routes/compute.py:11-65` |
| Criteria validation | Requires list, nonempty list, `weight/q/p/v`; permits missing `name/maximize`, unlimited length, numeric coercion, and no finite check. | Strict 1–8 item schema: all six fields, string nonempty unique names, strict JSON booleans, finite values, ordered thresholds. | `app/services/security.py:53-100`; `electre3/config.py:12-32` |
| Data formats | Core accepts `.csv`, `.npy`, `.npz`, and `.parquet`; CSV loader is numeric-only. | Web allow-list limits to CSV/NPY/NPZ and owns header/identifier CSV parsing. | `electre3/data.py:11-25`; requirements invariant 5 |
| Security state | Registry maps caller-provided IDs to paths. Flask default secret is embedded. 100 MiB request cap exists. | Opaque server-generated handles, configurable secret, scoped temporary data cleanup, session-bound result tokens, row/byte caps. | `app/services/security.py:8-36`; `app/__init__.py:33-35` |
| CSP/no-JS | App HTTP CSP omits `script-src`; `config.html` has contradictory inline `script-src 'unsafe-inline'`. Docs route permits scripts. | App pages omit `script-src` and contain no scripts/event handlers. Decide documentation scope separately. | `app/__init__.py:20-22`; `app/templates/config.html:6`; `app/routes/docs.py:27-42` |
| Cache/serializers | No result cache or result serializer exists. | Latest-result-only, bounded process cache stores immutable serialized bytes and safe metadata. | gap register G-09/G-10 |

## Proposed target architecture

```text
HTML form routes
  input_workflow routes  ──> input_contract parser/validator ─┐
  download routes        ──> result_cache                      │
                                                               v
                         ValidatedRunInput ──> compute_adapter.run()
                                                           │
                                              electre3.compute_ranking()
                                                           │
                         canonical_serializers <── RunResult (ranking, raw scores)
                                                           │
                                              result_cache (bytes only)
CLI commands ───────────────────────────────> same adapter + serializers
```

### New modules

| Module | Responsibility | Must not do |
|---|---|---|
| `app/services/input_contract.py` | Parse criteria and matrix bytes; header detection; missing-value policy; create immutable `ValidatedRunInput`. | Call Flask globals, create cache entries, calculate ELECTRE. |
| `app/services/compute_adapter.py` | Convert strict criteria records to `CriterionConfig`; call `compute_ranking`; bind identifiers; return `RunResult`. | Reimplement ranking or mutate input. |
| `app/services/canonical_serializers.py` | Create all downloadable bytes deterministically from `RunResult`. | Read request/session or use locale/current time. |
| `app/services/result_cache.py` | Bounded, locked, latest-only bytes cache and session-bound opaque tokens. | Store raw uploads, parsed matrix, criteria, or Flask session object. |
| `app/routes/workflow.py` | Four form routes and user-visible error rendering. | Parse CSV directly or invoke core directly. |
| `app/routes/downloads.py` | Authorise and serve cached bytes with fixed content type. | Regenerate results or accept filesystem paths. |
| `electre3/adapter.py` (preferred shared location) | A framework-free `run_validated(matrix, criteria, config)` function used by CLI and web. | Parse web forms, cache, or write files. |

**Choice:** locate the shared compute adapter in `electre3/`, because CLI and web require one computation boundary. `app.services.compute_adapter` may only bind app-level identifiers and call it.

## Route design

New routes are recommended. Existing JSON routes remain temporarily as compatibility endpoints and must not be represented as implementing the target flow.

| Route | Method | Server-owned input/output | Required gate |
|---|---:|---|---|
| `/app` | GET | Criteria entry form. | No computation. |
| `/confirm-inputs` | POST | Strict criteria parse; short-lived server-side draft handle; matrix entry form. | Reject invalid/more-than-eight criteria. |
| `/preview` | POST | Parse uploaded/pasted bytes once; render headers, mapping, first five rows, validation report; issue confirmation nonce. | Reject invalid header, shape, values, rows, formats, or missing values without approval. |
| `/compute` | POST | Consume draft handle plus one-time preview nonce; calculate and render top 10. | Revalidate stored canonical input and require prior successful preview. |
| `/results/<token>/<format>` | GET | Serve exact cached bytes for approved format. | Constant-time token check, session binding, TTL, rate/timeout policy. |

**Migration/rollback:** reserve current `/preview/<upload_id>`, `/compute/start`, and `/compute/status/<job_id>` until a separately approved deprecation test proves dependents migrated. They return JSON and do not match the no-JS target interaction. New target routes should have their own blueprint and templates. The bare `/` currently serves documentation (`app/routes/docs.py:27-34`), so target requirement `/` conflicts with deployed routing. Either mount workflow at `/app` first, or formally move docs to `/docs/` with redirects and regression tests. **BLOCKER:** product owner must select one.

## Input and data contracts

### `CriterionRecord` — strict web input

```json
{"name":"Quality","weight":0.6,"q":0.02,"p":0.08,"v":0.25,"maximize":true}
```

* Top-level JSON is an array of 1–8 records.
* Required fields are exact: `name`, `weight`, `q`, `p`, `v`, `maximize`.
* `name`: nonempty Unicode after trim; unique under an agreed comparison policy. **Open:** byte-exact vs case-fold uniqueness.
* Numeric fields: JSON numbers only, finite IEEE-754 `float64`; `weight > 0`; `0 <= q <= p <= v`.
* `maximize`: JSON boolean only; do not use `bool("false")` or string coercion.
* Weight total and matrix score range conflict across source material: invariants only require positive weights; the walkthrough says target weights sum to 1 and values lie in `[0,1]`. **BLOCKER:** scientific owner must make these target acceptance conditions explicit. The existing core intentionally normalizes any positive weights (`electre3/config.py:44-47`).

### `ValidatedRunInput` — server-side, immutable

| Field | Contract |
|---|---|
| `matrix` | C-contiguous, owned `float64` ndarray with shape `(N,C)`, `N >= 2`, finite, and C equals criteria count. Apply `[0,1]` only if approved. |
| `criteria` | Ordered tuple of strict records; order defines matrix criterion columns. |
| `identifiers` | Tuple of N display strings. Never passed to Electre core. |
| `header_mode` | `headered_csv`, `headerless_csv`, or `numpy`. |
| `labels` | Identifier label and ordered criterion labels used only for rendering. |
| `missing_replacement` | `None`, or approved finite float in `[0,1]` for CSV only. Record replacement count and location summary. |
| `config` | `ComputeConfig` containing an approved bounded positive block size. |
| `fingerprint` | SHA-256 of canonical validated input bytes, for audit correlation only; not a download token. |

### Matrix parsing policy

1. Accept pasted CSV or uploaded CSV/NPY/NPZ; reject extension/content disagreement and client paths.
2. CSV must produce `N x (C+1)` logical fields: identifier plus C criterion values.
3. Headered CSV accepts any nonempty identifier heading, then criterion names exactly equal to criterion order; reject duplicates, reordering, and extra columns.
4. Headerless CSV labels logical columns `Asset ID`, then criteria names. Identifier values must remain strings; numeric values parse to `float64`.
5. NumPy input has no identifiers. Generate stable index identifiers only unless a separate identifier-list contract is approved. NPZ must require exactly one named array or an explicitly selected, allow-listed key.
6. Empty CSV cells: reject by default. Permit only after explicit preview checkbox and supplied/default replacement `0.0` in `[0,1]`; record the policy in preview and result metadata. Never repair criteria JSON.
7. Reject malformed CSV, nonnumeric criterion cells, `NaN`, `Inf`, wrong shape, fewer than two rows, and row/byte excess before core invocation.

**Unresolved limits (BLOCKER):** maximum upload bytes, matrix rows, block-size range, cache bytes, cache entries, TTL, download rate, and compute timeout have no measurable approved values. `MAX_CONTENT_LENGTH=100 MiB` is a current Flask setting, not an adequate target contract (`app/__init__.py:34`).

## Shared compute adapter

```python
# target API; illustrative only, not implemented
@dataclass(frozen=True)
class RunResult:
    ranking: np.ndarray      # int64, shape (N,)
    scores: np.ndarray       # float64 raw net flow, shape (N,)
    identifiers: tuple[str, ...]
    criteria: tuple[CriterionRecord, ...]
    config: ComputeConfig


def run_validated(validated: ValidatedRunInput) -> RunResult:
    core_criteria = tuple(CriterionConfig(...strict fields...) for ...)
    ranking, accumulator = compute_ranking(validated.matrix, core_criteria, validated.config)
    scores = accumulator.net_flow()
    return RunResult(ranking, scores, validated.identifiers, validated.criteria, validated.config)
```

This retains core isolation. `compute_ranking()` already uses `ComputeConfig`, direction adjustment, blocks, and `NetFlowAccumulator` (`electre3/ranking.py:10-33`). `compute_block()` has only one current `(B1,B2,C)` difference and a `(B1,B2)` score block (`electre3/block.py:35-54`). The adapter must not call `accumulator.normalize()` because ranking is raw net flow; existing end-to-end tests enforce that distinction (`tests/test_end_to_end_composition.py:test_end_to_end_sorting_never_uses_normalize`).

### Reproducibility qualification

Current block accumulation uses `S_block.sum(axis=...)` for each block (`NetFlowAccumulator.update`, `electre3/accumulator.py:16-20`). Different `block_size` values group floating-point additions differently, so byte-identical score output across block sizes is **not established**. The existing tests establish numerical agreement for several sizes, not byte equality (`tests/test_end_to_end_composition.py:test_end_to_end_blockwise_matches_full_reference`).

**BLOCKER:** the invariant requiring block-size-invariant bytes needs a scientific/engineering decision:

* define a canonical fixed reduction order independent of blocks, while retaining bounded memory; or
* guarantee only numerical equivalence under a specified tolerance; or
* restrict byte-identity claims to a fixed shared block size.

Do not publish a byte-identity promise before this choice and tests pass.

## Canonical result serialization contract

Create serializer version `electre3-result-v1` only after the unresolved core policy is decided.

| Artifact | Canonical form |
|---|---|
| `ranking.json` | UTF-8 without BOM, LF newline, final LF, compact JSON, fixed key order, `allow_nan=False`; include schema version, ranking index array, raw score representation, and explicit tie policy. |
| `ranking.csv` | UTF-8 without BOM, LF newline, fixed header order: `rank,alternative_index,asset_id,raw_net_flow,tied_with_previous`; RFC 4180 quoting; fixed numeric formatter agreed after reproducibility decision. |
| `ranking.npy` | C-contiguous `int64` array saved through one shared function; no pickle. |
| `scores.npy` | C-contiguous `float64` raw net-flow vector saved through the same shared function. |
| optional `manifest.json` | Metadata only: serializer version, shapes/dtypes, criteria canonical JSON, block size, input fingerprint; no raw input matrix or token. |

Serialize once during compute; cache the resulting immutable bytes. CLI must call the same serializer rather than its current `np.save(ranking)` path (`electre3/cli.py:38-40`). Use Python `json` parameters explicitly and a designated numeric encoder. JSON’s standard float rendering is stable only for a pinned runtime and is insufficient to prove cross-version decimal stability; pin the runtime or specify an exact decimal/hex representation. **BLOCKER:** choose the numeric wire format and supported Python/NumPy versions.

## Bounded cache integration

### Required target cache record

```text
CacheEntry(
  token_digest, session_binding_digest, expires_monotonic,
  artifacts: Mapping[format, bytes], content_types,
  total_bytes, serializer_version
)
```

* One process-global entry maximum, guarded by a lock; replace atomically only after all serializations succeed.
* Generate token with `secrets.token_urlsafe(32)`; store only a SHA-256 digest; compare digests with `hmac.compare_digest`.
* Bind to a server-side session identifier digest. Flask’s signed cookie must never contain result bytes, raw data, criteria, or download token.
* Require proposed limits before construction: `max_entries=1`, an approved `max_total_bytes`, approved TTL, rate limit, and synchronous compute/download timeout.
* Evict expired entry on access; delete/reject over-limit result before insertion; replacement invalidates old token. Unknown, malformed, expired, replaced, cross-session, and restarted-process tokens give the same non-disclosing 404/410 policy.
* State one worker only. Process restart invalidates all results. Do not add a shared cache without a separate threat model.
* Serve `Content-Disposition: attachment`, exact cached content type, `Cache-Control: no-store`, `X-Content-Type-Options: nosniff`, no redirect that exposes token, and no token logging.

Current upload registry provides only path lookup, not lifecycle, bounds, or session ownership (`app/services/security.py:8-36`). It is not a sufficient cache substrate.

## KaTeX and no-JavaScript assessment

**Recommendation: reject KaTeX.**

| Option | Assessment |
|---|---|
| Client-side KaTeX | Infeasible: needs executable script and conflicts with app CSP requirement to omit `script-src`. |
| Pre-rendered KaTeX | Reject: requires a build artifact/toolchain, violates no-build constraint, and creates additional supply-chain/a11y verification work. |
| Server-rendered MathML | Possible only after accessibility/browser support review; adds complexity without a stated need. |
| SVG equations | Possible but creates generated asset/a11y burden and no functional gain. |
| Semantic HTML notation | Select: no JS, no build step, readable with screen readers when labels accompany notation. |

`CSP_APP` already omits `script-src` (`app/__init__.py:20-22`), but `app/templates/config.html:6` injects a conflicting CSP with `script-src 'unsafe-inline'`; remove the template CSP or make it identical to the response header. The existing documentation policy is separate: docs CSP permits `script-src 'self'` and tutorial assets allow `theme.js` (`app/__init__.py:14-16`, `app/routes/docs.py:13-16`). **BLOCKER:** product/security must resolve whether no-JS applies to docs. App-only no-JS is feasible; whole-site no-JS requires docs remediation outside this web workflow.

## Phased milestones, owners, tests, and stop conditions

| Phase | Owner | Scope and acceptance tests | Stop condition |
|---|---|---|---|
| 0 — Contract closure | Scientific Critic + Security Lead + Product owner | Signed decision for route root, score range/weight rule, deterministic reduction/byte promise, numeric format, all limits, docs no-JS scope, identifier policy. | Any item remains undefined or contradicts requirements. |
| 1 — Pure contracts | Code Agent; Engineering Critic reviews | Unit tests: criteria missing `name/maximize`; nonboolean maximize; >8; nonfinite values; duplicate names; headered/headerless mapping; missing-checkbox matrix; NPY/NPZ policy. | Parser lacks lossless identifiers or validation differs from chosen contract. |
| 2 — Shared compute/serialization | Code Agent; Scientific Critic reviews | CLI and adapter use same run function; compare ranking/scores shape, dtype, values; `filecmp.cmp(..., shallow=False)` for same configured input; B=1, B=2, default and boundary tests. | Block-size byte test fails under selected invariant; core output diverges. |
| 3 — Server-rendered workflow | Code Agent + UI/UX | GET/POST route tests; no computation before preview nonce; rendered header mapping/first-five rows/missing-value disclosure; top 10 including N<10 and tie display; template scan has no script/event handlers. | `/` migration breaks docs tests without approved rollback; accessibility acceptance fails. |
| 4 — Result cache/downloads | Code Agent + Security Lead | Tests: max entries/bytes, replacement, expiry, unknown/malformed/session-mismatched/restarted token, exact byte response, content types, concurrent download/replacement, timeout/rate decision. | Limits are absent; raw inputs/cookies contain prohibited data; cache race returns mismatched metadata/bytes. |
| 5 — Release gate | Engineering Critic + Security Lead + Scientific Critic | Full regression suite; CLI/web equivalence fixtures; security header checks including no `script-src`; local binding config test; memory/block instrumentation as agreed. | Any blocker or required test fails; no production-readiness claim from smoke tests. |

### Minimum acceptance-test matrix

* Strict criteria: all required-field, type, finite, bounds, and max-eight failures.
* Matrix: malformed CSV, extra/missing/reordered headers, row mismatch, empty ID policy, nonnumeric, NaN, Inf, exact row/byte caps, missing CSV cells with and without explicit approval.
* Scientific: minimize direction, q=p, p=v, full veto, N=2, ties, raw net-flow (not normalization), block shapes, no NxN persistence instrumentation.
* Equivalence: same input/config gives elementwise equal `int64` ranking and `float64` scores; repeated canonical bytes match; block-size test follows the chosen reproducibility rule.
* Routes: direct POST to compute without valid preview/nonce fails; result renders top `min(10,N)`; all user errors are escaped and actionable.
* Cache: malformed/unknown/expired/replaced/session-mismatched/restart token fails safely; exact cached bytes and headers succeed; atomic replacement race cannot cross artifacts.
* Security: path traversal, extension/content mismatch, oversized body, no external URLs/scripts in app output, CSP source/header agreement, non-default secret config.

## Explicit unresolved contracts and stop conditions

1. **Route root conflict:** requirements define workflow `/`; code defines documentation `/`. Select migration or use `/app`.
2. **Scientific validation conflict:** source demands positive weights but walkthrough demands sum-to-one; walkthrough demands values `[0,1]`, invariants do not. Lock the rule before validation implementation.
3. **Byte identity conflict:** current reduction order makes cross-block-size bytes unproven. Select a reproducibility mechanism before claiming invariant 4.
4. **Output contract gap:** current CLI emits ranking only, while target demands scores/identifiers/downloads. Select mandatory artifact set and numeric representation.
5. **Operational limits absent:** all cache/upload/download/timeout thresholds need exact values and tests.
6. **Identifier contract gap:** headerless CSV requires a first identifier column; NumPy identifiers need a separate list or index-only rule.
7. **No-JS scope conflict:** app CSP works in principle but `config.html` contradicts it; docs currently permit/serve scripts.
8. **State/security gap:** embedded development secret and global path registry are unacceptable target designs; define configuration injection, session lifecycle, upload expiry, and cleanup.

**Implementation must stop immediately** on any unresolved item above, a critic-confirmed scientific/security defect, a failed canonical-byte test under the selected policy, route migration regression without rollback, cache bound violation, or any material scope expansion.

## Evidence and validation performed

Read: `docs/decisions/web-app-pre-read-meeting-brief.md`; `docs/decisions/web-app-pre-read-gap-register.md`; `web-app-requirements.txt`; relevant `app/`, `electre3/`, templates, and tests. No repository setup script ran. No files under `app/` or `electre3/` changed.

Executed:

```text
python -m pytest tests/test_preview_gate.py tests/test_security.py tests/test_security_headers.py tests/test_cli_run.py tests/test_end_to_end_composition.py -q
69 passed in 1.16s

python -m pytest tests/test_ranking.py tests/test_block.py tests/test_accumulator.py tests/test_data.py tests/test_negative.py -q
63 passed in 0.52s
```

These results validate current behavior and selected negative/edge coverage. They do **not** validate the unimplemented target routes, contracts, canonical serializers, cache, no-JS workflow, or cross-block-size byte identity.
