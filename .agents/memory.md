# Agent Core Memory

> **Memory Schema Version**: 5.0.0  
> **Target System**: Antigravity Agent Core
> **Active Guidelines**: Read [AGENTS.md](file://../AGENTS.md) and [.agents/rules/project_rules.md](file://./rules/project_rules.md) for execution details. Keep this file under 100 lines at all times.

---

## 1. Git State & Infrastructure Runtime
- **Active Branch**: main
- **Last Commit Reference**: 75b2eb9
- **Active Pull Request Target**: `main`
- **Infrastructure Health Status**:
  - Database: `HEALTHY`
  - Cache/Broker: `HEALTHY`
  - Primary API Server: `HEALTHY`

---

## 2. Active Epic & Sub-Tasks Execution Matrix
- **Primary Epic**: API Rotation Enhancements
- **Current Task Target**: Implement API profile cooldowns
- **State Flag**: `COMPLETED`

### Sprint Tasks Checklist
- [x] Implement API profile cooldown logic in helper.sh
- [x] Update wrapper scripts and python skill
- [x] Implement rotation tests with cooldown verify
- [x] Run all tests and validation checks
---

## 3. Relayed Context & Handover Notes
- **Last Active Agent**: Antigravity
- **Last Action Completed**: Implemented rate-limit cooldown persistence (.agents/cooldowns.json) and sleep-wait fallback when all profiles are in cooldown; integrated --rate-limited flag across wrapper scripts and Python skills; added robust Test 3 coverage in tests/test_rotation.py.
- **Next Planned Action**: None. Workspace is fully clean, validated, and committed.
- **Blockers / Runtime Notes**: None.

---

## 4. Reference Links Index
- **Core Guidelines**: [AGENTS.md](file://../AGENTS.md)
- **Project Specific Rules**: [project_rules.md](file://./rules/project_rules.md)
- **Database Schema**: [schema.md](file://./schema.md)
- **Design Decisions**: [adr.md](file://./adr.md)
- **Sprint Archives**: [archive/](file://./archive/)
