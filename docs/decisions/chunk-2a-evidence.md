# Chunk 2A implementation evidence

## Scope

Implemented only the server-rendered ranking workflow under `/app/`.

- `GET /app/` provides criteria JSON or structured-form entry.
- `POST /app/confirm-inputs` applies `electre3.shared.validate_criteria`.
- `POST /app/preview` validates matrix input, CSV mapping, scores, and missing-value approval.
- `POST /app/compute` requires preview plus explicit confirmation, then calls `electre3.shared.compute_validated_ranking`.
- Results show the top ten identifiers and raw adapter net-flow scores.

## Preserved and excluded work

- Docs routes and pre-existing JSON compatibility routes remain registered and tested.
- No serializers, cache, downloads, benchmarks, or split artifacts were added.
- `app/templates/config.html` no longer declares an unsafe `script-src` policy.

## Validation evidence

Executed on 2026-10-21:

```text
python -m pytest tests/test_app_workflow.py tests/test_preview_gate.py tests/test_security.py tests/test_security_headers.py tests/test_docs_routes.py -q
235 passed

python -m compileall app electre3
completed successfully

findstr /s /i /n "<script onload= onclick= onchange= onsubmit=" app\templates\app_*.html
No script tags or inline handlers found.
```

The focused workflow tests cover successful flow, preview and confirmation gates, headers, missing-value approval, invalid criteria, out-of-range scores, CSP, no-script responses, and docs/compatibility regressions.
