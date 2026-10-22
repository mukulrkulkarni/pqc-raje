# DC4.5 documentation notes — equal criteria cards

## Scope and sources

- Approved scope: `out/dc-4-5-checkpoint.json`.
- Workflow contract: `app/routes/workflow.py` and `electre3/shared.py`.
- Card template and styles: `app/templates/app_input.html` and `app/static/style.css`.
- Tests: `tests/test_dc45_criteria_cards.py`, `tests/test_app_workflow.py`, `tests/test_active_template_ui.py`, and `tests/test_ui_styles.py`.

## Correction

The criteria form renders eight cards. The desktop grid uses four equal columns and two equal implicit rows. It uses one shared `var(--space-md)` gap for equal horizontal and vertical spacing. Entries use flex layout and cards use `flex: 1` with `min-height: 22rem`; fixed card grid rows keep internal controls aligned even when labels differ.

The checkbox directly precedes its card. Standard CSS sibling selectors make that checkbox authoritative without JavaScript:

- Unchecked: translucent grey tint, prominent 3px red/pink `#d23f6d` border, and visible **Not included** badge.
- Checked: translucent purple-to-green tint, prominent 3px purple `#6400ff` border, and visible **Included** badge.
- Badge rules hide **Included** when unchecked and **Not included** when checked.
- The visible native checkbox remains focusable. Its associated label toggles the same input and receives a focus outline when that input is focused.
- Responsive fallbacks retain the same equal-card rules in two columns at 900px and one column at 520px.

## Preserved behavior

Only checked cards are parsed. Malformed values on unchecked cards are ignored. Checked cards retain strict parsing and validation. Fewer than two selected cards fail; eight selected cards pass at the boundary. Defaults remain `Criteria 1` through `Criteria 8`, weight `0.125`, thresholds `0`, and checked Maximize controls. JSON mode and ranking computation are unchanged.

## Test evidence

| Category | Evidence | Result |
| --- | --- | --- |
| Geometry | Eight cards, four equal desktop columns, equal rows, shared gap, flex entries, equal card height contract. | Pass |
| Positive | Two selected cards submit and reach matrix input. | Pass |
| Positive boundary | Eight selected cards with `0.125` weights submit. | Pass |
| Negative | One selected card returns 400 and a minimum-selection error. | Pass |
| Negative | Malformed selected numeric input returns 400. | Pass |
| Edge | Malformed values on an unchecked card are ignored. | Pass |
| State cue | Checked sibling CSS has purple/green tint, purple border, and Included badge. | Pass |
| State cue | Unchecked CSS has grey tint, red/pink border, and Not included badge. | Pass |
| Semantic/no-script | Checkbox authority, labels, mutually exclusive badges, no scripts, and no `:has()` selector. | Pass |
| Responsive | Four-column, 900px two-column, and 520px one-column contracts retain equal-card rules. | Pass |
| Regression | Workflow, active-template, and stylesheet suites. | Pass |

Executed:

```text
python -m pytest tests/test_dc45_criteria_cards.py tests/test_app_workflow.py tests/test_active_template_ui.py tests/test_ui_styles.py -q
```

Result: `101 passed in 1.21s` for the latest card-order correction.

Executed:

```text
python -m compileall -q app electre3
```

Result: exit code `0`.

Executed:

```text
git diff --check
```

Result: exit code `0`.

## CSP correction evidence

The app CSP now uses `style-src 'self' 'unsafe-inline'`. This permits the existing same-origin `/static/style.css` resource while retaining the absence of an app `script-src` directive and application JavaScript. Tests verify the app response policy, linked stylesheet, no-script markup, CSS response type, and card stylesheet marker.

Executed after correction:

```text
python -m pytest tests/test_dc45_criteria_cards.py tests/test_app_workflow.py tests/test_active_template_ui.py tests/test_ui_styles.py tests/test_security_headers.py tests/test_security.py -q
```

Result: `98 passed in 1.46s`.

`python -m compileall -q app electre3` and `git diff --check` both returned exit code `0`.

## Visible-checkbox correction

