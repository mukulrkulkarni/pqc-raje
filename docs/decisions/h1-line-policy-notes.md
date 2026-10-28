# H1 Line-Policy Notes

**Status:** Completed. Engineering approved; final acceptance validation passed; committed as `99aa360` (`complete-h1-cli-config-line-policy`).

## Scope and source evidence

- Baseline: `e28ae17` (`checkpoint-d6-reference-draft`), with a clean working tree.
- Refactored public modules: `electre3/cli.py` and `electre3/config.py`.
- Cohesive helpers: `cli_args.py`, `cli_io.py`, `cli_output.py`, and `config_validation.py`.
- Recovery change: `tests/test_ranking_deep.py` permits valid repository-local links and limits Flask route checks to module-served links.
- Added regression coverage: `tests/test_cli.py` preserves CLI flags, load-error handling, and EOF confirmation behavior.
- Excluded: user documentation pages, D6 materials, `data.py`, `runtime.py`, `serialization.py`, `shared.py`, CSP preflight, remote Git, and tag changes.

## Engineering approval

Engineering Critic approved H1 stale-link recovery. This final acceptance run uses that approved repair: each local target must resolve beneath repository `ROOT`, be an existing file, and contain any specified fragment. Route and CSP assertions apply only when the target resolves beneath `PAGE.parent`; repository-local documentation such as the root `README.md` has no module Flask route.

## Executable-line audit

`python out/h1_line_audit.py` passed with these results:

| Module | Executable lines |
|---|---:|
| `electre3/cli.py` | 30 |
| `electre3/cli_args.py` | 13 |
| `electre3/cli_io.py` | 29 |
| `electre3/cli_output.py` | 18 |
| `electre3/config.py` | 27 |
| `electre3/config_validation.py` | 26 |

The audit uses Python tokenization and excludes comments, blank lines, indentation, and logical line markers. Each H1 Python module is within the strict 50 executable-line limit.

## Final acceptance evidence — 2026-10-28

| Check | Exact command | Result |
|---|---|---|
| Failed-test-first recovery | `python -m pytest tests/test_ranking_deep.py -q` | Initially **29 passed, 1 failed**; the valid `../../README.md` link exposed the stale module-only containment assertion. |
| Repaired ranking test | `python -m pytest tests/test_ranking_deep.py -q` | **30 passed in 0.62s** |
| Focused H1 tests | `python -m pytest tests/test_cli.py tests/test_cli_run.py tests/test_config.py -q` | **29 passed in 0.40s** |
| Full suite | `python -m pytest -q` | **1045 passed in 24.32s** |
| Syntax compilation | `python -m compileall -q electre3 app` | **passed** |
| Strict line audit | `python out/h1_line_audit.py` | **passed**; counts shown above |
| Whitespace/diff audit | `git diff --check` | **passed**; Git emitted existing LF-to-CRLF conversion warnings for edited tracked files |

## Positive, negative, and edge coverage

- **Positive:** The repaired ranking tutorial test accepts the repository-root README link. The CLI test saves a ranking with the existing flags, while the focused H1 tests confirm refactored CLI and configuration behavior.
- **Negative:** Existing link-negative coverage rejects `#missing`, `missing.html`, `https://example.com`, `//example.com`, and `../../escape.html`. The CLI regression test reports a missing input file to stderr and returns `1`.
- **Edge:** The repository-root README exists but has no Flask documentation route. File and fragment validation therefore continue for all local links, while route/CSP checks run only for module-served links. EOF during CLI confirmation safely prints `Aborted.` and returns `0`.

## Limitations

- Browser, assistive-technology, zoom, reflow, keyboard-runtime, offline, and load validation remain deferred and non-blocking.
- No remote Git operation or v0.1 tag change occurred.
- Git's LF-to-CRLF conversion warnings are environmental; `git diff --check` reported no whitespace errors.

## Maintenance notes

`electre3.cli.main` remains the public CLI entry point. Helpers separate argument parsing, input and confirmation handling, output, and configuration validation without changing CLI flags or output. Keep each changed or added H1 Python module at 50 executable lines or fewer. Re-run the focused H1 tests, full suite, compileall, line audit, and `git diff --check` after future H1 changes.
