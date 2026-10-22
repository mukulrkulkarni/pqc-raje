# Documentation Styling Audit

**Audit date:** 2026-10-22  
**Pinned revision:** `1f1c9395fb4fb591b41d473edf6e75b0a53782d0` (`record-final-release-gate`)  
**Disposition:** **NEEDS WORK** — static integrity passes, but documentation styling is not consistently aligned with the app/Getting Started MK-TII system.  
**Scope:** Audit only. No documentation page, application template, stylesheet, or generator was edited. No commit was created.

## Decision rationale

**Chosen:**
- MK-TII convergence — Reuses the shipped app/Getting Started tokens while preserving tutorial-specific dense layouts.

**Near-miss:**
- Preserve both systems — Avoids churn but leaves visible brand, spacing, and navigation drift.
- Replace tutorials wholesale — Maximizes uniformity but risks content, interaction, and no-JS regressions.

**Disqualified:**
- External design framework — Breaks offline-first and minimal-dependency constraints.
- JavaScript-first shell — Violates the app’s no-JS boundary.

## Objective and boundaries

This audit inventories the requested surfaces, compares them with the MK-TII reference, records source ownership, and defines target styling rules. Static source inspection and executed tests are reported separately.

Browser-rendered reflow, zoom, keyboard, offline, screen-reader/AT, and visual comparison tests are explicitly deferred and non-blocking. Static inspection does not prove browser behavior.

## Inventory

| Surface | Audited paths | Current state | Target label |
|---|---|---|---|
| Repository orientation | `README.md` | Markdown; content-oriented; no page-owned CSS | Keep semantic Markdown; align rendered-site wrapper where controlled |
| Getting Started | `docs/GETTING_STARTED.html` | MK-TII reference; Arial, purple/teal tokens, hero, cards, callout, code | **Reference / retain** |
| Tutorials | `docs/tutorials/cli_quickstart.md` | Markdown; renderer-dependent presentation | Preserve content; apply MK-TII only in owned renderer |
| Runbook | `docs/runbook/*.md` | Markdown; renderer-dependent presentation | Preserve content; apply MK-TII only in owned renderer |
| Module documents | `docs/modules/*.html`, `docs/modules/assets/*` | Blue/system-ui tutorial system; dense sidebar/split layout; optional JS | Retain dense layout; remap shared brand tokens and navigation |
| Website sources/output | `website/index.html`, `website/app/index.html`, `website/modules/**`, `website/_includes/primary-nav.html`, `website/site-config.json` | Mixed MK-TII landing pages and blue/system-ui module pages | Converge owned source pages; regenerate derived tutorials |
| App templates | `app/templates/*.html`, `app/static/style.css` | Arial MK-TII app system; server-rendered workflow; no script on active app pages | **Reference / retain** |

Tracked inventory at the pinned revision includes 1 README, 1 Getting Started HTML file, 1 tutorial Markdown file, 5 runbook Markdown files, 20 module paths, 17 website paths, and 7 app templates. Generated and source assets are counted as paths, not only pages.

## Reference visual system

Evidence: `app/static/style.css`, `docs/GETTING_STARTED.html`, `website/index.html`, `website/app/index.html`, and active workflow templates under `app/templates/app_*.html`.

