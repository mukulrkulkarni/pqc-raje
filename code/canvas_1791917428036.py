import sys, os, hashlib, base64
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.makedirs("docs/mock", exist_ok=True)

CSS  = open("build_v22/tut.css", encoding="utf-8").read()
CODE = open("build_v22/code.html", encoding="utf-8").read()

JS = """
(function () {
  "use strict";
  var KEY   = "electre3.docs.theme";
  var VALID = ["light", "dark", "system"];
  var root  = document.documentElement;
  var store = null;

  /* localStorage can throw: private mode, disabled storage, some file:// */
  try {
    store = window.localStorage;
    store.setItem(KEY + ".probe", "1");
    store.removeItem(KEY + ".probe");
  } catch (e) { store = null; }

  function read() {
    var v = null;
    try { v = store ? store.getItem(KEY) : null; } catch (e) { v = null; }
    return VALID.indexOf(v) >= 0 ? v : "system";
  }

  var current = read();
  root.setAttribute("data-theme", current);
  root.className = root.className.replace(/\\bno-js\\b/g, "").trim();
  if (!store) { root.className = (root.className + " tut-nostore").trim(); }

  function wire() {
    var inputs = document.querySelectorAll("input[name='tut-theme']");
    var i;
    for (i = 0; i < inputs.length; i++) {
      inputs[i].checked = (inputs[i].value === current);
      inputs[i].addEventListener("change", function () {
        var v = this.value;
        if (VALID.indexOf(v) < 0) { return; }
        current = v;
        root.setAttribute("data-theme", v);
        try { if (store) { store.setItem(KEY, v); } } catch (e) {}
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", wire);
  } else { wire(); }
})();
"""

CARDS = [
 dict(n=1, title="Criterion record", kind="Data shape", s=6, e=12,
      body=['A <code>Criterion</code> holds one decision attribute. The record is frozen. '
            'A criterion cannot change after the engine reads it.',
            'Three thresholds give the outranking relation its shape. <code>q</code> is the '
            'indifference limit. <code>p</code> is the preference limit. <code>v</code> is the veto limit.'],
      formula=None, note="Read this first."),
 dict(n=2, title="Threshold ordering rule", kind="Constraint", s=14, e=20,
      body=['The method rejects a criterion that breaks the threshold order. '
            'This keeps the concordance index monotone.'],
      formula="0 &lt;= q &lt;= p &lt;= v      (and not q = p = v = 0)", note="Raises ValueError."),
 dict(n=3, title="Weight normalisation", kind="Formula", s=22, e=27,
      body=['The function divides each weight by the sum of all weights. '
            'The result is a set of weights that add up to 1.'],
      formula="w&#770;_j = w_j / &#931;_k w_k ,   &#931;_j w&#770;_j = 1", note="Pure function."),
 dict(n=4, title="Entry point and failure mode", kind="I/O", s=28, e=33,
      body=['<code>load()</code> reads the records, builds the criteria, and validates each one. '
            'The function stops at the first bad record.',
            'The full engine calls <code>load()</code> one time. It then gives the normalised '
            'weights to the concordance step.'],
      formula=None, note="Fails fast."),
]

def card(c):
    body = "".join('<p class="tut-card__body">%s</p>' % b for b in c["body"])
    frm = ('\n        <div class="tut-formula" role="figure" aria-label="Formula for %s">%s</div>'
           % (c["title"], c["formula"])) if c["formula"] else ""
    note = ('\n          <span class="tut-card__note">%s</span>' % c["note"]) if c["note"] else ""
    return """      <article class="tut-card" id="c{n}" aria-labelledby="c{n}-t">
        <div class="tut-card__head">
          <span class="tut-card__chip" aria-hidden="true">{n}</span>
          <h3 class="tut-card__title" id="c{n}-t">{title}</h3>
          <span class="tut-card__kind">{kind}</span>
          <span class="tut-card__state">Selected</span>
        </div>
        {body}{frm}
        <div class="tut-card__foot">
          <a class="tut-link" href="#r{n}">Show the code
            <span class="tut-link__range">lines {s}-{e}</span>
            <span class="tut-sr">of config.py</span></a>{note}
        </div>
      </article>""".format(n=c["n"], title=c["title"], kind=c["kind"],
                           body=body, frm=frm, s=c["s"], e=c["e"], note=note)

cards_html = "\n".join(card(c) for c in CARDS)
jump = "\n".join(
    '            <li><a href="#c{n}"><b>{n}</b><span>{t}</span></a></li>'.format(n=c["n"], t=c["title"])
    for c in CARDS)

MODULES = ["config", "concordance", "discordance", "credibility", "ranking"]
nav = "\n".join(
    '            <li><a href="#"%s>%s</a></li>' % (' aria-current="page"' if m == "config" else "", m)
    for m in MODULES)

