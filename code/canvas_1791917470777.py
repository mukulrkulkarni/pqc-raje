import sys, re, hashlib, base64, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p="docs/mock/module_tutorial_v2_2.html"
t=open(p,encoding="utf-8",newline="").read()

print("real transforms:", re.findall(r'(?<!text-)transform:[^;}]*', t))

# Make module nav realistic: current = span, others = real Flask routes.
MODULES=["config","concordance","discordance","credibility","ranking"]
old_items="\n".join('            <li><a href="#"%s>%s</a></li>'%(' aria-current="page"' if m=="config" else "", m) for m in MODULES)
new_items="\n".join(
    ('            <li><span class="tut-nav__cur" aria-current="page">%s</span></li>'%m) if m=="config"
    else ('            <li><a href="/docs/modules/%s">%s</a></li>'%(m,m))
    for m in MODULES)
assert old_items in t, "nav block not found"
t=t.replace(old_items,new_items)

# style the current item as a span (reuse the a[aria-current] rule)
old_css='.tut-nav a[aria-current="page"]{'
new_css='.tut-nav__cur{\n  display:block; padding:6px var(--tut-s2); border-radius:var(--tut-radius-sm);\n  font:600 13px/1.4 var(--t-sans); overflow-wrap:anywhere;\n}\n.tut-nav__cur, .tut-nav a[aria-current="page"]{'
assert old_css in t
t=t.replace(old_css,new_css,1)

with open(p,"w",encoding="utf-8",newline="\n") as f: f.write(t)

# re-verify hash still matches (script untouched)
t2=open(p,encoding="utf-8",newline="").read()
a=t2.index("<script>")+8; b=t2.index("</script>")
h="sha256-"+base64.b64encode(hashlib.sha256(t2[a:b].encode("utf-8")).digest()).decode()
print("script hash:", h)
print("in document:", h in t2)
print("bytes:", os.path.getsize(p), "| CRLF:", b"\r\n" in open(p,"rb").read())
print("href='#' remaining:", t2.count('href="#"'))
open("tmp_probe.html","w").write("x")
