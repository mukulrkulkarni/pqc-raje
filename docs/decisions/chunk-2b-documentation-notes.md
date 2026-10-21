# Chunk 2B Documentation Notes

**Purpose:** Record the verified serialization foundation. This note does not claim cache, downloads, or runtime controls.

## Current behavior

Chunk 2B adds immutable `RankingResult` in `electre3/serialization.py`. It contains ranking indices, raw net-flow scores, identifiers, criteria metadata, and compute configuration. `electre3.shared.compute_validated_ranking` now returns this model through its retained `ComputeResult` alias. Existing CLI compatibility remains: `run_ranking` still returns only ranking indices.

Canonical serializers use UTF-8, deterministic JSON key ordering, LF endings, and explicit little-endian float64 NPY data:

- `serialize_ranking_json`, `serialize_scores_json`, and `serialize_result_json`.
- `serialize_result_csv` with rank, index, identifier, and hexadecimal raw score.
- `serialize_scores_npy` for 1D `<f8` score vectors.
- `split_artifact`, `serialize_manifest`, and `reassemble_artifact`.

Split manifests contain serializer version, total byte length, total SHA-256, and ordered part records. Each part record has index, byte length, and SHA-256. Reassembly validates all fields before returning bytes. Artifact names must be basenames; serializers do not write files or resolve paths.

## Source evidence

- `electre3/serialization.py`
- `electre3/shared.py`
- `tests/test_serialization.py`
- `tests/test_shared_contract.py`
- `tests/test_cli_run.py`

## Verified commands

```text
python -m pytest tests/test_serialization.py tests/test_shared_contract.py tests/test_cli_run.py -q
python -m compileall electre3 app
```

Run these commands at the Chunk 2B commit to reproduce current evidence. The serialization suite includes repeated byte identity, malformed model input, Unicode, LF, CSV quoting, NumPy dtype/shape, split/reassembly, checksum tampering, ordering, unsafe names, and invalid part sizes.

## Current versus target

Current: pure serialization functions and in-memory split/reassembly validation.

Not implemented: cache storage, 16 MiB automatic splitting policy at a route boundary, downloads, download rate limits, session cache metadata, TTL, 32 MiB cache enforcement, feasibility benchmark, or timeout enforcement. No routes changed in this chunk; Chunk 2A `/app` workflow and compatibility routes stay intact.

## Debugging and tutorial notes

Use `RankingResult` with a permutation ranking, one finite raw score per row, one string identifier per row, and immutable metadata tuples. A serializer `ValueError` identifies malformed model data, invalid manifest version, checksum failure, ordering mismatch, unsafe artifact name, or invalid part size. To diagnose a reassembly failure, check the part sequence, each byte length, each SHA-256, then the total SHA-256. Keep result bytes opaque; do not decode NPY as text.
