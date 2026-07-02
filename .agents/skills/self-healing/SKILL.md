---
name: self-healing
description: Diagnostic and recovery playbook for resolving local git states, locked configuration files, broken workspace setups, and process deadlocks.
---

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
