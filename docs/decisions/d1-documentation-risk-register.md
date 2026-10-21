# D1 documentation risk register

**Scope:** Documentation planning only at revision `b5a1e9d2bd2abf1829aa6eca3fac94183908d847`.  
**Status scale:** Blocker = drafting/publication must stop; High = resolve before review approval; Medium = track within stage; Low = monitor.

| ID | Risk | Severity | Evidence | Consequence | Required mitigation / acceptance evidence | Owner / gate |
|---|---|---:|---|---|---|---|
| D1-R01 | No root README or authoritative entry point | Blocker | No tracked project-root `README*` | Users cannot reliably install, launch, or choose CLI/web docs | PI-approved README structure with prerequisites, install, launch, first success, limits, and doc map | Writer → PI |
| D1-R02 | Historical target language can be published as current behavior | Blocker | Requirements and design report predate chunks 2A–2E | False statements about missing or future features | Current/target labels backed by pinned source and focused tests | Writer + Engineering Critic |
| D1-R03 | Four-phase template identity is ambiguous | High | No separately named template found; supplied context defines four workflow steps | Writer may structure the wrong onboarding model | PI confirms the audit’s four-step interpretation before drafting | PI |
| D1-R04 | CLI and web contract duplication will drift | High | Contracts repeated in requirements, chunk notes, tutorials, and source | Conflicting limits, formats, defaults, or equations | One shared contract reference; task guides link to it | Writer + Engineering Critic |
| D1-R05 | `.npz` target/current mismatch | High | Requirements mention `.npz`; current workflow evidence emphasizes `.csv`/`.npy` | Users receive unsupported instructions | Document executable current behavior or authorize implementation separately | Engineering Critic |
| D1-R06 | Generated website and source ownership are unclear | High | `docs/modules/` copied into nested `website/` routes | Hand edits diverge or are overwritten | Declare source-of-truth and build-only generated paths; build check passes | Writer + PI |
| D1-R07 | Historical snapshots pollute search and citation | Medium | Multiple `docs/design/**/snapshot/` trees | Stale science/layout gets cited as current | Exclude snapshots from user nav/search and label historical | Writer |
| D1-R08 | Local links lack one cross-format integrity gate | High | Website tests exist; no D1 Markdown/fragment sweep | Broken Markdown, route, fragment, or asset links ship | Test Markdown links, static relative links, Flask routes, fragments, and assets | Engineering Critic |
| D1-R09 | Missing-target regression can regress during navigation changes | High | Route allow-lists and 404 tests currently exist | Broken or unsafe routes expose errors | Preserve positive/negative module, tutorial, asset, and traversal tests | Engineering Critic |
| D1-R10 | Accessibility claims exceed executed evidence | Blocker | Static tests/rationale only; no D1 browser or AT run | Misleading keyboard/focus/reflow claims | Execute keyboard traversal, visible focus, zoom/reflow, names/roles, and no-trap checks | UI/UX review |
| D1-R11 | Math enhancement failure is undocumented | High | App requires semantic math; docs tutorials load local scripts | Equations or code context may degrade silently | Disable/fail local scripts and verify meaningful semantic fallback | Scientific + UI/UX |
| D1-R12 | Offline claim exceeds static inspection | High | Local asset/static URL tests; no network-disabled browser execution | Hidden external dependency or broken offline navigation | Network-disabled docs/app smoke test; capture exact routes and assets | Engineering Critic |
| D1-R13 | Malformed-input documentation lacks paired recovery paths | High | Tests cover failures; user guides do not consolidate them | Users cannot correct criteria/CSV/limits efficiently | Each input section includes valid, invalid, message, and correction examples | Writer + Engineering Critic |
| D1-R14 | Numeric example outputs could be invented or stale | Blocker | Requirements mark inputs illustrative; outputs not computed there | Scientific misinformation | Generate examples at pinned revision; record command/input/hash and reviewer verification | Scientific Critic |
| D1-R15 | Performance results lose environment and uncertainty context | High | Benchmark artifact/model notes are implementation-oriented | Users treat estimate as guarantee | Publish date, hardware, tested grid, p95 method, threshold, timeout, and limitations | Engineering + Scientific |
| D1-R16 | Cache/download lifecycle surprises users | High | Latest-only, replacement, TTL, restart, session binding are scattered | Lost downloads and confusing token failures | One lifecycle diagram/table and recovery instructions | Writer + Security review |
| D1-R17 | Static site “App” route is confused with live Flask `/app/` | Medium | `website/app/index.html` versus application route | Users open explanation instead of workflow | Distinct labels: “App guide” and “Launch local app” | Writer + UI/UX |
| D1-R18 | Docs JavaScript policy is confused with app no-JavaScript policy | High | Module tutorials use local scripts; app forbids JavaScript | Incorrect CSP/offline/security claims | Explicit policy matrix for app, served docs, and static website | Engineering + Security |
| D1-R19 | Test-count claims confuse collection, focused execution, and historical full pass | High | D1: 904 collected; 273 passed; prior notes: 904 passed | Inflated verification claim | Report command, scope, revision, result, and whether current or historical | Engineering Critic |
| D1-R20 | Debugging remains tool-centric rather than symptom-centric | Medium | Existing debugging runbook lacks workflow error map | High support burden | Index errors by criteria, matrix, preview, feasibility, compute, download, restart | Writer |
| D1-R21 | Source traceability decays after implementation changes | High | Strong chunk notes, no public traceability convention | Docs become stale without detection | Per-page “verified against” metadata or maintained evidence matrix | PI + Writer |
| D1-R22 | Workflow route module complexity obscures ownership | Medium | `app/routes/workflow.py` statically measured at 258 lines | Docs oversimplify boundaries; maintainers miss coupled behavior | Module/route responsibility map; no D1 refactor | Engineering Critic |
| D1-R23 | Companion website build success is mistaken for browser quality | Medium | `build_website.py --check` exits 0 | Rendering, keyboard, and responsive defects remain | Separate build, static-link, browser, and accessibility gates | UI/UX + Engineering |
| D1-R24 | Security details expose internals or omit boundaries | Medium | Token/session/cache rationale is detailed in decisions/tests | Docs either leak unnecessary detail or understate controls | Publish threat boundary and user behavior, not secrets/token examples | Security review |
| D1-R25 | Unsupported production/multi-worker usage is implied | High | Current cache is process-memory/single-worker/local-only | Data loss or inconsistent downloads | Prominent support boundary in README, app guide, operations, limitations | PI + Engineering |
| D1-R26 | Delegation limitation disappears from audit trail | Low | Intended research-agent ID unavailable | Readers assume independent research review | Preserve local-fallback statement and request normal stage reviews | PI |
| D1-R27 | D1 checkpoint or artifacts are committed without PI verification | Medium | Fallback explicitly forbids commit | Governance breach | PI verifies artifacts, updates acceptance state, commits focused paths | PI |

## Publication stop conditions

1. Stop if PI has not approved the writer structure and authority map.
2. Stop if current behavior lacks pinned source and positive/negative executable evidence.
3. Stop if scientific examples, keyboard behavior, math fallback, offline behavior, or local links remain asserted without relevant execution.
4. Stop if generated-file ownership or route placement remains ambiguous.
5. Stop if material navigation/layout changes lack UI/UX approval.

## Residual risks after D1

- D1 does not prove browser accessibility, offline runtime behavior, or every local link.
- D1 does not rerun the full 904-test suite; it executed a bounded 273-test subset.
- D1 does not resolve product/documentation mismatches; it identifies them for the writer plan and later review.
- D1 does not authorize tutorial drafting, page edits, application changes, deployment, or commits.
