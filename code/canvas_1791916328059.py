
import os, html, textwrap

os.makedirs(os.path.dirname(output_path), exist_ok=True)

CSS = r"""
/* ============================================================
   MODULE TUTORIAL v2.1  —  Option 2: Linked Callouts
   Scope: every rule is nested under .tut  (no global leakage)
   Tokens: consumed from Getting Started v2 with safe fallbacks
   ============================================================ */
.tut{
  /* --- inherited GS-v2 tokens (fallbacks only if host omits) --- */
  --t-bg:        var(--bg,        #0f1115);
  --t-surface:   var(--surface,   #161a21);
  --t-surface-2: var(--surface-2, #1c222b);
  --t-border:    var(--border,    #2a313d);
  --t-border-sf: var(--border-soft, #222935);
  --t-text:      var(--text,      #e6e9ef);
  --t-muted:     var(--muted,     #9aa4b4);
  --t-accent:    var(--accent,    #5b9dff);
  --t-accent-sf: var(--accent-soft, rgba(91,157,255,.14));
  --t-mono:      var(--font-mono, ui-monospace, SFMono-Regular, Menlo, Consolas, monospace);
  --t-sans:      var(--font-sans, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif);

  /* --- v2.1 local layout tokens (4px base scale) --- */
  --tut-s1: 4px;  --tut-s2: 8px;  --tut-s3: 12px; --tut-s4: 16px;
  --tut-s5: 24px; --tut-s6: 32px; --tut-s7: 48px;
  --tut-gap: var(--tut-s6);
  --tut-radius: 10px;
  --tut-radius-sm: 6px;
  --tut-maxw: 1440px;
  --tut-header-h: var(--header-h, 56px);   /* site header offset */
  --tut-scroll-pad: calc(var(--tut-header-h) + var(--tut-s4));

  /* code metrics — FIXED line box keeps rail + lines in lockstep */
  --tut-code-fs: 13px;
  --tut-line-h: 22px;
  --tut-rail-w: 64px;   /* range-tag rail */
  --tut-num-w: 40px;    /* line numbers   */

  color: var(--t-text);
  font-family: var(--t-sans);
}

/* ---------- 1. PAGE SHELL ---------- */
.tut-wrap{
  max-width: var(--tut-maxw);
  margin-inline: auto;
  padding: var(--tut-s5) var(--tut-s5) var(--tut-s7);
  /* every :target lands below the sticky header, never under it */
  scroll-padding-top: var(--tut-scroll-pad);
}
.tut-head{ margin-bottom: var(--tut-s5); max-width: 72ch; }
.tut-eyebrow{
  font-size: 11px; letter-spacing:.09em; text-transform: uppercase;
  color: var(--t-muted); margin:0 0 var(--tut-s2);
}
.tut-title{ font-size: clamp(22px, 2.4vw, 30px); line-height:1.25; margin:0 0 var(--tut-s3); font-weight:650; }
.tut-lede{ margin:0; color: var(--t-muted); font-size: 15px; line-height:1.65; }

/* ---------- 2. THE GRID (overlap-proof) ----------
   minmax(0,·) on BOTH tracks is mandatory: it stops a long code
   line from forcing the column wider than its share and pushing
   the doc column out of the viewport. No float, no absolute
   positioning, no negative margins anywhere in this layout. */
.tut-grid{
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(0, 1fr);
  gap: var(--tut-gap);
  align-items: start;        /* panes never stretch into each other */
}
.tut-col{ min-width: 0; }    /* belt-and-braces against overflow */

/* code pane tracks the reader; doc column scrolls past it */
.tut-col--code{
  position: sticky;
  top: var(--tut-scroll-pad);
  max-height: calc(100vh - var(--tut-scroll-pad) - var(--tut-s5));
  display: flex; flex-direction: column;
}

/* ---------- 3. CODE PANE ---------- */
.tut-pane{
  background: var(--t-surface);
  border: 1px solid var(--t-border);
  border-radius: var(--tut-radius);
  overflow: hidden;                 /* clips nothing but the corners */
  display: flex; flex-direction: column; min-height: 0;
}
.tut-pane__bar{
  display:flex; align-items:center; gap: var(--tut-s3);
  padding: var(--tut-s3) var(--tut-s4);
  border-bottom: 1px solid var(--t-border-sf);
  background: var(--t-surface-2);
  flex: 0 0 auto;
}
.tut-pane__file{ font-family: var(--t-mono); font-size: 12.5px; color: var(--t-text); }
.tut-pane__meta{ margin-left:auto; font-size: 11.5px; color: var(--t-muted); }

.tut-code{
  margin:0; min-height:0; flex:1 1 auto;
  overflow: auto;                   /* the ONLY scroll container here */
  scroll-padding-top: var(--tut-s4);
  font-family: var(--t-mono);
  font-size: var(--tut-code-fs);
  line-height: var(--tut-line-h);
}

/* A segment = one contiguous run of lines, ranged or plain.
   Segments stack vertically. Nothing overlaps because the tag
   lives in its own grid COLUMN and spans the segment's rows. */
.tut-seg{
  display: grid;
  grid-template-columns: var(--tut-rail-w) var(--tut-num-w) minmax(0, 1fr);
  grid-auto-rows: var(--tut-line-h);
  min-width: max-content;           /* long lines scroll, never wrap */
  border-left: 3px solid transparent;
  scroll-margin-top: var(--tut-s4);
  transition: background-color .18s ease, border-color .18s ease;
}
.tut-seg--ranged{ background: color-mix(in srgb, var(--t-accent) 3%, transparent); }

/* the range tag: in-flow, spans all rows of its segment */
.tut-tag{
  grid-column: 1; grid-row: 1 / -1;
  position: sticky; left: 0; z-index: 2;   /* horizontal pin only */
  display:flex; flex-direction:column; align-items:center; gap: var(--tut-s1);
  padding: var(--tut-s1) var(--tut-s2) var(--tut-s2);
  background: var(--t-surface);
  border-right: 1px solid var(--t-border-sf);
  text-decoration: none; color: inherit;
}
.tut-tag__chip{
  display:inline-flex; align-items:center; justify-content:center;
  min-width: 20px; height: 20px; padding: 0 5px;
  border-radius: 999px;
  border: 1px solid var(--t-accent);
  background: var(--t-accent-sf);
  color: var(--t-accent);
  font: 600 11px/1 var(--t-sans);
  flex: 0 0 auto;
}
.tut-tag__bracket{
  flex: 1 1 auto; width: 2px; min-height: 6px;
  border-radius: 1px;
  background: color-mix(in srgb, var(--t-accent) 45%, transparent);
}
.tut-tag__lines{ font: 500 10px/1 var(--t-sans); color: var(--t-muted); letter-spacing:.02em; }
.tut-tag:hover .tut-tag__chip,
.tut-tag:focus-visible .tut-tag__chip{ background: var(--t-accent); color: var(--t-bg); }

.tut-ln{
  grid-column: 2; text-align: right;
  padding-right: var(--tut-s3);
  color: var(--t-muted); opacity:.55;
  user-select: none; font-variant-numeric: tabular-nums;
}
.tut-src{
  grid-column: 3; white-space: pre;
  padding-right: var(--tut-s5);
  color: var(--t-text);
}
/* plain (unranged) segments keep the rail width so nothing shifts */
.tut-seg--plain .tut-rail-spacer{
  grid-column:1; grid-row: 1 / -1;
  position: sticky; left:0; z-index:2;
  background: var(--t-surface);
  border-right: 1px solid var(--t-border-sf);
}

/* --- selection, driven by :target only (works with JS disabled) --- */
.tut-seg:target{
  background: var(--t-accent-sf);
  border-left-color: var(--t-accent);
}
.tut-seg:target .tut-tag__chip{ background: var(--t-accent); color: var(--t-bg); }
.tut-seg:target .tut-tag__bracket{ background: var(--t-accent); }

/* ---------- 4. DOC COLUMN — CALLOUT CARDS ---------- */
.tut-doc{ display:flex; flex-direction:column; gap: var(--tut-s4); }
.tut-sectiontitle{
  margin: var(--tut-s5) 0 0; font-size: 12px; letter-spacing:.08em;
  text-transform: uppercase; color: var(--t-muted); font-weight:600;
}
.tut-sectiontitle:first-child{ margin-top:0; }

.tut-card{
  background: var(--t-surface);
  border: 1px solid var(--t-border);
  border-left: 3px solid var(--t-border);
  border-radius: var(--tut-radius);
  padding: var(--tut-s4) var(--tut-s5) var(--tut-s5);
  scroll-margin-top: var(--tut-scroll-pad);
  transition: border-color .18s ease, box-shadow .18s ease, background-color .18s ease;
}
.tut-card__head{
  display:flex; align-items:center; gap: var(--tut-s3);
  flex-wrap: wrap;                 /* wraps instead of colliding */
  margin-bottom: var(--tut-s3);
}
.tut-card__chip{
  display:inline-flex; align-items:center; justify-content:center;
  min-width:22px; height:22px; padding:0 6px; border-radius:999px;
  border:1px solid var(--t-accent); background: var(--t-accent-sf);
  color: var(--t-accent); font:600 11.5px/1 var(--t-sans); flex:0 0 auto;
}
.tut-card__title{ margin:0; font-size: 15.5px; font-weight:620; line-height:1.35; flex:1 1 220px; min-width:0; }
.tut-card__kind{
  font:600 10px/1 var(--t-sans); letter-spacing:.08em; text-transform:uppercase;
  color: var(--t-muted); border:1px solid var(--t-border-sf);
  padding:4px 7px; border-radius: var(--tut-radius-sm); white-space:nowrap;
}
.tut-card__body{ margin:0; font-size:14px; line-height:1.68; color: var(--t-text); }
.tut-card__body + .tut-card__body{ margin-top: var(--tut-s3); }
.tut-card__body code{
  font-family: var(--t-mono); font-size: 12.5px;
  background: var(--t-surface-2); border:1px solid var(--t-border-sf);
  padding: 1px 5px; border-radius: 4px;
}
.tut-formula{
  margin: var(--tut-s3) 0 0; padding: var(--tut-s3) var(--tut-s4);
  background: var(--t-surface-2); border:1px solid var(--t-border-sf);
  border-radius: var(--tut-radius-sm);
  font-family: var(--t-mono); font-size: 13px; line-height:1.6;
  overflow-x: auto; white-space: pre;
}
.tut-card__foot{
  display:flex; align-items:center; gap: var(--tut-s3); flex-wrap: wrap;
  margin-top: var(--tut-s4); padding-top: var(--tut-s3);
  border-top: 1px solid var(--t-border-sf);
}
.tut-link{
  display:inline-flex; align-items:center; gap: var(--tut-s2);
  font: 600 12.5px/1 var(--t-sans); text-decoration:none;
  color: var(--t-accent);
  border:1px solid var(--t-border); border-radius: var(--tut-radius-sm);
  padding: 7px var(--tut-s3); background: transparent;
  transition: background-color .15s ease, border-color .15s ease;
}
.tut-link:hover{ background: var(--t-accent-sf); border-color: var(--t-accent); }
.tut-link__range{ font-family: var(--t-mono); font-weight:500; color: var(--t-muted); }
.tut-card__note{ font-size:12px; color: var(--t-muted); margin-left:auto; }

.tut-card:target{
  border-color: var(--t-accent);
  border-left-color: var(--t-accent);
  background: color-mix(in srgb, var(--t-accent) 5%, var(--t-surface));
  box-shadow: 0 0 0 1px var(--t-accent-sf);
}

/* ---------- 5. FOCUS / MOTION / A11Y ---------- */
.tut a:focus-visible, .tut [tabindex]:focus-visible{
  outline: 2px solid var(--t-accent); outline-offset: 2px; border-radius: 4px;
}
@media (prefers-reduced-motion: no-preference){
  html{ scroll-behavior: smooth; }
}
@media (prefers-reduced-motion: reduce){
  .tut *{ transition: none !important; }
}
.tut-sr{ position:absolute; width:1px; height:1px; overflow:hidden; clip-path: inset(50%); white-space:nowrap; }

/* ---------- 6. RESPONSIVE ---------- */
/* md: two columns, pane no longer pinned (short viewports) */
@media (max-width: 1199px){
  .tut{ --tut-gap: var(--tut-s5); --tut-rail-w: 56px; }
}
@media (max-height: 700px) and (min-width: 900px){
  .tut-col--code{ position: static; max-height: 560px; }
}
/* sm: single column. Code pane sits on top, capped, scrolls inside. */
@media (max-width: 899px){
  .tut-wrap{ padding: var(--tut-s4) var(--tut-s4) var(--tut-s6); }
  .tut-grid{ grid-template-columns: minmax(0, 1fr); gap: var(--tut-s5); }
  .tut-col--code{ position: static; max-height: none; }
  .tut-pane{ max-height: 58vh; }
  .tut{ --tut-rail-w: 48px; --tut-num-w: 34px; --tut-code-fs: 12.5px; }
  .tut-card{ padding: var(--tut-s4); }
  .tut-tag__lines{ display:none; }   /* first clutter cut on small screens */
}
@media (max-width: 560px){
  .tut-card__kind{ display:none; }   /* second clutter cut */
  .tut-card__note{ margin-left:0; flex-basis:100%; }
}
@media print{
  .tut-col--code{ position: static; max-height:none; }
  .tut-pane{ max-height:none; }
  .tut-grid{ grid-template-columns: minmax(0,1fr); }
}
"""

