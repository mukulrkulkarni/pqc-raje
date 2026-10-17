# Project scratchpad
Updated: 2026-10-16
Canonical progress record: MILESTONE_TRACKER.md. Both records synchronized in this update.

## Current phase
Phase 5: Deep tutorials, concordance + discordance. User reports phases 1–4 complete; phases 6–10 pending. Preserve that historical baseline without claiming fresh verification.

## Approved design checkpoint
Agenda approved: content meta-template (section, text/math balance, objective, prerequisites), simpler accurate notation, collapsible consistent worked example, 2–3 visual proposals; no production redesign until user approves visuals.
N1 = notation before I/O Summary. N2 = notation after I/O Summary.
Clarify a,b are objects (IPs/items), directional comparison, B1/B2 comparison groups, and three-dimensional diff indexing. Preserve approved neutral dark text, selection, keyboard, progress and theme behavior. Math must degrade readably offline; local concept links and bottom collapsible backlinks only.

## Completed setup
Scientific Critic and Engineering Critic were absent from agent registry. Recreated project-scoped, configured gpt-5.2, rationale-explainer assigned; reconciled=true, notReflectedIn empty, read-skill granted. This establishes configuration, not successful runtime execution.
PI, UI/UX Redesign Agent and Security Lead already have rationale-explainer and read-skill.
Existing review roles cover Scientific, Engineering, Security, and UI/UX/accessibility. User visual approval and PI evidence/commit checks complete the gate sequence.

## Unexpected blocker
Read-only Git inspection found widespread tracked files missing, including docs/modules tutorial HTML, core Python, tests, and .gitignore. HEAD: ea0e562 (concordance_deep_tutorial_C1_notation_formulas_edge_cases_and_tests).
Working tree is NOT clean. No deletions were performed or staged in this session; cause unknown. No commit or review has been run. Do not automatically discard changes or stage all files. Ask user to confirm recovery of missing tracked files from HEAD while preserving other changes/untracked files.
Evidence: observations/shell__shell_execute_2026-10-16T13-56-27-195Z_c49d4eb1.txt.
First shell inspection used Unix head on Windows and failed; reran with Windows-compatible commands successfully.

## Recovery B completed
User selected isolated recovery and reaffirmed the same ten-phase plan. Snapshot: recovery/isolated-20261016T140439Z/working-files.zip preserves 86 existing files; status, staged/unstaged patches and index listing also saved. HEAD ea0e562 extracted under that folder's head/ without restoring production files. Comparison: all 205 HEAD files missing in original workspace, zero different or identical existing tracked files. Archive integrity passed; 14 core Python modules parsed; all eight tutorial HTML pages present. No behavioral tests or gates run; no staging/commit. Evidence: comparison.json and verification.json in recovery folder. Tracker synchronized.

## Recovery integration completed
User approved missing-file integration, fast verification and clean-state checkpoint. All 205 files restored without overwrites and verified byte-for-byte against archive. Windows autocrlf caused temporary status noise; index refreshed and staged production diff confirmed empty. Preflight PASS (existing three fixed/absolute CSS-position warning). Focused module-docs/concordance/discordance tests: 233 passed in 1.05s. Full suite and reviewer gates not rerun. RECOVERY_CHECKPOINT.json records hashes and evidence. Local snapshots retained under recovery/, now ignored; no off-device backup claim. This record accompanies the checkpoint commit; clean status checked after committing. Earlier blocker sections above describe historical discovery, not current missing-file status. Milestone tracker synchronized; ten-phase user plan unchanged.

## Active committee checkpoint
Recovery checkpoint committed as 74d0ae0; post-commit working tree verified clean. User explicitly resumed phase 5 and reaffirmed ten-phase plan. Shared evidence/feedback recorded in docs/design/committee_phase5/BRIEF.md before delegation. Committee now active: scientific content review, followed by UI/UX visual proposals and one content cross-review. No production edits, extra agents, or silent model retries. New design artifacts make working tree dirty until later approved checkpoint.

## Committee results
Scientific CONTENT_SPEC.md completed and corrected against executed example_results.json and VERIFIED_CORRECTIONS.md. Designer initial call blocked by unavailable claude-fable-5. User authorized one retry; configuration showed claude-fable-5-1, retry succeeded. N1.html (notation first), N2.html (I/O first plus direction banner), DESIGN_NOTES.md and contrast evidence delivered. One planned scientific cross-review completed: CROSS_REVIEW.md APPROVED prototype content only; spec reconciled. No production edits, commits or production gates. UI/UX contrast calculations flag production selected badge white on green 1.40:1; prototypes locally correct foreground. Actual browser/keyboard/width checks not performed; row selection/progress are static. New artifacts and synchronized records are uncommitted.

