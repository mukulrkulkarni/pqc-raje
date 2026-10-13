import sys, os, hashlib, base64, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CSS = open("build_v22/tut.css", encoding="utf-8").read()

JS = """
(function () {
  "use strict";
  var KEY   = "electre3.docs.theme";
  var VALID = ["light", "dark", "system"];
  var root  = document.documentElement;
  var store = null;

  try {                                   // localStorage can throw: private
    store = window.localStorage;          // mode, disabled storage, file://
    store.setItem(KEY + ".probe", "1");   // on some engines. Probe, do not
    store.removeItem(KEY + ".probe");     // assume.
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
    var inputs = document.querySelectorAll("input[name=\\"tut-theme\\"]");
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

SRC = [
 '"""Configuration loading and validation for the ELECTRE III engine."""',
 'from __future__ import annotations',
 '',
 'from dataclasses import dataclass',
 '',
 '@dataclass(frozen=True)',
 'class Criterion:',
 '    name: str',
 '    weight: float',
 '    q: float   # indifference threshold',
 '    p: float   # preference threshold',
 '    v: float   # veto threshold',
 '',
 '    def validate(self) -> None:',
 '        if self.weight <= 0:',
 '            raise ValueError("weight must be positive")',
 '        if not 0 <= self.q <= self.p <= self.v:',
 '            raise ValueError("thresholds must satisfy q <= p <= v")',
 '        if self.p == self.q == self.v == 0:',
 '            raise ValueError("thresholds must not all be zero")',
 '',
 'def normalise(criteria: list[Criterion]) -> list[float]:',
 '    total = sum(c.weight for c in criteria)',
 '    if total == 0:',
 '        raise ValueError("total weight must not be zero")',
 '    return [c.weight / total for c in criteria]',
 '',
 'def load(path: str) -> list[Criterion]:',
 '    records = _read_records(path)',
 '    criteria = [Criterion(**r) for r in records]',
 '    for c in criteria:',
 '        c.validate()',
 '    return criteria',
]

RANGES = [
  (1, 6, 12, "Criterion record"),
  (2, 14, 20, "Threshold ordering rule"),
  (3, 22, 27, "Weight normalisation"),
  (4, 28, 33, "Entry point and failure mode"),
]

import html as H
def esc(s):
    return H.escape(s, quote=True) if s.strip() else "&nbsp;"

def partition(n_lines, ranges):
    segs, cur = [], 1
    for (n, s, e, t) in ranges:
        if s > cur: segs.append(("plain", None, cur, s - 1))
        segs.append(("ranged", (n, t), s, e)); cur = e + 1
    if cur <= n_lines: segs.append(("plain", None, cur, n_lines))
    return segs

def render_seg(kind, meta, s, e):
    rows = "".join(
        '<span class="tut-ln" aria-hidden="true">%d</span>'
        '<span class="tut-src">%s</span>' % (i, esc(SRC[i-1]))
        for i in range(s, e + 1))
    if kind == "plain":
        return ('<div class="tut-seg tut-seg--plain">'
                '<span class="tut-rail-spacer" aria-hidden="true"></span>%s</div>' % rows)
    n, t = meta
    tag = ('<a class="tut-tag" href="#c%d" aria-label="Go to note %d: %s">'
           '<span class="tut-tag__chip">%d</span>'
           '<span class="tut-tag__bracket" aria-hidden="true"></span>'
           '<span class="tut-tag__lines">%d-%d</span></a>' % (n, n, H.escape(t), n, s, e))
    return '<div class="tut-seg tut-seg--ranged" id="r%d">%s%s</div>' % (n, tag, rows)

code_html = "\n".join(render_seg(*sg) for sg in partition(len(SRC), RANGES))
open("build_v22/code.html","w",encoding="utf-8",newline="\n").write(code_html)
print("segments rendered:", code_html.count("tut-seg "), "| lines:", len(SRC))
print(code_html[:300])
open("tmp_probe.html","w").write("x")
