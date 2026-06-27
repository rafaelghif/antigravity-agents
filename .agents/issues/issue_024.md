# Issue 024: Implement Automated Installer Upgrade Flow with Directory Backup

## 1. Description
We will implement an automated upgrade and migration mechanism in `install.sh` to safely upgrade older versions of Antigravity Agent Core. When a target folder already contains `.agents`, the installer will automatically backup the old directory and `AGENTS.md` with timestamps before performing a clean V2 installation.

## 2. Scope & Design Choices
- **Archive old files**: Move target's `.agents` to `.agents_backup_YYYYMMDD_HHMMSS`.
- **Backup AGENTS.md**: Copy `AGENTS.md` to `AGENTS.md.backup_YYYYMMDD_HHMMSS` but keep active `AGENTS.md` to preserve custom developer guidelines, and let `bootstrap.sh` sync its metadata.
- **Support Local and Remote upgrade**: Apply this backup and clean install sequence to both the local clone installation and remote GitHub zip download paths.

## 3. Implementation Subtasks
- [x] **install.sh**: Implement timestamped backup logic for `.agents` and `AGENTS.md` when they already exist.
- [x] **install.sh**: Ensure the target gets a clean `.agents` structure (excluding source `memory/` files except templates) after backup.
- [x] **test_upgrade.py**: Write unit tests verifying backup folder creation, file preservation, and cleanup operations.
- [x] **Validation**: Verify that the entire validation guard runs and passes successfully.

## 4. Acceptance Criteria
- [x] Running `install.sh` in a directory containing `.agents` moves the old folder to `.agents_backup_YYYYMMDD_HHMMSS` before writing V2 files.
- [x] A copy of the existing `AGENTS.md` is saved as a timestamped backup, but the active file is kept and dynamically updated with V2 versions.
- [x] A clear release warning and checklist message is printed at the end of the installation to inform the developer about the backup folder location.
- [x] All unit tests pass.
- [x] Validation guard runs and passes successfully.
