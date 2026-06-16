# Agent Core Memory

> **Memory Schema Version**: 5.0.0  
> **Target System**: Antigravity Agent Core
> **Active Guidelines**: Read [AGENTS.md](file://../AGENTS.md) and [.agents/rules/project_rules.md](file://./rules/project_rules.md) for execution details. Keep this file under 100 lines at all times.

---

## 1. Git State & Infrastructure Runtime
- **Active Branch**: main
- **Last Commit Reference**: 5cbbf75
- **Active Pull Request Target**: `main`
- **Infrastructure Health Status**:
  - Database: `HEALTHY`
  - Cache/Broker: `HEALTHY`
  - Primary API Server: `HEALTHY`

---

## 2. Active Epic & Sub-Tasks Execution Matrix
- **Primary Epic**: CLI Helper Push Automation
- **Current Task Target**: Implement CLI push subcommand
- **State Flag**: `COMPLETED`

### Sprint Tasks Checklist
- [x] Implement CLI push subcommand
---

## 3. Relayed Context & Handover Notes
- **Last Active Agent**: Antigravity
- **Last Action Completed**: Reviewed workspace onboarding experience. Added a new `guide` console command, updated docs (`agent_workflow.md`, `setup_guide.md`, `cli_guide.md`) to use helper commits, and updated `compile_bootstrap.py` to recursively compile all Python CLI scripts into `bootstrap.sh`. Committed successfully.
- **Next Planned Action**: None. Onboarding optimizations, code reviews, and secure push command are completed.
- **Blockers / Runtime Notes**: None. Workspace is validated, locks released, and tests passed.

---

## 4. Reference Links Index
- **Core Guidelines**: [AGENTS.md](file://../AGENTS.md)
- **Project Specific Rules**: [project_rules.md](file://./rules/project_rules.md)
- **Database Schema**: [schema.md](file://./schema.md)
- **Design Decisions**: [adr.md](file://./adr.md)
- **Sprint Archives**: [archive/](file://./archive/)
