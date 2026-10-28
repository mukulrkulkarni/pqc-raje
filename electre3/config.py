"""Configuration dataclasses for ELECTRE III."""
from dataclasses import dataclass
from typing import Optional

from .config_validation import validate_block_size, validate_criterion


@dataclass
class CriterionConfig:
    name: str
    weight: float
    q: float
    p: float
    v: float
    maximize: bool = True

    def __post_init__(self) -> None:
        validate_criterion(self.q, self.p, self.v, self.weight)


@dataclass
class ComputeConfig:
    block_size: int = 1000
    use_numba: bool = True
    seed: Optional[int] = None

    def __post_init__(self) -> None:
        validate_block_size(self.block_size)


def normalize_weights(criteria: list[CriterionConfig]) -> list[float]:
    """Return weights normalized to one while preserving criterion order."""
    total = sum(criterion.weight for criterion in criteria)
    if total <= 0:
        raise ValueError(f"Total weight must be > 0, got {total}")
    return [criterion.weight / total for criterion in criteria]
