---
id: issue-073
title: "Fix changelog titles and parsing logic"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Issue Details

## Problem Statement
Fix changelog titles and parsing logic

## Tasks
- [x] Task 1: Fix changelog parsing logic in commands/changelog.py to extract frontmatter titles.
- [x] Task 2: Clean existing entries in CHANGELOG.md using fix_changelog_history.py.

## Acceptance Criteria
- [x] changelog.py successfully extracts actual title from frontmatter of issue markdown files.
- [x] Generic titles in CHANGELOG.md are replaced with descriptive issue titles.