| Element | Current MK-TII reference | Target rule |
|---|---|---|
| Sans font | `Arial, sans-serif` | Use Arial first on owned HTML documentation surfaces |
| Mono font | `Consolas`, `Monaco`, monospace | Use for code, signatures, values, and technical identifiers |
| Canvas/text | `#ffffff`, `#253746`, muted `#53646d` | Use as default light palette |
| Brand/action | Purple `#6400ff`; hover `#4f00cc` | Use for primary actions, headings, active states, and code accents |
| Accent/focus | Teal `#7eddd3` | Use for focus outlines, hero rule, and informational callouts |
| Surface/border | `#f5f7f8`, `#c9d4d9` | Use for cards, table heads, inline code, and boundaries |
| Typography | 16px/1.6 body; strong hierarchy; large hero title | Preserve readable measure and heading hierarchy |
| Spacing | `.25/.5/1/1.5/2/3rem` progression | Use shared spacing tokens; avoid isolated pixel scales |
| Layout | 1100–1200px centered container; responsive grids | Use centered content and collapse without horizontal page overflow |
| Cards | Light surface, 1px border, 8px radius | Use for choices, summaries, and grouped module links |
| Tables | Collapsed borders, scoped heads, overflow wrapper | Keep semantic tables; provide responsive labels where app patterns apply |
| Code | Mono, horizontal overflow, pale surface, purple left rule | Preserve whitespace; never require a remote highlighter |
| Callouts | Surface fill plus teal or warning left border | Encode meaning with text/icon and border, not color alone |
| Navigation | Semantic `<nav aria-label="Primary">`; local route vocabulary | Present Getting Started, App, Tutorials consistently; mark current page |
| Math | Native `<var>`, `<sub>`, Unicode symbols, descriptive prose | Do not require MathJax or another renderer for meaning |
| App boundary | Active `/app` templates have no scripts or inline handlers | Styling work must not add JavaScript to the app workflow |

## Static inspection findings

### Positive evidence

- `docs/GETTING_STARTED.html` and `app/static/style.css` share Arial, purple/teal, text, surface, border, spacing, and mono tokens.
- `website/index.html` and `website/app/index.html` reproduce the primary MK-TII landing-page vocabulary.
- Active app templates load one local stylesheet and use semantic `<main>` without scripts or inline handlers.
- Getting Started expresses net-flow math with `<var>Φ</var>`, `<sub>`, and Unicode operators; meaning does not depend on a math renderer.
- Module tutorials keep source, theme, and highlighting assets local; CSS includes a `:target` no-JS selection fallback.
- Navigation uses semantic labels on principal indexes and generated tutorial pages.

### Negative evidence

- `docs/modules/index.html`, module tutorials, and `website/modules/index.html` use blue `#2563eb`, slate colors, and `system-ui`, not MK-TII Arial/purple/teal.
- Module pages use a separate 4/8/12/16/24/32px spacing system and 10px radii, creating density and rhythm drift.
- Generated tutorial primary navigation is injected as inline styles with `var(--sans,system-ui)` and slate fallback colors.
- Module landing pages under `website/modules/*/index.html` are sparse route stubs and do not implement the MK-TII hierarchy, cards, or callouts.
- Navigation presentation differs across Flask docs, static website indexes, generated tutorials, and app templates.
- The tutorial sidebar disappears below 768px; source inspection cannot prove that remaining in-page navigation is sufficient in a browser.
- Tutorial enhancement controls depend on local JavaScript for theme and row toggling; the content remains present, but parity of all controls without JS is unproved.
- No common owned documentation stylesheet exists; repeated inline CSS increases drift and maintenance cost.

### Edge and boundary evidence

- `scripts/build_website.py` rejects malformed tutorial HTML without a real `<body>` and rejects an existing primary nav missing required links.
- The generator normalizes nested tutorial asset paths and injects local website plus Flask back-links.
- `docs/modules/assets/highlight.js` guards missing targets and indicator nodes, and handles Enter/Space statically; browser interaction remains deferred.
- `app/static/docs/theme.js` catches unavailable `localStorage`; default HTML and CSS remain readable without stored preferences.
- Root-absolute website links require a local HTTP server; `docs/runbook/website-local.md` documents this offline/local boundary.

## Ownership and generated-file rules

Evidence: `scripts/build_website.py`, `website/site-config.json`, `docs/runbook/website-local.md`, and existing D1 decision records.

