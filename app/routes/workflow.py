"""Server-rendered, no-JavaScript ELECTRE III workflow under /app."""
from __future__ import annotations

import csv
import io
import json
import secrets
from dataclasses import dataclass
from typing import Any

import numpy as np
from flask import Blueprint, Response, abort, render_template, request, session, url_for

from app.services.result_cache import result_cache
from app.services.runtime_profile import APP_RUNTIME_MODEL
from electre3.runtime import ComputeTimeoutError, FeasibilityError
from electre3.serialization import serialize_result_json
from electre3.shared import (
    DEFAULT_BLOCK_SIZE,
    MAX_ROWS,
    compute_validated_ranking,
    validate_criteria,
    validate_csv_headers,
    validate_identifiers,
)

bp = Blueprint("workflow", __name__, url_prefix="/app")
_MAX_INPUT_BYTES = 100 * 1024 * 1024
_WORKFLOWS: dict[str, dict[str, Any]] = {}


def _workflow() -> dict[str, Any]:
    workflow_id = session.get("app_workflow_id")
    if not isinstance(workflow_id, str) or workflow_id not in _WORKFLOWS:
        abort(400, "Start at /app/ and submit criteria first.")
    return _WORKFLOWS[workflow_id]


def _download_session_id() -> str:
    """Return a small opaque identifier stored in Flask's signed session cookie."""
    session_id = session.get("app_download_session_id")
    if not isinstance(session_id, str) or not session_id:
        session_id = secrets.token_urlsafe(24)
        session["app_download_session_id"] = session_id
        session.modified = True
    return session_id


def _new_workflow(criteria_data: list[dict[str, Any]]) -> str:
    workflow_id = secrets.token_urlsafe(24)
    _WORKFLOWS[workflow_id] = {"criteria": criteria_data, "previewed": False}
    session["app_workflow_id"] = workflow_id
    # Keep only opaque identifiers in the signed cookie for 30 minutes.
    session.permanent = True
    session.modified = True
    return workflow_id


def _criteria_from_form() -> list[dict[str, Any]]:
    mode = request.form.get("criteria_mode")
    if mode == "json":
        try:
            value = json.loads(request.form.get("criteria_json", ""))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Criteria JSON is invalid: {exc.msg}") from exc
        if not isinstance(value, list):
            raise ValueError("Criteria JSON must contain a list.")
        return value
    if mode != "form":
        raise ValueError("Select either Paste JSON or Fill form.")
    criteria = []
    for index in range(8):
        # A card participates only when its explicit Include checkbox is posted.
        # Ignore all values from omitted cards, including malformed edited values.
        if request.form.get(f"c{index}_include") != "true":
            continue
        name = request.form.get(f"c{index}_name", "").strip()
        try:
            criteria.append({
                "name": name, "weight": float(request.form.get(f"c{index}_weight", "")),
                "q": float(request.form.get(f"c{index}_q", "")),
                "p": float(request.form.get(f"c{index}_p", "")),
                "v": float(request.form.get(f"c{index}_v", "")),
                "maximize": request.form.get(f"c{index}_maximize") == "true",
            })
        except ValueError as exc:
            raise ValueError(f"Criterion {index + 1} contains an invalid number.") from exc
    if len(criteria) < 2:
        raise ValueError("Select at least 2 criteria in the structured form.")
    return criteria


def _matrix_text() -> tuple[bytes, str]:
    pasted = request.form.get("matrix_csv", "")
    upload = request.files.get("matrix_file")
    if pasted.strip():
        payload = pasted.encode("utf-8")
        return payload, "matrix.csv"
    if upload and upload.filename:
        payload = upload.read(_MAX_INPUT_BYTES + 1)
        return payload, upload.filename
    raise ValueError("Provide matrix CSV text or select a matrix file.")


def _parse_csv(payload: bytes, criteria: list[Any], header_mode: str, allow_missing: bool, replacement: float) -> tuple[np.ndarray, list[str], list[str]]:
    try:
        text = payload.decode("utf-8-sig")
        rows = list(csv.reader(io.StringIO(text)))
    except (UnicodeDecodeError, csv.Error) as exc:
        raise ValueError("CSV must be valid UTF-8 text.") from exc
    if not rows:
        raise ValueError("CSV contains no rows.")
    if header_mode not in {"headered", "headerless"}:
        raise ValueError("Select whether the CSV has a header row.")
    config = validate_criteria(criteria)
    expected = len(config) + 1
    headers = ["Asset ID", *[criterion.name for criterion in config]]
    identifiers: list[str] = []
    data_rows = rows
    if header_mode == "headered":
        validate_csv_headers(rows[0], config)
        headers = rows[0]
        data_rows = rows[1:]
    values: list[list[float]] = []
    for row_index, row in enumerate(data_rows, start=2 if header_mode == "headered" else 1):
        if len(row) != expected:
            raise ValueError(f"CSV row {row_index} has {len(row)} columns; expected {expected}.")
        score_cells = row[1:]
        identifiers.append(row[0])
        scores = []
        for column_index, cell in enumerate(score_cells, start=1):
            if not cell.strip():
                if not allow_missing:
                    raise ValueError(f"CSV row {row_index}, score column {column_index} is missing. Select missing-value approval to replace it.")
                scores.append(replacement)
                continue
            try:
                scores.append(float(cell))
            except ValueError as exc:
                raise ValueError(f"CSV row {row_index}, score column {column_index} is not numeric.") from exc
        values.append(scores)
    validate_identifiers(identifiers)
    return np.asarray(values, dtype=np.float64), headers, identifiers


