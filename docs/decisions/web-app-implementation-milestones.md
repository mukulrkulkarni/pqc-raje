# Local ELECTRE III Web-App Implementation Milestones

**Status:** Planning only. No implementation authorization is included.
**Contracts:** `docs/decisions/web-app-design-meeting-report.md`

## Milestone 1 — Shared contracts and evidence

**Owner:** Code Agent; Scientific Critic and Engineering Critic review.

**Deliverables:**
- Immutable validated-input model.
- Strict criteria and matrix parser.
- Shared CLI/web compute adapter.
- Identifier/header mapping.
- Shared canonical result model.

**Acceptance tests:**
- Required fields, strict booleans, max eight criteria.
- Weights sum to one and scores lie in `[0,1]`.
- Headered/headerless mapping and missing-cell approval.
- Finite values, shape, row, byte, and format limits.
- CLI and web call the same adapter.

**Stop conditions:** contract mismatch, missing evidence, or parser bypasses.

## Milestone 2 — Exact computation and serialization

**Owner:** Code Agent; Scientific Critic and Engineering Critic review.

**Deliverables:**
- Fixed-order accumulation preserving byte identity across block sizes.
- Canonical ranking, score, CSV/JSON/NPY, and manifest serializers.
- Runtime benchmark harness.

**Acceptance tests:**
- Block sizes 1, prime values, 1,000, 5,000, 10,000, and sizes above N.
- Exact score/ranking equality and byte equality.
- Benchmarks at N = 100, 500, 1,000, 5,000, 10,000, 15,000; C = 4, 8.
- Feasibility estimate rejects >300 seconds.

**Stop conditions:** byte identity fails, memory exceeds O(N) contract, or benchmark exceeds hard limits.

## Milestone 3 — Server-rendered workflow

**Owner:** Code Agent; UI/UX Redesign Agent and Security Lead review.

**Deliverables:**
- `/app/`, `/app/confirm-inputs`, `/app/preview`, `/app/compute`.
- Column mapping table and actionable errors.
- Missing-value approval checkbox and bounded replacement field.
- Semantic HTML equations and accessible result table.
- App CSP correction; no app JavaScript.

**Acceptance tests:**
- Preview required before compute.
- Header/missing-value/error recovery flows.
- Keyboard traversal and semantic labels.
- No scripts or inline handlers in app responses.
- Docs routes remain functional under separate CSP.

**Stop conditions:** accessibility failure, CSP conflict, route regression, or unescaped user output.

## Milestone 4 — Cache and split downloads

**Owner:** Code Agent; Security Lead and Engineering Critic review.

**Deliverables:**
- Latest-only process-memory cache.
- Session-bound opaque tokens.
- 32 MiB total and 16 MiB per-artifact limits.
- 30-minute TTL and 30 successful downloads/session/minute.
- Ordered split artifacts, manifest, lengths, and SHA-256 checksums.
- 30-minute session metadata policy.

**Acceptance tests:**
- Replacement, expiry, restart invalidation, malformed/unknown/session-mismatched tokens.
- Exact cached bytes and headers.
- Artifact splitting and checksum reassembly.
- Concurrent lookup/replacement safety.
- No result bytes or tokens in signed cookies.

**Stop conditions:** cache bound violation, token ambiguity, race, or partial-result caching.

## Milestone 5 — Release gate

**Owner:** Engineering Critic; Security Lead, Scientific Critic, and UI/UX review.

**Deliverables:**
- Full regression suite.
- Evidence-linked documentation.
- Compatibility and rollback notes.
- Technical and executive release recommendation.

**Acceptance tests:**
- Core, web, security, scientific, accessibility, offline, serializer, and benchmark suites pass.
- No unresolved gap-register blockers.
- Runtime, cache, upload, and session limits are enforced.

**Stop conditions:** any critical test failure, missing evidence, scope expansion, or unapproved dependency.
