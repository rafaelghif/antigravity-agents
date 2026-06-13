---
name: project-rules
activation: Always On
description: "Project architecture blueprint and technical stack rules."
---

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
- **Autonomous Bootstrapping Sequence**: Before performing any edit or script action, you MUST read the core files in sequence: `AGENTS.md`, `.agents/rules/project_rules.md`, `.agents/schema.md`, and `.agents/memory.md`. No file writes or terminal runs are allowed prior to this initialization.
- **Workspace Git Tracking**: Never ignore `.agents/` or `AGENTS.md` in `.gitignore` (except `.agents/locks/`). Commit all memory, schemas, dynamic workflows, and ADR files to Git to ensure proper multi-agent synchronization.
- **Upstream Sync Gate**: You must run `./.agents/scripts/helper.sh validate` before beginning code changes to check if the branch is behind origin. If it is behind, stop and ask the user to pull first.
- **Discussion and Design Plans**: Document all `/grill-me` outcomes and execution plans under `.agents/workflows/task_<task_name>.md`. Never log task-specific plans or checklists globally or in the main memory ledger.
- **Real-Time Schema & Dependency Updates**: Any discussion on database models, API routes, or third-party libraries must be documented in the repository *immediately* before starting code edits:
  - Database structures must be saved under `.agents/schemas/` and registered in `.agents/schema.md`.
  - Technologies/libraries must be documented in `.agents/rules/project_rules.md` and their respective workspace configuration files (`package.json`, `go.mod`, etc.).
  - Architectural decisions must be documented as a new ADR entry in `.agents/adr.md`.
- **Strict Checklist Checkbox Rules**: Checklists must follow a strict 3-state lifecycle. Only ONE task can be marked `[/]` at a time across the entire workspace. Do not change a task checklist state to `[x]` until verification has passed and the changes have been staged and committed in the completed state.
- **Handover Relayed Context**: Before logging off or ending a turn, you MUST write concise handover notes (under 5 lines) in the active memory ledger under `## 3. Relayed Context & Handover Notes`. This ensures any incoming agent or new account knows exactly where to resume work without token waste.

## 7. Autonomous Operational Scripts & Commands
The agent must execute workspace scripts automatically without manual user guidance or request under the following conditions:
- **Project Discovery**: If `.agents/rules/project_rules.md` is empty or generic, run `./.agents/scripts/helper.sh recon` immediately.
- **Initial Verification**: Run `./.agents/scripts/helper.sh validate` and `./.agents/scripts/helper.sh doctor` as the first step of any edit cycle.
- **Module Lock**: Before editing any code within a directory (e.g. `apps/backend`), run `./.agents/scripts/helper.sh lock <module_name>`.
- **API Synchronization**: When backend model schemas or API paths change, run `./.agents/scripts/helper.sh sync-api` to sync types to the frontend.
- **Skill Scaffolding**: To autonomously create new specialized skills when gaps are detected, run `./.agents/scripts/helper.sh create-skill <name> [description]`.
- **Skill Compliance Check**: To verify that all registered skills conform to Keep-a-Skill compliance and possess executable scripts, run `./.agents/scripts/helper.sh list-skills`.
- **Code Validation**: Run `./.agents/scripts/helper.sh validate` before staging and preparing any commit.
- **Pre-Merge Cleanup**: Run `./.agents/scripts/helper.sh archive` before completing a pull request task to clean up dynamic workspaces.
- **Token Budget Compliance**: The agent must log its token usage using `./.agents/scripts/helper.sh log-usage <token_count>` at the end of each turn. If validation warns that token usage has reached the threshold, the agent must immediately save its progress, update the task checklist target in `memory.md` to `IN_PROGRESS`, and log off for handover.

