"""DC-3 recovery contract for normalized direction-aware pairwise scoring."""
from __future__ import annotations

import csv
import io
import json
import re

import numpy as np
import pytest

from app import create_app
from app.services.result_cache import LatestResultCache
from electre3.block import compute_block
from electre3.config import ComputeConfig, CriterionConfig
from electre3.ranking import compute_ranking
from electre3.serialization import serialize_result_csv, serialize_result_json
from electre3.shared import compute_validated_ranking
from electre3.validate import validate_matrix


def _criteria(*, maximize: bool, q: float = 0.0, p: float = 0.25, v: float = 0.75) -> list[CriterionConfig]:
    return [CriterionConfig("criterion", 1.0, q, p, v, maximize=maximize)]


def _negative_reference(scores: np.ndarray, *, q: float, p: float, v: float) -> tuple[np.ndarray, np.ndarray]:
    """Former negative-score implementation used solely as an independent reference."""
    adjusted = -np.asarray(scores, dtype=np.float64)
    credibility = compute_block(adjusted, adjusted, np.array([q]), np.array([p]), np.array([v]), np.array([1.0]), True)
    flow = credibility.sum(axis=1) - credibility.sum(axis=0)
    return np.argsort(-flow), flow


def test_positive_minimize_endpoints_match_old_reference_and_preserve_input() -> None:
    scores = np.array([[0.0], [0.5], [1.0]])
    before = scores.copy()
    order, accumulator = compute_ranking(scores, _criteria(maximize=False), ComputeConfig(block_size=1))
    expected_order, expected_flow = _negative_reference(scores, q=0.0, p=0.25, v=0.75)
    np.testing.assert_array_equal(scores, before)
    np.testing.assert_array_equal(order, expected_order)
    np.testing.assert_array_equal(accumulator.net_flow(), expected_flow)
    assert order[0] == 0


def test_scientific_subnormal_direct_difference_matches_negative_reference() -> None:
    subnormal = np.nextafter(0.0, 1.0)
    scores = np.array([[0.0], [subnormal]])
    direct = scores[1, 0] - scores[0, 0]
    transformed = (1.0 - scores[1, 0]) - (1.0 - scores[0, 0])
    assert direct == subnormal
    assert transformed == 0.0
    order, accumulator = compute_ranking(scores, _criteria(maximize=False, p=subnormal, v=subnormal), ComputeConfig(block_size=1))
    expected_order, expected_flow = _negative_reference(scores, q=0.0, p=subnormal, v=subnormal)
    np.testing.assert_array_equal(order, expected_order)
    np.testing.assert_array_equal(accumulator.net_flow(), expected_flow)


@pytest.mark.parametrize("difference", [0.0, 0.25, np.nextafter(0.25, 0.0), np.nextafter(0.25, 1.0), 0.75, np.nextafter(0.75, 0.0), np.nextafter(0.75, 1.0)])
def test_edge_threshold_boundaries_match_old_reference(difference: float) -> None:
    scores = np.array([[0.0], [difference]])
    order, accumulator = compute_ranking(scores, _criteria(maximize=False), ComputeConfig(block_size=1))
    expected_order, expected_flow = _negative_reference(scores, q=0.0, p=0.25, v=0.75)
    np.testing.assert_array_equal(order, expected_order)
    np.testing.assert_array_equal(accumulator.net_flow(), expected_flow)


def test_mixed_directions_use_raw_direction_aware_differences() -> None:
    scores = np.array([[0.0, 1.0], [0.5, 0.5], [1.0, 0.0]])
    criteria = [CriterionConfig("benefit", 0.4, 0.0, 0.25, 0.75, True), CriterionConfig("cost", 0.6, 0.0, 0.25, 0.75, False)]
    order, accumulator = compute_ranking(scores, criteria, ComputeConfig(block_size=2))
    adjusted = scores.copy()
    adjusted[:, 1] = -adjusted[:, 1]
    expected = compute_block(adjusted, adjusted, np.zeros(2), np.full(2, 0.25), np.full(2, 0.75), np.array([0.4, 0.6]), True)
    flow = expected.sum(axis=1) - expected.sum(axis=0)
    np.testing.assert_array_equal(order, np.argsort(-flow))
    np.testing.assert_array_equal(accumulator.net_flow(), flow)


@pytest.mark.parametrize("value", [np.nextafter(0.0, -1.0), np.nextafter(1.0, 2.0), np.nan, np.inf, -np.inf])
def test_negative_closed_range_rejected_at_core_and_shared_boundaries(value: float) -> None:
    matrix = np.array([[0.0], [value]])
    with pytest.raises(ValueError, match="normalized|finite"):
        compute_validated_ranking(matrix, [{"name": "criterion", "weight": 1.0, "q": 0.0, "p": 0.25, "v": 0.75, "maximize": False}])


def test_serialization_cache_download_and_end_to_end_remain_stable() -> None:
    criteria = [{"name": "quality", "weight": 1.0, "q": 0.0, "p": 0.25, "v": 0.75, "maximize": False}]
    result = compute_validated_ranking([[0.0], [np.nextafter(0.0, 1.0)]], criteria, identifiers=("low", "subnormal"), block_size=1)
    payload = serialize_result_json(result)
    assert payload == serialize_result_json(result)
    assert json.loads(payload)["identifiers"] == ["low", "subnormal"]
    assert list(csv.reader(io.StringIO(serialize_result_csv(result).decode())))[1][2] in {"low", "subnormal"}
    cache = LatestResultCache()
    token = cache.store("session", "ranking-result.json", payload)
    assert cache.download("session", token) == ("ranking-result.json", payload)

    client = create_app({"TESTING": True, "SECRET_KEY": "dc3-test"}).test_client()
    assert client.post("/app/confirm-inputs", data={"criteria_mode": "json", "criteria_json": json.dumps(criteria)}).status_code == 200
    assert client.post("/app/preview", data={"matrix_csv": "Asset,quality\nlow,0\nsubnormal,5e-324\n", "header_mode": "headered", "missing_replacement": "0"}).status_code == 200
    page = client.post("/app/compute", data={"confirm_compute": "yes"})
    assert page.status_code == 200
    path = re.search(rb'href="(/app/download/[^"]+)"', page.data).group(1).decode()
    assert json.loads(client.get(path).data)["identifiers"] == ["low", "subnormal"]
