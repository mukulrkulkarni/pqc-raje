# D1 documentation evidence matrix

**Revision:** `b5a1e9d2bd2abf1829aa6eca3fac94183908d847`  
**Legend:** Executed = command run during D1; Inspected = static source/revision review; Historical = recorded evidence not rerun in D1; Gap = no sufficient evidence.

| Topic / claim | Current evidence | Type | Assessment / limitation | Writer action |
|---|---|---|---|---|
| Repository implementation baseline | Git HEAD and `27c8c4b..b5a1e9d` diff | Executed + inspected | Pins audit to completed chunks 1–2E | Cite revision/date in contributor evidence. |
| Root onboarding | No tracked root README | Inspected | Critical discoverability gap | Create README plan; do not draft before PI approval. |
| Getting-started page | `docs/GETTING_STARTED.html`, `website/index.html` | Inspected | Strong presentation; incomplete current CLI/web journey | Reframe around installation and first success. |
| CLI quickstart | `docs/tutorials/cli_quickstart.md` | Inspected | Useful commands; weak navigation and strict-contract integration | Merge into CLI task guide. |
| Four-step workflow | `web-app-requirements.txt`; `attachments/web-app-requirements.txt` | Inspected | Available template context; no separately named four-phase template found | PI confirms interpretation before drafting. |
| Current web routes | `app/routes/workflow.py`, `app/__init__.py` | Inspected | `/app` workflow implemented; requirements still use target language | Document current behavior from source/tests. |
| Documentation routes | `app/routes/docs.py` | Inspected | Allow-listed modules/assets; sibling tutorial compatibility route | Publish route manifest and negative behavior. |
| Missing documentation targets | `tests/test_docs_routes.py` | Executed in 273-test subset | Controlled 404/path protection covered | Preserve negative route tests. |
| Companion navigation | `website/site-config.json`, generated pages | Inspected | Static `/app/index.html` differs from live `/app/` | Label static explanation versus live route. |
| Website build integrity | `python scripts/build_website.py --check` | Executed; exit 0 | Verifies generated output consistency, not browser behavior | Include in contributor gate. |
| Static website links/assets | `tests/test_website_static.py` | Executed in subset | Good relative/local asset checks; no Markdown link sweep | Add Markdown and fragment checker. |
| Offline-first static site | Website tests and local assets | Executed + inspected | Static evidence only; no network-disabled browser run | Add browser offline smoke test. |
| App no-JavaScript policy | Requirements, templates, app tests | Inspected + executed subset | App policy differs from docs JS policy | State split explicitly. |
| Math rendering | Semantic HTML requirement; module docs use local scripts | Inspected | No D1 renderer-failure execution | Test script-disabled/failure fallback and readable semantics. |
| Criteria contract | `electre3/shared.py`; chunk 1/2A notes; workflow tests | Inspected + executed subset | Strict required fields, 1–8, sum 1, finite thresholds | Use shared contract table once. |
| Malformed criteria | `tests/test_app_workflow.py`, `test_shared_contract.py` | Executed workflow subset; shared tests collected only in D1 | Relevant malformed web cases pass; not all shared tests rerun | Cite exact focused cases after writer-stage rerun. |
| Matrix validation | Workflow source/tests and chunk 2A notes | Inspected + executed subset | CSV/.npy behavior current; `.npz` target mismatch remains | Document current supported formats only. |
| Headered/headerless flow | `test_app_workflow.py`, chunk 2A notes | Executed + inspected | Positive and negative mapping evidence | Include paired examples. |
| Missing-value approval | Workflow source/tests | Executed + inspected | Explicit approval and bounded replacement documented | Add correction-oriented troubleshooting. |
| Scientific equations | Module tutorials, design reviews, core source | Inspected | Strong depth; stale snapshots complicate authority | Cite current source and current tests, not snapshots. |
| Threshold edge behavior | Deep scientific tests | Collected; historical completion notes | Not rerun in bounded D1 subset | Scientific reviewer reruns focused edges. |
| Ranking/net flow/ties | `ranking.py`, `accumulator.py`, module docs, chunk notes | Inspected | Raw net flow and tie caveat available | Consolidate interpretation in concepts/results. |
| Canonical serialization | `serialization.py`, chunk 2B notes, tests | Executed subset + inspected | Exact formats and negative non-finite behavior covered | Add format reference and byte-identity verification. |
| CLI/web byte identity | chunk 2B/2E notes and tests | Historical + inspected | D1 did not rerun entire equivalence suite | Rerun focused equivalence before publication claims. |
| Block-size invariance | ranking/serialization tests and notes | Historical + inspected | Strong recorded evidence; bounded subset excludes ranking deep suite | Scientific/engineering gate reruns focused matrix. |
| Runtime feasibility | `runtime.py`, benchmark JSON, chunk 2C notes, runtime tests | Executed subset + inspected | Model behavior tested; hardware/date limits must remain visible | Publish methodology and non-guarantee. |
| Hard timeout/no partial cache | runtime/workflow source and tests | Executed subset | Relevant behavior covered | Add user-facing rejection/recovery text. |
| Cache bounds/latest-only | `result_cache.py`, chunk 2D notes, tests | Executed subset | Replacement, expiry, checksums, malformed payload evidence | Document ephemeral single-worker semantics. |
| Token/download security | cache/workflow/security tests | Executed subset | Unknown/malformed/session and exact bytes covered | Explain without exposing token internals. |
| Restart invalidation | Architecture and notes; relevant tests | Inspected/historical | Process-memory implication clear; D1 did not restart a process | Add explicit limitation and stage test. |
| Accessibility semantics | templates, UI rationale, static tests | Inspected + executed subset | Labels/structure evidence; no assistive technology run | Require browser keyboard/focus/reflow evidence. |
| Keyboard interaction | Design rationale and collected test names | Inspected/collected | Static or synthetic evidence only | Execute real keyboard traversal before layout approval. |
| UI layout rationale | module spec, committee reviews, layout README | Inspected | Strong tradeoff record; historical alternatives remain searchable | Writer cites approved current layout only. |
| Security headers/CSP | app initialization and security tests | Executed subset + inspected | App/docs policy separation exists | Document separate CSP and JS boundaries. |
| External network isolation | requirements and static URL checks | Inspected + partial executed | No packet/network-disabled execution | Add network-denial test or explicit limitation. |
| Debugging journey | `docs/runbook/debugging.md` | Inspected | Operator commands exist; user symptom mapping absent | Build error catalogue by workflow stage. |
| Local website runbook | `docs/runbook/website-local.md` | Inspected | Useful launch details | Link from README and offline guide. |
| Dependency/runbook material | `docs/runbook/dependencies.md`, `architecture.md`, `api.md` | Inspected | Good contributor material; fragmented | Create one operations index. |
| Test inventory | `pytest --collect-only -q` | Executed: 904 collected in 2.61s | Collection is not execution | Never report 904 passed from D1. |
| Bounded regression execution | Eight focused files | Executed: 273 passed in 2.70s | Valid current evidence for selected categories only | Record exact command and date. |
| Prior full regression | chunk 2E checkpoint/notes | Historical: 904 passed | Not independently rerun in D1 | Label historical until PI reruns. |
| Core module maintainability | line-count command | Executed static count | Core mostly small; `runtime.py` 184, `serialization.py` 177, `shared.py` 133 | Use module map; avoid claiming uniform smallness. |
| Route module maintainability | line-count command | Executed static count | `workflow.py` 258 lines mixes concerns | Document boundaries; implementation refactor is out of D1. |
| Generated/source ownership | docs, website, build script | Inspected | Duplication is purposeful but under-documented | Add generated-file policy. |
| Local Markdown links | No dedicated executed checker | Gap | Link rot can escape website tests | Add local Markdown/fragment integrity test. |
| Browser route/link journey | Flask tests and static tests | Partial executed | No live browser traversal | Add browser route manifest smoke test. |
| Production deployment | No D1 deployment | Gap/out of scope | Local-only app; no production claim permitted | State unsupported deployment boundary. |
| Delegation | Checkpoint records unavailable agent ID | Inspected | Local fallback only | Preserve limitation in all D1 artifacts. |

## Evidence interpretation rules for future documentation

- Use **current source plus current executable tests** for behavior claims.
- Use decision records for rationale, not current-state assertions.
- Label benchmark results with environment, date, sample set, and limits.
- Label collected tests separately from passed tests.
- Do not convert static inspection into runtime, browser, accessibility, or offline claims.
- Every example output must be generated or independently recomputed; never infer numeric results from prose.
