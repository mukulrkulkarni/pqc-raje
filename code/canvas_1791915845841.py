import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

PURPLE=(100/255,0,255/255)
DARK=(37/255,55/255,70/255)
GRAY=(117/255,120/255,123/255)
TEAL=(126/255,221/255,211/255)
GREEN=(0/255,195/255,137/255)
LGRAY=(164/255,188/255,194/255)
BG=(0.975,0.98,0.992)


def rrect(ax,x,y,w,h,fc,ec=None,lw=1,rad=10,alpha=1.0):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle=f"round,pad=0.02,rounding_size={rad}",fc=fc,ec=ec if ec else fc,lw=lw,alpha=alpha))

fig, axes = plt.subplots(2,1,figsize=(12,10))
for ax in axes:
    ax.set_xlim(0,120); ax.set_ylim(0,70); ax.axis('off')

# Option 1: Static with anchors
ax=axes[0]
rrect(ax,0,0,120,70,BG,rad=0)
rrect(ax,6,60,108,8,(1,1,1),ec=LGRAY,rad=16,alpha=0.9)
ax.text(10,65,"Side-by-side: Static sections",fontsize=14,color=DARK,fontweight='bold')
ax.text(10,62,"Right pane scrolls with headings; click TOC anchors.",fontsize=9.5,color=GRAY)

# two panes
rrect(ax,6,8,54,50,(1,1,1),ec=LGRAY,rad=16)
rrect(ax,60,8,54,50,(1,1,1),ec=LGRAY,rad=16)
ax.text(10,54,"Code",fontsize=11,color=DARK,fontweight='bold')
ax.text(64,54,"Doc",fontsize=11,color=DARK,fontweight='bold')
# code lines
for i in range(6):
    ax.add_patch(Rectangle((10,46-5*i),44,3,ec=None,fc=(0.96,0.96,0.98)))
ax.text(10,16,"No per-line callouts.\nSimple and robust.",fontsize=9.5,color=GRAY)
# doc headings
for i,t in enumerate(["Purpose","Inputs","Formulas","Edge cases","How code works","How it fits"]):
    ax.add_patch(Rectangle((64,46-6*i),44,4,ec=LGRAY,fc=(0.99,0.99,1)))
    ax.text(66,48-6*i,t,fontsize=9.5,color=GRAY)

# Option 2: Callouts tied to code ranges
ax=axes[1]
rrect(ax,0,0,120,70,BG,rad=0)
rrect(ax,6,60,108,8,(1,1,1),ec=LGRAY,rad=16,alpha=0.9)
ax.text(10,65,"Side-by-side: Callouts tied to code ranges",fontsize=14,color=DARK,fontweight='bold')
ax.text(10,62,"Click a code range. Doc pane jumps to explanation.",fontsize=9.5,color=GRAY)

rrect(ax,6,8,54,50,(1,1,1),ec=LGRAY,rad=16)
rrect(ax,60,8,54,50,(1,1,1),ec=LGRAY,rad=16)
ax.text(10,54,"Code (clickable ranges)",fontsize=11,color=DARK,fontweight='bold')
ax.text(64,54,"Doc (linked callouts)",fontsize=11,color=DARK,fontweight='bold')

# highlight ranges in code
for i in range(6):
    fc=(0.96,0.96,0.98)
    ax.add_patch(Rectangle((10,46-5*i),44,3,ec=None,fc=fc))
# range tags
for i,lab in enumerate(["R1","R2","R3"]):
    rrect(ax,49,46-10*i,4,3,fc=PURPLE,ec=PURPLE,rad=6)
    ax.text(51,47.5-10*i,lab,fontsize=8,color='white',ha='center',va='center')

# doc callout cards
for i,t in enumerate(["R1: define symbols","R2: compute c_j","R3: sum weights"]):
    rrect(ax,64,45-12*i,46,10,fc=(0.99,0.99,1),ec=TEAL,rad=14)
    ax.text(66,52-12*i,t,fontsize=10,color=DARK,fontweight='bold')
    ax.text(66,48.5-12*i,"Short explanation.",fontsize=9,color=GRAY)

ax.text(10,16,"More interactive. More JS logic.\nHarder to maintain.",fontsize=9.5,color=GRAY)

plt.tight_layout()
plt.savefig('visualizations/side_by_side_callouts_vs_static.png',dpi=200)
