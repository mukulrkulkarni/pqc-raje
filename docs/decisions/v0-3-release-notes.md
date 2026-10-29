# v0.3.0 Release Notes

**Status:** Draft for review. No tag created. No remote operations performed.

## SemVer classification

`v0.3.0` is a minor release after `v0.2.1`. It adds backward-compatible link-contract hardening, static asset packaging, examples delivery, and launcher diagnostics. Existing tags remain immutable.

## Changes since v0.2.1

### W3 — Link contract hardening

- Added static and Flask URL namespace checks.
- Added resolver-aware link, fragment, asset, traversal, and open-redirect tests.
- Preserved source ownership and generated tutorial rules.
- Evidence: `docs/decisions/w3-link-contract-notes.md`; commits `5bdd403`, `efb68e6`, `c3d3d79`.

### W4 — Static asset packaging

- Added `docs/static-asset-manifest.json`.
- Packaged approved `examples/assets_priority` files for the static website.
- Made generated example synchronization deletion-safe.
- Added missing-source, extra-source, path, and stale-output tests.
- Evidence: `docs/decisions/w4-documentation-notes.md`; commit `d1608e8`.

### Launcher hardening

- Added root and port preflight checks.
- Added serving-root health checks.
- Added runtime identity output.
- Added deterministic port-conflict and child-failure handling.
- Preserved one-command startup and graceful shutdown.
- Evidence: `docs/decisions/launcher-hardening-notes.md`; commits `bfaaffa`, `c7e72ed`.

## Verification

- W3 focused and full evidence: recorded in W3 notes.
- W4 focused tests: 11 passed; full suite at that checkpoint: 1,135 passed.
- Launcher focused tests: 9 passed; full suite at that checkpoint: 1,137 passed.
- Preflight, compilation, and diff checks passed for the scoped changes.

## Limitations

Browser rendering, assistive technology, zoom, reflow, keyboard, offline, and load-performance evidence remain deferred and non-blocking. The launcher uses local development servers and is not a production deployment mechanism. Remote publication is user-only.

## Tag policy

Preserve `v0.2.1`. Create an annotated local `v0.3.0` tag only after Engineering and Scientific review of these notes. Do not move or delete existing tags.
