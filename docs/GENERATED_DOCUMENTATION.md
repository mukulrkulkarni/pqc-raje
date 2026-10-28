# Generated documentation ownership

`docs/modules/*_tutorial_side_by_side.html` is the source for each generated tutorial at `website/modules/<module>/tutorial/index.html`.

`scripts/build_website.py` owns the transformation and writes the tracked website output. Run `python scripts/build_website.py` after changing a source tutorial, then run `python scripts/preflight_checks.py`. The preflight check fails when a declared target is missing or older than its source. Do not manually repair generated tutorial output; correct its source and rebuild.

`website/index.html`, `website/app/index.html`, and `website/modules/index.html` are tracked website inputs that the builder normalizes. `website/site-config.json` owns their configured domain values and navigation metadata.

The repository preserves generated output for local, offline review. A release archive must include only the approved user-facing generated output, not decision records or checkpoints. See `docs/VERSIONING_AND_ROLLBACK.md` for release-resource verification.
