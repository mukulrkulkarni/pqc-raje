"""Strict shared CLI and web input contract for ELECTRE III."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
import math
from numbers import Real
from typing import Any

import numpy as np

from .config import ComputeConfig, CriterionConfig
from .ranking import compute_ranking
from .runtime import HARD_TIMEOUT_SECONDS, RuntimeModel, deadline_after, require_feasible
from .serialization import ComputeConfiguration, CriterionMetadata, RankingResult

MAX_CRITERIA = 8
MAX_ROWS = 100_000
DEFAULT_BLOCK_SIZE = 1_000
MIN_BLOCK_SIZE = 1
MAX_BLOCK_SIZE = 10_000
_WEIGHT_SUM_TOLERANCE = 1e-12
_REQUIRED_CRITERION_FIELDS = ("name", "weight", "q", "p", "v", "maximize")

ComputeResult = RankingResult


def _finite_number(value: Any, field: str, index: int) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"criterion {index} field '{field}' must be a finite number")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"criterion {index} field '{field}' must be finite")
    return number


def validate_criteria(criteria_data: Any) -> list[CriterionConfig]:
    """Validate and convert criteria under the approved shared policy."""
    if not isinstance(criteria_data, list):
        raise ValueError("criteria must be a list")
    if not 1 <= len(criteria_data) <= MAX_CRITERIA:
        raise ValueError(f"criteria must contain 1 through {MAX_CRITERIA} entries")
    criteria: list[CriterionConfig] = []
    weights: list[float] = []
    for index, raw in enumerate(criteria_data):
        if not isinstance(raw, Mapping):
            raise ValueError(f"criterion {index} must be an object")
        missing = [field for field in _REQUIRED_CRITERION_FIELDS if field not in raw]
        if missing:
            raise ValueError(f"criterion {index} missing required field '{missing[0]}'")
        name = raw["name"]
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"criterion {index} field 'name' must be a non-empty string")
        maximize = raw["maximize"]
        if type(maximize) is not bool:
            raise ValueError(f"criterion {index} field 'maximize' must be a boolean")
        weight = _finite_number(raw["weight"], "weight", index)
        q = _finite_number(raw["q"], "q", index)
        p = _finite_number(raw["p"], "p", index)
        v = _finite_number(raw["v"], "v", index)
        criteria.append(CriterionConfig(name, weight, q, p, v, maximize))
        weights.append(weight)
    if not math.isclose(math.fsum(weights), 1.0, rel_tol=0.0, abs_tol=_WEIGHT_SUM_TOLERANCE):
        raise ValueError("criteria weights must sum to 1")
    return criteria


def validate_score_matrix(matrix: Any, criterion_count: int) -> np.ndarray:
    """Validate finite normalized scores and return a C-contiguous float64 matrix."""
    try:
        scores = np.asarray(matrix, dtype=np.float64)
    except (TypeError, ValueError) as exc:
        raise ValueError("matrix must contain numeric scores") from exc
    if scores.ndim != 2:
        raise ValueError(f"matrix must be 2D, got {scores.ndim}D")
    if not 2 <= scores.shape[0] <= MAX_ROWS:
        raise ValueError(f"matrix must contain 2 through {MAX_ROWS} rows")
    if scores.shape[1] != criterion_count:
        raise ValueError(f"matrix has {scores.shape[1]} columns, expected {criterion_count}")
    if not np.isfinite(scores).all():
        raise ValueError("matrix scores must be finite")
    if np.any(scores < 0.0) or np.any(scores > 1.0):
        raise ValueError("matrix scores must be normalized to [0, 1]")
    return np.ascontiguousarray(scores, dtype=np.float64)


def validate_csv_headers(headers: Sequence[Any], criteria: Sequence[CriterionConfig]) -> None:
    """Validate header-mode identifier and ordered criterion-name mapping."""
    expected = [criterion.name for criterion in criteria]
    if len(headers) != len(expected) + 1:
        raise ValueError(f"CSV header has {len(headers)} columns, expected {len(expected) + 1}")
    if not isinstance(headers[0], str) or not headers[0].strip():
        raise ValueError("CSV identifier header must be a non-empty string")
    if list(headers[1:]) != expected:
        raise ValueError("CSV criterion headers must match criteria names in order")


def compute_validated_ranking(
    matrix: Any,
    criteria_data: Any,
    block_size: int = DEFAULT_BLOCK_SIZE,
    *,
    runtime_model: RuntimeModel | None = None,
    timeout_seconds: float = HARD_TIMEOUT_SECONDS,
) -> ComputeResult:
    """Validate, gate, compute, and return a complete immutable ranking result.

    Passing a runtime model activates the pre-compute feasibility gate. The default
    preserves existing CLI and Chunk 2A behavior until a deployment profile supplies
    measured benchmarks.
    """
    if isinstance(block_size, bool) or not isinstance(block_size, int):
        raise ValueError("block_size must be an integer")
    if not MIN_BLOCK_SIZE <= block_size <= MAX_BLOCK_SIZE:
        raise ValueError(f"block_size must be between {MIN_BLOCK_SIZE} and {MAX_BLOCK_SIZE}")
    criteria = validate_criteria(criteria_data)
    scores = validate_score_matrix(matrix, len(criteria))
    if runtime_model is not None:
        require_feasible(runtime_model, scores.shape[0], len(criteria), block_size)
    configuration = ComputeConfig(block_size=block_size)
    ranking, accumulator = compute_ranking(
        scores, criteria, configuration, deadline=deadline_after(timeout_seconds)
    )
    return ComputeResult(
        ranking=ranking,
        net_flow=accumulator.net_flow(),
        identifiers=tuple(str(index) for index in range(scores.shape[0])),
        criteria=tuple(CriterionMetadata(**criterion.__dict__) for criterion in criteria),
        configuration=ComputeConfiguration(
            block_size=configuration.block_size,
            use_numba=configuration.use_numba,
            seed=configuration.seed,
        ),
    )
