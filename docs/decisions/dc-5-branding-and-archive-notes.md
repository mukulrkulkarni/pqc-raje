# DC5 branding verification and preserved-reference archive

**Evidence date:** 2026-10-22
**Scope:** Documentation evidence only. No browser-rendered verification claim is made.

## Brand source and static verification

Authoritative source: `skills/brand-styling-framework/MK-TII-brand-template.json`, version `1.0.0`.

| Template requirement | Static evidence | Status |
| --- | --- | --- |
| Preferred font: Arial; fallback: Arial, sans-serif | `app/static/style.css`: `--font-sans: Arial, sans-serif` | Verified statically |
| Primary purple `#6400FF` | `--color-primary: #6400ff`; selected card border and heading use it | Verified statically |
| Primary navy `#253746` | `--color-text: #253746` | Verified statically |
| Primary gray `#75787B` | Template reviewed; application uses its own muted gray token | Not a one-to-one token assertion |
| Primary aqua `#7EDDD3` | `--color-accent: #7eddd3`; selected-card gradient includes `rgba(126, 221, 211, 0.28)` | Verified statically |
| Contrast check required | DC4.5 static test calculates card foreground/background non-text contrast ratios at least 3:1 | Verified by `tests/test_dc45_criteria_cards.py` |

The brand template requests contrast checks before delivery. The listed automated static test covers two card-state non-text contrast values. It does not establish all rendered text, browser, or device contrast outcomes.

## Deferred browser and accessibility limitations

The following remain **deferred limitations**, not release claims:

- Browser-rendered visual verification.
- Assistive-technology behavior.
- Keyboard traversal in a browser.
- Zoom behavior.
- Responsive reflow behavior.
- Offline behavior.

Source inspection and Flask test-client evidence show semantic markup, visible focus CSS, no JavaScript in the application route, and responsive CSS declarations. Those facts do not replace the deferred browser evidence.

## Preserved-reference archive

The following pre-existing untracked references were moved without deletion to `out/archive/dc-5-preserved-references/`:

| Archived path | Original path | Provenance and classification | Safe-to-archive basis |
| --- | --- | --- | --- |
| `clipboard-2026-10-22_05-35-51.png` | `attachments/clipboard-2026-10-22_05-35-51.png` | 102,500-byte PNG screenshot; tool description identifies documentation/mockup content; untracked pre-change | User explicitly authorized preserved mockup/reference archiving; content inspected locally; no executable content |
| `dc-4-5-single-card-selected.svg` | `out/dc-4-5-single-card-selected.svg` | 2,242-byte static SVG reference showing selected card styling; untracked pre-change | User explicitly authorized archive; inspected XML contains only SVG shapes/text |
| `dc-4-5-single-card-unselected.svg` | `out/dc-4-5-single-card-unselected.svg` | 2,175-byte static SVG reference showing unselected card styling; untracked pre-change | User explicitly authorized archive; inspected XML contains only SVG shapes/text |

No other attachment was archived. Existing tracked evidence remains untouched. Archive movement intentionally preserves these artifacts as untracked files; it does not make them reviewed product assets or release evidence.

## Archive verification

Archive paths were created before movement. The original three paths were untracked in the pre-change `git status --short`; the archive contains the same three preserved artifacts. The DC5 focused commit includes documentation and archive artifacts only after review records are current.
