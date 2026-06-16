# Agent Core Memory

> **Memory Schema Version**: 5.0.0  
> **Target System**: Antigravity Agent Core
> **Active Guidelines**: Read [AGENTS.md](file://../AGENTS.md) and [.agents/rules/project_rules.md](file://./rules/project_rules.md) for execution details. Keep this file under 100 lines at all times.

---

## 1. Git State & Infrastructure Runtime
- **Active Branch**: main
- **Last Commit Reference**: e55bfd1
- **Active Pull Request Target**: `main`
- **Infrastructure Health Status**:
  - Database: `HEALTHY`
  - Cache/Broker: `HEALTHY`
  - Primary API Server: `HEALTHY`

---

## 2. Active Epic & Sub-Tasks Execution Matrix
- **Primary Epic**: PowerShell Rotation Wrapper & Helper Active Key Loading
- **Current Task Target**: Implement PowerShell api-rotate-wrapper.ps1 and helper.ps1 loading
- **State Flag**: `COMPLETED`

### Sprint Tasks Checklist
- [x] Implement PowerShell api-rotate-wrapper.ps1 and helper.ps1 loading
- [x] Compile templates and synchronize bootstrap scripts
- [x] Verify validation and clean workspace

---

## 3. Relayed Context & Handover Notes
- **Last Active Agent**: Antigravity
- **Last Action Completed**: Successfully implemented native PowerShell wrapper api-rotate-wrapper.ps1, updated helper.ps1 active key loading support, compiled all templates into bootstrap scripts, and committed changes.
- **Next Planned Action**: push commits to origin (git push)
- **Blockers / Runtime Notes**: None. Workspace is fully clean, validated, and committed.

---

## 4. Reference Links Index
- **Core Guidelines**: [AGENTS.md](file://../AGENTS.md)
- **Project Specific Rules**: [project_rules.md](file://./rules/project_rules.md)
- **Database Schema**: [schema.md](file://./schema.md)
- **Design Decisions**: [adr.md](file://./adr.md)
- **Sprint Archives**: [archive/](file://./archive/)
