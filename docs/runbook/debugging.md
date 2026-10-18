# Debugging playbook (deterministic ELECTRE III blockwise ranking)

## Golden rules

- Reproduce with `pytest tests/` first.
- Do not change ranking semantics:
  - ranking uses **raw net flow (descending)**.
- Treat every change as a contract change unless proven otherwise.

## Common failures and fast diagnosis

### 1) “Upload not confirmed” (HTTP 403)

Symptoms:
- `POST /compute/start` returns 403.

Meaning:
- The UI requires a confirmation gate before computation.

Checks:
- Call `POST /preview/<upload_id>/confirm`.
- Ensure the client preserves the session cookie.

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

## Repro commands

- Main suite:
  - `python -m pytest -q tests/`

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
