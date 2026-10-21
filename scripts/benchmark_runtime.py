"""Run the bounded Chunk 2C complete-work benchmark and write JSON evidence."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from electre3.runtime import bounded_benchmark, estimated_block_bytes, model_from_records
from electre3.serialization import serialize_result_json
from electre3.shared import compute_validated_ranking

ROWS = (100, 500, 1000, 5000, 10000, 15000)
CRITERIA_COUNTS = (4, 8)
BLOCK_SIZES = (1000, 5000, 10000)


def criteria_for(count: int) -> list[dict[str, object]]:
    return [
        {"name": f"c{index}", "weight": 1.0 / count, "q": 0.0, "p": 0.2, "v": 0.8,
         "maximize": index % 2 == 0}
        for index in range(count)
    ]


def runner(rows: int, criteria: int, block_size: int) -> None:
    matrix = np.random.default_rng(rows * 100 + criteria).random((rows, criteria))
    result = compute_validated_ranking(matrix, criteria_for(criteria), block_size=block_size)
    serialize_result_json(result)


def main() -> None:
    records = bounded_benchmark(runner, rows=ROWS, criteria=CRITERIA_COUNTS,
                                block_sizes=BLOCK_SIZES, repeats=3,
                                max_measured_rows=1000)
    model = model_from_records(records)
    payload = {
        "method": "complete shared adapter plus canonical JSON serialization",
        "requested_rows": ROWS,
        "criteria_counts": CRITERIA_COUNTS,
        "block_sizes": BLOCK_SIZES,
        "repeats": 3,
        "max_measured_rows": 1000,
        "memory_formula": "min(N, block_size)^2 * C * 48 bytes",
        "records": [record.__dict__ for record in records],
        "model": {"safety_factor": model.safety_factor,
                  "estimate_100000_rows_8_criteria_seconds": model.estimate(100000, 8, 1000).seconds},
    }
    output = Path("out/chunk-2c-benchmark.json")
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
