# Approved N1 pilot review gates
User approved four reviewers: Scientific, Engineering, Security, UI/UX. Estimate 15,000–25,000 total tokens, provisional USD 2–5, 8–15 minutes. One pinned review, batched findings; stop on model failure. No production changes or commits by reviewers. Phase 5 remains active; ten-phase plan unchanged. User visual approval complete, not a substitute for independent gates.

Evidence: manifest.json pins three scoped files; snapshot/ contains their exact bytes. pilot.diff covers tracked HTML and route changes; new tests are in snapshot/tests/test_concordance_n1.py. Inspect live source dependencies as needed but flag drift against manifest. PILOT_STATUS.md explains implementation and limitations. Full tests: 652 passed in 3.51s; preflight passed with existing CSS-position warning. Do not claim these as personally executed tests.

Read rationale-explainer before decisions. Report APPROVED / NEEDS WORK / BLOCKED with precise file evidence, all actionable findings batched, distinguish pre-existing versus introduced issues, and disclose static/browser/execution limitations. No hidden reasoning requested. No extra delegation, silent retries, model switches, downloads or scope expansion. Save your concise report in this review folder.

Key areas: scientifically accurate notation/threshold precedence/finite-input and weight contracts/executable examples; meaningful positive and negative tests; sibling route allow-list/traversal/CSP/file-mode behavior; readability/contrast/keyboard/selection/system theme/layout. No browser runner is installed. Existing highlight.js has a 64px subtraction in baseline alignment; actual top-edge alignment remains unverified. Shared JS untouched. Don't mark visual/browser requirements passed without evidence.

After results PI will consolidate, request scoped fixes/re-review approval if needed, and only commit after successful gates. No cross-page rollout in this chunk.
