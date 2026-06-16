# Task Workflow: Implement CLI push Subcommand

This task adds a new `push` subcommand to the Antigravity CLI helper framework. The command automates workspace validation checks, profile email verification, and Git push execution utilizing rotated SSH keys.

## 1. Architectural Decisions & Mappings
- **Command Entrypoint**: `./.agents/scripts/helper.sh push`
- **Implementation File**: [push.py](file://../../.agents/scripts/cli/commands/push.py)
- **Features & Logic**:
  - **Workspace Validation**: Runs `./.agents/scripts/validate.sh` before pushing, unless `--no-validate` is provided. If validation fails, it aborts the push.
  - **Active Profile Alignment**: Reads `.agents/git_profiles` to verify if the current local Git user email (`git config user.email`) matches a configured profile. Warns if mismatched, but allows bypass.
  - **Dynamic SSH Authentication**: If the active profile specifies an SSH key file (`ssh_key`), it automatically sets `GIT_SSH_COMMAND="ssh -i /path/to/key -o IdentitiesOnly=yes"` dynamically during the `git push` execution.
  - **Branch Auto-Detection**: Dynamically resolves the active branch name via `git rev-parse --abbrev-ref HEAD`.
  - **Options Supported**:
    - `--force` or `-f`: Executes a force push (`git push origin <branch> --force`).
    - `--no-validate` or `-n`: Skips workspace validation checks and profile email warnings.

---

## 2. Implementation Checklist

- [x] **Lock target modules**
  - Run `./.agents/scripts/helper.sh lock cli`
- [x] **Create `push.py` Command Module**
  - Implement parsing, validation, key rotation, and push execution logic in [push.py](file://../../.agents/scripts/cli/commands/push.py).
- [x] **Register `push` Command**
  - Import and add `push` to the commands map in [helper.py](file://../../.agents/scripts/cli/helper.py).
- [x] **Verify and Validate**
  - Perform test pushes or dry runs.
  - Run `./.agents/scripts/helper.sh validate` and ensure it passes.
- [x] **Document Changes**
  - Update `README.md` and `CHANGELOG.md` under the current version.
- [/] **Release Locks & Commit**
  - Run `./.agents/scripts/helper.sh commit feat cli "add push subcommand wrapping validation and profile ssh rotation"`
