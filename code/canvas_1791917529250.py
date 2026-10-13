import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

def hx(c):
    c=c.lstrip('#'); return tuple(int(c[i:i+2],16) for i in (0,2,4))
def lin(v):
    v/=255.0
    return v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4
def Lum(r): return 0.2126*lin(r[0])+0.7152*lin(r[1])+0.0722*lin(r[2])
def cr(a,b):
    la,lb=Lum(hx(a)),Lum(hx(b)); hi,lo=max(la,lb),min(la,lb); return (hi+0.05)/(lo+0.05)
def over(f,a,b):
    f,b=hx(f),hx(b); return '#%02x%02x%02x'%tuple(round(f[i]*a+b[i]*(1-a)) for i in range(3))

TH = {
 "LIGHT": dict(bg="#f6f7f9", surf="#ffffff", s2="#f1f3f6", bd="#d7dce4", bds="#e7eaf0",
               tx="#141922", mu="#5b6472", ac="#1d4ed8", sel="#0b7a4b", a=0.10, on="#ffffff"),
 "DARK":  dict(bg="#0f1115", surf="#161a21", s2="#1c222b", bd="#2a313d", bds="#222935",
               tx="#e6e9ef", mu="#9aa4b4", ac="#5b9dff", sel="#3ddc97", a=0.12, on="#0f1115"),
}

fig = plt.figure(figsize=(15.5, 9.6), dpi=150)
fig.patch.set_facecolor("#20242c")
fig.text(.5,.972,"Module Tutorial v2.2  —  selection state proof sheet",
         ha="center",va="top",color="#ffffff",fontsize=17,fontweight="bold")
fig.text(.5,.944,"Green is a STATE colour only. It never appears at rest, and :target guarantees at most one selected pair per page.",
         ha="center",va="top",color="#aab3c0",fontsize=9.5)

def card(ax, x, y, w, h, T, selected, label):
    sel, tint = T["sel"], over(T["sel"], T["a"], T["surf"])
    bg   = tint if selected else T["surf"]
    edge = sel  if selected else T["bd"]
    if selected:  # optical lift: soft green halo + 1px ring
        for k,(o,al) in enumerate([(0.030,.10),(0.020,.14),(0.011,.20)]):
            ax.add_patch(FancyBboxPatch((x-o, y-o-0.012), w+2*o, h+2*o, boxstyle="round,pad=0,rounding_size=0.012",
                                        fc=sel, ec="none", alpha=al, zorder=1))
    ax.add_patch(FancyBboxPatch((x,y),w,h, boxstyle="round,pad=0,rounding_size=0.012",
                                fc=bg, ec=edge, lw=1.3, zorder=2))
    ax.add_patch(Rectangle((x,y+0.004),0.006,h-0.008, fc=edge, ec="none", zorder=3))  # 3px left border
    # chip
    cx, cy = x+0.035, y+h-0.052
    ax.add_patch(FancyBboxPatch((cx,cy),0.030,0.040, boxstyle="round,pad=0,rounding_size=0.020",
                                fc=sel if selected else T["surf"], ec=sel if selected else T["ac"], lw=1.2, zorder=4))
    ax.text(cx+0.015, cy+0.020, "2", ha="center", va="center", zorder=5, fontsize=9, fontweight="bold",
            color=T["on"] if selected else T["ac"])
    ax.text(x+0.080, cy+0.020, "Threshold ordering rule", va="center", color=T["tx"], fontsize=11, fontweight="semibold", zorder=5)
    ax.text(x+0.335, cy+0.020, "CONSTRAINT", va="center", color=T["mu"], fontsize=7, zorder=5,
            bbox=dict(boxstyle="round,pad=0.35", fc="none", ec=T["bds"], lw=.9))
    if selected:
        ax.text(x+0.455, cy+0.020, "SELECTED", va="center", color=sel, fontsize=7, fontweight="bold", zorder=5,
                bbox=dict(boxstyle="round,pad=0.35", fc="none", ec=sel, lw=1.1))
    ax.text(x+0.035, y+h-0.115, "The method rejects a criterion that breaks the\nthreshold order. This keeps the concordance\nindex monotone.",
            va="top", color=T["tx"], fontsize=9.2, linespacing=1.6, zorder=5)
    ax.add_patch(FancyBboxPatch((x+0.035,y+0.072),w-0.070,0.052, boxstyle="round,pad=0,rounding_size=0.008",
                                fc=T["s2"], ec=T["bds"], lw=.9, zorder=4))
    ax.text(x+0.050, y+0.098, "0 <= q <= p <= v", va="center", color=T["tx"], fontsize=9, family="monospace", zorder=5)
    ax.add_patch(Rectangle((x+0.035,y+0.058), w-0.070, 0.0012, fc=T["bds"], ec="none", zorder=4))
    ax.add_patch(FancyBboxPatch((x+0.035,y+0.016),0.175,0.032, boxstyle="round,pad=0,rounding_size=0.008",
                                fc="none", ec=sel if selected else T["bd"], lw=1.0, zorder=4))
    ax.text(x+0.122, y+0.032, "Show the code", ha="center", va="center", zorder=5, fontsize=8.5,
            fontweight="bold", color=sel if selected else T["ac"])
    ax.text(x+w-0.035, y+0.032, "Raises ValueError.", ha="right", va="center", color=T["mu"], fontsize=8, zorder=5)
    ax.text(x, y+h+0.028, label, color=T["mu"], fontsize=9, fontweight="bold", zorder=5)

