"""Net flow accumulator for O(N) storage during block computation."""

import numpy as np
from dataclasses import dataclass, field


@dataclass
class NetFlowAccumulator:
    """Accumulates net flow scores with O(N) storage.

    Instead of storing the full N×N credibility matrix,
    we accumulate row sums (outflow) and column sums (inflow)
    as each block is computed.

    Net flow: φ(a) = Σ_b S(a,b) - Σ_b S(b,a)
    """

    n_alternatives: int
    outflow: np.ndarray = field(init=False)
    inflow: np.ndarray = field(init=False)
    blocks_done: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        """Initialize accumulator arrays."""
        self.outflow = np.zeros(self.n_alternatives, dtype=np.float64)
        self.inflow = np.zeros(self.n_alternatives, dtype=np.float64)

    def update(
        self,
        S_block: np.ndarray,
        row_start: int,
        col_start: int,
    ) -> None:
        """Update accumulators with a computed block.

        Args:
            S_block: Credibility block of shape (B1, B2).
            row_start: Starting row index in full matrix.
            col_start: Starting column index in full matrix.
        """
        B1, B2 = S_block.shape
        row_end = row_start + B1
        col_end = col_start + B2

        # Outflow: sum across columns (row sums)
        self.outflow[row_start:row_end] += S_block.sum(axis=1)

        # Inflow: sum across rows (column sums)
        self.inflow[col_start:col_end] += S_block.sum(axis=0)

        self.blocks_done += 1

    def net_flow(self) -> np.ndarray:
        """Compute net flow scores.

        Returns:
            Net flow φ(a) for each alternative.
        """
        return self.outflow - self.inflow

    def normalize(self) -> np.ndarray:
        """Compute normalized net flow in [0, 1].

        Returns:
            Normalized scores where 1 is best.
        """
        flow = self.net_flow()
        min_val, max_val = flow.min(), flow.max()
        if max_val == min_val:
            return np.ones_like(flow) * 0.5
        return (flow - min_val) / (max_val - min_val)
