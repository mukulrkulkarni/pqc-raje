import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
t=open("docs/mock/module_tutorial_v2_1.html", encoding="utf-8").read()
print(t[5400:11000])
open("tmp_probe.html","w").write("x")
