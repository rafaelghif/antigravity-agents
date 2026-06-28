# Pre-Implementation Impact Analysis: Auto-Task ID Injection via prepare-commit-msg Git hook

We evaluate options to implement the auto-injection of issue references into git commit messages.

## Option A: Pure Bash logic in Git hook
Implement the branch parsing and file-appending logic directly as a bash shell script inside the hook template.
- **Pros**: Zero python dependencies at commit preparation time.
- **Cons**: Difficult to unit test, hard to maintain, and prone to platform compatibility errors when run inside Windows Git Bash environments.

## Option B: Python-driven hook logic (Recommended)
Write the branch parsing and commit message editing logic inside a new script `.agents/scripts/prepare_commit_msg.py`. The `prepare-commit-msg` hook will act as a thin wrapper that invokes this python script.
- **Pros**: Easy to unit test, highly readable, platform-independent, and consistent with the existing pre-commit hook execution model.
- **Cons**: Requires Python to be present at commit creation time (falls back gracefully if python is missing).

### Downstream Impacts
- Modifies `bootstrap.sh` and `bootstrap.ps1` to write the `prepare-commit-msg` hook to `.git/hooks/`.
- Modifies `.agents/scripts/cli/commands/bootstrap.py` to also write the hook when bootstrapping from Python.
- Adds `.agents/scripts/prepare_commit_msg.py` containing the branch-parsing and file-modification logic.
- Adds `.agents/tests/test_prepare_commit_msg.py` to test the injection behavior.

**Decision**: **Option B** is selected.
