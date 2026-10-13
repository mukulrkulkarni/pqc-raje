# Module tutorial — layout options

Three self-contained mockups of the same-row, two-column per-range tutorial layout.
No external assets, no scripts, no `<link>` tags. All use the existing token set
(`--bg / --surface / --border / --accent / --code-bg`, `--s1..--s6` spacing scale)
and both light and dark palettes via `html[data-theme]`.

| File | Concept | Sidebar | Code column at 1366px |
|---|---|---|---|
| `layout1.html` | Dense same-row grid | 236px fixed, full descriptions | 537px = **68 chars** |
| `layout2.html` | Code-dominant split | 200px fixed, compact descriptions | 652px = **83 chars** |
| `layout3.html` | Expanding rail | 64px rail, expands to 248px on hover/focus | 661px = **84 chars** |

All three clear requirement (a) — the 60-monospace-character floor at 1366px with
no horizontal scroll — at 13px type on a 0.6em advance width.

---

## Layout 1 — Dense same-row grid

Every range is a bordered card. A header bar carries `R1 · Imports · L1–L8 · pure`,
and underneath the code and explanation sit in one grid with a shared divider.
The I/O summary is a single-line chip strip; the usage example reuses the exact
same 54/46 column split as the ranges.

**Pros**
- Strongest visual containment — the card border makes "this code goes with this prose" unambiguous.
- Row selection and toggle state read clearly (border + tinted header).
- I/O strip collapses four facts into one 36px band, versus a four-card grid.
- Usage example inherits the range rhythm, so the page has exactly one column ruleset.
- Richest sidebar: two-line entries with full jump descriptions.

**Cons**
- Narrowest code column of the three (68 chars). Fine for the 60-char floor but the least headroom for long signatures.
- Card chrome (borders + header bars on every range) is itself a form of visual weight.
- 236px sidebar is permanently spent, even for returning users.

---

## Layout 2 — Code-dominant split

No cards. Each range is a lightweight header rule (`R1 Imports L1–L8 ——————`)
with a bordered code block on the left at 62% and the explanation as a borderless
margin note on the right. The I/O summary disappears entirely as a dedicated
block — it is folded into a sticky top bar as a live signature line.

**Pros**
- Best whitespace economy of the three. Removing the explanation card border and the I/O card recovers roughly 120px of vertical space per screen.
- 83 chars of code — comfortable headroom above the floor.
- Sticky header keeps the signature and `raises` visible while scrolling any range.
- Margin-note style reads like good API documentation; prose does not compete with code for emphasis.
- Smallest sidebar footprint of the two fixed options at 200px.

**Cons**
- Weakest row containment. With no card border, a long explanation next to a short snippet can blur where one range ends and the next begins.
- Selection/toggle state must be carried by the code block border and the `Rk` badge alone — less obvious than Layout 1.
- Sticky top bar costs ~46px of permanent vertical space.
- Sidebar descriptions are truncated to one short line to fit 200px.

---

## Layout 3 — Expanding rail

A 64px icon rail showing only `R1 R2 R3 R4 EX` badges, expanding to 248px on
hover or `:focus-within` to reveal the jump descriptions. Each range header gains
a one-line summary next to the title, so the gist is readable without opening the
row. The I/O summary is a four-cell bordered strip using dividers instead of padding.

**Pros**
- Widest code column (84 chars) because the rail only costs 64px at rest.
- The per-row summary line in the header means a reader can skim all four ranges without reading any explanation column.
- I/O strip uses 1px dividers rather than gaps — four facts in one 44px band with no wasted gutter.
- Usage example packs output plus three meta facts (`exit 0`, `~2 ms`, `no network`) into the same height as the code.
- Rail expansion is keyboard-reachable via `:focus-within`, and the transition is disabled under `prefers-reduced-motion`.

**Cons**
- Jump descriptions are hidden at rest, which conflicts most directly with requirement (c) — they are present but not persistently visible.
- Hover-to-expand overlays content; on a trackpad this can fire accidentally.
- Icon-only theme toggle at rest relies on glyphs (☀ ☾ ⚙) plus `aria-label`, which is less explicit than visible text labels.
- Most CSS state of the three, so it is the most work to port into the real template.

---

## Recommendation

**Layout 2** best satisfies the brief as written: it posts the largest whitespace
reduction (requirement b) while giving the code column 83 characters, and it keeps
the sidebar descriptions permanently visible (requirement c), which Layout 3
sacrifices.

If row-boundary clarity turns out to matter more than density during review, the
cheapest fix is Layout 2 with Layout 1's card border restored on the selected row
only — that keeps the flat default state and reserves chrome for the active range.

Layout 3's header summary line is worth stealing regardless of which shell wins.
