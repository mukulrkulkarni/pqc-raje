"""Security utilities for upload validation."""

import re
from pathlib import Path
from typing import Any, Optional

from electre3.shared import validate_criteria

# Upload directory
UPLOAD_DIR = Path("uploads")

# Registry of valid uploads (in production, use database)
_upload_registry: dict[str, Path] = {}


def register_upload(upload_id: str, path: Path) -> None:
    """Register an upload in the registry."""
    _upload_registry[upload_id] = path


def get_upload_path(upload_id: str) -> Optional[Path]:
    """Return an uploaded path only from the registry."""
    return _upload_registry.get(upload_id)


def validate_upload_id(upload_id: str) -> bool:
    """Validate upload identifiers before registry lookup."""
    return bool(re.match(r"^[a-zA-Z0-9\-]+$", upload_id))


def validate_criteria_json(criteria: Any) -> Optional[str]:
    """Return a shared-contract validation error, or ``None`` when valid.

    Routes retain this error-returning compatibility API. The strict parser lives
    in ``electre3.shared`` and is also used by the CLI adapter.
    """
    try:
        validate_criteria(criteria)
    except ValueError as exc:
        return str(exc)
    return None
