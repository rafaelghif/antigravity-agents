# Issue 022: Implement Auto-Changelog Generator CLI with Semantic Tagging

## 1. Description
We will implement an automated changelog generator and semantic versioning CLI tool for Antigravity Agent Core. This command will parse conventional commit history to determine version bumps, update version metadata, and update the changelog.

## 2. Scope & Design Choices
- **Command Module**: `.agents/scripts/cli/commands/changelog.py`
- **Register CLI**: `.agents/scripts/cli/helper.py`
- **CLI Options**:
  - `--preview`: Only display changes and estimated version bump without writing files.
  - `--bump-only`: Only update version strings in files without editing `CHANGELOG.md`.
- **Version Boundary**: Detect the latest version header in `CHANGELOG.md` (e.g. `## [2.1.0]`), search for a matching release commit (e.g., `chore(release): 2.1.0`), and parse all commits from that hash to `HEAD`. Fall back to all commits if not found.
- **Rules File Sync**: Automatically sync version bumps to `AGENTS.md` (`Version: X.Y.Z`) and `bootstrap.sh`.

## 3. Implementation Subtasks
- [x] **changelog.py**: Implement git log parsing to extract conventional commits since the boundary commit.
- [x] **changelog.py**: Implement semantic version calculation (Major for breaking changes, Minor for `feat`, Patch for `fix`).
- [x] **changelog.py**: Implement file updates for `AGENTS.md` and `bootstrap.sh`.
- [x] **changelog.py**: Implement changelog prepending (formatting per type group under version/date header).
- [x] **helper.py**: Register the `changelog` subcommand in the allowed commands set.
- [x] **test_changelog.py**: Implement unit tests covering parsing, semantic bumps, file writes, and CLI arguments.
- [x] **Validation**: Verify that the test suite and validation guard run and pass successfully.

## 4. Acceptance Criteria
- [x] `helper.sh changelog --preview` prints the parsed commits, grouped by type, and shows the recommended next version without making file changes.
- [x] Running `helper.sh changelog` automatically updates the version in `AGENTS.md` and `bootstrap.sh`, and prepends the grouped commits under a new version header to `CHANGELOG.md`.
- [x] Only commits since the last version's release commit are analyzed.
- [x] All unit tests pass.
- [x] Validation guard runs and passes successfully.
