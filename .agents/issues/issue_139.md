---
id: issue-139
title: "Implement Git profile and credentials management in local dashboard"
status: open
assignee: agent-antigravity
created_at: 2026-07-02
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: HTML/CSS/JavaScript (Frontend), Python 3 (Backend).
- **Architecture**:
  - Add REST API endpoints to `/api/profiles` (GET list, POST switch, POST add, GET public-key).
  - Add a "👥 Profiles" tab to the dashboard sidebar.
  - Implement forms in the frontend to:
    - View active profile details and list all registered profiles.
    - Switch active profile with one click.
    - Create a new Git profile (with options to generate SSH keys or enter GPG/tokens).
    - View and copy SSH public key for copying to GitHub.
- **Key Modules**:
  - [.agents/scripts/cli/commands/dashboard.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/commands/dashboard.py)
  - [.agents/dashboard/index.html](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/dashboard/index.html)
  - [.agents/dashboard/style.css](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/dashboard/style.css)
  - [.agents/dashboard/app.js](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/dashboard/app.js)
  - [.agents/tests/test_dashboard.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/tests/test_dashboard.py)

### Pre-Implementation Impact Analysis
- **Option A (Recommended)**: Implement Git profile, GPG keys, SSH key generation, and Github tokens management inside the local dashboard through REST API routes and a dedicated Outfit-themed view.
  - *Trade-off*: Delivers an exceptionally premium and feature-rich UI, fully aligning the web control panel with CLI capabilities. Extremely secure since the HTTP server is bound to localhost.
- **Option B**: Only show read-only details of the active Git profile without switching or creation forms.
  - *Trade-off*: High friction since the user still has to drop down to the CLI to rotate credentials or add new keys.

## 2. Implementation Subtasks
- [ ] Subtask 1: Add `/api/profiles` (GET, POST switch, POST add) and `/api/ssh/public-key` endpoints to `dashboard.py`.
- [ ] Subtask 2: Add the "Profiles" tab layout and modal forms to `index.html`.
- [ ] Subtask 3: Implement client-side API requests, form validations, and profile view rendering in `app.js`.
- [ ] Subtask 4: Add styling for the profiles card lists, badge details, and forms in `style.css`.
- [ ] Subtask 5: Write unit tests in `test_dashboard.py` verifying profiles API routes.
- [ ] Subtask 6: Run validation guard checks and ensure all pass.

## 3. Acceptance Criteria
- [ ] Clicking "Profiles" in the sidebar opens the profiles management tab.
- [ ] Displays all registered profiles from `.agents/git_profiles.json` with their status (active/inactive).
- [ ] Clicking "Switch" on a profile switches the active profile in the JSON config and updates the local Git config dynamically.
- [ ] Submitting the "Create Profile" form validates fields (alphanumeric name, email format) and registers the new profile successfully.
- [ ] Selecting "Generate SSH Key" during creation correctly triggers `generate_ssh_key()` and displays the public key in the UI for copy-pasting.
- [ ] Validation checklist passes without errors.
