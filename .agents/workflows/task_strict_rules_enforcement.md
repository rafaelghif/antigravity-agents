# Task Workflow: Strict Rules Enforcement

This workflow details the execution plan to enforce strict compliance with the Antigravity Agent Core developer protocol. By implementing programmatic guardrails, we eliminate common loopholes that allow agents or developers to bypass mandatory procedures.

---

## 1. Identified Loopholes & Mitigation Plan

### Loophole 1: Raw `git commit` Bypass
- **Problem**: Agents/developers can execute raw `git commit` in the terminal, bypassing Git profile/SSH key rotation and automatic issue updates. The `pre-commit` hook runs `validate`, but has no way of knowing whether the commit was initiated via `helper.sh commit` or directly.
- **Mitigation**: 
  - Modify `commands/commit.py` to set an environment variable `AAC_COMMIT_RUNNING=1` when executing the commit command.
  - Modify `.agents/hooks/pre-commit` to check if `AAC_COMMIT_RUNNING` is set to `1`. If not, abort the commit with a clear error message instructing the user to run `./.agents/scripts/helper.sh commit`.

### Loophole 2: Direct Modifications on Base Branches
- **Problem**: Code changes can be edited or staged directly on base branches (`main`/`master`) instead of using isolated feature branches.
- **Mitigation**: 
  - Update `commands/validate.py` and `.agents/scripts/validate.sh` to check if the current branch is `main` or `master`.
  - If so, verify that there are no modified or untracked code files (excluding workspace metadata like locks, `memory.md`, issues, workflows, ADRs, `README.md`, and `CHANGELOG.md`).
  - If unauthorized modifications exist, fail the validation.

### Loophole 3: Editing Without Acquiring a Module Lock
- **Problem**: Files can be modified or committed without acquiring a lock via `./.agents/scripts/helper.sh lock <module>`.
- **Mitigation**: 
  - Update `commands/validate.py` and `.agents/scripts/validate.sh` to get the list of modified/staged files.
  - Map each code file to its top-level module (e.g. `tests/` -> `tests`, root files -> `root`).
  - Check if a corresponding lockfile exists under `.agents/locks/`.
  - If a file is modified but its module is not locked, fail the validation.

### Loophole 4: Out-of-Sync Issue Tracking
- **Problem**: Commits can be made on feature branches that are not aligned with `memory.md` task checklists or target targets.
- **Mitigation**: 
  - If the branch name matches the pattern `issue-<id>-<slug>`, parse the ID.
  - Verify that the issue file `.agents/issues/issue_<padded_id>.md` exists.
  - Verify that `memory.md` has its `Current Task Target` aligned with the issue title.
  - Verify that the `State Flag` is `IN_PROGRESS` (or `COMPLETED` when preparing a commit).

---

## 2. Implementation Checklist

- [x] Lock necessary modules before editing code
- [x] Implement Parent Process Check (`AAC_COMMIT_RUNNING`) in `commands/commit.py` and `.agents/hooks/pre-commit`
- [x] Implement Base Branch Modification Check in `commands/validate.py` and `validate.sh`
- [x] Implement Staged Files Module Locking Check in `commands/validate.py` and `validate.sh`
- [x] Implement Issue Branch and Memory Alignment Check in `commands/validate.py` and `validate.sh`
- [x] Update tests to verify the new validation rules
- [x] Verify health and run complete validation suite via `./.agents/scripts/helper.sh doctor`
- [x] Commit changes using Conventional Commits via helper script
