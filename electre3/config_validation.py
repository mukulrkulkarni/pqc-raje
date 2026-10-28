"""Validation helpers for ELECTRE III configuration dataclasses."""
import math


def check_finite(value: float, name: str) -> None:
    """Reject non-finite configuration values with the established message."""
    if math.isnan(value) or math.isinf(value):
        raise ValueError(f"{name} must be finite, got {value}")


def validate_criterion(q: float, p: float, v: float, weight: float) -> None:
    """Validate threshold ordering and a positive criterion weight."""
    for value, name in ((q, "q"), (p, "p"), (v, "v"), (weight, "weight")):
        check_finite(value, name)
    if q < 0:
        raise ValueError(f"q must be >= 0, got {q}")
    if p < q:
        raise ValueError(f"p must be >= q, got p={p}, q={q}")
    if v < p:
        raise ValueError(f"v must be >= p, got v={v}, p={p}")
    if weight <= 0:
        raise ValueError(f"weight must be > 0, got {weight}")


def validate_block_size(block_size: int) -> None:
    """Validate the supported compute block-size range."""
    if isinstance(block_size, bool) or not isinstance(block_size, int):
        raise ValueError("block_size must be an integer")
    if block_size < 1:
        raise ValueError(f"block_size must be >= 1, got {block_size}")
    if block_size > 10_000:
        raise ValueError(f"block_size must be <= 10000, got {block_size}")
