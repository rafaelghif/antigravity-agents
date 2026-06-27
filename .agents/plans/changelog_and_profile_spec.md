# Pre-Implementation Impact Analysis

## Issue ID: issue-034
## Title: Implement structured changelog categorization and repository-isolated SSH key rotation

This analysis compares the chosen design options for both tasks.

---

### Task 1: Auto-Changelog Categorization

We will parse commit messages based on standard Conventional Commit prefixes:
- `feat`: 🚀 Features
- `fix`: 🐛 Bug Fixes
- `docs`: 📝 Documentation
- `chore`, `refactor`, `style`, `perf`, `test`, `ci`: ⚙️ Maintenance & Chores
- Other: 📋 Other Changes

#### Implementation:
In `.agents/scripts/cli/commands/changelog.py`:
- Parse the parsed commits list.
- Group commits into categories.
- Format the output with clear headers and bullet points.

---

### Task 2: Profile Switcher SSH Key Integration

We will add `ssh_key_path` in `git_profiles.json`. When switching profiles:
- Check if `ssh_key_path` is present.
- If present, set `git config --local core.sshCommand "ssh -i <ssh_key_path> -o IdentitiesOnly=yes"`.
- If absent, unset `core.sshCommand` locally in git.

#### Implementation:
Modify `profile.py` (`handle_switch`) and `commit.py` (`run`) to apply `core.sshCommand` locally.
- In `profile.py`:
  ```python
  ssh_key = active_profile.get("ssh_key_path")
  if ssh_key:
      subprocess.run(['git', 'config', '--local', 'core.sshCommand', f'ssh -i {ssh_key} -o IdentitiesOnly=yes'])
  else:
      subprocess.run(['git', 'config', '--local', '--unset', 'core.sshCommand'], stderr=subprocess.DEVNULL)
  ```
- In `commit.py`, match this inside the profile application logic.

---

### Recommendation
The proposed local SSH command rotation is clean and safe, avoiding global system contamination. Commit categorization aligns directly with standard SemVer practice.