# ---- demo content ---------------------------------------------------------
CODE_SEGS = [
    ("plain", None, 1, [
        '"""Configuration loading and validation for the ELECTRE III engine."""',
        'from __future__ import annotations',
        '',
        'from dataclasses import dataclass',
        '',
    ]),
    ("ranged", (1, "Criterion record", "6-12"), 6, [
        '@dataclass(frozen=True)',
        'class Criterion:',
        '    name: str',
        '    weight: float',
        '    q: float   # indifference threshold',
        '    p: float   # preference threshold',
        '    v: float   # veto threshold',
    ]),
    ("plain", None, 13, [
        '',
    ]),
    ("ranged", (2, "Threshold ordering rule", "14-20"), 14, [
        '    def validate(self) -> None:',
        '        if self.weight <= 0:',
        '            raise ValueError("weight must be positive")',
        '        if not 0 <= self.q <= self.p <= self.v:',
        '            raise ValueError("thresholds must satisfy q <= p <= v")',
        '        if self.p == self.q == self.v == 0:',
        '            raise ValueError("thresholds must not all be zero")',
    ]),
    ("plain", None, 21, [
        '',
    ]),
    ("ranged", (3, "Weight normalisation", "22-27"), 22, [
        'def normalise(criteria: list[Criterion]) -> list[float]:',
        '    total = sum(c.weight for c in criteria)',
        '    if total == 0:',
        '        raise ValueError("total weight must not be zero")',
        '    return [c.weight / total for c in criteria]',
        '',
    ]),
    ("ranged", (4, "Entry point and failure mode", "28-33"), 28, [
        'def load(path: str) -> list[Criterion]:',
        '    records = _read_records(path)',
        '    criteria = [Criterion(**r) for r in records]',
        '    for c in criteria:',
        '        c.validate()',
        '    return criteria',
    ]),
]

