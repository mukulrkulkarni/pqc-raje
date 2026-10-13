import os, glob
root = os.getcwd()
print("CWD:", root)
for base in ["docs", "docs/design", "docs/mock", "scripts"]:
    p = os.path.join(root, base)
    print("---", base, os.path.isdir(p))
    if os.path.isdir(p):
        for f in sorted(os.listdir(p)):
            fp = os.path.join(p, f)
            print("   ", f, os.path.getsize(fp) if os.path.isfile(fp) else "<dir>")

# fallback: search wider
for pat in ["**/module_tutorial*", "**/*GETTING_START*"]:
    for f in glob.glob(pat, recursive=True):
        print("FOUND:", f)

with open(output_path, "w") as fh:
    fh.write("<html><body>probe</body></html>")
