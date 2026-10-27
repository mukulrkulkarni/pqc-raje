# D4 fixture correction notes

**State:** Checkpointed; Scientific and Engineering review is required before a commit.
**Scope:** Real D4 fixtures and draft only. No user-facing pages, application changes, remote Git, browser testing, or commit.

## Artifacts

- `examples/d4_phase2/` contains 3-, 5-, and 8-asset four-criterion fixtures.
- The five ignored `matrix_headered.csv` fixture files are deterministic generated artifacts. Run `python out\generate_d4_fixture_evidence.py` from repository root before D4 tests; evidence records their SHA-256 values. They remain ignored because the repository ignores all CSV files, but the generator, matrices, hashes, and regression checks make regeneration reproducible.
- `examples/d4_phase2/exact-tie/` and `examples/d4_phase2/near-tie/` contain deterministic comparisons.
- `out/generate_d4_fixture_evidence.py` regenerates fixtures and evidence.
- `out/d4-fixture-evidence.json` records SHA-256 values, direct CLI stdout, binary64 hexadecimal credibility/outflow/inflow/net-flow evidence, and tie assertions.
- `docs/decisions/d4-phase2-tutorial-draft.md` records draft tutorial semantics and paths.

## Test categories and results

| Category | Command | Result |
|---|---|---|
| Positive/end-to-end | `python out\generate_d4_fixture_evidence.py` | Generated all scenario, tie, and near-tie fixtures; direct CLI executions returned 0. |
| Scientific | `python -m pytest -q tests\test_d4_fixture_correction.py` | Validates fixed-matrix comparisons, full-precision exact/near ties, threshold precedence, and `C=1` veto. |
| Negative | Same pytest command | Validates malformed header input fails with CLI exit 1. |
| Edge | Same pytest command | Checks `q=p`, `p=v`, full veto at `C=1`, and exact versus ULP-scale near flow differences. |
| Serialization/reproducibility | Same pytest command | Recomputes fixture byte hashes and compares CLI stdout exactly. |

## Tutorial guidance

Use the direct CSV CLI command when readers need original asset identifiers. Use the converter path only to demonstrate that NumPy arrays retain scores but not identifiers. Explain priority results as a changed preference policy, not a changed algorithm. State that a displayed sort order for equal flows is not a supported tie-break rule.

## Limitations

- `/app` browser, accessibility, zoom, reflow, offline, and load evidence remains deferred and non-blocking.
- The draft names `/app` limits but does not execute a browser flow in this correction.
- The CLI's auto header detection may treat a malformed header as data and emit a numeric-score error; the direct loader's explicit `header_mode="headered"` emits ordered-header validation.
- Scientific and Engineering review remain required. This correction must not be committed before those reviews.
