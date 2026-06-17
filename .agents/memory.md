# Agent Core Memory

> **Memory Schema Version**: 5.0.0  
> **Target System**: Antigravity Agent Core
> **Active Guidelines**: Read [AGENTS.md](file://../AGENTS.md) and [.agents/rules/project_rules.md](file://./rules/project_rules.md) for execution details. Keep this file under 100 lines at all times.

---

## 1. Git State & Infrastructure Runtime
- **Active Branch**: main
- **Last Commit Reference**: 3708ebf
- **Active Pull Request Target**: `main`
- **Infrastructure Health Status**:
  - Database: `HEALTHY`
  - Cache/Broker: `HEALTHY`
  - Primary API Server: `HEALTHY`

---

## 2. Active Epic & Sub-Tasks Execution Matrix
- **Primary Epic**: Initial Setup
- **Current Task Target**: Resolve issue #3: Add Git profile and credential status display to interactive menu
- **State Flag**: `COMPLETED`

### Sprint Tasks Checklist
- [x] Implement align_col and get_active_git_profile_details in menu.py
- [x] Redesign control panel header layout in menu.py
- [x] Add unit tests for Git profile menu resolution
- [x] Conduct /grill-me design interview for GitLab/Gitea rotation





---

## 3. Relayed Context & Handover Notes
- **Last Active Agent**: Antigravity
- **Last Action Completed**: Completed /grill-me alignment interview and saved the plan to task_gitlab_gitea_rotation.md.
- **Next Planned Action**: Implement the Gitea/GitLab rotation & sync changes based on the execution plan.
- **Blockers / Runtime Notes**: None. Workspace is fully validated.

---

## 4. Reference Links Index
- **Core Guidelines**: [AGENTS.md](file://../AGENTS.md)
- **Project Specific Rules**: [project_rules.md](file://./rules/project_rules.md)
- **Database Schema**: [schema.md](file://./schema.md)
- **Design Decisions**: [adr.md](file://./adr.md)
- **Sprint Archives**: [archive/](file://./archive/)
