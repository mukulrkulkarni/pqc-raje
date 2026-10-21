import ast
import hashlib
import json
from pathlib import Path

phase5 = Path("docs/design/committee_phase5/discordance_review/snapshot/tests/test_module_docs.py")
phase6 = Path("docs/design/phase6/credibility_review/snapshot/tests/test_module_docs.py")
active = Path("tests/test_module_docs.py")
archive_paths = [
    Path("docs/design/committee_phase5/discordance_review/snapshot/archive/test_module_docs.py.txt"),
    Path("docs/design/phase6/credibility_review/snapshot/archive/test_module_docs.py.txt"),
]
source_paths = [phase5, phase6]

source_bytes = {str(path).replace("\\", "/"): path.read_bytes() for path in source_paths}
active_bytes = active.read_bytes()
phase5_text = source_bytes[str(phase5).replace("\\", "/")].decode("utf-8")
phase5_tree = ast.parse(phase5_text, filename=str(phase5))
missing = None
for node in phase5_tree.body:
    if isinstance(node, ast.ClassDef) and node.name == "TestCredibilityTutorialScaffold":
        for child in node.body:
            if isinstance(child, ast.FunctionDef) and child.name == "test_no_deterministic_output_assertions":
                lines = phase5_text.splitlines(keepends=True)
                missing = "".join(lines[child.lineno - 1:child.end_lineno]).encode("utf-8")
                break
if missing is None:
    raise RuntimeError("Missing phase-5 credibility test cannot be located")
active_tree_before = ast.parse(active_bytes, filename=str(active))
if any(
    isinstance(node, ast.ClassDef)
    and node.name == "TestCredibilityDeepTutorial"
    and any(
        isinstance(child, ast.FunctionDef) and child.name == "test_no_deterministic_output_assertions"
        for child in node.body
    )
    for node in active_tree_before.body
):
    raise RuntimeError("Phase-5-only test already exists in active credibility test class")
needle = b"class TestRankingTutorialScaffold:"
insertion = missing + b"\r\n\r\n"
if needle not in active_bytes:
    raise RuntimeError("Active insertion point is missing")
active.write_bytes(active_bytes.replace(needle, insertion + needle, 1))

for source, archive in zip(source_paths, archive_paths):
    archive.parent.mkdir(parents=True, exist_ok=True)
    if archive.exists():
        raise RuntimeError(f"Archive destination exists: {archive}")
    source.replace(archive)
    if archive.read_bytes() != source_bytes[str(source).replace("\\", "/")]:
        raise RuntimeError(f"Archive hash mismatch: {archive}")

active_tree = ast.parse(active.read_bytes(), filename=str(active))
active_ids = set()
for node in active_tree.body:
    if isinstance(node, ast.ClassDef):
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name.startswith("test_"):
                active_ids.add(f"{node.name}.{child.name}")
    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
        active_ids.add(node.name)

def source_tests(raw, path):
    tree = ast.parse(raw, filename=path)
    result = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name.startswith("test_"):
                    source_id = f"{node.name}.{child.name}"
                    if source_id == "TestCredibilityTutorialScaffold.test_no_deterministic_output_assertions":
                        target = "TestCredibilityDeepTutorial.test_no_deterministic_output_assertions"
                    elif source_id.startswith("TestCredibilityTutorialScaffold."):
                        target = source_id.replace("TestCredibilityTutorialScaffold", "TestCredibilityDeepTutorial", 1)
                    else:
                        target = source_id
                    result.append({"source_id": source_id, "line": child.lineno, "status": "represented", "active_id": target})
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
            result.append({"source_id": node.name, "line": node.lineno, "status": "represented", "active_id": node.name})
    return result

sources = []
for source, archive in zip(source_paths, archive_paths):
    source_key = str(source).replace("\\", "/")
    entries = source_tests(source_bytes[source_key].decode("utf-8"), source_key)
    missing_targets = [entry["active_id"] for entry in entries if entry["active_id"] not in active_ids]
    if missing_targets:
        raise RuntimeError(f"Unrepresented tests: {missing_targets}")
    sources.append({
        "source_path": source_key,
        "archive_path": str(archive).replace("\\", "/"),
        "original_bytes": len(source_bytes[source_key]),
        "original_sha256": hashlib.sha256(source_bytes[source_key]).hexdigest(),
        "archived_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        "classes": [node.name for node in ast.parse(source_bytes[source_key]).body if isinstance(node, ast.ClassDef)],
        "tests": entries,
    })
manifest = {
    "schema_version": 1,
    "purpose": "Maps every duplicate archived test to its active consolidated representation.",
    "active_module": "tests/test_module_docs.py",
    "active_test_count": len(active_ids),
    "sources": sources,
    "obsolete_tests": [],
    "validation": {
        "all_source_tests_represented": True,
        "archive_contents_byte_identical": True,
        "archives_are_non_python": True
    }
}
Path("out/test-collection-merge-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
