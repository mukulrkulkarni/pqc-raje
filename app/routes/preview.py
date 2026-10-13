"""Preview routes for upload confirmation gate."""

from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify

from ..services.preview import get_matrix_preview
from ..services.security import get_upload_path

bp = Blueprint("preview", __name__, url_prefix="/preview")


def is_upload_confirmed(upload_id: str) -> bool:
    """Check if an upload has been confirmed by the user."""
    confirmed = session.get("confirmed_uploads", [])
    return upload_id in confirmed


def mark_upload_confirmed(upload_id: str) -> None:
    """Mark an upload as confirmed."""
    confirmed = session.get("confirmed_uploads", [])
    if upload_id not in confirmed:
        confirmed.append(upload_id)
    session["confirmed_uploads"] = confirmed
    session.modified = True


def clear_upload_confirmation(upload_id: str) -> None:
    """Clear confirmation status for an upload."""
    confirmed = session.get("confirmed_uploads", [])
    if upload_id in confirmed:
        confirmed.remove(upload_id)
    session["confirmed_uploads"] = confirmed
    session.modified = True


@bp.route("/<upload_id>")
def show_preview(upload_id: str):
    """Show preview page for uploaded matrix."""
    upload_path = get_upload_path(upload_id)
    if upload_path is None:
        return jsonify({"error": "Upload not found"}), 404

    preview_data = get_matrix_preview(upload_path)
    if preview_data is None:
        return jsonify({"error": "Could not load matrix"}), 400

    return render_template(
        "preview.html",
        upload_id=upload_id,
        preview=preview_data,
    )


@bp.route("/<upload_id>/confirm", methods=["POST"])
def confirm_upload(upload_id: str):
    """Confirm an upload for computation."""
    upload_path = get_upload_path(upload_id)
    if upload_path is None:
        return jsonify({"error": "Upload not found"}), 404

    mark_upload_confirmed(upload_id)
    return jsonify({"status": "confirmed", "upload_id": upload_id})


@bp.route("/<upload_id>/cancel", methods=["POST"])
def cancel_upload(upload_id: str):
    """Cancel an upload and clear confirmation."""
    clear_upload_confirmation(upload_id)
    return jsonify({"status": "cancelled", "upload_id": upload_id})
