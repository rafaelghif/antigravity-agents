---
id: issue-098
title: "Fix Windows compatibility, CLI encoding, and test suite execution bugs"
status: open
assignee: agent-antigravity
created_at: 2026-07-02
---

# Issue Details

## Problem Statement
Fix Windows compatibility, CLI encoding, and test suite execution bugs

## Tasks
- [x] Fix UnicodeEncodeError in printing command banners/emojis on Windows cp932 consoles
- [x] Resolve cross-drive calculation ValueError in bootstrap path calculation
- [x] Correct helper.ps1 exit code propagation using exit $LASTEXITCODE
- [x] Add encoding='utf-8' to open() calls in unit tests
- [x] Adapt integration wrapper tests to run helper.ps1 on Windows and specify encoding='utf-8' in subprocess runs

## Acceptance Criteria
- [x] All 101 unit and integration tests pass successfully on Windows
- [x] Validation guard command runs and passes successfully on Windows
