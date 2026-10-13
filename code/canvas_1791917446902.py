import sys, re
from html.parser import HTMLParser
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
t = open("docs/mock/module_tutorial_v2_2.html", encoding="utf-8").read()

VOID={'meta','link','br','hr','img','input','source','area','base','col','embed','param','track','wbr'}
class P(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True); s.stack=[]; s.ids=[]; s.hrefs=[]; s.err=[]; s.labels=[]
    def handle_starttag(s,tag,attrs):
        d=dict(attrs)
        if d.get('id'): s.ids.append(d['id'])
        if d.get('href','').startswith('#'): s.hrefs.append(d['href'][1:])
        if tag=='label' and d.get('for'): s.labels.append(d['for'])
        if tag not in VOID: s.stack.append((tag,s.getpos()))
    def handle_endtag(s,tag):
        if tag in VOID: return
        if not s.stack: s.err.append(f"stray </{tag}> at {s.getpos()}"); return
        o,pos=s.stack.pop()
        if o!=tag: s.err.append(f"mismatch <{o}> at {pos} closed by </{tag}> at {s.getpos()}")
p=P(); p.feed(t)
print("unclosed:", p.stack)
print("errors  :", p.err)
dups=[i for i in set(p.ids) if p.ids.count(i)>1]
print("duplicate ids:", dups)
missing=sorted({h for h in p.hrefs if h and h!='' and h not in p.ids})
print("dangling in-page hrefs:", missing)
print("label[for] without matching id:", [l for l in p.labels if l not in p.ids])
print("ids:", sorted(p.ids))

# scroll/overlap guards
print("\n-- overlap guard grep --")
for pat in [r'position:\s*absolute', r'position:\s*fixed', r'transform:\s*', r'float:\s*', r'z-index:\s*']:
    print(f"  {pat:28} {len(re.findall(pat,t))}  ->", re.findall(pat+r'[^;]*;', t)[:6])
print("\nminmax(0 count:", t.count("minmax(0"))
print("min-width:0 count:", t.count("min-width:0"))
print("scroll-padding-top:", t.count("scroll-padding-top"), "| scroll-margin-top:", t.count("scroll-margin-top"))
open("tmp_probe.html","w").write("x")
