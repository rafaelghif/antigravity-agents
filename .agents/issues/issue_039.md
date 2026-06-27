---
id: issue-039
title: "Automatically publish GitHub Release Draft during release bump"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Issue Details

## Problem Statement
We want to automate the creation of draft releases on GitHub. When `./helper.sh changelog` is run (or during issue close which runs changelog), if a new version is created and GITHUB_TOKEN/GIT_PAT is set, we should construct the release body from the newly generated changelog entries and call the GitHub Release API to publish a draft release.

## Tasks
- [x] Implement create_github_release function in git_api.py
- [x] Integrate git_api.create_github_release call in changelog.py when not running in preview or bump-only mode
- [x] Add unit tests covering release creation on release bump in test_changelog.py
- [x] Validate and close issue-039 using the automated close command

## Acceptance Criteria
- [x] Running changelog successfully bumps version and triggers create_github_release API call
- [x] Release draft uses the new version tag (e.g. `v2.14.0`) and features parsed from CHANGELOG.md
- [x] All unit tests pass successfully
