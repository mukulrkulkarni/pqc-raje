import ast
import hashlib
import json
from pathlib import Path

paths = [
    Path("tests/test_module_docs.py"),
    Path("docs/design/committee_phase5/discordance_review/snapshot/tests/test_module_docs.py"),
    Path("docs/design/phase6/credibility_review/snapshot/tests/test_module_docs.py"),
]

def inventory(path):
    raw = path.read_bytes()
    tree = ast.parse(raw, filename=str(path))
    names = []
    test_ids = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.append(node.name)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
            test_ids.append(node.name)
        if isinstance(node, ast.ClassDef):
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name.startswith("test_"):
                    test_ids.append(f"{node.name}.{child.name}")
    return {"path": str(path), "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(), "top_level_names": names, "test_ids": test_ids}

items = [inventory(path) for path in paths]
for item in items:
    item["count"] = len(item.pop("test_ids"))
print(json.dumps(items, indent=2))
print("overlaps")
for a in range(len(paths)):
    for b in range(a + 1, len(paths)):
        ai = inventory(paths[a]); bi = inventory(paths[b])
        print(paths[a], paths[b], "top", len(set(ai['top_level_names']) & set(bi['top_level_names'])), "tests", len(set(ai['test_ids']) & set(bi['test_ids'])))
