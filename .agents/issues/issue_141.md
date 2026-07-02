---
id: issue-141
title: "Implement lock, learn, sync, and fast-polling in local dashboard"
status: open
assignee: agent-antigravity
created_at: 2026-07-02
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: HTML/CSS/JavaScript (Frontend), Python 3 (Backend).
- **Architecture**:
  - Add REST API endpoints to `dashboard.py`:
    - `POST /api/locks/acquire`: Lock a module.
    - `POST /api/locks/release`: Unlock a module.
    - `POST /api/learn`: Append a new lesson learned.
    - `POST /api/sync`: Force auto-synchronize project maps/rules.
  - Implement Frontend UX Enhancements in `app.js` and `index.html`:
    - Active polling speed up: If the dashboard detects it is auditing, it polls every 500ms instead of 5000ms, restoring 5s interval on completion.
    - Lock Management: An inputs card on the module locks tab to lock new modules, and a release button on each lock card.
    - Learn Management: A card on the memory tab to record lessons learned.
    - Sync Action: A "Sync Workspace" button next to "Refresh Audit" in the top header.
- **Key Modules**:
  - [.agents/scripts/cli/commands/dashboard.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/commands/dashboard.py)
  - [.agents/dashboard/index.html](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/dashboard/index.html)
  - [.agents/dashboard/style.css](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/dashboard/style.css)
  - [.agents/dashboard/app.js](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/dashboard/app.js)
  - [.agents/tests/test_dashboard.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/tests/test_dashboard.py)

### Pre-Implementation Impact Analysis
- **Option A (Recommended)**: Implement lock, learn, sync, and fast-polling in the dashboard.
  - *Trade-off*: Fully syncs all CLI features to the web control panel, resolves user frustration about "slow loading/refresh wait time", and boosts overall developer velocity.
- **Option B**: Keep polling at 5s and do not support adding data from the dashboard.
  - *Trade-off*: Leaves the dashboard as a read-only viewer rather than a fully interactive developer assistant.

## 2. Implementation Subtasks
- [x] Subtask 1: Add `/api/locks/acquire`, `/api/locks/release`, `/api/learn`, and `/api/sync` endpoints to `dashboard.py`.
- [x] Subtask 2: Add interactive lock creation form, release button, and record lesson form to `index.html`. Add "Sync Workspace" button.
- [x] Subtask 3: Implement client-side dynamic polling speed control (500ms fast / 5s default) and interactive button events in `app.js`.
- [x] Subtask 4: Add CSS styling for new forms and control buttons in `style.css`.
- [x] Subtask 5: Write unit tests in `test_dashboard.py` verifying locks, learn, and sync API routes.
- [x] Subtask 6: Run validation guard checks and ensure all pass.

## 3. Acceptance Criteria
- [x] Clicking "Sync Workspace" triggers a sync run on the backend and updates the UI.
- [x] Clicking "Release" next to a lock successfully unlocks the module in `locks.json`.
- [x] Filling the lock form and clicking "Lock Module" locks the module.
- [x] Recording a lesson adds it to `lessons-learned.md` and displays it in the ledger.
- [x] When auditing is triggered, polling switches to every 500ms, and changes back to 5s as soon as validation completes.
- [x] All unit tests and validation checks pass cleanly.
