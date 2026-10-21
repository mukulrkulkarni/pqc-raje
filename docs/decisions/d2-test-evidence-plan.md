# D2 Documentation Test Evidence Plan

**Status:** Plan only. This file defines evidence required for later documentation batches.

## Method

Each page batch must identify the source revision, commands, expected result, actual result, limitations, and reviewer decisions. Test evidence must include positive, negative, and edge cases where applicable. Test collection is not test execution.

## Required categories

| Category | Positive evidence | Negative evidence | Edge evidence |
|---|---|---|---|
| Unit/examples | Every command or code example runs. | Invalid criteria or matrix example fails as documented. | Eight criteria; block size 1 and 10,000. |
| Integration | Same scenario works through module, CLI, and web paths. | Wrong route, flag, or mapping fails clearly. | Headered/headerless paths and fewer than ten results. |
| Scientific | Net flow and raw descending ranking match source. | Unsupported tie or determinism claim is rejected. | q=p, p=v, veto, minimization, ties. |
| Security | Documented controls match routes/tests. | Invalid token, path, format, or session fails safely. | TTL, replacement, restart, rate, and size limits. |
| UI/accessibility | Labels, headings, tables, math, and forms are semantic. | JavaScript or non-semantic math blocks approval. | Keyboard focus, zoom/reflow, error focus, screen-reader pass. |
| Performance | Runtime gate and benchmark method match code. | Oversized estimate is rejected. | 300-second gate and 330-second timeout boundary. |
| Serialization/cache | Bytes, manifests, parts, and checksums reproduce. | Tampering, wrong ordering, or malformed artifact fails. | 16 MiB artifact and 32 MiB total boundaries. |
| End-to-end | Install → run → interpret → recover works. | Invalid input fails at the documented stage. | 100 MiB, 100,000 rows, and block-size limits. |
| Link/offline | Markdown, fragments, routes, and assets resolve offline. | Broken-link checker catches a deliberate bad link. | Network-disabled browser smoke test. |

## Review gates

- Scientific Critic: equations, thresholds, examples, net flow, ties, and claims.
- Engineering Critic: commands, source links, routes, limits, tests, and maintainability.
- UI/UX Redesign Agent: material layout, navigation, accessibility, and math presentation.
- PI: scope, authority, current/target wording, and release decision.

Missing category evidence, reviewer approval, checkpoint, auxiliary notes, commit, or clean worktree blocks completion.