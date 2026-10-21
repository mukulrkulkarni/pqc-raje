# Dynamic Page Elements Meeting Report

**Status:** Planning recommendation only. No page or application files changed.
**Evidence:** independent Engineering, Security, UI/UX, Code, and Technical Writer assessments; D1/D2 artifacts; current app/docs sources and tests.

## Collective recommendation

**Chosen:** native HTML and server-rendered interactions as the default.

- Use `<details>/<summary>` for optional explanatory content.
- Use a semantic ordered-list stepper with visible “Step N of 4”.
- Keep server-round-trip validation with actionable errors.
- Keep standard server-generated download links.
- Use semantic HTML math and plain selectable code blocks.
- Use CSS wrapping or stacked navigation only where a navigation shell exists.
- Keep `/app` free of JavaScript.

**Near-miss:** docs-only progressive JavaScript for optional theme, highlighting, or copy enhancements. It requires separate CSP, provenance, browser, accessibility, offline, and failure tests.

**Disqualified for `/app`:** client sorting/filtering, clipboard buttons, live validation, visual tabs, live progress, KaTeX/MathJax, and JavaScript accordions.

## Decision matrix

| Element | `/app` | Docs/website | Recommendation and control |
|---|---|---|---|
| Disclosure | Approve optional | Approve optional | Native details only; never hide required steps/errors. Test keyboard, print, no-CSS fallback. |
| Tabs | Reject | Defer | Use headings and anchors. Do not create radio controls that falsely present tab semantics. |
| Accordions | Conditional | Approve optional | Independent native details; preserve submitted form state server-side. |
| Sort/filter tables | Reject client-side | Defer | Keep canonical static order; use a server round trip only after demonstrated need. |
| Copy buttons | Reject | Optional later | Use selectable `<pre><code>` or read-only textarea. Test clipboard denial if added. |
| Live validation | Reject | Defer | Keep server validation, error summary, and server-rendered focus guidance. |
| Progress | Approve textual | Approve | Use visible Step N of 4; optional semantic `<ol>` with `aria-current`. No fake percentage. |
| Downloads | Approve current | Link to app | Standard links; show format and 30-minute expiry. Preserve token/cache controls. |
| Responsive navigation | Defer | Approve CSS wrapping | Avoid checkbox hamburger until browser/AT evidence exists. |
| Math | Approve semantic HTML | Approve semantic HTML | Reject KaTeX/MathJax. Test script-disabled and print readability. |

## Blocking findings

- `app/static/style.css` is not linked by active `app_*.html` templates. Do not claim active styling or responsive behavior until corrected and tested.
- Existing UI tests focus on legacy templates and do not fully cover active `/app` templates.
- No browser keyboard, assistive-technology, network-disabled offline, or route-scoped CSP execution was verified in this meeting.
- Docs JavaScript is separately governed by `CSP_DOCS`; it requires provenance, failure, offline, and accessibility controls.

## Required controls and tests

Positive, negative, and edge evidence must cover: disclosure keyboard use; malformed routes/fragments/assets; expired/replaced downloads; invalid criteria/matrix; long labels and narrow widths; ties and empty tables; semantic math with scripts disabled; route-scoped CSP; and network-disabled local navigation. Add CSP assertions for `/app` and `/docs`, active-template UI tests, Markdown/fragment link checks, and browser/AT evidence before material layout approval.

## Audience recommendations

**Technical:** adopt native controls, isolate app/docs JavaScript policy, fix stylesheet linkage, add route/CSP/UI/link/offline tests, and document source ownership.

**Executive:** proceed with low-risk native interaction patterns. Defer rich widgets until user value justifies their accessibility, security, and maintenance cost. Do not publish material layout claims before browser/AT evidence.

## Stop conditions

Stop dynamic-element approval if the stylesheet gap remains, route CSP is untested, browser/AT evidence is absent for a material layout change, or any element requires JavaScript in `/app`.
