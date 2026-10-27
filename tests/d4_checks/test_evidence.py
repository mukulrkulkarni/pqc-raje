"""Fixture evidence regression checks."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "out" / "d4-fixture-evidence.json"


def evidence():
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def test_priority_pairs_share_matrix_thresholds_and_directions():
    pairs = [("scenario-5/balanced", "scenario-5/business-criticality-priority", "Business-Criticality"), ("scenario-8/balanced", "scenario-8/data-sensitivity-priority", "Data-Sensitivity")]
    for balanced, priority, criterion in pairs:
        runs = evidence()["runs"]
        assert runs[balanced]["matrix_sha256"] == runs[priority]["matrix_sha256"]
        left, right = [json.loads((ROOT / runs[key]["criteria"]).read_text()) for key in (balanced, priority)]
        assert [(x["name"], x["q"], x["p"], x["v"], x["maximize"]) for x in left] == [(x["name"], x["q"], x["p"], x["v"], x["maximize"]) for x in right]
        assert max(right, key=lambda x: x["weight"])["name"] == criterion


def test_tie_and_near_tie_preserve_full_precision_evidence():
    runs = evidence()["runs"]
    tied, near = runs["exact-tie/balanced"]["net_flow"], runs["near-tie/balanced"]["net_flow"]
    assert tied[0] == tied[1] and near[0] != near[1]
    assert all(value.startswith(("0x", "-0x")) for value in tied + near)


def test_evidence_hashes_match_fixture_bytes_and_cli_runs():
    for record in evidence()["runs"].values():
        for path_key, hash_key in [("matrix", "matrix_sha256"), ("criteria", "criteria_sha256")]:
            assert hashlib.sha256((ROOT / record[path_key]).read_bytes()).hexdigest() == record[hash_key]
        proc = subprocess.run([sys.executable, "-m", "electre3.cli", record["matrix"], record["criteria"], "-y", "-b", "2"], cwd=ROOT, text=True, capture_output=True, check=False)
        assert proc.returncode == 0, proc.stderr
        assert proc.stdout == record["cli_stdout"]
