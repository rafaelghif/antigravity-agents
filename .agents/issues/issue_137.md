---
id: issue-137
title: "Enable asynchronous non-blocking validation audits and auto-updating dashboard"
status: closed
assignee: agent-antigravity
created_at: 2026-07-02
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: HTML/CSS/JavaScript (Frontend), Python 3 (Backend).
- **Architecture**: Async background worker for `/api/status?force=true` to prevent HTTP request blocking. Local dashboard polling when the page is active.
- **Key Modules**:
  - [.agents/scripts/cli/commands/dashboard.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/commands/dashboard.py)
  - [.agents/dashboard/app.js](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/dashboard/app.js)
  - [.agents/tests/test_dashboard.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/tests/test_dashboard.py)

### Pre-Implementation Impact Analysis
- **Option A (Recommended)**: Use a non-blocking background thread on the server for force-audit updates and communicate the status via the `"auditing"` boolean in JSON responses. Integrate focus-aware auto-polling on the frontend (runs `loadData` every 5 seconds only when document is visible).
  - *Trade-off*: Fully responsive UI, no loading freeze/timeouts, real-time updates when files/branches/tasks are modified in the terminal, minimal CPU/network usage when tab is inactive.
- **Option B**: Maintain synchronous validation on force requests, but run it inside a thread pool with a timeout.
  - *Trade-off*: Still risks long-running requests timing out or returning partial/error data on slow test runs. Doesn't solve the auto-update requirement.

## 2. Implementation Subtasks
- [x] Subtask 1: Define lock variables and refactor `get_dashboard_data` to trigger `run_silent_validation` in a separate thread on `force=true`.
- [x] Subtask 2: Update `app.js` to handle `auditing` status in the response and introduce focus-aware periodic polling.
- [x] Subtask 3: Write unit tests in `test_dashboard.py` asserting non-blocking behavior.
- [x] Subtask 4: Verify the entire validation guard passes cleanly.

## 3. Acceptance Criteria
- [x] Forced audit requests return immediately (within milliseconds) instead of hanging.
- [x] Clicking "Refresh Audit" disables the button and updates the label to "Auditing...".
- [x] Once background validation completes, the dashboard automatically updates and re-enables the button on the next poll.
- [x] Tab auto-updates every 5 seconds when active, reflecting external git/task modifications.
- [x] Dashboard test suites pass successfully.
