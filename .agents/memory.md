# Agent Core Memory

> **Memory Schema Version**: 5.0.0  
> **Target System**: Antigravity Agent Core
> **Active Guidelines**: Read [AGENTS.md](file://../AGENTS.md) and [.agents/rules/project_rules.md](file://./rules/project_rules.md) for execution details. Keep this file under 100 lines at all times.

---

## 1. Git State & Infrastructure Runtime
- **Active Branch**: main
- **Last Commit Reference**: 174f4ed
- **Active Pull Request Target**: `main`
- **Infrastructure Health Status**:
  - Database: `HEALTHY`
  - Cache/Broker: `HEALTHY`
  - Primary API Server: `HEALTHY`

---

## 2. Active Epic & Sub-Tasks Execution Matrix
- **Primary Epic**: Modular ADR Scaffolding & Validation
- **Current Task Target**: Implement create-adr command and validate.sh ADR compliance checks
- **State Flag**: `COMPLETED`

### Sprint Tasks Checklist
- [x] Implement create-adr command, validate.sh compliance check, and migrate existing adr.md (Refer to [task_modular_adrs.md](file://./workflows/task_modular_adrs.md))
---

## 3. Relayed Context & Handover Notes
- **Last Active Agent**: Antigravity
- **Last Action Completed**: Added native PowerShell wrapper `helper.ps1` for Windows compatibility and integrated an enterprise-ready GitHub Actions workflow template for automated CI validation.
- **Next Planned Action**: None.
- **Blockers / Runtime Notes**: Workspace validated. Lock will be released automatically upon commit.

---

## 4. Reference Links Index
- **Core Guidelines**: [AGENTS.md](file://../AGENTS.md)
- **Project Specific Rules**: [project_rules.md](file://./rules/project_rules.md)
- **Database Schema**: [schema.md](file://./schema.md)
- **Design Decisions**: [adr.md](file://./adr.md)
- **Sprint Archives**: [archive/](file://./archive/)
