---
id: issue-035
title: "Improve auto-reconnaissance system to generate structured recommendations report"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Issue Details

## Problem Statement
The current auto-reconnaissance script (`recon.py`) only detects stacks and updates versions. We need to expand it to scan for:
- Missing standard directories (e.g. `src/`, `tests/`, etc.) based on active stack.
- Missing dev dependencies (linters like flake8/eslint, test runners like pytest/jest).
- Missing critical gitignore patterns.
It must generate a detailed recommendations report at `.agents/plans/recon_recommendations.md`.

## Tasks
- [x] Implement advanced directory structure and dependency scanning logic in recon.py
- [x] Implement recon_recommendations.md generator function in recon.py
- [x] Add unit tests for workspace scanner and recommendations report in test_recon.py
- [x] Validate and close issue-035 using the automated close command

## Acceptance Criteria
- [x] running `./helper.sh sync` or `recon.py` generates `.agents/plans/recon_recommendations.md`
- [x] Recommendations report details stack, missing directories, missing dev dependencies, and install commands
- [x] All unit tests pass successfully
