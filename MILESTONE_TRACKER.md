# Milestone tracker
Updated: 2026-10-16

Status baseline: user-supplied plan; historical completion is preserved, not newly verified.

1. COMPLETED — Phase 3 status audit and unblockers.
2. COMPLETED — Resolve Engineering Critic 403 access issue (historical). Current reviewer recreated; runtime execution not yet verified.
3. COMPLETED — Tutorial scaffolds (Layout2) for all modules.
4. COMPLETED — Tutorial scaffold: accumulator module.
5. ACTIVE — Deep tutorials: concordance + discordance.
   - Concordance: graduate-level content, I/O summary, disclaimers, negative tests, gates and commit.
   - Discordance: graduate-level content, veto/edge cases, gates and commit.
   - Cross-links and link-integrity tests.
   - Approved design checkpoint: Scientific Critic + UI/UX + PI; content meta-template and 2–3 visual proposals. Compare N1 (notation before I/O Summary) and N2 (notation after). User must approve visuals before production changes.
   - SETUP COMPLETE: Scientific Critic and Engineering Critic recreated with gpt-5.2 configured; rationale-explainer assigned with successful reconciliation. PI, UI/UX and Security have the skill.
   - RECOVERY COMPLETE: user approved integration and checkpoint commit. Restored all 205 missing tracked files from ea0e562 without overwrites; exact archive-byte match verified. Windows index refreshed with no staged production differences. Preflight passed (existing CSS-position warning); 233 focused docs/concordance/discordance tests passed. Full suite and reviewer gates not rerun. Local snapshots retained in ignored recovery/; hashes and verification recorded in RECOVERY_CHECKPOINT.json. This record accompanies the recovery checkpoint commit; post-commit clean status is verified separately. Loss cause remains unknown. Checkpoint committed as 74d0ae0; post-commit tree verified clean. User approved resumption: committee checkpoint ACTIVE, shared brief at docs/design/committee_phase5/BRIEF.md. Scientific content review, N1/N2 visual proposals, and the single scientific cross-review COMPLETE. CROSS_REVIEW.md approves prototype scientific content only. N1.html and N2.html available in docs/design/committee_phase5/. UI/UX reported calculated contrast, not browser validation; static row/progress interactions remain prototype limitations. USER SELECTED N1 (notation before I/O Summary). Visual-choice gate complete; production implementation and reviewer gates remain pending. Preserve real theme, keyboard, selection/progress and baseline alignment behavior; do not port static prototype controls. Next proposed chunk: concordance-only N1 pilot with compact notation, verified collapsible example, readable math fallback, local links and selected-badge contrast correction, plus positive/negative tests. Concordance-only N1 pilot IMPLEMENTED; user approved integrated layout/content ('this is ok') and reaffirmed the ten-phase plan. User visual gate COMPLETE. User approved four bounded reviews (Scientific, Engineering, Security, UI/UX): 15,000–25,000 tokens, provisional USD 2–5, 8–15 minutes. Four gates COMPLETED: Engineering APPROVED (197 targeted tests executed), Security APPROVED (static), UI/UX APPROVED (static/calculated contrast; browser limits non-blocking), Scientific NEEDS WORK (credibility docstring and suggested ranking-pipeline finite-weight negatives). PI verified credibility.py unchanged from HEAD: finding is pre-existing despite report labeling. Snapshot hashes and all three files verified; directory enumeration concern resolved with direct listing. Await approval for narrowly scoped docstring correction, relevant regression tests and Scientific/Engineering delta reviews. No commit or rollout; phase 5 active. 652 tests passed in 3.51s; preflight passed (existing CSS-position warning); diff check passed. Changes: concordance HTML, allow-listed sibling tutorial route, new test_concordance_n1.py; shared JS and other tutorials unchanged. Compact notation/example, CSS-only system-theme resolution, contrast fix, offline/served links and executable example tests included. No browser runner: actual interactions/width/alignment unverified; existing baseline subtraction noted in PILOT_STATUS.md. No delegated agents, reviewer gates, commit or rollout in implementation chunk. Working tree dirty with pilot/design artifacts and synchronized records. Ten-phase plan unchanged.
6. PENDING — Deep tutorials: credibility + ranking.
7. PENDING — Deep tutorials: validate + block + accumulator.
8. PENDING — Repo architecture, dependency graph, and debugging playbook/runbook.
9. PENDING — Companion website parity + hardening.
10. PENDING — Getting Started page completion (final).

Review gates: Scientific accuracy; UI/UX including contrast and keyboard accessibility; Engineering including positive/negative behavior tests, local links and offline math fallback; Security including CSP and asset provenance; user visual approval before rollout; PI evidence/checkpoint verification. No additional agent swarm required.

Approval: committee agenda approved; estimated 20,000–35,000 tokens, USD 1–4, 10–20 minutes. No committee execution yet. Estimates are provisional, not measured billing. Request approval for material expansion; budget-impact reminder above USD 10.

Synchronize this file and SCRATCHPAD.md at progress changes and after commits. Platform milestone objects have not been updated through an API in this session.


## User-directed checkpoint and correction approval
User requested commit FIRST, then proceed with the proposed docstring/negative-test batch and Scientific/Engineering delta reviews. This commit is a preservation checkpoint, NOT all-gates approval: Scientific remains NEEDS WORK; Engineering, Security and UI/UX approved the pinned N1 scope. Phase 5 stays active; all ten phases unchanged. Follow-up will correct documentation only, add targeted tests, and seek delta verdicts before a final gated commit.


Follow-up status: checkpoint d8397ba created first; tree verified clean. Approved correction now implemented: two credibility docstring lines only, plus seven targeted test cases. Computation AST unchanged. Full suite 659 passed in 4.34s; preflight passed with existing CSS-position warning. Scientific/Engineering delta reviews COMPLETE: both APPROVED. Snapshot/live hashes verified; reviewer missing-snapshot observation corrected by direct verification in followup/PI_VERIFICATION.md. Phase 5 remains active; all ten phases unchanged.


## Current authoritative status — N1 gate closure
Concordance N1 pilot and corrective batch have all four scoped gate approvals. Checkpoint d8397ba preceded corrections as requested. This record accompanies final corrective commit; working-tree cleanliness checked after commit. Prior pending/blocked entries are historical evidence, superseded by this status. UI browser limitations remain explicit. Phase 5 stays ACTIVE: discordance deep content, remaining cross-links and relevant gates still pending; phases 6–10 unchanged. No cross-page style rollout performed. Scratchpad and milestone tracker synchronized.
