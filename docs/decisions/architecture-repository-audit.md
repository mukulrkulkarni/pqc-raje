# Architecture and repository audit

**Date:** 2026-10-27  
**Reviewer:** Engineering Critic  
**Verdict:** **NEEDS WORK**  
**Scope:** Local architecture, repository, launcher, generated documentation, tests, maintenance, rollback, and user-only upstream reconciliation.  
**Pinned revisions:** release launcher `3e32ed6`; release verification `cff0f40`; local release/tag evidence HEAD `8344edff36223b9a4528d4db39a0534376853d29` (`v0.1`).  
**Excluded:** application/page edits, browser execution, remote Git operations, commits.

## Executive conclusion

The v0.1 runtime has clear algorithm/UI boundaries and strong executable validation. The launcher and focused regression set pass locally. The repository itself is not yet a clean minimal release repository: tracked historical snapshots, raw attachments, design/build artifacts, duplicated generated HTML, and operational records are mixed with user runtime resources. The documented commit gate also contradicts the accepted release process because its preflight currently fails on established code and response-header CSP handling. Rollback guidance includes destructive and remote commands without a user-only reconciliation procedure.

The release can remain **released with limitations**. Do not represent the current tree as a minimal distribution or the maintenance instructions as safe/current until the findings below are resolved.

## Evidence basis

### Static inspection

- Architecture: `electre3/`, `app/routes/`, `app/services/`, `scripts/`, `docs/runbook/architecture.md`.
- Tests: focused positive, negative, and edge suites under `tests/`.
- Launcher: `scripts/dev_local.py`, `tests/test_dev_local.py`, commit `3e32ed6`.
- Website generation: `scripts/build_website.py`, `scripts/module_docs_html.py`, `website/site-config.json`, generated `website/` resources.
- Release evidence: `docs/decisions/v0-1-release-verification-evidence.md`, commit `cff0f40`.
- Tag evidence: `docs/decisions/v0-1-tag-notes.md`, HEAD/tag commit `8344edf`.
- Repository policy: `.gitignore`, `.gitattributes`, `docs/VERSIONING_AND_ROLLBACK.md`.
- Tracked-resource inventory: local `git ls-files` at `8344edf`.
- Pinned diff: `cff0f40..8344edf` adds only `docs/decisions/v0-1-tag-notes.md` and `out/v0-1-tag-checkpoint.json`; `3e32ed6..8344edf` adds six release-record files. No runtime change follows the launcher commit.

### Executed checks in this audit

| Check | Result | Evidence type |
| --- | --- | --- |
| Focused architecture/route/launcher/docs/security/cache suite | **481 passed in 10.00s** | Executed: `pytest -q` against ten named test modules. |
| Focused collection | **481 tests collected in 0.58s** | Executed; confirms the tested set. |
| Python compilation | **Passed** before the chained preflight failure | Executed: `python -m compileall -q electre3 app scripts`. |
| Legacy preflight | **Failed, exit 1** | Executed: six core files exceed 50 lines; four app templates lack literal CSP text. |
| Local Git status before audit writes | `main...origin/main`; only planned checkpoint untracked | Executed local inspection; no fetch or other remote operation. |

The earlier release record reports **947 passed** at `cff0f40`; this audit treats that as recorded evidence, not as a rerun.

## Architecture and module/service boundaries

### Strengths

- `electre3/` owns configuration, validation, data loading, credibility/block computation, accumulation, ranking, serialization, runtime controls, and CLI flow.
- `app/routes/` separates workflow, preview, compute, and documentation HTTP concerns.
- `app/services/` isolates preview parsing, result caching, runtime profiles, and security helpers.
- `app/routes/compute.py` delegates scientific work to `electre3.runtime`; the UI does not reimplement the ranking algorithm.
- `app/services/preview.py` centralizes preview parsing and validation rather than embedding file rules in templates.
- `scripts/dev_local.py` composes static website and Flask services without embedding either server into the scientific package.
- `docs/runbook/architecture.md` records the pipeline and deterministic block/accumulation invariants.

### Boundary risks

1. **Core size policy is detached from maintainability reality.** `scripts/preflight_checks.py` reports `cli.py` 66, `config.py` 55, `data.py` 99, `runtime.py` 184, `serialization.py` 195, and `shared.py` 157 lines against a fixed 50-line limit. Several are orchestration/contract modules where arbitrary splitting can reduce cohesion. Either revise the policy with justified per-module thresholds or refactor by responsibility; do not keep a permanently failing mandatory gate.
2. **Generation has two mechanisms.** `scripts/module_docs_html.py` creates documentation HTML, while `scripts/build_website.py` copies/transforms selected outputs into `website/`. There is no single manifest that states source, generated target, ownership, and stale-output detection.
3. **The website builder mutates tracked output in place.** It reads and rewrites existing `website/index.html`, `website/app/index.html`, module indexes, assets, and tutorials. Tests prove a successful rebuild, but no test builds into a temporary directory and compares the complete tree for determinism or deletion of stale outputs.
4. **Module lists are duplicated.** `scripts/build_website.py` hard-codes five modules; route allow-lists and documentation tests maintain related lists independently. Drift can create missing pages or inconsistent serving.

