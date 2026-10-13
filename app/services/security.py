"""Security utilities for upload validation."""

import re
from pathlib import Path
from typing import Any, Optional

# Upload directory
UPLOAD_DIR = Path("uploads")

# Registry of valid uploads (in production, use database)
_upload_registry: dict[str, Path] = {}


def register_upload(upload_id: str, path: Path) -> None:
    """Register an upload in the registry.

    Args:
        upload_id: Unique upload identifier.
        path: Path to the uploaded file.
    """
    _upload_registry[upload_id] = path


def get_upload_path(upload_id: str) -> Optional[Path]:
    """Get the path for a registered upload.

    Uses registry lookup instead of path construction
    to prevent path traversal attacks.

    Args:
        upload_id: The upload identifier.

    Returns:
        Path to upload file, or None if not found.
    """
    return _upload_registry.get(upload_id)


def validate_upload_id(upload_id: str) -> bool:
    """Validate upload ID format.

    Args:
        upload_id: The upload identifier.

    Returns:
        True if valid format, False otherwise.
    """
    # Only allow alphanumeric and hyphens
    return bool(re.match(r"^[a-zA-Z0-9\-]+$", upload_id))


def validate_criteria_json(criteria: Any) -> Optional[str]:
    """Validate criteria JSON structure.

    Args:
        criteria: The criteria data to validate.

    Returns:
        Error message if invalid, None if valid.
    """
    if not isinstance(criteria, list):
        return "criteria must be a list"

    if len(criteria) == 0:
        return "criteria list cannot be empty"

    for i, c in enumerate(criteria):
        if not isinstance(c, dict):
            return f"criterion {i} must be an object"

        # Required fields
        if "weight" not in c:
            return f"criterion {i} missing 'weight'"
        if "q" not in c:
            return f"criterion {i} missing 'q'"
        if "p" not in c:
            return f"criterion {i} missing 'p'"
        if "v" not in c:
            return f"criterion {i} missing 'v'"

        # Numeric validation
        try:
            w = float(c["weight"])
            q = float(c["q"])
            p = float(c["p"])
            v = float(c["v"])
        except (TypeError, ValueError):
            return f"criterion {i} has non-numeric threshold values"

        # Threshold ordering
        if q < 0:
            return f"criterion {i}: q must be >= 0"
        if p < q:
            return f"criterion {i}: p must be >= q"
        if v < p:
            return f"criterion {i}: v must be >= p"
        if w <= 0:
            return f"criterion {i}: weight must be > 0"

    return None