## Next actions
1. User selected N1: notation BEFORE I/O Summary. Visual-choice gate COMPLETE. Shared UI/UX note saying user chooses N1/N2 is superseded by this selection. Workspace records updated; shared scratch-pad API not available to PI in this session.
2. Proposed next bounded scope: concordance-only N1 pilot, retaining existing interactive JS, correcting selected badge contrast, compact notation, verified collapsible example, readable math fallback and local links; meaningful positive/negative tests. User approved PI implementation on 2026-10-17: concordance-only N1 pilot, ~8,000–15,000 tokens, provisional USD 1–3, 10–20 minutes; no delegated agents/gates/commit/rollout. Implementation ACTIVE. Minimal docs route compatibility may be required for local file links in served mode, with allow-list tests. Browser runner unavailable (no Playwright or Node); do not claim visual/browser checks. Show integrated pilot before production gates and commit; no rollout yet.
3. Keep ten-phase plan unchanged: phase 5 active; phases 6–10 pending.

## N1 pilot completion — 2026-10-17
Approved PI chunk implemented in concordance HTML only, plus allow-listed sibling docs route needed for identical offline/served local hrefs and tests/test_concordance_n1.py. Shared JS and other tutorials unchanged. Compact notation before I/O, verified collapsed worked example and matching runnable Python, safe readable HTML math fallback, neutral dark text, selected-badge contrast fix, system-theme CSS, native concept links and bottom collapsed related/backlink block. Corrected legacy prose and removed faux stdout/timing. No new agents, downloads, gates or commits.
Final verification: 652 tests passed in 3.51s; preflight passed with existing CSS-position warning; git diff --check passed. Tests execute example from HTML, test reversed pair and q=p edges, check all file/HTTP anchors, reject invalid links/traversal, and compute contrast. Structural wiring checks are NOT browser interaction proof. No Playwright/Node installed. Existing highlight.js baseline subtracts 64px; exact alignment remains unverified. KaTeX bundling and automated reciprocal backlinks deferred, not represented as complete.
PILOT_STATUS.md holds evidence and limitations. User approved integrated N1 layout/content ('this is ok') and reaffirmed exact ten-phase plan. Visual review gate complete. User approved all four independent gates: Scientific, Engineering, Security, UI/UX; estimate 15,000–25,000 tokens, USD 2–5 provisional, 8–15 minutes. Reviews COMPLETED on docs/design/committee_phase5/review/ manifest, diff and exact snapshots: Engineering/Security/UI-UX APPROVED; Scientific NEEDS WORK. Reviewers must batch findings and disclose browser limits. No unapproved retries/fixes; commit only after successful gates. Working tree is intentionally dirty with scoped pilot, design artifacts and progress records. MILESTONE_TRACKER.md synchronized; phase 5 not complete. Discordance deep content still pending; do not confuse scaffolds or pilot approval with phase completion.

Report each completed subtask, expand active task only. No repeated blind agent retries. Approved meeting estimate: 20,000–35,000 tokens, USD 1–4, 10–20 minutes; not yet executed. Request approval for scope/resource expansion; remind budget impact over USD 10. Platform internal milestone objects not updated through an API this session.


## User-directed checkpoint and correction approval
User requested commit FIRST, then proceed with the proposed docstring/negative-test batch and Scientific/Engineering delta reviews. This commit is a preservation checkpoint, NOT all-gates approval: Scientific remains NEEDS WORK; Engineering, Security and UI/UX approved the pinned N1 scope. Phase 5 stays active; all ten phases unchanged. Follow-up will correct documentation only, add targeted tests, and seek delta verdicts before a final gated commit.


Follow-up status: checkpoint d8397ba created first; tree verified clean. Approved correction now implemented: two credibility docstring lines only, plus seven targeted test cases. Computation AST unchanged. Full suite 659 passed in 4.34s; preflight passed with existing CSS-position warning. Scientific/Engineering delta reviews COMPLETE: both APPROVED. Snapshot/live hashes verified; reviewer missing-snapshot observation corrected by direct verification in followup/PI_VERIFICATION.md. Phase 5 remains active; all ten phases unchanged.


