# Pre-Implementation Impact Analysis

## Issue ID: issue-036
## Title: Fix git_api import path bug and implement CI commit status reporting

This analysis compares the chosen design options for the two tasks.

---

### Task 1: Fix `git_api` Import Path Bug
The bug arises because `.agents/scripts` is not consistently present in `sys.path` when commands are executed from the CLI helper wrappers or imported from other scripts.

#### Solution:
Explicitly add the absolute path of `.agents/scripts` to `sys.path` at the top of:
- `validate.py`
- `issue.py`

This ensures that `import git_api` will always work, regardless of execution context or working directory.

---

### Task 2: Implement CI Commit Status Reporting
When running validations in CI (e.g. `CI=true`), the validator should update the commit validation status on GitHub.

#### Solution:
1. Implement `post_commit_status(sha, state, description)` in `git_api.py`.
2. Add `get_commit_sha()` in `validate.py`.
3. In `run_validations()`:
   - Check if `CI` is `"true"`.
   - If yes and GITHUB_TOKEN/GIT_PAT is set, post `pending` status at the start.
   - Post `success` or `failure` status at the end.

This provides automated build checks feedback directly inside the GitHub interface.
