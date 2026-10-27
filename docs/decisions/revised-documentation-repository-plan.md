# Revised Documentation and Repository Plan

**Status:** Plan only. No page or application edits.

## Finding map

| Finding | Priority | Milestone | Remedy |
|---|---:|---|---|
| Legacy JSON routes and wrong debugging gate | P0 | D3 | Label compatibility routes; correct `/app` guidance. |
| CLI output explanations diverge | P1 | D4 | Reconcile direct CSV and NumPy labels. |
| `/app` lacks escape navigation | P1 | D4 | Document current limitation; separately approve code change if needed. |
| Duplicated style tokens | P2 | D5 | Define shared token ownership and normalize sources. |
| Criteria defaults lack threshold guidance | P2 | D5 | Add guidance without changing behavior. |
| Bare module 404 | P3 | D6 | Define index recovery link. |
| Debug mode remains public | P3 | D6 | Document or separately remove. |
| Release tree and generated ownership unclear | High | D7 | Define minimal release and source/generated policy. |
| Branch and rollback guidance conflicts | High | D7 | Define local branches, append-only rollback, user-only upstream. |
| Browser/AT/zoom/reflow/offline/load evidence deferred | Deferred | D8 | Preserve explicit non-blocking labels. |

## Ordered documentation phases

- **D3:** legacy routes, debugging correction, current-vs-planned labels.
- **D4:** CLI output reconciliation and workflow navigation guidance.
- **D5:** style-token and criteria guidance.
- **D6:** 404 recovery and debug-mode disposition.
- **D7:** repository release set, generated ownership, local branch/rollback/upstream policy.
- **D8:** reproducibility, links, static evidence, and deferred-browser audit.

Each phase requires source evidence, positive/negative/edge evidence where behavior is claimed, a checkpoint, required reviewer gates, a focused local commit, and clean-tree verification. No agent performs upstream Git operations.

## Source authority

Implementation and executed tests are authoritative for behavior. Approved decisions define policy. Tutorials and runbooks explain behavior. Website pages summarize and link; they do not duplicate changing numeric contracts. Generated pages must be rebuilt from authoritative sources.

Mark content `CURRENT`, `PLANNED`, or `DEFERRED/NON-BLOCKING`. Historical notes remain traceable and are not silently deleted.

## Release and maintenance

D7 defines a minimal user release tree separate from tests, checkpoints, decisions, audits, snapshots, raw attachments, and build artifacts. It defines generated website ownership, dependency/version manifest, rollback using local append-only revert, and local branch workflows.

Agents may inspect local Git state. Only the user may fetch, pull, push, mutate remote branches/tags, merge/rebase with remote, or force-push.

## Review gates

Engineering reviews code/routes/repository claims. UI/UX reviews user journey and material layout. Scientific reviews formulas, examples, rankings, and terminology. PI consolidates and commits plan/page artifacts. Browser evidence remains deferred and non-blocking.
