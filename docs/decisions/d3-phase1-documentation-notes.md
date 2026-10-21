# D3 Phase 1 Documentation Notes

**Status:** Draft stage checkpoint. No user-facing pages changed.

## Current evidence

- Draft: `docs/decisions/d3-phase1-content-draft.md`.
- Engineering Critic: approved after corrections.
- Scientific Critic: approved after scenario alignment.
- UI/UX gate: not required yet because no page layout or navigation changed.
- PI acceptance: deferred until D3 stage end.

## Verified source paths

- CLI: `electre3/cli.py`, `electre3/cli_run.py`.
- Shared validation: `electre3/shared.py`.
- Converter: `scripts/convert_matrix_csv.py`.
- Local runner: `scripts/dev_local.py`.
- Web workflow: `app/routes/workflow.py`, `app/templates/app_*.html`.
- Results/cache: `electre3/serialization.py`, `app/services/result_cache.py`.
- Example: `examples/assets_priority/`.

## Evidence requirements before publication

Run every command verbatim on the pinned revision. Record command, exit status, actual output, source path, environment, and limitation. Cover positive, negative, and edge cases across unit, integration, scientific, security, UI/accessibility, performance, serialization/cache, end-to-end, links, and offline behavior.

Do not claim browser reflow, keyboard, offline, or screen-reader evidence. Current browser evidence verifies no app scripts, stylesheet presence, and one screenshot only.

## Current versus planned

The draft is not a published README, Getting Started page, or website page. Code Agent placement and independent reproducibility remain later D3 activities. No install command is published until packaging evidence is verified.
