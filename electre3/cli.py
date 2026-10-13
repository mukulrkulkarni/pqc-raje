"""Command-line interface for ELECTRE III."""
import argparse, json, sys
from pathlib import Path
from .data import load_matrix
from .cli_run import run_ranking, format_preview

def main() -> int:
    p = argparse.ArgumentParser(description="ELECTRE III MCDA")
    p.add_argument("matrix_file", type=Path, help="Matrix file (.npy/.csv)")
    p.add_argument("criteria_file", type=Path, help="Criteria JSON file")
    p.add_argument("-o", "--output", type=Path, help="Output file")
    p.add_argument("-b", "--block-size", type=int, default=1000)
    p.add_argument("-y", "--yes", action="store_true", help="Skip prompts")
    p.add_argument("-q", "--quiet", action="store_true")
    args = p.parse_args()
    try:
        matrix = load_matrix(args.matrix_file)
    except Exception as e:
        print(f"Error loading matrix: {e}", file=sys.stderr); return 1
    try:
        with open(args.criteria_file) as f: criteria_data = json.load(f)
    except Exception as e:
        print(f"Error loading criteria: {e}", file=sys.stderr); return 1
    if not args.yes:
        print(format_preview(matrix, criteria_data), "\n")
        try: resp = input("Proceed? [y/N] ")
        except EOFError: resp = "n"
        if resp.lower() not in ("y", "yes"): print("Aborted."); return 0
    if args.output and args.output.exists() and not args.yes:
        try: resp = input(f"{args.output} exists. Overwrite? [y/N] ")
        except EOFError: resp = "n"
        if resp.lower() not in ("y", "yes"): print("Aborted."); return 0
    try:
        ranking = run_ranking(matrix, criteria_data, args.block_size, args.quiet)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr); return 1
    if args.output:
        import numpy as np; np.save(args.output, ranking)
        if not args.quiet: print(f"Saved to {args.output}")
    else:
        print("Ranking:", *(f"{i+1}. Alt {r}" for i,r in enumerate(ranking[:10])), sep="\n  ")
        if len(ranking) > 10: print(f"  ... ({len(ranking)-10} more)")
    return 0

if __name__ == "__main__": sys.exit(main())