## Positive, negative, and edge evidence

### Positive

- `tests/test_dev_local.py::test_launcher_starts_both_services_prints_urls_and_stops_without_orphans` starts both loopback services, probes HTTP 200, interrupts, and confirms closed ports.
- `tests/test_docs_routes.py` serves landing, application, module, tutorial, and local assets with route-scoped CSP assertions.
- `tests/test_website_static.py::test_build_website_rebuilds_without_error` executes the local website build.
- `tests/test_app_workflow.py`, `tests/test_validate_deep.py`, `tests/test_security.py`, and `tests/test_result_cache.py` exercise valid workflows, validator boundaries, security controls, and successful cache/download paths.

### Negative

- Launcher tests reject occupied, invalid, and equal ports and stop the peer after child failure.
- Documentation routes reject nonexistent modules, traversal, encoded traversal, null bytes, mixed case, and unapproved assets.
- Website generation rejects malformed `<body>` structure and incomplete existing primary navigation.
- `tests/test_local_document_links.py` proves its checker reports missing local files and fragments.
- Result-cache tests reject invalid payloads and tampered checksums.

### Edge

- Port values `0`, `65536`, and nonnumeric text are covered.
- Double-encoded, Unicode, backslash, and null-byte route variants are covered.
- Keyboard-source assertions cover Enter, Space, `preventDefault`, focus styles, and missing-element guards in module tutorials.
- Reduced-motion, hash changes, no-JavaScript `:target`, missing sidebar/progress elements, and localStorage failure paths have static regression assertions.

## Required evidence gaps and limitations

- **Local link integrity is partial.** `tests/test_local_document_links.py` checks only two decision documents. It does not crawl all README, docs, website, fragment, or generated navigation targets.
- **Missing-target coverage is split and narrow.** Route missing modules/assets and tutorial row/sidebar guards exist, but no repository-wide missing generated-page test exists.
- **Malformed-input coverage is strong** for routes, launcher ports, website nav injection, scientific inputs, and cache payloads in the executed set.
- **Keyboard interactions are statically inspected, not browser-executed.** Source-token assertions do not prove event behavior, focus order, or assistive-technology operation.
- **Math-renderer failure has no regression.** No MathJax/KaTeX runtime is part of the inspected release path; formulas are static HTML/text. Record this as not applicable unless a renderer is introduced. If introduced, require load-failure fallback tests.
- **Offline behavior is structurally supported but not executed in a browser.** Static tests reject external assets and validate local script paths. They do not prove service interruption behavior, `file:` behavior, browser caching, or every navigation target.
- **Browser/AT/zoom/reflow/load evidence remains deferred and non-blocking.** This audit makes no browser-readiness claim.
- **No package/dependency lock file was found at repository root.** Reproducibility depends on environment instructions rather than a machine-verifiable release dependency manifest.

## Launcher and offline operation

The launcher at `3e32ed6` is appropriately bounded: loopback-only listeners, validated distinct ports, bind-before-announcement, no Flask reloader child, coordinated shutdown, thread joining, and deterministic nonzero errors. The seven launcher behaviors are included in the passing focused suite.

Offline operation has no external service dependency for computation. Local assets and CSP constraints support offline-first use. However, the static website contains absolute `http://localhost:5000` links while the supported launcher advertises `127.0.0.1` and configurable `APP_PORT`; custom-port navigation can therefore leave generated links stale. Centralize effective local URLs or make navigation relative/proxy-independent.

## User-release versus development/test/archive resources

### User-release resources

- `electre3/`, `app/`, launcher/converter scripts, required static/templates.
- `README.md`, concise runbooks/tutorials, `examples/`, and the built `website/` if shipping prebuilt docs.
- A dependency manifest, license, version metadata, and release notes should be explicit release inputs.

### Development/test resources

- `tests/`, generator and benchmark scripts, preflight tooling, detailed decision records.
- These can remain in the development repository but should not be required in a minimal user archive.

### Archive/review resources currently tracked

- `docs/design/**/snapshot/`, review manifests, images, diffs, duplicate historical HTML, and archived test copies.
- `attachments/` includes raw briefs, screenshots, browser-evidence JSON, and model metadata.
- `artifacts/`, `build_v22/`, and many `code/canvas_*.py` files are tracked despite `.gitignore` now naming some directories.
- Numerous `out/*.json` checkpoints and decision records document process but enlarge the release tree.

`.gitignore` does not untrack files already committed. A clean release requires an explicit allow-list export or a dedicated packaging manifest, not assumptions based on ignore rules.

## Branch strategy and clean minimal release repository

Local inspection found one branch, `main`, at `8344edf`, tracking the locally recorded `origin/main`, with annotated tag `v0.1`. No remote contact occurred. `docs/VERSIONING_AND_ROLLBACK.md` says never commit directly to `main`, but the visible project history and PI consolidation workflow operate on `main`. This contradiction makes the written policy non-authoritative.

