# Agent Core Memory

> **Memory Schema Version**: 5.0.0  
> **Target System**: Antigravity Agent Core
> **Active Guidelines**: Read [AGENTS.md](file://../AGENTS.md) and [.agents/project_rules.md](file://./project_rules.md) for execution details. Keep this file under 100 lines at all times.

---

## 1. Git State & Infrastructure Runtime
- **Active Branch**: main
- **Last Commit Reference**: f1a09eb
- **Active Pull Request Target**: `main`
- **Infrastructure Health Status**:
  - Database: `HEALTHY`
  - Cache/Broker: `HEALTHY`
  - Primary API Server: `HEALTHY`

---

## 2. Active Epic & Sub-Tasks Execution Matrix
- **Primary Epic**: World-Class Agent Workspace Core Improvements
- **Current Task Target**: Review and improve bootstrap.sh and bootstrap.ps1 for enterprise and world-class grade safety
- **State Flag**: `COMPLETED`

### Sprint Tasks Checklist
- [x] Review and improve bootstrap.sh and bootstrap.ps1 for enterprise and world-class grade safety
- [x] Refine bootstrapping sequence, checkbox lifecycle, and real-time schema/library updates in AGENTS.md and project_rules.md
- [x] Run /grill-me alignment and document outcomes in task_teamwork_rules.md
- [x] Implement branch-specific dynamic workflow archiving in helper.sh
- [x] Add .antigravityignore configuration to exclude dependency and build files
- [x] Document setup, teamwork guidelines, and changelog in README.md and CHANGELOG.md
- [x] Implement Git pre-commit and post-commit hook automations
- [x] Update README.md with the simplified Git commit workflow and hook automations
- [x] Implement Check 7 Gitignore Compliance validation check in validate.sh and bootstrap.sh
- [x] Relocate CHANGELOG.md to project root and update README link
- [x] Implement Check 8 Memory State Flag Enforcement validation check in validate.sh and bootstrap.sh
- [x] Create commit-msg Git hook template to validate conventional commit formats
- [x] Support -Version parameter in bootstrap.ps1 for pinned installation
- [x] Run validate.sh and commit changes









---

## 3. Relayed Context & Handover Notes
- **Last Active Agent**: Gemini (Antigravity Agent)
- **Last Action Completed**: Committed fixed bootstrapper with robust command parsing, PS1 force flag, and timeout fetch.
- **Next Planned Action**: Document and commit Handover Protocol improvements to AGENTS.md, project_rules.md, and bootstrap.sh.
- **Blockers / Runtime Notes**: None. Working tree is clean.

---

## 4. Reference Links Index
- **Core Guidelines**: [AGENTS.md](file://../AGENTS.md)
- **Project Specific Rules**: [project_rules.md](file://./project_rules.md)
- **Database Schema**: [schema.md](file://./schema.md)
- **Design Decisions**: [adr.md](file://./adr.md)
- **Sprint Archives**: [archive/](file://./archive/)
