# UI/UX Gate — Credibility Tutorial (Phase 6, N1 pilot)

**Verdict: APPROVED** (static/calculated scope; browser-dependent behaviour explicitly unverified)

Reviewed: `docs/design/phase6/credibility_review/snapshot/docs/modules/credibility_tutorial_side_by_side.html`
(sha256 `530204c9…c89d`, 43,023 bytes — matches manifest and live file).
Baseline: live `docs/modules/discordance_tutorial_side_by_side.html` (approved N1) and concordance N1.
Evidence files: `uiux_static_checks.txt`, `uiux_contrast.txt` (same folder). No prototypes, edits, agents, retries or commits.

## Verdict rationale

**Chosen:**
- APPROVED — all static N1 parity checks pass; introduced findings are low severity and non-blocking.

**Near-miss:**
- NEEDS WORK — nested-subscript formula and one aria-label mismatch are real but minor; neither breaks parity or WCAG A.

**Disqualified:**
- BLOCKED — browser runner absence affects only width/alignment/keyboard behaviour in shared, unchanged JS/CSS already approved for N1.

## Static / calculated evidence (verified)

| Check | Result | Evidence |
|---|---|---|
| Hashes (3 files, snapshot + live) | all match manifest | `uiux_static_checks.txt` lines 1–6 |
| CSS block identical to discordance N1 (modulo module name) | True | `uiux_static_checks.txt` |
| Notation before I/O before example before rows | indices 19963 < 22295 < 25933 < 28292 | same |
| Source snippets vs `electre3/credibility.py` | 25/25 excerpt lines exact (L1–6, 27, 30–32, 34–35, 37–45) | same |
| Internal anchors (10) and cross-file links (8) | all resolve, all fragments present | same |
| Green selection: `.hl`, `.row.sel .rk`, `::after "selected"` text cue | present, identical to N1 | HTML CSS lines |
| Table semantics | `<caption>`, `<thead>`, `th scope="col"`, `th scope="row"`; byte-identical to discordance example | HTML |
| Collapsible shared example | `<details class="ex" id="example">` closed by default; linked from R4 and concept-nav | HTML |
| Keyboard markup | `.row-head[role=button][tabindex=0][aria-pressed][aria-label]`; theme `button[type=button][aria-pressed]` in `role=group`; `:focus-visible` on links, summaries, row-heads, theme buttons | HTML; `highlight.js` handles Enter/Space |
| Theme controls | Light/Dark/Sys buttons; `html[data-theme=system]` + `prefers-color-scheme` block present; `theme.js` unchanged | HTML, `assets/theme.js` |
| Bottom backlinks | `<details id="backlinks">` after usage; 3 curated links + return-to-notation | HTML |
| Contrast (WCAG 1.4.3 text) | 31/31 text pairs ≥ 4.5:1 in light and dark; min light 4.55:1 (`#64748b` on `#f8fafc`), min dark 5.87:1 | `uiux_contrast.txt` |

## Findings — introduced (credibility-specific content)

1. **Dense formula uses nested `<sub>` (I/O Summary, "Full veto takes precedence").** `∏<sub>j: C(a,b)&lt;d<sub>j</sub>(a,b)&lt;1</sub>` yields ~11.2px condition text and ~9.3px inner `j` at the 13.5px `.math` base (calculated from browser default `font-size: smaller`). Readable but strains low-vision users. Recommend prose condition ("product over criteria j with C(a,b) < d_j(a,b) < 1") in a later pass. Low.
2. **Label-in-name mismatch (WCAG 2.5.3) on R4.** Visible title "Credibility Aggregation"; `aria-label="Toggle R4: Aggregation"` and jump-nav title "Aggregation". Discordance N1 labels match titles exactly. Voice-control users saying the visible name may miss. Low; one-word fix in a later pass.
3. **Non-contiguous excerpts without elision marker.** R2 shows L6 then L27; R3 shows L30–32 then L34–35. Row-lines honestly read "Selected source lines", but no visual gap marker exists, so readers may assume adjacency. Adding a marker would require updating `test_source_excerpts_and_highlights_are_exact`. Low; documented, not blocking.
4. **R4/R5 overlap L40–L43.** Same pattern as discordance R3/R5 overlap; acceptable, noted for consistency.

## Findings — pre-existing (shared with approved N1; not introduced)

5. Light-theme `--sel-border #86efac` vs white: 1.40:1 non-text contrast (1.4.11 target 3:1). Mitigated by green `.rk` badge (5.02:1), "SELECTED" text cue and 3–4px `#15803d` highlight border. Dark theme passes (7.83:1).
6. Inherited 64px `scroll-margin-top`/`topbarOffset` and `#notation…{scroll-margin-top:80px}` divergence — known; alignment not verifiable here.
7. Initial `data-theme="light"` with deferred `theme.js` may flash for stored-dark users. Shared JS, unchanged.
8. Sidebar jump-nav omits Notation/I-O/Example entries; covered by `.concept-nav`. Same in N1.
9. Footer badge "browser check pending" remains accurate.

## Browser-dependent items — NOT verified (no runner)

Actual rendering, 60+ column width budget, sidebar baseline alignment, smooth-scroll, Enter/Space row toggling, theme switching, details expansion, and formula wrapping at ≤1100px. These are inherited from byte-identical CSS and unchanged shared JS approved in N1; they do not block this scoped approval but remain open for the project-level browser check.

## Scope limits honoured

Reused existing evidence (88 targeted tests passed; preflight PASS with known CSS-position warning). No tests run, no production edits, no additional agents.
