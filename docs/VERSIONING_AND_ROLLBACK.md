# Versioning and rollback

## Local maintenance gate

Before a focused local commit, inspect `git status --short`, run `python scripts/preflight_checks.py`, run the relevant focused tests, run `python -m pytest -q tests/` when scope permits, and run `git diff --check`. The preflight validates Flask **response** CSP headers, local assets, H2 generated-documentation ownership and freshness, and the 50-line policy for H2 support modules. The existing `scripts/build_website.py` exception remains documented.

Use focused commits. The local PI consolidation workflow controls `main`; this document does not authorize a remote operation.

## Generated and release resources

Tutorial sources at `docs/modules/*_tutorial_side_by_side.html` generate `website/modules/<module>/tutorial/index.html`. See `docs/GENERATED_DOCUMENTATION.md`. Rebuild with `python scripts/build_website.py` after source edits. Preflight rejects a missing or source-older target.

A user release contains runtime code, required app/static files, concise documentation, examples, and approved generated website output. Tests, attachments, snapshots, decision records, checkpoints, and build artifacts remain development/archive resources unless an explicit release manifest includes them. Verify the intended resource list and local links before packaging.

## Local rollback procedure

1. Stop when the tree is dirty. Record `git status --short` and `git log --oneline -10`.
2. Create a local recovery reference before history changes: `git branch recovery/<date>-<topic> HEAD`.
3. Prefer `git revert <commit>` for shared or published history. Run the maintenance gate after resolving any conflict.
4. Use `git reset --soft <commit>` or `git reset <commit>` only for unpublished local work after verifying the recovery reference.
5. `git reset --hard <commit>` discards work. Use it only after a clean-tree check and explicit user confirmation. Do not automate it.
6. Use `git reflog` to locate lost local references. Restore deliberately and rerun the gate.

## User-only upstream reconciliation

Only the user may fetch, pull, push, mutate remote branches or tags, merge/rebase with remote history, or force-push. Agents may inspect local state and prepare evidence only.

The user should inspect status and local HEAD/tag, explicitly choose whether to contact upstream, compare histories and tags after an approved fetch, reconcile on a user-controlled branch, run local checks, and publish deliberately. Do not use plain `--force`; unexpected differences, conflicts, failed tests, or a dirty tree require a stop and preservation of both histories.

## Quick reference

| Action | Command |
| --- | --- |
| Run preflight | `python scripts/preflight_checks.py` |
| Run tests | `python -m pytest -q tests/` |
| Rebuild generated site | `python scripts/build_website.py` |
| Inspect local status | `git status --short` |
| Revert a commit | `git revert <commit>` |
| Create recovery reference | `git branch recovery/<date>-<topic> HEAD` |
| Recover local reference | `git reflog` |
