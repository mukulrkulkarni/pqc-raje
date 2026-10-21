"""Bounded runtime measurement, feasibility decisions, and compute deadlines.

The model is intentionally local to a process profile.  It estimates complete shared
adapter work: input conversion and validation, ranking, and canonical JSON serialization.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import time
from typing import Callable, Iterable, Sequence

import numpy as np

MAX_ESTIMATED_SECONDS = 300.0
HARD_TIMEOUT_SECONDS = 330.0
# diff, concordance, discordance, credibility, and temporary vector allocations.
_TEMPORARY_BYTES_PER_CELL_PER_CRITERION = 48


class FeasibilityError(ValueError):
    """Raised when a computation lacks a safe pre-compute runtime estimate."""


class ComputeTimeoutError(TimeoutError):
    """Raised before a complete ranking result is available."""


@dataclass(frozen=True)
class BenchmarkSample:
    """One p95 runtime observation for a complete validated computation."""

    rows: int
    criteria: int
    block_size: int
    p95_seconds: float
    overhead_seconds: float = 0.0

    def __post_init__(self) -> None:
        if self.rows < 2 or self.criteria < 1 or self.block_size < 1:
            raise ValueError("benchmark dimensions must be positive and rows must be at least two")
        if not math.isfinite(self.p95_seconds) or self.p95_seconds < 0:
            raise ValueError("p95_seconds must be finite and non-negative")
        if not math.isfinite(self.overhead_seconds) or self.overhead_seconds < 0:
            raise ValueError("overhead_seconds must be finite and non-negative")


@dataclass(frozen=True)
class RuntimeEstimate:
    """A deterministic, conservative complete-work estimate."""

    seconds: float
    pair_seconds: float
    overhead_seconds: float


@dataclass(frozen=True)
class RuntimeModel:
    """Scale the slowest recorded normalized sample with criterion count.

    This simple model uses the maximum observed pair-cost coefficient.  It never
    averages away a slow measurement, so a later slow sample only makes estimates
    more conservative.
    """

    samples: tuple[BenchmarkSample, ...]
    safety_factor: float = 1.25

    def __post_init__(self) -> None:
        if not self.samples:
            raise ValueError("runtime model requires at least one benchmark sample")
        if not math.isfinite(self.safety_factor) or self.safety_factor < 1.0:
            raise ValueError("safety_factor must be finite and at least one")

    def estimate(self, rows: int, criteria: int, block_size: int) -> RuntimeEstimate:
        if rows < 2 or criteria < 1 or block_size < 1:
            raise ValueError("rows, criteria, and block_size must be positive")
        coefficients = [
            max(0.0, sample.p95_seconds - sample.overhead_seconds)
            / (sample.rows * sample.rows * sample.criteria)
            for sample in self.samples
        ]
        pair_seconds = max(coefficients) * rows * rows * criteria * self.safety_factor
        # Preserve the highest observed complete-work fixed overhead.
        overhead = max(sample.overhead_seconds for sample in self.samples) * self.safety_factor
        return RuntimeEstimate(pair_seconds + overhead, pair_seconds, overhead)


def require_feasible(model: RuntimeModel, rows: int, criteria: int, block_size: int,
                     limit_seconds: float = MAX_ESTIMATED_SECONDS) -> RuntimeEstimate:
    """Reject an estimate above the approved interactive 300-second limit."""
    if not math.isfinite(limit_seconds) or limit_seconds <= 0:
        raise ValueError("limit_seconds must be finite and positive")
    estimate = model.estimate(rows, criteria, block_size)
    if estimate.seconds > limit_seconds:
        raise FeasibilityError(
            f"estimated p95 runtime {estimate.seconds:.3f}s exceeds {limit_seconds:.0f}s limit"
        )
    return estimate


def deadline_after(timeout_seconds: float = HARD_TIMEOUT_SECONDS) -> float:
    """Return a monotonic deadline for complete-result computation."""
    if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be finite and positive")
    return time.monotonic() + timeout_seconds


def require_before_deadline(deadline: float | None) -> None:
    """Prevent further work or result creation after the approved hard timeout."""
    if deadline is not None and time.monotonic() >= deadline:
        raise ComputeTimeoutError("computation exceeded the 330-second hard timeout")


def estimated_block_bytes(block_size: int, criteria: int) -> int:
    """Return a conservative temporary-memory estimate for one square block."""
    if block_size < 1 or criteria < 1:
        raise ValueError("block_size and criteria must be positive")
    return block_size * block_size * criteria * _TEMPORARY_BYTES_PER_CELL_PER_CRITERION


@dataclass(frozen=True)
class BenchmarkRecord:
    """One requested benchmark point, measured or safely rejected."""

    rows: int
    criteria: int
    block_size: int
    status: str
    samples_seconds: tuple[float, ...] = ()
    reason: str | None = None


def bounded_benchmark(
    runner: Callable[[int, int, int], None], *,
    rows: Sequence[int] = (100, 500, 1000, 5000, 10000, 15000),
    criteria: Sequence[int] = (4, 8),
    block_sizes: Sequence[int] = (1000, 5000, 10000),
    repeats: int = 3,
    max_block_bytes: int = 256 * 1024 * 1024,
    max_measured_rows: int = 1000,
) -> tuple[BenchmarkRecord, ...]:
    """Run bounded benchmark points and explicitly reject unsafe or oversized points.

    The caller supplies a complete-work runner, including parsing, validation,
    ranking, and serialization.  The function records every approved matrix point;
    it does not silently substitute a smaller computation.
    """
    if repeats < 1 or max_block_bytes < 1 or max_measured_rows < 2:
        raise ValueError("benchmark bounds must be positive")
    records: list[BenchmarkRecord] = []
    for row_count in rows:
        for criterion_count in criteria:
            for block_size in block_sizes:
                bytes_required = estimated_block_bytes(min(row_count, block_size), criterion_count)
                if row_count > max_measured_rows:
                    records.append(BenchmarkRecord(row_count, criterion_count, block_size, "rejected", reason="measured-row bound"))
                elif bytes_required > max_block_bytes:
                    records.append(BenchmarkRecord(row_count, criterion_count, block_size, "rejected", reason="temporary memory bound"))
                else:
                    timings = []
                    for _ in range(repeats):
                        started = time.perf_counter()
                        runner(row_count, criterion_count, block_size)
                        timings.append(time.perf_counter() - started)
                    records.append(BenchmarkRecord(row_count, criterion_count, block_size, "measured", tuple(timings)))
    return tuple(records)


def model_from_records(records: Iterable[BenchmarkRecord], safety_factor: float = 1.25) -> RuntimeModel:
    """Build a model from measured complete-work benchmark records only."""
    samples = tuple(
        BenchmarkSample(record.rows, record.criteria, record.block_size, p95_seconds(record.samples_seconds))
        for record in records if record.status == "measured"
    )
    return RuntimeModel(samples, safety_factor=safety_factor)


def p95_seconds(samples: Iterable[float]) -> float:
    """Return the nearest-rank p95, without interpolation optimism."""
    values = sorted(float(value) for value in samples)
    if not values or any(not math.isfinite(value) or value < 0 for value in values):
        raise ValueError("samples must contain finite non-negative values")
    return values[math.ceil(0.95 * len(values)) - 1]
