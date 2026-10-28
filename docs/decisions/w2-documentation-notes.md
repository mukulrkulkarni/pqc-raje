# W2 recovery documentation notes

## Scope and repaired routes

W2 repairs only companion-site navigation and generated-example synchronization. It does not modify ranking algorithms, release tags, or remote state.

### Exact path changes

| Surface | Before | After |
|---|---|---|
| Flask landing Examples link | `docs/GETTING_STARTED.html`: `/examples/index.html` on Flask port | `docs/GETTING_STARTED.html`: `__COMPANION_WEBSITE_URL__/examples/index.html`, rendered by `app/routes/docs.py` from validated `COMPANION_WEBSITE_URL` |
| Flask workflow Examples link | `app/templates/app_input.html`: `http://127.0.0.1:8000/examples/index.html` | `{{ config['COMPANION_WEBSITE_URL'] }}/examples/index.html` |
| Generated example synchronization | `scripts/build_website.py`: `shutil.copytree(..., dirs_exist_ok=True)` retained stale destination files | `synchronize_generated_tree`: stage copy, replace destination, remove stale output, restore prior output when replacement fails |

`app/__init__.py` accepts `COMPANION_WEBSITE_URL`, defaulting to `http://127.0.0.1:8000`. It only accepts an absolute HTTP(S) origin without credentials, paths, query, or fragment. Deployments can set this configuration to their working companion website origin. The served-link tests use `http://127.0.0.1:43127`; no test contract hard-codes port 8000.

`examples/assets_priority/` remains authoritative. The build output is `website/examples/assets_priority/`. The build now removes output files deleted from the authoritative source and does not delete existing output when the source directory is absent.

## Test evidence

- Positive, negative, and edge regression tests: `python -m pytest -q tests/test_w2_recovery.py tests/test_w2_static_flask_links.py tests/test_active_template_ui.py` — **49 passed in 25.40s**.
  - Positive: configured Flask Examples link and current generated file.
  - Negative: unsafe companion origins and absent source directory.
  - Edge: empty source removes stale generated output.
- Full suite: `python -m pytest -q` — **1099 passed in 55.41s**.
- Website build: `python scripts/build_website.py` — **passed**.
- Compilation: `python -m compileall -q electre3 app scripts tests` — **passed**.
- Preflight: `python scripts/preflight_checks.py` — **all four checks passed**.
- Whitespace: `git diff --check` — **passed**; Git emitted only LF-to-CRLF working-copy warnings.

## Reviews

### Engineering review — approved

The origin validator prevents credentials, path injection, query, and fragment values. The landing renderer replaces one controlled placeholder using application configuration. The generated-tree synchronization validates and stages the source before moving the current destination, removes stale files after a successful replacement, and restores the prior destination when replacement raises. Regression tests cover success, missing source preservation, and empty-source deletion.

### UI/UX review — approved for static/documentation scope

The Examples label remains explicit. Flask and workflow pages point to the configured companion site, while static pages keep local root-relative Examples navigation. Existing semantic navigation and focus styling remain unchanged. No JavaScript is introduced.

## Limitations

Browser rendering, keyboard operation, assistive technology, zoom, reflow, offline, and load checks remain deferred and non-blocking. The default companion origin remains port 8000 for local launcher compatibility; deployments must set `COMPANION_WEBSITE_URL` to their actual companion-site origin. Filesystem replacement rollback is tested for missing sources; a process crash between destination move and staged move remains outside this bounded recovery.
