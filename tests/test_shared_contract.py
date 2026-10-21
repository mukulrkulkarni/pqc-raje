"""Focused tests for the strict shared CLI/web input contract."""
import numpy as np
import pytest

from electre3.cli_run import run_ranking
from electre3.shared import (
    MAX_ROWS,
    compute_validated_ranking,
    validate_criteria,
    validate_csv_headers,
    validate_score_matrix,
)


@pytest.fixture
def criteria():
    return [
        {"name": "quality", "weight": 0.6, "q": 0.0, "p": 0.2, "v": 0.8, "maximize": True},
        {"name": "cost", "weight": 0.4, "q": 0.0, "p": 0.1, "v": 0.6, "maximize": False},
    ]


@pytest.fixture
def matrix():
    return np.array([[0.8, 0.4], [0.7, 0.2], [0.2, 0.9]])


def test_adapter_returns_ranking_and_net_flow(criteria, matrix):
    result = compute_validated_ranking(matrix, criteria, block_size=2)
    assert result.ranking.dtype.kind in "iu"
    assert set(result.ranking) == {0, 1, 2}
    assert result.net_flow.shape == (3,)
    assert result.net_flow.dtype == np.dtype("<f8")
    assert result.identifiers == ("0", "1", "2")
    assert result.configuration.block_size == 2
    assert result.ranking.flags.writeable is False
    with pytest.raises(ValueError):
        result.net_flow[0] = 0.0


def test_cli_helper_uses_strict_shared_contract(criteria, matrix):
    np.testing.assert_array_equal(
        run_ranking(matrix, criteria, quiet=True),
        compute_validated_ranking(matrix, criteria).ranking,
    )


@pytest.mark.parametrize("bad_criteria", [
    [],
    [{"name": "x", "weight": 1, "q": 0, "p": 0, "v": 0}],
    [{"name": "x", "weight": 1, "q": 0, "p": 0, "v": 0, "maximize": 1}],
    [{"name": "x", "weight": 0.9, "q": 0, "p": 0, "v": 0, "maximize": True}],
    [{"name": "x", "weight": float("nan"), "q": 0, "p": 0, "v": 0, "maximize": True}],
    [{"name": "x", "weight": 1, "q": 0.3, "p": 0.2, "v": 0.4, "maximize": True}],
])
def test_criteria_contract_rejects_invalid_data(bad_criteria):
    with pytest.raises(ValueError):
        validate_criteria(bad_criteria)


def test_criteria_contract_rejects_more_than_eight():
    criteria = [{"name": str(i), "weight": 1 / 9, "q": 0, "p": 0, "v": 0, "maximize": True} for i in range(9)]
    with pytest.raises(ValueError, match="1 through 8"):
        validate_criteria(criteria)


@pytest.mark.parametrize("bad_matrix", [
    [[0.1, 0.2]],
    [[0.1, 0.2], [np.nan, 0.3]],
    [[0.1, 0.2], [np.inf, 0.3]],
    [[-0.1, 0.2], [0.3, 0.4]],
    [[0.1, 1.1], [0.3, 0.4]],
])
def test_matrix_contract_rejects_invalid_data(bad_matrix):
    with pytest.raises(ValueError):
        validate_score_matrix(bad_matrix, 2)


def test_matrix_contract_rejects_row_limit():
    matrix = np.zeros((MAX_ROWS + 1, 1))
    with pytest.raises(ValueError, match="100000"):
        validate_score_matrix(matrix, 1)


def test_header_mapping_allows_identifier_and_requires_order(criteria):
    parsed = validate_criteria(criteria)
    validate_csv_headers(["Asset ID", "quality", "cost"], parsed)
    with pytest.raises(ValueError, match="match"):
        validate_csv_headers(["Asset ID", "cost", "quality"], parsed)


@pytest.mark.parametrize("block_size", [0, 10_001, True, 1.5])
def test_adapter_rejects_invalid_block_size(criteria, matrix, block_size):
    with pytest.raises(ValueError):
        compute_validated_ranking(matrix, criteria, block_size)


def test_adapter_supports_each_block_size_boundary(criteria, matrix):
    one = compute_validated_ranking(matrix, criteria, block_size=1)
    maximum = compute_validated_ranking(matrix, criteria, block_size=10_000)
    np.testing.assert_array_equal(one.ranking, maximum.ranking)
    np.testing.assert_allclose(one.net_flow, maximum.net_flow)
