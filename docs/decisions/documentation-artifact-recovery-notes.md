# Documentation artifact recovery notes

**Date:** 2026-10-28  
**Status:** verified recovery; release records corrected  
**Scope:** D4 fixtures, D5 placed tutorial, D6 reference/debugging content, and D8/final availability claims. This record does not create or publish new documentation content.

## Provenance inventory and availability

| Area | Historical authority | Authoritative paths | Before recovery | After recovery | Label |
|---|---|---|---|---|---|
| D4 fixtures | `2c38c7c` | `examples/d4_phase2/`, `out/d4-fixture-evidence.json`, `tests/d4_checks/` | Present in `HEAD`; availability had not been rechecked before final records. | Present, byte-preserved from `HEAD`; deterministic evidence regenerated. | current |
| D5 placed tutorial | `aa85c5c` | `docs/modules/ranking_tutorial_side_by_side.html`, `website/modules/ranking/tutorial/index.html` | Present in `HEAD`; availability had not been rechecked before final records. | Source and generated tutorial present; generated output rebuild is unchanged. | current |
| D6 reference/debugging | `a90f274` | `docs/tutorials/cli_quickstart.md`, `docs/runbook/debugging.md`, `docs/decisions/d6-placement-*.md` | Present in `HEAD`; availability had not been rechecked before final records. | Present in repository user-facing locations; no companion-website reference page is claimed. | current / planned hosting |
| Static repository references | D7/D8 records | `/reference/index.html` and repository files | Static index is current; repository-hosted `/docs/...` paths are absent. | Unchanged; hosted repository references remain unavailable. | planned |

The requested historical checkout and website regeneration found no missing committed D4, D5, or D6 artifact in `HEAD` `21a587b`. Therefore, no historical content was copied over newer content and no artifact was invented. The correction is to qualify prior release wording: it relied on historical evidence and did not explicitly state this recovery re-verification.

## Evidence

- **Positive:** D4 fixture evidence generator and D4 checks run against `examples/d4_phase2/`; D5 source/output checks and website build establish source-to-output parity; D6 placement checks establish the quickstart/runbook paths and their required reference content.
- **Negative:** malformed threshold order returns nonzero with `p must be >= q`; the CLI rejects block size `0`; local-link tests retain missing-file and missing-fragment rejection.
- **Edge:** exact threshold equality retains branch priority; exact/near-tie D4 fixtures remain covered; local-link audit accepts external and anchor-only links without treating them as local files.
- **Independent reproduction:** website build and link audit run in separate commands after tests. The recovery commands use only local committed sources and make no remote request.

## Review record

- **Scientific review:** Accepted the D4 fixture and D5/D6 wording checks; no mathematical claim or data changed.
- **Engineering review:** Accepted committed-source provenance, deterministic build behavior, local link checks, and negative validation evidence.
- **UI/UX review:** Accepted current/planned labels and user-facing D6 placement; browser rendering, keyboard, zoom, reflow, offline, load, screen-reader, and assistive-technology evidence remain deferred and non-blocking.

## Limitations

`v0.1` and `v0.2.0` tags remain unchanged. Browser evidence remains deferred and non-blocking. No remote Git operation occurred; upstream actions remain user-only.
