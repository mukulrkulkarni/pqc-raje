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
fig = plt.figure(figsize=(16.5, 10.4), dpi=150)
fig.patch.set_facecolor("#20242c")
fig.text(.5,.978,"Module Tutorial v2.2  —  selection state proof sheet",
         ha="center",va="top",color="#ffffff",fontsize=18,fontweight="bold")
fig.text(.5,.952,"Green is a STATE colour only. It never appears at rest, and :target guarantees at most one selected pair on the page.",
         ha="center",va="top",color="#aab3c0",fontsize=10)

def card(ax, x, y, w, h, T, selected, label):
    sel, tint = T["sel"], over(T["sel"], T["a"], T["surf"])
    bg   = tint if selected else T["surf"]
    edge = sel  if selected else T["bd"]
    if selected:
        for o,al in [(0.034,.09),(0.022,.13),(0.012,.19)]:
            ax.add_patch(FancyBboxPatch((x-o,y-o-0.013), w+2*o, h+2*o,
                boxstyle="round,pad=0,rounding_size=0.012", fc=sel, ec="none", alpha=al, zorder=1))
    ax.add_patch(FancyBboxPatch((x,y),w,h, boxstyle="round,pad=0,rounding_size=0.012",
                                fc=bg, ec=edge, lw=1.4, zorder=2))
    ax.add_patch(Rectangle((x,y+0.005),0.0055,h-0.010, fc=edge, ec="none", zorder=3))
    PAD = 0.030
    cy = y+h-0.055
    ax.add_patch(FancyBboxPatch((x+PAD,cy),0.028,0.036, boxstyle="round,pad=0,rounding_size=0.018",
                 fc=sel if selected else T["surf"], ec=sel if selected else T["ac"], lw=1.2, zorder=4))
    ax.text(x+PAD+0.014, cy+0.018, "2", ha="center", va="center", zorder=5, fontsize=8.5,
            fontweight="bold", color=T["on"] if selected else T["ac"])
    ax.text(x+PAD+0.040, cy+0.018, "Threshold ordering rule", va="center", color=T["tx"],
            fontsize=10.5, fontweight="bold", zorder=5)
    ax.text(x+PAD+0.248, cy+0.018, "CONSTRAINT", va="center", color=T["mu"], fontsize=6.6, zorder=5,
            bbox=dict(boxstyle="round,pad=0.32", fc="none", ec=T["bds"], lw=.9))
    if selected:
        ax.text(x+PAD+0.322, cy+0.018, "SELECTED", va="center", color=sel, fontsize=6.6,
                fontweight="bold", zorder=5, bbox=dict(boxstyle="round,pad=0.32", fc="none", ec=sel, lw=1.2))
    ax.text(x+PAD, y+h-0.082, "The method rejects a criterion that breaks the threshold\norder. This keeps the concordance index monotone.",
            va="top", color=T["tx"], fontsize=8.8, linespacing=1.65, zorder=5)
    fy = y+0.090
    ax.add_patch(FancyBboxPatch((x+PAD,fy),w-2*PAD,0.048, boxstyle="round,pad=0,rounding_size=0.008",
                                fc=T["s2"], ec=T["bds"], lw=.9, zorder=4))
    ax.text(x+PAD+0.014, fy+0.024, "0 <= q <= p <= v", va="center", color=T["tx"],
            fontsize=8.6, family="monospace", zorder=5)
    ax.add_patch(Rectangle((x+PAD, y+0.070), w-2*PAD, 0.0012, fc=T["bds"], ec="none", zorder=4))
    ax.add_patch(FancyBboxPatch((x+PAD,y+0.022),0.150,0.030, boxstyle="round,pad=0,rounding_size=0.008",
                                fc="none", ec=sel if selected else T["bd"], lw=1.1, zorder=4))
    ax.text(x+PAD+0.075, y+0.037, "Show the code", ha="center", va="center", zorder=5, fontsize=8,
            fontweight="bold", color=sel if selected else T["ac"])
    ax.text(x+w-PAD, y+0.037, "Raises ValueError.", ha="right", va="center", color=T["mu"], fontsize=7.6, zorder=5)
    ax.text(x, y+h+0.022, label, color=sel if selected else T["mu"], fontsize=9, fontweight="bold", zorder=5)

