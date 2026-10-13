import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
print(open("docs/design/module_tutorial_v2_1_spec.md", encoding="utf-8").read())
open("tmp_probe.html","w").write("<html><body>probe</body></html>")
