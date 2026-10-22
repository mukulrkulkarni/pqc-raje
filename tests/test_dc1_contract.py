"""DC-1 identifier-contract tests: unit, integration, scientific, security, and E2E."""
from __future__ import annotations

import json

import numpy as np
import pytest

from app import create_app
from app.routes.workflow import _parse_csv
from electre3.config import ComputeConfig, CriterionConfig
from electre3.data import load_input
from electre3.ranking import compute_ranking
from electre3.serialization import SERIALIZER_VERSION, serialize_result_json
from electre3.shared import compute_validated_ranking, validate_criteria

CRITERIA = [
    {"name": "quality", "weight": 0.5, "q": 0.0, "p": 0.2, "v": 0.5, "maximize": True},
    {"name": "cost", "weight": 0.5, "q": 0.0, "p": 0.2, "v": 0.5, "maximize": False},
]


def test_unit_csv_loader_preserves_headered_identifiers(tmp_path):
    path = tmp_path / "assets.csv"
    path.write_text("System ID,quality,cost\nalpha,0.9,0.2\nbeta,0.4,0.8\n", encoding="utf-8")
    loaded = load_input(path, validate_criteria(CRITERIA), header_mode="headered")
    assert loaded.identifier_header == "System ID"
    assert loaded.identifiers == ("alpha", "beta")
    np.testing.assert_array_equal(loaded.scores, [[0.9, 0.2], [0.4, 0.8]])


def test_unit_headerless_csv_uses_asset_id_label(tmp_path):
    path = tmp_path / "assets.csv"
    path.write_text("alpha,0.9,0.2\nbeta,0.4,0.8\n", encoding="utf-8")
    loaded = load_input(path, validate_criteria(CRITERIA), header_mode="headerless")
    assert loaded.identifier_header == "Asset ID"
    assert loaded.identifiers == ("alpha", "beta")


@pytest.mark.parametrize("csv_text, error", [
    ("Asset ID,quality,cost\n ,0.9,0.2\nbeta,0.4,0.8\n", "non-empty"),
    ("Asset ID,quality,cost\nalpha,0.9,0.2\nalpha,0.4,0.8\n", "unique"),
    ("Asset ID,quality,cost\n" + "x" * 51 + ",0.9,0.2\nbeta,0.4,0.8\n", "50"),
])
def test_security_identifier_validation_rejects_ambiguous_values(csv_text, error):
    with pytest.raises(ValueError, match=error):
        _parse_csv(csv_text.encode(), CRITERIA, "headered", False, 0.0)


def test_edge_numpy_input_uses_positional_identifiers(tmp_path):
    path = tmp_path / "scores.npy"
    np.save(path, np.array([[0.0, 1.0], [1.0, 0.0]]))
    loaded = load_input(path, validate_criteria(CRITERIA))
    assert loaded.identifiers == ("0", "1")
    assert loaded.identifier_header == "Asset ID"


def test_integration_ranking_and_v2_serialization_preserve_identifiers():
    result = compute_validated_ranking(
        [[0.9, 0.2], [0.4, 0.8]], CRITERIA, identifiers=("asset-A", "asset-B")
    )
    payload = json.loads(serialize_result_json(result))
    assert SERIALIZER_VERSION == "2"
    assert payload["serializer_version"] == "2"
    assert payload["identifiers"] == ["asset-A", "asset-B"]


def test_scientific_minimize_translation_is_invariant_at_boundaries():
    criteria = [CriterionConfig("cost", 1.0, 0.0, 0.2, 0.5, maximize=False)]
    scores = np.array([[0.0], [0.5], [1.0]])
    order, accumulator = compute_ranking(scores, criteria, ComputeConfig(block_size=1))
    transformed_order, transformed = compute_ranking(1.0 - scores, [CriterionConfig("benefit", 1.0, 0.0, 0.2, 0.5)], ComputeConfig(block_size=2))
    np.testing.assert_array_equal(order, transformed_order)
    np.testing.assert_allclose(accumulator.net_flow(), transformed.net_flow())
    assert order[0] == 0


def test_end_to_end_web_download_preserves_source_identifier():
    app = create_app({"TESTING": True, "SECRET_KEY": "dc1-test"})
    client = app.test_client()
    criteria = json.dumps(CRITERIA)
    assert client.post("/app/confirm-inputs", data={"criteria_mode": "json", "criteria_json": criteria}).status_code == 200
    preview = client.post("/app/preview", data={
        "matrix_csv": "Inventory Key,quality,cost\nasset-A,0.9,0.2\nasset-B,0.4,0.8\n",
        "header_mode": "headered", "missing_replacement": "0",
    })
    assert preview.status_code == 200
    page = client.post("/app/compute", data={"confirm_compute": "yes"})
    assert page.status_code == 200 and b"asset-A" in page.data
    token = page.data.split(b'/app/download/', 1)[1].split(b'"', 1)[0].decode()
    result = json.loads(client.get("/app/download/" + token).data)
    assert result["identifiers"] == ["asset-A", "asset-B"]
