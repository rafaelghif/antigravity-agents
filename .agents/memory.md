# Agent Core Memory

> **Memory Schema Version**: 5.0.0  
> **Target System**: Antigravity Agent Core
> **Active Guidelines**: Read [AGENTS.md](file://../AGENTS.md) and [.agents/rules/project_rules.md](file://./rules/project_rules.md) for execution details. Keep this file under 100 lines at all times.

---

## 1. Git State & Infrastructure Runtime
- **Active Branch**: main
- **Last Commit Reference**: 12ca83e
- **Active Pull Request Target**: `main`
- **Infrastructure Health Status**:
  - Database: `HEALTHY`
  - Cache/Broker: `HEALTHY`
  - Primary API Server: `HEALTHY`

---

## 2. Active Epic & Sub-Tasks Execution Matrix
- **Primary Epic**: Python CLI Migration
- **Current Task Target**: Implement modular Python helper CLI
- **State Flag**: `COMPLETED`

### Sprint Tasks Checklist
- [x] Create CLI folder structure and base files
- [x] Implement utils.py and helper.py dispatcher
- [x] Implement commands (lock, unlock, log_usage, archive, api_profile, git_profile)
- [x] Implement commands (validate, doctor, migrate, recon, skills, rules, init)
- [x] Replace helper.sh/helper.ps1 with dispatch wrappers
- [x] Run all tests and validation checks
---

## 3. Relayed Context & Handover Notes
- **Last Active Agent**: Antigravity
- **Last Action Completed**: Defined the design plan and execution workflow for migrating the massive helper.sh CLI to modular Python commands under .agents/scripts/cli/ (task_python_cli_migration.md).
- **Next Planned Action**: Execute the migration steps in the next sprint, beginning with utils.py and the command dispatcher helper.py.
- **Blockers / Runtime Notes**: None.

---

## 4. Reference Links Index
- **Core Guidelines**: [AGENTS.md](file://../AGENTS.md)
- **Project Specific Rules**: [project_rules.md](file://./rules/project_rules.md)
- **Database Schema**: [schema.md](file://./schema.md)
- **Design Decisions**: [adr.md](file://./adr.md)
- **Sprint Archives**: [archive/](file://./archive/)
