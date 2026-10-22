"""Command-line interface for ELECTRE III."""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

from .cli_run import format_preview
from .data import load_input
from .shared import compute_validated_ranking, validate_criteria


def main() -> int:
    parser = argparse.ArgumentParser(description="ELECTRE III MCDA")
    parser.add_argument("matrix_file", type=Path, help="Matrix file (.npy/.npz/.csv)")
    parser.add_argument("criteria_file", type=Path, help="Criteria JSON file")
    parser.add_argument("-o", "--output", type=Path, help="Output file")
    parser.add_argument("-b", "--block-size", type=int, default=1000)
    parser.add_argument("-y", "--yes", action="store_true", help="Skip prompts")
    parser.add_argument("-q", "--quiet", action="store_true")
    args = parser.parse_args()
    try:
        with args.criteria_file.open(encoding="utf-8") as stream:
            criteria_data = json.load(stream)
        input_data = load_input(args.matrix_file, validate_criteria(criteria_data))
    except Exception as exc:
        print(f"Error loading input: {exc}", file=sys.stderr)
        return 1
    if not args.yes:
        print(format_preview(input_data.scores, criteria_data), "\n")
        try:
            response = input("Proceed? [y/N] ")
        except EOFError:
            response = "n"
        if response.lower() not in ("y", "yes"):
            print("Aborted.")
            return 0
    if args.output and args.output.exists() and not args.yes:
        try:
            response = input(f"{args.output} exists. Overwrite? [y/N] ")
        except EOFError:
            response = "n"
        if response.lower() not in ("y", "yes"):
            print("Aborted.")
            return 0
    try:
        result = compute_validated_ranking(
            input_data.scores, criteria_data, args.block_size, identifiers=input_data.identifiers
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    if args.output:
        np.save(args.output, result.ranking)
        if not args.quiet:
            print(f"Saved to {args.output}")
    else:
        print("Ranking:", *(f"{index + 1}. {result.identifiers[row]}" for index, row in enumerate(result.ranking[:10])), sep="\n  ")
        if len(result.ranking) > 10:
            print(f"  ... ({len(result.ranking) - 10} more)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
