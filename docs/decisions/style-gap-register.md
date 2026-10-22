# Documentation Style Gap Register

**Audit revision:** `1f1c9395fb4fb591b41d473edf6e75b0a53782d0`  
**Status:** Open register for a later approved correction chunk.  
**Browser note:** Browser-rendered checks are deferred and non-blocking; static acceptance does not prove browser behavior.

## Labels

- **Current:** observed at the pinned revision.
- **Target:** required MK-TII styling or integrity rule.
- **Static acceptance:** executable evidence required before correction review.

| ID | Priority | Evidence paths | Current | Target | Static acceptance |
|---|---|---|---|---|---|
| SG-01 | High | `docs/modules/index.html`, `docs/modules/*_tutorial_side_by_side.html`, `website/modules/index.html` | Blue/slate `system-ui` visual system | Arial and MK-TII purple/teal/text/surface/border tokens | Token tests cover every owned HTML family; no content diff |
| SG-02 | High | `scripts/build_website.py`, generated `website/modules/*/tutorial/index.html` | Injected nav uses inline slate/system-ui fallbacks | Shared MK-TII nav contract with consistent current-page semantics | Generator positive test; malformed/missing-nav negative tests; idempotent rebuild |
| SG-03 | High | `website/modules/*/tutorial/index.html`, `website/modules/assets/*` | Generated copies are easy to hand-edit accidentally | Source-first changes under `docs/modules`; generated outputs rebuilt only | Test maps each output to an existing source and compares normalized generated content |
| SG-04 | High | `website/modules/*/index.html`, `scripts/build_website.py` | Existing landing files are hybrid authored/generated pages | Explicit source ownership and deterministic generation policy | Missing source/target test; rebuild leaves no unexpected diff |
| SG-05 | High | Requested README/docs/website/app scope; `tests/test_local_document_links.py` | Link helper covers only two decision files | Repository-local href, fragment, asset, and route integrity for all changed surfaces | Positive full-scope crawl plus missing target/fragment negative fixtures |
| SG-06 | High | `docs/modules/assets/highlight.js`, tutorial `.row-head[role="button"]` | Enter/Space handling exists in source; execution is not shown | Preserve keyboard contract and native hash/link fallback | Executable JS/unit test for Enter/Space and missing target; browser execution remains deferred |
| SG-07 | High | `docs/GETTING_STARTED.html`, `README.md`, module prose | Semantic math works without a renderer; no explicit failure regression | Math meaning must survive absent/failed renderer and offline use | Static test rejects remote math assets and requires meaningful text/semantic math |
| SG-08 | Medium | `docs/modules/*.html`, `website/modules/*.html` | Separate 4/8/12/16/24/32px spacing and 10px radius vocabulary | Map shared rhythm to MK-TII spacing and 4/8px radii where layout permits | CSS token assertions and source snapshot review |
| SG-09 | Medium | `docs/GETTING_STARTED.html`, website indexes, module indexes, injected tutorial nav | Navigation labels match broadly; route forms and visual treatment vary | Consistent Getting Started/App/Tutorials order, labels, active state, and focus cues | Route-context parameterized tests for Flask and static website paths |
| SG-10 | Medium | `docs/modules/*_tutorial_side_by_side.html` | Dense cards/code panels are useful but visually detached from app | Retain split layout while mapping surfaces, borders, headings, code accents, and callouts | Required class/token assertions; tutorial content and IDs unchanged |
| SG-11 | Medium | `website/modules/*/index.html` | Sparse stubs lack MK-TII hierarchy, cards, code, and callout vocabulary | Use MK-TII container, heading, action, card, and status patterns | Static structure/style tests; all links resolve |
| SG-12 | Medium | `docs/modules/assets/theme.js`, module pages | Theme control is optional JS; base light theme remains | Preserve readable default and no-JS content; avoid JS at app boundary | No-script app test; tutorial no-JS structural test; local asset test |
| SG-13 | Medium | `website/_includes/primary-nav.html`, `scripts/build_website.py` | Include exists but generator does not consume it | One authoritative nav source or explicit deletion/migration plan | Test proves include consumption or removes all stale references |
| SG-14 | Medium | Inline `<style>` blocks across docs and website | Repeated tokens increase drift and review size | Centralize shared CSS where route/offline constraints allow | Local stylesheet resolution test and external-asset rejection |
| SG-15 | Low | `README.md`, `docs/tutorials/*.md`, `docs/runbook/*.md` | Styling depends on the Markdown renderer | Keep portable semantic Markdown; style only an owned renderer | Markdown lint/link tests; no embedded remote CSS/scripts |
| SG-16 | Low | Tutorial CSS at `@media (max-width:768px)` | Sidebar disappears; browser usability is unverified | Ensure visible in-content navigation and readable single-column flow | Static fallback assertions; browser reflow remains deferred |
| SG-17 | Low | Tables in `app/static/style.css` and app preview/results templates | Responsive table contract exists in app, not uniformly documented | Reuse semantic table wrapper/header/data-label rules when docs add tables | Scoped headers and labels tests on changed tables |
| SG-18 | Low | Callouts across Getting Started, tutorials, and app | `.note`, `.callout`, `.warning-box` differ | Normalize info/warning callout tokens; retain explicit textual labels | Static class/token checks and non-color-label assertions |

## Correction guardrails

- Do not alter formulas, sample outputs, route claims, release status, or algorithm descriptions during visual work.
- Do not add JavaScript to `app/templates/app_input.html`, `app_matrix.html`, `app_preview.html`, or `app_results.html`.
- Do not hand-edit generated tutorial pages or copied assets.
- Keep all fonts, scripts, styles, and images local for offline operation.
- Preserve tutorial IDs, fragment targets, semantic landmarks, scoped headers, and no-JS content order.

## Review gate

A correction remains **NEEDS WORK** if any High gap lacks executable positive, negative, and edge evidence. Browser-deferred items remain limitations, not blockers, unless the user opens a browser-evidence chunk.
