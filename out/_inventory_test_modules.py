import ast
import hashlib
import json
from pathlib import Path

paths = [
    Path("docs/design/committee_phase5/discordance_review/snapshot/tests/test_module_docs.py"),
    Path("docs/design/phase6/credibility_review/snapshot/tests/test_module_docs.py"),
]
inventory = []
for path in paths:
    content = path.read_bytes()
    tree = ast.parse(content, filename=str(path))
    tests = []
    classes = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
            tests.append({"kind": "function", "qualified_name": node.name, "line": node.lineno})
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name.startswith("test_"):
                    tests.append({"kind": "method", "qualified_name": f"{node.name}.{child.name}", "line": child.lineno})
    inventory.append({
        "path": str(path).replace("\\", "/"),
        "bytes": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
        "classes": classes,
        "tests": tests,
    })
print(json.dumps(inventory, indent=2))
