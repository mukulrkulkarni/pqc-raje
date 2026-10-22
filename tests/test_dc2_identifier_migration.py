"""DC-2 CSV identifier migration tests by required evidence category."""
from __future__ import annotations

import csv
import io
import json
import re

import numpy as np
import pytest

from app import create_app
from app.routes.workflow import _parse_csv
from app.services.result_cache import LatestResultCache
from electre3.serialization import (
    ComputeConfiguration, RankingResult, serialize_result_csv, serialize_result_json,
)
from electre3.shared import compute_validated_ranking

CRITERIA = [
    {"name": "Quality", "weight": 0.5, "q": 0.0, "p": 0.2, "v": 0.5, "maximize": True},
    {"name": "Cost", "weight": 0.5, "q": 0.0, "p": 0.2, "v": 0.5, "maximize": False},
]
HEADERED = "Asset Ref,Quality,Cost\nA-001,0.9,0.2\n0012,0.5,0.8\n"
HEADERLESS = "A-001,0.9,0.2\n0012,0.5,0.8\n"


def _client():
    return create_app({"TESTING": True, "SECRET_KEY": "dc2-test"}).test_client()


def _start(client):
    assert client.post("/app/confirm-inputs", data={"criteria_mode": "json", "criteria_json": json.dumps(CRITERIA)}).status_code == 200


def test_unit_headered_and_headerless_csv_extract_only_numeric_core():
    headered, headers, identifiers = _parse_csv(HEADERED.encode(), CRITERIA, "headered", False, 0.0)
    headerless, fallback_headers, fallback_identifiers = _parse_csv(HEADERLESS.encode(), CRITERIA, "headerless", False, 0.0)
    assert headers == ["Asset Ref", "Quality", "Cost"]
    assert fallback_headers == ["Asset ID", "Quality", "Cost"]
    assert identifiers == fallback_identifiers == ["A-001", "0012"]
    assert headered.shape == headerless.shape == (2, 2)
    assert headered.dtype == np.float64 and headered.flags.c_contiguous
    np.testing.assert_array_equal(headered, headerless)


@pytest.mark.parametrize(("text", "message"), [
    ("A-001,0.9\n0012,0.5\n", "expected 3"),
    ("A-001,NaN,0.2\n0012,0.5,0.8\n", "finite"),
    ("A-001,1.1,0.2\n0012,0.5,0.8\n", "normalized"),
    (" ,0.9,0.2\n0012,0.5,0.8\n", "non-empty"),
])
def test_negative_csv_contract_rejects_legacy_or_invalid_scores(text, message):
    with pytest.raises(ValueError, match=message):
        matrix, _, identifiers = _parse_csv(text.encode(), CRITERIA, "headerless", False, 0.0)
        compute_validated_ranking(matrix, CRITERIA, identifiers=identifiers)


def test_edge_identifier_bounds_and_control_characters_are_rejected():
    valid = compute_validated_ranking([[0.0, 1.0], [1.0, 0.0]], CRITERIA, identifiers=("x" * 50, "=2+2"))
    assert valid.identifiers[0] == "x" * 50
    for identifiers, message in [(("x" * 51, "B"), "50"), (("A\x00", "B"), "control"), (("same", "same"), "unique")]:
        with pytest.raises(ValueError, match=message):
            compute_validated_ranking([[0.0, 1.0], [1.0, 0.0]], CRITERIA, identifiers=identifiers)


def test_integration_headerless_preview_compute_and_download_keep_ids():
    client = _client()
    _start(client)
    preview = client.post("/app/preview", data={"matrix_csv": HEADERLESS, "header_mode": "headerless", "missing_replacement": "0"})
    assert preview.status_code == 200 and b"Asset ID" in preview.data and b">0012<" in preview.data
    page = client.post("/app/compute", data={"confirm_compute": "yes"})
    assert page.status_code == 200 and b"Asset ID" in page.data
    path = re.search(rb'href="(/app/download/[^"]+)"', page.data).group(1).decode()
    payload = client.get(path)
    assert payload.status_code == 200
    assert json.loads(payload.data)["identifiers"] == ["A-001", "0012"]


def test_ui_headered_source_label_and_html_identifier_are_escaped():
    client = _client()
    _start(client)
    source = "System &amp; Ref,Quality,Cost\n&lt;img src=x onerror=1&gt;,0.9,0.2\nplain,0.5,0.8\n"
    preview = client.post("/app/preview", data={"matrix_csv": source, "header_mode": "headered", "missing_replacement": "0"})
    assert preview.status_code == 200
    assert b"System &amp;amp; Ref" in preview.data and b"&amp;lt;img src=x onerror=1&amp;gt;" in preview.data
    page = client.post("/app/compute", data={"confirm_compute": "yes"})
    assert b"System &amp;amp; Ref" in page.data and b"<img src=x onerror=1>" not in page.data


def test_serialization_and_cache_preserve_ranked_identifier_bytes():
    result = compute_validated_ranking([[0.9, 0.2], [0.5, 0.8]], CRITERIA, identifiers=("=2+2", '東京,"ID"'))
    payload = serialize_result_json(result)
    assert json.loads(payload)["identifiers"] == ["=2+2", '東京,"ID"']
    rows = list(csv.reader(io.StringIO(serialize_result_csv(result).decode())))
    assert {row[2] for row in rows[1:]} == {"=2+2", '東京,"ID"'}
    cache = LatestResultCache()
    token = cache.store("session", "ranking-result.json", payload)
    assert cache.download("session", token) == ("ranking-result.json", payload)


def test_result_model_rejects_identifier_loss_or_unsafe_values():
    base = dict(ranking=[0, 1], net_flow=[0.2, 0.1], criteria=(), configuration=ComputeConfiguration(1, True, None))
    for identifiers, message in [(("only",), "match"), (("", "two"), "non-empty"), (("one\n", "two"), "control")]:
        with pytest.raises(ValueError, match=message):
            RankingResult(identifiers=identifiers, **base)


def test_end_to_end_headered_page_download_and_result_share_source_identifiers():
    client = _client()
    _start(client)
    assert client.post("/app/preview", data={"matrix_csv": HEADERED, "header_mode": "headered", "missing_replacement": "0"}).status_code == 200
    page = client.post("/app/compute", data={"confirm_compute": "yes"})
    assert b"Asset Ref" in page.data and b">A-001<" in page.data
    path = re.search(rb'href="(/app/download/[^"]+)"', page.data).group(1).decode()
    result = json.loads(client.get(path).data)
    assert set(result["identifiers"]) == {"A-001", "0012"}
