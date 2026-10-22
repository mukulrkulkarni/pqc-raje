# v0.1 release notes

**Date:** 2026-10-22
**Status:** **released with limitations**
**Release boundary:** Local-source v0.1 verification after launcher commit `3e32ed6`. No Git tag was created.

## Included

- One-command local launcher: `python scripts/dev_local.py`.
- Companion website and Flask application on separate loopback ports.
- DC1–DC4.5 contracts, identifier preservation, scientific ranking behavior, serializer/runtime behavior, static no-JS UI, and security/session/download controls.
- Release verification records in this decision set.

## Verification result

The full suite passed: **947 passed in 18.91s**. Launcher lifecycle checks passed: **7 passed**; the launcher starts both services, prints URLs, rejects invalid/conflicting ports, stops peers after service failure, and leaves no listeners after shutdown. Focused contracts/science (**72**), security/session (**67**), UI/static/CSP/no-JS (**249**), and workflow-edge (**72**) suites passed. The website build, `compileall`, and Git diff checks exited zero.

README documents the launcher and port overrides. Existing Getting Started and runbook material remains consistent with local launch and deferred browser scope. A stale planning statement that described launcher work as pending is superseded in these release records; unrelated project UI text was not rewritten.

## Limitations

Browser-rendered browser/AT, screen-reader, zoom, reflow, keyboard, offline, and load checks remain explicitly deferred and non-blocking. This release does not establish browser CSP enforcement, deployment/proxy configuration, external-client compatibility, penetration-test coverage, or production performance.

See [verification evidence](v0-1-release-verification-evidence.md) for exact commands, positive/negative/edge evidence, and a legacy preflight diagnostic that remains non-acceptance.
