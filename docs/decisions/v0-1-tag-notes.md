# v0.1 Git tag notes

**Date:** 2026-10-22
**Release status:** **released with limitations**

## Tag decision

Create annotated tag `v0.1` from the documented final successor to release-verification commit `cff0f40`. The successor contains only the v0.1 tag evidence records required by the release-tag chunk.

## Verified release basis

- `cff0f40` records v0.1 release verification after launcher commit `3e32ed6`.
- Full regression evidence: **947 passed in 18.91s**.
- Engineering, Scientific, and Security reviews: **APPROVED**.
- UI/UX review: **APPROVED WITH DEFERRED LIMITATIONS**.
- The worktree was clean before creating tag evidence.

## Released limitations

Browser-rendered and assistive-technology checks remain deferred and non-blocking. Deferred checks include screen-reader, zoom, reflow, keyboard, offline, and load-performance verification. This release does not establish browser CSP enforcement, deployment/proxy configuration, external-client compatibility, penetration-test coverage, or production performance.

## Tag annotation

`v0.1` is released with the documented limitations above.
