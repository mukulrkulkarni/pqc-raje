# Launcher engineering review

**Reviewer:** Innovium prepared Code specialist, candidate v1  
**Date:** 2026-10-22  
**Verdict:** approved for the bounded launcher scope.

## Review scope

- `scripts/dev_local.py`
- `tests/test_dev_local.py`
- Launcher instructions in `README.md`, `docs/GETTING_STARTED.html`, and `docs/runbook/debugging.md`
- `docs/decisions/launcher-documentation-notes.md`

## Findings

- The launcher binds only `127.0.0.1`, avoiding unintended network exposure.
- It validates integer port ranges and rejects identical service ports before server creation.
- Bind failures report the affected service and exit before startup URLs print.
- It starts website and Flask server threads only after both listeners bind.
- It reports effective URLs, handles Ctrl+C and Windows console break, shuts down both services, and joins threads.
- A child-service exception or unexpected exit stops the peer and returns a nonzero result.
- The Flask reloader is not enabled, so this launcher creates no reloader child process.

## Evidence reviewed

- `python -m pytest -q tests/test_dev_local.py` — 7 passed in 6.06s.
- `python -m compileall -q scripts/dev_local.py tests/test_dev_local.py` — passed.
- `git diff --check -- ...` for launcher-scoped files — passed; only CRLF conversion warnings appeared.

## Limitations

- The tests use loopback HTTP and simulated child failure only.
- Browser usability, offline behavior, assistive technology, load, and deployment checks remain deferred and non-blocking.
