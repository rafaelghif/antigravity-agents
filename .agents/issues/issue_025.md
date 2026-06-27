# Issue 025: Update Public Facing README.md Documentation for V2 CLI and Compliance

## 1. Description
We will update the repository's public `README.md` documentation to document the new AAC V2 features, including the Developer CLI (`helper.sh`/`helper.ps1`), Git profile credential validation, module locking workflows, local issue tracking, automatic changelog generation, and automated upgrade/backup procedures.

## 2. Scope & Design Choices
- **CLI commands list**: Document all dispatcher subcommands in a markdown table.
- **Git Profiles rotation**: Explain how `./helper.sh profile` prevents credential mismatches.
- **Module locks**: Document lock acquisition and stale lock auto-pruning.
- **Timestamped backups**: Explain how the installer archives old `.agents` setups during upgrades.

## 3. Implementation Subtasks
- [x] **README.md**: Rewrite the document to incorporate the V2 CLI command reference, locking guides, profile setup, and upgrade details.
- [x] **Validation**: Run the validation guard to verify all files are compliant.

## 4. Acceptance Criteria
- [x] `README.md` contains clear guides for all 7 helper subcommands (bootstrap, validate, lock, profile, issue, changelog, sync).
- [x] Windows PowerShell wrappers (`helper.ps1`, `bootstrap.ps1`) are documented alongside bash equivalents.
- [x] Lock auto-release and profile identity rotation compliance steps are clearly explained.
- [x] Validation guard runs and passes successfully.
