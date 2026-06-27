---
id: issue-034
title: "Implement structured changelog categorization and repository-isolated SSH key rotation"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Issue Details

## Problem Statement
We need to improve our CLI helpers in two areas:
1. **Auto-Changelog**: Currently, the changelog generator lists all commits in a flat list. We need to categorize them into professional sections (e.g. Features, Bug Fixes, Chores, etc.).
2. **Profile Switcher**: We need to allow repository-isolated SSH key rotation by defining `ssh_key_path` in `git_profiles.json` and setting `core.sshCommand` locally in git.

## Tasks
- [x] Implement commit type categorization logic in changelog.py
- [x] Update changelog template formatting for clean, structured sections
- [x] Implement core.sshCommand configuration in profile switcher (profile.py and commit.py)
- [x] Add unit tests for changelog categorization and sshCommand rotation
- [x] Verify validations and run issue close command to merge issue-034

## Acceptance Criteria
- [x] CHANGELOG.md contains categorized commit lists (Features, Bug Fixes, etc.)
- [x] Profiles with `ssh_key_path` configured automatically update `core.sshCommand` locally
- [x] All unit tests pass successfully