The previous `.include-toggle` rule visually hid each native checkbox with absolute positioning and clipping. This contradicted the explicit Include criterion control requirement.

The correction retains the native checkbox immediately before its card and removes hidden/clip styling. Each Include control now has visible `1.25rem` width and height, a purple native `accent-color`, and standard keyboard focus. The existing label still uses `for="cN_include"`, so selecting **Include criterion** toggles the same input without JavaScript. Existing checked sibling selectors continue to control the selected card tint/border and mutually exclusive Included/Not included badges.

Regression assertions cover:

- **Positive:** two posted visible Include controls reach matrix input.
- **Negative:** one posted Include control fails the two-criterion minimum.
- **Edge:** all eight controls remain accepted at the maximum boundary.
- **Markup/accessibility:** eight rendered native checkboxes have explicit visible dimensions, no absolute or clip declaration, associated labels, native focus selector support, and checked sibling state rules.

## Internal-card hierarchy correction

The visible native Include checkbox now sits inside the top-left of each criterion card, immediately before its **Include criterion** label. The checkbox and label remain direct native form controls: the label `for` attribute toggles the checkbox, keyboard focus stays on the checkbox, and checked values post unchanged.

Each card is one semantic `section` that holds its input controls. A non-interactive, `aria-hidden` surface behind its controls receives the approved selected tint and purple border. This allows checked-state styling with standard general-sibling selectors, without JavaScript or `:has()`, while keeping the checkbox authoritative.

The card hierarchy now uses a top include row, centered criterion header, separate **Criterion name** label with centered editable name, consistent threshold label/input rows, and a bottom Maximize control. Grid rows, minimum height, and responsive 4/2/1-column geometry prevent controls from extending outside a card.

Additional regression assertions verify that all eight checkboxes are inside the card section, precede their Include labels, retain label association and native dimensions, and preserve selected/unselected sibling-state rules.

**External overlay note:** Project Plan/Scratch Pad is an Innovium external overlay. It is not application HTML and is outside this correction.

## Final gate status

UI/UX approved the final focus-selector correction and the user reported Visual pass. No persistent service was started. Validation for the final correction passed:

```text
python -m pytest tests/test_dc45_criteria_cards.py tests/test_app_workflow.py tests/test_active_template_ui.py tests/test_ui_styles.py tests/test_security_headers.py tests/test_security.py -q
```

Result: `100 passed in 1.41s` before the final focus-selector correction; the latest focused command passed `76` tests after that correction.

```text
python -m compileall -q app electre3
git diff --check
```

Both commands returned exit code `0`.

The user must explicitly report visual pass or fail for unchecked and checked cards at desktop and responsive widths. UI/UX re-review remains required before any commit. Browser rendering, keyboard traversal, focus presentation, assistive technology behavior, and visual polish remain unverified until that report.

No commit was created.

## Checkbox-state and Step 1 correction

The nested card markup uses a native Include checkbox followed by its label, state surface, and card heading. The state selectors now target the current heading level (`h3`): checked cards show the approved purple/aqua-green tint, prominent purple border, and **Included** badge; unchecked cards retain the grey tint, prominent red/pink border, and **Not included** badge.

Step 1 now provides a semantic **Step 1 of 4** indicator, page heading, criteria-entry-mode fieldset, JSON guidance with a labelled textarea, and a structured-criteria heading with selection help. This formatting-only change preserves the selection parser, JSON mode, strict validation, card geometry, no-JavaScript policy, and ranking computation.

Executed after this correction:

```text
python -m pytest tests/test_dc45_criteria_cards.py tests/test_app_workflow.py tests/test_active_template_ui.py tests/test_ui_styles.py tests/test_security_headers.py tests/test_security.py -q
```

Result: `100 passed in 1.41s`.

```text
python -m compileall -q app electre3
git diff --check
```

Both commands returned exit code `0`.

One initial focused test run failed because two assertions still expected the former `h2` badge selector. The assertions were corrected to `h3`; the full focused command then passed. The user visual pass and UI/UX review are complete. Final engineering verification and commit remain required.
