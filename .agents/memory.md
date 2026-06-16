# Agent Core Memory

> **Memory Schema Version**: 5.0.0  
> **Target System**: Antigravity Agent Core
> **Active Guidelines**: Read [AGENTS.md](file://../AGENTS.md) and [.agents/rules/project_rules.md](file://./rules/project_rules.md) for execution details. Keep this file under 100 lines at all times.

---

## 1. Git State & Infrastructure Runtime
- **Active Branch**: main
- **Last Commit Reference**: e8c7ab2
- **Active Pull Request Target**: `main`
- **Infrastructure Health Status**:
  - Database: `HEALTHY`
  - Cache/Broker: `HEALTHY`
  - Primary API Server: `HEALTHY`

---

## 2. Active Epic & Sub-Tasks Execution Matrix
- **Primary Epic**: Enforce Strict Framework Alignment & Isolation
- **Current Task Target**: Implement Interactive ADR Wizard Skill
- **State Flag**: `COMPLETED`

### Sprint Tasks Checklist
- [x] Execute task checklist in [task_adr_wizard.md](file://./workflows/task_adr_wizard.md)
---

## 3. Relayed Context & Handover Notes
- **Last Active Agent**: Antigravity
- **Last Action Completed**: Created task plan `task_adr_wizard.md` and scaffolded the `adr-wizard` skill directory, unit test skeleton, and active lock.
- **Next Planned Action**: Register `adr-wizard` subcommand in the helper CLI and implement interactive/non-interactive prompt logic.
- **Blockers / Runtime Notes**: Active lock acquired on `adr-wizard`. Workspace is validated.

---

## 4. Reference Links Index
- **Core Guidelines**: [AGENTS.md](file://../AGENTS.md)
- **Project Specific Rules**: [project_rules.md](file://./rules/project_rules.md)
- **Database Schema**: [schema.md](file://./schema.md)
- **Design Decisions**: [adr.md](file://./adr.md)
- **Sprint Archives**: [archive/](file://./archive/)
