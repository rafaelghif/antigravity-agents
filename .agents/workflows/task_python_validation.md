# Task Workflow: Pure-Python Workspace Validation Suite

## 1. Scope & Objective
Migrate the workspace security, quality, and configuration validation checks from the Bash-based `validate.sh` script into a cross-platform Python validation framework inside `validate.py` (and helper modules if needed). This removes the runtime dependency on Bash, Unix-like tools (grep, sed, find), and `sh.exe` on Windows.

---

## 2. Design & Implementation Plan

### A. Python Validation Script Architecture (`validate.py`)
Reimplement the 16 checks of `validate.sh` natively:
1. **Memory Line Count**: Open `.agents/memory.md` and count lines. Warn if > 100.
2. **Active Locks**: Scan `.agents/locks/*.lock` files and print active locks.
3. **Secret Scanner**: Perform file-level scanning for high-entropy strings and keys (excluding `.agents/`, `.git/`, `.venv/`, `node_modules/`).
4. **Domain Purity (Raw Environment Access)**: Check for raw env accesses in domain files.
5. **Git Upstream Sync**: Query `git status` or `git rev-list --count` to verify local status vs remote.
6. **Schema Registration**: Parse `.agents/schema.md` and verify all files in `.agents/schemas/` are referenced.
7. **Gitignore Compliance**: Ensure `.agents/` is tracked.
8. **Memory State Flag**: Read state flag from `memory.md` and verify it is `COMPLETED` if committing.
9. **Token Budget Guard**: Parse `token_budget.json` and verify budget limits.
10. **ADR Compliance**: Parse `.agents/adr.md` and verify all files in `.agents/adrs/` are referenced.
11. **Git Configuration & Profile Compliance**: Verify local git config.
12. **API Configuration & Profile Compliance**: Validate API profile setup.
13. **Keep a Changelog Compliance**: Check `CHANGELOG.md` formatting.
14. **Staged TODO/FIXME Guard**: Scan staged files for temporary comments.
15. **Staged Transient Files Guard**: Ensure no private keys or `.env` files are staged.
16. **Local Issues Validation**: Check metadata and state of issue files.

### B. Hook Integration
- Update Git hooks `pre-commit`, `commit-msg`, and `post-commit` to directly run Python:
  `python .agents/scripts/cli/helper.py validate`

---

## 3. Verification & Testing Plan
- Execute Python validator on the current workspace: `python .agents/scripts/cli/helper.py validate`
- Run test suites to ensure no regressions are introduced.
