# Task Workflow: Implement CLI clean Subcommand

This task adds a new `clean` subcommand to the helper CLI framework. The command prepares the repository for public release by cleaning locks, logs, sprint archives, task workflows, and resetting memory/API configs to clean templates.

## 1. Architectural Decisions & Mappings
- **Command Entrypoint**: `./.agents/scripts/helper.sh clean`
- **Implementation File**: [clean.py](file://../../.agents/scripts/cli/commands/clean.py)
- **Features & Logic**:
  - **Locks Removal**: Deletes all active lock files in `.agents/locks/` (except the currently active lock of the clean task itself to prevent concurrency errors).
  - **Archive Purge**: Deletes all archived sprint checklist files and subfolders in `.agents/archive/`.
  - **Workflows Purge**: Deletes all task workflow files in `.agents/workflows/` (except the current cleanup workflow).
  - **Budget Reset**: Resets token budget stats in `.agents/token_budget.json` to default clean values.
  - **API profile Reset**: Resets `.agents/active_api_profile_name` to 'default' and overrides active keys `.agents/active_api_keys` / `.agents/active_api_keys.ps1` to empty template values.
  - **Memory Ledger Reset**: Rewrites `.agents/memory.md` to a clean template (resolving active branch and last commit dynamically).

---

## 2. Implementation Checklist

- [x] **Lock target modules**
  - Run `./.agents/scripts/helper.sh lock cli`
- [x] **Create `clean.py` Command Module**
  - Implement file purges, token/API resets, and dynamic clean memory template writing in [clean.py](file://../../.agents/scripts/cli/commands/clean.py).
- [x] **Register `clean` Command**
  - Import and add `clean` to the commands map in [helper.py](file://../../.agents/scripts/cli/helper.py).
- [x] **Verify and Validate**
  - Run the clean command and verify that logs, locks, and templates are reset correctly.
- [x] **Document Changes**
  - Update `docs/cli_guide.md` and `CHANGELOG.md` under the current version.
  - Re-run `scratch/compile_bootstrap.py` to compile all new scripts into `bootstrap.sh`.
- [x] **Release Locks & Commit**
  - Run `./.agents/scripts/helper.sh commit feat cli "add clean subcommand to purge locks archives and reset configs"`
