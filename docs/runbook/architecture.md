# Repository architecture (ELECTRE III credibility + blockwise net-flow ranking)

## Purpose
This runbook describes how the codebase is structured, how data flows through the pipeline, and which invariants keep results deterministic.

## Top-level layout

- `electre3/` — Core algorithms and CLI entrypoints (pure Python + NumPy)
- `app/` — Flask UI and documentation routes
- `docs/` — Offline-first HTML documentation and module tutorials
- `tests/` — Deterministic test suite (use `pytest tests/`)

## Core pipeline (conceptual)

1. **Inputs**
   - Performance matrix `G` with shape `(N, M)`
   - Criterion thresholds and weights (`q`, `p`, `v`, `w`) derived from `electre3/config.py`

2. **Per-block credibility**
   - `electre3/block.py::compute_block(rows, cols, q, p, v, w, is_diagonal)`
   - Computes a credibility submatrix `S_block` for a block of row alternatives vs column alternatives.
   - Diagonal blocks must be called with `is_diagonal=True` so the *local* diagonal is cleared.

3. **Accumulation (O(N) memory)**
   - `electre3/accumulator.py::NetFlowAccumulator`
   - `update(S_block, row_start, col_start)` updates:
     - `outflow[row_start:row_start+B1] += S_block.sum(axis=1)`
     - `inflow[col_start:col_start+B2] += S_block.sum(axis=0)`
   - `net_flow() = outflow - inflow`

4. **Ranking**
   - `electre3/ranking.py`
   - Project contract: sort alternatives by **raw net flow (descending)**.
   - `normalize()` exists for presentation only; it must not silently change ranking semantics.

## Module map (core)

- `electre3/config.py` — Criterion configuration structures and validation at construction time.
- `electre3/validate.py` — Validation utilities for config and array-level checks.
- `electre3/concordance.py` — Concordance computation primitives.
- `electre3/discordance.py` — Discordance computation primitives.
- `electre3/credibility.py` — Credibility aggregation (concordance + discordance logic).
- `electre3/block.py` — Blockwise credibility computation for scalability.
- `electre3/accumulator.py` — Net-flow accumulation without storing N×N.
- `electre3/ranking.py` — Net-flow ranking utilities.
- `electre3/data.py` — IO helpers for matrices/configs used by CLI/UI.
- `electre3/cli.py`, `electre3/cli_run.py` — CLI entrypoints.

## Determinism invariants (project-level)

- No randomness in the pipeline.
- Block tiling must be deterministic (fixed iteration order, fixed block size policy).
- Floating-point results must be stable:
  - Use consistent dtypes (float64 for flows).
  - Avoid nondeterministic parallelization.

## Flask UI / docs surface

- `app/__init__.py`
  - Adds security headers on all responses.
  - Uses route-scoped CSP:
    - Docs routes allow local scripts (`script-src 'self'`) for theme toggle/highlight.
    - App routes disallow scripts (no `script-src`).

- `app/routes/docs.py`
  - Strict allow-list for module docs and tutorial assets.
  - Rejects traversal via name regex + allow-list membership.

- `app/routes/preview.py`
  - Upload confirmation gate stored in session.

- `app/routes/compute.py`
  - Starts computation jobs from a confirmed upload and validated criteria JSON.

## Test harness notes

- Run the main suite with:
  - `pytest tests/`
- Avoid running `pytest` at repo root unless you intentionally want to collect snapshot tests under `docs/design/*`.