## Current authoritative status — N1 gate closure
Concordance N1 pilot and corrective batch have all four scoped gate approvals. Checkpoint d8397ba preceded corrections as requested. This record accompanies final corrective commit; working-tree cleanliness checked after commit. Prior pending/blocked entries are historical evidence, superseded by this status. UI browser limitations remain explicit. Phase 5 stays ACTIVE: discordance deep content, remaining cross-links and relevant gates still pending; phases 6–10 unchanged. No cross-page style rollout performed. Scratchpad and milestone tracker synchronized.


## Discordance deep pilot — approved and active
User approved PI-only discordance N1 pilot: 8,000–15,000 tokens, provisional USD 1–3, 10–20 minutes. Deep explanations, calculated veto example, p=v equality, links and positive/negative tests; no algorithm edits, delegated agents, gates or commit. Reuse N1 style and live JS. Ten-phase plan unchanged: 1–4 complete historically, 5 active, 6–10 pending. Show integrated page for user review after verification.


## Current authoritative status — discordance pilot awaiting visual review
PI-only approved chunk complete. Discordance now has deep R1–R5 explanations, compact N1 notation/I-O, calculated collapsed veto example, exact source excerpts and local cross-links. Shared JS, algorithms, routes and other production pages unchanged. Full suite: 679 passed in 4.31s; preflight PASS (existing CSS-position warning); diff check PASS. New tests execute the HTML example against its visible table and exercise p=v priority, shapes, negative cases and file/served links. Stale scaffold assertions retargeted without dropping security checks.
Evidence: docs/design/committee_phase5/DISCORDANCE_PILOT_STATUS.md. Actual browser/keyboard/width/alignment not verified. User APPROVED discordance pilot for review gates. Independent gates and commit remain pending; no review execution yet. Testing policy revised after user feedback: targeted affected tests per edit; add dependent route/link checks when relevant; run full suite once at final phase checkpoint or for cross-cutting changes, not repeatedly for local edits. Approved page review does not imply full gate completion. Working tree dirty with scoped pilot, tests, evidence and synchronized records. Phase 5 remains ACTIVE: concordance committed, discordance pilot ready but NOT gated or committed. Phases 1–4 historically complete; 6–10 pending, unchanged.


## Discordance review gates — approved and ACTIVE
User reaffirmed ten-phase plan and approved four bounded gates (12,000–20,000 tokens, provisional USD 2–4, 8–12 minutes). Pinned snapshot at docs/design/committee_phase5/discordance_review/manifest.json. Reuse prior 679-test/preflight evidence; targeted checks only as necessary. No automatic retries. Commit after successful gates and assess phase 5 completion; no premature milestone closure.


## Discordance gates — partial result, review access blocker
Engineering APPROVED (21 targeted tests executed), Security APPROVED, UI/UX APPROVED (static/calculated evidence only). Scientific returned NEEDS WORK because snapshot directory listing appeared empty; content review incomplete, not proof of content defects. PI direct verification confirms all three exact snapshot files exist and SHA-256 matches live/manifest; UI/UX independently confirmed hashes. Evidence: discordance_review/snapshot_verification.json. No automatic retry: ask user approval for one exact-path Scientific completion, no new files or tests needed. No commit; phase 5 remains active. All ten phases unchanged.


## Current authoritative status — Phase 5 completion (2026-10-17)
User-approved exact-path Scientific retry succeeded, APPROVED in discordance_review/SCIENTIFIC_COMPLETION.md; no code changes. All four discordance gates approved, pinned hashes unchanged. Phase-final checkpoint verification: 679 passed in 3.73s, preflight PASS (existing warning), diff check PASS. One final full-suite run at phase closure, not repeated local edit testing.
Phase 5 defined tasks complete: concordance and discordance deep content, examples, negatives, reciprocal links/file+HTTP integrity and gates; final discordance commit accompanies this record. Historical ACTIVE/BLOCKED entries above are superseded. Phase 6 is NEXT but remains PENDING, no implementation authorized/started. Ten-phase order unchanged; phases 7–10 pending. MILESTONE_TRACKER.md condensed to truthful current status; completion evidence docs/design/committee_phase5/COMPLETION.md. Browser interaction/width/alignment and renderer/backlink automation limitations remain explicitly deferred, not passed. Platform milestone API unavailable; workspace records synchronized. Post-commit clean status checked separately.
