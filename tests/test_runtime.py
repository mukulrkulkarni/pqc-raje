"""Focused tests for Chunk 2C feasibility and byte-identity controls."""
import time

import numpy as np
import pytest

from electre3.runtime import (
    BenchmarkSample, ComputeTimeoutError, FeasibilityError, RuntimeModel,
    bounded_benchmark, deadline_after, estimated_block_bytes, model_from_records, p95_seconds,
    require_before_deadline, require_feasible,
)
from electre3.serialization import serialize_result_json
from electre3.shared import compute_validated_ranking


@pytest.fixture
def criteria():
    return [
        {"name": "a", "weight": 0.25, "q": 0.0, "p": 0.2, "v": 0.8, "maximize": True},
        {"name": "b", "weight": 0.25, "q": 0.0, "p": 0.2, "v": 0.8, "maximize": False},
        {"name": "c", "weight": 0.25, "q": 0.0, "p": 0.2, "v": 0.8, "maximize": True},
        {"name": "d", "weight": 0.25, "q": 0.0, "p": 0.2, "v": 0.8, "maximize": False},
    ]


def test_runtime_model_is_deterministic_and_uses_slowest_pair_cost():
    model = RuntimeModel((
        BenchmarkSample(100, 4, 1000, 0.8, 0.1),
        BenchmarkSample(500, 8, 1000, 2.0, 0.2),
    ))
    first = model.estimate(1000, 4, 1000)
    assert first == model.estimate(1000, 4, 1000)
    assert first.seconds > 0 and first.overhead_seconds == pytest.approx(0.25)
    assert p95_seconds([0.1, 0.3, 0.2]) == 0.3
    from_records = model_from_records((
        __import__("electre3.runtime", fromlist=["BenchmarkRecord"]).BenchmarkRecord(100, 4, 1000, "measured", (0.1, 0.2, 0.3)),
    ))
    assert from_records.estimate(100, 4, 1000).seconds == pytest.approx(0.375)


def test_gate_accepts_limit_and_rejects_over_limit():
    model = RuntimeModel((BenchmarkSample(100, 4, 1000, 1.0),))
    assert require_feasible(model, 100, 4, 1000, limit_seconds=1.25).seconds == pytest.approx(1.25)
    with pytest.raises(FeasibilityError, match="exceeds"):
        require_feasible(model, 101, 4, 1000, limit_seconds=1.25)


def test_deadline_raises_before_partial_result_can_return():
    with pytest.raises(ComputeTimeoutError, match="hard timeout"):
        require_before_deadline(deadline_after(-1) if False else time.monotonic() - 0.001)


def test_bounded_harness_records_all_requested_points_without_large_compute():
    calls = []
    records = bounded_benchmark(
        lambda rows, criteria, block: calls.append((rows, criteria, block)),
        rows=(100, 15000), criteria=(4, 8), block_sizes=(1000, 10000), repeats=1,
        max_measured_rows=1000, max_block_bytes=100 * 1024 * 1024,
    )
    assert len(records) == 8
    assert all(record.rows <= 1000 for record in records if record.status == "measured")
    assert any(record.reason == "measured-row bound" for record in records)
    assert calls
    assert estimated_block_bytes(1000, 4) == 192_000_000


def test_block_sizes_produce_byte_identical_canonical_result(criteria):
    matrix = np.random.default_rng(44).random((48, 4))
    payloads = [
        serialize_result_json(compute_validated_ranking(matrix, criteria, block_size=block))
        for block in (1, 7, 48, 1000, 5000, 10000)
    ]
    assert payloads.count(payloads[0]) == len(payloads)


def test_compute_timeout_does_not_return_partial_result(criteria):
    matrix = np.random.default_rng(8).random((20, 4))
    with pytest.raises(ComputeTimeoutError):
        compute_validated_ranking(matrix, criteria, timeout_seconds=1e-12)
