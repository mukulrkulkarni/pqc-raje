"""D3 Phase 1 user-facing documentation placement checks."""
from pathlib import Path


ROOT = Path(__file__).parent.parent
README = ROOT / "README.md"
GETTING_STARTED = ROOT / "docs" / "GETTING_STARTED.html"
WEBSITE_INDEX = ROOT / "website" / "index.html"
WEBSITE_APP = ROOT / "website" / "app" / "index.html"

SETUP_CHECK = "python -m compileall -q electre3 app"
CONVERT_COMMAND = (
    "python scripts/convert_matrix_csv.py "
    "examples/assets_priority/matrix_with_headers.csv "
    "out/assets_priority_cli.npy --has-header --id-col Asset"
)
CLI_COMMAND = "python -m electre3.cli out/assets_priority_cli.npy examples/assets_priority/criteria.json -y"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase1_entry_points_publish_verified_cli_commands() -> None:
    """README and both landing pages retain the independently run CLI path."""
    for path in (README, GETTING_STARTED, WEBSITE_INDEX):
        text = _read(path)
        for command in (SETUP_CHECK, CONVERT_COMMAND, CLI_COMMAND):
            assert command in text, f"{path} omits {command}"
        assert "1. Alt 1" in text or "<code>Alt 1</code>" in text
        assert "Alt 0" in text
        assert "Alt 2" in text


def test_phase1_pages_do_not_invent_install_commands() -> None:
    """The placement uses the repository environment instead of package installation."""
    for path in (README, GETTING_STARTED, WEBSITE_INDEX, WEBSITE_APP):
        text = _read(path).lower()
        assert "pip install" not in text
        assert "conda install" not in text


def test_phase1_html_preserves_local_hardening_and_semantics() -> None:
    """User-facing HTML retains CSP, viewport, primary navigation, and semantic math."""
    for path in (GETTING_STARTED, WEBSITE_INDEX, WEBSITE_APP):
        text = _read(path)
        assert "Content-Security-Policy" in text
        assert 'name="viewport"' in text
        assert 'aria-label="Primary"' in text
    for path in (GETTING_STARTED, WEBSITE_INDEX):
        text = _read(path)
        assert "<var>Φ</var>" in text
        assert "<sub>b</sub>" in text


def test_phase1_documents_explicit_browser_evidence_limits() -> None:
    """Pages must not claim browser checks that current evidence does not support."""
    for path in (README, GETTING_STARTED, WEBSITE_APP):
        text = _read(path).lower()
        assert "browser reflow" in text
        assert "screen-reader" in text
        assert "unverified" in text or "limited" in text


def test_uiux_gate_corrections_preserve_semantics_and_local_links() -> None:
    """The five D3 UI/UX corrections retain static, no-JavaScript page contracts."""
    index = _read(WEBSITE_INDEX)
    app = _read(WEBSITE_APP)
    quickstart = _read(ROOT / "docs" / "tutorials" / "cli_quickstart.md")

    orientation = index.split('<section class="grid" aria-label="Orientation">', 1)[1].split("</section>", 1)[0]
    assert orientation.count("<h3>") == 3
    assert "<h2>CLI</h2>" not in orientation
    assert "<h2>Web app</h2>" not in orientation
    assert "<h2>Learn more</h2>" not in orientation

    assert "app.pqcmig.scoring.draft" not in app
    assert 'href="https://' not in app
    assert "Review status:" in app
    assert "under D3 review" in app
    assert "<script" not in app.lower()

    assert "### Chosen" not in quickstart
    assert "### Near-miss" not in quickstart
    assert "Mermaid flowchart is used because" in quickstart


def test_uiux_gate_uses_shared_tokens_and_spacing_names() -> None:
    """D3 pages use the same color, font, and spacing token vocabulary."""
    required_tokens = (
        "--color-bg:", "--color-surface:", "--color-text:",
        "--color-text-muted:", "--color-primary:", "--color-border:",
        "--color-accent:", "--font-sans:", "--font-mono:",
        "--space-sm:", "--space-md:", "--space-lg:", "--space-xl:",
    )
    for path in (GETTING_STARTED, WEBSITE_INDEX, WEBSITE_APP):
        text = _read(path)
        for token in required_tokens:
            assert token in text, f"{path} omits {token}"
        assert "--bg:" not in text
        assert "--s1:" not in text


def test_cli_quickstart_matches_cli_score_and_output_contract() -> None:
    """The quickstart describes strict scores and ranking-index-only CLI output."""
    text = _read(ROOT / "docs" / "tutorials" / "cli_quickstart.md")
    assert "finite matrix scores in `[0,1]`" in text
    assert "prints ranking indices" in text
    assert "saves ranking indices" in text
    assert "does not print or save net-flow scores" in text
    assert "not net-flow scores" in text


def test_browser_evidence_names_zoom_as_unverified() -> None:
    """The pages disclose the unverified browser-zoom boundary."""
    for path in (README, GETTING_STARTED, WEBSITE_APP):
        text = _read(path).lower()
        assert "browser zoom" in text
        assert "unverified" in text


def test_app_landing_uses_website_landing_style_contract() -> None:
    """The app landing retains the website landing layout and static-page styling."""
    index = _read(WEBSITE_INDEX)
    app = _read(WEBSITE_APP)
    shared_rules = (
        ".main{max-width:1100px",
        ".nav,.actions{display:flex;flex-wrap:wrap;gap:var(--space-sm)}",
        ".hero{padding:var(--space-2xl) 0 var(--space-xl);border-bottom:4px solid var(--color-accent)}",
        "h1{font-size:clamp(2rem,5vw,3.2rem)",
        "@media(max-width:768px){.main{padding:var(--space-md)}.hero{padding:var(--space-xl) 0}}",
    )
    for rule in shared_rules:
        assert rule in index
        assert rule in app
    assert "<script" not in app.lower()
