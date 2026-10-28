"""Validate local web assets."""
import re
from pathlib import Path

from scripts.preflight.result import CheckResult

ROOT = Path(__file__).resolve().parents[2]
# Navigation to the local companion static site is allowed; remote assets remain blocked.
PATTERNS = (r'href=["\']https?://(?!(?:localhost|127\.0\.0\.1)(?::\d+)?(?:/|["\']))', r'src=["\']https?://(?!localhost|127\.0\.0\.1)')


def check_no_external_assets(verbose: bool = False) -> CheckResult:
    """Reject external assets from local documentation surfaces."""
    result = CheckResult("No external assets")
    for base, pattern in ((ROOT / "docs", "**/*.html"), (ROOT / "app", "**/*.html"), (ROOT / "app", "**/*.css")):
        for path in base.glob(pattern):
            if re.search("|".join(PATTERNS), path.read_text(encoding="utf-8"), re.I):
                result.fail(f"{path.relative_to(ROOT)}: external asset detected")
            elif verbose:
                result.info(f"{path.relative_to(ROOT)}: local assets only")
    return result
