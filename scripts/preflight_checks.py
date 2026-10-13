#!/usr/bin/env python3
"""Pre-commit style checks for ELECTRE III project.

Exit codes:
    0 - All checks passed
    1 - One or more checks failed

Usage:
    python scripts/preflight_checks.py [--run-tests] [--verbose]
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

# Configuration
MAX_CORE_MODULE_LINES = 50
EXCLUDED_MODULES = {"__init__.py"}
HARDENED_CSP_REQUIRED = "default-src 'none'"

# Paths relative to project root
PROJECT_ROOT = Path(__file__).parent.parent
ELECTRE3_DIR = PROJECT_ROOT / "electre3"
DOCS_DIR = PROJECT_ROOT / "docs"
APP_DIR = PROJECT_ROOT / "app"
TEMPLATES_DIR = APP_DIR / "templates"
STATIC_DIR = APP_DIR / "static"

# URL patterns to detect external assets
EXTERNAL_URL_PATTERNS = [
    r'href=["\']https?://(?!localhost)',
    r'src=["\']https?://(?!localhost)',
    r'url\(["\']?https?://(?!localhost)',
    r'@import\s+["\']https?://(?!localhost)',
    r'@import\s+url\(["\']?https?://(?!localhost)',
    # Protocol-relative URLs (//external.com)
    r'(?:href|src)=["\']//(?!localhost)',
    r'url\(["\']?//(?!localhost)',
]

# Design token classes expected in UI
EXPECTED_CSS_CLASSES = ["--color-", "--space-", "--font-"]


class CheckResult:
    """Result of a single check."""

    def __init__(self, name: str):
        self.name = name
        self.passed = True
        self.messages: list[str] = []

    def fail(self, msg: str) -> None:
        self.passed = False
        self.messages.append(f"FAIL: {msg}")

    def warn(self, msg: str) -> None:
        self.messages.append(f"WARN: {msg}")

    def info(self, msg: str) -> None:
        self.messages.append(f"INFO: {msg}")


def check_module_line_limits(verbose: bool = False) -> CheckResult:
    """Check that core modules are within line limits."""
    result = CheckResult("Core module line limits")

    if not ELECTRE3_DIR.exists():
        result.fail(f"electre3/ directory not found")
        return result

    for py_file in ELECTRE3_DIR.glob("*.py"):
        if py_file.name in EXCLUDED_MODULES:
            continue

        lines = py_file.read_text(encoding="utf-8").splitlines()
        line_count = len(lines)

        if line_count > MAX_CORE_MODULE_LINES:
            result.fail(
                f"{py_file.name}: {line_count} lines (max {MAX_CORE_MODULE_LINES})"
            )
        elif verbose:
            result.info(f"{py_file.name}: {line_count} lines OK")

    return result


def check_no_external_assets(verbose: bool = False) -> CheckResult:
    """Check that no external URLs are referenced in HTML/CSS/JS."""
    result = CheckResult("No external assets")

    patterns_to_check = [
        (DOCS_DIR, "**/*.html"),
        (TEMPLATES_DIR, "**/*.html"),
        (STATIC_DIR, "**/*.css"),
        (STATIC_DIR, "**/*.js"),
    ]

    combined_pattern = "|".join(EXTERNAL_URL_PATTERNS)

    for base_dir, glob_pattern in patterns_to_check:
        if not base_dir.exists():
            continue

        for file_path in base_dir.glob(glob_pattern):
            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception:
                continue

            matches = re.findall(combined_pattern, content, re.IGNORECASE)
            if matches:
                rel_path = file_path.relative_to(PROJECT_ROOT)
                result.fail(f"{rel_path}: external URL detected: {matches[0][:50]}...")
            elif verbose:
                rel_path = file_path.relative_to(PROJECT_ROOT)
                result.info(f"{rel_path}: no external assets")

    return result


def check_csp_headers(verbose: bool = False) -> CheckResult:
    """Check that HTML files have hardened CSP meta tags."""
    result = CheckResult("CSP headers")

    html_files_to_check = []

    # Check docs HTML
    getting_started = DOCS_DIR / "GETTING_STARTED.html"
    if getting_started.exists():
        html_files_to_check.append(getting_started)

    modules_dir = DOCS_DIR / "modules"
    if modules_dir.exists():
        html_files_to_check.extend(modules_dir.glob("*.html"))

    # Check app templates
    if TEMPLATES_DIR.exists():
        html_files_to_check.extend(TEMPLATES_DIR.glob("*.html"))

    for html_file in html_files_to_check:
        try:
            content = html_file.read_text(encoding="utf-8")
        except Exception:
            continue

        if HARDENED_CSP_REQUIRED not in content:
            rel_path = html_file.relative_to(PROJECT_ROOT)
            result.fail(f"{rel_path}: missing hardened CSP ('{HARDENED_CSP_REQUIRED}')")
        elif verbose:
            rel_path = html_file.relative_to(PROJECT_ROOT)
            result.info(f"{rel_path}: CSP OK")

    # Check Flask app for security headers (required)
    app_init = APP_DIR / "__init__.py"
    if app_init.exists():
        content = app_init.read_text(encoding="utf-8")
        if "Content-Security-Policy" not in content or "after_request" not in content:
            result.fail("app/__init__.py: missing CSP response headers via @after_request")
        elif verbose:
            result.info("app/__init__.py: Flask CSP headers OK")

    return result


def check_design_tokens(verbose: bool = False) -> CheckResult:
    """Check that design tokens are present and used."""
    result = CheckResult("Design tokens")

    # Check for tokens file
    tokens_file = DOCS_DIR / "design" / "tokens.css"
    if not tokens_file.exists():
        # Also check in static
        tokens_file = STATIC_DIR / "tokens.css"

    # Check style.css has token definitions
    style_css = STATIC_DIR / "style.css"
    if style_css.exists():
        content = style_css.read_text(encoding="utf-8")
        for token_pattern in EXPECTED_CSS_CLASSES:
            if token_pattern not in content:
                result.fail(f"style.css: missing token pattern '{token_pattern}'")
            elif verbose:
                result.info(f"style.css: found '{token_pattern}'")
    else:
        result.warn("app/static/style.css not found")

    # Check for problematic fixed/absolute positioning
    if style_css.exists():
        content = style_css.read_text(encoding="utf-8")
        # Allow position in specific contexts
        pos_matches = re.findall(
            r"position\s*:\s*(fixed|absolute)", content, re.IGNORECASE
        )
        if pos_matches:
            result.warn(f"style.css: {len(pos_matches)} fixed/absolute positions found")

    return result


def check_tests(verbose: bool = False) -> CheckResult:
    """Run pytest and check all tests pass."""
    result = CheckResult("Test suite")

    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=300,
        )

        if proc.returncode != 0:
            # Extract summary line
            lines = proc.stdout.strip().split("\n")
            summary = lines[-1] if lines else "No output"
            result.fail(f"pytest failed: {summary}")
            if verbose:
                result.info(proc.stdout)
        else:
            lines = proc.stdout.strip().split("\n")
            summary = lines[-1] if lines else "passed"
            result.info(f"pytest: {summary}")

    except subprocess.TimeoutExpired:
        result.fail("pytest timed out after 300s")
    except Exception as e:
        result.fail(f"pytest error: {e}")

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run preflight checks")
    parser.add_argument("--run-tests", action="store_true", help="Run pytest")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    print("=" * 60)
    print("ELECTRE III Preflight Checks")
    print("=" * 60)
    print()

    checks = [
        check_module_line_limits(args.verbose),
        check_no_external_assets(args.verbose),
        check_csp_headers(args.verbose),
        check_design_tokens(args.verbose),
    ]

    if args.run_tests:
        checks.append(check_tests(args.verbose))

    all_passed = True
    for check in checks:
        status = "PASS" if check.passed else "FAIL"
        print(f"[{status}] {check.name}")

        for msg in check.messages:
            print(f"       {msg}")

        if not check.passed:
            all_passed = False

        print()

    print("=" * 60)
    if all_passed:
        print("All checks passed!")
        return 0
    else:
        print("Some checks failed. Fix issues before committing.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
