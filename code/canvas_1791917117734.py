import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def hx(c):
    c=c.lstrip('#'); return tuple(int(c[i:i+2],16) for i in (0,2,4))
def lin(v):
    v/=255.0
    return v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4
def L(rgb):
    r,g,b=[lin(x) for x in rgb]
    return 0.2126*r+0.7152*g+0.0722*b
def cr(a,b):
    la,lb=L(hx(a) if isinstance(a,str) else a), L(hx(b) if isinstance(b,str) else b)
    hi,lo=max(la,lb),min(la,lb)
    return (hi+0.05)/(lo+0.05)
def over(fg_hex, alpha, bg_hex):
    f,b=hx(fg_hex),hx(bg_hex)
    return tuple(round(f[i]*alpha+b[i]*(1-alpha)) for i in range(3))
def tohex(t): return '#%02x%02x%02x'%t

print("="*66)
print("DARK THEME  bg=#0f1115 surface=#161a21 surface2=#1c222b text=#e6e9ef")
print("="*66)
for g in ["#34d399","#3ddc97","#2ee6a8","#4ade80","#22c55e","#10b981","#5eead4"]:
    print(f"{g}  on surface #161a21 = {cr(g,'#161a21'):5.2f} | on bg #0f1115 = {cr(g,'#0f1115'):5.2f}")

print("\n-- dark selected surface = green tint over surface --")
for g in ["#34d399","#3ddc97"]:
    for a in (0.10,0.12):
        s=tohex(over(g,a,'#161a21'))
        print(f"  {g} @{int(a*100)}% -> {s} | text #e6e9ef on it = {cr('#e6e9ef',s):5.2f} | muted #9aa4b4 = {cr('#9aa4b4',s):5.2f} | green text on it = {cr(g,s):5.2f}")

print("\n"+"="*66)
print("LIGHT THEME bg=#f6f7f9 surface=#ffffff surface2=#f1f3f6 text=#141922")
print("="*66)
for g in ["#047857","#059669","#0f766e","#15803d","#16a34a","#0d9488","#00875a"]:
    print(f"{g}  on surface #ffffff = {cr(g,'#ffffff'):5.2f} | on bg #f6f7f9 = {cr(g,'#f6f7f9'):5.2f}")

print("\n-- light selected surface = green tint over white --")
for g in ["#047857","#059669","#16a34a"]:
    for a in (0.10,0.12):
        s=tohex(over(g,a,'#ffffff'))
        print(f"  {g} @{int(a*100)}% -> {s} | text #141922 on it = {cr('#141922',s):5.2f} | muted #5b6472 = {cr('#5b6472',s):5.2f} | green text on it = {cr(g,s):5.2f}")

print("\n-- blue identity accent check --")
print("dark  #5b9dff on #161a21 =", round(cr('#5b9dff','#161a21'),2))
print("light #2563eb on #ffffff =", round(cr('#2563eb','#ffffff'),2))
print("light #1d4ed8 on #ffffff =", round(cr('#1d4ed8','#ffffff'),2))
print("light muted #5b6472 on #ffffff =", round(cr('#5b6472','#ffffff'),2))
print("light text  #141922 on #ffffff =", round(cr('#141922','#ffffff'),2))
print("dark  muted #9aa4b4 on #161a21 =", round(cr('#9aa4b4','#161a21'),2))

print("\n-- non-text UI contrast (>=3.0) : green border vs adjacent surface --")
print("dark  #34d399 vs #161a21 =", round(cr('#34d399','#161a21'),2))
print("light #059669 vs #ffffff =", round(cr('#059669','#ffffff'),2))
print("light #047857 vs #ffffff =", round(cr('#047857','#ffffff'),2))
open("tmp_probe.html","w").write("x")
