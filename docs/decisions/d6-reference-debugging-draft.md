# D6 Phase 4 Reference and Debugging Draft

**Status:** Draft only. No user-facing page edits. Scientific and Engineering review pending.

## 1. CLI reference

```cmd
set PYTHONPATH=.
python -m electre3.cli matrix_file criteria_file [-o OUTPUT] [-b BLOCK_SIZE] [-y] [-q]
```

- `matrix_file`: identifier-bearing CSV, numeric `.npy`, or one-array `.npz`.
- `criteria_file`: UTF-8 JSON criteria list.
- `-b/--block-size`: integer `1..10000`; default `1000`.
- `-y/--yes`: skip confirmation prompts.
- `-q/--quiet`: suppress computation/status and save messages; it does not suppress prompts or ranking output when no `--output` is supplied.
- `-o/--output`: saves zero-based ranking row indices with NumPy serialization, not identifiers or net-flow scores.

The ranking deadline applies to the ranking computation. Parsing, request handling, and response serialization are separate work.

Errors print to stderr and return nonzero. The CLI ranks by descending raw net flow. Printed output uses source identifiers for identifier-bearing CSV and positional identifiers for numeric NumPy input.

## 2. Input reference

CSV shape is `(N,C+1)`: string identifier in column 0 and `C` finite normalized scores in columns 1..C. Headered input preserves its non-empty identifier heading. Headerless input displays `Asset ID`. IDs are non-empty, unique, and at most 50 characters. NumPy matrices contain numeric `(N,C)` scores and receive positional identifiers.

Criteria require `name`, positive `weight`, `q`, `p`, `v`, and Boolean `maximize`; `0 ≤ q ≤ p ≤ v`, weights sum to one, and one to eight criteria are supported.

## 3. Scientific reference

This project implements **ELECTRE III credibility followed by descending raw-net-flow ranking**, not ELECTRE III distillation. `a` and `b` are alternative objects; matrix rows and columns are comparison groups.

For direction-adjusted pair differences, maximize criteria use `g(a)-g(b)`. Validated minimize criteria directly use `g(b)-g(a)`, equivalent to normalized `1-g` without storing rounded transformed values.

Concordance is full when `diff ≥ -q`, zero when `diff ≤ -p`, and linear between. If `q=p`, the full-concordance branch takes priority at the overlap. Discordance is zero when `diff ≥ -p`, one when `diff ≤ -v`, and linear between. If `p=v`, the full-veto branch takes priority at the overlap. Credibility starts at concordance and applies `(1-d_j)/(1-C)` only when `C<d_j<1`; `d_j=C` does not reduce credibility and `d_j≥1` is a full veto.

Raw flow excludes the diagonal:

`φ(a) = Σ(b≠a) S(a,b) − Σ(b≠a) S(b,a)`.

Raw flow is not normalized; `NetFlowAccumulator.normalize()` is not used for ranking. Exact equal flows are ties with no documented stable relative order because ranking uses `np.argsort(-net_flow)`. Scores are validated in `[0,1]` at the shared CLI/web boundary.

## 4. Web and runtime limits

The supported `/app/*` workflow validates criteria and matrix input, requires preview before compute, and uses server-rendered HTML without JavaScript. Documentation routes and legacy compatibility routes have separate behavior.

Supported routes include `GET /app/`, `POST /app/confirm-inputs`, `POST /app/preview`, `POST /app/compute`, and `GET /app/download/<token>`. Compatibility routes include `GET /preview/<upload_id>`, `POST /preview/<upload_id>/confirm`, `POST /preview/<upload_id>/cancel`, `POST /compute/start`, and `GET /compute/status/<job_id>`.

- `/app` upload limit: 100 MiB; larger requests return HTTP 413.
- Shared row limit: 100,000.
- `/app` feasibility gate: reject estimated runtime above 300 seconds.
- Hard timeout: 330 seconds; no partial result publication.
- Cache: one latest process-memory result, maximum 32 MiB cached artifact payload; metadata adds separate memory overhead.
- Split parts: 16 MiB maximum per part.
- Cache TTL: 30 minutes.
- Signed session lifetime: 30 minutes.
- Successful downloads: 30 per session per rolling minute.
- Cache is single-worker and process-local; restart invalidates results.
- Serializer version: 2.

## 5. Module reference

Source links:

- [data.py](../../electre3/data.py)
- [shared.py](../../electre3/shared.py)
- [ranking.py](../../electre3/ranking.py)
- [concordance.py](../../electre3/concordance.py)
- [discordance.py](../../electre3/discordance.py)
- [credibility.py](../../electre3/credibility.py)
- [accumulator.py](../../electre3/accumulator.py)
- [serialization.py](../../electre3/serialization.py)
- [workflow.py](../../app/routes/workflow.py)
- [result_cache.py](../../app/services/result_cache.py)

| Module | Role |
|---|---|
| `electre3/data.py` | Identifier-aware CSV and numeric NumPy input loading. |
| `electre3/shared.py` | Strict shared validation and result construction. |
| `electre3/ranking.py` | Blockwise ELECTRE computation and raw ranking. |
| `electre3/concordance.py` | Partial/global concordance. |
| `electre3/discordance.py` | Discordance and veto. |
| `electre3/credibility.py` | Credibility reductions. |
| `electre3/accumulator.py` | O(N) incoming/outgoing flow accumulation. |
| `electre3/serialization.py` | Serializer v2 and split/checksum validation. |
| `app/routes/workflow.py` | Server-rendered app flow and download route. |
| `app/services/result_cache.py` | Latest-only cache, token, TTL, rate, and checksum controls. |

## 6. Debugging reference

- **400:** invalid criteria, matrix, header, score, or missing confirmation.
- **403:** legacy compatibility route lacks upload confirmation. Use `/app/` for the supported flow.
- **422:** `/app` feasibility estimate exceeds 300 seconds.
- **504:** hard deadline expired. No partial result is published.
- **404 download:** token expired, replaced, foreign-session, unknown, or lost after restart.
- **410 download:** cached checksum validation failed.
- **429 download:** successful-download rate limit reached.

Use the current runbook: [debugging](../runbook/debugging.md).

## 7. Reproducibility and evidence

Run every command at a pinned revision. Record command, environment, exit code, output, hashes, and limitations. Cover positive, negative, and edge cases across unit, integration, scientific, security, UI/static, performance, serialization/cache, end-to-end, links, and generated-site checks. Every changed or added Python module must pass the strict 50-executable-line audit.

## 8. Current and planned documentation

- Current D5 mental model: `docs/modules/ranking_tutorial_side_by_side.html` and generated `website/modules/ranking/tutorial/index.html`.
- D5 source draft: `docs/decisions/d5-mental-model-draft.md`.
- Phase 4 reference: this draft; publication pending review and reproducibility.
- Companion website D6 reference integration: planned, not yet created.

When transferred to HTML, preserve complete math meaning with semantic `<var>`, `<sub>`, `<sup>`, and text operators. The reference must remain readable without JavaScript and must not require KaTeX. Every changed or added Python module must pass the strict 50-executable-line audit; `scripts/build_website.py` remains an existing documented exception.

Browser rendering, keyboard/focus, zoom/reflow, offline, accessibility/AT, screen-reader, and load/performance evidence remain deferred and non-blocking.
