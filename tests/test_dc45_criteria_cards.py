"""DC4.5 criteria-card workflow, semantic, and responsive-contract tests."""
from pathlib import Path

import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app({"TESTING": True, "SECRET_KEY": "dc45-test"})
    return app.test_client()


def _card_data(*included: int, **overrides: str) -> dict[str, str]:
    data = {"criteria_mode": "form"}
    for index in included:
        data.update({
            f"c{index}_include": "true",
            f"c{index}_name": f"Criteria {index + 1}",
            f"c{index}_weight": "0.5",
            f"c{index}_q": "0",
            f"c{index}_p": "0",
            f"c{index}_v": "0",
            f"c{index}_maximize": "true",
        })
    data.update(overrides)
    return data


def test_landing_renders_exactly_eight_cards_in_four_column_grid(client):
    response = client.get("/app/")
    body = response.data.decode()
    css = Path("app/static/style.css").read_text(encoding="utf-8")
    grid_block = css.split(".criteria-grid {", 1)[1].split(".criterion-entry", 1)[0]
    entry_block = css.split(".criterion-entry {", 1)[1].split(".include-toggle {", 1)[0]
    card_block = entry_block
    assert response.status_code == 200
    assert body.count('class="criterion-entry criteria-card"') == 8
    assert 'range(8)' in Path("app/templates/app_input.html").read_text(encoding="utf-8")
    assert 'grid-template-columns: repeat(4, minmax(0, 1fr));' in grid_block
    assert 'grid-auto-rows: 1fr;' in grid_block and 'gap: var(--space-md);' in grid_block
    assert 'display: grid;' in entry_block
    assert 'min-height: 22rem;' in card_block
    for index in range(8):
        assert f'c{{{{ i }}}}_name' not in body  # Rendered page has concrete controls.
        assert f'name="c{index}_name"' in body
        assert f'value="Criteria {index + 1}"' in body
    for index in range(8):
        assert body.count(f'name="c{index}_') == 7


def test_selected_cards_submit_and_unselected_malformed_cards_are_ignored(client):
    response = client.post(
        "/app/confirm-inputs",
        data=_card_data(0, 2, c1_weight="not-a-number", c1_name="Ignored"),
    )
    assert response.status_code == 200
    assert b"Criteria 1" in response.data
    assert b"Criteria 3" in response.data
    assert b"Ignored" not in response.data


def test_selected_card_values_remain_strictly_validated(client):
    response = client.post("/app/confirm-inputs", data=_card_data(0, 1, c1_weight="not-a-number"))
    assert response.status_code == 400
    assert b"Criterion 2 contains an invalid number" in response.data


def test_form_requires_at_least_two_selected_cards(client):
    response = client.post("/app/confirm-inputs", data=_card_data(0))
    assert response.status_code == 400
    assert b"Select at least 2 criteria" in response.data


def test_eight_selected_cards_are_accepted_at_form_boundary(client):
    data = _card_data(*range(8))
    for index in range(8):
        data[f"c{index}_weight"] = "0.125"
    response = client.post("/app/confirm-inputs", data=data)
    assert response.status_code == 200
    assert b"Criteria 8" in response.data


def test_json_mode_remains_supported_and_strict(client):
    valid = '[{"name":"A","weight":0.5,"q":0,"p":0,"v":0,"maximize":true},{"name":"B","weight":0.5,"q":0,"p":0,"v":0,"maximize":false}]'
    assert client.post("/app/confirm-inputs", data={"criteria_mode": "json", "criteria_json": valid}).status_code == 200
    invalid = client.post("/app/confirm-inputs", data={"criteria_mode": "json", "criteria_json": "[]"})
    assert invalid.status_code == 400
    assert b"1 through 8" in invalid.data


