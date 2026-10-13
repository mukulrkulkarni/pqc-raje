import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

PURPLE=(100/255,0,255/255)
DARK=(37/255,55/255,70/255)
GRAY=(117/255,120/255,123/255)
TEAL=(126/255,221/255,211/255)
LGRAY=(164/255,188/255,194/255)
BG=(0.975,0.98,0.992)

def rrect(ax,x,y,w,h,fc,ec=None,lw=1,rad=10,alpha=1.0):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle=f"round,pad=0.02,rounding_size={rad}",fc=fc,ec=ec if ec else fc,lw=lw,alpha=alpha))

fig, axes = plt.subplots(2,1,figsize=(12,10))
for ax in axes:
    ax.set_xlim(0,120); ax.set_ylim(0,70); ax.axis('off')

# Static option
ax=axes[0]
rrect(ax,0,0,120,70,BG,rad=0)
rrect(ax,6,60,108,8,(1,1,1),ec=LGRAY,rad=16,alpha=0.9)
ax.text(10,65,"Option 1: Static side-by-side (anchors)",fontsize=14,color=DARK,fontweight='bold')
ax.text(10,62,"Simple. Click section anchors in the doc pane.",fontsize=9.5,color=GRAY)

rrect(ax,6,8,54,50,(1,1,1),ec=LGRAY,rad=16)
rrect(ax,60,8,54,50,(1,1,1),ec=LGRAY,rad=16)
ax.text(10,54,"Code",fontsize=11,color=DARK,fontweight='bold')
ax.text(64,54,"Doc",fontsize=11,color=DARK,fontweight='bold')

for i in range(10):
    ax.add_patch(Rectangle((10,48-3.5*i),44,2.2,ec=None,fc=(0.96,0.96,0.98)))

for i,t in enumerate(["Purpose","Inputs/Outputs","Constraints","How it fits","Walkthrough"]):
    ax.add_patch(Rectangle((64,48-8*i),44,6,ec=LGRAY,fc=(0.99,0.99,1)))
    ax.text(66,51-8*i,t,fontsize=10,color=GRAY)

ax.text(10,12,"Pros: lowest complexity; easy to maintain;\nworks well for printing.",fontsize=9.5,color=GRAY)

# Callouts option
ax=axes[1]
rrect(ax,0,0,120,70,BG,rad=0)
rrect(ax,6,60,108,8,(1,1,1),ec=LGRAY,rad=16,alpha=0.9)
ax.text(10,65,"Option 2: Linked callouts (code ranges → explanations)",fontsize=14,color=DARK,fontweight='bold')
ax.text(10,62,"Interactive. Click a code tag to jump to the matching explanation.",fontsize=9.5,color=GRAY)

rrect(ax,6,8,54,50,(1,1,1),ec=LGRAY,rad=16)
rrect(ax,60,8,54,50,(1,1,1),ec=LGRAY,rad=16)
ax.text(10,54,"Code (tagged ranges)",fontsize=11,color=DARK,fontweight='bold')
ax.text(64,54,"Doc (callout cards)",fontsize=11,color=DARK,fontweight='bold')

for i in range(10):
    ax.add_patch(Rectangle((10,48-3.5*i),44,2.2,ec=None,fc=(0.96,0.96,0.98)))

# tags on code
for i,lab in enumerate(["R1","R2","R3","R4"]):
    rrect(ax,50,48-10*i,4.5,2.8,fc=PURPLE,ec=PURPLE,rad=6)
    ax.text(52.2,49.4-10*i,lab,fontsize=8,color='white',ha='center',va='center')

# callout cards
for i,t in enumerate(["R1: Definitions","R2: Validation","R3: Normalize weights","R4: Return config"]):
    rrect(ax,64,46-10*i,46,8,fc=(0.99,0.99,1),ec=TEAL,rad=14)
    ax.text(66,51-10*i,t,fontsize=10,color=DARK,fontweight='bold')
    ax.text(66,48-10*i,"Short explanation.",fontsize=9,color=GRAY)

ax.text(10,12,"Pros: better teaching flow; more guided.\nCons: more JS and more tests.",fontsize=9.5,color=GRAY)

plt.tight_layout()
plt.savefig('visualizations/side_by_side_callouts_vs_static.png',dpi=200)
