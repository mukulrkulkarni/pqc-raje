# DC5 documentation notes — evidence remediation

## Scope and authority

- Approved scope: documentation/evidence remediation only; no application feature or tutorial rewrite.
- Current pre-remediation `HEAD`: `6c6b2d478f8fda23e37d17a4134e8e9df19b6c57` — `record-dc5-recovery-commit-state`.
- Preceding DC5 metadata commit: `0aee973678f7395aa77e3ca24741c6a86eacd5d6` — `recover-dc5-release-metadata`.
- Authoritative implementation commits: DC-1 `8cab5db`, DC-2 `62f461b`, DC-3 `36b2bb0`, DC-4 `e111b46`, and DC4.5 `cd6b3cf`.
- DC4.5 commit identity: `cd6b3cf6765e26823b98fc31761b4aecb37a790e` — `implement-dc45-criteria-card-ui`.

## Remediation completed before focused commit

1. `docs/decisions/dc-3-documentation-notes.md` now clearly identifies itself as historical and superseded by `dc-3-recovery-notes.md`; its failure history is preserved.
2. [DC5 security evidence](dc-5-security-evidence.md) records exact current commands/results for full suite, CSP, security/cache/runtime, download/session/token behavior, identifier safety, and positive/negative/edge coverage.
3. [DC5 branding and archive notes](dc-5-branding-and-archive-notes.md) verifies static brand alignment with `skills/brand-styling-framework/MK-TII-brand-template.json` and identifies browser/AT/zoom/reflow/offline as deferred limitations.
4. Preserved untracked screenshot/mockup references moved without deletion to `out/archive/dc-5-preserved-references/`; [its manifest](../../out/archive/dc-5-preserved-references/ARCHIVE-MANIFEST.md) records provenance and classification.
5. [DC5 bounded release reviews](dc-5-release-reviews.md) records Scientific, Engineering, Security, and UI/UX verdicts after evidence metadata became current.

## Current executed validation evidence

| Category | Command | Result |
| --- | --- | --- |
| Full suite | `python -m pytest tests -q` | `932 passed in 8.62s` |
| Security/cache/runtime/workflow routes | `python -m pytest tests/test_security.py tests/test_security_headers.py tests/test_runtime.py tests/test_result_cache.py tests/test_app_workflow.py -q` | `57 passed in 1.57s` |
| Identifier/card/serialization/DC3 boundary evidence | `python -m pytest tests/test_dc2_identifier_migration.py tests/test_dc45_criteria_cards.py tests/test_serialization.py tests/test_dc3_minimize_transform.py -q` | `54 passed in 0.90s` |
| Syntax and whitespace diff | `python -m compileall -q electre3 app tests && git diff --check && git diff --cached --check` | exit code `0` |

The commands cover positive workflow and download paths, negative security/validation paths, and boundary/concurrency/identifier/selection/IEEE-754 edge cases. See the security bundle for test-level details.

## Reviews

| Review | Verdict | Basis |
| --- | --- | --- |
| Scientific | **APPROVED** | DC3 stable direct evaluation and positive/negative/edge evidence reviewed. |
| Engineering | **APPROVED** | Traceability, exact commands, focused scope, and reproducibility evidence reviewed. |
| Security | **APPROVED** | Header, cache, download, session/token, identifier, and runtime evidence reviewed. |
| UI/UX | **APPROVED WITH DEFERRED LIMITATIONS** | Static brand/UI semantics and card tests reviewed; no browser claim. |

The review details and limitations are authoritative in [DC5 bounded release reviews](dc-5-release-reviews.md).

## Deferred limitations and release boundary

No browser automation or rendered-browser evidence was obtained. Browser/assistive-technology behavior, keyboard traversal, zoom, responsive reflow, offline operation, and load performance remain deferred limitations. This remediation records no final release claim.

## Commit and tree boundary

The focused remediation commit must contain only DC5 documentation/checkpoint records and the DC3 supersession marker. The preserved reference archive remains intentionally untracked and excluded from that commit, so the post-commit repository state is expected to be **dirty_tree**. No unrelated work may be deleted, staged, or committed.
