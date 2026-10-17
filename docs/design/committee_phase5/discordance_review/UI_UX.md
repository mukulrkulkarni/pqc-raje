# UI/UX gate — discordance deep N1 pilot

**Verdict: APPROVED** (static review only; browser-dependent items are unverified and NOT marked passed).

## Scope and evidence
- Manifest sha256 == live == snapshot for all three pinned files (recomputed; `uiux_static_checks.txt`). No drift.
- Live dependencies read: `docs/modules/assets/highlight.js`, `assets/theme.js` (unpinned, unchanged by pilot).
- Baselines: live `concordance_tutorial_side_by_side.html` (HEAD), approved `N1.html`, prior `review/UI_UX.md`, `DISCORDANCE_PILOT_STATUS.md`.
- Test count (679 passed) quoted from REQUEST.md; not executed by me. Hashes, contrast ratios, link resolution and markup counts were computed by script against the implementation.

## Limitations (explicit)
No browser runner. NOT verified: rendered widths/60-column budget at any viewport, actual keyboard activation or focus order, scroll/sidebar alignment, `<details>` open/close, theme flash, mobile layout, screen-reader output. Contrast is computed from CSS tokens, not pixels. Decision: these limitations do not block, because every browser-only item is either inherited unchanged from the approved concordance page (shared CSS, shared JS) or native HTML with structurally correct wiring; the pilot adds no new CSS or JS.

## Checks passed (static evidence)
| Area | Evidence |
|---|---|
| Reused style/notation | `<style>` block differs from live concordance by one comment line only; `#notation` section byte-identical; CSP/viewport meta identical; zero inline `style=` attributes. |
| Compactness / N1 order | `#notation` → `#io` → `.gnd-facts` dl → collapsed grounding `<details>` → collapsed `details.ex#example` → rows → usage → collapsed `#backlinks`; same sequence as approved concordance. |
| Light/dark readability | note text 7.24 / 12.12 on surface; text-dim 4.76 / 7.42; links 5.17 / 7.41 (4.94 / 7.02 on surface); h3/h4 4.94 / 16.22; new `tag.warn` "edge" 4.84 / 11.23. All ≥ 4.5. |
| Selected green foreground | `--sel-fg` on `--sel-accent` 5.02 light / 10.62 dark for `.row.sel .rk`, `.row:target .rk`, active `.j-badge`; "SELECTED" pill 4.79 / 10.62; `html[data-theme="system"]` dark block carries `--sel-fg`/`--accent-fg`. |
| Collapsible scenario table | `<details class="ex" id="example">` without `open`; `<table id="scenario-results">` has `<caption>`, 5× `th scope="col"`, 3× `th scope="row"`; values 0.85 / 5/6 / 7/18 / 0 match Scientific/Engineering computed outputs. |
| Semantic code/explanation rows | 5× `section.row` with `.row-head[role=button][tabindex=0][aria-pressed=false][data-range]`, `aria-label="Toggle Rn: …"`, `.code-col` + `.note-col` Purpose/I/O/Why/Pitfalls `h4`s; `.kw/.str/.com/.num` tokens present in R1–R5. |
| Keyboard markup (structural) | highlight.js handles Enter/Space on `.row-head[role=button][data-range]` and `.jump a[data-range]`; `#usage` jump has no `data-range` so it stays a plain link; `:focus-visible` rules on links, row-heads, summaries, theme buttons; `<details>` keyboard native. |
| Theme preservation | `data-theme="light"` on `<html>` matches theme.js default; static `aria-pressed="true"` on Light; three `[data-theme-value]` buttons; theme.js/highlight.js `defer` with same relative paths. |
| Local backlinks | All `#` hrefs resolve to ids in file. Sibling links resolve to existing files and existing fragment ids: concordance `#row-R3`/`#example`, credibility `#row-R4`, validate `#row-R4`, block `#row-R3`, ranking `#row-R2`. `#backlinks` returns to `#notation`. |
| highlight.js contract | `#main-scroll`, `#jump-R1..R5`, `#row-R1..R5`, `#prog-txt`, `#prog-fill` present; `.prog-fill{width:0%}` matches "No selection". |

## Findings — introduced by this pilot (non-blocking)
1. **No `.hl` emphasis lines in any row** — concordance uses 5 `span.hl` (green left rule) to point at the decisive lines; discordance uses 0, so the R4 `np.where` veto-first line has no in-code visual anchor. Severity: low, consistency.
2. **Worked-example `<summary>` lacks the `.lbl` pills** ("illustrative inputs" / "calculated example") that concordance and N1 show while collapsed; the disclaimer is only visible after expanding. Severity: low, parity.
3. **Longest code line grows to 83 chars** (L32 comment, repeated in R4 and R5) vs 77 in concordance; `pre{overflow-x:auto}` prevents layout breakage, but the "60+ columns" footer badge is exceeded further. Actual wrapping/scroll at 1366px unverified.
4. **R5 repeats L28–L34 verbatim** from R3 (L28–L30) and R4 (L32–L34). Compactness cost; the explanation (credibility handoff) is distinct, so acceptable, but a shorter excerpt would reduce page length.
5. **`.steps` uses `<b>` where concordance uses `<strong>`** — visually identical; semantic nit only.

## Findings — pre-existing (inherited unchanged from approved concordance; out of chunk scope)
- Unstyled `<h2 id="usage-title">` (UA default larger than 18px `h1`); heading order h1→h3→h4→h2.
- Usage `<pre>` has no syntax tokens while R1–R5 do.
- `.jump a.active` blue (`--accent-soft`) vs green active `.j-badge`; N1 used green for both.
- `#io` uses `.io-summary` `minmax(200px)` grid, not `.card` `minmax(230px)`.
- Sidebar jump lacks Notation/Backlinks entries; reachable only via `.concept-nav`.
- "Related:" links in a flex `<p class="concept-nav">` with bare text node (same pattern as concordance "Next:"). `.usage-disclaimer` has no CSS rule.
- highlight.js subtracts fixed 64px; topbar is `static` ≤768px; alignment unverified at any width.
- theme.js `defer`: stored dark theme may flash light.
- `.ln` opacity .6 (~2.3:1, decorative); `.j-badge` 4.34:1 at 9.5px; theme buttons ~26px tall; dark `--border` equals `--surface-2`.

## Decision rationale
**Chosen:**
- APPROVED — zero new CSS/JS, byte-identical notation, all contrast ≥ 4.5, links and ARIA wiring verified statically.

**Near-miss:**
- NEEDS WORK — missing `.hl` anchors and summary pills are real parity gaps but cosmetic, content-only fixes.

**Disqualified:**
- BLOCKED — no unreachable content, broken link, contrast failure or security regression found.

No production edits, design proposals, prototypes, commits, retries or extra agents. Evidence: `uiux_static_checks.txt`.
