# Agent Core Memory

> **Memory Schema Version**: 5.0.0  
> **Target System**: Antigravity Agent Core
> **Active Guidelines**: Read [AGENTS.md](file://../AGENTS.md) and [.agents/rules/project_rules.md](file://./rules/project_rules.md) for execution details. Keep this file under 100 lines at all times.

---

## 1. Git State & Infrastructure Runtime
- **Active Branch**: main
- **Last Commit Reference**: 1381d3b
- **Active Pull Request Target**: `main`
- **Infrastructure Health Status**:
  - Database: `HEALTHY`
  - Cache/Broker: `HEALTHY`
  - Primary API Server: `HEALTHY`

---

## 2. Active Epic & Sub-Tasks Execution Matrix
- **Primary Epic**: Document Prerequisites & Improve Python CLI Robustness
- **Current Task Target**: Add Python 3 requirement to README, check in bootstrap and helper scripts
- **State Flag**: `COMPLETED`

### Sprint Tasks Checklist
- [x] Add Python 3 check to bootstrap, helper, and document in README
- [x] Verify build and validation checks pass
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
