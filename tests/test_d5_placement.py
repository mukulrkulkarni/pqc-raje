"""Static and reproducibility checks for the D5 mental-model tutorial placement."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from electre3.concordance import partial_concordance
from electre3.discordance import discordance

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "docs/modules/ranking_tutorial_side_by_side.html"
GENERATED = ROOT / "website/modules/ranking/tutorial/index.html"
SOURCE_TARGETS = ("#source-references",)
GENERATED_TARGETS = ("#source-references",)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_d5_mental_model_is_semantic_and_branded() -> None:
    text = _text(SOURCE)
    for token in (
        'id="mental-model"', "<var>G</var>", "Σ<sub>b</sub>",
        "<table>", "<caption>Threshold branches", "<pre class=\"diagram\"",
        "Arial,sans-serif", "--accent:#6400ff", "#253746", "#7eddd3",
    ):
        assert token in text
    assert "KaTeX" not in text and "katex" not in text.lower()
    assert not re.search(r'<script[^>]+(?:app|katex)', text, re.I)


def test_d5_threshold_edges_preserve_branch_priority() -> None:
    equal = np.array([[[0.0]]])
    assert partial_concordance(equal, np.array([0.0]), np.array([0.0]))[0, 0, 0] == 1.0
    assert discordance(equal, np.array([0.0]), np.array([0.0]))[0, 0, 0] == 1.0


def test_d5_negative_malformed_threshold_order_is_rejected() -> None:
    command = [sys.executable, "-c", "from electre3.validate import validate_thresholds; from electre3.config import CriterionConfig; validate_thresholds([CriterionConfig('x', 1, .3, .2, .4, True)])"]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    assert result.returncode != 0
    assert "p must be >= q" in result.stderr.lower()


def test_d5_links_resolve_and_generated_output_is_reproducible() -> None:
    for page, targets in ((SOURCE, SOURCE_TARGETS), (GENERATED, GENERATED_TARGETS)):
        text = _text(page)
        for target in targets:
            assert f'href="{target}"' in text
        assert 'id="source-references"' in text
    before = _text(GENERATED)
    result = subprocess.run([sys.executable, "scripts/build_website.py"], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert _text(GENERATED) == before
    assert before.index("<h1") < before.index('id="mental-model"') < before.index("<h2")
    assert "computed binary64 flows" in before
    assert "O(B&sup2;)" not in before
    assert "<var>B1</var>·<var>B2</var>·<var>C</var>" in before


@pytest.mark.parametrize("needle", ["ELECTRE III distillation", "np.argsort(-net_flow)", "D4 fixture criteria"])
def test_d5_verbatim_approved_claims_survive_placement(needle: str) -> None:
    assert needle in _text(SOURCE)
