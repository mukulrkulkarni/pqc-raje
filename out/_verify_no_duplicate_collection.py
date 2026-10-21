from pathlib import Path

collection = Path("out/test-collection-after.txt").read_text(encoding="utf-8")
for forbidden in (
    "Import file mismatch",
    "docs/design/committee_phase5/discordance_review/snapshot/tests/test_module_docs.py",
    "docs/design/phase6/credibility_review/snapshot/tests/test_module_docs.py",
):
    if forbidden in collection:
        raise SystemExit(f"duplicate collection evidence found: {forbidden}")
print("no duplicate test_module_docs collection evidence")
