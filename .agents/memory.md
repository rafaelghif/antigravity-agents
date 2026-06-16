# Agent Core Memory

> **Memory Schema Version**: 5.0.0  
> **Target System**: Antigravity Agent Core
> **Active Guidelines**: Read [AGENTS.md](file://../AGENTS.md) and [.agents/rules/project_rules.md](file://./rules/project_rules.md) for execution details. Keep this file under 100 lines at all times.

---

## 1. Git State & Infrastructure Runtime
- **Active Branch**: main
- **Last Commit Reference**: a549c86
- **Active Pull Request Target**: `main`
- **Infrastructure Health Status**:
  - Database: `HEALTHY`
  - Cache/Broker: `HEALTHY`
  - Primary API Server: `HEALTHY`

---

## 2. Active Epic & Sub-Tasks Execution Matrix
- **Primary Epic**: Implement Git PR Review Scaffolder Skill
- **Current Task Target**: Design and document the `pr-scaffolder` skill workflow
- **State Flag**: `COMPLETED`

### Sprint Tasks Checklist
- [x] Align on design specifications via /grill-me
- [x] Create the task workflow blueprint file [task_pr_scaffolder.md](file://./workflows/task_pr_scaffolder.md)
---

## 3. Relayed Context & Handover Notes
- **Last Active Agent**: Antigravity
- **Last Action Completed**: Fully migrated the monolithic helper.sh and helper.ps1 script logic into a modular, clean Python CLI under .agents/scripts/cli/ (including skills, rules, init, and hooks).
- **Next Planned Action**: Ready for use. No further actions needed.
- **Blockers / Runtime Notes**: None.

---

## 4. Reference Links Index
- **Core Guidelines**: [AGENTS.md](file://../AGENTS.md)
- **Project Specific Rules**: [project_rules.md](file://./rules/project_rules.md)
- **Database Schema**: [schema.md](file://./schema.md)
- **Design Decisions**: [adr.md](file://./adr.md)
- **Sprint Archives**: [archive/](file://./archive/)
