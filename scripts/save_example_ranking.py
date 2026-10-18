"""Save ranking outputs for the assets_priority example.

Writes:
- examples/assets_priority/ranking.npy (numpy array of alt indices)
- examples/assets_priority/ranking.txt (human-readable with asset names)

This script is deterministic.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

# Ensure repo root is importable when launched as a script.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from electre3.data import load_matrix
from electre3.cli_run import run_ranking


def main() -> int:
    base = Path("examples/assets_priority")
    matrix = load_matrix(base / "matrix_numeric_only.csv")
    criteria = json.loads((base / "criteria.json").read_text(encoding="utf-8"))
    names = (base / "asset_names.txt").read_text(encoding="utf-8").splitlines()

    ranking = run_ranking(matrix, criteria, block_size=1000, quiet=True)

    np.save(base / "ranking.npy", ranking)

    lines = ["Ranking (best first):"]
    for i, idx in enumerate(ranking.tolist(), start=1):
        idx = int(idx)
        name = names[idx] if 0 <= idx < len(names) else f"Alt {idx}"
        lines.append(f"{i}. {name} (Alt {idx})")
    (base / "ranking.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
