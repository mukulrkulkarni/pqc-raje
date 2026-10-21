# Web-App Pre-Read: Gap and Contradiction Register

**Source:** `attachments/web-app-requirements.txt`
**Purpose:** Prepare a future design meeting. This register does not authorize implementation.
**Status:** Pre-read draft; meeting approval remains separate.

## Gap register

| ID | Requirement | Current evidence | Gap or contradiction | Risk | Proposed owner | Decision needed |
|---|---|---|---|---|---|---|
| G-01 | Web must run ELECTRE III ranking and expose scores. | `app/routes/compute.py` starts a placeholder job and returns status; it does not call `compute_ranking`. | Web compute orchestration is incomplete. | Scientific, product | Code Agent | Define first executable compute slice. |
| G-02 | Preview must validate values and schema. | `app/services/preview.py` loads and summarizes a matrix; it reports NaN/Inf flags but does not enforce the full web contract. | Header, missing-cell, score-bound, row-limit, and criteria checks need one contract. | Security, scientific | Engineering Critic | Lock validation order and errors. |
| G-03 | Web and CLI must use the same core. | `electre3/ranking.py` provides `compute_ranking`; web routes do not call it. | Shared-core integration is not complete. | Correctness | Code Agent | Require one adapter used by both paths. |
| G-04 | Headered and headerless CSV policies. | `electre3/data.py` uses numeric loading; `scripts/convert_matrix_csv.py` supports conversion. | Web parser and identifier mapping are not implemented as specified. | UX, data integrity | Code Agent + UI/UX | Choose one canonical parsed-input model. |
| G-05 | Missing CSV values require checkbox approval and replacement. | No evidence in current preview route for this policy. | UI control, value range, default `0`, and audit display are unspecified in code. | Scientific, UX | UI/UX + Engineering | Confirm wording and validation behavior. |
| G-06 | Criteria list has required fields and maximum eight. | `app/services/security.py` checks list and numeric threshold fields but does not require `name`/`maximize` or enforce eight. | Web validator is incomplete. | Scientific, security | Security + Scientific | Add strict web-only schema validator. |
| G-07 | Weights and score normalization. | `electre3/ranking.py` normalizes positive weights; current validators do not enforce score bounds `[0,1]`. | Requirements document asks for web restrictions not present in current implementation. | Scientific | Scientific Critic | Confirm whether these are mandatory target rules. |
| G-08 | No NxN persistence and O(N) accumulation. | `electre3/ranking.py` computes blocks; `NetFlowAccumulator` stores O(N) flow vectors. | Web adapter must preserve this property. | Performance | Engineering Critic | Add memory and block-size tests. |
| G-09 | Byte-identical CLI/web output. | CLI currently saves ranking indices with `np.save`; web output serializers do not exist. | Canonical result schema and serializers are absent. | Reproducibility | Engineering Critic | Define supported artifact formats first. |
| G-10 | Bounded in-memory result cache. | No result-cache implementation is evidenced in current routes. | Token, TTL, eviction, single-worker, and restart behavior need implementation. | Security, operations | Security Lead + Code Agent | Confirm cache limits and token binding. |
| G-11 | No JavaScript for app UX. | `CSP_APP` omits `script-src`; docs CSP allows `script-src 'self'`; existing tutorial assets include `theme.js`. | “No JS” applies to app, docs, or both? | UX, accessibility | UI/UX + Security | Decide scope explicitly. |
| G-12 | KaTeX for mathematical content. | No KaTeX integration is evidenced. KaTeX client rendering normally requires JavaScript. | KaTeX conflicts with strict no-JS unless pre-rendered at build time or replaced. | Technical, UX | UI/UX + Engineering | Select rendering strategy. |
| G-13 | Local-only and upload containment. | `create_app` sets `MAX_CONTENT_LENGTH`; security service uses a registry and upload paths. | Row limits, lifecycle deletion, and memory-only policy are not fully evidenced. | Security | Security Lead | Set byte/row limits and lifecycle tests. |
| G-14 | Existing route workflow. | Current routes are `/preview/<upload_id>`, `/preview/<upload_id>/confirm`, `/compute/start`, `/compute/status/<job_id>`. | Requirements describe `/`, `/confirm-inputs`, `/preview`, `/compute`. | UX, integration | Code Agent | Choose migration or retain API routes. |

## Contradiction register and escalation

| ID | Contradiction | Evidence | Escalation path |
|---|---|---|---|
| C-01 | “No JavaScript” versus KaTeX. | Requirements prohibit JS; KaTeX browser rendering normally uses JS. | UI/UX proposes options; Security checks CSP/privacy; Engineering checks build/test cost; user decides. |
| C-02 | Web target requires normalized scores/weights sum 1, while current core normalizes positive weights and lacks score bounds. | `electre3/ranking.py`, `electre3/config.py`, requirements source. | Scientific Critic verifies the mathematical contract; Code Agent estimates adapter scope; user resolves product policy. |
| C-03 | Requirements describe a server-rendered four-step flow; current app exposes JSON upload/preview/compute routes and placeholder jobs. | `app/routes/*.py`, requirements source. | Engineering Critic maps routes; UI/UX selects user flow; unresolved product choice returns to user. |
| C-04 | Requirements prohibit signed-cookie result storage, but existing app uses Flask sessions for upload confirmation. | `app/routes/preview.py`, requirements source. | Security Lead defines what session metadata is allowed; Code Agent separates confirmation metadata from result bytes. |

## Stop and escalation rules

- Security Lead blocks progress when a storage, path, token, CSP, or local-only decision lacks a testable contract.
- Scientific Critic blocks progress when equations, thresholds, direction handling, score policy, or CLI/web equivalence is ambiguous.
- Engineering Critic blocks progress when a requirement lacks an owner, acceptance test, or maintainable integration path.
- UI/UX blocks the UX recommendation when the chosen math renderer or no-JS scope harms keyboard access, error recovery, or comprehension.
- Any unresolved cross-domain contradiction becomes a user decision. It is not silently resolved by the PI.
