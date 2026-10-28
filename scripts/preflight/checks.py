"""Assemble preflight checks."""
import subprocess
import sys

from scripts.preflight.assets import check_no_external_assets
from scripts.preflight.csp import check_csp_headers
from scripts.preflight.lines import check_module_line_limits
from scripts.preflight.ownership import check_generated_docs
from scripts.preflight.result import CheckResult

CHECKS = (check_module_line_limits, check_no_external_assets, check_csp_headers, check_generated_docs)


def check_tests(verbose: bool = False) -> CheckResult:
    """Run the deterministic test suite."""
    result = CheckResult("Test suite")
    process = subprocess.run([sys.executable, "-m", "pytest", "-q", "tests/"], capture_output=True, text=True, timeout=300)
    if process.returncode:
        result.fail(process.stdout.strip().split("\n")[-1])
    else:
        result.info(process.stdout.strip().split("\n")[-1])
    return result
