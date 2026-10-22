# DC-4 documentation notes

## Scope and authoritative sources

DC-4 is limited to the approved identifier-bearing CSV contract across CLI, data, converter, examples, expected output, migration documentation, and tests. DC4.5 criteria-card UI is explicitly excluded. D3 final publication changes are explicitly excluded.

Authoritative contract sources inspected before editing:

- User-approved DC-4 brief and shared scratchpad: CSV shape `(N,C+1)`, identifier in column zero, headerless `Asset ID`, preserved headered heading, nonempty/unique/max-50 identifiers, positional NumPy identifiers, serializer v2, and minimize `1-g`.
- `electre3/data.py`: CLI CSV loader and positional NumPy behavior.
- `electre3/shared.py`: shared identifier, header, normalized-score, and ranking boundary validation.
- `electre3/serialization.py`: `SERIALIZER_VERSION = "2"` and identifier serialization.
- `docs/decisions/dc-3-recovery-notes.md`: direct direction-aware pairwise computation preserves `1-g` semantics and binary64 subnormal differences.

## Changes checkpointed before regression failure

- Created `out/dc-4-checkpoint.json` before product changes.
- Updated `scripts/convert_matrix_csv.py` to validate a selected identifier column with the shared identifier contract before emitting its numeric `(N,C)` core.
- Repaired malformed `examples/assets_priority` CSV samples, updated expected CLI output, and documented direct identifier-bearing CLI operation and deliberate NumPy conversion.
- Updated `README.md`, `docs/tutorials/cli_quickstart.md`, `docs/GETTING_STARTED.html`, and `website/index.html` to describe the current CSV and positional NumPy contracts.
- Updated stale D3 placement assertions that required legacy `Alt N` output, Mermaid rationale, and obsolete CLI phrases; the tests now require identifier-bearing CSV and positional NumPy documentation without weakening D3 hardening or layout checks.
- Added `tests/test_dc4_cli_converter_migration.py` covering CLI, converter, data loader, scientific direction behavior, serializer/cache/download, web end-to-end, security identifier rejection, and stale-example/documentation checks.

## Test evidence

| Category | Command / evidence | Result |
|---|---|---|
| Positive CLI | Direct headered sample CLI subprocess | Passed; exact `B`, `A`, `C` output |
| Converter/data | Headered conversion and positional `.npy` IDs | Passed |
| Negative/security | Empty, duplicate, control-character, and 51-character IDs | Passed |
| Edge | Headerless `Asset ID`; preserved custom heading; header order rejection | Passed |
| Scientific | Subnormal minimize direct-difference comparison | Passed |
| Serialization/cache/download | Serializer v2 JSON/CSV, cache, Flask download | Passed |
| End-to-end | Headered web preview/compute/download | Passed |
| Focused regression | `python -m pytest tests/test_dc4_cli_converter_migration.py tests/test_convert_matrix_csv.py tests/test_dc1_contract.py tests/test_dc2_identifier_migration.py tests/test_dc3_minimize_transform.py tests/test_serialization.py tests/test_result_cache.py tests/test_security.py tests/test_end_to_end_composition.py tests/test_cli_run.py -q` | `119 passed in 2.19s` |
| Compile/diff | `python -m compileall -q electre3 app scripts tests && git diff --check` | Passed; Git emitted only LF-to-CRLF working-copy warnings |
| Initial D3 documentation regression | `python -m pytest tests/test_d3_phase1_docs.py -q` | **3 failed, 6 passed**: legacy `Alt N`, Mermaid, and obsolete output assertions conflicted with DC-4 |
| Positive | Direct headered CSV preserves `B`, `A`, `C`; serializer v2 JSON/CSV preserves identifiers | Passed in focused tests |
| Negative/security | Empty, duplicate, control-character, and 51-character IDs reject | Passed in focused tests |
| Edge | Headerless `Asset ID`, preserved custom heading, header-order rejection, NumPy positional IDs, and subnormal `1-g` evaluation | Passed in focused tests |
| D3 documentation recovery | `python -m pytest tests/test_d3_phase1_docs.py -q` | `9 passed in 0.09s` |
| Focused DC-4 recovery | `python -m pytest tests/test_dc4_cli_converter_migration.py tests/test_convert_matrix_csv.py tests/test_dc1_contract.py tests/test_dc2_identifier_migration.py tests/test_dc3_minimize_transform.py tests/test_serialization.py tests/test_result_cache.py tests/test_security.py tests/test_end_to_end_composition.py tests/test_cli_run.py tests/test_d3_phase1_docs.py -q` | `128 passed in 1.68s` |
| Compile/diff recovery | `python -m compileall -q electre3 app scripts tests && git diff --check` | Passed; only Git LF-to-CRLF warnings |
| Full regression | `python -m pytest tests -q` | `917 passed in 9.26s` |

## Stop condition and limitation

The initial DC-4 attempt stopped before Scientific and Engineering review, commit, and clean-tree verification because the required full regression reported three failures in `tests/test_d3_phase1_docs.py`.

The approved DC-4 recovery limits the change to stale D3 documentation assertions and closely related placed CLI references. It replaces legacy `Alt N`, Mermaid rationale, and obsolete output assertions with explicit identifier-bearing CSV `(N,C+1)`, column-zero identifiers, propagation, positional NumPy identifiers, and current output assertions. It does not alter DC4.5 card UI, D3 hardening/layout tests, or application behavior.

## Recovery reviews

- **Scientific review: approved.** Direct CSV evidence preserves `B`, `A`, and `C`; focused serializer v2 JSON/CSV, cache, and download tests pass; `1-g` direct-evaluation/subnormal evidence remains covered by `tests/test_dc3_minimize_transform.py`.
- **Engineering review: approved.** The recovery diff is confined to approved DC-4 documentation/tests and prior DC-4 migration files; it excludes DC4.5 card UI and application behavior. D3, focused DC-4, compile, whitespace, and full-suite checks pass.
- **UI/UX review: not required.** The recovery does not change DC4.5 card UI or page layout/styling contracts.

## Tutorial notes

Use headered CSV directly to preserve source identifiers. Headerless CSV still includes identifier column zero and displays `Asset ID`. The converter validates then discards selected IDs because `.npy` stores only numeric scores; subsequent NumPy CLI runs use positional identifiers. Minimize semantics remain `1-g`; direct pairwise evaluation uses the equivalent direction-aware difference for IEEE-754 stability.
