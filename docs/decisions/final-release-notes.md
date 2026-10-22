# Final release notes

**Release date:** 2026-10-22
**Release status:** **released with limitations**
**Scope:** Final Release Gate. This record releases the tested local source and the three approved preserved reference artifacts. It does not claim full browser readiness.

## Included focused release records

- `out/archive/dc-5-preserved-references/clipboard-2026-10-22_05-35-51.png`
- `out/archive/dc-5-preserved-references/dc-4-5-single-card-selected.svg`
- `out/archive/dc-5-preserved-references/dc-4-5-single-card-unselected.svg`
- This final gate checkpoint and release records.

`ARCHIVE-MANIFEST.md` was already tracked and remains unchanged. The three archived references are preserved material, not product evidence.

## Final Release Gate validation

| Category | Exact command | Result |
| --- | --- | --- |
| Full regression | `python -m pytest tests -q` | `932 passed in 8.00s` |
| DC-1–DC-4.5 contracts, identifiers, serializer v2, direct 1-g scientific invariance, cache/download/security/runtime, composition, document links | `python -m pytest tests/test_dc1_contract.py tests/test_dc2_identifier_migration.py tests/test_dc3_minimize_transform.py tests/test_dc4_cli_converter_migration.py tests/test_dc45_criteria_cards.py tests/test_serialization.py tests/test_result_cache.py tests/test_security.py tests/test_security_headers.py tests/test_runtime.py tests/test_end_to_end_composition.py tests/test_local_document_links.py -q` | `128 passed in 2.82s` |
| DC4.5 UI, CSP, no-JS | `python -m pytest tests/test_dc45_criteria_cards.py tests/test_active_template_ui.py tests/test_ui_styles.py tests/test_security_headers.py -q` | `64 passed in 0.83s` |
| Independent local reproducibility; no persistent service | `python -m pytest tests/test_cli_run.py tests/test_convert_matrix_csv.py tests/test_app_workflow.py -q` | `36 passed in 0.80s` |
| Syntax and diff integrity | `python -m compileall -q electre3 app tests && git diff --check && git diff --cached --check` | exit code `0` |

The focused suites include positive workflows, negative validation and security paths, and boundary cases. Covered boundaries include invalid criteria and identifiers, non-finite/out-of-range scores, direct minimize threshold/ULP cases, result-token/cache expiry and integrity failures, 2/8 selection boundaries, and missing/invalid workflow state.

## Review records confirmed

- **Scientific:** APPROVED — direct direction-aware `1-g` evaluation, threshold/ULP boundaries, and raw-flow behavior.
- **Engineering:** APPROVED — contract and regression evidence, compile/diff integrity, and scope review.
- **Security:** APPROVED — CSP/headers, upload and identifier validation, session-bound downloads, cache expiry, integrity, and rate limiting.
- **UI/UX:** APPROVED WITH DEFERRED LIMITATIONS — static card-state, semantic markup, focus CSS, responsive declarations, brand tokens, and no-JS evidence.

See `docs/decisions/dc-5-release-reviews.md` and `docs/decisions/dc-5-security-evidence.md` for supporting evidence.

## Explicit release limitations

The release has **no browser-rendered verification** for reflow, zoom, keyboard operation, offline behavior, screen-reader/assistive-technology behavior, or load performance. Flask test-client and static-source checks do not establish browser enforcement, deployment behavior, proxy configuration, external-client compatibility, or penetration-test coverage. Do not interpret this release as full browser readiness.

## Reproducibility boundary

All commands ran locally with repository dependencies and no persistent service. The test evidence establishes only the covered local implementation behavior.
