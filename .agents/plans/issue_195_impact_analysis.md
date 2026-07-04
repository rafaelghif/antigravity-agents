# Pre-Implementation Impact Analysis — Issue-195

Evaluating approaches to fix upgrade configuration overwrite and memory pollution.

## 1. Options Comparison

### Option A: Remove AGENTS.md and rules.md from Upgrade Checkout (Recommended)
- **Description**: Remove `AGENTS.md` and `.agents/rules.md` from the list of updated files (`paths_to_update`) in `upgrade.py`. Upgrades will continue to update CLI scripts, templates, and skills, but leave the project's customized instructions intact.
- **Complexity**: Low.
- **Maintainability**: High.
- **Prompt Cache Efficiency**: High. Prevents the CLI repo's rules and specs from overwriting target project versions.

### Option B: Local Backup and Merge
- **Description**: Back up target versions of `AGENTS.md` and `rules.md` to a temp directory, perform the upgrade checkout from remote, and merge the core repo's updates with the target project's local configurations.
- **Complexity**: High. Very prone to merge conflicts and formatting issues.

---

## 2. Recommendation
We recommend **Option A** because `AGENTS.md` and `.agents/rules.md` are project-specific workspace files that shouldn't be overwritten by a checkout from the core CLI repository during general tool updates.
