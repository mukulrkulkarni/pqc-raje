# Versioning and Rollback

This document describes the branching policy, commit rules, and rollback procedures for the ELECTRE III project.

## 1. Branching Policy

### 1.1 Branch Types

| Branch | Purpose | Naming |
|--------|---------|--------|
| main | Stable release code | main |
| wip/* | Work in progress features | wip/feature-name |
| fix/* | Bug fixes | fix/issue-description |

### 1.2 Rules

1. Do not commit directly to main.
2. Create a wip/* branch for new features.
3. Create a fix/* branch for bug fixes.
4. Delete branches after merge.

## 2. Commit-After-Gate Rule

### 2.1 Gate Checks

Before you commit, run preflight checks:

```bash
python scripts/preflight_checks.py
```

Or with tests:

```bash
python scripts/preflight_checks.py --run-tests
```

### 2.2 Required Conditions

A commit is allowed only when:

1. All preflight checks pass (exit code 0).
2. All tests pass (pytest -q).
3. No external asset URLs in HTML/CSS.
4. CSP headers are present in all HTML files.
5. Core modules are within line limits (≤50 lines).

### 2.3 Commit Message Format

```
<type>: <short description>

<optional body>
```

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation only
- refactor: Code change that does not fix a bug or add a feature
- test: Adding or updating tests

## 3. Rollback Procedures

### 3.1 Find Last Good Commit

List recent commits:

```bash
git log --oneline -10
```

### 3.2 Rollback to Specific Commit

**Soft rollback** (keeps changes staged):

```bash
git reset --soft <commit-hash>
```

**Mixed rollback** (keeps changes unstaged):

```bash
git reset <commit-hash>
```

**Hard rollback** (discards all changes):

```bash
git reset --hard <commit-hash>
```

**Warning**: If you already pushed the commits, you will need `git push --force`. This can cause problems for collaborators.

### 3.3 Rollback a Single File

```bash
git checkout <commit-hash> -- path/to/file.py
```

### 3.4 Create a Revert Commit

If the bad commit is already pushed:

```bash
git revert <commit-hash>
```

If conflicts occur, resolve them manually, then:

```bash
git add .
git commit
```

## 4. Run Preflight Checks

### 4.1 Basic Usage

```bash
python scripts/preflight_checks.py
```

### 4.2 With Tests

```bash
python scripts/preflight_checks.py --run-tests
```

### 4.3 Verbose Output

```bash
python scripts/preflight_checks.py --verbose
```

### 4.4 Windows Batch File

```bash
scripts\run_preflight.bat
```

### 4.5 Expected Output

```
============================================================
ELECTRE III Preflight Checks
============================================================

[PASS] Core module line limits
[PASS] No external assets
[PASS] CSP headers
[PASS] Design tokens

============================================================
All checks passed!
```

## 5. Emergency Procedures

### 5.1 Broken Main Branch

1. Identify the last working commit.
2. Create a fix branch from that commit.
3. Fix only the code that caused the failure. Do not add unrelated changes.
4. Run all preflight checks.
5. Merge to main.

### 5.2 Lost Work Recovery

Check the reflog:

```bash
git reflog
```

Recover from reflog:

```bash
git checkout <reflog-hash>
```

## 6. Quick Reference

| Action | Command |
|--------|---------|
| Run checks | `python scripts/preflight_checks.py` |
| Run checks + tests | `python scripts/preflight_checks.py --run-tests` |
| View history | `git log --oneline -10` |
| Soft reset | `git reset --soft HEAD~1` |
| Hard reset | `git reset --hard HEAD~1` |
| Revert commit | `git revert <hash>` |
| Recover lost | `git reflog` |
