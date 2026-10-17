# Engineering review — Discordance scoped gates (Phase 5)

## Decision
**APPROVED**

## Scope / invariants checked
- Tutorial-only change + tests retargeted; algorithms/shared JS/routes expected unchanged.
- Verified tutorial content contracts, example-vs-table parity, p=v edges, source excerpt parity, local/served links, and security/CSP retention.

## Evidence (pinned manifest + live)
- Manifest pins (HEAD b88f7c1): `docs/design/committee_phase5/discordance_review/manifest.json`.
- Live files inspected:
  - `docs/modules/discordance_tutorial_side_by_side.html`
  - `tests/test_discordance_deep.py`
  - `tests/test_module_docs.py` (static HTML/security checks)

## Executed tests (actual run)
- Ran: `pytest -q tests/test_discordance_deep.py`
- Result: pass (21 tests) — see shell output in review log.

## Minimal scope / change isolation
- Engineering review limited to the tutorial HTML + docs tests.
- No evidence gathered here about changes to `electre3/*` algorithms, shared JS, or route wiring beyond the checks below.

## Required gates — results
### 1) Meaningful positive + negative executable tests
- Positive: `test_execute_usage_and_compare_visible_table` executes tutorial code block and matches rendered table values.
- Positive: `test_code_excerpts_match_actual_source` enforces excerpt parity with `electre3/discordance.py` line ranges.
- Negative: `test_invalid_links_rejected` blocks external/nonlocal/escaping links.
- Negative: `test_lowlevel_nonfinite_and_mismatch_are_not_validation` covers NaN/±inf behavior + shape mismatch + silent broadcast warning.

### 2) Extracted example-vs-table checks
- `test_execute_usage_and_compare_visible_table` parses HTML table `#scenario-results`, evaluates Fractions (e.g. 5/6, 7/18), and compares against computed `discordance`, `global_concordance`, `credibility`.

### 3) p=v edges / veto-first precedence
- `test_equal_threshold_veto_first` asserts p=v returns 1 at equality and 0 above; runs under `np.errstate(divide='raise', invalid='raise')`.
- Tutorial text explicitly states: “At p=v, the veto-first branch wins at equality: diff=-p=-v gives 1.”

### 4) Source excerpt parity
- Enforced by `test_code_excerpts_match_actual_source` against `electre3/discordance.py` for rows R1–R5.

### 5) Local file links + served link integrity (offline behavior)
- `check_links()` enforces: no scheme/netloc, no path escape, target files exist, fragment IDs exist.
- `test_local_links_and_served_assets` serves tutorial via Flask app (`create_app({'TESTING':True})`) and asserts 200 for linked docs and assets.

### 6) Security coverage retained after scaffold retarget
- Tutorial uses strict CSP meta: `default-src 'none'` with `script-src 'self'`.
- `test_local_links_and_served_assets` asserts CSP header contains `script-src 'self'` when served.
- `tests/test_module_docs.py` contains negative patterns to reject external references and bans `unsafe-eval` in CSP (static checks).

## Limitations / non-claims
- Browser rendering, keyboard navigation behavior, and layout width were not manually verified (no browser runner).
- Snapshot folder under `docs/design/committee_phase5/discordance_review/snapshot/` is empty in this workspace, so pinned snapshot hash verification could not be performed.

## Introduced vs pre-existing
- Introduced/retargeted: deep tutorial tests validate table parity, links, and p=v edge semantics.
- Pre-existing: low-level math functions rely on upstream validation; tests document this contract explicitly.
