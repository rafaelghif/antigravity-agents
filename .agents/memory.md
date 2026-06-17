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
- **Current Task Target**: Resolve issue #2: Add support for Gitea and GitLab issue synchronization
- **State Flag**: `COMPLETED`

### Sprint Tasks Checklist
- [x] Implement provider auto-detection and token resolution in issue.py
- [x] Implement GitLab and Gitea API sync functions in issue.py
- [x] Update issue creation, metadata saving, and closing commands to use the unified sync engine
- [x] Add unit tests for GitLab and Gitea issue synchronization




---

## 3. Relayed Context & Handover Notes
- **Last Active Agent**: None
- **Last Action Completed**: Initialized clean Antigravity Agent Core workspace.
- **Next Planned Action**: None. Ready for new features or tasks.
- **Blockers / Runtime Notes**: None.

---

## 4. Reference Links Index
- **Core Guidelines**: [AGENTS.md](file://../AGENTS.md)
- **Project Specific Rules**: [project_rules.md](file://./rules/project_rules.md)
- **Database Schema**: [schema.md](file://./schema.md)
- **Design Decisions**: [adr.md](file://./adr.md)
- **Sprint Archives**: [archive/](file://./archive/)
