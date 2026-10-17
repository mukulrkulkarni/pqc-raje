# Phase 5 — UI/UX design notes (N1 vs N2 prototypes)

Status: ⏳ phase 5 active. These are prototypes only; no production file, test, commit, agent or model change. User chooses before any implementation.

## Deliverables
| File | What it is |
|---|---|
| `N1.html` | Notation block **before** I/O Summary |
| `N2.html` | Notation block **after** I/O Summary + one-line micro-banner pinned in I/O Summary (CONTENT_SPEC §E note) |
| `contrast_evidence.png`, `contrast_table.txt` | Calculated WCAG 2.x ratios for Layout2 tokens |
| `n2_generation_check.png` | Proof N2 was generated from N1; line-level diff; width-budget estimate |

Content sources: `CONTENT_SPEC.md` (blocks 1, 2, 5), `VERIFIED_CORRECTIONS.md` (supersedes spec on q=p step semantics, orientation, a→b meaning, weights), `example_results.json` (A→B 0.85, B→A 0.75). Styling tokens copied verbatim from `docs/modules/concordance_tutorial_side_by_side.html`.

## Rationale (layout)
**Chosen:**
- N1 — Readers meet a, b, a→b and B1/B2 before any (B1,B2,C) shape appears; prevents the reported confusions.

**Near-miss:**
- N2 — Faster orientation for returning readers; micro-banner mitigates but splits definitions across two places.

**Disqualified:**
- Notation only in a collapsed details block — Hides the exact content the user flagged as confusing.
- Notation in sidebar — 200px column cannot hold six definitions legibly.

## Rationale (theme control)
**Chosen:**
- CSS-only radio inputs — No JS, no assets, works offline, keyboard reachable; honest for a static mock.

**Near-miss:**
- Reuse `assets/theme.js` — Real behaviour, but brief forbids external files and the mock lives outside `docs/modules/`.

**Disqualified:**
- Inline script — Violates "no scripts" CSP of the existing tutorial.

## Contrast evidence (calculated, not browser-measured)
Formula: WCAG 2.x relative luminance; see `contrast_table.txt`. All 21 token pairs reach AA (≥4.5:1) except one:
- ⚠️ Dark mode `.row.sel .rk` in production uses `#fff` on `--sel-accent #86efac` = **1.40:1 (fail)**. Prototypes add a `--sel-fg` token (`#052e16` on `#86efac` = 10.62:1). This is a prototype-only token; production unchanged. Flag for a later phase.
- Lowest passing pairs: light `--text-dim` on `--surface` 4.55:1; light `--com` on code-bg 4.55:1 (both 11–13px, borderline but AA).
- Dark non-code note text `#d1d5db` on `#0b1120` = 12.78:1 at 13.5px (neutral near-white, as agreed).

## Width budget (estimated, not rendered at 1366px)
At 1366px: main ≈ 1118px, code column 62% minus gap ≈ 682px, minus pre padding ≈ 656px, 13px mono ≈ 7.8px/char → ~84 columns, ~80 after the line-number gutter. 60-character budget fits with margin. Representative R3 row: lines 24–29 and 31 fit; line 30 (72 chars) overflows and scrolls horizontally, exactly as in production. Footer badge states "60 mono chars @ 1366px budget".

## Preservation checklist
- ✓ Layout2 code-dominant split (`--code-frac:62%`), code colours unchanged
- ✓ Variant B green selection + non-colour "selected" cue; sidebar active item aligned to selected row
- ✓ Neutral near-white dark non-code text, 13.5px dark / 12.5px light
- ✓ Option 3 compact facts `<dl>` + borderless `<details>`
- ✓ Sidebar labels, progress bar (static 60%), local theme control
- ✓ Local concept links (#notation, #io, #example), relative module links, bottom collapsible backlinks
- ✓ Math readable without renderer: HTML entities + `<sub>`, serif `.math` span, no MathJax/KaTeX
- ✓ No external assets, no network, no scripts, no downloads
- ✓ Identical substantive content in N1 and N2 (diff limited to titles, block order, micro-banner — see `n2_generation_check.png`)
- ✓ Worked example collapsible, labelled "illustrative inputs" and "outputs verified by verify_example.py"

## Limitations (honest)
- Static inspection + calculated contrast only. ⚠️ No browser rendering at 1366px, no screen-reader pass, no keyboard test executed.
- Row toggle, scroll-spy and progress update are **not** functional; labelled in the amber prototype banner.
- Theme radios: "Sys" uses `prefers-color-scheme`; cannot persist choice without JS.
- Only one code row (R3) is shown; full tutorial would carry R1–R5 and usage block.
- N2 micro-banner is the single deliberate content delta; if the committee wants a byte-identical body, remove it and N2 loses its mitigation.
- Column estimate assumes ~0.6em glyph width for the system mono font; actual font may vary ±5 columns.
