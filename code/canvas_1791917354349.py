import sys, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.makedirs("build_v22", exist_ok=True)

CSS = r"""
/* ==========================================================================
   MODULE TUTORIAL v2.2
   Pattern: Option 2 - Linked Callouts  (unchanged from v2.1)
   New in v2.2: (a) light/dark/system theme, (b) green selection state,
                (c) sidebar that hosts the theme control.
   Scope rule: every selector begins with .tut, :root or html. No bare
   element selectors, so global site CSS is never touched.
   ========================================================================== */

/* --------------------------------------------------------------------------
   1. THEME TOKENS
   Resolution order (mutually exclusive by attribute value - no cascade race):
     :root                      -> LIGHT  (base)
     [data-theme="light"]       -> LIGHT  (explicit)
     [data-theme="system"] + @media(dark) -> DARK
     [data-theme="dark"]        -> DARK   (explicit)
   The attribute is always present in markup (default "system"), so with
   JavaScript blocked the page still resolves to the device setting.
   -------------------------------------------------------------------------- */
:root{
  color-scheme: light;

  --bg:#f6f7f9;  --surface:#ffffff;  --surface-2:#f1f3f6;
  --border:#d7dce4; --border-soft:#e7eaf0;
  --text:#141922; --muted:#5b6472;

  /* identity accent - links, numbers, focus. One hue, at rest. */
  --accent:#1d4ed8; --accent-soft:rgba(29,78,216,.10);

  /* SELECTION green - state only, never at rest. */
  --sel:#0b7a4b;                 /* 5.39:1 on #fff - text safe        */
  --sel-tint:rgba(11,122,75,.10);/* 10% - light surfaces need less    */
  --sel-ring:rgba(11,122,75,.26);
  --sel-on:#ffffff;              /* text on a filled green chip       */
  --sel-lift:0 1px 2px rgba(16,24,40,.05), 0 10px 22px -8px rgba(11,122,75,.30);

  --header-h:56px;
  --font-sans: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
}
:root[data-theme="light"]{ color-scheme: light; }

@media (prefers-color-scheme: dark){
  :root[data-theme="system"]{
    color-scheme: dark;
    --bg:#0f1115; --surface:#161a21; --surface-2:#1c222b;
    --border:#2a313d; --border-soft:#222935;
    --text:#e6e9ef; --muted:#9aa4b4;
    --accent:#5b9dff; --accent-soft:rgba(91,157,255,.14);
    --sel:#3ddc97;                   /* 9.87:1 on #161a21 */
    --sel-tint:rgba(61,220,151,.12); /* 12% - dark surfaces absorb tint */
    --sel-ring:rgba(61,220,151,.30);
    --sel-on:#0f1115;
    --sel-lift:0 10px 28px -10px rgba(61,220,151,.34);
  }
}
:root[data-theme="dark"]{
  color-scheme: dark;
  --bg:#0f1115; --surface:#161a21; --surface-2:#1c222b;
  --border:#2a313d; --border-soft:#222935;
  --text:#e6e9ef; --muted:#9aa4b4;
  --accent:#5b9dff; --accent-soft:rgba(91,157,255,.14);
  --sel:#3ddc97;
  --sel-tint:rgba(61,220,151,.12);
  --sel-ring:rgba(61,220,151,.30);
  --sel-on:#0f1115;
  --sel-lift:0 10px 28px -10px rgba(61,220,151,.34);
}

/* --------------------------------------------------------------------------
   2. PAGE CHROME (mockup shell only - the real site supplies this)
   -------------------------------------------------------------------------- */
*{box-sizing:border-box}
html{background:var(--bg)}
body{
  margin:0; background:var(--bg); color:var(--text);
  font-family:var(--font-sans); -webkit-font-smoothing:antialiased;
  transition: background-color .2s ease, color .2s ease;
}
.site-header{
  position:sticky; top:0; z-index:50; height:var(--header-h);
  display:flex; align-items:center; gap:16px; padding:0 24px;
  background:var(--surface); border-bottom:1px solid var(--border);
  font-size:13.5px;
}
.site-header strong{font-weight:650}
.site-header span{color:var(--muted)}

/* --------------------------------------------------------------------------
   3. TUTORIAL SCOPE + LOCAL LAYOUT TOKENS
   -------------------------------------------------------------------------- */
.tut{
  --t-bg:        var(--bg,        #f6f7f9);
  --t-surface:   var(--surface,   #ffffff);
  --t-surface-2: var(--surface-2, #f1f3f6);
  --t-border:    var(--border,    #d7dce4);
  --t-border-sf: var(--border-soft, #e7eaf0);
  --t-text:      var(--text,      #141922);
  --t-muted:     var(--muted,     #5b6472);
  --t-accent:    var(--accent,    #1d4ed8);
  --t-accent-sf: var(--accent-soft, rgba(29,78,216,.10));
  --t-sel:       var(--sel,       #0b7a4b);
  --t-sel-tint:  var(--sel-tint,  rgba(11,122,75,.10));
  --t-sel-ring:  var(--sel-ring,  rgba(11,122,75,.26));
  --t-sel-on:    var(--sel-on,    #ffffff);
  --t-sel-lift:  var(--sel-lift,  0 10px 22px -8px rgba(11,122,75,.30));
  --t-mono:      var(--font-mono, ui-monospace, SFMono-Regular, Menlo, Consolas, monospace);
  --t-sans:      var(--font-sans, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif);

  /* 4px base scale - the only spacing values allowed */
  --tut-s1:4px; --tut-s2:8px; --tut-s3:12px; --tut-s4:16px;
  --tut-s5:24px; --tut-s6:32px; --tut-s7:48px;
  --tut-gap: var(--tut-s6);
  --tut-radius:10px; --tut-radius-sm:6px;
  --tut-maxw:1520px;
  --tut-side-w:232px;
  --tut-header-h: var(--header-h, 56px);
  --tut-scroll-pad: calc(var(--tut-header-h) + var(--tut-s4));
  --tut-code-fs:13px; --tut-line-h:22px;
  --tut-rail-w:64px;  --tut-num-w:40px;

  color: var(--t-text);
  font-family: var(--t-sans);
}

/* --------------------------------------------------------------------------
   4. PAGE SHELL + 3-COLUMN LAYOUT  (overlap-proof: see spec R1-R12)
   -------------------------------------------------------------------------- */
.tut-wrap{
  max-width: var(--tut-maxw); margin-inline:auto;
  padding: var(--tut-s5) var(--tut-s5) var(--tut-s7);
  scroll-padding-top: var(--tut-scroll-pad);
}
.tut-head{ margin-bottom: var(--tut-s5); max-width:78ch; }
.tut-eyebrow{ font-size:11px; letter-spacing:.09em; text-transform:uppercase;
  color:var(--t-muted); margin:0 0 var(--tut-s2); }
.tut-title{ font-size:clamp(22px,2.4vw,30px); line-height:1.25; margin:0 0 var(--tut-s3); font-weight:650; }
.tut-lede{ margin:0; color:var(--t-muted); font-size:15px; line-height:1.65; max-width:68ch; }

.tut-layout{
  display:grid;
  grid-template-columns: var(--tut-side-w) minmax(0,1.15fr) minmax(0,1fr);
  gap: var(--tut-gap);
  align-items:start;
}
.tut-col{ min-width:0; }

.tut-col--code{
  position:sticky; top:var(--tut-scroll-pad);
  max-height: calc(100vh - var(--tut-scroll-pad) - var(--tut-s5));
  display:flex; flex-direction:column;
}

/* --------------------------------------------------------------------------
   5. SIDEBAR  (new in v2.2 - hosts the theme control)
   -------------------------------------------------------------------------- */
.tut-side{
  position:sticky; top:var(--tut-scroll-pad);
  min-width:0;
  display:flex; flex-direction:column; gap:var(--tut-s5);
  padding: var(--tut-s4);
  background: var(--t-surface);
  border:1px solid var(--t-border);
  border-radius: var(--tut-radius);
}
.tut-side__t{
  margin:0 0 var(--tut-s3); font:600 10.5px/1 var(--t-sans);
  letter-spacing:.09em; text-transform:uppercase; color:var(--t-muted);
}
.tut-nav{ list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:2px; }
.tut-nav li{ min-width:0; }
.tut-nav a{
  display:block; min-width:0;
  padding:6px var(--tut-s2); border-radius:var(--tut-radius-sm);
  font:500 13px/1.4 var(--t-sans); color:var(--t-muted); text-decoration:none;
  overflow-wrap:anywhere;
}
.tut-nav a:hover{ background:var(--t-surface-2); color:var(--t-text); }
.tut-nav a[aria-current="page"]{
  color:var(--t-text); font-weight:600; background:var(--t-accent-sf);
  box-shadow: inset 2px 0 0 var(--t-accent);
}
.tut-jump{ list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:1px; counter-reset:none; }
.tut-jump a{
  display:flex; gap:var(--tut-s2); align-items:baseline; min-width:0;
  padding:5px var(--tut-s2); border-radius:var(--tut-radius-sm);
  font:400 12.5px/1.45 var(--t-sans); color:var(--t-muted); text-decoration:none;
}
.tut-jump a:hover{ background:var(--t-surface-2); color:var(--t-text); }
.tut-jump b{ font:600 11px/1.6 var(--t-mono); color:var(--t-muted); flex:0 0 auto; }
.tut-jump span{ min-width:0; overflow-wrap:anywhere; }

/* --- 5.1 Theme control ---------------------------------------------------- */
.tut-theme{
  margin:0; padding:var(--tut-s4) 0 0; border:0;
  border-top:1px solid var(--t-border-sf);
  min-width:0;
}
.tut-theme__legend{
  padding:0; margin:0 0 var(--tut-s3);
  font:600 10.5px/1 var(--t-sans); letter-spacing:.09em;
  text-transform:uppercase; color:var(--t-muted);
}
.tut-theme__set{
  display:flex; min-width:0;
  background:var(--t-surface-2);
  border:1px solid var(--t-border);
  border-radius:var(--tut-radius-sm);
  padding:3px;
  gap:2px;
}
/* The input stays IN FLOW at 1px. No position:absolute anywhere. */
.tut-theme__in{
  appearance:none; -webkit-appearance:none;
  width:1px; height:1px; flex:0 0 1px;
  margin:0 -1px 0 0; padding:0; border:0; opacity:0;
}
.tut-theme__lb{
  flex:1 1 0; min-width:0;
  display:flex; align-items:center; justify-content:center;
  padding:6px 2px; border-radius:4px;
  font:600 11.5px/1.2 var(--t-sans); color:var(--t-muted);
  cursor:pointer; user-select:none; text-align:center;
  transition: background-color .15s ease, color .15s ease;
}
.tut-theme__lb:hover{ color:var(--t-text); }
.tut-theme__in:checked + .tut-theme__lb{
  background:var(--t-surface); color:var(--t-text);
  box-shadow: 0 1px 2px var(--t-sel-ring), inset 0 0 0 1px var(--t-sel);
}
.tut-theme__in:focus-visible + .tut-theme__lb{
  outline:2px solid var(--t-accent); outline-offset:2px;
}
.tut-theme__hint{
  margin:var(--tut-s2) 0 0; font-size:11.5px; line-height:1.5; color:var(--t-muted);
}
.tut-theme__warn{ display:none; margin:var(--tut-s2) 0 0; font-size:11.5px; line-height:1.5; color:var(--t-muted); }
html.tut-nostore .tut-theme__warn{ display:block; }
/* No JavaScript -> no persistence and no attribute switching, so the control
   is hidden rather than shown dead. The page stays on the device setting. */
html.no-js .tut-theme{ display:none; }

/* --------------------------------------------------------------------------
   6. CODE PANE
   -------------------------------------------------------------------------- */
.tut-pane{
  background:var(--t-surface); border:1px solid var(--t-border);
  border-radius:var(--tut-radius); overflow:hidden;
  display:flex; flex-direction:column; min-height:0;
}
.tut-pane__bar{
  display:flex; align-items:center; gap:var(--tut-s3);
  padding:var(--tut-s3) var(--tut-s4);
  border-bottom:1px solid var(--t-border-sf);
  background:var(--t-surface-2); flex:0 0 auto;
}
.tut-pane__file{ font-family:var(--t-mono); font-size:12.5px; color:var(--t-text); }
.tut-pane__meta{ margin-left:auto; font-size:11.5px; color:var(--t-muted); }
.tut-code{
  margin:0; min-height:0; flex:1 1 auto; overflow:auto;
  scroll-padding-top:var(--tut-s4);
  font-family:var(--t-mono); font-size:var(--tut-code-fs); line-height:var(--tut-line-h);
}
.tut-seg{
  display:grid;
  grid-template-columns: var(--tut-rail-w) var(--tut-num-w) minmax(0,1fr);
  grid-auto-rows: var(--tut-line-h);
  min-width:max-content;
  border-left:3px solid transparent;
  scroll-margin-top:var(--tut-s4);
  transition: background-color .18s ease, border-color .18s ease, box-shadow .18s ease;
}
.tut-seg--ranged{ background:var(--t-accent-sf); }
.tut-tag{
  grid-column:1; grid-row:1 / -1;
  position:sticky; left:0; z-index:2;
  display:flex; flex-direction:column; align-items:center; gap:var(--tut-s1);
  padding:var(--tut-s1) var(--tut-s2) var(--tut-s2);
  background:var(--t-surface);
  border-right:1px solid var(--t-border-sf);
  text-decoration:none; color:inherit;
}
.tut-tag__chip{
  display:inline-flex; align-items:center; justify-content:center;
  min-width:20px; height:20px; padding:0 5px; border-radius:999px;
  border:1px solid var(--t-accent); background:var(--t-surface);
  color:var(--t-accent); font:600 11px/1 var(--t-sans); flex:0 0 auto;
  transition: background-color .15s ease, color .15s ease, border-color .15s ease;
}
.tut-tag__bracket{
  flex:1 1 auto; width:2px; min-height:6px; border-radius:1px;
  background:var(--t-accent); opacity:.45;
  transition: width .15s ease, opacity .15s ease, background-color .15s ease;
}
.tut-tag__lines{ font:500 10px/1 var(--t-sans); color:var(--t-muted); letter-spacing:.02em; }
.tut-tag:hover .tut-tag__chip,
.tut-tag:focus-visible .tut-tag__chip{ background:var(--t-accent); color:var(--t-surface); }
.tut-ln{
  grid-column:2; text-align:right; padding-right:var(--tut-s3);
  color:var(--t-muted); opacity:.6; user-select:none; font-variant-numeric:tabular-nums;
}
.tut-src{ grid-column:3; white-space:pre; padding-right:var(--tut-s5); color:var(--t-text); }
.tut-rail-spacer{
  grid-column:1; grid-row:1 / -1; position:sticky; left:0; z-index:2;
  background:var(--t-surface); border-right:1px solid var(--t-border-sf);
}

/* --- 6.1 SELECTED SEGMENT (green, strong) --------------------------------- */
.tut-seg:target{
  background: var(--t-sel-tint);
  border-left-color: var(--t-sel);
  box-shadow: inset 0 0 0 1px var(--t-sel-ring);
}
.tut-seg:target .tut-tag{ border-right-color: var(--t-sel); }
.tut-seg:target .tut-tag__chip{
  background: var(--t-sel); border-color: var(--t-sel); color: var(--t-sel-on);
}
.tut-seg:target .tut-tag__bracket{ background: var(--t-sel); opacity:1; width:3px; }
.tut-seg:target .tut-tag__lines{ color: var(--t-sel); }

/* --------------------------------------------------------------------------
   7. DOC COLUMN - CALLOUT CARDS
   -------------------------------------------------------------------------- */
.tut-doc{ display:flex; flex-direction:column; gap:var(--tut-s4); }
.tut-sectiontitle{
  margin:var(--tut-s5) 0 0; font-size:12px; letter-spacing:.08em;
  text-transform:uppercase; color:var(--t-muted); font-weight:600;
}
.tut-sectiontitle:first-child{ margin-top:0; }
.tut-card{
  background:var(--t-surface);
  border:1px solid var(--t-border);
  border-left:3px solid var(--t-border);
  border-radius:var(--tut-radius);
  padding:var(--tut-s4) var(--tut-s5) var(--tut-s5);
  scroll-margin-top:var(--tut-scroll-pad);
  transition: border-color .18s ease, box-shadow .18s ease,
              background-color .18s ease, transform .18s ease;
}
.tut-card__head{ display:flex; align-items:center; gap:var(--tut-s3); flex-wrap:wrap; margin-bottom:var(--tut-s3); }
.tut-card__chip{
  display:inline-flex; align-items:center; justify-content:center;
  min-width:22px; height:22px; padding:0 6px; border-radius:999px;
  border:1px solid var(--t-accent); background:var(--t-surface);
  color:var(--t-accent); font:600 11.5px/1 var(--t-sans); flex:0 0 auto;
  transition: background-color .15s ease, color .15s ease, border-color .15s ease;
}
.tut-card__title{ margin:0; font-size:15.5px; font-weight:620; line-height:1.35; flex:1 1 220px; min-width:0; }
.tut-card__kind{
  font:600 10px/1 var(--t-sans); letter-spacing:.08em; text-transform:uppercase;
  color:var(--t-muted); border:1px solid var(--t-border-sf);
  padding:4px 7px; border-radius:var(--tut-radius-sm); white-space:nowrap;
}
/* Transient, never more than one on the page. Non-colour cue for :target. */
.tut-card__state{
  display:none;
  font:600 10px/1 var(--t-sans); letter-spacing:.08em; text-transform:uppercase;
  color:var(--t-sel); border:1px solid var(--t-sel);
  padding:4px 7px; border-radius:var(--tut-radius-sm); white-space:nowrap;
}
.tut-card:target .tut-card__state{ display:inline-block; }
.tut-card__body{ margin:0; font-size:14px; line-height:1.68; color:var(--t-text); max-width:66ch; }
.tut-card__body + .tut-card__body{ margin-top:var(--tut-s3); }
.tut-card__body code{
  font-family:var(--t-mono); font-size:12.5px;
  background:var(--t-surface-2); border:1px solid var(--t-border-sf);
  padding:1px 5px; border-radius:4px;
}
.tut-formula{
  margin:var(--tut-s3) 0 0; padding:var(--tut-s3) var(--tut-s4);
  background:var(--t-surface-2); border:1px solid var(--t-border-sf);
  border-radius:var(--tut-radius-sm);
  font-family:var(--t-mono); font-size:13px; line-height:1.6;
  overflow-x:auto; white-space:pre;
}
.tut-card__foot{
  display:flex; align-items:center; gap:var(--tut-s3); flex-wrap:wrap;
  margin-top:var(--tut-s4); padding-top:var(--tut-s3);
  border-top:1px solid var(--t-border-sf);
}
.tut-link{
  display:inline-flex; align-items:center; gap:var(--tut-s2);
  font:600 12.5px/1 var(--t-sans); text-decoration:none; color:var(--t-accent);
  border:1px solid var(--t-border); border-radius:var(--tut-radius-sm);
  padding:7px var(--tut-s3); background:transparent;
  transition: background-color .15s ease, border-color .15s ease, color .15s ease;
}
.tut-link:hover{ background:var(--t-accent-sf); border-color:var(--t-accent); }
.tut-link__range{ font-family:var(--t-mono); font-weight:500; color:var(--t-muted); }
.tut-card__note{ font-size:12px; color:var(--t-muted); margin-left:auto; }

/* --- 7.1 SELECTED CARD (green, strong, slight lift) ----------------------- */
.tut-card:target{
  background: var(--t-sel-tint);
  border-color: var(--t-sel);
  border-left-color: var(--t-sel);
  box-shadow: 0 0 0 1px var(--t-sel-ring), var(--t-sel-lift);
}
.tut-card:target .tut-card__chip{
  background:var(--t-sel); border-color:var(--t-sel); color:var(--t-sel-on);
}
.tut-card:target .tut-link{ color:var(--t-sel); border-color:var(--t-sel-ring); }
.tut-card:target .tut-link:hover{ background:var(--t-sel-tint); border-color:var(--t-sel); }
/* The lift is 1px inside a 16px flex gap - it can never reach a neighbour.
   Motion is a preference, so it is opt-out. */
@media (prefers-reduced-motion: no-preference){
  .tut-card:target{ transform: translateY(-1px); }
}

/* --------------------------------------------------------------------------
   8. FOCUS / MOTION / SCREEN READER
   -------------------------------------------------------------------------- */
.tut a:focus-visible, .tut [tabindex]:focus-visible, .tut input:focus-visible{
  outline:2px solid var(--t-accent); outline-offset:2px; border-radius:4px;
}
@media (prefers-reduced-motion: no-preference){ html{ scroll-behavior:smooth; } }
@media (prefers-reduced-motion: reduce){
  .tut *, body{ transition:none !important; }
}
.tut-sr{ position:absolute; width:1px; height:1px; overflow:hidden; clip-path:inset(50%); white-space:nowrap; }

/* --------------------------------------------------------------------------
   9. RESPONSIVE
   -------------------------------------------------------------------------- */
@media (max-width:1399px){ .tut{ --tut-side-w:208px; --tut-gap:var(--tut-s5); --tut-rail-w:56px; } }

/* Below 1280 the sidebar becomes a full-width strip above the grid.
   It is still a grid item, still in flow - it cannot overlap anything. */
@media (max-width:1279px){
  .tut-layout{ grid-template-columns: minmax(0,1.05fr) minmax(0,1fr); }
  .tut-side{
    grid-column:1 / -1; position:static;
    flex-direction:row; flex-wrap:wrap; align-items:flex-start;
    gap:var(--tut-s5); padding:var(--tut-s3) var(--tut-s4);
  }
  .tut-side__grp{ min-width:0; }
  .tut-side__grp--jump{ display:none; }
  .tut-side__t{ margin-bottom:var(--tut-s2); }
  .tut-nav{ flex-direction:row; flex-wrap:wrap; gap:var(--tut-s1); }
  .tut-theme{ margin-left:auto; border-top:0; padding-top:0; }
  .tut-theme__set{ min-width:208px; }
  .tut-theme__hint{ display:none; }
}
@media (max-height:700px) and (min-width:900px){
  .tut-col--code{ position:static; max-height:560px; }
  .tut-side{ position:static; }
}
@media (max-width:899px){
  .tut-wrap{ padding:var(--tut-s4) var(--tut-s4) var(--tut-s6); }
  .tut-layout{ grid-template-columns:minmax(0,1fr); gap:var(--tut-s5); }
  .tut-col--code{ position:static; max-height:none; }
  .tut-pane{ max-height:58vh; }
  .tut{ --tut-rail-w:48px; --tut-num-w:34px; --tut-code-fs:12.5px; }
  .tut-card{ padding:var(--tut-s4); }
  .tut-tag__lines{ display:none; }
}
@media (max-width:559px){
  .tut-side{ flex-direction:column; gap:var(--tut-s4); }
  .tut-theme{ margin-left:0; width:100%; }
  .tut-theme__set{ min-width:0; width:100%; }
  .tut-card__kind{ display:none; }
  .tut-card__note{ margin-left:0; flex-basis:100%; }
}

/* --------------------------------------------------------------------------
   10. PRINT - force the light token set so the page costs no ink.
   Declared last, so it beats [data-theme="dark"] at equal specificity.
   -------------------------------------------------------------------------- */
@media print{
  :root[data-theme]{
    color-scheme:light;
    --bg:#ffffff; --surface:#ffffff; --surface-2:#f4f5f7;
    --border:#c9ced8; --border-soft:#e3e6ec;
    --text:#000000; --muted:#44505f;
    --accent:#1d4ed8; --accent-soft:rgba(29,78,216,.08);
    --sel:#0b5c39; --sel-tint:rgba(11,92,57,.10);
    --sel-ring:rgba(11,92,57,.30); --sel-on:#ffffff; --sel-lift:none;
  }
  .site-header, .tut-side{ display:none; }
  .tut-layout{ grid-template-columns:minmax(0,1fr); }
  .tut-col--code{ position:static; max-height:none; }
  .tut-pane{ max-height:none; }
  .tut-card:target{ transform:none; }
}
"""
open("build_v22/tut.css","w",encoding="utf-8",newline="\n").write(CSS)
print("css bytes:", len(CSS))
# guard: no bare element selectors at rule start
import re
bad=[l for l in CSS.splitlines() if re.match(r'^[a-zA-Z]', l.strip()) and '{' in l and not l.strip().startswith(('html','body','@','*'))]
print("bare-element rule candidates:", bad)
open("tmp_probe.html","w").write("x")