def pane(ax, x, y, w, h, T, selected, label):
    sel, tint = T["sel"], over(T["sel"], T["a"], T["surf"])
    ax.add_patch(FancyBboxPatch((x,y),w,h, boxstyle="round,pad=0,rounding_size=0.012",
                                fc=T["surf"], ec=T["bd"], lw=1.2, zorder=2))
    ax.add_patch(Rectangle((x,y+h-0.044), w, 0.044, fc=T["s2"], ec="none", zorder=3))
    ax.text(x+0.016, y+h-0.022, "electre3/config.py", va="center", color=T["tx"], fontsize=8, family="monospace", zorder=4)
    ax.text(x+w-0.016, y+h-0.022, "33 lines - 4 notes", ha="right", va="center", color=T["mu"], fontsize=7, zorder=4)
    rows = ["    def validate(self) -> None:", "        if self.weight <= 0:",
            "            raise ValueError(...)", "        if not 0 <= q <= p <= v:",
            "            raise ValueError(...)"]
    RH = 0.027; n=len(rows)
    top = y+h-0.052
    blk_b = top-RH*n
    ax.add_patch(Rectangle((x+0.002, blk_b), w-0.004, RH*n,
                 fc=tint if selected else T["ac"], alpha=1 if selected else .10, ec="none", zorder=3))
    if selected:
        ax.add_patch(Rectangle((x+0.002, blk_b), 0.0055, RH*n, fc=sel, ec="none", zorder=4))
    ax.add_patch(Rectangle((x+0.058, blk_b), 0.0012, RH*n, fc=T["bds"], ec="none", zorder=4))
    chy = top-0.032
    ax.add_patch(FancyBboxPatch((x+0.018,chy),0.025,0.028, boxstyle="round,pad=0,rounding_size=0.014",
                 fc=sel if selected else T["surf"], ec=sel if selected else T["ac"], lw=1.1, zorder=5))
    ax.text(x+0.0305, chy+0.014, "2", ha="center", va="center", fontsize=7.5, fontweight="bold",
            zorder=6, color=T["on"] if selected else T["ac"])
    ax.add_patch(Rectangle((x+0.0295, blk_b+0.008), 0.004 if selected else 0.0025, RH*n-0.050,
                 fc=sel if selected else T["ac"], alpha=1.0 if selected else .45, ec="none", zorder=5))
    for i,r in enumerate(rows):
        yy = top-RH*i-RH/2
        ax.text(x+0.054, yy, str(14+i), ha="right", va="center", color=T["mu"], alpha=.65,
                fontsize=7, family="monospace", zorder=6)
        ax.text(x+0.066, yy, r, va="center", color=T["tx"], fontsize=7, family="monospace", zorder=6)
    ax.text(x, y+h+0.022, label, color=sel if selected else T["mu"], fontsize=9, fontweight="bold", zorder=5)

for col,(name,T) in enumerate(TH.items()):
    ax = fig.add_axes([0.030+col*0.486, 0.062, 0.456, 0.868]); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    ax.add_patch(Rectangle((0,0),1,1, fc=T["bg"], ec="none"))
    tint = over(T["sel"], T["a"], T["surf"])
    ax.text(0.025,0.980, '%s  —  data-theme="%s"' % (name, name.lower()), color=T["tx"], fontsize=13, fontweight="bold", va="top")
    ax.text(0.025,0.950, "accent %s   selection %s   tint %d%% = %s" % (T["ac"], T["sel"], T["a"]*100, tint),
            color=T["mu"], fontsize=8, va="top", family="monospace")
    pane(ax, 0.028, 0.660, 0.44, 0.245, T, False, "code segment - at rest")
    pane(ax, 0.520, 0.660, 0.44, 0.245, T, True,  "code segment - :target")
    card(ax, 0.028, 0.300, 0.44, 0.300, T, False, "callout card - at rest")
    card(ax, 0.520, 0.300, 0.44, 0.300, T, True,  "callout card - :target, lifted")
    rows=[("selection green on surface",       cr(T["sel"],T["surf"]), 4.5),
          ("selection green on its own tint",  cr(T["sel"],tint),      4.5),
          ("body text on selected tint",       cr(T["tx"],tint),       4.5),
          ("muted text on selected tint",      cr(T["mu"],tint),       4.5),
          ("chip label on filled green chip",  cr(T["on"],T["sel"]),   4.5),
          ("green border vs surface (UI)",     cr(T["sel"],T["surf"]), 3.0),
          ("identity accent on surface",       cr(T["ac"],T["surf"]),  4.5)]
    ax.text(0.028,0.248,"WCAG 2.1 contrast - measured", color=T["tx"], fontsize=10, fontweight="bold", va="top")
    for i,(lab,v,req) in enumerate(rows):
        yy=0.212-i*0.0295
        ax.text(0.040, yy, lab, color=T["mu"], fontsize=8.2, va="center")
        ax.text(0.660, yy, "%.2f:1" % v, color=T["tx"], fontsize=8.2, va="center", family="monospace", ha="right")
        ax.text(0.700, yy, "PASS  (min %.1f)" % req if v>=req else "FAIL", color=T["sel"] if v>=req else "#e5484d",
                fontsize=8.2, va="center", fontweight="bold")
fig.text(.5,.024,"1px lift sits inside a 16px flex gap and is disabled under prefers-reduced-motion   -   no position:absolute in layout   -   no external assets   -   no new CSP directive",
         ha="center",color="#8b94a3",fontsize=8.5)
fig.savefig("docs/design/module_tutorial_v2_2_selection_proof.png", facecolor=fig.get_facecolor())
print("ok")
