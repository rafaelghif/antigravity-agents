# Agent Core Memory

> **Memory Schema Version**: 5.0.0  
> **Target System**: Antigravity Agent Core
> **Active Guidelines**: Read [AGENTS.md](file://../AGENTS.md) and [.agents/rules/project_rules.md](file://./rules/project_rules.md) for execution details. Keep this file under 100 lines at all times.

---

## 1. Git State & Infrastructure Runtime
- **Active Branch**: [branch-name]
- **Last Commit Reference**: [commit-hash]
- **Active Pull Request Target**: `main`
- **Infrastructure Health Status**:
  - Database: `HEALTHY`
  - Cache/Broker: `HEALTHY`
  - Primary API Server: `HEALTHY`

---

## 2. Active Epic & Sub-Tasks Execution Matrix
- **Primary Epic**: API Key Auto-Rotation Support
- **Current Task Target**: Implement api-profile subcommand and CLI auto-rotation
- **State Flag**: `COMPLETED`

### Sprint Tasks Checklist
- [x] Implement api-profile subcommand in helper.sh, helper.ps1, and bootstrap.sh
- [x] Implement api_keys.example template and update .gitignore/.antigravityignore templates
- [x] Implement runner wrapper script/skill for auto-rotation
- [x] Update README.md and CHANGELOG.md with API profile features
- [x] Verify validation and clean workspace

---

## 3. Relayed Context & Handover Notes
- **Last Active Agent**: Antigravity Gemini 3.5 Flash
- **Last Action Completed**: Implemented api-profile subcommand, validation checks, and wrapper script for API key auto-rotation
- **Next Planned Action**: Push changes to origin (git push) and deploy the updated bootstrap.sh on new workspaces
- **Blockers / Runtime Notes**: None. Workspace is fully clean, validated, and committed.

---

## 4. Reference Links Index
- **Core Guidelines**: [AGENTS.md](file://../AGENTS.md)
- **Project Specific Rules**: [project_rules.md](file://./rules/project_rules.md)
- **Database Schema**: [schema.md](file://./schema.md)
- **Design Decisions**: [adr.md](file://./adr.md)
- **Sprint Archives**: [archive/](file://./archive/)
