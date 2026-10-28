"""Command-line interface for ELECTRE III."""
import sys

from .cli_args import parse_args
from .cli_io import confirm_run, load_cli_input
from .cli_output import confirm_overwrite, report_result
from .shared import compute_validated_ranking


def main() -> int:
    """Run the established ELECTRE III command-line workflow."""
    args = parse_args()
    loaded = load_cli_input(args.matrix_file, args.criteria_file)
    if loaded is None:
        return 1
    input_data, criteria_data = loaded
    if not confirm_run(input_data, criteria_data, args.yes):
        print("Aborted.")
        return 0
    if args.output and not confirm_overwrite(args.output, args.yes):
        print("Aborted.")
        return 0
    try:
        result = compute_validated_ranking(
            input_data.scores, criteria_data, args.block_size, identifiers=input_data.identifiers
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    report_result(result, args.output, args.quiet)
    return 0


if __name__ == "__main__":
    sys.exit(main())
