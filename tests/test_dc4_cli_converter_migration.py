"""DC-4 CLI, converter, documentation, and identifier-boundary regression evidence."""
from __future__ import annotations

import csv
import io
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from app import create_app
from app.services.result_cache import LatestResultCache
from electre3.config import ComputeConfig, CriterionConfig
from electre3.data import load_input
from electre3.ranking import compute_ranking
from electre3.serialization import SERIALIZER_VERSION, serialize_result_csv, serialize_result_json
from electre3.shared import compute_validated_ranking, validate_criteria
from scripts.convert_matrix_csv import ConversionError, convert_csv_to_matrix

ROOT = Path(__file__).resolve().parents[1]
CRITERIA = [
    {"name": "Quality", "weight": 0.5, "q": 0.0, "p": 0.2, "v": 0.5, "maximize": True},
    {"name": "Cost", "weight": 0.5, "q": 0.0, "p": 0.2, "v": 0.5, "maximize": False},
]


def _write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "assets.csv"
    path.write_text(text, encoding="utf-8")
    return path


def test_positive_cli_headered_csv_preserves_ids_and_expected_example_output() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "electre3.cli", "examples/assets_priority/matrix_with_headers.csv",
         "examples/assets_priority/criteria.json", "-y"],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout == "Ranking:\n  1. B\n  2. A\n  3. C\n"
    assert (ROOT / "examples/assets_priority/ranking.txt").read_text(encoding="utf-8") == completed.stdout


def test_positive_converter_validates_ids_then_numpy_cli_uses_positional_ids(tmp_path: Path) -> None:
    source = _write(tmp_path, "Asset,Quality,Cost\nA-001,0.9,0.2\n0012,0.5,0.8\n")
    matrix = convert_csv_to_matrix(source, has_header=True, id_col="Asset")
    npy = tmp_path / "matrix.npy"
    np.save(npy, matrix)
    loaded = load_input(npy, validate_criteria(CRITERIA))
    assert loaded.scores.shape == (2, 2)
    assert loaded.identifiers == ("0", "1")
    assert loaded.identifier_header == "Asset ID"


@pytest.mark.parametrize(("csv_text", "error"), [
    ("Asset,Quality,Cost\n,0.9,0.2\nB,0.5,0.8\n", "non-empty"),
    ("Asset,Quality,Cost\nA,0.9,0.2\nA,0.5,0.8\n", "unique"),
    ("Asset,Quality,Cost\nA\x00,0.9,0.2\nB,0.5,0.8\n", "control"),
    ("Asset,Quality,Cost\n" + "x" * 51 + ",0.9,0.2\nB,0.5,0.8\n", "50"),
])
def test_negative_converter_rejects_unsafe_or_lossy_identifiers(tmp_path: Path, csv_text: str, error: str) -> None:
    with pytest.raises(ConversionError, match=error):
        convert_csv_to_matrix(_write(tmp_path, csv_text), has_header=True, id_col="Asset")


def test_edge_headerless_and_headered_loader_rules_are_explicit(tmp_path: Path) -> None:
    headerless = _write(tmp_path, "A-001,0.9,0.2\n0012,0.5,0.8\n")
    loaded = load_input(headerless, validate_criteria(CRITERIA), header_mode="headerless")
    assert loaded.identifier_header == "Asset ID"
    assert loaded.identifiers == ("A-001", "0012")
    headered = _write(tmp_path, "Source Ref,Quality,Cost\nA-001,0.9,0.2\n0012,0.5,0.8\n")
    loaded = load_input(headered, validate_criteria(CRITERIA), header_mode="headered")
    assert loaded.identifier_header == "Source Ref"
    with pytest.raises(ValueError, match="criterion headers"):
        load_input(_write(tmp_path, "Source Ref,Cost,Quality\nA,0.9,0.2\nB,0.5,0.8\n"), validate_criteria(CRITERIA), header_mode="headered")


def test_scientific_direct_minimize_remains_equivalent_to_negative_reference() -> None:
    scores = np.array([[0.0], [np.nextafter(0.0, 1.0)]])
    criterion = CriterionConfig("Cost", 1.0, 0.0, np.nextafter(0.0, 1.0), np.nextafter(0.0, 1.0), maximize=False)
    order, accumulator = compute_ranking(scores, [criterion], ComputeConfig(block_size=1))
    reference_order, reference = compute_ranking(-scores, [CriterionConfig("Cost", 1.0, 0.0, criterion.p, criterion.v)], ComputeConfig(block_size=1))
    np.testing.assert_array_equal(order, reference_order)
    np.testing.assert_array_equal(accumulator.net_flow(), reference.net_flow())


def test_serialization_cache_download_and_web_end_to_end_retain_identifiers() -> None:
    result = compute_validated_ranking([[0.9, 0.2], [0.5, 0.8]], CRITERIA, identifiers=("=asset", '東京,"ID"'))
    payload = serialize_result_json(result)
    assert json.loads(payload)["serializer_version"] == SERIALIZER_VERSION == "2"
    assert json.loads(payload)["identifiers"] == ["=asset", '東京,"ID"']
    rows = list(csv.reader(io.StringIO(serialize_result_csv(result).decode("utf-8"))))
    assert {row[2] for row in rows[1:]} == {"=asset", '東京,"ID"'}
    cache = LatestResultCache()
    token = cache.store("dc4", "ranking-result.json", payload)
    assert cache.download("dc4", token) == ("ranking-result.json", payload)

    client = create_app({"TESTING": True, "SECRET_KEY": "dc4-test"}).test_client()
    assert client.post("/app/confirm-inputs", data={"criteria_mode": "json", "criteria_json": json.dumps(CRITERIA)}).status_code == 200
    assert client.post("/app/preview", data={"matrix_csv": "Source,Quality,Cost\nA-001,0.9,0.2\n0012,0.5,0.8\n", "header_mode": "headered", "missing_replacement": "0"}).status_code == 200
    page = client.post("/app/compute", data={"confirm_compute": "yes"})
    assert page.status_code == 200
    token = page.data.split(b'/app/download/', 1)[1].split(b'"', 1)[0].decode()
    assert json.loads(client.get("/app/download/" + token).data)["identifiers"] == ["A-001", "0012"]


def test_docs_and_examples_state_the_current_contract() -> None:
    for path in (ROOT / "README.md", ROOT / "docs/tutorials/cli_quickstart.md", ROOT / "examples/assets_priority/README.md"):
        text = path.read_text(encoding="utf-8")
        assert "(N,C+1)" in text
        assert "positional" in text
    assert "Asset,E,X,O" in (ROOT / "examples/assets_priority/matrix_with_headers.csv").read_text(encoding="utf-8")
    assert (ROOT / "examples/assets_priority/matrix_numeric_only.csv").read_text(encoding="utf-8").splitlines()[0] == "0.90,0.40,0.60"
