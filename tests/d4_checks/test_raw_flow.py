"""Independently recompute D4 tie flows from raw fixture inputs."""
import csv
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]

def raw_flows(name):
    folder = ROOT / "examples" / "d4_phase2" / name
    criteria = json.loads((folder / "criteria_balanced.json").read_text(encoding="utf-8"))
    rows = list(csv.reader((folder / "matrix_headered.csv").open(encoding="utf-8", newline="")))[1:]
    scores = np.array([[float(value) for value in row[1:]] for row in rows])
    q, p, v = (np.array([item[key] for item in criteria]) for key in ("q", "p", "v"))
    weights = np.array([item["weight"] for item in criteria])
    directions = np.array([1 if item["maximize"] else -1 for item in criteria])
    diff = (scores[:, None, :] - scores[None, :, :]) * directions
    concordance = np.where(diff >= -q, 1.0, np.where(diff <= -p, 0.0, (diff + p) / (p - q)))
    discordance = np.where(diff <= -v, 1.0, np.where(diff >= -p, 0.0, (-diff - p) / (v - p)))
    base = np.einsum("ijk,k->ij", concordance, weights)
    credibility = base.copy()
    for index in range(len(criteria)):
        values = discordance[:, :, index]
        credibility[values >= 1.0] = 0.0
        mask = (values > base) & (values < 1.0)
        credibility[mask] *= (1.0 - values[mask]) / (1.0 - base[mask])
    np.fill_diagonal(credibility, 0.0)
    return credibility.sum(axis=1) - credibility.sum(axis=0)

def test_raw_fixture_recomputation_distinguishes_exact_and_near_ties():
    exact, near = raw_flows("exact-tie"), raw_flows("near-tie")
    assert exact[0] == exact[1]
    assert near[0] != near[1]
    assert exact[0].hex() == "0x1.4aac3cd964020p-2"
    assert near[1].hex() == "0x1.4aac3cd964028p-2"
