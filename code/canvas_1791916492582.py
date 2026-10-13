
import os
output_path = "docs/design/module_tutorial_v2_1_spec.md"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

SPEC = r"""# Module Tutorial UI — v2.1 Specification
**Pattern: Option 2, Linked Callouts.** Left pane = source. Right column = numbered
callout cards. A shared integer is the only link between them. No connector lines.

Reference mockup: `docs/mock/module_tutorial_v2_1.html`
Target implementation: `scripts/module_docs_html.py`
Namespace: every selector is prefixed `tut-` and lives under `.tut`. Global site CSS is untouched.

---

## 0. Why Option 2 cannot overlap

v2.0 overlapped because connectors were drawn with absolute/SVG positioning across
two independently scrolling columns. v2.1 removes that class of bug by construction:

| Rule | Reason |
|---|---|
| R1. No `position:absolute` or `transform` anywhere in the tutorial layout. | Removes all out-of-flow boxes. |
| R2. No SVG/canvas connectors. The shared number **is** the connector. | Nothing to mis-measure. |
| R3. `position:sticky` is allowed only on `left:0` (rail) and the code column `top`. Sticky stays in flow and reserves its box. | Cannot collide. |
| R4. Both grid tracks use `minmax(0, …)`, and `.tut-col{min-width:0}`. | A long code line can never widen its track and shove the doc column off-screen. |
| R5. Code lines use `white-space:pre` + one horizontal scroller. | Row height is constant, so the rail and the lines stay in lockstep. |
| R6. The range tag is a **grid cell** (`grid-column:1; grid-row:1/-1`), not an overlay. | Its height is derived from the segment, never guessed. |
| R7. Card header uses `flex-wrap:wrap`. | Long titles wrap, badges never collide. |
| R8. `scroll-padding-top` + `scroll-margin-top` = header height + 16px. | Targets never land under the sticky header. |
| R9. Ranges must be **disjoint and ascending**. No nesting. | Guarantees a clean one-segment-per-range partition. |

R9 is a data contract, not a style. Enforce it in Python (see §7).

---

## 1. Tokens

v2.1 adds **no new colours**. It consumes Getting Started v2 tokens, with fallbacks so the
file still opens standalone (`file://`, no server):

```
--t-bg --t-surface --t-surface-2 --t-border --t-border-sf
--t-text --t-muted --t-accent --t-accent-sf --t-mono --t-sans
```

Local layout tokens only (4px base scale):

| Token | Value | Use |
|---|---|---|
| `--tut-s1..s7` | 4, 8, 12, 16, 24, 32, 48 | the only spacing values allowed |
| `--tut-gap` | 32px (24px <1200) | column gap |
| `--tut-radius` / `-sm` | 10px / 6px | cards, panes / chips, buttons |
| `--tut-maxw` | 1440px | page shell |
| `--tut-header-h` | `var(--header-h, 56px)` | sticky offset source |
| `--tut-scroll-pad` | `header-h + 16px` | anchor landing offset |
| `--tut-code-fs` / `--tut-line-h` | 13px / 22px | **fixed** code line box |
| `--tut-rail-w` / `--tut-num-w` | 64px / 40px | range rail / line numbers |

> Never hard-code a pixel value in a new rule. If a value is missing, add a token.

---

## 2. Layout

### 2.1 Page shell
`.tut-wrap` — `max-width:1440px`, `margin-inline:auto`, padding `24px 24px 48px`,
`scroll-padding-top: var(--tut-scroll-pad)`.

Header block `.tut-head`: eyebrow (11px, uppercase, muted) → H1 (`clamp(22px,2.4vw,30px)`)
→ lede (15px/1.65, muted, `max-width:68ch`). Bottom margin 24px.

### 2.2 The two-column grid
```css
.tut-grid{
  display:grid;
  grid-template-columns: minmax(0,1.05fr) minmax(0,1fr);
  gap: var(--tut-gap);
  align-items:start;
}
```
Code gets 1.05fr: source lines are wider than prose, and prose is capped at 66ch anyway,
so the extra space is spent where it is needed.

`align-items:start` is required — without it both columns stretch to the tallest, and the
sticky code pane stops working.

### 2.3 Sticky code pane
```css
.tut-col--code{
  position:sticky;
  top: var(--tut-scroll-pad);
  max-height: calc(100vh - var(--tut-scroll-pad) - var(--tut-s5));
  display:flex; flex-direction:column;
}
```
The pane is pinned; the doc column scrolls past it. Inside the pane, only `.tut-code`
scrolls. One scroller per axis, never nested.

### 2.4 Responsive

| Breakpoint | Behaviour |
|---|---|
| ≥1200px | Two columns, gap 32, pane sticky, rail 64px. |
| 900–1199px | Two columns, gap 24, rail 56px. |
| `max-height:700px` and ≥900px | Pane un-sticks, `max-height:560px`. Short laptop windows otherwise show ~6 lines. |
| <900px | **Single column.** Pane first, static, `max-height:58vh`, scrolls internally. Rail 48px, numbers 34px, code 12.5px. Range sub-labels hidden. |
| <560px | Card `kind` badge hidden, note badge drops to its own line. |
| `print` | Single column, all heights released, nothing clipped. |

In stacked mode the code pane is **not** duplicated. "Show the code" scrolls the page to
the pane and `:target` highlights the segment inside it. One DOM, two layouts.

---

## 3. Component — code-pane range tag

### 3.1 Structure
The file is partitioned into **segments**. A segment is a contiguous run of lines that is
either *ranged* (belongs to exactly one callout) or *plain*. Segments stack vertically.

```html
<div class="tut-seg tut-seg--ranged" id="r2">
  <a class="tut-tag" href="#c2" aria-label="Go to note 2: Threshold ordering rule">
    <span class="tut-tag__chip">2</span>
    <span class="tut-tag__bracket" aria-hidden="true"></span>
    <span class="tut-tag__lines">14-20</span>
  </a>
  <span class="tut-ln" aria-hidden="true">14</span><span class="tut-src">…</span>
  …
</div>
```
Plain segments emit `<span class="tut-rail-spacer" aria-hidden="true">` so the rail width
never changes between segments.

### 3.2 Style
- Segment: 3-col grid `[rail][numbers][source]`, `grid-auto-rows:22px`, `min-width:max-content`.
- Ranged segment resting tint: `rgba(accent, .035)` — just enough to read as a group.
- Tag: `grid-column:1; grid-row:1/-1`, `position:sticky; left:0`, column flex,
  surface background, 1px right border. Horizontal pin only, so the rail survives
  sideways scrolling.
- Chip: 20px pill, 1px accent border, `--t-accent-sf` fill, accent text, 11px/600.
- Bracket: 2px wide, `flex:1`, `rgba(accent,.45)` — a quiet vertical extent marker that
  grows with the segment at zero layout cost.
- Sub-label: the line range, 10px muted. Hidden <900px.

### 3.3 States
| State | Change |
|---|---|
| rest | chip outlined |
| hover / focus-visible | chip fills accent, text flips to `--t-bg` |
| focus-visible | 2px accent outline, offset 2 |
| `:target` (selected) | segment background → `--t-accent-sf`, `border-left-color` → accent, chip fills, bracket goes full accent |

Selection is **pure CSS `:target`**. No JavaScript, so it survives the hardened CSP and
works in the standalone file. Do not add JS for this.

---

## 4. Component — doc callout card

```html
<article class="tut-card" id="c2" aria-labelledby="c2-t">
  <div class="tut-card__head">
    <span class="tut-card__chip" aria-hidden="true">2</span>
    <h3 class="tut-card__title" id="c2-t">Threshold ordering rule</h3>
    <span class="tut-card__kind">Constraint</span>
  </div>
  <p class="tut-card__body">…</p>
  <div class="tut-formula" role="figure" aria-label="Formula for …">0 &lt;= q &lt;= p &lt;= v</div>
  <div class="tut-card__foot">
    <a class="tut-link" href="#r2">Show the code <span class="tut-link__range">lines 14-20</span>
       <span class="tut-sr">of config.py</span></a>
    <span class="tut-card__note">Raises ValueError.</span>
  </div>
</article>
```

- Card: surface, 1px border, **3px left border** (the state channel), radius 10,
  padding `16px 24px 24px`, stack gap 16.
- Chip: 22px pill, identical treatment to the rail chip. This visual rhyme is the whole
  linking mechanism — never restyle one without the other.
- Title: 15.5px/620, `flex:1 1 220px; min-width:0` so it wraps rather than pushing the badge out.
- Kind badge: 10px uppercase, muted, 1px soft border. **Text only — no colour coding.**
- Body: 14px/1.68, `max-width:66ch`. Inline `code` on surface-2 with a soft border.
- Formula block: surface-2, mono 13px, `white-space:pre; overflow-x:auto`. Scrolls, never wraps mid-equation.
- Foot: top divider, flex-wrap. Primary action left, note right via `margin-left:auto`.
- `:target`: accent border all round, accent left border, slightly lifted background,
  1px accent-soft ring. No movement, no scale — the reader's eye is already there.

### 4.1 Allowed `kind` values (max 4)
`Data shape` · `Constraint` · `Formula` · `I/O`
Plus optional `Engine link` for the "how this feeds the full pipeline" card.
Adding a sixth kind requires a design review.

---

## 5. Interaction microcopy (ASD-STE100)

Short sentences. One instruction per sentence. Active voice. Approved vocabulary.
Use **"select"**, not "click" or "tap" — it is device-neutral and STE-approved.

| Location | Text |
|---|---|
| Page lede | "The code is on the left. The notes are on the right. Each note has a number. The same number marks the related lines in the code. Select a number to move between the two." |
| Card action | "Show the code" + `lines 14-20` |
| Card action, screen-reader tail | "of config.py" (visually hidden) |
| Range tag `aria-label` | "Go to note 2: Threshold ordering rule" |
| Pane meta | "33 lines · 4 notes" |
| Card note, validation | "Raises ValueError." |
| Card note, purity | "Pure function." |
| Card note, order | "Read this first." |
| Section title | "What the module does" |
| Stacked-mode hint (<900px, optional) | "The code is above. Select a number to go to it." |
| Empty state (module with no notes) | "This module has no notes. Read the code below." |

Rules:
- Never write "simply", "just", "easily", or "obviously".
- Never promise motion ("the code will slide into view") — motion is a user preference.
- Keep card titles ≤ 5 words. Keep notes ≤ 3 words.
- Use the same verb for the same action everywhere. "Show", not "View"/"Jump"/"Go".

---

## 6. Anti-clutter guidance

The failure mode of linked callouts is a page that looks like a Christmas tree. Hard limits:

1. **≤ 8 callouts per page.** More than 8 means the module should be split, or the notes
   should be merged. A 50-line module rarely needs more than 5.
2. **One accent colour.** Kind is carried by *text*, never by hue. No red/green/amber card
   variants. This is also an accessibility win: no information by colour alone.
3. **Ranges are disjoint and ascending.** No nested or crossing ranges. If two notes want
   the same lines, merge the notes.
4. **A range covers ≥ 2 lines.** Single-line notes are noise; fold them into a neighbour.
5. **≤ 2 badges in a card header** (kind + nothing else). The foot note is the third
   maximum, and it is optional.
6. **≤ 2 paragraphs + 1 formula per card.** If a card needs more, it is a section, not a callout.
7. **Resting tint ≤ 4% accent.** Ranged segments must be *findable*, not *loud*. Only the
   selected segment is allowed to be obvious.
8. **No icons.** Numbers and words only. Icons add a legend the reader must learn.
9. **Plain segments stay plain.** Do not tint, do not label, do not dim them — dimming
   unselected code is a readability regression.
10. **One divider per card** (the foot rule). No dividers between paragraphs.

---

## 7. Implementation notes for `scripts/module_docs_html.py`

Keep each function under the 50-line cap. Suggested split:

```
TUT_CSS                      # module-level string constant, the §1–4 CSS
_partition(lines, ranges)    # -> [(kind, meta, start, [lines])]   enforces R9
_render_segment(seg)         # -> str    one .tut-seg
_render_card(note)           # -> str    one .tut-card
render_tutorial(module, notes)  # -> str  shell + grid, calls the two above
```

**Note data contract** (one dict per callout, authored per module):
```python
{"n": 2,                      # assigned, not authored: index+1
 "title": "Threshold ordering rule",   # <= 5 words
 "kind": "Constraint",                 # one of the 4 (+1) allowed values
 "start": 14, "end": 20,               # 1-based, inclusive, end >= start+1
 "body": ["<p-safe html>", ...],       # <= 2 entries
 "formula": "0 <= q <= p <= v" or None,
 "note": "Raises ValueError." or None} # <= 3 words
```

**Validation to add (fail the build, do not render a broken page):**
- `end >= start + 1` (rule 6.4)
- ranges sorted by `start`, and `ranges[i].start > ranges[i-1].end` (rule R9 / 6.3)
- `end <= len(source_lines)`
- `len(notes) <= 8` (rule 6.1)
- `kind in ALLOWED_KINDS` (rule 4.1)
- `len(body) <= 2` (rule 6.6)

**Escaping:** `html.escape()` every source line. Emit `&nbsp;` for an empty line so the
grid row keeps its height. Body HTML is author-controlled — allow only `<code>`, `<em>`,
`<strong>`; escape everything else.

**IDs:** `r{n}` on the segment, `c{n}` on the card. `aria-labelledby="c{n}-t"` on the card,
`id="c{n}-t"` on its title. These four IDs are the entire linking contract.

**CSP:** the design is zero-JavaScript. Ship `TUT_CSS` inside the existing `<style>` block
that Getting Started v2 already emits, so `style-src 'self' 'unsafe-inline'` is unchanged
and no new directive is needed. Do not add an external script file.

**Global safety:** `TUT_CSS` must not contain a bare element selector (`h3{…}`, `a{…}`) or
a `:root{…}` block. Every rule starts with `.tut`. A quick preflight grep for
`^\s*[^.@}/\s]` inside `TUT_CSS` catches regressions.

---

## 8. Accessibility checklist

- [x] Both links of every pair are real `<a href="#…">` — keyboard and no-JS reachable.
- [x] Code scroller is `tabindex="0"` with `role="region"` and a label, so keyboard users
      can scroll it.
- [x] Line numbers and the bracket are `aria-hidden` — they are decoration.
- [x] The rail chip duplicates the card chip, so it is `aria-hidden` there and the link
      carries an `aria-label` with the note title.
- [x] Focus ring: 2px accent, 2px offset, on every interactive element.
- [x] `prefers-reduced-motion: reduce` kills all transitions; smooth scroll is only
      enabled under `no-preference`.
- [x] State is never colour-only: `:target` changes border weight and background together,
      and the kind badge is text.
- [x] Body text 14px/1.68, prose capped at 66ch.
- [ ] Verify accent-on-surface contrast ≥ 4.5:1 against the final GS v2 accent token.

---

## 9. Review-gate mapping

| Gate | What to check |
|---|---|
| UI/UX | Rendered page at 1440 / 1024 / 768 / 375 and at 700px height. No overlap, no clipped text, no double scrollbars. |
| Engineering | Each render function ≤ 50 lines. Validation raises on bad note data. Tests cover partition + each validation rule, including negatives. |
| Security | No new CSP directive. No external asset. No JS. Source lines escaped. |
| Scientific Critic | Formula strings match the engine's actual maths. Threshold ordering and normalisation claims are correct. |
"""

with open(output_path, "w", encoding="utf-8") as fh:
    fh.write(SPEC)
print("wrote", output_path, len(SPEC), "bytes")
