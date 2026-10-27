# Debugging playbook (deterministic ELECTRE III blockwise ranking)

## Golden rules

- Reproduce with `pytest tests/` first.
- Do not change ranking semantics:
  - ranking uses **raw net flow (descending)**.
- Treat every change as a contract change unless proven otherwise.

## Common failures and fast diagnosis

### 1) Supported app computation needs preview and confirmation (HTTP 400)

Symptoms:
- `POST /app/compute` returns 400 when no successful preview exists or `confirm_compute` is absent.

Meaning:
- The supported server-rendered `/app/` workflow requires criteria, a successful preview, and explicit confirmation before computation.

Checks:
- Return to `/app/`, correct the relevant form, review the preview, then confirm computation.
- Inspect the response message; do not infer `/app/` guidance from legacy JSON endpoints.

Legacy compatibility only:
- `/preview/<upload_id>`, `/preview/<upload_id>/confirm`, `/preview/<upload_id>/cancel`, `/compute/start`, and `/compute/status/<job_id>` are legacy compatibility routes, not the primary browser workflow.
- `app/templates/preview.html` and `app/templates/config.html` support legacy compatibility only. Do not direct new users to them.
- In that legacy JSON flow, an unconfirmed upload at `POST /compute/start` returns HTTP 403. Its client must preserve the session cookie and call `POST /preview/<upload_id>/confirm`.

### 2) Module docs return 404

Symptoms:
- `/docs/modules/<name>` or `/docs/modules/<name>/tutorial` returns 404.

Meaning:
- Either `<name>` is not allow-listed or the expected file does not exist.

Checks:
- `app/routes/docs.py::ALLOWED_MODULE_DOCS` contains `<name>`.
- `docs/modules/<name>.html` exists.
- `docs/modules/<name>_tutorial_side_by_side.html` exists.

### 3) Path traversal / prefix collision regression

Symptoms:
- Allow-list tests fail.
- Security Lead gate blocks.

Checks:
- Route code must:
  - validate name via strict regex (no dots, slashes, uppercase)
  - require membership in allow-list
  - contain resolved paths under the allowed directory

### 4) Net flow values look plausible but ranking is wrong

Likely causes:
- Block-to-global indices swapped (`row_start` vs `col_start`).
- Diagonal not cleared in diagonal blocks.
- Block tiling overlaps or has gaps.

Checks:
- Run deep tests:
  - `tests/test_block_deep.py` (directionality oracle, diagonal clearing)
  - `tests/test_accumulator_deep.py` (index mapping oracle, bounds regressions)

### 5) Validator errors at construction time

Symptoms:
- A test expects `validate.py` to raise, but construction fails earlier.

Meaning:
- Some checks are enforced in `CriterionConfig` (`electre3/config.py`).

Checks:
- Use a dummy/stand-in criterion object when you want to unit-test the validator function in isolation.

## Logging and instrumentation (local)

- Prefer adding assertions and deterministic tests over ad-hoc print debugging.
- When printing intermediate arrays, always print:
  - shapes
  - dtype
  - `np.isfinite()` summary
  - min/max

## Local launcher

Run both local services from the repository root with one command:

```bash
python scripts/dev_local.py
```

The launcher prints `Website: http://127.0.0.1:8000/` and `App: http://127.0.0.1:5000/app/`. Press `Ctrl+C` once to stop both. Set distinct ports when needed:

```bash
WEBSITE_PORT=8100 APP_PORT=5100 python scripts/dev_local.py
```

On Windows Command Prompt, use `set WEBSITE_PORT=8100&& set APP_PORT=5100&& python scripts\dev_local.py`. A port conflict or invalid port exits with code `2` before startup URLs print. The launcher binds only `127.0.0.1`; it is not a network deployment.

## Repro commands

- Main suite:
  - `python -m pytest -q tests/`
- Launcher lifecycle suite:
  - `python -m pytest -q tests/test_dev_local.py`

## CSV input: common failure and fix

If your CSV has headers or an ID column, `np.loadtxt` will fail.

Use the converter:

```bash
python scripts/convert_matrix_csv.py in.csv out/matrix.npy --has-header --id-col id
python -m electre3.cli out/matrix.npy criteria.json -y
```
- Focused suites:
  - `python -m pytest -q tests/test_block_deep.py`
  - `python -m pytest -q tests/test_accumulator_deep.py`
  - `python -m pytest -q tests/test_module_docs.py::TestAccumulatorTutorialScaffold`

## Known harness caveat

- Running `pytest` at repo root may collect snapshot tests under `docs/design/*` and trigger duplicate-module-name collection errors.
- Use `pytest tests/` for the main deterministic suite.
