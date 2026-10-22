# DC5 security, cache, runtime, and route evidence

**Evidence date:** 2026-10-22
**Scope:** DC5 evidence remediation only. No application source or test logic changed.

## Exact executed commands and results

| Evidence area | Exact command | Result |
| --- | --- | --- |
| Full suite | `python -m pytest tests -q` | `932 passed in 8.62s` |
| Security, cache, runtime, and workflow routes | `python -m pytest tests/test_security.py tests/test_security_headers.py tests/test_runtime.py tests/test_result_cache.py tests/test_app_workflow.py -q` | `57 passed in 1.57s` |
| Identifier, selection-boundary, serialization, and IEEE-754 coverage | `python -m pytest tests/test_dc2_identifier_migration.py tests/test_dc45_criteria_cards.py tests/test_serialization.py tests/test_dc3_minimize_transform.py -q` | `54 passed in 0.90s` |
| Syntax and whitespace | `python -m compileall -q electre3 app tests && git diff --check && git diff --cached --check` | exit code `0` |

No browser automation, browser rendering, assistive-technology, zoom, reflow, or offline test was executed or inferred.

## CSP and response-header evidence

`tests/test_security_headers.py` verifies:

- `/preview/<registered-upload>` returns `200` with `Content-Security-Policy` containing `default-src 'none'`.
- `/app/` returns `200`, links `/static/style.css`, contains no `<script`, and has CSP `style-src 'self' 'unsafe-inline'` with no `script-src` directive.
- `/static/style.css` returns `200` with `text/css`, and receives the same application CSP.
- Preview responses include `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, `Cross-Origin-Opener-Policy: same-origin`, and `Cross-Origin-Resource-Policy: same-origin`.
- A nonexistent preview returns `404` with CSP, and a preview confirmation POST also has CSP.

The executed tests validate Flask test-client responses. They do not prove browser enforcement.

## Route-level download, session, token, and cache evidence

`tests/test_app_workflow.py` and `tests/test_result_cache.py` verify:

- Positive: criteria confirmation, CSV preview, confirmed compute, and `/app/download/<token>` return a JSON attachment.
- Positive: download bytes end in a newline and response headers include `Cache-Control: no-store`, `X-Content-Type-Options: nosniff`, exact `Content-Length`, and `Content-Disposition: attachment; filename="ranking-result.json"`.
- Negative: compute before preview or without confirmation returns `400`; unknown download tokens return `404`.
- Negative: infeasible work returns `422` before cache publication; timeout returns `504` and no download URL.
- Edge: cache rejects payloads above 32 MiB, rejects invalid session/payload values, detects tampered part checksums, expires entries, and applies the successful-download rate limit under 40 concurrent attempts.
- Session: the application lifetime is `1800` seconds; the signed session contains opaque workflow/download identifiers and does not store matrix, criteria, or result token payloads.
- Token binding: opaque tokens have length at least 32, are session-bound, are latest-result-only, and fail after cache recreation.

## Identifier safety evidence

`tests/test_dc2_identifier_migration.py` verifies:

- Positive: headered and headerless CSV paths preserve `A-001` and `0012`; downloads preserve source identifiers.
- Negative: malformed row width, `NaN`, out-of-range score, and blank identifier are rejected.
- Negative: identifiers longer than 50 characters, control characters, and duplicates are rejected.
- Edge: a 50-character identifier is accepted; `=2+2` and `東京,"ID"` survive JSON, CSV parsing, and the cache as bytes.
- Injection: an HTML-like identifier/header is escaped in preview and result HTML; literal `<img src=x onerror=1>` is absent from output.

## Positive, negative, and edge coverage summary

- **Positive:** full ranking workflow, CSP headers, stylesheet delivery, valid cache download, identifier propagation, selected-card form submission, and normal direct minimize ranking.
- **Negative:** traversal/special-character upload IDs, invalid criteria, absent preview/confirmation, unknown token, over-size payload, integrity failure, out-of-range scores, malformed selected cards, invalid identifiers, and non-finite/boundary score cases.
- **Edge:** opaque-session token binding, cache expiry/rate limiting/concurrency, 32 MiB size boundary, exact 50-character identifiers, Unicode/formula-like identifiers, 2/8 selected criteria, and IEEE-754 subnormal/threshold-ULP ranking cases.

## Limitations

These local tests establish only the covered source and Flask test-client behaviors. They do not establish deployment configuration, browser CSP enforcement, browser/AT keyboard behavior, zoom, reflow, offline operation, performance, or external-client compatibility.
