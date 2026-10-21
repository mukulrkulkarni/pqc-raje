import ast
import hashlib
import json
from pathlib import Path

manifest = json.loads(Path("out/test-collection-merge-manifest.json").read_text(encoding="utf-8"))
errors = []
for source in manifest["sources"]:
    archive = Path(source["archive_path"])
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest != source["original_sha256"] or digest != source["archived_sha256"]:
        errors.append(f"hash mismatch: {archive}")
    if archive.suffix == ".py":
        errors.append(f"discoverable archive suffix: {archive}")
active_tree = ast.parse(Path(manifest["active_module"]).read_bytes())
active_ids = {
    f"{node.name}.{child.name}"
    for node in active_tree.body if isinstance(node, ast.ClassDef)
    for child in node.body
    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name.startswith("test_")
}
for source in manifest["sources"]:
    for test in source["tests"]:
        if test["status"] != "represented" or test["active_id"] not in active_ids:
            errors.append(f"unrepresented: {source['source_path']}::{test['source_id']}")
for source in manifest["sources"]:
    if Path(source["source_path"]).exists():
        errors.append(f"discoverable original remains: {source['source_path']}")
if errors:
    raise SystemExit("\n".join(errors))
print(f"verified {sum(len(source['tests']) for source in manifest['sources'])} source test entries mapped to {len(active_ids)} active tests")
