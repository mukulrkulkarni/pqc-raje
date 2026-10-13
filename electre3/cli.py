"""Command-line interface for ELECTRE III."""

import argparse
import json
import sys
from pathlib import Path

from .data import load_matrix
from .cli_run import run_ranking, format_preview


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ELECTRE III Multi-Criteria Decision Analysis"
    )
    parser.add_argument(
        "matrix_file",
        type=Path,
        help="Path to performance matrix file (.npy, .npz, .csv, .parquet)",
    )
    parser.add_argument(
        "criteria_file",
        type=Path,
        help="Path to criteria configuration JSON file",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output file for ranking results",
    )
    parser.add_argument(
        "-b", "--block-size",
        type=int,
        default=1000,
        help="Block size for computation (default: 1000)",
    )
    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Skip confirmation prompts",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress progress output",
    )

    args = parser.parse_args()

    # Load data
    try:
        matrix = load_matrix(args.matrix_file)
    except Exception as e:
        print(f"Error loading matrix: {e}", file=sys.stderr)
        return 1

    try:
        with open(args.criteria_file) as f:
            criteria_data = json.load(f)
    except Exception as e:
        print(f"Error loading criteria: {e}", file=sys.stderr)
        return 1

    # Show preview and confirm
    if not args.yes:
        preview = format_preview(matrix, criteria_data)
        print(preview)
        print()

        try:
            response = input("Proceed with computation? [y/N] ")
        except EOFError:
            response = "n"

        if response.lower() not in ("y", "yes"):
            print("Aborted.")
            return 0

    # Check output file
    if args.output and args.output.exists():
        if not args.yes:
            try:
                response = input(f"Output file {args.output} exists. Overwrite? [y/N] ")
            except EOFError:
                response = "n"
            if response.lower() not in ("y", "yes"):
                print("Aborted.")
                return 0

    # Run computation
    try:
        ranking = run_ranking(
            matrix, criteria_data,
            block_size=args.block_size,
            quiet=args.quiet,
        )
    except Exception as e:
        print(f"Computation error: {e}", file=sys.stderr)
        return 1

    # Output results
    if args.output:
        import numpy as np
        np.save(args.output, ranking)
        if not args.quiet:
            print(f"Ranking saved to {args.output}")
    else:
        print("Ranking (best to worst):")
        for i, idx in enumerate(ranking[:10], 1):
            print(f"  {i}. Alternative {idx}")
        if len(ranking) > 10:
            print(f"  ... ({len(ranking) - 10} more)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
