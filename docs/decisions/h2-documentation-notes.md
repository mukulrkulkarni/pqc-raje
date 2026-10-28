# H2 Architecture Hotfix notes

## Scope and decisions

- The supported browser workflow remains `/app/`; legacy preview and compute endpoints remain compatibility routes. The debugging runbook now states both status behavior and migration boundary. H2 removes no route.
- `scripts/preflight_checks.py` now checks CSP on Flask test-client responses. Templates do not need literal CSP text because `app/__init__.py` applies route-scoped response headers.
- `docs/GENERATED_DOCUMENTATION.md` names tutorial sources, generated targets, builder ownership, stale-output handling, and release-resource boundary. The preflight check rejects missing or stale declared tutorial output.
- Rollback guidance now requires a clean-tree inspection and recovery reference before local history changes. Prefer revert for shared history. All upstream actions remain user-only.

## Evidence and limits

H2 adds positive, negative, and edge checks in `tests/test_h2_hotfixes.py`. Browser, assistive-technology, zoom, reflow, offline, and load evidence remain deferred and non-blocking. H2 does not alter generated page layout or navigation, so UI/UX review is not required.
