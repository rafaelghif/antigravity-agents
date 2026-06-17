# Task Workflow: Git Profile Switching and Status Display in Menu

## 1. Scope & Objective
Add Git profile switching details, Git name, and remote token status (GitHub, GitLab, Gitea) to the interactive control panel `menu` dashboard. Fix the column alignment bug caused by ANSI color code length counting in python format strings.

---

## 2. Design & Implementation Plan

### A. Resolve Git Profile and Token Status (`menu.py`)
Implement `get_active_git_profile_details(email)` in [menu.py](file:///D:/Muhammad%20Rafael%20Ghifari/Software%20Engineer/Application/antigravity-agents/.agents/scripts/cli/commands/menu.py):
1. Locate the Git profiles file.
2. Read the active profile matching the current Git email.
3. Extract the active profile name, display name (falls back to `git config user.name` or `"Local Developer"`), and boolean flags indicating whether `github_token`, `gitlab_token`, and `gitea_token` exist.

### B. Implement Column Alignment Helper (`menu.py`)
Implement `align_col(text, raw_text, width=25)` in [menu.py](file:///D:/Muhammad%20Rafael%20Ghifari/Software%20Engineer/Application/antigravity-agents/.agents/scripts/cli/commands/menu.py) to format the column strings based on their raw visual length, ignoring ANSI color character length.

### C. Redesign Dashboard Control Panel Header (`menu.py`)
Update the main dashboard layout to display:
- `Branch` and `API Profile` (aligned columns).
- `Git Profile` (e.g. `work` or `personal`) and `Locks` (e.g. `🔓 Open`).
- `Git Name` and `Active Tokens` (e.g. `github [✅] gitlab [❌] gitea [✅]`).
- `Git Email` and `Token Limit` usage statistics.

---

## 3. Verification & Testing Plan
- Run existing test suites: `python tests/test_rotation.py`
- Add a new unit test in `tests/test_menu_command.py` verifying that the Git profile resolution returns the correct profile name, display name, and token statuses.