def seg_html(kind, meta, start, lines):
    rows = []
    if kind == "ranged":
        n, title, rng = meta
        rows.append(
            f'<a class="tut-tag" href="#c{n}" aria-label="Go to note {n}: {html.escape(title)}">'
            f'<span class="tut-tag__chip">{n}</span>'
            f'<span class="tut-tag__bracket" aria-hidden="true"></span>'
            f'<span class="tut-tag__lines">{rng}</span></a>'
        )
    else:
        rows.append('<span class="tut-rail-spacer" aria-hidden="true"></span>')
    for i, ln in enumerate(lines):
        rows.append(f'<span class="tut-ln" aria-hidden="true">{start+i}</span>'
                    f'<span class="tut-src">{html.escape(ln) or "&nbsp;"}</span>')
    cls = "tut-seg tut-seg--ranged" if kind == "ranged" else "tut-seg tut-seg--plain"
    idattr = f' id="r{meta[0]}"' if kind == "ranged" else ""
    return f'<div class="{cls}"{idattr} style="--_n:{len(lines)}">' + "".join(rows) + "</div>"

code_html = "\n".join(seg_html(*s) for s in CODE_SEGS)

CARDS = [
    (1, "Criterion record", "Data shape", "6-12",
     ["A <code>Criterion</code> holds one decision attribute. The record is frozen, so a criterion cannot change after the engine reads it.",
      "Three thresholds give the fuzzy outranking relation its shape. <code>q</code> is the indifference limit. <code>p</code> is the preference limit. <code>v</code> is the veto limit."],
     None, "Read this first."),
    (2, "Threshold ordering rule", "Constraint", "14-20",
     ["The method rejects any criterion that breaks the threshold order. This keeps the concordance index monotone."],
     "0 &lt;= q &lt;= p &lt;= v        (and not q = p = v = 0)",
     "Raises ValueError."),
    (3, "Weight normalisation", "Formula", "22-27",
     ["The function divides each weight by the sum of all weights. The result is a set of weights that add up to 1."],
     "w&#770;_j = w_j / &#931;_k w_k ,   &#931;_j w&#770;_j = 1",
     "Pure function."),
    (4, "Entry point and failure mode", "I/O", "28-33",
     ["<code>load()</code> reads the records, builds the criteria, and validates each one. The function stops at the first bad record.",
      "The full engine calls <code>load()</code> once. It then gives the normalised weights to the concordance step."],
     None, "Fails fast."),
]

