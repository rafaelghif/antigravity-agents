# Pre-Implementation Impact Analysis

## Issue ID: issue-032
## Title: Enforce strict module lock verification gate in validation checks

This analysis compares two implementation options for lock verification.

---

### Option A: Enforce Staged Lock Auditing Natively in `validate.py` (Recommended)
Introduce a new validation audit in `validate.py` (e.g. `audit_staged_locks()`) that checks if any staged source code files (Python modules) are locked in `locks.json` by the current branch. If a file is modified/staged but not locked, or locked by another branch, validation fails.

#### Pros:
- Programmatic enforcement: completely eliminates the possibility of developers or agents forgetting to acquire locks before modifying modules.
- High transparency: explains exactly which module needs to be locked and how to do it.
- Non-disruptive: automatically ignores specifications, tests, configuration files, and plans.

#### Cons:
- None.

---

### Option B: Check Locks Only in the CLI Commit Command
Perform lock checks inside `commit.py` when running `./helper.sh commit`.

#### Pros:
- Simpler implementation.

#### Cons:
- Can be bypassed if someone runs `git commit` directly (since the git pre-commit hook runs `validate.py`, not `commit.py`). Option A is much safer because it runs in the git hook.

---

### Recommendation
**Option A** is the recommended choice because it is integrated directly into the Git pre-commit hook validation pipeline, making it impossible to bypass regardless of how commits are created.
