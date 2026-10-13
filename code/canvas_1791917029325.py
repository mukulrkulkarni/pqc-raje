import sys,re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
t=open("docs/GETTING_STARTED.html", encoding="utf-8").read()
i=t.find(":root"); j=t.find("</style>")
print(t[i:i+1800])
open("tmp_probe.html","w").write("x")
