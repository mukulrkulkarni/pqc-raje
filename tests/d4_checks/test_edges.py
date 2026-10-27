"""D4 negative, link, and numerical edge regression checks."""
import subprocess
import sys
from pathlib import Path

import numpy as np

from tests.test_local_document_links import _check_links

ROOT = Path(__file__).resolve().parents[2]


def test_invalid_fixture_header_is_rejected(tmp_path):
    criteria = ROOT / "examples/d4_phase2/scenario-3/criteria_balanced.json"
    bad = tmp_path / "bad.csv"
    bad.write_text("Asset ID / IP,Migration-Complexity,Quantum-Vulnerability,Business-Criticality,Data-Sensitivity\na,0.1,0.2,0.3,0.4\nb,0.5,0.6,0.7,0.8\n", encoding="utf-8")
    proc = subprocess.run([sys.executable, "-m", "electre3.cli", str(bad), str(criteria), "-y"], cwd=ROOT, text=True, capture_output=True, check=False)
    assert proc.returncode == 1
    assert "CSV row 1 contains a non-numeric score" in proc.stderr


def test_d4_draft_links_and_rejects_missing_target_and_fragment(tmp_path):
    draft = ROOT / "docs/decisions/d4-phase2-tutorial-draft.md"
    assert _check_links(draft) == []
    assert "[Planned D5]" not in draft.read_text(encoding="utf-8")
    source = tmp_path / "d4.md"
    source.write_text("[missing](absent.md) [bad](target.md#missing)", encoding="utf-8")
    (tmp_path / "target.md").write_text("# Present\n", encoding="utf-8")
    assert _check_links(source) == ["missing local target: absent.md", "missing fragment: target.md#missing"]


def test_threshold_precedence_and_veto_edge_cases():
    from electre3.concordance import partial_concordance
    from electre3.credibility import credibility
    from electre3.discordance import discordance
    diff = np.array([[[-0.1]]])
    assert partial_concordance(diff, np.array([.1]), np.array([.1]))[0, 0, 0] == 1.0
    assert discordance(diff, np.array([.1]), np.array([.1]))[0, 0, 0] == 1.0
    assert credibility(np.array([[1.0]]), np.array([[[1.0]]]))[0, 0] == 0.0
