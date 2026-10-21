# D2 Documentation Structure Plan

**Status:** Plan only. No final pages are drafted.

## Purpose and authority

Use one information architecture for the CLI, modules, local web app, and companion website. Use current source and passing tests for behavior. Use requirements and decisions for approved contracts. Label planned behavior separately.

**Source authority:** implementation and tests → approved requirements/decisions → tutorials/runbooks → website summaries. Generated website pages must not become a second source of truth.

## Audiences

- CLI users: install, commands, outputs, errors.
- Module users: function contracts, equations, validation, examples.
- Web users: criteria, matrix, preview, compute, results, recovery.
- Engineers: architecture, tests, limits, cache, debugging.
- Evaluators: purpose, evidence, trust boundaries, local operation.

## Four-phase onboarding

| Phase | Goal | Deliverables |
|---|---|---|
| 1. Working in 10 minutes | Complete one real ranking run | Prerequisites, setup, one command, expected output, verification. |
| 2. Build a real thing | Construct an end-to-end scenario | Input, criteria, transformation, run, one error case, full result. |
| 3. Mental model | Explain daily concepts | Diagram, core operations, gotchas, comparison table. |
| 4. Reference | Support lookup | Commands, APIs, limits, errors, links back to tutorials, changelog. |

Use one realistic Asset ID/IP scenario across CLI and web. Do not lead with theory. Keep examples copyable. State “why” after “how.”

## Information architecture and placement

1. **Root README:** purpose, prerequisites, install, first success, CLI/web choice, documentation map.
2. **Getting Started:** Phase 1 entry point with CLI and `/app/` paths.
3. **CLI guide:** strict input contract, converter-first workflow, flags, outputs, errors, debugging.
4. **Web guide:** `/app/` journey, header mapping, preview, missing-value approval, feasibility, results, cache/download recovery.
5. **Concepts:** ELECTRE III notation, blockwise computation, net flow, ties, scientific caveats.
6. **Module reference:** concise entries linked to Phase 2 and source functions.
7. **Operations runbook:** installation, local launch, test commands, limits, cache/session behavior, troubleshooting.
8. **Testing guide:** methodology and category inventory.
9. **Companion website:** orientation and links; do not duplicate numeric contracts.

Use Markdown for versioned narrative, CLI, runbooks, and references. Use semantic HTML for `/app` guidance. Use website generator sources for static pages. Label snapshots as historical and keep them out of user navigation.

## Cross-links and layout

The landing page routes to all four phases. Each phase is self-contained. Reference entries link back to the tutorial step that introduces them. Keep “See also” links to one level. Add a route/link manifest for Markdown, HTML, website, fragments, and assets.

Use semantic headings, labels, tables with scope, visible errors, keyboard-friendly forms, and semantic math (`var`, `sub`, `sup`, entities). Reject KaTeX and app JavaScript. UI/UX approval is required for material navigation or layout changes.

## Testing and evidence plan

Every page batch records positive, negative, and edge evidence where applicable. Cover unit/example execution, integration, scientific correctness, security, UI/accessibility, performance, serialization/cache, end-to-end, link, and offline checks. Report command, revision, result, limitation, and source evidence. Collection is not execution.

## Governance and stop conditions

1. PI approves this plan and authority map before drafting.
2. Technical Document Writer drafts one bounded page group.
3. Scientific Critic reviews equations, thresholds, net flow, ties, examples, and claims.
4. Engineering Critic reviews commands, routes, limits, tests, links, and current behavior.
5. UI/UX reviews material layout/navigation changes.
6. Code Agent places approved content into pages, adds tests, and preserves generated-source rules.
7. Checkpoint, notes, focused commit, and clean tree are required.

Stop when source authority, current/target labels, test evidence, link integrity, accessibility evidence, offline evidence, or required reviewer approval is missing.

**Evidence basis:** D1 artifacts (`docs/decisions/d1-documentation-*.md`), Chunk 1–2E notes, `web-app-requirements.txt`, `app/`, `electre3/`, `tests/`, `docs/`, and `website/`.