| Path | Ownership | Rule |
|---|---|---|
| `docs/GETTING_STARTED.html` | Authoritative documentation source and MK-TII reference | Edit directly; preserve content claims and semantic math |
| `docs/tutorials/*.md`, `docs/runbook/*.md` | Authoritative Markdown sources | Edit content directly; do not embed renderer-specific styling without an owned rendering contract |
| `docs/modules/*_tutorial_side_by_side.html` | Authoritative tutorial HTML | Apply tutorial layout/style changes here first |
| `docs/modules/assets/theme.js`, `highlight.js` | Authoritative local enhancement assets | Preserve optional enhancement and no-JS readable content |
| `website/modules/*/tutorial/index.html` | Generated from `docs/modules/*_tutorial_side_by_side.html` | Do not hand-edit; rebuild with `scripts/build_website.py` |
| `website/modules/assets/*` | Generated copies from `docs/modules/assets/*` | Do not hand-edit; rebuild |
| `website/index.html`, `website/app/index.html`, `website/modules/index.html` | Website-owned source pages normalized in place by generator | Edit directly, then run generator and review diff |
| `website/modules/*/index.html` | Hybrid: generator creates only when absent, then treats existing pages as authored | Treat tracked existing files as website-owned sources; generator contract should be clarified before broad correction |
| `website/_includes/primary-nav.html` | Website source fragment, currently not consumed by `build_website.py` | Do not assume changes propagate; either wire it into generation or remove duplication in a later approved change |
| `app/templates/*.html`, `app/static/style.css` | Application-owned runtime UI | Use as target evidence; preserve no-JS active app boundary |

The generator is deterministic for copied tutorial pages and assets, but it has no `--check` mode. The existing regression invokes a rebuild and relies on version-control diff inspection to detect drift.

## Executed static tests

Command:

```text
python -m pytest -q tests/test_website_static.py tests/test_local_document_links.py tests/test_docs_routes.py tests/test_module_docs.py tests/test_ui_styles.py tests/test_active_template_ui.py
```

Result: **444 passed in 2.77s**, exit 0.

Collected-test command:

```text
python -m pytest --collect-only -q tests/test_website_static.py tests/test_local_document_links.py tests/test_docs_routes.py tests/test_module_docs.py tests/test_ui_styles.py tests/test_active_template_ui.py
```

Result: **444 tests collected in 0.40s**, exit 0.

Coverage represented by the executed suites:

- Positive: expected pages, routes, local assets, semantic structures, design tokens, navigation, and app stylesheet responses.
- Negative: external assets, scripts/inline handlers in active app templates, malformed tutorial bodies, and incomplete injected navigation.
- Edge: body/bodyguard matching, missing local files/fragments in the decision-link helper, responsive table labels, dark-mode/static tutorial invariants, and route variants.

Important limitation: `tests/test_local_document_links.py` validates two remediation decision documents and its helper behavior; it does **not** crawl every requested README/docs/website/app surface. Full local-link integrity remains a gap despite the passing suite.

## Required regression coverage for corrections

Any approved styling implementation must add or retain executable static coverage for:

1. Missing generated source/target and missing local href/fragment across all changed documentation surfaces.
2. Malformed HTML inputs, including missing/duplicate body boundaries and incomplete navigation placeholders.
3. Enter and Space behavior for custom tutorial controls, plus native-link behavior without JavaScript.
4. Math-renderer absence/failure: equations remain meaningful as semantic HTML/text with no remote dependency.
5. Local link and asset integrity for Flask routes, root-absolute static routes, nested generated pages, and offline-local serving.
6. No scripts or inline handlers in active app workflow templates.
7. Generator idempotence: rebuild produces no unexpected tracked diff.

Browser execution for keyboard behavior, reflow, zoom, offline loading, and assistive technology remains deferred and non-blocking for this audit.

## Maintainability and scope assessment

- `app/static/style.css` is the single app style owner, but documentation duplicates tokens inline across many HTML files.
- Tutorial HTML files are large, self-contained documents; a correction should centralize shared tokens without rewriting content or interaction logic.
- `scripts/build_website.py` is compact and focused, but hybrid landing ownership and unused `_includes` create ambiguity.
- No core executable module was changed. Core-module line-limit compliance is therefore not affected by this audit.
- The approved correction scope should change shared style ownership and generated outputs only; it must not change algorithms, documentation claims, formulas, routes, or app workflow behavior.

## Recommended correction order

1. Establish shared MK-TII documentation tokens and navigation rules at authoritative sources.
2. Adapt dense tutorials through token mapping, preserving layout, semantic content, no-JS fallback, and local enhancements.
3. Regenerate website outputs and run static route, link, generator, math, keyboard-source, and no-JS boundary regressions.

See `docs/decisions/style-gap-register.md` for prioritized, file-level actions and acceptance evidence.