def _parse_matrix(criteria: list[Any]) -> tuple[np.ndarray, list[str], list[str], str]:
    payload, filename = _matrix_text()
    if len(payload) > _MAX_INPUT_BYTES:
        raise ValueError("Matrix input exceeds the 100 MiB limit.")
    replacement_text = request.form.get("missing_replacement", "0")
    try:
        replacement = float(replacement_text)
    except ValueError as exc:
        raise ValueError("Missing-value replacement must be a number in [0, 1].") from exc
    if not 0 <= replacement <= 1:
        raise ValueError("Missing-value replacement must be in [0, 1].")
    allow_missing = request.form.get("approve_missing") == "yes"
    if filename.lower().endswith(".csv"):
        matrix, headers, identifiers = _parse_csv(payload, criteria, request.form.get("header_mode", ""), allow_missing, replacement)
        return matrix, headers, identifiers, "CSV"
    if filename.lower().endswith(".npy"):
        try:
            matrix = np.load(io.BytesIO(payload), allow_pickle=False)
        except (ValueError, OSError) as exc:
            raise ValueError("NPY matrix could not be read.") from exc
    elif filename.lower().endswith(".npz"):
        try:
            archive = np.load(io.BytesIO(payload), allow_pickle=False)
            keys = list(archive.keys())
            if len(keys) != 1:
                raise ValueError("NPZ input must contain exactly one array.")
            matrix = archive[keys[0]]
        except (ValueError, OSError) as exc:
            raise ValueError("NPZ matrix could not be read.") from exc
    else:
        raise ValueError("Matrix file must use .csv, .npy, or .npz.")
    config = validate_criteria(criteria)
    return np.asarray(matrix), ["Asset ID", *[c.name for c in config]], [str(i) for i in range(len(matrix))], "NumPy"


@bp.get("")
@bp.get("/")
def input_form():
    return render_template("app_input.html")


@bp.post("/confirm-inputs")
def confirm_inputs():
    try:
        criteria = _criteria_from_form()
        validate_criteria(criteria)
    except ValueError as exc:
        return render_template("app_input.html", error=str(exc), submitted=request.form), 400
    workflow_id = _new_workflow(criteria)
    return render_template("app_matrix.html", workflow_id=workflow_id, criteria=criteria)


@bp.post("/preview")
def preview():
    state = _workflow()
    try:
        matrix, headers, identifiers, source = _parse_matrix(state["criteria"])
        # Strict shared validation owns shape, count, finite, and score-range rules.
        from electre3.shared import validate_score_matrix
        matrix = validate_score_matrix(matrix, len(state["criteria"]))
    except ValueError as exc:
        return render_template("app_matrix.html", workflow_id=session["app_workflow_id"], criteria=state["criteria"], error=str(exc)), 400
    state.update(matrix=matrix, headers=headers, identifiers=identifiers, source=source, previewed=True)
    return render_template(
        "app_preview.html", criteria=state["criteria"], headers=headers,
        rows=matrix[:5], identifiers=identifiers[:5], total_rows=len(matrix), source=source,
        identifier_label=headers[0],
    )


@bp.post("/compute")
def compute():
    state = _workflow()
    if not state.get("previewed") or "matrix" not in state:
        abort(400, "Preview is required before computation.")
    if request.form.get("confirm_compute") != "yes":
        abort(400, "Confirm validated inputs before computation.")
    # Reject infeasible work before ranking. The shared adapter owns validation,
    # calculation, deadline checks, and immutable RankingResult construction.
    try:
        result = compute_validated_ranking(
            state["matrix"], state["criteria"], DEFAULT_BLOCK_SIZE,
            runtime_model=APP_RUNTIME_MODEL,
            identifiers=state["identifiers"],
        )
    except FeasibilityError as exc:
        abort(422, f"Computation rejected before start: {exc}")
    except ComputeTimeoutError as exc:
        # Do not serialize or publish a partial result after the hard deadline.
        abort(504, str(exc))
    except ValueError as exc:
        abort(400, str(exc))
    top = []
    for rank, index in enumerate(result.ranking[:10], start=1):
        row = int(index)
        top.append({"rank": rank, "identifier": result.identifiers[row], "score": float(result.net_flow[row])})
    token = result_cache.store(_download_session_id(), "ranking-result.json", serialize_result_json(result))
    return render_template(
        "app_results.html", top=top, total=len(result.ranking),
        identifier_label=state["headers"][0],
        download_url=url_for("workflow.download_result", token=token),
    )


@bp.get("/download/<token>")
def download_result(token: str):
    """Serve a current, session-bound, checksum-verified result without storage."""
    try:
        cached = result_cache.download(_download_session_id(), token)
    except PermissionError:
        abort(429, "Download rate limit exceeded.")
    except ValueError:
        abort(410, "Cached result integrity validation failed.")
    if cached is None:
        abort(404, "Download is unavailable or expired.")
    name, payload = cached
    response = Response(payload, mimetype="application/json")
    response.headers["Content-Disposition"] = f'attachment; filename="{name}"'
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    response.headers["Content-Length"] = str(len(payload))
    return response
