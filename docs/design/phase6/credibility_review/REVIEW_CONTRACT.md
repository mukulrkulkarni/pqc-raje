# Accepted review mitigation — preparation only

User accepted this mitigation. This approval authorizes package preparation and local readiness verification ONLY. Production corrections and reviewer retries still need separate approval. Original verdicts remain unchanged.

## Scope and evidence
- Repository root: directory containing .git, electre3/, app/, tests/ and MILESTONE_TRACKER.md. Do not use the snapshot directory as the working directory.
- Changed files and required local dependencies are pinned by REVIEW_PACKAGE.json. Hashes refer to exact working-file bytes. Base commit records the committed baseline, not a claim that uncommitted files are already committed.
- Canonical files are reviewed and tested in place after hash verification.
- snapshot/ is READ-ONLY EVIDENCE, NOT A RUNNABLE CHECKOUT or distribution package. Missing dependencies under snapshot/ are not production defects.
- Exact canonical paths are listed in the package. Failed directory enumeration does not prove files are missing: open the exact path.
- Files not pinned but necessary for a finding must be identified explicitly. Do not silently broaden the gate or require an independent installation.

## Mandatory readiness check (inside the authorized review)
Before substantive review, open REVIEW_PACKAGE.json and the canonical files assigned to your gate. Confirm repository root, file access, hashes if tools permit, and command scope. Report readiness in the same review report; no extra agent round.
If exact-path access fails, stop with BLOCKED — evidence unavailable. Do not label inaccessible content defective, change models, retry automatically or invent results. A reviewer without shell tools must disclose that hash verification relies on the PI's recorded local check.

## Allowed test execution after separate retry approval
Working directory: repository root only.
Command: python -m pytest -q tests/test_credibility_deep.py tests/test_module_docs.py::TestCredibilityDeepTutorial
Reuse existing targeted-test evidence unless fresh execution is necessary. Never run snapshot/tests/...; those files derive paths from __file__ and are relocated evidence copies. No full-suite run for this local batch. No downloads, installations or external calls.
Local package-readiness command (not product tests): python docs/design/phase6/credibility_review/verify_review_package.py

## Findings contract
Each blocker must state: exact canonical path and passage/test; violated approved requirement; observed evidence; minimal correction; introduced versus pre-existing versus evidence-access failure. Distinguish requirements on valid inputs from validation enforced by code. A precondition is not a promise of runtime rejection. Inspect nearby statements before claiming an omission.
Return APPROVED, NEEDS WORK or BLOCKED for the requested scope only. Batch all actionable findings. Disclose static inspection, executed tests, calculated contrast and actual browser verification separately. No hidden reasoning is requested; provide conclusions and evidence.

## Stop and follow-up rules
No production edits or commits by reviewers. No automatic retries, extra agents, paid fallbacks or expanded requirements. Preserve all earlier reports. PI may clarify provenance but cannot overwrite reviewer verdicts. Any production edit invalidates its pinned hash: refresh package after an approved correction, then obtain explicitly approved delta reviews.

## Current boundaries
UI/UX approved static/calculated scope. Scientific, Engineering and Security remain NEEDS WORK. Browser interaction/width/alignment remain unverified. The mitigation reduces recurrence but does not guarantee agent compliance. Phase 5 completed in 26ccab6; phase 6 active by explicit approval. Ten-phase scope/order unchanged despite older pasted status labels.
