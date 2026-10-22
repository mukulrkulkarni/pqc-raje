# v0.1 release verification evidence

**Date:** 2026-10-22
**Scope:** Verification after launcher commit `3e32ed6`; no tag; no feature changes.

## Executed checks

| Category | Command | Result | Positive, negative, and edge evidence |
| --- | --- | --- | --- |
| Full regression | `python -m pytest tests -q` | **947 passed in 18.91s** | Covers all repository regression tests, including valid workflows, rejected inputs, and boundary conditions. |
| Launcher and lifecycle | `python -m pytest tests/test_dev_local.py -q` | **7 passed in 6.27s** | Starts website and Flask, verifies URLs, stops without orphan listeners; rejects occupied, invalid, and equal ports; stops peer after child failure. |
| Identifiers, DC1–DC4, serializer, runtime, science | `python -m pytest tests/test_dc1_contract.py tests/test_dc2_identifier_migration.py tests/test_dc3_minimize_transform.py tests/test_dc4_cli_converter_migration.py tests/test_serialization.py tests/test_runtime.py tests/test_n1_scientific_followup.py -q` | **72 passed in 1.73s** | Verifies valid identity preservation, rejects invalid IDs/contracts, and exercises direct minimize, threshold, ULP, and runtime boundaries. |
| Security, cache, download, session | `python -m pytest tests/test_security.py tests/test_security_headers.py tests/test_result_cache.py tests/test_app_workflow.py tests/test_preview_gate.py -q` | **67 passed in 1.38s** | Covers hardened headers and valid sessions; rejects unsafe uploads, invalid state, stale/tampered tokens, expiry, and rate-limit paths. |
| DC4.5 UI/CSP/no-JS and static website | `python -m pytest tests/test_dc45_criteria_cards.py tests/test_active_template_ui.py tests/test_ui_styles.py tests/test_website_static.py tests/test_docs_routes.py tests/test_local_document_links.py -q` | **249 passed in 2.41s** | Verifies card states and local/static/CSP/no-JS invariants; rejects malformed HTML/nav injection conditions. |
| CLI/workflow edge integration | `python -m pytest tests/test_cli_run.py tests/test_convert_matrix_csv.py tests/test_integration.py tests/test_end_to_end_composition.py tests/test_negative.py tests/test_validate_deep.py -q` | **72 passed in 1.00s** | Covers successful CLI/composition and invalid data, conversion, and deep validator boundaries. |
| Website build, syntax, diff | `python scripts/build_website.py && python -m compileall -q electre3 app scripts tests && git diff --check && git diff --cached --check` | **exit 0** | Deterministic build, Python bytecode compilation, and whitespace-integrity checks pass. |
| Command documentation | `git grep -n "dev_local\|WEBSITE_PORT\|APP_PORT" -- README.md docs scripts tests` plus browser-limitations grep | **exit 0** | README documents the one-command launcher and Windows ports. Getting Started and runbook references are present; limitations remain recorded. |

## Release reviews

| Discipline | Verdict | Basis and limitation |
| --- | --- | --- |
| Engineering | **APPROVED** | Full regression, launcher lifecycle, deterministic build, compilation, diff integrity, and scoped documentation review pass. |
| Scientific | **APPROVED** | Identifier/DC1–DC4, serializer/runtime, direct minimize, threshold, and ULP coverage pass; production-performance behavior remains unmeasured. |
| Security | **APPROVED** | Headers/CSP, upload, session, cache, download, expiry, integrity, and rate-limit paths pass; no deployment or penetration test occurred. |
| UI/UX | **APPROVED WITH DEFERRED LIMITATIONS** | DC4.5 semantic no-JS, card state, static styling, and source-CSP evidence pass; browser/AT checks remain deferred. |

## Supplemental diagnostic

`python scripts/preflight_checks.py` exited **1**. Its fixed 50-line core-module policy flags existing `cli.py`, `config.py`, `data.py`, `runtime.py`, `serialization.py`, and `shared.py`; it also searches templates for CSP text although CSP is applied through tested Flask response headers. This legacy diagnostic is not a release acceptance command and required no safe fix. The dedicated security and full suites above pass.

## Explicitly deferred, non-blocking browser evidence

No browser-rendered verification was run for browser/AT (screen reader), zoom, reflow, keyboard operation, offline behavior, or load performance. Static-source and Flask test-client evidence do not establish browser CSP enforcement, deployment/proxy behavior, or penetration-test coverage.
