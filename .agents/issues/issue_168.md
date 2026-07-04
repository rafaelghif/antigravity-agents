---
id: issue-168
title: "Add Token Budget visualization to dashboard"
status: closed
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
Add Token Budget visualization to dashboard

## Tasks
- [x] Update `.agents/issues/issue_168.md` subtasks and claim in board
- [x] Inject token budget data into `get_dashboard_data()` in `dashboard.py`
- [x] Add Token Budget tab navigation and content panels in `index.html`
- [x] Add custom styling for token progress bars and lists in `style.css`
- [x] Implement token budget data rendering logic in `app.js`
- [x] Run validation checks and close issue

## Acceptance Criteria
- [x] The web dashboard features a dedicated "Token Budget" tab
- [x] Daily and monthly token budgets are visualised with dynamic progress bars
- [x] Usage is broken down by active API account (secure masked key/profile)
- [x] Usage is broken down per Git issue/task with clear timestamps
- [x] `./helper.sh validate` passes successfully
