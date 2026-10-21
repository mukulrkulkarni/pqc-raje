"""Configuration dataclasses for ELECTRE III."""
from dataclasses import dataclass
from typing import Optional
import math


def _check_finite(val: float, name: str) -> None:
    if math.isnan(val) or math.isinf(val):
        raise ValueError(f"{name} must be finite, got {val}")


@dataclass
class CriterionConfig:
    name: str
    weight: float
    q: float
    p: float
    v: float
    maximize: bool = True

    def __post_init__(self) -> None:
        _check_finite(self.q, "q")
        _check_finite(self.p, "p")
        _check_finite(self.v, "v")
        _check_finite(self.weight, "weight")
        if self.q < 0:
            raise ValueError(f"q must be >= 0, got {self.q}")
        if self.p < self.q:
            raise ValueError(f"p must be >= q, got p={self.p}, q={self.q}")
        if self.v < self.p:
            raise ValueError(f"v must be >= p, got v={self.v}, p={self.p}")
        if self.weight <= 0:
            raise ValueError(f"weight must be > 0, got {self.weight}")


@dataclass
class ComputeConfig:
    block_size: int = 1000
    use_numba: bool = True
    seed: Optional[int] = None

    def __post_init__(self) -> None:
        if isinstance(self.block_size, bool) or not isinstance(self.block_size, int):
            raise ValueError("block_size must be an integer")
        if self.block_size < 1:
            raise ValueError(f"block_size must be >= 1, got {self.block_size}")
        if self.block_size > 10_000:
            raise ValueError(f"block_size must be <= 10000, got {self.block_size}")


def normalize_weights(criteria: list[CriterionConfig]) -> list[float]:
    total = sum(c.weight for c in criteria)
    if total <= 0:
        raise ValueError(f"Total weight must be > 0, got {total}")
    return [c.weight / total for c in criteria]