def test_form_is_semantic_script_free_and_responsive_without_javascript(client):
    template = Path("app/templates/app_input.html").read_text(encoding="utf-8").lower()
    css = Path("app/static/style.css").read_text(encoding="utf-8")
    assert '<fieldset class="criteria-mode">' in template
    assert '<legend>criteria entry mode</legend>' in template
    assert '<section class="structured-criteria" aria-labelledby="structured-criteria-heading">' in template
    assert '<legend class="visually-hidden">structured criteria cards</legend>' in template
    assert "<section class=\"criterion-entry criteria-card\"" in template
    assert "<script" not in template and "onchange=" not in template and "onclick=" not in template
    assert 'type="checkbox" value="true"' in template
    assert 'type="checkbox" value="true" checked' in template
    assert ".criteria-grid" in css
    assert "@media (max-width: 900px)" in css
    assert "@media (max-width: 520px)" in css
    assert "input:focus" in css


def test_criteria_card_ui_matches_required_reference_details():
    template = Path("app/templates/app_input.html").read_text(encoding="utf-8")
    css = Path("app/static/style.css").read_text(encoding="utf-8")
    card_block = css.split(".criterion-entry {", 1)[1].split(".include-toggle {", 1)[0]
    selected_block = css.split(".include-toggle:checked ~ .criteria-card-surface {", 1)[1].split(".criteria-card >", 1)[0]
    badge_block = css.split(".include-toggle:checked ~ h3 .included-badge,", 1)[1].split(".criteria-card h3", 1)[0]
    heading_block = css.split(".criteria-card h3 {", 1)[1].split(".criteria-card input", 1)[0]
    assert '<button class="btn btn-primary" type="submit">Continue to matrix input</button>' in template
    assert '<section class="criterion-entry criteria-card"' in template
    assert '<input class="include-toggle" id="c{{ i }}_include"' in template
    assert '<label class="include-control" for="c{{ i }}_include">Include criterion</label>' in template
    assert '<div class="criteria-card-surface" aria-hidden="true"></div>' in template
    assert '<span class="included-badge">Included</span>' in template
    assert '<span class="excluded-badge">Not included</span>' in template
    assert 'background: rgba(111, 125, 132, 0.14);' in card_block
    assert 'border: 3px solid #d23f6d;' in card_block
    assert 'background: linear-gradient(135deg, rgba(100, 0, 255, 0.12), rgba(126, 221, 211, 0.28));' in selected_block
    assert 'border-color: var(--color-primary);' in selected_block
    assert 'min-height: 22rem;' in card_block and 'grid-template-rows: auto auto auto auto auto 1fr auto;' in card_block
    assert 'display: none;' in css.split(".included-badge, .excluded-badge {", 1)[1].split(".include-toggle:checked", 1)[0]
    assert 'display: inline-block;' in badge_block
    assert ".include-toggle:not(:checked) ~ h3 .excluded-badge" in css
    assert ":has(" not in css
    assert "color: var(--color-primary);" in heading_block
    assert "box-shadow" not in card_block


