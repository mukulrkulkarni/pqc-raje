"""H1 executable-line audit."""
import io
import tokenize
from pathlib import Path

PATHS = [
    "electre3/cli.py", "electre3/cli_args.py", "electre3/cli_io.py",
    "electre3/cli_output.py", "electre3/config.py", "electre3/config_validation.py",
]

for path in PATHS:
    tokens = tokenize.generate_tokens(io.StringIO(Path(path).read_text(encoding="utf-8")).readline)
    lines = {token.start[0] for token in tokens if token.type not in {
        tokenize.COMMENT, tokenize.ENCODING, tokenize.ENDMARKER, tokenize.INDENT,
        tokenize.DEDENT, tokenize.NEWLINE, tokenize.NL,
    }}
    print(f"{path}: {len(lines)} executable lines")
    if len(lines) > 50:
        raise SystemExit(f"{path} exceeds 50 executable lines")