Recommended local strategy:

1. Keep `main` as the locally verified integration/release branch.
2. Use short-lived `audit/*`, `docs/*`, `fix/*`, or `feature/*` branches for changes; PI alone consolidates focused commits.
3. Cut annotated release tags only after tests, release manifest verification, and clean-tree checks.
4. Generate a minimal user archive from an allow-list; do not delete historical evidence merely to make the development repository appear small.
5. Verify archive contents in CI/local tests: expected files present, forbidden development/archive files absent, launch smoke test passes, links resolve locally, and archive rebuild is deterministic.

## Maintenance workflow

A safe maintenance chunk should record its base commit, scope, acceptance commands, checkpoint, and stop conditions. It should use one focused local commit after reviewing `git diff --check`, changed paths, tests, and clean status. PI consolidates this audit; this independent review intentionally creates no commit.

The current preflight cannot serve as a mandatory gate because it fails the released tree. Align `scripts/preflight_checks.py`, `docs/VERSIONING_AND_ROLLBACK.md`, and actual acceptance commands. Prefer checks that validate response CSP through the Flask client rather than searching templates for header text.

## Rollback assessment

`docs/VERSIONING_AND_ROLLBACK.md` explains reset, checkout, revert, and reflog, but it is unsafe as a current user procedure:

- It recommends `git reset --hard` without first requiring a clean tree, backup branch, or explicit data-loss confirmation.
- It mentions force-push although all upstream operations are user-only and force-push is not an approved default.
- It does not distinguish unpublished local rollback from published-history reconciliation.
- It does not pin rollback acceptance tests or release-artifact verification.

Prefer additive `git revert` for shared/published history. Reserve reset for unpublished local history after the user verifies a clean tree and creates a recovery reference. Never automate remote correction.

## User-only upstream reconciliation procedure

Agents stop after local inspection and preparation. The user performs every remote action.

1. **Inspect without changing history:** user runs `git status --short --branch`, records local HEAD/tag, then explicitly chooses whether to contact upstream.
2. **User retrieves and compares:** user runs an approved fetch, reviews `git log --left-right --graph main...origin/main`, tag differences, and changed paths. No automatic pull, merge, or rebase.
3. **Choose reconciliation:** fast-forward only when local has no unique commits; otherwise create a user-controlled reconciliation branch and merge/rebase only after backup and tests.
4. **Verify locally:** run focused plus full regressions, deterministic website build, complete local-link/package checks, `git diff --check`, and clean-tree verification.
5. **Publish deliberately:** user alone pushes the named branch/tag. Avoid force-push; if unavoidable, require explicit collaborator coordination and `--force-with-lease`, never plain `--force`.

If upstream differs unexpectedly, tags conflict, tests fail, or the tree is dirty, stop and preserve both histories. Do not retry or overwrite.

## Batched actionable findings

### P0 — Maintenance policy integrity

- Replace the permanently failing 50-line/CSP preflight rules or refactor with documented responsibility-based limits.
- Reconcile branch policy with the actual PI consolidation workflow.
- Rewrite rollback guidance around clean-tree checks, recovery references, revert-first behavior, and user-only upstream operations.

### P1 — Release hygiene and reproducibility

- Define a release allow-list/manifest separating runtime/docs/examples from tests, attachments, snapshots, checkpoints, and design artifacts.
- Add an explicit dependency/version manifest and license/version files to the release contract.
- Build generated documentation into a clean temporary target and compare the full output tree for determinism and stale files.
- Consolidate module/page manifests used by routes, builders, and tests.

### P1 — Integrity regressions

- Add a repository-wide local link/fragment crawler covering README, docs, website, generated pages, missing targets, and malformed links.
- Add archive-content positive and forbidden-file negative tests.
- Add custom-port navigation tests so launcher URLs and generated links remain coherent.
- Keep keyboard and missing-element source tests; add browser execution only in the separately approved browser-evidence milestone.

### P2 — Repository organization

- Move historical snapshots and raw evidence behind a documented archive boundary without rewriting published history.
- Decide whether generated `website/` and `docs/modules/*.html` are release artifacts or rebuild products; document one source of truth.
- Keep process checkpoints out of the user archive while retaining them in the development repository as required evidence.

## Decision rationale

**Chosen:**
- NEEDS WORK — Runtime tests pass, but repository policy, release hygiene, and integrity coverage remain inconsistent.

**Near-miss:**
- APPROVED — Strong runtime boundaries and 481 passing focused tests nearly satisfy the bounded audit.

**Disqualified:**
- BLOCKED — Local source, pinned revisions, tests, and release evidence were available.

## Final limitations

This review inspected local state only. It did not fetch, compare live upstream state, run browser/AT evidence, benchmark production load, test installation on a clean machine, or create a release archive. It did not edit application or documentation pages and did not commit.
