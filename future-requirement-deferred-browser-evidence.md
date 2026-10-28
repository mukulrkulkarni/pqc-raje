# Future Requirement: Deferred Browser Evidence

**Status:** Deferred, non-blocking for v0.1 and current documentation work.

## Purpose

This file records browser evidence that remains useful for a future verification chunk. It is not a release claim and does not state that these checks passed.

## Required future checks

Run the local application and companion website in a supported browser. Record the browser, version, operating system, revision, viewport, zoom level, and commands.

### Browser rendering

- Load `/app/`.
- Complete criteria entry, matrix entry, preview, confirmation, compute, and download.
- Verify the criteria-card layout at desktop and narrow widths.

### Keyboard and focus

- Traverse every control with the keyboard.
- Verify logical tab order.
- Verify visible focus.
- Verify Enter and Space activation.
- Verify no keyboard trap.
- Verify error recovery and focus guidance.

### Zoom and responsive layout

- Test normal scale.
- Test 200% zoom.
- Test 400% zoom where practical.
- Test narrow viewport reflow.
- Verify no critical content clips or overlaps.

### Offline and local-only behavior

- Disable network access after the local services start.
- Verify local app pages and local documentation assets continue to work.
- Record any expected limitation for generated links or external services.

### Accessibility

- Run available automated accessibility checks.
- Verify semantic headings, labels, tables, landmarks, and status messages.
- Screen-reader behavior remains a separate manual test unless a user performs it.

### Performance observation

- Record page load and compute observations separately from the existing runtime feasibility model.
- Do not convert a browser observation into a production performance guarantee.

## Evidence format

For each check, record:

- exact command or manual steps;
- revision and environment;
- expected result;
- actual result;
- screenshots or DOM/accessibility output where available;
- positive, negative, and edge cases;
- failures and remediation;
- remaining limitations.

## Current known limitations

The current project has verified native DOM script absence, stylesheet presence, and limited screenshot evidence. It has not verified browser reflow, zoom, keyboard traversal, offline navigation, screen-reader behavior, or browser load performance.

Future agents must not claim these checks passed without new evidence. Remote Git operations remain user-only.
