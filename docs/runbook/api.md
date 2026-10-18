# API documentation (Flask UI/CLI surface)

## Purpose
This document describes the Flask HTTP surface used by the UI and tests.

## Security headers and CSP

- Implemented in `app/__init__.py` via `after_request`.
- Base headers applied to all routes:
  - `X-Content-Type-Options: nosniff`
  - `Referrer-Policy: no-referrer`
  - `Cross-Origin-Opener-Policy: same-origin`
  - `Cross-Origin-Resource-Policy: same-origin`
- Route-scoped CSP:
  - Docs routes (`/` and `/docs/*`) use `CSP_DOCS` (allows local scripts: `script-src 'self'`).
  - Other routes use `CSP_APP` (no `script-src`; scripts are effectively disallowed).

## Routes

### `GET /`

Serves the offline-first landing page.

- Handler: `app/routes/docs.py::landing`
- Response: `docs/GETTING_STARTED.html` (text/html)
- Errors:
  - 404 if the file is missing.

### `GET /app`

Serves a minimal HTML entry page.

- Handler: `app/routes/docs.py::app_ui`
- Response: inline HTML (text/html)

### `GET /docs/modules/<name>`

Serves a module documentation page.

- Handler: `app/routes/docs.py::module_doc`
- Preconditions (enforced):
  - `<name>` matches regex `^[a-z_]+$`.
  - `<name>` is in `ALLOWED_MODULE_DOCS`.
  - `docs/modules/<name>.html` exists.
- Response: text/html
- Errors:
  - 404 if name is invalid/not allow-listed or file does not exist.

### `GET /docs/modules/<name>/tutorial`

Serves a module side-by-side tutorial page.

- Handler: `app/routes/docs.py::module_tutorial`
- Preconditions (enforced):
  - same `<name>` validation as above
  - `docs/modules/<name>_tutorial_side_by_side.html` exists
- Response: text/html
- Errors: 404 as above

### `GET /docs/modules/<name>/<target>_tutorial_side_by_side.html`

Offline-friendly sibling-link resolver.

- Handler: `app/routes/docs.py::linked_tutorial`
- Behaviour:
  - Validates `<name>` (the path segment used to reach this handler)
  - Ignores `<name>` after validation and serves the tutorial for `<target>` via `module_tutorial(target)`
- Security note:
  - The target tutorial is still allow-listed by `_validate_doc_name(target)` inside `module_tutorial`.

### `GET /docs/modules/<name>/assets/<asset>`

Serves tutorial assets.

- Handler: `app/routes/docs.py::tutorial_asset`
- Preconditions (enforced):
  - `<name>` must be allow-listed
  - `<asset>` must be in `ALLOWED_TUTORIAL_ASSETS` (`theme.js`, `highlight.js`)
  - The resolved path must remain under `docs/modules/assets/`
- Response:
  - `application/javascript` for `.js` assets

### `GET /preview/<upload_id>`

Shows a preview page for an uploaded matrix.

- Handler: `app/routes/preview.py::show_preview`
- Input:
  - `<upload_id>` is an identifier used to locate a previously uploaded file.
- Errors:
  - 404 if upload not found
  - 400 if preview cannot be loaded
- Output:
  - HTML template: `app/templates/preview.html`

### `POST /preview/<upload_id>/confirm`

Confirms an upload for computation.

- Handler: `app/routes/preview.py::confirm_upload`
- Effect:
  - Adds `<upload_id>` to session key `confirmed_uploads`.
- Response:
  - JSON: `{ "status": "confirmed", "upload_id": "..." }`
- Errors:
  - 404 if upload not found

### `POST /preview/<upload_id>/cancel`

Cancels an upload confirmation.

- Handler: `app/routes/preview.py::cancel_upload`
- Effect:
  - Removes `<upload_id>` from `confirmed_uploads` if present.
- Response:
  - JSON: `{ "status": "cancelled", "upload_id": "..." }`

### `POST /compute/start`

Starts a ranking computation job.

- Handler: `app/routes/compute.py::start_computation`
- Request body: JSON
  - `upload_id` (required)
  - `criteria` (required; validated by `validate_criteria_json`)

Example:
```json
{
  "upload_id": "abc123",
  "criteria": {"criteria": []}
}
```

Preconditions (enforced):
- Request JSON must exist.
- `upload_id` must exist.
- Upload must be confirmed (session gate) or returns 403.
- Upload must exist on disk (via `get_upload_path`) or returns 404.
- Criteria must validate or returns 400.

Response:
- 200 JSON:
```json
{
  "status": "started",
  "job_id": "job_abc123",
  "upload_id": "abc123"
}
```

Errors:
- 400 for missing fields or validation failure
- 403 if upload not confirmed
- 404 if upload id not found

### `GET /compute/status/<job_id>`

Returns job status.

- Handler: `app/routes/compute.py::job_status`
- Response:
  - JSON: `{ "job_id": "...", "status": "completed", "progress": 100 }`
- Note:
  - Current implementation is simplified and always returns "completed".

## Testing guidance

- Main suite: `pytest tests/`
- Docs contract tests: `tests/test_docs_routes.py` and `tests/test_module_docs.py`

## Non-goals (current)

- No OpenAPI schema is generated.
- No public unauthenticated file browsing; docs and assets are allow-listed.
