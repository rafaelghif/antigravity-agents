# Project Architecture Blueprint (PAB)

This file defines the specific technical stack, directory boundaries, coding standards, and system dependencies for this project.

---

## 1. Stack & Directory Boundaries
- **Primary Language/Framework**: Unknown
- **Directory Structure**:
  - `tests/` -> Project workspace component
  - `config/` -> Project workspace component

## 2. Architectural Conventions
- **Architectural Pattern**: Standard Model-View-Controller (MVC)
- **Boundary insulation**: Core domain logic must remain completely independent of external libraries, databases, and frameworks.

## 3. Spacing & Styling Standards
- **Linter command**: `echo 'No linter found'`
- **Build validation**: `echo 'No build command needed'`
- **Test runner command**: `echo 'No test suite found'`
- **Follow formatting**: Follow standard formatting guidelines for Unknown development.

## 4. Security & External Services
- **Database/ORM**: None detected
- **Required Configuration Variables**:
  - No configuration parameters detected.

## 5. Long-Term Impact & 10-Year Maintainability Gates
- **Impact-Analysis Check**: Before installing new packages, modifying database structures, or altering cross-domain APIs, the agent must run the `impact-analysis` skill and document design rationales.
- **Architectural Boundary Gate**: Domain business logic must remain completely independent of libraries and frameworks (e.g. database schemas, server frameworks).
- **Code Sustainability**: Code must prioritize long-term readability over brevity. Avoid complex runtime assumptions, unverified imports, or undocumented configuration requirements.
- **Ambiguity Gate**: If any implementation details are unclear, halt and ask the user for confirmation first.

## 6. Multi-Agent & Teamwork Constraints
- **Autonomous Bootstrapping Sequence**: Before performing any edit or script action, you MUST read the core files in sequence: `AGENTS.md`, `.agents/project_rules.md`, `.agents/schema.md`, and `.agents/memory.md`. No file writes or terminal runs are allowed prior to this initialization.
- **Workspace Git Tracking**: Never ignore `.agents/` or `AGENTS.md` in `.gitignore` (except `.agents/locks/`). Commit all memory, schemas, dynamic workflows, and ADR files to Git to ensure proper multi-agent synchronization.
- **Upstream Sync Gate**: You must run `./.agents/scripts/helper.sh validate` before beginning code changes to check if the branch is behind origin. If it is behind, stop and ask the user to pull first.
- **Discussion and Design Plans**: Document all `/grill-me` outcomes and execution plans under `.agents/workflows/task_<task_name>.md`. Never log task-specific plans or checklists globally or in the main memory ledger.
- **Real-Time Schema & Dependency Updates**: Any discussion on database models, API routes, or third-party libraries must be documented in the repository *immediately* before starting code edits:
  - Database structures must be saved under `.agents/schemas/` and registered in `.agents/schema.md`.
  - Technologies/libraries must be documented in `.agents/project_rules.md` and their respective workspace configuration files (`package.json`, `go.mod`, etc.).
  - Architectural decisions must be documented as a new ADR entry in `.agents/adr.md`.
- **Strict Checklist Checkbox Rules**: Checklists must follow a strict 3-state lifecycle. Only ONE task can be marked `[/]` at a time across the entire workspace. Do not change a task checklist state to `[x]` until verification has passed and the changes have been staged and committed in the completed state.
