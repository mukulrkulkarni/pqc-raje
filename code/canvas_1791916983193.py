import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
t=open("docs/design/module_tutorial_v2_1_spec.md", encoding="utf-8").read()
print(t[:5200])
open("tmp_probe.html","w").write("x")
