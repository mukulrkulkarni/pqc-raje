# Dependency graph (narrative) and module boundaries

## Purpose
This document explains how modules depend on each other and which direction dependencies are allowed to flow.

## Allowed dependency direction

- `app/` depends on `electre3/`.
- `electre3/` does **not** depend on `app/`.
- `tests/` depends on both `electre3/` and `app/`.
- `docs/` is content; it must not be required at runtime for the core algorithm.

## Core algorithm layer (`electre3/`)

### High-level dependency chain

- `config.py` and `validate.py` sit at the bottom of the stack.
- `concordance.py` and `discordance.py` build on validated thresholds/weights.
- `credibility.py` combines concordance + discordance.
- `block.py` applies credibility computation to blocks.
- `accumulator.py` accumulates block outputs into flows.
- `ranking.py` consumes net flow outputs.

### Key boundaries

- **Validation boundary:**
  - Some validation is performed at configuration construction time (`CriterionConfig`), and some is done in `validate.py`.
  - Tests must distinguish between:
    - “constructor rejects invalid config” vs
    - “validator rejects invalid arrays”.

- **Block boundary (scalability boundary):**
  - `compute_block` must not allocate N×N.
  - The only large allocation per call is the local `S_block`.

- **Accumulator boundary (storage boundary):**
  - `NetFlowAccumulator` stores only O(N) state.
  - It does not validate tiling coverage or bounds; caller owns these invariants.

## Flask layer (`app/`)

- Routes call into services, which call into `electre3`.
- Security-critical logic lives in `app/services/security.py`:
  - allow-lists
  - path containment
  - name validation

## Documentation runtime boundary

- Docs/tutorial HTML must work in two modes:
  - served: `/docs/modules/<name>/tutorial`
  - offline: `docs/modules/<name>_tutorial_side_by_side.html`

Constraints:
- No external assets.
- Only relative assets `assets/theme.js` and `assets/highlight.js`.
- CSP is strict; scripts are local only.

## Test dependency notes

- “Doc contract tests” validate tutorial structure (e.g., required subheadings and CSP-safe assets).
- “Deep tests” validate algorithm contracts and numerical oracles.

## Harness note

- Main test suite: `pytest tests/`.
- Root `pytest` also collects snapshot tests under `docs/design/*` and can fail on module-name collisions.
