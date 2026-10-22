# DC-2 documentation notes

## Status

**Current before DC-2:** DC-1 established the identifier-aware input/result contract, serializer version `2`, and normalized minimize transform. The `/app` workflow retained identifiers through preview and JSON download, but rendered result-table labels always said `Asset ID`; the source identifier header was not propagated to the results page. `RankingResult` also trusted direct callers to validate identifier content.

**Target implemented in DC-2:** Both headered and headerless CSV require `(N,C+1)`: column `0` is a string identifier and columns `1..C` are finite normalized `[0,1]` scores. Headerless display uses `Asset ID`; headered preview and results retain the source header. The numeric core remains C-contiguous `float64` `(N,C)`. `RankingResult`, JSON/CSV serializers, checksum cache, download, and results table preserve source identifiers. NumPy remains numeric-only with positional identifiers. Direct result construction now enforces non-empty, unique, maximum-50-character identifiers and rejects control characters.

## Source evidence

- User-approved DC-2 contract and shared scratch pad, 2026-10-22.
- `docs/decisions/data-contract-impact-assessment.md` and `docs/decisions/data-contract-test-matrix.md` define the migration and evidence obligations.
- `app/routes/workflow.py`, `app/templates/app_preview.html`, `app/templates/app_results.html`, `electre3/shared.py`, and `electre3/serialization.py` implement the reviewed propagation path.
- `tests/test_dc2_identifier_migration.py` supplies DC-2 positive, negative, edge, UI, security, serialization/cache/download, integration, and end-to-end evidence.

## Migration

1. Headered CSV producers provide `identifier_header,criterion_1,...,criterion_C`; the identifier header is non-empty and displayed unchanged in preview/results.
2. Headerless CSV producers provide `identifier,score_1,...,score_C`; preview/results display `Asset ID`.
3. Identifiers remain text exactly as decoded, must be non-empty after trimming, unique, at most 50 characters, and contain no control characters. They are HTML-escaped by Jinja and CSV-quoted by `csv.writer`; formula-looking values remain text but downloaded CSV is not claimed spreadsheet-safe.
4. Numeric scores alone enter validation/ranking as `(N,C)`. `.npy`/single-array `.npz` keep positional identifiers (`"0"..."N-1"`) with `allow_pickle=False`.
5. New result/download payloads use canonical serializer version `2`. The process-local cache stores exact result bytes and validates split-artifact checksums before serving them.

## Tutorial notes

DC-2 does not alter final user tutorials or pages. A future user-facing guide must state that a headerless first field is an identifier, not score data, and must caution users to handle formula-looking values safely after CSV download.

## Commands and results

| Category | Command | Result |
|---|---|---|
| DC-2 unit, negative, edge, integration, scientific regression, security, UI, serialization/cache/download, end-to-end | `python -m pytest tests/test_dc2_identifier_migration.py tests/test_dc1_contract.py tests/test_data.py tests/test_shared_contract.py tests/test_serialization.py tests/test_app_workflow.py tests/test_result_cache.py tests/test_ranking.py tests/test_ranking_deep.py tests/test_integration.py tests/test_security.py tests/test_end_to_end_composition.py -q` | `169 passed in 1.76s` |
| DC-1 regression | `python -m pytest tests/test_dc1_contract.py -q` | `9 passed in 0.52s` |
| Relevant full suite | `python -m pytest tests -q` | `891 passed in 7.42s` |
| Compilation/diff | `python -m compileall electre3 app tests && git diff --check` | Passed; no compile or whitespace errors. |

The DC-2 tests prove headered/headerless source labels and identifiers survive parser, core ranking, results page, canonical JSON/CSV, cache, and authenticated download. Negative coverage rejects legacy-width CSV, non-finite/out-of-range scores, blank, duplicate, overlength, and control-character identifiers. The existing DC-1 scientific boundary test retains minimize-transform evidence.

## Reviews

- **Scientific review: approved.** `1-g` remains in `electre3/ranking.py`; the unchanged DC-1 boundary/invariance test passed within the focused command. Identifier extraction occurs before `validate_score_matrix`, preserving an `(N,C)` normalized numeric core.
- **Engineering review: approved.** The reviewed diff passes one validated `identifier_label` from workflow state to Jinja templates, retains cache checksum/session boundaries, and validates direct `RankingResult` construction. The test suite covers serializer, cache, download, escaping, and error paths.
- **UI/UX review: not required.** The change substitutes an existing identifier-column label without changing page/table structure, navigation, styling, or interaction.

## Limitations

- No final user tutorials/pages, D3 documentation, CLI conversion behavior, or legacy `/preview` upload route were changed.
- Browser keyboard, assistive technology, reflow, offline, and spreadsheet application behavior remain unverified.
- Local tests do not establish production readiness, external deployment behavior, load performance, or spreadsheet-injection safety after opening exported CSV.
