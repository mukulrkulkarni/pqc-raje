"""Independent command-level reproduction for D5 placement corrections."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[2]
COMMANDS = (
    [sys.executable, "scripts/build_website.py"],
    [sys.executable, "-m", "pytest", "-q", "tests/test_d5_placement.py"],
)


def test_d5_independent_reproduction_commands_succeed() -> None:
    for command in COMMANDS:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
