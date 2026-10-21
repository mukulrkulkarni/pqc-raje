# D2 Executive Summary — Documentation Structure Plan

**Status:** Plan only. No pages are drafted.

This plan creates one documentation system for four surfaces: CLI, modules, local `/app`, and the companion website. It uses four phases: **Working in 10 minutes**, **Build a real thing**, **Mental model**, and **Reference**. One realistic Asset ID/IP scenario will run through every surface.

The plan addresses D1 findings. Existing documentation has strong scientific depth, offline assets, accessibility rationale, and broad test evidence. It lacks one authoritative entry point, one current CLI/web journey, clear generated-page ownership, systematic Markdown and route-link checks, browser accessibility evidence, and network-disabled offline evidence.

The proposed deliverables are:

- Root README with prerequisites, installation, first success, launch paths, and documentation map.
- Getting Started page for the Phase 1 success path.
- CLI guide with converter workflow, flags, output semantics, limits, and debugging.
- Web guide for criteria, matrix mapping, preview, validation, compute, results, and recovery.
- Concepts guide for ELECTRE III, blockwise processing, net flow, ties, and scientific limits.
- Module/API reference with concise entries and tutorial backlinks.
- Operations and testing runbooks.
- Companion website navigation and links without duplicating numeric contracts.

The main benefit is lower drift. One authority map and one contract reference prevent conflicting limits, commands, and claims. A shared scenario improves learning and makes CLI/web comparison practical. Clear Markdown, semantic HTML, and generated-website ownership reduce maintenance risk.

Key risks are stale current-versus-target wording, unsupported numeric examples, unclear generated-page ownership, and unverified browser/offline behavior. No documentation page will publish an unsupported claim. Numeric examples must have reproducible evidence. Browser accessibility, offline behavior, and local-link checks must be executed before release.

Governance is strict. PI must approve this structure before drafting. Each page batch requires Technical Writer authorship, Scientific Critic approval, Engineering Critic approval, and UI/UX approval for material layout or navigation changes. Code Agent places approved content into pages and adds documentation tests. Each batch requires positive, negative, and edge evidence, a checkpoint, auxiliary notes, a focused commit, and a clean worktree.

The plan does not authorize page drafting. It first requires PI approval of the authority map, phase boundaries, page ownership, and evidence plan.