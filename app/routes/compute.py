"""Compute routes for ELECTRE III ranking."""

from flask import Blueprint, request, jsonify, session

from ..services.security import get_upload_path, validate_criteria_json
from .preview import is_upload_confirmed

bp = Blueprint("compute", __name__, url_prefix="/compute")


@bp.route("/start", methods=["POST"])
def start_computation():
    """Start a ranking computation job.

    Requires:
    - upload_id: Previously uploaded matrix
    - criteria: JSON criteria configuration

    Returns 403 if upload not confirmed.
    Returns 400 if validation fails.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    upload_id = data.get("upload_id")
    if not upload_id:
        return jsonify({"error": "upload_id required"}), 400

    # Check confirmation gate
    if not is_upload_confirmed(upload_id):
        return jsonify({"error": "Upload not confirmed. Please preview and confirm first."}), 403

    # Validate upload exists
    upload_path = get_upload_path(upload_id)
    if upload_path is None:
        return jsonify({"error": "Upload not found"}), 404

    # Validate criteria
    criteria = data.get("criteria")
    if not criteria:
        return jsonify({"error": "criteria required"}), 400

    validation_error = validate_criteria_json(criteria)
    if validation_error:
        return jsonify({"error": validation_error}), 400

    # Create job (simplified - just return job ID)
    job_id = f"job_{upload_id}"

    return jsonify({
        "status": "started",
        "job_id": job_id,
        "upload_id": upload_id,
    })


@bp.route("/status/<job_id>")
def job_status(job_id: str):
    """Get status of a computation job."""
    # Simplified - would normally check actual job status
    return jsonify({
        "job_id": job_id,
        "status": "completed",
        "progress": 100,
    })
