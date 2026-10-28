# Launcher hardening continuation

**Status:** complete and locally verified on 2026-10-28.

## Target and current status

The launcher binds the generated website and Flask app to loopback only. Before it starts, it checks required website and application roots, rejects identical or invalid ports, and checks occupied loopback ports. It reports the owning PID when the operating system exposes it. After both listeners start, it checks the required website pages and `/app/`, then prints repository, serving roots, ports, and local commit identity.

Run from the repository root:

```bash
python scripts/dev_local.py
```

Use alternative distinct ports when defaults conflict:

```bash
WEBSITE_PORT=8100 APP_PORT=5100 python scripts/dev_local.py
```

Windows Command Prompt:

```bat
set WEBSITE_PORT=8100&& set APP_PORT=5100&& python scripts\dev_local.py
```

Use `Ctrl+C` once to close both local services. Startup errors print to standard error and do not print service URLs.

## Test inventory and exact results

- Positive: temporary loopback website and app start; health endpoints return 200; identity and URLs print; Ctrl+C closes both listeners.
- Negative: occupied website port fails before URL output and reports a PID or `unknown`; invalid values (`nope`, `0`, `65536`) fail deterministically; matching ports fail before server creation.
- Edge: missing website pages or `app/__init__.py` report each required path; HTTP 404 health responses report all five endpoints; a child-service exception stops its peer.
- Focused: `python -m pytest -q tests/test_dev_local.py tests/test_launcher_preflight.py tests/test_launcher_lifecycle.py` — `9 passed in 7.22s`.
- Full: `python -m pytest -q` — `1137 passed in 57.66s`.
- Compile: `python -m compileall -q scripts\dev_local.py scripts\launcher_cli.py scripts\launcher_health.py scripts\launcher_lifecycle.py scripts\launcher_preflight.py scripts\launcher_runtime.py scripts\launcher_shutdown.py scripts\launcher_startup.py tests\test_dev_local.py tests\test_launcher_preflight.py tests\test_launcher_lifecycle.py tests\launcher_test_support.py` — passed.
- Diff: `git diff --check -- <launcher-hardening paths>` — passed; only Git CRLF conversion warnings occurred.
- Reproducibility: the focused command was rerun after refactoring, with no persistent services; it passed `9 passed in 7.22s`.

## Reviews

- **Engineering — approved.** The launcher validates configuration before construction, shuts peer services after failures, checks serving roots and endpoint health, and prints actionable runtime identity.
- **Security — approved.** Both services bind `127.0.0.1`; input ports are range-checked; subprocess calls use fixed argument lists; no remote operation, credential, shell interpolation, or path traversal was introduced.
- **UI/UX — approved.** Startup output presents identity first, then exact service URLs and a single shutdown instruction. Configuration, startup, runtime, health, and shutdown errors identify the failed condition without false success URLs.

## 50-line policy

Every new or changed Python file is at most 50 physical lines except the pre-existing documented exception `scripts/build_website.py`. The command-line line count was checked for all launcher-hardening Python files. The rule is scoped to this approved change; it is not project-wide proof.

## Limitations

PID lookup can return `unknown` when platform tooling cannot identify a listener. Health checks cover local HTTP reachability and intended roots, not browser rendering. Browser reflow, zoom, keyboard navigation, offline behavior, assistive technology, load testing, and deployment behavior remain deferred and non-blocking. The launcher uses development servers and is not a production deployment mechanism.
