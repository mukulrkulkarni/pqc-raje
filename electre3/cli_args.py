"""Argument parsing for the ELECTRE III command-line interface."""
import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    """Parse the public ELECTRE III CLI arguments."""
    parser = argparse.ArgumentParser(description="ELECTRE III MCDA")
    parser.add_argument("matrix_file", type=Path, help="Matrix file (.npy/.npz/.csv)")
    parser.add_argument("criteria_file", type=Path, help="Criteria JSON file")
    parser.add_argument("-o", "--output", type=Path, help="Output file")
    parser.add_argument("-b", "--block-size", type=int, default=1000)
    parser.add_argument("-y", "--yes", action="store_true", help="Skip prompts")
    parser.add_argument("-q", "--quiet", action="store_true")
    return parser.parse_args()
