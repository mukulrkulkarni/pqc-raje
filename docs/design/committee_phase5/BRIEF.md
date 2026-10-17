# Phase 5 approved committee brief
Baseline: 74d0ae0 recovery checkpoint; original tutorial/code baseline ea0e562. User approved committee and reaffirmed ten-phase plan on 2026-10-16. Phases 1–4 historically complete, phase 5 active, 6–10 pending. No production edits authorized by this design step.

## Roles and bounded work
Scientific Critic: inspect implementation and current concordance tutorial; propose teaching meta-template and accurate shared sample. UI/UX: use that content to build 2–3 visual alternatives, not production changes. PI: consolidate evidence and choices. One scientific cross-review of resulting content, not open-ended retries. Approved planning estimate: 20,000–35,000 total tokens, provisional USD 1–4 with unverified pricing, 10–20 minutes. Stop on failure or material expansion; do not change model or add agents silently.

## User feedback (carry into every proposal)
- Explicitly explain a and b are both objects (IP addresses, items, etc.), not criteria. Explain the directional assertion a outranks b and distinguish it from b outranks a.
- B1 and B2 remain confusing: explain row/column comparison groups, not spreadsheet field groups. C counts criteria; N counts all objects. Avoid symbol collisions with global concordance C(a,b).
- Explain why diff has axes (B1,B2,C), including [[[d1,d2,d3]]] for one row object, one column object, three criteria. Explain two objects generate two distinct directed non-self comparisons.
- Simplify language while retaining graduate-level accuracy. Avoid undefined abbreviations like alts.
- Notation block wastes space. Compare N1: notation BEFORE I/O Summary; N2: notation AFTER I/O Summary. Both are layout variants, not symbols.
- Build meta-template: block/header name, content style (text/math/balanced/code), learning objective, prerequisites, default visibility.
- Include a compact collapsible worked example consistent across preliminaries and module content. Do not reject verified numeric results merely because they are numeric; label illustrative inputs and calculate examples from real code where possible.

## Preserve agreed design and functions
Layout2 code-dominant rows; roughly 60 code columns at 1366px; neutral near-white dark-mode non-code text, slightly increased text size; strong green Variant B selection with non-color cue; local theme controls; keyboard interaction; sidebar labels/progress; selection aligned to sidebar R1 baseline. Approved Option3 facts and borderless details. Code colors unchanged.
No external assets/network requests. Mathematical content outside code should use readable math markup with safe local fallback: rendering must not be required to read a formula. No new downloads for this design checkpoint. Local concept hyperlinks and collapsible bottom backlinks. New layouts are prototypes only; no production adoption before user visual approval.

## Deliverables
Content meta-template and notation contract; 2–3 HTML visual proposals using identical content for fair comparison, including light/dark views and expanded/collapsed example; concise rationale with Chosen/Near-miss/Disqualified; preservation checklist and known limitations. User chooses before implementation/gates/commits.

## Evidence and status
Read actual files, cite them. Do not infer runtime model from self-report. Read rationale-explainer before decisions. Report results/evidence, no hidden reasoning. Distinguish static inspection, calculated contrast, actual browser checks, and test execution. Each reviewer must state limitations. Honor standing policy: at most three numbered steps, five subtasks per step, no unapproved agent retries. No production files or tests changed by committee.
