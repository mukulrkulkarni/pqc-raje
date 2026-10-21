# Chunk 2D Documentation Notes

**Purpose:** Record the bounded in-process result cache and `/app` download implementation. This note does not claim multi-worker persistence, runtime benchmark changes, ranking changes, or JavaScript.

## Implemented

- `app/services/result_cache.py` stores one latest result in process memory.
- The cache accepts at most 32 MiB for the current result.
- Each part is at most 16 MiB. `split_artifact` creates ordered parts and a manifest.
- The manifest contains byte lengths, serializer version, per-part SHA-256 values, and full SHA-256 value.
- The cache validates deterministic reassembly before publication and before download.
- A 30-minute monotonic-clock TTL invalidates cached results.
- A new opaque cryptographic token binds one cached result to one small session identifier.
- The signed session cookie contains only the opaque session identifier. It contains no result bytes, matrix data, tokens, criteria, or uploads.
- The process keeps only one result. A later result replaces the prior result. A restart creates an empty cache and invalidates all prior tokens.
- Each session can complete 30 successful downloads in a rolling 60-second window. Invalid, expired, foreign-session, and rate-rejected requests do not count.
- `/app/download/&lt;token&gt;` returns canonical JSON bytes only after token, session, expiry, rate, and checksum validation.
- The download sends `Cache-Control: no-store`, `Pragma: no-cache`, attachment disposition, exact content length, JSON media type, and the existing security headers.
- The `/app` results page has one ordinary HTML download link. No JavaScript exists in this chunk.
- Existing docs and compatibility routes remain registered.

## Verified

The tests cover cache bounds, a result larger than one 16 MiB part, latest-only replacement, restart invalidation, opaque token distinction, foreign-session rejection, TTL expiry, successful-only rate limits, concurrency, checksum tampering, unknown tokens, exact bytes, safe headers, and compatibility routes.

Commands executed for this chunk:

```text
python -m pytest tests/test_result_cache.py tests/test_app_workflow.py tests/test_serialization.py tests/test_shared_contract.py tests/test_cli_run.py -q
python -m compileall electre3 app tests
python -m pytest tests/test_app_workflow.py tests/test_serialization.py -q
python -m pytest tests/test_runtime.py tests/test_shared_contract.py tests/test_serialization.py tests/test_cli_run.py tests/test_accumulator.py tests/test_accumulator_deep.py -q
```

The final checkpoint records the command results and commit evidence.

## Planned

- A multi-worker or persistent deployment needs a shared cache and atomic rate store. This single-worker implementation intentionally does not provide that behavior.
- Deployment configuration must provide a non-development Flask secret key.
- A user interface for selecting formats or split parts is not implemented. The route serves the canonical JSON artifact.

## Debugging guidance

A 404 response means the token is unknown, expired, replaced, from another session, or lost after restart. A 429 response means the session completed 30 downloads during the previous minute. A 410 response means checksum validation failed. Treat a 410 result as invalid. Do not retry by reading raw cache fields.

## Tutorial-writing rules

Use ASD-STE100 plain language. Use semantic HTML math such as `<var>N</var>` and `<sup>2</sup>` when required. Do not add KaTeX, JavaScript, a build step, claims about persistence, claims about multiple workers, or unverified performance claims.