CSP_PLACEHOLDER = "__CSP_SCRIPT_HASH__"

DOC = """<!DOCTYPE html>
<html lang="en" class="no-js" data-theme="system">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src '{csp}'; style-src 'unsafe-inline'; img-src 'self' data:; base-uri 'none'; form-action 'none'; frame-ancestors 'none'">
<meta name="color-scheme" content="light dark">
<title>config.py - Module Tutorial (v2.2 mockup)</title>
<style>
{css}
</style>
<script>{js}</script>
</head>
<body>
<header class="site-header">
  <strong>ELECTRE III</strong><span>/ Docs / Modules / config</span>
</header>

<main class="tut">
 <div class="tut-wrap">
  <header class="tut-head">
    <p class="tut-eyebrow">Module tutorial &middot; v2.2</p>
    <h1 class="tut-title">electre3/config.py &mdash; criteria and thresholds</h1>
    <p class="tut-lede">The code is on the left. The notes are on the right. Each note has a number.
       The same number marks the related lines in the code. Select a number to move between the two.</p>
  </header>

  <div class="tut-layout">

    <!-- ===== SIDEBAR (new in v2.2) ===== -->
    <aside class="tut-side" aria-label="Tutorial sidebar">
      <nav class="tut-side__grp" aria-label="Modules">
        <h2 class="tut-side__t">Modules</h2>
        <ul class="tut-nav">
{nav}
        </ul>
      </nav>

      <nav class="tut-side__grp tut-side__grp--jump" aria-label="Notes on this page">
        <h2 class="tut-side__t">On this page</h2>
        <ul class="tut-jump">
{jump}
        </ul>
      </nav>

      <fieldset class="tut-theme">
        <legend class="tut-theme__legend">Appearance</legend>
        <div class="tut-theme__set">
          <input class="tut-theme__in" type="radio" name="tut-theme" id="tut-th-light"  value="light">
          <label class="tut-theme__lb" for="tut-th-light">Light</label>
          <input class="tut-theme__in" type="radio" name="tut-theme" id="tut-th-dark"   value="dark">
          <label class="tut-theme__lb" for="tut-th-dark">Dark</label>
          <input class="tut-theme__in" type="radio" name="tut-theme" id="tut-th-system" value="system" checked>
          <label class="tut-theme__lb" for="tut-th-system">System</label>
        </div>
        <p class="tut-theme__hint">System uses your device setting.</p>
        <p class="tut-theme__warn">This browser does not keep the setting.</p>
      </fieldset>
    </aside>

    <!-- ===== CODE COLUMN ===== -->
    <div class="tut-col tut-col--code">
      <section class="tut-pane" aria-label="Source code of config.py">
        <div class="tut-pane__bar">
          <span class="tut-pane__file">electre3/config.py</span>
          <span class="tut-pane__meta">33 lines &middot; 4 notes</span>
        </div>
        <div class="tut-code" tabindex="0" role="region" aria-label="Source code, scrollable">
{code}
        </div>
      </section>
    </div>

    <!-- ===== DOC COLUMN ===== -->
    <div class="tut-col">
      <div class="tut-doc">
        <h2 class="tut-sectiontitle">What the module does</h2>
{cards}
      </div>
    </div>

  </div>
 </div>
</main>
</body>
</html>
""".format(csp=CSP_PLACEHOLDER, css=CSS.strip(), js=JS, nav=nav, jump=jump, code=CODE, cards=cards_html)

# --- compute the CSP hash over the EXACT inline script text ---
digest = hashlib.sha256(JS.encode("utf-8")).digest()
h = "sha256-" + base64.b64encode(digest).decode("ascii")
DOC = DOC.replace(CSP_PLACEHOLDER, h)

out = "docs/mock/module_tutorial_v2_2.html"
with open(out, "w", encoding="utf-8", newline="\n") as f:
    f.write(DOC)

# --- verify: re-extract the script body from the written file and re-hash ---
t = open(out, encoding="utf-8", newline="").read()
a = t.index("<script>") + len("<script>"); b = t.index("</script>")
again = "sha256-" + base64.b64encode(hashlib.sha256(t[a:b].encode("utf-8")).digest()).decode("ascii")
print("hash in CSP :", h)
print("hash re-read:", again)
print("MATCH       :", h == again)
print("bytes       :", os.path.getsize(out))
print("CRLF present:", b"\r\n" in open(out,"rb").read())
for bad in ["onclick=", "onload=", "eval(", "new Function", "http://", "https://", "innerHTML", "document.write"]:
    print(f"  {bad:>16} -> {t.count(bad)}")
open("tmp_probe.html","w").write("x")
