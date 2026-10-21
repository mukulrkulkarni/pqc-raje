"""Byte-stability and malformed-input tests for result serialization."""
import json

import numpy as np
import pytest

from electre3.serialization import (
    ComputeConfiguration, CriterionMetadata, RankingResult, reassemble_artifact,
    serialize_manifest, serialize_result_csv, serialize_result_json,
    serialize_ranking_json, serialize_scores_json, serialize_scores_npy, split_artifact,
)


def result():
    return RankingResult(
        ranking=np.array([1, 0], dtype=np.int32),
        net_flow=np.array([0.0, -0.25], dtype=np.float32),
        identifiers=("Ångström", "東京,\"ID\""),
        criteria=(CriterionMetadata("quality", 1.0, 0.0, 0.1, 0.5, True),),
        configuration=ComputeConfiguration(block_size=1000, use_numba=True, seed=None),
    )


def test_serializers_are_byte_identical_on_repeated_calls():
    value = result()
    for serializer in (serialize_ranking_json, serialize_scores_json, serialize_result_json, serialize_result_csv, serialize_scores_npy):
        assert serializer(value) == serializer(value)


def test_json_is_utf8_canonical_and_lf_terminated():
    payload = serialize_result_json(result())
    assert payload.endswith(b"\n") and b"\r" not in payload
    decoded = json.loads(payload)
    assert decoded["identifiers"] == ["Ångström", '東京,"ID"']
    assert b"\xc3\x85" in payload


def test_csv_uses_lf_and_preserves_unicode_and_quotes():
    payload = serialize_result_csv(result())
    assert b"\r" not in payload
    assert '東京,""ID""'.encode() in payload
    assert payload.splitlines()[1].endswith(b"-0x1.0000000000000p-2")


def test_npy_has_little_endian_float64_vector():
    loaded = np.load(__import__("io").BytesIO(serialize_scores_npy(result())), allow_pickle=False)
    assert loaded.dtype == np.dtype("<f8")
    assert loaded.shape == (2,)
    np.testing.assert_array_equal(loaded, [0.0, -0.25])


@pytest.mark.parametrize("kwargs, message", [
    ({"ranking": [[0, 1]]}, "ranking must be a 1D"),
    ({"ranking": [0, 0]}, "permutation"),
    ({"net_flow": [float("nan"), 0]}, "finite"),
    ({"identifiers": ("only",)}, "identifiers must match"),
])
def test_result_rejects_malformed_vectors(kwargs, message):
    base = dict(ranking=[0, 1], net_flow=[0.1, 0.0], identifiers=("a", "b"), criteria=(), configuration=ComputeConfiguration(1, True, None))
    base.update(kwargs)
    with pytest.raises(ValueError, match=message):
        RankingResult(**base)


def test_split_manifest_reassembles_byte_identically_and_is_canonical():
    payload = serialize_result_csv(result())
    manifest, parts = split_artifact("result.csv", payload, part_size=7)
    assert reassemble_artifact(manifest, parts) == payload
    assert serialize_manifest(manifest) == serialize_manifest(manifest)
    assert [entry["index"] for entry in manifest["parts"]] == list(range(len(parts)))


def test_split_rejects_tampering_order_and_unsafe_names():
    manifest, parts = split_artifact("result.json", b"abcdefgh", part_size=3)
    with pytest.raises(ValueError, match="checksum mismatch"):
        reassemble_artifact(manifest, (parts[0], b"XXX", parts[2]))
    with pytest.raises(ValueError, match="order"):
        reassemble_artifact({**manifest, "parts": [manifest["parts"][1], manifest["parts"][0], manifest["parts"][2]]}, parts)
    with pytest.raises(ValueError, match="basename"):
        split_artifact("../result.json", b"x")


@pytest.mark.parametrize("part_size", [0, True, 16 * 1024 * 1024 + 1])
def test_split_rejects_invalid_part_size(part_size):
    with pytest.raises(ValueError, match="part_size"):
        split_artifact("result.json", b"x", part_size=part_size)
