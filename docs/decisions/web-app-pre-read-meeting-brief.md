# Web-App Design Meeting Brief

**Status:** Pre-read only. The design meeting requires separate approval.
**Source:** `attachments/web-app-requirements.txt`
**Evidence register:** `docs/decisions/web-app-pre-read-gap-register.md`

## What the pre-read establishes

### Scope

- Local Flask web app on `127.0.0.1`.
- ELECTRE III credibility computation with raw net-flow ranking.
- CSV/NumPy input, criteria JSON, preview, confirmation, ranking view, and downloads.
- Blockwise computation without NxN persistence.
- Security, determinism, byte-identity, and bounded-cache requirements.

### Current evidence

- Core ranking: `electre3/ranking.py`.
- Blockwise accumulation: `electre3/block.py`, `electre3/accumulator.py`.
- Matrix loading: `electre3/data.py`.
- CLI: `electre3/cli.py`, `electre3/cli_run.py`.
- Preview service: `app/services/preview.py`.
- Upload security registry: `app/services/security.py`.
- Current compute route is a placeholder: `app/routes/compute.py`.
- Existing tests cover core ranking, preview gates, security headers, and routes, but not the target web compute/cache contract.

## What will be discussed in the meeting

1. **Scientific contract**
   - Confirm criteria schema, direction handling, thresholds, normalization policy, score reporting, ties, and CLI/web numerical equivalence.
   - Review whether math content needs KaTeX, pre-rendered KaTeX, server-rendered MathML, SVG, or plain accessible notation.

2. **No-JavaScript decision**
   - Define scope: ranking app only, or documentation pages too.
   - Compare server-rendered HTML, pre-rendered math, MathML, SVG, and limited JS.
   - Evaluate CSP, offline behavior, keyboard flow, screen readers, maintenance, and testability.

3. **Input and UX flow**
   - Decide canonical route flow and migration from existing `/preview/<upload_id>` and `/compute/*` routes.
   - Define header detection, identifier mapping, missing-cell checkbox, errors, and preview evidence.

4. **Security and storage**
   - Set upload byte/row limits, lifecycle, path containment, cache limits, opaque tokens, TTL, eviction, restart behavior, and worker scope.

5. **Engineering plan**
   - Select module boundaries, shared adapter, serializers, test matrix, milestone order, and implementation stop conditions.

## Required meeting outputs

- Technical recommendation with evidence and rejected alternatives.
- Executive recommendation with decision, benefits, risks, and required user choices.
- Closed/deferred gap register with evidence links.
- Architecture and route/data-flow diagram.
- Data contract and serialization contract.
- KaTeX/no-JS decision with accessibility and security rationale.
- Milestones with owners, acceptance tests, and stop conditions.

## Meeting stop conditions

The meeting must stop without an implementation plan if:

- Scientific or security critics identify an unresolved blocker.
- KaTeX/no-JS scope remains contradictory.
- CLI/web equivalence lacks a canonical input/output contract.
- Upload or cache limits lack measurable values and tests.
- A route migration would break existing tested behavior without a rollback plan.
- Required evidence cannot be inspected or tests cannot be defined.

## Audience outputs

### Technical audience

Receives route contracts, module boundaries, equations, data schemas, threat controls, test cases, evidence links, and implementation milestones.

### Executive audience

Receives the recommended product scope, no-JS/KaTeX decision, delivery risks, security/scientific gates, milestone boundaries, resource request, and explicit decisions required.
