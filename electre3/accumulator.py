"""Net flow accumulator for O(N) storage."""
import numpy as np
from dataclasses import dataclass, field


@dataclass
class NetFlowAccumulator:
    n_alternatives: int
    outflow: np.ndarray = field(init=False)
    inflow: np.ndarray = field(init=False)
    blocks_done: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        self.outflow = np.zeros(self.n_alternatives, dtype=np.float64)
        self.inflow = np.zeros(self.n_alternatives, dtype=np.float64)

    def update(self, S_block: np.ndarray, row_start: int, col_start: int) -> None:
        """Add cells in global row-major order for block-size-independent sums.

        Vector reductions change floating-point grouping when blocks change. Scalar
        additions retain each global row's column order and each column's row order,
        so canonical result bytes remain invariant across permitted block sizes.
        """
        rows, columns = S_block.shape
        if row_start >= 0 and row_start + rows > self.n_alternatives:
            raise ValueError("row block exceeds accumulator bounds")
        if col_start >= 0 and col_start + columns > self.n_alternatives:
            raise ValueError("column block exceeds accumulator bounds")
        for local_row in range(rows):
            global_row = row_start + local_row
            row_in_bounds = 0 <= global_row < self.n_alternatives
            for local_column in range(columns):
                global_column = col_start + local_column
                column_in_bounds = 0 <= global_column < self.n_alternatives
                value = S_block[local_row, local_column]
                if row_in_bounds:
                    self.outflow[global_row] += value
                if column_in_bounds:
                    self.inflow[global_column] += value
        self.blocks_done += 1

    def net_flow(self) -> np.ndarray:
        return self.outflow - self.inflow

    def normalize(self) -> np.ndarray:
        flow = self.net_flow()
        min_val, max_val = flow.min(), flow.max()
        if max_val == min_val:
            return np.ones_like(flow) * 0.5
        return (flow - min_val) / (max_val - min_val)
