# W4 static asset packaging

## Before and after

Before W4, `scripts/build_website.py` copied `examples/assets_priority` directly. The copy destination was deletion-safe, but no declared source-of-truth listed the approved published files. The Examples page linked to four files while the static child directory did not have a packaging contract.

After W4, [static-asset-manifest.json](../static-asset-manifest.json) declares the sole approved static example bundle. The build validates that the source directory contains exactly the manifest files, then atomically stages and replaces only its owned destination. The existing Examples child links resolve to manifest-owned published targets.

## Source ownership

- `examples/assets_priority/` owns committed source assets.
- `docs/static-asset-manifest.json` owns the approved source-to-target publication mapping.
- `scripts/build_website.py` owns validation and generated synchronization.
- `website/examples/assets_priority/` is generated output. Do not edit it directly.
- `website/examples/index.html` owns user-facing child links.

## Evidence

| Check | Result |
| --- | --- |
| Manifest source and target bytes | Positive: all seven declared files match. |
| Examples landing links | Positive: README, criteria JSON, headered CSV, and ranking resolve. |
| Static nested routes | Positive: root, tutorial, reference, examples, assets, and fragments pass. |
| Stale output | Positive: staged synchronization deletes stale files. |
| Missing source | Negative: raises `FileNotFoundError` and preserves existing output. |
| Extra source asset | Negative: manifest mismatch raises `ValueError`. |
| Invalid paths | Negative: traversal, nested separators, and blank paths raise `ValueError`. |

Executed commands and results:

```text
python -m pytest tests\\test_w4_static_asset_packaging.py tests\\test_w3_link_contract.py tests\\test_w2_static_flask_links.py -q
57 passed in 24.97s

python scripts\\build_website.py && git diff --check && git diff -- website\\examples
exit 0

python scripts\\preflight_checks.py
All checks passed!
```

## Tutorial: publish an approved static asset bundle

1. Add a committed, flat source directory below `examples/`.
2. Add one manifest entry with a unique `id`, flat `source` and `target`, and every approved filename.
3. Link only published `/examples/<target>/<file>` paths from static HTML.
4. Run the focused packaging/link tests and `python scripts/build_website.py`.
5. Do not manually edit `website/examples/<target>/`; the next build replaces it.

## Limitations

Browser checks remain deferred and non-blocking. The manifest deliberately supports flat files only; recursive packages need a reviewed manifest schema change. This evidence does not certify remote hosting behavior or upstream publication.
