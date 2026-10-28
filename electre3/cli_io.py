"""Input and prompt helpers for the ELECTRE III command-line interface."""
import json
import sys
from typing import Any

from .cli_run import format_preview
from .data import load_input
from .shared import validate_criteria


def load_cli_input(matrix_file: Any, criteria_file: Any) -> tuple[Any, Any] | None:
    """Load validated CLI inputs, reporting load failures consistently."""
    try:
        with criteria_file.open(encoding="utf-8") as stream:
            criteria_data = json.load(stream)
        return load_input(matrix_file, validate_criteria(criteria_data)), criteria_data
    except Exception as exc:
        print(f"Error loading input: {exc}", file=sys.stderr)
        return None


def confirmed(prompt: str) -> bool:
    """Return whether the user confirms a CLI prompt."""
    try:
        response = input(prompt)
    except EOFError:
        response = "n"
    return response.lower() in ("y", "yes")


def confirm_run(input_data: Any, criteria_data: Any, assume_yes: bool) -> bool:
    """Preview and confirm the pending ranking unless confirmation is skipped."""
    if assume_yes:
        return True
    print(format_preview(input_data.scores, criteria_data), "\n")
    return confirmed("Proceed? [y/N] ")
