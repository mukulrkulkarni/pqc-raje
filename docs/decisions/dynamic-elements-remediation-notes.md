# Dynamic-elements remediation notes

**Status:** Evidence remediation complete. No dynamic widget, JavaScript, KaTeX, ranking, cache, or documentation narrative change occurred.

## Current and target status

| Control | Previous status | Target | Result |
|---|---|---|---|
| Active `/app` stylesheet | `style.css` existed but active templates did not link it | Local stylesheet on every active app template | Complete |
| Active-template UI evidence | Legacy-template tests dominated | Test active semantic structure, responsive tables, and no-script policy | Complete |
| Route CSP evidence | Route checks existed but were not exact policy assertions | Test `/app` uses `CSP_APP`; docs uses `CSP_DOCS` | Complete |
| Markdown/local-link evidence | No narrow remediation checker | Validate local decision-document targets and fragments | Complete |
| Browser, keyboard, AT, offline evidence | Not executed | Attempt available local browser tooling | Limited: no browser or browser automation executable found |

## Changes and rationale

- Linked `app/static/style.css` using Flask `url_for` in all active `app_*.html` templates.
- Added viewport metadata and `container`/`table-wrapper` hooks without adding behavior.
- Added table header scopes and rendered `data-label` attributes for responsive table cells.
- Preserved forms, route actions, text, server-rendered workflow, and no-JavaScript policy.
- Added focused structural tests and exact route-policy CSP tests.
- Added stdlib-only Markdown local-target and heading-fragment checks for the remediation decision documents.

## Evidence inventory

| Category | Positive evidence | Negative evidence | Edge evidence |
|---|---|---|---|
| Stylesheet and UI structure | Every active template links local `style.css`, has viewport/title/main, and serves CSS | Test rejects scripts and inline `on*` handlers | Input, preview, and results tables require scoped headers and `data-label`; app redirects are followed |
| CSP | `/app` and `/app/` resolve with exact `CSP_APP`; docs routes resolve with exact `CSP_DOCS` | App policy has no `script-src`; docs policy rejects `unsafe-inline` scripts | Root and module documentation routes exercise docs policy; trailing-slash app redirect exercises route normalization |
| Markdown links/fragments | Remediation and meeting notes have valid local targets/fragments | Synthetic missing file and missing fragment report errors | Anchor-only and external links are intentionally ignored |
| Workflow regression | Existing criteria, preview, computation, cache download, and session tests pass | Invalid criteria, missing preview/confirmation, unknown download tokens, score/header errors pass | Missing-value approval, infeasible/timeout handling, compatibility routes pass |
| Browser/keyboard/AT/offline | Server-rendered semantic forms and native controls receive structural coverage | No browser executable or Playwright/Selenium runner was available | Network-disabled navigation and assistive-technology behavior remain unexecuted |

## Commands and results

```text
python -m pytest tests/test_active_template_ui.py tests/test_app_workflow.py tests/test_security_headers.py tests/test_docs_routes.py -q
219 passed in 2.02s

python -m compileall -q app electre3 tests && git diff --check
exit 0

where playwright & where chromium & where chrome & where firefox & python -c "print('browser-python-ok')"
No Playwright, Chromium, Chrome, or Firefox executable found.

python -m pytest tests/test_active_template_ui.py tests/test_local_document_links.py tests/test_app_workflow.py tests/test_security_headers.py tests/test_docs_routes.py -q
223 passed in 2.22s
```

## Debugging and verification guide

1. Run the final focused pytest command above. It covers active templates, links, CSP, and workflow regressions.
2. To diagnose a CSP failure, compare the response header with `CSP_APP` or `CSP_DOCS` in `app/__init__.py`; do not add JavaScript to `/app`.
3. To diagnose layout output, request `/app/`, complete the server workflow, and inspect the local `/static/style.css` response. Browser checks require an approved local browser tool.
4. To diagnose a decision-document link failure, run `tests/test_local_document_links.py`; headings produce lowercase hyphenated fragment identifiers.

## Limitations

- No installed browser, browser automation package, or browser executable was available. Therefore, this remediation does not provide browser-rendered responsive, keyboard traversal, screen-reader/AT, print, or offline/network-disabled evidence.
- The Markdown checker is deliberately narrow. It validates local Markdown links and fragments in the remediation decision documents only; it does not validate all repository documentation pages.
- `style.css` retains its pre-existing responsive strategy. The change supplies active-template linkage and markup hooks; no visual rendering claim is made.
- Full-suite execution is not repeated in this bounded remediation. Focused regressions passed; broader regressions remain governed by their existing evidence.