def _relative_luminance(hex_color: str) -> float:
    channels = [int(hex_color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4 for channel in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast_ratio(foreground: str, background: str) -> float:
    lighter, darker = sorted((_relative_luminance(foreground), _relative_luminance(background)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def test_card_dom_and_grid_order_match_checkbox_header_badge_include_fields_contract():
    template = Path("app/templates/app_input.html").read_text(encoding="utf-8")
    css = Path("app/static/style.css").read_text(encoding="utf-8")
    card = template.split('{% for i in range(8) %}', 1)[1].split('{% endfor %}', 1)[0]

    checkbox = card.index('class="include-toggle"')
    heading = card.index('id="c{{ i }}_heading"')
    badge = card.index('class="included-badge"')
    include_text = card.index('class="include-control"')
    name = card.index('class="criterion-name-label"')
    values = card.index('class="criterion-values"')
    maximize = card.index('class="maximize-control"')

    assert checkbox < heading < badge < include_text < name < values < maximize
    toggle_placement = css.rsplit('.include-toggle {', 1)[1].split('.include-toggle:focus', 1)[0]
    assert 'grid-column: 1;' in toggle_placement
    assert 'grid-row: 1;' in toggle_placement
    include_block = css.split('.include-control {', 1)[1].split('.include-toggle {', 1)[0]
    assert 'grid-row: 3;' in include_block and 'justify-self: center;' in include_block
    heading_block = css.split('.criteria-card h3 {', 1)[1].split('.criteria-card input', 1)[0]
    assert 'text-align: center;' in heading_block


def test_card_state_cues_retain_visible_focusable_checkbox_labels_and_no_script(client):
    template = Path("app/templates/app_input.html").read_text(encoding="utf-8").lower()
    css = Path("app/static/style.css").read_text(encoding="utf-8")
    body = client.get("/app/").data.decode().lower()
    toggle_block = css.split(".include-toggle {", 1)[1].split(".criteria-card-surface", 1)[0]
    assert template.count('name="c{{ i }}_include" type="checkbox" value="true"') == 1
    assert body.count('class="include-toggle"') == 8
    assert body.count('<section class="criterion-entry criteria-card"') == 8
    assert '<input class="include-toggle" id="c{{ i }}_include"' in template
    assert template.index('class="include-toggle"') < template.index('id="c{{ i }}_heading"')
    assert template.index('id="c{{ i }}_heading"') < template.index('class="include-control"')
    assert '<label class="include-control" for="c{{ i }}_include">include criterion</label>' in template
    assert body.count('for="c') >= 48
    assert "width: 1.25rem;" in toggle_block and "height: 1.25rem;" in toggle_block
    assert "position: absolute;" not in toggle_block and "clip:" not in toggle_block
    assert "accent-color: var(--color-primary);" in toggle_block
    assert ".include-toggle:focus ~ .include-control" in css
    assert "included</span>" in template and "not included</span>" in template
    assert ".include-toggle:checked ~ .criteria-card-surface" in css
    assert ".include-toggle:not(:checked) ~ h3 .excluded-badge" in css
    assert ":has(" not in css
    assert "<script" not in template and "onclick=" not in template and "onchange=" not in template


def test_visible_include_checkbox_posts_checked_state_and_omits_unchecked_state(client):
    selected = client.post("/app/confirm-inputs", data=_card_data(0, 1))
    assert selected.status_code == 200
    unchecked = client.post("/app/confirm-inputs", data=_card_data(0))
    assert unchecked.status_code == 400
    assert b"Select at least 2 criteria" in unchecked.data


def test_card_state_foregrounds_meet_non_text_contrast_requirements():
    assert _contrast_ratio("#6400ff", "#e1f7f4") >= 3
    assert _contrast_ratio("#d23f6d", "#eef1f2") >= 3


def test_step_one_hierarchy_and_guidance_are_semantic_and_script_free(client):
    template = Path("app/templates/app_input.html").read_text(encoding="utf-8").lower()
    body = client.get("/app/").data.decode().lower()
    assert '<main class="container workflow-step">' in template
    assert '<p class="step-indicator">step 1 of 4</p>' in template
    assert '<h1>define ranking criteria</h1>' in template
    assert '<fieldset class="criteria-mode">' in template
    assert '<section class="json-guidance" aria-labelledby="json-guidance-heading">' in template
    assert '<label for="criteria_json">paste criteria json</label>' in template
    assert '<section class="structured-criteria" aria-labelledby="structured-criteria-heading">' in template
    assert 'id="structured-criteria-help"' in template
    assert 'aria-describedby="structured-criteria-help"' in template
    assert 'weights must sum to 1.' in body
    assert "<script" not in template


def test_responsive_grid_preserves_equal_card_contracts():
    css = Path("app/static/style.css").read_text(encoding="utf-8")
    tablet = css.split("@media (max-width: 900px)", 1)[1].split("@media (max-width: 768px)", 1)[0]
    mobile = css.split("@media (max-width: 520px)", 1)[1]
    assert 'grid-template-columns: repeat(2, minmax(0, 1fr));' in tablet
    assert 'grid-template-columns: 1fr;' in mobile
    assert 'min-height: 22rem;' in css and 'grid-auto-rows: 1fr;' in css
