# Pre-Implementation Impact Analysis: Upgrade Command Repository URL and Path Adjustments

We evaluate options to update the `upgrade` command behavior.

## Option A: Align Repository URL to rafaelghif and Add Core Files to Update Paths (Recommended)
Change `SOURCE_REPO` in `upgrade.py` to `https://github.com/rafaelghif/antigravity-agents.git`. Add `.agents/skills/`, `.agents/rules.md`, and `AGENTS.md` to `paths_to_update` to checkout all core documents and skills directly from GitHub during upgrades.
- **Pros**: Matches user's repository settings, ensures full system upgrades (including playbooks and skills), and avoids configuration drift/inconsistency.
- **Cons**: Upgrades will overwrite local modifications to AGENTS.md or rules.md, but this is the desired behavior for strict official release tracking.

## Option B: Fix URL only without updating paths
Only fix `SOURCE_REPO` to point to the correct username (`rafaelghif`).
- **Pros**: None.
- **Cons**: Fails to update skills, AGENTS.md, or rules.md from GitHub during upgrade, resulting in version mismatch.

### Downstream Impacts
- Modifies `.agents/scripts/cli/commands/upgrade.py`.
- Ensures any manual changes to AGENTS.md or rules.md are reset to upstream versions on upgrade.

**Decision**: **Option A** is selected.
