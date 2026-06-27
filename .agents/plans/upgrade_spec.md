# Pre-Implementation Impact Analysis: Automated Installer Upgrade Flow

We analyze implementation approaches to support safe, seamless, and automated framework upgrades without configuration loss.

---

## 1. Option Comparison Matrix

| Criteria | Option A: Full Override (Clean Slate - Recommended) | Option B: Selective Overwrite |
|---|---|---|
| **Description** | Automatically archives old `.agents` folder to `.agents_backup_YYYYMMDD_HHMMSS` and performs a clean V2 installation. | Overwrites only core framework scripts and templates, keeping user-specific files in place. |
| **Upgrade Safety** | High (guarantees no stale or orphaned files from older framework versions remain). | Medium (stale files from older versions might remain in `.agents/scripts` or `.agents/skills`). |
| **Data Preservation** | High (archived folder preserves 100% of tasks, profiles, and issue history). | High (preserves files in-place). |
| **Code Simplicity** | High (relies on standard POSIX shell commands to move directories). | Medium (requires granular checks and exclusions for every single file/folder). |

---

## 2. Upgrade Workflow Design

1. Check if the target project contains `.agents`.
2. If it does, generate `TIMESTAMP=$(date +%Y%m%d_%H%M%S)`.
3. Rename and move the existing `.agents` folder to `.agents_backup_$TIMESTAMP`.
4. If `AGENTS.md` exists, create a backup copy `AGENTS.md.backup_$TIMESTAMP`.
5. Proceed with clean V2 copy operations (from local or remote sources) and run `bootstrap.sh`.
6. Log warnings highlighting the backup folders to guide the developer on how to restore their profiles and tasks.

---

## 3. Implementation Steps

1. Update [install.sh](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/install.sh) to execute the backup and rename operations before copying new directories.
2. Write test suite [.agents/tests/test_upgrade.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/tests/test_upgrade.py).
3. Verify that the entire validation guard runs and passes successfully.
