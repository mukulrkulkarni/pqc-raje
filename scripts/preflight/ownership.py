"""Validate generated documentation ownership and freshness."""
from pathlib import Path

from scripts.preflight.result import CheckResult

ROOT = Path(__file__).resolve().parents[2]
MODULES = ("config", "validate", "block", "accumulator", "ranking")


def check_generated_docs(verbose: bool = False) -> CheckResult:
    """Require declared sources, generated targets, and fresh outputs."""
    result = CheckResult("Generated documentation integrity")
    manifest = ROOT / "docs" / "GENERATED_DOCUMENTATION.md"
    if not manifest.exists():
        result.fail("docs/GENERATED_DOCUMENTATION.md: ownership declaration missing")
        return result
    for name in MODULES:
        source = ROOT / "docs" / "modules" / f"{name}_tutorial_side_by_side.html"
        target = ROOT / "website" / "modules" / name / "tutorial" / "index.html"
        if not target.exists():
            result.fail(f"{target.relative_to(ROOT)}: generated target missing")
        elif source.stat().st_mtime > target.stat().st_mtime:
            result.fail(f"{target.relative_to(ROOT)}: stale after source update")
        elif verbose:
            result.info(f"{name}: declared output is current")
    return result
