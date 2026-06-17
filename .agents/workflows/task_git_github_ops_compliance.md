# Task Workflow: Git & GitHub CLI Operational Guidelines Compliance

## 1. Description
This task implements programmatic validation and compliance checks for the newly introduced "Git & GitHub CLI Operational Guidelines" (`.kimchi/docs/git_github_ops.md`). It ensures developers and AI agents follow safe, auditable, and token-efficient practices.

---

## 2. Architectural Decisions & Scope
- **Check 17 & 18 Bugfix**: Update the base branch modification check and module locking check to correctly expand untracked/modified directories (like `.kimchi/`) to check their contents, avoiding false failures on directories that only contain documentation, metadata, or ignored files.
- **Check 20: Staging Discipline Compliance Check**:
  - Scan staged files (`git diff --cached`) for common debug/leak patterns and forbidden secret files.
  - Warn/fail if all modified/untracked files are staged in bulk (detecting likely raw `git add .` or `git add -A` when file count is > 3).
- **Check 21: Protected Branches Guard**:
  - Extend branch protection detection to cover `main`, `master`, `release/*`, and `hotfix/*` branches.
  - Block direct code mutations on these branches.
- **Check 22: Git Environment Compliance Audit**:
  - Audit `GIT_PAGER` and `GIT_EDITOR` environment variables.
  - Enforce `GIT_PAGER=cat` (or `core.pager=cat`) to prevent blocking interactive pager sessions during automation.
- **Check 23: GitHub CLI Auth & Profile Verification**:
  - Validate GitHub CLI auth status and highlight if auth is using placeholders or is inactive.
- **Language Alignment**: Implement all checks in both `.agents/scripts/cli/commands/validate.py` and `.agents/scripts/validate.sh` to ensure perfect parity.

---

## 3. Checklist

- [x] Lock the validation/core module before editing
- [x] Implement directory expansion fix for Check 17 and Check 18 in `validate.py`
- [x] Implement directory expansion fix for Check 17 and Check 18 in `validate.sh`
- [x] Implement Check 20 (Staging Discipline) in `validate.py` and `validate.sh`
- [x] Implement Check 21 (Protected Branches) in `validate.py` and `validate.sh`
- [x] Implement Check 22 (Git Environment) in `validate.py` and `validate.sh`
- [x] Implement Check 23 (GitHub CLI Auth) in `validate.py` and `validate.sh`
- [x] Add the execution calls for Checks 20-23 in the main execution blocks of `validate.py` and `validate.sh`
- [x] Run validation locally to verify that `.kimchi/` no longer causes Check 17 & 18 to fail
- [x] Verify that workspace status changes to VALIDATED (or warning/fail as expected for new checks)
- [x] Run python tests to ensure no regressions in validation command tests
- [x] Release the lock, mark checklist items as complete, and commit the changes using `helper.sh commit`
