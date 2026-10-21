"""Canonical, byte-stable result serialization for validated ELECTRE III results.

The functions here use explicit UTF-8, LF-only CSV, canonical JSON, and little-endian
float64 NPY encodings.  They are pure: callers own storage, downloads, and caching.
"""
from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from hashlib import sha256
import io
import json
from typing import Any, Mapping, Sequence

import numpy as np

SERIALIZER_VERSION = "1"
MAX_ARTIFACT_BYTES = 16 * 1024 * 1024


@dataclass(frozen=True)
class CriterionMetadata:
    """Immutable validated criterion metadata in user-supplied order."""

    name: str
    weight: float
    q: float
    p: float
    v: float
    maximize: bool


@dataclass(frozen=True)
class ComputeConfiguration:
    """Immutable compute configuration captured with a result."""

    block_size: int
    use_numba: bool
    seed: int | None


@dataclass(frozen=True)
class RankingResult:
    """Immutable result model with read-only, C-contiguous numeric vectors."""

    ranking: np.ndarray
    net_flow: np.ndarray
    identifiers: tuple[str, ...]
    criteria: tuple[CriterionMetadata, ...]
    configuration: ComputeConfiguration

    def __post_init__(self) -> None:
        ranking = _readonly_vector(self.ranking, np.dtype("<i8"), "ranking")
        scores = _readonly_vector(self.net_flow, np.dtype("<f8"), "net_flow")
        if len(ranking) != len(scores):
            raise ValueError("ranking and net_flow must have equal lengths")
        if len(self.identifiers) != len(ranking):
            raise ValueError("identifiers must match ranking length")
        if any(not isinstance(identifier, str) for identifier in self.identifiers):
            raise ValueError("identifiers must be strings")
        if set(ranking.tolist()) != set(range(len(ranking))):
            raise ValueError("ranking must be a permutation of row indices")
        if not np.isfinite(scores).all():
            raise ValueError("net_flow must contain finite scores")
        object.__setattr__(self, "ranking", ranking)
        object.__setattr__(self, "net_flow", scores)
        object.__setattr__(self, "identifiers", tuple(self.identifiers))
        object.__setattr__(self, "criteria", tuple(self.criteria))


def _readonly_vector(values: Any, dtype: np.dtype[Any], field: str) -> np.ndarray:
    array = np.asarray(values, dtype=dtype)
    if array.ndim != 1:
        raise ValueError(f"{field} must be a 1D array")
    # Copy prevents callers from mutating the model through an input-array alias.
    result = np.array(array, dtype=dtype, order="C", copy=True)
    result.flags.writeable = False
    return result


def _canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":"), sort_keys=True) + "\n").encode("utf-8")


def _result_metadata(result: RankingResult) -> dict[str, Any]:
    return {
        "criteria": [asdict(criterion) for criterion in result.criteria],
        # Block size controls execution only. Omit it so equivalent computations
        # serialize byte-identically across approved block sizes.
        "configuration": {
            "seed": result.configuration.seed,
            "use_numba": result.configuration.use_numba,
        },
        "identifiers": list(result.identifiers),
        "serializer_version": SERIALIZER_VERSION,
    }


def serialize_ranking_json(result: RankingResult) -> bytes:
    """Serialize ranking indices as canonical UTF-8 JSON with one trailing LF."""
    return _canonical_json({"ranking": result.ranking.tolist(), **_result_metadata(result)})


def serialize_scores_json(result: RankingResult) -> bytes:
    """Serialize raw net-flow scores as canonical UTF-8 JSON with one trailing LF."""
    return _canonical_json({"net_flow": result.net_flow.tolist(), **_result_metadata(result)})


def serialize_result_json(result: RankingResult) -> bytes:
    """Serialize complete ranking and scores in one canonical JSON artifact."""
    return _canonical_json({"net_flow": result.net_flow.tolist(), "ranking": result.ranking.tolist(), **_result_metadata(result)})


def serialize_result_csv(result: RankingResult) -> bytes:
    """Serialize result rows with deterministic column order and LF line endings."""
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(("rank", "index", "identifier", "net_flow"))
    for position, index in enumerate(result.ranking, start=1):
        row = int(index)
        writer.writerow((position, row, result.identifiers[row], float(result.net_flow[row]).hex()))
    return stream.getvalue().encode("utf-8")


def serialize_scores_npy(result: RankingResult) -> bytes:
    """Serialize scores as a deterministic 1D little-endian float64 NPY artifact."""
    stream = io.BytesIO()
    np.lib.format.write_array(stream, np.asarray(result.net_flow, dtype="<f8"), version=(1, 0), allow_pickle=False)
    return stream.getvalue()


def split_artifact(name: str, payload: bytes, part_size: int = MAX_ARTIFACT_BYTES) -> tuple[dict[str, Any], tuple[bytes, ...]]:
    """Split an artifact into ordered checksum-verified byte parts.

    The caller stores returned parts in list order. The manifest holds no paths, so it
    cannot direct a consumer outside its chosen storage namespace.
    """
    if not isinstance(name, str) or not name or "/" in name or "\\" in name:
        raise ValueError("artifact name must be a non-empty basename")
    if not isinstance(payload, bytes):
        raise ValueError("payload must be bytes")
    if isinstance(part_size, bool) or not isinstance(part_size, int) or not 1 <= part_size <= MAX_ARTIFACT_BYTES:
        raise ValueError(f"part_size must be an integer from 1 through {MAX_ARTIFACT_BYTES}")
    parts = tuple(payload[offset:offset + part_size] for offset in range(0, len(payload), part_size)) or (b"",)
    manifest = {
        "artifact": name,
        "byte_length": len(payload),
        "parts": [
            {"index": index, "byte_length": len(part), "sha256": sha256(part).hexdigest()}
            for index, part in enumerate(parts)
        ],
        "serializer_version": SERIALIZER_VERSION,
        "sha256": sha256(payload).hexdigest(),
    }
    return manifest, parts


def serialize_manifest(manifest: Mapping[str, Any]) -> bytes:
    """Serialize a split-artifact manifest as canonical UTF-8 JSON."""
    return _canonical_json(dict(manifest))


def reassemble_artifact(manifest: Mapping[str, Any], parts: Sequence[bytes]) -> bytes:
    """Validate and reassemble exactly the ordered parts described by a manifest."""
    if not isinstance(manifest, Mapping) or manifest.get("serializer_version") != SERIALIZER_VERSION:
        raise ValueError("manifest serializer_version is unsupported")
    entries = manifest.get("parts")
    if not isinstance(entries, list) or len(entries) != len(parts) or not entries:
        raise ValueError("manifest parts do not match supplied parts")
    validated: list[bytes] = []
    for index, (entry, part) in enumerate(zip(entries, parts)):
        if not isinstance(entry, Mapping) or entry.get("index") != index or not isinstance(part, bytes):
            raise ValueError("manifest part order or type is invalid")
        if entry.get("byte_length") != len(part) or entry.get("sha256") != sha256(part).hexdigest():
            raise ValueError(f"manifest checksum mismatch for part {index}")
        validated.append(part)
    payload = b"".join(validated)
    if manifest.get("byte_length") != len(payload) or manifest.get("sha256") != sha256(payload).hexdigest():
        raise ValueError("manifest payload checksum mismatch")
    return payload
