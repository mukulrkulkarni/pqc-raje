"""Direct and converter CLI parity check."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def execute(*args):
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=False)


def test_direct_csv_and_converter_paths_rank_the_same_rows(tmp_path):
    matrix = ROOT / "examples/d4_phase2/scenario-3/matrix_headered.csv"
    criteria = ROOT / "examples/d4_phase2/scenario-3/criteria_balanced.json"
    direct = execute("-m", "electre3.cli", str(matrix), str(criteria), "-y", "-b", "2")
    converted = tmp_path / "matrix.npy"
    converter = execute("scripts/convert_matrix_csv.py", str(matrix), str(converted), "--has-header", "--id-col", "Asset ID / IP")
    positional = execute("-m", "electre3.cli", str(converted), str(criteria), "-y", "-b", "2")
    assert converter.returncode == positional.returncode == 0, converter.stderr + positional.stderr
    direct_order = [line.rsplit(". ", 1)[1] for line in direct.stdout.splitlines()[1:]]
    indices = [int(line.rsplit(". ", 1)[1]) for line in positional.stdout.splitlines()[1:]]
    identifiers = [line.split(",", 1)[0] for line in matrix.read_text(encoding="utf-8").splitlines()[1:]]
    assert [identifiers[index] for index in indices] == direct_order
