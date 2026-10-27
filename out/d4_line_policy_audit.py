"""Audit the D4 Python line limit and its documented exception."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D4_PATHS = [
    ROOT / "scripts/convert_matrix_csv.py",
    *sorted((ROOT / "scripts/matrix_csv").glob("*.py")),
    ROOT / "tests/test_d4_fixture_correction.py",
    *sorted((ROOT / "tests/d4_checks").glob("*.py")),
    ROOT / "out/generate_d4_fixture_evidence.py",
    ROOT / "out/d4_line_policy_audit.py",
]
EXCEPTIONS = {ROOT / "scripts/build_website.py": "existing unchanged documented exception"}

def doc_lines(tree):
    return {node.body[0].lineno for node in ast.walk(tree)
            if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            and ast.get_docstring(node, clean=False) and isinstance(node.body[0], ast.Expr)}

def count(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    docs = doc_lines(ast.parse("\n".join(lines)))
    return sum(bool(line.strip()) and not line.lstrip().startswith("#") and index not in docs
               for index, line in enumerate(lines, 1))

def main():
    audited = [*D4_PATHS, *EXCEPTIONS]
    missing = [path for path in audited if not path.exists()]
    if missing:
        raise SystemExit("Missing audit path: " + ", ".join(str(path) for path in missing))
    failures = []
    for path in audited:
        total = count(path)
        state = EXCEPTIONS.get(path, "pass" if total <= 50 else "FAIL")
        print(f"{path.relative_to(ROOT).as_posix()}: {total} ({state})")
        if path not in EXCEPTIONS and total > 50:
            failures.append(path)
    if failures:
        raise SystemExit("D4 line policy failed")

if __name__ == "__main__":
    main()
