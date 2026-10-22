# Launcher documentation notes

**Status:** implemented and test-verified locally on 2026-10-22.

## One-command local launch

From the repository root, run:

```bash
python scripts/dev_local.py
```

The launcher binds the companion website to `http://127.0.0.1:8000/` and the Flask app to `http://127.0.0.1:5000/app/`. It prints the effective URLs after both listeners bind. Press `Ctrl+C` once to request shutdown of both services.

Set distinct loopback ports before the command when defaults conflict:

```bash
WEBSITE_PORT=8100 APP_PORT=5100 python scripts/dev_local.py
```

Windows Command Prompt equivalent:

```bat
set WEBSITE_PORT=8100&& set APP_PORT=5100&& python scripts\dev_local.py
```

`WEBSITE_PORT` and `APP_PORT` must be integers from 1 through 65535 and must differ. A bind conflict or invalid configuration exits deterministically before URLs print.

## Source evidence

- Implementation: `scripts/dev_local.py`.
- Lifecycle tests: `tests/test_dev_local.py`.
- User-facing instructions: `README.md`, `docs/GETTING_STARTED.html`, and `docs/runbook/debugging.md`.
- Required implementation checkpoint: `out/launcher-checkpoint.json`.

## Test categories and results

The launcher suite uses temporary loopback ports and short-lived subprocesses; it needs no manually managed services.

- Positive: starts website and Flask endpoints, prints configured URLs, and responds over HTTP.
- Shutdown/no orphan: sends `Ctrl+C`, requires a zero exit, and confirms both ports refuse new connections.
- Negative: occupied website port and invalid port values return deterministic configuration/startup errors.
- Edge: identical configured ports are rejected before servers start.
- Child failure: a simulated service exception causes peer shutdown and a nonzero result.

Record exact command output in the implementation checkpoint before commit.

## Deferred browser limitations

Browser reflow, zoom, keyboard navigation, offline behavior, screen-reader/assistive-technology behavior, and load testing remain deferred and non-blocking. Launcher tests verify process lifecycle and HTTP reachability only; they do not provide browser usability evidence.
