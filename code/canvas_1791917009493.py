import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
t=open("docs/GETTING_STARTED.html", encoding="utf-8").read()
print(t[:6935])
open("tmp_probe.html","w").write("x")
