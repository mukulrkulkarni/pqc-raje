"""D8 local Markdown link and fragment audit."""
import re
from pathlib import Path

FILES = [
    Path("README.md"),
    *Path("docs/decisions").glob("d[3-7]*.md"),
    Path("docs/tutorials/cli_quickstart.md"),
    Path("docs/runbook/debugging.md"),
]
LINK = re.compile(r"(?<!!)\[[^]]*\]\(([^)]+)\)")
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.M)


def anchor(text):
    return re.sub(r"[^a-z0-9 -]", "", text.lower()).replace(" ", "-")


def main():
    errors = []
    for source in FILES:
        text = source.read_text(encoding="utf-8")
        for target in LINK.findall(text):
            if "://" in target or target.startswith(("mailto:", "#")):
                continue
            path, _, fragment = target.partition("#")
            destination = source.parent / path if path else source
            if not destination.is_file():
                errors.append(f"{source}: missing {target}")
            elif fragment and destination.suffix == ".md":
                anchors = {anchor(x) for x in HEADING.findall(destination.read_text(encoding="utf-8"))}
                if fragment not in anchors:
                    errors.append(f"{source}: missing fragment {target}")
    print(f"audited_files={len(FILES)} local_link_errors={len(errors)}")
    print("\n".join(errors))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
