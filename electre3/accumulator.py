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
        B1, B2 = S_block.shape
        self.outflow[row_start:row_start + B1] += S_block.sum(axis=1)
        self.inflow[col_start:col_start + B2] += S_block.sum(axis=0)
        self.blocks_done += 1

    def net_flow(self) -> np.ndarray:
        return self.outflow - self.inflow

    def normalize(self) -> np.ndarray:
        flow = self.net_flow()
        min_val, max_val = flow.min(), flow.max()
        if max_val == min_val:
            return np.ones_like(flow) * 0.5
        return (flow - min_val) / (max_val - min_val)
