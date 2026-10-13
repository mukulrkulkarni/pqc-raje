import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
def hx(c):
    c=c.lstrip('#'); return tuple(int(c[i:i+2],16) for i in (0,2,4))
def lin(v):
    v/=255.0
    return v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4
def L(r):
    return 0.2126*lin(r[0])+0.7152*lin(r[1])+0.0722*lin(r[2])
def cr(a,b):
    la,lb=L(hx(a) if isinstance(a,str) else a),L(hx(b) if isinstance(b,str) else b)
    hi,lo=max(la,lb),min(la,lb); return (hi+0.05)/(lo+0.05)
def over(f,a,b):
    f,b=hx(f),hx(b); return tuple(round(f[i]*a+b[i]*(1-a)) for i in range(3))
def th(t): return '#%02x%02x%02x'%t

for g in ["#15803d","#047857","#0b7a4b"]:
    for a in (0.10,0.12):
        s=th(over(g,a,'#ffffff'))
        print(f"LIGHT {g}@{int(a*100)}% tint={s}  green-on-tint={cr(g,s):.2f}  text={cr('#141922',s):.2f}  muted={cr('#5b6472',s):.2f}")
    print(f"      {g} on white={cr(g,'#ffffff'):.2f}   on #f6f7f9={cr(g,'#f6f7f9'):.2f}\n")

print("LIGHT bright edge candidates (non-text, need >=3.0 vs white):")
for e in ["#059669","#10b981","#16a34a","#22c55e"]:
    print("  ",e, round(cr(e,'#ffffff'),2))

print("\nDARK final: #3ddc97")
for a in (0.10,0.12):
    s=th(over('#3ddc97',a,'#161a21'))
    print(f"  @{int(a*100)}% tint={s} text={cr('#e6e9ef',s):.2f} muted={cr('#9aa4b4',s):.2f} green={cr('#3ddc97',s):.2f}")
# code pane tint over surface-2 bar? and over bg
print("  dark tint over bg #0f1115 @12% ->", th(over('#3ddc97',0.12,'#0f1115')))
open("tmp_probe.html","w").write("x")