def pane(ax, x, y, w, h, T, selected):
    sel, tint = T["sel"], over(T["sel"], T["a"], T["surf"])
    ax.add_patch(FancyBboxPatch((x,y),w,h, boxstyle="round,pad=0,rounding_size=0.012",
                                fc=T["surf"], ec=T["bd"], lw=1.2, zorder=2))
    ax.add_patch(Rectangle((x,y+h-0.050), w, 0.050, fc=T["s2"], ec="none", zorder=3))
    ax.text(x+0.018, y+h-0.025, "electre3/config.py", va="center", color=T["tx"], fontsize=8.5, family="monospace", zorder=4)
    ax.text(x+w-0.018, y+h-0.025, "33 lines · 4 notes", ha="right", va="center", color=T["mu"], fontsize=7.5, zorder=4)
    rows = ["    def validate(self) -> None:", "        if self.weight <= 0:",
            "            raise ValueError(...)", "        if not 0 <= q <= p <= v:",
            "            raise ValueError(...)"]
    top = y+h-0.072
    if selected:
        ax.add_patch(Rectangle((x+0.002, top-0.030*len(rows)+0.004), w-0.004, 0.030*len(rows), fc=tint, ec="none", zorder=3))
        ax.add_patch(Rectangle((x+0.002, top-0.030*len(rows)+0.004), 0.006, 0.030*len(rows), fc=sel, ec="none", zorder=4))
    else:
        ax.add_patch(Rectangle((x+0.002, top-0.030*len(rows)+0.004), w-0.004, 0.030*len(rows),
                               fc=T["ac"], alpha=.10, ec="none", zorder=3))
    ax.add_patch(Rectangle((x+0.062, top-0.030*len(rows)+0.004), 0.0012, 0.030*len(rows)-0.008,
                           fc=T["bds"], ec="none", zorder=4))
    chy = top-0.024
    ax.add_patch(FancyBboxPatch((x+0.022,chy),0.026,0.030, boxstyle="round,pad=0,rounding_size=0.015",
                                fc=sel if selected else T["surf"], ec=sel if selected else T["ac"], lw=1.1, zorder=5))
    ax.text(x+0.035, chy+0.015, "2", ha="center", va="center", fontsize=8, fontweight="bold", zorder=6,
            color=T["on"] if selected else T["ac"])
    bh = 0.030*len(rows)-0.050
    ax.add_patch(Rectangle((x+0.0335, top-0.030*len(rows)+0.010), 0.004 if selected else 0.0025, bh,
                           fc=sel if selected else T["ac"], alpha=1.0 if selected else .45, ec="none", zorder=5))
    for i,r in enumerate(rows):
        yy = top-0.030*i-0.015
        ax.text(x+0.058, yy, str(14+i), ha="right", va="center", color=T["mu"], alpha=.6, fontsize=7.5, family="monospace", zorder=6)
        ax.text(x+0.072, yy, r, va="center", color=T["tx"], fontsize=7.5, family="monospace", zorder=6)

for col,(name,T) in enumerate(TH.items()):
    ax = fig.add_axes([0.035+col*0.485, 0.075, 0.455, 0.845])
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    ax.add_patch(Rectangle((0,0),1,1, fc=T["bg"], ec="none"))
    ax.text(0.02,0.975, name+"  —  data-theme=\"%s\"" % name.lower(), color=T["tx"], fontsize=13, fontweight="bold", va="top")
    tint = over(T["sel"], T["a"], T["surf"])
    ax.text(0.02,0.942, "accent %s   ·   selection %s   ·   tint %d%% -> %s" % (T["ac"], T["sel"], T["a"]*100, tint),
            color=T["mu"], fontsize=8, va="top", family="monospace")
    pane(ax, 0.03, 0.645, 0.44, 0.255, T, False)
    pane(ax, 0.52, 0.645, 0.44, 0.255, T, True)
    ax.text(0.03, 0.915, "code segment — at rest", color=T["mu"], fontsize=8.5, fontweight="bold")
    ax.text(0.52, 0.915, "code segment — :target (green)", color=T["sel"], fontsize=8.5, fontweight="bold")
    card(ax, 0.03, 0.300, 0.44, 0.275, T, False, "callout card — at rest")
    card(ax, 0.52, 0.300, 0.44, 0.275, T, True,  "callout card — :target (green, lifted)")
    rows=[("selection green on surface", cr(T["sel"],T["surf"]), 4.5),
          ("selection green on its own tint", cr(T["sel"],tint),  4.5),
          ("body text on selected tint",      cr(T["tx"],tint),   4.5),
          ("muted text on selected tint",     cr(T["mu"],tint),   4.5),
          ("chip label on filled green chip", cr(T["on"],T["sel"]),4.5),
          ("green border vs surface (UI)",    cr(T["sel"],T["surf"]),3.0)]
    ax.text(0.03,0.245,"WCAG 2.1 contrast — measured", color=T["tx"], fontsize=9.5, fontweight="bold", va="top")
    for i,(lab,v,req) in enumerate(rows):
        yy=0.208-i*0.0335
        ax.text(0.045, yy, lab, color=T["mu"], fontsize=8.3, va="center")
        ax.text(0.68,  yy, "%.2f:1" % v, color=T["tx"], fontsize=8.3, va="center", family="monospace", ha="right")
        ok = v>=req
        ax.text(0.72, yy, ("PASS  (>= %.1f)" % req) if ok else "FAIL", color=T["sel"] if ok else "#e5484d",
                fontsize=8.3, va="center", fontweight="bold")
fig.text(.5,.028,"Lift is 1px inside a 16px flex gap and is disabled under prefers-reduced-motion  ·  no position:absolute in layout  ·  no external assets  ·  no new CSP directive",
         ha="center",color="#8b94a3",fontsize=8.5)
fig.savefig("docs/design/module_tutorial_v2_2_selection_proof.png", facecolor=fig.get_facecolor())
print("ok")
