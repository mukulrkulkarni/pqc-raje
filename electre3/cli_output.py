"""Output helpers for the ELECTRE III command-line interface."""
from typing import Any

import numpy as np

from .cli_io import confirmed


def confirm_overwrite(output: Any, assume_yes: bool) -> bool:
    """Return whether an existing output may be overwritten."""
    return assume_yes or not output.exists() or confirmed(f"{output} exists. Overwrite? [y/N] ")


def report_result(result: Any, output: Any, quiet: bool) -> None:
    """Save or display a ranking with the established CLI output format."""
    if output:
        np.save(output, result.ranking)
        if not quiet:
            print(f"Saved to {output}")
        return
    entries = (f"{index + 1}. {result.identifiers[row]}" for index, row in enumerate(result.ranking[:10]))
    print("Ranking:", *entries, sep="\n  ")
    if len(result.ranking) > 10:
        print(f"  ... ({len(result.ranking) - 10} more)")
