"""Enforce the local Python executable-line rule."""
from pathlib import Path

from scripts.preflight.result import CheckResult

ROOT = Path(__file__).resolve().parents[2]
EXEMPT = {ROOT / "scripts" / "build_website.py"}


def check_module_line_limits(verbose: bool = False) -> CheckResult:
    """Check H2 support modules; the existing builder remains exempt."""
    result = CheckResult("Python module line limits")
    for path in (ROOT / "scripts" / "preflight").glob("*.py"):
        if path in EXEMPT or path.name == "__init__.py":
            continue
        count = len(path.read_text(encoding="utf-8").splitlines())
        if count > 50:
            result.fail(f"{path.relative_to(ROOT)}: {count} lines (max 50)")
        elif verbose:
            result.info(f"{path.relative_to(ROOT)}: {count} lines OK")
    return result
