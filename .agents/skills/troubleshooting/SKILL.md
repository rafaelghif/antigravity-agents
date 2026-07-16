---
name: troubleshooting
description: Diagnostic playbook for troubleshooting CLI errors, shell script crashes, and test failures. Diagnostic and recovery playbook for resolving local git states, locked configuration files, broken workspace setups, and process deadlocks.
---

## Inherited from debugging

# Debugging Skill Playbook

Use this playbook when encountering test failures or unexpected system behavior.

## Diagnostic Flow
1. **Verify Prerequisites**: Ensure Python 3 and Git are installed and available in the current PATH.
2. **Path Separators**: On Windows, check if path backslashes (`\`) are causing script syntax errors; ensure paths are dynamically constructed or handled.
3. **Budget Status**: Verify that the daily token limits haven't been exceeded in `token_budget.json`.
4. **Mock State**: Verify that external systems (such as Git remote actions or environment keys) are properly mocked in test suites.

## Loop Detection & Mitigation Protocol

To prevent wasting agent tokens and user budgets, the agent must monitor its own action patterns for loop behaviors.

### A. Recognizing an Infinite Loop
A loop condition is present if:
- You run the same test suite or run command multiple times in a row with the exact same output without modifying files in between.
- You repeatedly search for the same pattern or string in the codebase using `grep_search` or `view_file` calls.
- You repeatedly edit the same file chunk back and forth (e.g. reverting a change then applying it again).
- A validation gate fails, and you run the same repair command without checking if the underlying issue has changed.

### B. Mitigation Actions
1. **Halt Execution**: Stop all automated repair loops immediately once a pattern is executed 3 times without a successful outcome.
2. **Analyze Root Cause**: Before making any further tool call, output a concise diagnostic explanation detailing why the loop occurred.
3. **Request Help**: Present the diagnostic log to the user and ask for clarification, guidance, or code modification permissions rather than continuing the loop.

## Inherited from self-healing

# Self-Healing & Recovery Playbook

This playbook defines standard operational procedures for diagnosing, recovering, and healing a corrupted developer or agent workspace environment without manual intervention.

---

## 1. Local Git State Recovery

When an autonomous agent runs into Git anomalies (detached HEAD, dirty tree, merge conflicts, or lock file issues), it must apply these recovery steps.

### A. Resolving Git Merge Conflicts
1. **Detect Conflict**: Run `git status` and search for files with unmerged paths (marked with `UU`).
2. **Determine Abort vs Resolve**:
   - If the conflict is in a core system configuration file or too wide in scope, abort the merge immediately:
     ```bash
     git merge --abort
     ```
   - If the conflict is localized and easily reconcilable, open the file, inspect conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`), resolve the logic, and stage the file:
     ```bash
     git add <resolved_file>
     ```
3. **Commit Cleanly**: Conclude the merge using a conventional commit message.

### B. Repairing Git Index Locks
If a git action returns `Fatal: Unable to create '.git/index.lock': File exists`, the agent should:
1. Verify if another git process is running. If not, delete the stale lock file safely:
   ```bash
   rm -f .git/index.lock
   ```

---

## 2. Lock File & Configuration Rescue

Stale locks on modules or databases can freeze agent pipelines.

### A. Releasing Stale Module Locks
If a file remains locked by a dead or non-existent branch:
1. View `.agents/locks.json` to identify the lock holder.
2. Verify if the holder branch exists locally/remotely:
   ```bash
   git show-ref refs/heads/<holder_branch>
   ```
3. If the branch does not exist, execute the release command to unlock the module:
   ```bash
   python3 .agents/scripts/cli/helper.py lock <module_name> --release
   ```

---

## 3. Broken Workspace Setup & Dependency Repair

If an agentic execution fails because of missing dependencies, outdated libraries, or environment compiler errors:

1. **Package Re-installation**:
   - For Node: run `npm install --no-audit` or `npm ci`.
   - For Python: run `pip install -r requirements.txt`.
2. **Environment Clean**:
   - Clean compiled caches:
     - Python: `find . -name "*.pyc" -delete && find . -name "__pycache__" -delete`
     - Node: `rm -rf .next build dist`
3. **Sub-Project Re-Bootstrap**:
   - If a target sub-project directory is corrupt, run `./helper.sh bootstrap` to restore default stack configuration guidelines.