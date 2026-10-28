# W1 Complete URL/Link Audit

**Status: NEEDS WORK**
**Pinned revision:** `36fce43bbb7c4075f4852b99763f2f5729710a16`
**Scope:** audit only; no production repair, browser execution, remote Git, or application change.

## Decision

W1 found 12 broken served-path references. They are six unique repository-oriented links duplicated in the ranking tutorial's Flask derivative and static derivative. All other resolved local references, registered routes, tutorial assets, fragments, workflow endpoints, and the generated download passed bounded local checks.

## Inventory

| Surface | Files | Result |
|---|---:|---|
| Static companion HTML | 14 | Every `href`, `src`, `action`, `poster`, and `download` inventoried |
| Flask generated documentation | 10 | Landing, modules index, and eight tutorial derivatives audited |
| Flask workflow templates | 4 | Input, matrix, preview, results audited |
| References | 270 | 241 valid; 12 broken; 1 planned; 16 external; 0 historical |
| Flask probes | 52 | Full allow-list vocabulary, slash variants, invalid routes, and download |

## Broken references

The six unique targets below fail from both served ranking-tutorial locations.

| Source served path | Target | Actual failed resolution |
|---|---|---|
| `/modules/ranking/tutorial/index.html` | `../../../../README.md` | `website/README.md` missing |
| same | `../../../../docs/tutorials/cli_quickstart.md` | `website/docs/tutorials/cli_quickstart.md` missing |
| same | `../../../../docs/runbook/debugging.md` | `website/docs/runbook/debugging.md` missing |
| same | `../../../../examples/d4_phase2/scenario-3/criteria_balanced.json` | `website/examples/...` missing |
| same | `../../../../electre3/ranking.py` | `website/electre3/ranking.py` missing |
| same | `../../../../tests/d4_checks/test_evidence.py` | `website/tests/...` missing |
| `/docs/modules/ranking/tutorial` | `../../README.md` | `/docs/README.md` returns 404 |
| same | `../tutorials/cli_quickstart.md` | `/docs/modules/tutorials/...` returns 404 |
| same | `../runbook/debugging.md` | `/docs/modules/runbook/...` returns 404 |
| same | `../../examples/d4_phase2/scenario-3/criteria_balanced.json` | `/docs/examples/...` returns 404 |
| same | `../../electre3/ranking.py` | `/docs/electre3/ranking.py` returns 404 |
| same | `../../tests/d4_checks/test_evidence.py` | `/docs/tests/...` returns 404 |

## Other classifications

- **Planned (1):** `{{ download_url }}` in `app/templates/app_results.html`; runtime workflow generated and verified as HTTP 200.
- **Historical (0):** no in-scope reference required a historical-only classification.
- **External (16):** absolute remote or localhost URLs were inventoried but not fetched remotely.
- **Trailing slashes:** `/docs/modules/`, module `/`, and tutorial `/` return 404; no audited link targets these variants.
- **App slash behavior:** `/app` and `/app/` both return 200.
- **Negative routes:** missing, uppercase, traversal-like, invalid asset, invalid tutorial, app, and download targets return 404.

## Generated ownership and maintainability

`scripts/build_website.py` owns static tutorial relocation. Its `normalize_tutorial_assets()` deliberately rewrites repository references, producing the six static failures. Flask serves the original generated tutorial without routes for repository files, producing the matching six Flask failures. The audit utility is isolated under `out/`; no core module grew and no production file changed.

## Offline and deferred evidence

- Static local assets and fragments resolve except the six broken repository links.
- External URLs remain unavailable offline by definition and were not fetched.
- Browser, assistive-technology, keyboard execution, and visual checks remain deferred and non-blocking for W1.
- Static keyboard assertions ran through focused tests; no browser interaction evidence was created.
- No math renderer exists in the audited pages, so renderer-failure regression coverage is not applicable.

## Required follow-up

Repair or intentionally remove/classify the six unique ranking tutorial references in both serving vocabularies, then rerun this inventory and focused tests.
