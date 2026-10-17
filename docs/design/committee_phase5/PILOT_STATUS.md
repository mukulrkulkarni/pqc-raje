# Concordance N1 integrated pilot

User selected N1 and approved PI implementation. Ten-phase plan unchanged; phase 5 remains active. This is an integrated pilot awaiting user visual review, not a production gate approval.

## Implemented
- Compact six-cell notation BEFORE I/O Summary, with explicit objects, directional assertions, B1/B2 counts, groups and diff axes.
- Approved collapsed worked example, same dataset in runnable Python, readable semantic HTML formulas without renderer dependency.
- All five deep code/explanation rows retained; source code snippets and syntax-color tokens unchanged.
- Existing theme/highlight scripts retained. Correct static aria-pressed state; usage link no longer intercepted as an absent selectable row. System theme CSS added to resolve existing theme.js's system state. Mobile theme controls remain accessible.
- Selected badge foreground fixed for dark green accent; no white-on-light-green text.
- Local concept links and collapsed related/backlink block. New allow-listed sibling HTML route makes same hrefs work offline and through Flask. Does not introduce filesystem-path route parameters.
- Contradictory legacy prose corrected: q=p equality, non-finite inputs, weight preconditions and unsupported speed claims. Removed faux stdout/timing.

## Verification
- Focused pilot/module-docs/docs-routes suite: 406 passed.
- Full tests directory: 652 passed (rerun after final edits; see latest tool evidence).
- Preflight passed; existing warning: three fixed/absolute CSS positions.
- Example is executed from the HTML by tests, including reverse direction; q=p boundary cases checked.
- Local links/fragments validated against files and served HTTP content; missing pages/unknown modules/traversal rejected.
- Contrast calculated from actual CSS tokens; former white-on-green pair used as negative control.
- Existing JS files unchanged; control wiring preserved structurally. Tests do NOT prove browser interaction behavior.

## Limitations and follow-up
No Playwright or Node installed; no browser rendering, screenshot, keyboard interaction, measured 1366px width or selection baseline verification performed. Width remains a layout estimate. Existing highlight.js subtracts 64px from sidebar baseline; exact top-edge alignment remains unverified and may need a separately scoped fix. Automatic reciprocal backlink indexing and locally bundled KaTeX are not implemented; semantic HTML math is readable offline without JavaScript. Other pages remain unchanged.

No reviewer gates, commit or cross-page rollout performed. User review is the next gate. Only after approval should independent reviewers assess this pinned pilot and any required interaction fixes.