def card_html(n, title, kind, rng, paras, formula, note):
    body = "".join(f'<p class="tut-card__body">{p}</p>' for p in paras)
    f = f'<div class="tut-formula" role="figure" aria-label="Formula for {html.escape(title)}">{formula}</div>' if formula else ""
    return f"""
      <article class="tut-card" id="c{n}" aria-labelledby="c{n}-t">
        <div class="tut-card__head">
          <span class="tut-card__chip" aria-hidden="true">{n}</span>
          <h3 class="tut-card__title" id="c{n}-t">{html.escape(title)}</h3>
          <span class="tut-card__kind">{html.escape(kind)}</span>
        </div>
        {body}{f}
        <div class="tut-card__foot">
          <a class="tut-link" href="#r{n}">Show the code
            <span class="tut-link__range">lines {rng}</span>
            <span class="tut-sr">of config.py</span></a>
          <span class="tut-card__note">{html.escape(note)}</span>
        </div>
      </article>"""

cards_html = "".join(card_html(*c) for c in CARDS)

DOC = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy"
      content="default-src 'none'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; base-uri 'none'; form-action 'none'">
<title>config.py — Module Tutorial (v2.1 mockup)</title>
<style>
:root{{
  --bg:#0f1115; --surface:#161a21; --surface-2:#1c222b;
  --border:#2a313d; --border-soft:#222935;
  --text:#e6e9ef; --muted:#9aa4b4;
  --accent:#5b9dff; --accent-soft:rgba(91,157,255,.14);
  --header-h:56px;
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--text);
     font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
     -webkit-font-smoothing:antialiased}}
