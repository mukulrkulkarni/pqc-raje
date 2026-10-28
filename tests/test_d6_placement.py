"""Static, semantic, no-JavaScript, and reproduction checks for D6 placement."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from electre3.concordance import partial_concordance
from electre3.discordance import discordance

ROOT = Path(__file__).parent.parent
CLI = ROOT / "docs" / "tutorials" / "cli_quickstart.md"
RUNBOOK = ROOT / "docs" / "runbook" / "debugging.md"
NOTES = ROOT / "docs" / "decisions" / "d6-placement-notes.md"
REVIEWS = ROOT / "docs" / "decisions" / "d6-placement-reviews.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_d6_reference_uses_owned_user_surfaces() -> None:
    cli, runbook, notes, reviews = map(_read, (CLI, RUNBOOK, NOTES, REVIEWS))
    for token in ("--block-size", "--quiet", "NumPy serialization", "not ELECTRE III distillation", "np.argsort(-net_flow)"):
        assert token in cli
    for token in ("HTTP 413", "HTTP 422", "HTTP 504", "HTTP 410", "HTTP 429", "Serializer version 2", "process-local"):
        assert token in runbook
    assert "No companion-website page is added or changed in D6." in notes
    for role in ("Scientific review — approved", "Engineering review — approved", "UI/UX review — conditional, static scope approved"):
        assert role in reviews


def test_d6_links_and_no_javascript_requirement_are_explicit() -> None:
    cli, runbook = _read(CLI), _read(RUNBOOK)
    assert "../runbook/debugging.md" in cli
    assert (CLI.parent / "../runbook/debugging.md").is_file()
    assert "server-rendered HTML" in runbook
    assert "without JavaScript" in runbook
    assert "<script" not in cli.lower()
    assert "<script" not in runbook.lower()


def test_d6_threshold_edge_branches_preserve_priority() -> None:
    import numpy as np
    equal = np.array([[[0.0]]])
    assert partial_concordance(equal, np.array([0.0]), np.array([0.0]))[0, 0, 0] == 1.0
    assert discordance(equal, np.array([0.0]), np.array([0.0]))[0, 0, 0] == 1.0


def test_d6_negative_malformed_threshold_order_returns_nonzero() -> None:
    command = [sys.executable, "-c", "from electre3.validate import validate_thresholds; from electre3.config import CriterionConfig; validate_thresholds([CriterionConfig('x', 1, .3, .2, .4, True)])"]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    assert result.returncode != 0
    assert "p must be >= q" in result.stderr.lower()
