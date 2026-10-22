# v0.1 executive summary

**Decision:** **Release with limitations.** Local v0.1 verification passed after the committed launcher implementation (`3e32ed6`). No v0.1 Git tag was created.

## Release evidence

- **Engineering:** APPROVED. Full regression passed: **947 tests in 18.91s**. The website build, Python compile check, and Git whitespace checks passed.
- **Scientific:** APPROVED. DC1–DC4 contract, identifier, serializer, runtime, direct minimize, threshold, and ULP coverage passed (**72 focused tests**).
- **Security:** APPROVED. Headers/CSP, uploads, cache, session-bound downloads, integrity, expiry, and rate-limit paths passed (**67 focused tests**).
- **UI/UX:** APPROVED WITH DEFERRED LIMITATIONS. DC4.5 card-state, semantic no-JS, focus/style, static website, and source CSP checks passed (**249 focused tests**).
- **Launcher:** APPROVED. Seven lifecycle checks passed, including startup, clear URLs, invalid and occupied ports, peer failure shutdown, and no residual listeners.

## Scope control

This verification adds records only. It creates no feature changes and no Git tag. Documentation confirms `python scripts/dev_local.py` and configurable ports. Release records supersede stale launcher-pending plan wording without rewriting unrelated project UI.

## Deferred non-blocking limitations

Browser/AT and screen-reader behavior, zoom, reflow, keyboard operation, offline behavior, and load performance were not browser-rendered tested. The verification also does not prove production proxy configuration, browser CSP enforcement, external-client compatibility, or penetration resistance.

The legacy `scripts/preflight_checks.py` exited 1 because its outdated source-length and template-text heuristics do not match the tested architecture. This diagnostic is documented and does not override passing dedicated tests.

See [release notes](v0-1-release-notes.md) and [verification evidence](v0-1-release-verification-evidence.md).
