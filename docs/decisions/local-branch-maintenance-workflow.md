# Local Branch Maintenance Workflow

**Status:** Proposal only. No remote operation is performed by agents.

## Permanent upstream rule

Agents may inspect local Git state only. Agents must never fetch, pull, push, create/delete/mutate remote branches or tags, merge or rebase against remote refs, or force-push. The user performs every upstream operation.

## Local branches

- Keep `main` as the local release/integration branch.
- Use short-lived `local/<milestone>` branches for approved work.
- Use focused commits per accepted chunk.
- PI consolidates local branches after tests, reviews, and clean-tree checks.
- Do not switch branches mid-chunk without recording it.

## Rollback

Prefer an append-only local `git revert`. Do not use `reset --hard`, `git clean -fdx`, or history rewriting without explicit user approval. Record rollback reason, source commit, resulting commit, tests, and working-tree state.

## User-only upstream reconciliation

The user may choose to inspect upstream after explicit approval. The user should compare local and remote histories before deciding fast-forward, merge, or rebase. Agents must not execute those remote operations. If histories conflict, preserve both histories and stop rather than overwrite.

## Evidence

Each maintenance chunk records base commit, scope, acceptance commands, reviewers, checkpoint, focused commit, and clean-tree result. Browser evidence remains deferred/non-blocking.
