# Agent Core Memory

> **Memory Schema Version**: 5.0.0  
> **Target System**: Antigravity Agent Core
> **Active Guidelines**: Read [AGENTS.md](file://../AGENTS.md) and [.agents/rules/project_rules.md](file://./rules/project_rules.md) for execution details. Keep this file under 100 lines at all times.

---

## 1. Git State & Infrastructure Runtime
- **Active Branch**: main
- **Last Commit Reference**: 380f60b
- **Active Pull Request Target**: `main`
- **Infrastructure Health Status**:
  - Database: `HEALTHY`
  - Cache/Broker: `HEALTHY`
  - Primary API Server: `HEALTHY`

---

## 2. Active Epic & Sub-Tasks Execution Matrix
- **Primary Epic**: API Key Rotation and Budget Auto-Reset
- **Current Task Target**: Implement automatic token usage reset
- **State Flag**: `COMPLETED`

### Sprint Tasks Checklist
- [x] Implement automatic token usage reset in budget tracker and api-rotator
---

## 3. Relayed Context & Handover Notes
- **Last Active Agent**: Antigravity
- **Last Action Completed**: Implemented automatic token usage reset based on configurable intervals in `token_budget.json`, integrated with `validate.sh` and `api-rotator`, and verified via unit tests.
- **Next Planned Action**: Ready for next session.
- **Blockers / Runtime Notes**: Workspace is fully validated and all tests pass. Lock 'cli' acquired.
---

## 4. Reference Links Index
- **Core Guidelines**: [AGENTS.md](file://../AGENTS.md)
- **Project Specific Rules**: [project_rules.md](file://./rules/project_rules.md)
- **Database Schema**: [schema.md](file://./schema.md)
- **Design Decisions**: [adr.md](file://./adr.md)
- **Sprint Archives**: [archive/](file://./archive/)
