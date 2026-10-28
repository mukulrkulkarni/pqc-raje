# Future Requirement: Project-Wide Python Line-Policy Enforcement

**Status:** Deferred. This file records future work. It does not claim project-wide compliance.

## Current status

The existing preflight check passes its configured scope. Audited new and changed modules comply with the 50-executable-line rule. The project is **not globally proven compliant**.

Known exception:

- `scripts/build_website.py` remains an existing documented exception.

The following areas remain outside the audited scope:

- Existing large modules outside the current refactor scope.
- Test modules and test helpers.
- Utility scripts and benchmark generators.
- Archive or evidence-only Python files.
- Any generated or historical Python snapshots.

## Deferred inventory work

Create a complete repository inventory for every tracked Python file.
Record:

- path
- executable-line count
- generated or source status
- test or production role
- current exception status
- proposed owner
- refactor priority

The inventory must distinguish executable lines from comments, blank lines, and docstrings. Use one reproducible counting method for all files.

## Deferred test requirements

Add tests for the inventory and policy:

### Positive tests

- Every new or changed Python module stays at or below 50 executable lines.
- Every approved exception has a documented path, owner, rationale, and review date.
- The audit includes production modules, tests, utilities, and generated-source boundaries.

### Negative tests

- A new module above 50 executable lines fails the policy check.
- An undocumented exception fails the policy check.
- A changed module omitted from the inventory fails the policy check.
- A generated or archived file misclassified as production code is reported.

### Edge tests

- A module with exactly 50 executable lines passes.
- A module with 51 executable lines fails.
- Decorators, multiline expressions, nested functions, class bodies, and docstrings count consistently.
- Windows and Unix line endings produce the same count.
- Files under generated or archive directories follow the declared policy.

## Refactoring controls

Refactor one bounded module group at a time. Preserve public APIs. Add regression tests before and after each refactor. Do not refactor `scripts/build_website.py` unless separately approved.

Each refactor requires:

- checkpoint
- test evidence
- Engineering review
- Scientific review when numerical behavior changes
- UI/UX review when rendered behavior changes
- focused commit
- clean-worktree verification

## Release impact

This deferred work does not block the existing v0.1 release. Do not claim project-wide 50-line compliance until the complete inventory and policy tests pass.
