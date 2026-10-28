#!/usr/bin/env python3
"""Run local ELECTRE III preflight checks."""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.preflight.checks import CHECKS, check_tests


def main() -> int:
    parser = argparse.ArgumentParser(description="Run preflight checks")
    parser.add_argument("--run-tests", action="store_true", help="Run pytest")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()
    checks = [check(args.verbose) for check in CHECKS]
    if args.run_tests:
        checks.append(check_tests(args.verbose))
    print("ELECTRE III Preflight Checks\n" + "=" * 60)
    for check in checks:
        print(f"[{'PASS' if check.passed else 'FAIL'}] {check.name}")
        for message in check.messages:
            print(f"       {message}")
    passed = all(check.passed for check in checks)
    print("=" * 60 + "\n" + ("All checks passed!" if passed else "Some checks failed."))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
