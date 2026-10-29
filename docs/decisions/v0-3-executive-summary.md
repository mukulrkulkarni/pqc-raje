# v0.3.0 Executive Summary

**Status:** Draft for review. No tag created.

v0.3.0 is a minor release after v0.2.1. It adds backward-compatible link safety, static example packaging, deletion-safe website synchronization, and stronger local launcher diagnostics. Existing release tags remain immutable.

W3 adds a canonical link contract and tests for static and Flask namespaces, fragments, assets, traversal, and open-redirect risks. W4 adds a source manifest for approved examples and prevents stale generated assets. Launcher hardening validates ports and serving roots, reports runtime identity, checks health endpoints, handles child failures, and shuts down both local services together.

Evidence is recorded in the W3, W4, and launcher notes. The release uses focused tests, full regression tests, compilation, static builds, preflight checks, and diff checks. Engineering, Scientific, Security, and UI/UX approvals are required where applicable before tagging. Scientific review confirms that the release does not change ranking, input, or scientific behavior.

The release remains local-development focused. Browser rendering, assistive technology, zoom, reflow, keyboard, offline, and load-performance evidence remain deferred and non-blocking. Remote publication is user-only. Existing v0.1, v0.2.0, and v0.2.1 tags remain unchanged.

The recommended tag is `v0.3.0`, created only after review approval. The release does not claim production deployment readiness or browser-verified accessibility.
