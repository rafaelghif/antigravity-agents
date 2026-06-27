---
id: issue-054
title: "Refactor changelog generator to improve SemVer safety, boundary resolution, and issue classification"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Design & Task Specification

## 1. Pre-Implementation Impact Analysis
- **Option A**: Write external helper scripts to calculate SemVer.
  - *Trade-offs*: Scattered architecture, increases dependency on multiple files, difficult to maintain.
- **Option B (Recommended)**: Refactor `changelog.py` directly. Implement a structured priority map for commit types, expand git boundary tag search, and extract classification context from local issue markdown files.
  - *Trade-offs*: Highly cohesive, low maintenance, keeps logic encapsulated inside the changelog CLI module.

## 2. Technical Decisions
- **Stack**: Python 3, CLI.
- **Key Modules**:
  - [.agents/scripts/cli/commands/changelog.py](file://./.agents/scripts/cli/commands/changelog.py)
  - [.agents/issues/](file://./.agents/issues/)

## 3. Implementation Subtasks
- [x] Refactor commit parsing in `changelog.py` to group by issue ID and prioritize breaking changes over features/fixes to ensure correct SemVer bumps <!-- id: subtask-semver-dedup-priority -->
- [x] Improve tag-based boundary commit lookup and fallback in `get_boundary_commit` <!-- id: subtask-boundary-resolution -->
- [x] Implement local issue frontmatter parsing for automatic category/title classification fallback <!-- id: subtask-local-issue-classify -->
- [x] Run validation suite locally <!-- id: subtask-validate -->

## 4. Acceptance Criteria
- [x] Multiple commits for the same issue with mixed types (e.g. `feat`, `fix`, and `breaking!`) bump the version correctly based on the highest priority type
- [x] Boundary commit resolution works via git log and tags fallbacks
- [x] `./helper.sh validate` passes successfully without errors
