# Agent Core Memory

> **Memory Schema Version**: 5.0.0  
> **Target System**: Antigravity Agent Core
> **Active Guidelines**: Read [AGENTS.md](file://../AGENTS.md) and [.agents/rules/project_rules.md](file://./rules/project_rules.md) for execution details. Keep this file under 100 lines at all times.

---

## 1. Git State & Infrastructure Runtime
- **Active Branch**: main
- **Last Commit Reference**: 112d33f
- **Active Pull Request Target**: `main`
- **Infrastructure Health Status**:
  - Database: `HEALTHY`
  - Cache/Broker: `HEALTHY`
  - Primary API Server: `HEALTHY`

---

## 2. Active Epic & Sub-Tasks Execution Matrix
- **Primary Epic**: Framework Python & Shell Improvements
- **Current Task Target**: Implement 4 core improvements (venv, autocomplete, CI/CD, and skill tests)
- **State Flag**: `COMPLETED`

### Sprint Tasks Checklist
- [x] Execute task checklist in [task_prerequisites_improvements.md](file://./workflows/task_prerequisites_improvements.md)
- [x] Verify validation and commit changes
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
