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
- **Workspace Git Tracking**: Never ignore `.agents/` or `AGENTS.md` in `.gitignore` (except `.agents/locks/`). Commit all memory, schemas, and ADR files to Git to ensure proper multi-agent synchronization.
- **Upstream Sync Gate**: You must run `./.agents/scripts/helper.sh validate` before beginning code changes to check if the branch is behind origin. If it is behind, stop and ask the user to pull first.
- **Discussion and Design Plans**: Document all `/grill-me` outcomes and execution plans under `.agents/workflows/task_<task_name>.md`. Never log task-specific plans or checklists globally or in the main memory ledger.
- **Database & API Contracts**: Every DB/API design change must immediately be added as a domain schema under `.agents/schemas/` and mapped in the main `.agents/schema.md` index file, and documented as an ADR in `.agents/adr.md`.

