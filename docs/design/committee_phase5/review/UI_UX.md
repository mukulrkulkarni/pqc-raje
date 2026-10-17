# UI/UX gate — N1 concordance pilot

**Verdict: APPROVED** (static review; browser-dependent items remain unverified and are NOT marked passed).

## Scope and evidence
- Pinned files: manifest sha256 == live == snapshot for all three files (recomputed; see `uiux_static_checks.png`). No drift.
- Live dependencies inspected: `docs/modules/assets/highlight.js`, `docs/modules/assets/theme.js` (unpinned, unchanged by pilot).
- Compared against approved `N1.html`, `pilot.diff`, `snapshot/tests/test_concordance_n1.py`, `PILOT_STATUS.md`.
- Test counts (652 passed) are quoted from REQUEST.md, not executed by me.

## Limitations (explicit)
No browser runner. I did NOT verify: rendered width/60-column budget at 1366px, actual keyboard activation, scroll-spy/alignment, `<details>` behaviour, theme flash, mobile layout. Contrast values are computed from CSS tokens, not screenshots. Decision: these limitations do not block, because every browser-only item is either pre-existing (64px baseline offset, deferred theme flash) or native/standard (`<details>`, links) with structurally correct wiring; none is introduced by the pilot.

## Checks passed (static evidence)
| Area | Evidence |
|---|---|
| Compact N1 parity | Notation card precedes `#io` precedes `#example`; `.card` grid, `.gnd-facts` dl, collapsed `details.ex`/`#backlinks`, six notation cells, same worked values (0.85/0.75). |
| Light/dark text | note text 7.24 / 12.12; text-dim 4.55 / 7.03; links 5.17 / 7.41; h3 headings 4.94 / 16.22 (all ≥ 4.5). |
| Selected badge | `--sel-fg` on `--sel-accent`: 5.02 light, 10.62 dark; `.row.sel .rk,.row:target .rk{color:var(--sel-fg)}` present; former white-on-#86efac (1.3) removed. |
| System theme | `@media(prefers-color-scheme:dark) html[data-theme="system"]` block includes `--sel-fg`/`--accent-fg`; theme.js writes `data-theme` on `<html>` and sets `aria-pressed` on `[data-theme-value]` buttons. Static `aria-pressed="true"` on Light matches theme.js default `'light'`. |
| Selection/progress | `#main-scroll`, `#jump-R1`..`R5`, `#row-R1`..`R5`, `#prog-txt`, `#prog-fill` all present as highlight.js requires; `.prog-fill{width:0%}` now matches "No selection"; `role="button" tabindex="0" aria-pressed="false"` on five row-heads (replaces wrong `aria-expanded`); `#usage` link lost `data-range="EX"` so it is no longer intercepted. |
| Keyboard (structural) | highlight.js handles Enter/Space on `.row-head[role=button][data-range]` and jump links; `:focus-visible` outlines on links, row-heads, summaries, theme buttons. `<details>` keyboard is native; capture-phase handlers do not touch `summary`. |
| Concept links | Relative sibling hrefs (`discordance_…#row-R2` etc.) work offline and via new `linked_tutorial` route; hash on arrival triggers highlight.js selection in the target page. Fragments `#notation/#io/#example/#backlinks` exist; `scroll-margin-top:80px` set. |
| Tables/semantics | `<caption>`, `th scope="col"`, `aria-labelledby` on sections, `nav aria-label="Concepts"`. |

## Findings — introduced by pilot (non-blocking, scoped CSS/HTML only)
1. **Unstyled `<h2>` in `#usage`** — no `h2` rule exists; UA default (~21px bold, 0.83em margins) renders larger than the 18px `h1`. Fix: `.usage h2{font-size:14px;font-weight:650;margin:0 0 var(--s2);}` or reuse `.row-title` pattern.
2. **Usage code lost syntax tokens** — new `<pre><code>` is plain monochrome while R1–R5 keep `.kw/.num/.com` spans; visually inconsistent with "tokens unchanged". Fix: wrap tokens or state intentionally plain.
3. **Mixed accent on active jump item** — `.jump a.active` keeps blue `--accent-soft`/`--accent` (baseline) while the badge now uses green `--sel-accent` (pilot). N1.html used green for both. Fix: `.jump a.active{background:var(--sel-soft);color:var(--sel-accent)}`.
4. **Card grid mismatch** — `.card` uses `minmax(230px,1fr)` but `#io` retains `.io-summary` `minmax(200px,1fr)`; Notation and I/O columns will not align as in N1. Fix: give `#io` class `card`.
5. **Sidebar lacks Notation/Backlinks entries** — N1 listed NT/IO/EX/←; integrated page reaches them only via the top `.concept-nav`. Acceptable (highlight.js only needs R-links) but note the parity gap.
6. **"Next:" links in a `<p class="concept-nav">`** — flex `<p>` with bare text node; prefer `<nav aria-label="Next">`.

## Findings — pre-existing (not introduced; out of chunk scope)
- highlight.js subtracts fixed 64px; topbar is `static` ≤768px (pilot) so alignment math is off on mobile; top-edge alignment unverified at any width.
- theme.js is `defer`; stored dark theme may flash light on load.
- `.ln` line numbers at `opacity:.6` ≈ 2.25:1 light (decorative, `user-select:none`).
- `.j-badge` dim/surface-2 4.34:1 at 9.5px bold; "SELECTED" pseudo-pill 9px (state also exposed via `aria-pressed`, so not a failure).
- Heading levels skip h1→h3→h4; h2 appears after h3s.
- Theme buttons ~26px tall (below 44px touch target guidance).
- Dark `--border` equals `--surface-2` (card borders vanish on surface-2).

## Decision rationale
**Chosen:**
- APPROVED — introduced issues are cosmetic one-line CSS fixes; all accessibility-critical items hold on static evidence.

**Near-miss:**
- NEEDS WORK — h2 hierarchy inversion is real but trivial and already seen in user visual approval.

**Disqualified:**
- BLOCKED — no security, data-loss or unreachable-content defect found.

No production edits, prototypes, commits or extra agents. Artifact: `uiux_static_checks.png` (hash + contrast table).