.site-header{{position:sticky;top:0;z-index:50;height:var(--header-h);
  display:flex;align-items:center;gap:16px;padding:0 24px;
  background:rgba(15,17,21,.86);backdrop-filter:blur(8px);
  border-bottom:1px solid var(--border);font-size:13.5px}}
.site-header strong{{font-weight:650}}
.site-header span{{color:var(--muted)}}
{CSS}
</style>
</head>
<body>
<header class="site-header">
  <strong>ELECTRE III</strong><span>/ Docs / Modules / config</span>
</header>

<main class="tut">
 <div class="tut-wrap">
  <header class="tut-head">
    <p class="tut-eyebrow">Module tutorial &middot; v2.1</p>
    <h1 class="tut-title"><code style="font-family:var(--t-mono);font-size:.92em">electre3/config.py</code> &mdash; criteria and thresholds</h1>
    <p class="tut-lede">The code is on the left. The notes are on the right. Each note has a number.
       The same number marks the related lines in the code. Select a number to move between the two.</p>
  </header>

  <div class="tut-grid">
    <div class="tut-col tut-col--code">
      <section class="tut-pane" aria-label="Source code of config.py">
        <div class="tut-pane__bar">
          <span class="tut-pane__file">electre3/config.py</span>
          <span class="tut-pane__meta">33 lines &middot; 4 notes</span>
        </div>
        <div class="tut-code" tabindex="0" role="region" aria-label="Source code, scrollable">
{code_html}
        </div>
      </section>
    </div>

    <div class="tut-col">
      <div class="tut-doc">
        <h2 class="tut-sectiontitle">What the module does</h2>
        {cards_html}
      </div>
    </div>
  </div>
 </div>
</main>
</body>
</html>"""

with open(output_path, "w", encoding="utf-8") as fh:
    fh.write(DOC)

print("wrote", output_path, len(DOC), "bytes")
