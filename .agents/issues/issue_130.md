---
id: issue-130
title: "Modernize local visual dashboard with modular template serving and interactive subtasks checklist auto-update"
status: open
assignee: agent-antigravity
created_at: 2026-07-02
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: Python 3 (HTTP server in CLI command), Vanilla JavaScript, CSS, HTML.
- **Architecture**: Modular Static File Serving. Decouple dashboard frontend assets from CLI python execution.
- **Key Modules**:
  - [.agents/dashboard/app.js](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/dashboard/app.js)
  - [.agents/scripts/cli/commands/dashboard.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/commands/dashboard.py)

### Pre-Implementation Impact Analysis
- **Option A (Recommended)**: Read static files directly on every HTTP request from the `.agents/dashboard` folder.
  - *Trade-off*: Small local file read cost, but provides instant developer feedback when tweaking frontend assets without requiring a server restart. Extremely clean and decoupled.
- **Option B**: Cache all static files in memory on startup.
  - *Trade-off*: Zero runtime I/O, but any change to CSS/JS requires stopping and starting the server, degrading Developer Experience (DX).

## 2. Implementation Subtasks
- [x] Subtask 1: Create `.agents/dashboard/app.js` containing AJAX loading, tab switching, and toggle task interactivity.
- [x] Subtask 2: Refactor `dashboard.py` to serve static files (`index.html`, `style.css`, `app.js`) from `.agents/dashboard/` instead of inline template.
- [x] Subtask 3: Add `POST /api/task/toggle` endpoint in `dashboard.py` to update the active issue's subtask checkbox state in its markdown file.
- [x] Subtask 4: Verify the local validation guard passes and run unit tests.

## 3. Acceptance Criteria
- [x] The dashboard successfully loads and serves static files from `.agents/dashboard/`.
- [x] The UI looks modern, premium, responds to tab switching, and has a smaller navbar and better scroll.
- [x] Toggling subtask checkboxes on the dashboard UI updates the active issue file (e.g. `.agents/issues/issue_130.md`) dynamically.
- [x] Validation suite and unit tests pass without error.
