#!/usr/bin/env bash

# Antigravity Agent Workspace Bootstrapper
# This script initializes a clean, decoupled agent memory and protocol setup in any project repository.

set -euo pipefail

# Parse arguments
FORCE_OVERWRITE=false
UPDATE_ONLY=false
while [ $# -gt 0 ]; do
    case "$1" in
        -f|--force)
            FORCE_OVERWRITE=true
            shift
            ;;
        -u|--update)
            UPDATE_ONLY=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# Determine color support
RED=''
GREEN=''
YELLOW=''
BLUE=''
BOLD=''
NC=''
if [ -t 1 ] && command -v tput >/dev/null 2>&1; then
    ncolors=$(tput colors)
    if [ -n "$ncolors" ] && [ "$ncolors" -ge 8 ]; then
        RED='\033[0;31m'
        GREEN='\033[0;32m'
        YELLOW='\033[0;33m'
        BLUE='\033[0;34m'
        BOLD='\033[1m'
        NC='\033[0m'
    fi
fi

log_info() { echo -e "${BLUE}${BOLD}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}${BOLD}[PASS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}${BOLD}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}${BOLD}[FAIL]${NC} $1" >&2; }

echo "=========================================================="
log_info "Checking System Prerequisites..."
echo "=========================================================="

if ! command -v git >/dev/null 2>&1; then
    log_error "Git is required but not installed! Please install Git first."
    exit 1
fi
log_success "Git is installed."

# Helper function to write templates safely (preserves existing files unless -f/--force or -u/--update is specified)
write_template_safe() {
    local target_file="$1"
    if [ -f "$target_file" ] && [ "$FORCE_OVERWRITE" = "false" ]; then
        local is_system_file=false
        if [ "$target_file" = "AGENTS.md" ] || [[ "$target_file" =~ \.agents/scripts/ ]] || [[ "$target_file" =~ \.agents/hooks/ ]] || [[ "$target_file" =~ \.agents/skills/ ]]; then
            is_system_file=true
        fi

        if [ "$UPDATE_ONLY" = "true" ] && [ "$is_system_file" = "true" ]; then
            log_info "Updating system file: $target_file..."
            cat > "$target_file"
        else
            log_warning "$target_file already exists. Preserving current file."
        fi
    else
        log_info "Writing template to $target_file..."
        cat > "$target_file"
    fi
}

# Helper function to install Git hooks safely without breaking existing setups
install_git_hook_safe() {
    local hook_name="$1"
    local source_hook=".agents/hooks/$hook_name"
    local target_hook=".git/hooks/$hook_name"

    if [ ! -f "$source_hook" ]; then
        return 0
    fi

    if [ -f "$target_hook" ]; then
        # Check if it contains Antigravity marker
        if grep -q "# Antigravity Agent" "$target_hook"; then
            log_info "Updating existing Antigravity Git hook: $hook_name"
            cp "$source_hook" "$target_hook"
            chmod +x "$target_hook"
        else
            local backup_hook="$target_hook.backup"
            if [ -f "$backup_hook" ]; then
                log_warning "Custom Git hook '$hook_name' detected, but backup '$hook_name.backup' already exists. Overwriting current hook, preserving backup."
                rm -f "$target_hook"
            else
                log_warning "Custom Git hook '$hook_name' detected. Backing up to '$hook_name.backup' and chaining."
                mv "$target_hook" "$backup_hook"
            fi
            cp "$source_hook" "$target_hook"
            chmod +x "$target_hook"
        fi
    else
        log_info "Installing Git hook: $hook_name"
        cp "$source_hook" "$target_hook"
        chmod +x "$target_hook"
    fi
}

# Initialize Git if not present (ensures doctor and hooks pass seamlessly)
if [ ! -d .git ]; then
    log_info "Git repository not detected. Initializing Git repository..."
    git init
    git branch -m main
fi

# 1. Create directory structure
mkdir -p .agents/skills/codebase-recon
mkdir -p .agents/skills/git-ops
mkdir -p .agents/skills/test-driven-patch
mkdir -p .agents/skills/infra-provisioner
mkdir -p .agents/skills/security-ci-audit
mkdir -p .agents/skills/code-review
mkdir -p .agents/skills/impact-analysis
mkdir -p .agents/workflows
mkdir -p .agents/archive
mkdir -p .agents/locks
mkdir -p .agents/schemas
mkdir -p .agents/scripts
mkdir -p .agents/hooks

# 2. Write AGENTS.md (Global Agent Protocol) to project root
write_template_safe "AGENTS.md" << 'EOF'
# Global Agent Protocol (GAP)

This document dictates the absolute boundaries, operational procedures, memory constraints, and quality gates for all AI agent operations in this workspace. Compliance is mandatory for every agent execution.

---

## 1. Bootstrapping & Cognitive Alignment
- **Autonomous Bootstrapping**: At the beginning of any session or task context, the agent MUST read the core files. The agent MUST NOT perform any file edits, command execution, or code modifications prior to reading these files. To maximize prompt prefix cache hits, the agent or the loading interface MUST retrieve these files in the exact sequence from *Most Static* to *Most Dynamic*:
  1. The Global Agent Protocol (this file: [AGENTS.md](file://./AGENTS.md)).
  2. The Project-Specific Rules, if available (e.g. [.agents/project_rules.md](file://./.agents/project_rules.md)).
  3. The Schema Reference database, if available (e.g. [.agents/schema.md](file://./.agents/schema.md)).
  4. The Active Memory Ledger ([.agents/memory.md](file://./.agents/memory.md)).
- **Autonomy Principle & Strict Alignment**: The agent must rely on these documents and the codebase layout rather than asking the user repetitive or basic design questions. If a design pattern is missing or a user's instruction is ambiguous, default to standard industry best practices or ask a direct, clear multiple-choice question.
- **Zero-Halucination Rule**: Under no circumstances should the agent make assumptions about dependencies, compiler configurations, path paths, or API structures. If they are not detailed in the files read during bootstrapping, verify them immediately using read tools before taking actions.

---

## 2. Zero-Hallucination & Import Verification Gates
- **Fact-Checking over Guessing**: Never assume a file exists, a package is installed, or a function signature is correct.
- **Symbol & Command Verification Gate**: Before writing an import statement, invoking a function, or executing a terminal command/script, the agent MUST run `view_file` or `grep_search` to verify:
  1. The file path and module export spelling are correct.
  2. The package, linter, or script command exists in the workspace configuration files (e.g., `package.json`, `go.mod`, or `.agents/project_rules.md`). Do not guess or execute unverified third-party commands.
- **Batch Verification and Line Capping**: To prevent token bloat during verification, the agent MUST use precise `StartLine` and `EndLine` parameters in `view_file` to read only the imports/definitions needed, or run batch `grep_search` operations instead of parsing entire source files.
- **verbatim Reference**: When documenting compile, lint, or test failures, paste the exact stack traces and logs verbatim instead of describing them in general terms.


---

## 3. AI Prompt Caching & Token Optimization
To maximize prompt execution speed, leverage model-side context caching, and avoid token exhaustion, agents must strictly follow these caching protocols:
- **Cache-Friendly Memory Split**: Decouple static files (`AGENTS.md`, `project_rules.md`, `adr.md`) from dynamic ones. Static files must remain stable to hit 100% prompt cache.
- **Active Memory Cap**: Keep [.agents/memory.md](file://./.agents/memory.md) under 100 lines at all times. Once a milestone is achieved, immediately archive the checklist to [.agents/archive/](file://./.agents/archive/).
- **Hierarchical Task Trees (Memory Scaling)**: For large projects or complex tasks, the agent MUST NOT store granular, detailed checklists in `memory.md`. Instead, create task-specific workflow files under `.agents/workflows/task_<name>.md`. Track only high-level epic milestones in the core `memory.md`, and lazy-load the workflow files as needed.
- **Targeted File Reads**: NEVER read entire source files when looking for small details. Always use precise `StartLine` and `EndLine` parameters in file-viewing tools to preserve prefix cache hits.
- **Respect .antigravityignore**: The agent MUST strictly respect `.antigravityignore` patterns. Never read, search, or list files matching these patterns to optimize token usage and eliminate hallucination hazards.
- **Persistent Terminal Shells**: Reuse active terminal sessions by passing `RunPersistent: true` and specifying `RequestedTerminalID`. This avoids spawning new bash subshells, which bloats terminal history logs.


---

## 4. Multi-Agent & Teamwork Coordination
To operate seamlessly in collaborative environments with other developers and autonomous agents:
- **Isolated Feature Branches**: The agent must operate exclusively on the feature branch created by the user. Creating, switching, pushing, or pulling branches is forbidden for the agent; these tasks are strictly handled by the user.
- **Federated Git-Backed Memory & Git-Tracked Workspace**: Memory and configuration reside in the repository. All files under `.agents/` (including `memory.md`, `project_rules.md`, `adr.md`, `schema.md`, `schemas/`, and `workflows/`) and `AGENTS.md` MUST be committed to Git to synchronize context across different developer accounts and agents. The transient locks under `.agents/locks/` are the only excluded files.
- **Upstream Synchronization Gate**: Before starting any task or code modifications, the agent MUST run `.agents/scripts/helper.sh validate` to verify that the local repository is not behind its upstream branch (e.g. `origin/<branch>`). If the local repository is behind, the agent MUST halt execution and prompt the user to run `git pull` to ensure synchronization.
- **Design & /grill-me Alignment Documentation**: Whenever a design interview, `/grill-me` session, or architectural alignment is completed, the agent MUST immediately save the resulting execution plan to a new task workflow file at `.agents/workflows/task_<task_name>.md`. This file acts as the single source of truth for the task's execution plan, architectural decisions, and schema changes, and must be committed to Git.
- **Real-Time Schema & Library Synchronization**: Any discussion regarding changes to the database structure, API contracts, dependencies, libraries, or architectural patterns must be documented *immediately* in the corresponding workspace files *before* writing any code:
  - Database schema changes must immediately update the domain-driven schemas under `.agents/schemas/` and the master index `.agents/schema.md`.
  - Technology or library dependencies (e.g. npm package additions, go modules) must immediately update `.agents/project_rules.md` and the workspace package configuration files (e.g. `package.json`, `go.mod`).
  - Architectural changes must immediately be recorded as a new Architectural Decision Record (ADR) in `.agents/adr.md`.
- **Active Lockfile Protocol**: To prevent parallel agents/developers from editing the same module:
  - Acquire the lock by running `.agents/scripts/helper.sh lock <module_name>`. This creates a lockfile under `.agents/locks/<module_name>.lock`.
  - Before editing any file, check if a lock exists. If it does, do NOT proceed. Coordinate with the lock owner, wait for release, or notify the user.
  - Release the lock immediately upon committing your changes by running `.agents/scripts/helper.sh unlock <module_name>`.
- **Pre-Merge Compaction Protocol**: To prevent merge conflicts on `memory.md` during integration:
  - Before merging a branch into `main`/`master`, the agent/developer MUST archive their active task checklist by running `.agents/scripts/helper.sh archive`.
  - This automatically saves the checklist to `.agents/archive/sprint_<branch_name>.md` and resets the active checklist in `memory.md`.
  - Commit this compaction: `chore(memory): archive active checklists for merge`.
- **Peer Review Handover**: When submitting a PR, the agent/developer must write a review guide at `.agents/workflows/pr_review_<branch_name>.md` detailing:
  1. **Scope of Work**: Added/modified files and symbols.
  2. **Verification Logs**: Verbatim test suite outputs proving compilation and test completion.
  3. **Schema Changes**: Visual mappings of any table/field modifications.
  4. **Code References**: Clickable file links pointing to key files for review.

---

## 5. Stateful Task Checklist & Handover Notes
The active checklist inside [.agents/memory.md](file://./.agents/memory.md) and any dynamic workflow files must strictly follow this lifecycle:
- \`[ ]\` **Unstarted**: Proposed task.
- \`[/]\` **In Progress**: Active task. **CRITICAL**: Only ONE task can be marked \`[/]\` at a time across the entire workspace (including main \`memory.md\` and any active dynamic workflow file). The agent must focus 100% on this task. Any code modifications must strictly match the current active task scope.
- \`[x]\` **Completed**: Done, verified, and committed. A task must **only** be marked \`[x]\` after:
  1. Code compile/tests pass.
  2. Workspace validation checks via \`.agents/scripts/helper.sh validate\` pass.
  3. Changes have been staged and committed to Git (meaning the task is committed in a completed state).

- **Handover Protocol (Relayed Context)**: Before completing a turn, finishing a milestone, or handing over the repository to another agent/developer account, the agent MUST write a concise summary (under 5 lines) in [.agents/memory.md](file://./.agents/memory.md) under \`## 3. Relayed Context & Handover Notes\`. This allows the incoming agent to seamlessly resume work in a new session without reading long transcripts or wasting tokens.

---

## 6. The Atomic Commit Loop (Strict Discipline)
Every code mutation must execute in an atomic, sequential loop:
1. **Sync**: Verify that the workspace is on the correct branch and that there are no uncommitted changes (other than locks or memory files).
2. **Lock**: Run `.agents/scripts/helper.sh lock <module>` and set the target task to `[/]` in `memory.md`.
3. **Edit**: Modify a single file or write a test (under TDD guidelines).
4. **Commit Preparation**: Update the task checklist state to `[x]` and state flag to `COMPLETED` in `memory.md` (or the dynamic workflow checklist).
5. **Commit**: Stage files and execute a standard Git commit using conventional format: `git commit -m "type(scope): description"`.
   - **Automated Validation**: The Git `pre-commit` hook automatically runs `./.agents/scripts/validate.sh` and the project linter/tests. The commit will automatically abort on failure.
   - **Automated Sync & Unlock**: Upon a successful commit, the Git `post-commit` hook automatically updates `memory.md` with the new branch/commit hash and releases all active locks.



---

## 7. Self-Correction & Troubleshooting Playbook
If build tools, linters, or test suites crash, run this diagnostic checklist:
1. **Identify Module Context**: Determine if the crash is inside the frontend, backend, or database migrations container.
2. **Review Environment Configs**: Verify if `.env` values or docker containers are running and healthy.
3. **Trace Missing Imports**: If compiler reports missing types/packages, search the package configs (`package.json`, `go.mod`, etc.) to check if dependencies were installed or if aliases (e.g., tsconfig paths) are resolved correctly.
4. **Mock External Outages**: During test execution, mock external API dependencies (payment gateways, Firebase, AWS S3, etc.) to ensure tests run deterministically and fast without hitting real remote services.

---

## 8. Self-Improvement & Meta-Refactoring Protocol
The agent must continuously optimize its own tools, protocols, and developer guidelines to maintain a 1% world-class execution standard:
- **Refinement Triggers**: If a lint error, type mismatch, or testing bottleneck repeats more than 3 times, the agent MUST immediately refine [.agents/project_rules.md](file://./.agents/project_rules.md) or update the respective skill file to document the solution permanently.
- **Dynamic Skill Creation**: If the agent identifies a missing capability (e.g. a skill for code auditing, packaging, or migration validation), it must proactively define it under `.agents/skills/<skill_name>/SKILL.md` and use it.
- **Grounding Gate**: All proposed self-improvements and optimizations must be 100% realistic and functional. Do not suggest or create configurations for tools that are not installed or are unavailable in the workspace environment.

---

## 9. Modular Document Grouping (Domain-Driven Schemas)
To optimize prompt caching and prevent context window bloat:
- **Index Reference**: The main [.agents/schema.md](file://./schema.md) file acts strictly as a high-level index mapping domain-specific database and API layouts.
- **Domain Segmentation**: Schemas and contracts must be grouped by function under [.agents/schemas/](file://./schemas/) (e.g., `admin_and_auth.md`, `assets_and_taxonomy.md`).
- **Targeted Reading**: When modifying a resource, the agent MUST ONLY load the relevant domain schema file. Loading the entire database schema map for localized edits is strictly forbidden.
- **Incremental Growth & Registration Gate**: These domain-specific schemas grow incrementally. Every file created under `.agents/schemas/` MUST be registered as a markdown link in the primary `.agents/schema.md` index. The validation suite programmatically checks for registration compliance.
- **Decision Tracking (ADRs)**: Any new domain or database schema design decision must also have an associated Architectural Decision Record entry in `.agents/adr.md`.

---

## 10. Autonomous Adaptation & Self-Configuration Protocol
When the agent starts execution in a workspace, it must check if the project-specific blueprints (.agents/project_rules.md and .agents/schema.md) are either missing, empty, or contain default templates.
If the blueprints are not initialized for the current project:
1. **Trigger Autonomous Reconnaissance**: Immediately execute `./.agents/scripts/helper.sh recon` to automatically discover the tech stack, directory boundaries, build/test/lint commands, Relational DB/ORM integrations, and environment variable configuration template.
2. **Interactive User Alignment**: Present the auto-detected stack and boundaries to the user for quick confirmation or adjustments.
3. **Refine Blueprint**: Adjust [.agents/project_rules.md](file://./.agents/project_rules.md) and [.agents/schema.md](file://./.agents/schema.md) based on user confirmation.
4. **Populate Database Schema Map**:
   - Map all relational database models, tables, columns, and API routes found, organizing them into domain-driven schemas under [.agents/schemas/](file://./.agents/schemas/).
   - Update the high-level index map inside [.agents/schema.md](file://./.agents/schema.md) to link to these domain schemas.
5. **Initialize Active Memory**:
   - Populate [.agents/memory.md](file://./.agents/memory.md) with the verified system topology, active branch, and initial task checklist.
6. **Autoprovision Commit**: Commit these initialized configuration files using Git: `chore(agent): autodetect project stack and initialize memory blueprints`.
Once the blueprints are populated, the agent must strictly follow the detected project rules for all code mutations.

---

## 11. Long-Term Impact & Architectural Integrity Gates
To prevent technical debt and ensure the system remains maintainable, secure, and performant over a 10-year lifespan, all agent modifications must satisfy these checks:
- **Mandatory Impact Auditing**: Before proposing any major code change, architectural restructuring, or package import, the agent MUST run the `impact-analysis` skill to identify downstream dependency breaks, security vulnerabilities, or performance bottlenecks.
- **Architectural Boundary Insulation**: Maintain pure layer decoupling. Never mix infrastructure details (like database models, network clients, framework-specific wrappers) with core business logic.
- **Strict User Consultations**: In situations of ambiguity, high security risk, database schema migrations, or backward-incompatible API changes, the agent MUST halt execution and consult the user with options before writing code.
- **Self-Improving Memory Feedback Loop**: The agent must continuously audit its performance. If any structural bugs or compilation failures occur multiple times, the agent must proactively update `.agents/project_rules.md` to prevent future errors.
EOF
# 3. Write .agents/memory.md template
write_template_safe ".agents/memory.md" << 'EOF'
# Agent Core Memory

> **Memory Schema Version**: 5.0.0  
> **Target System**: [Project Name]
> **Active Guidelines**: Read [AGENTS.md](file://../AGENTS.md) and [.agents/project_rules.md](file://./project_rules.md) for execution details. Keep this file under 100 lines at all times.

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
- **Primary Epic**: [Active Epic / Feature Group]
- **Current Task Target**: [Current target being worked on]
- **State Flag**: `IN_PROGRESS`

### Sprint Tasks Checklist
- [ ] Implement core logic
- [ ] Write unit tests
- [ ] Verify build and tests pass

---

## 3. Relayed Context & Handover Notes
- **Last Active Agent**: [agent-id / model]
- **Last Action Completed**: [brief description of last done action]
- **Next Planned Action**: [immediate next task to execute]
- **Blockers / Runtime Notes**: [any active errors, pending verification, or configs]

---

## 4. Reference Links Index
- **Core Guidelines**: [AGENTS.md](file://../AGENTS.md)
- **Project Specific Rules**: [project_rules.md](file://./project_rules.md)
- **Database Schema**: [schema.md](file://./schema.md)
- **Design Decisions**: [adr.md](file://./adr.md)
- **Sprint Archives**: [archive/](file://./archive/)
EOF

# 4. Write .agents/project_rules.md template
write_template_safe ".agents/project_rules.md" << 'EOF'
# Project Architecture Blueprint (PAB)

This file defines the specific technical stack, directory boundaries, coding standards, and system dependencies for this project.

---

## 1. Stack & Directory Boundaries
- **Primary Language/Framework**: [e.g. Node/TypeScript, Python/FastAPI, Go, Rust]
- **Directory Structure**:
  - `src/` -> Application source code
  - `tests/` -> Test suites

## 2. Architectural Conventions
- [Describe the architecture pattern here, e.g. Clean Architecture, MVC, Hexagonal, simple service-repository layer]
- [Define rules regarding coupling and boundaries, e.g. UI layers must not call database adapters directly]

## 3. Spacing & Styling Standards
- [Define layout spacing, form guidelines, or styling patterns if frontend project, or code style rules]

## 4. Security & External Services
- [Define database transaction rules, third-party adapters (S3, Auth, Payment), and caching protocols]

## 5. Long-Term Impact & 10-Year Maintainability Gates
- **Impact-Analysis Check**: Before installing new packages, modifying database structures, or altering cross-domain APIs, the agent must run the `impact-analysis` skill and document design rationales.
- **Architectural Boundary Gate**: Domain business logic must remain completely independent of libraries and frameworks (e.g. database schemas, server frameworks).
- **Code Sustainability**: Code must prioritize long-term readability over brevity. Avoid complex runtime assumptions, unverified imports, or undocumented configuration requirements.
- **Ambiguity Gate**: If any implementation details are unclear, halt and ask the user for confirmation first.
EOF

# 5. Write .agents/schema.md template
write_template_safe ".agents/schema.md" << 'EOF'
# Technical Schema & Reference Database (SRD) - Index Map

This file serves as the high-level index for the project's technical schemas, database specifications, and API contracts.

---

## 1. Domain Schemas Index
- [Default Module](file://./schemas/default_module.md) -> Reference: [default_module.md](file://./schemas/default_module.md)
EOF

# 6. Write default_module.md template
write_template_safe ".agents/schemas/default_module.md" << 'EOF'
# Schema: Default Module

Description of tables and APIs in this domain.

---

## 1. Relational Database Tables
- `example_table` (id, name)
EOF

# 7. Write .agents/adr.md template
write_template_safe ".agents/adr.md" << 'EOF'
# Architectural Decision Records (ADR)

This document registers the historical technical design decisions, rationales, and consequences accepted in this project.

---

### ADR-001: [Title of Decision]
- **Status**: [Proposed / Accepted / Superceded]
- **Context**: [Describe the problem context and alternatives]
- **Decision**: [Describe the decision made]
- **Consequences**: [Describe the result and impact of this decision]
EOF

# 8. Write skills
# codebase-recon SKILL.md
write_template_safe ".agents/skills/codebase-recon/SKILL.md" << 'EOF'
---
name: codebase-recon
description: Maps the repository architecture, file layout, and config structures. Run this first before initiating any codebase changes or feature designs.
---

# Codebase Reconnaissance Skill

## 1. Input Specification
- **Search Path Target**: Workspace root folder.
- **Exclusion Filters**: Ignore all build/transient files or package locks (`node_modules`, `dist`, `build`, `package-lock.json`, `.git`, etc.).

## 2. Operational Procedures
1. **Directory Structure Discovery**:
   - Scan workspace root to locate key configuration files (e.g. `package.json`, `tsconfig.json`, `go.mod`, `Cargo.toml`, `requirements.txt`, `composer.json`, `gemfile`).
   - Identify active subprojects, monorepo partitions, or key folder boundaries (e.g. `src/`, `apps/`, `lib/`, `controllers/`, `views/`).
2. **Environment Profile Scanning**:
   - Inspect `.env.example`, `config/` files, or Docker Compose setups to map system dependencies (databases, caching hosts, external APIs, object storage).
3. **Relational & API Contract Mapping**:
   - Scan for data models, ORM entities, or database schemas (e.g., `.entity.ts`, `.go` models, migrations folder, SQL scripts).
   - Scan for API routes, controller files, or GraphQL schemas to map available endpoints.
4. **Boundary Verification**:
   - Verify decoupling boundaries. Confirm that frontend layers do not directly import backend files, and business domains remain insulated from framework-specific wrappers.

## 3. Decision Matrix
- **Are there database schema definitions?**
   - **YES**: Limit scanning to folders containing database configuration, entities, or migration scripts.
- **Are there separate frontend and backend workspaces?**
   - **YES**: Document their distinct routes, ports, run environments, and interface sharing mechanisms.
- **Are there environment variables?**
   - **YES**: Cross-reference `.env.example` with the active configuration loading files to ensure matching parameters.

## 4. Error Mitigation Tree
- **No package configurations found at workspace root**:
  - *Mitigation*: Fall back to recursive search for nested workspaces up to level-3 subdirectories.
- **Alias imports are unresolved**:
  - *Mitigation*: Consult compiler/bundler configurations (e.g. `tsconfig.json` paths, webpack alias, vite config) to resolve path mappings.

## 5. Output Protocol
Save the reconnaissance summary in the project's memory ledger (e.g., `schema.md` or a codebase map section in `memory.md`) detailing:
1. Workspace folders and project roles.
2. Relational database schema layout.
3. Active API endpoints and contract directories.
4. Build tools and local testing environment commands.
EOF

# git-ops SKILL.md
write_template_safe ".agents/skills/git-ops/SKILL.md" << 'EOF'
---
name: git-ops
description: Manages local Git branches and executes version control flows enforcing the strict Conventional Commits specification.
---

# Git Operations Skill

## 1. Input Specification
- **Operation Scope**: Feature development, bug fixing, refactoring, or infrastructure adjustments.
- **Changed Files List**: Selected list of files modified during the current subtask.
- **Target Branch**: Typically a feature branch branched off `main`/`master`.

## 2. Operational Procedures & Checklist
1. **Branch Hygiene & Naming Check**:
   - Ensure you are working on the user's checked-out feature branch.
   - You must NOT create, delete, switch, merge, push, or pull branches.
   - If the active branch is `main` or `master`, or if a branch operation is required, halt and instruct the user to handle the git branch operation.
2. **Pre-Staging Verification**:
   - Run compilation and tests locally (e.g. `npm run build` / `npm run test` or language-equivalent tools) before staging any files.
3. **Secret Scan Check**:
   - Ensure you are not staging `.env`, `.env.local`, credentials files, or private keys.
   - Run `git status` to see untracked and modified files.
4. **Selective Staging**:
   - Stage files individually rather than staging all: `git add <path/to/modified/file>`.
   - Run `git diff --cached` to inspect lines added and verify that no debugging statements or temporary passwords are being committed.
5. **Commit Assembly**:
   - Compose the message strictly matching: `type(scope): description`
     - **Types**: `feat` (new features), `fix` (bug fixes), `refactor` (code restructuring), `chore` (infra, build tools, dependency adjustments, memory updates).
     - **Scopes**: Use the project-specific module name or workspace directory (e.g. `backend`, `frontend`, `infra`, `auth`, `shared`, `db`).
     - *Example*: `fix(frontend): adjust asset detail layout overlay overflow`
6. **Local Commit Verification**:
   - Verify that the commit is successfully completed locally.
   - Inform the user that the changes have been committed, and let them handle pushing to the remote origin.

## 3. Decision Matrix
- **Are there remote changes that need to be pulled?**
   - **YES**: Halt and ask the user to pull the updates for you.
- **Did a file containing private credentials get staged/committed?**
   - **YES**: Instantly stop and undo: `git reset HEAD~1` (if committed) or `git reset HEAD <file>` (if staged). Move keys into `.env` and add the filename to `.gitignore`.

## 4. Error Mitigation Tree
- **Detached HEAD State**:
   - *Mitigation*: Run `git checkout <branch-name>` immediately to re-anchor on the active tracking branch.
- **Accidental commit to `main` branch**:
   - *Mitigation*: Run `git branch temp-branch`, reset main back to remote state: `git reset --hard origin/main`, then switch back: `git checkout temp-branch`.

## 5. Output Protocol
Update the project's active memory ledger (`.agents/memory.md`) under the Git/version control section with the active branch, last commit hash, and target PR status.
EOF

# test-driven-patch SKILL.md
write_template_safe ".agents/skills/test-driven-patch/SKILL.md" << 'EOF'
---
name: test-driven-patch
description: Modifies codebase operations or fixes defects under strict TDD constraints inside specific application domains.
---

# Test-Driven Patching Skill

## 1. Input Specification
- **Requirements/Defect Report**: Detailed description of the target behavior or bug description.
- **Target Files**: List of production source code files to modify.
- **Test Files**: Target path of corresponding spec or test files.
- **Mock Context**: List of external dependencies (e.g. database connections, external APIs, security middleware) to mock.

## 2. Operational Procedures & Checklist
1. **Red Phase (Write and Fail)**:
   - Identify or create the test/spec file corresponding to the target feature.
   - Write a unit test simulating the input and asserting the correct behavior or bug resolution.
   - Run the test runner command for the target language (e.g., `npm run test -- <path>`, `go test`, `pytest <path>`, `cargo test`). Verify that the test fails with a deterministic, expected assertion error.
2. **Green Phase (Implement and Pass)**:
   - Navigate to the production file.
   - Write the minimum amount of production code required to satisfy the unit test requirements and make it pass.
   - Re-run the test runner. Ensure the test passes successfully without side effects.
3. **Refactor Phase (Clean and Standardize)**:
   - Clean up code styles: eliminate duplicate lines, improve variable naming, optimize loops, and apply architectural spacing standards.
   - Run the test runner once more to confirm the code remains green.
4. **Coverage Analysis**:
   - Run coverage analysis commands if available.
   - Ensure the new modules or lines added satisfy the project's coverage threshold (typically >= 90%).
5. **Regression Verification**:
   - Run the project's global test suite across the active folder to verify no existing tests are broken.

## 3. Decision Matrix
- **Are we testing controllers or services guarded by authentication headers?**
   - **YES**: Mock or bypass the authorization guards inside the test container setup or pass valid mock JWT headers in the HTTP request simulator.
- **Are we testing database repositories or DB operations?**
   - **YES**: Use standard mock/stub repository adapters or an in-memory database configuration (e.g. SQLite in-memory, Go-sqlmock, mockito) to isolate tests from local databases.
- **Are we testing UI views or native components?**
   - **YES**: Mock native plugins, browser globals, or HTTP fetch clients to ensure tests run completely sandbox-isolated.

## 4. Error Mitigation Tree
- **Test environment crashes due to missing configuration variables**:
   - *Mitigation*: Ensure mock variables are loaded inside the test configuration setup block, or pass them inline to the execution environment.
- **Flaky or timing-sensitive asynchronous tests**:
   - *Mitigation*: Avoid using arbitrary sleep timers. Use built-in testing library virtual clocks/fake timers or wait for promise/goroutine resolutions explicitly.

## 5. Output Verification Gate
- [ ] Unit/Integration tests run green locally.
- [ ] Modified or added lines achieve target code coverage thresholds.
- [ ] Global regression suite passes without regression errors.
EOF

# infra-provisioner SKILL.md
write_template_safe ".agents/skills/infra-provisioner/SKILL.md" << 'EOF'
---
name: infra-provisioner
description: Generates, configures, and orchestrates local Docker and Docker Compose environments for system dependencies like databases, caches, and object storage.
---

# Infrastructure Provisioner Skill

## 1. Input Specification
- **Environment Configuration**: A `.env` file containing credentials (e.g., database user, cache credentials, API endpoints).
- **Network Boundaries**: Bridged private network configurations for cross-container communication.

## 2. Operational Procedures & Checklist
1. **Compose File Construction**:
   - Write a `docker-compose.yml` at the repository root.
   - Set up standard containers based on project dependencies (e.g. database, cache, storage).
   - Configure named persistent volumes to preserve service state.
2. **Resource Constraints**:
   - Restrict memory and CPU usage per service in local development environments to prevent host resource exhaustion.
3. **Decoupled Healthchecks**:
   - Configure health checks to verify that each service is fully operational.
   - Define interval, timeout, retries, and start period windows.
4. **Service Startup Sequencing**:
   - Map dependencies explicitly using `depends_on` with the `condition: service_healthy` clause to ensure services boot in the correct order.
5. **Autoprovisioning Scripts**:
   - Set up auto-initialization scripts or containers (e.g., creating database tables, seeding mock data, setting up default storage buckets).

## 3. Decision Matrix
- **Is a required service already running on the host system?**
   - **YES**: Do **NOT** shut down host processes. Edit the port binding in the local container configuration (e.g., bind host port `5433` to container port `5432`) and update environment configs.
- **Do logs indicate initialization failures due to invalid credentials or volumes?**
   - **YES**: Stop container, purge invalid volumes (`docker compose down -v`), correct configuration values, and restart services.

## 4. Error Mitigation Tree
- **Container health check times out or fails**:
   - *Mitigation*: Run `docker compose logs <service-name>` to identify error logs. Common fixes include adjusting database permissions, increasing the health check `start_period`, or correcting credential mismatches.
- **Docker daemon is unresponsive**:
   - *Mitigation*: Run `docker info` to verify state. Prompt the user to ensure Docker is running.

## 5. Output Verification Gate
- Run validation check: `docker compose ps`. Verify all services are listed as healthy.
- Connect to database and cache dependencies to verify credentials.
- Record local infrastructure status in the active memory ledger (`.agents/memory.md`).
EOF

# security-ci-audit SKILL.md
write_template_safe ".agents/skills/security-ci-audit/SKILL.md" << 'EOF'
---
name: security-ci-audit
description: Verifies security configurations, scans for hardcoded credentials, checks CORS/rate-limiting setup, API docs compliance, and environment schema validation.
---

# Security & CI Compliance Audit Skill

## 1. Input Specification
- **Modified Source Code**: List of added or changed files in the active commit stack.
- **Project Configuration**: Environment validation files, API gateway bootstrap files, security middlewares.

## 2. Operational Procedures & Checklist
1. **Secret Scanning Pattern Match**:
   - Run grep pattern searches to identify hardcoded credentials:
     - Private key block indicators (e.g., `-----BEGIN PRIVATE KEY-----`).
     - Files with credentials (e.g., `credential*.json`, `key*.json`, `.pem`).
     - Hardcoded password strings or credentials: `api_key`, `secret`, `password` assignments.
2. **Environment Variable Validation Audit**:
   - Scan the codebase for raw environment variable reads (e.g. `process.env` in JS/TS, `os.Getenv` in Go, `os.environ` in Python).
   - Verify that all environment configs are validated at application bootstrap using a schema validator or config loading service, avoiding raw access scattered across domain layers.
3. **API Documentation Audit**:
   - For all files modified under API boundary folders (e.g., controllers, handlers):
     - Verify properties and endpoints are documented with clear tags, JSDoc/Swagger comments, or annotations.
     - Verify response schemas and return status codes are explicitly declared.
4. **Domain Layer Purity Audit**:
   - Verify files inside core business domain layers have zero dependencies on frameworks, HTTP routers, or ORM annotations.
5. **Third-Party Isolation Audit (Frontend UI)**:
   - Verify UI components consume abstract client/adapter interfaces (e.g., wrapper hooks or service adapters) rather than importing raw HTTP clients or native device packages directly.
6. **Observability and Security Middleware Audit**:
   - Verify that the API gateway entrypoint initializes:
     - Security headers (e.g., Helmet, CORS rules restricting wildcards).
     - Global validation pipelines for incoming requests.
     - Rate-limiting (throttling) policies.
     - Dependency health check endpoints (checking database, cache, storage connectivity).

## 3. Decision Matrix
- **Was a raw environment variable access violation found?**
   - **YES**: Replace the raw access with the appropriate property retrieved from the config loading service, and register the new key in the schema loader if not already mapped.
- **Did a route handler miss API docs annotations?**
   - **YES**: Add the appropriate annotations or documentation blocks to ensure schema contract compliance.

## 4. Error Mitigation Tree
- **App fails to boot due to env validation errors**:
   - *Mitigation*: Inspect the validation logs. Copy missing parameters from the configuration example into your local `.env`, bind the correct value type, and re-run startup.

## 5. Output Verification Gate
- [ ] No private keys or credentials files are tracked in git.
- [ ] Direct environment variables access is strictly restricted to the configuration module.
- [ ] API endpoints and models explicitly declare return types and validation rules.
- [ ] Health Check endpoint tracks active services.
- [ ] Rate limiting and security headers are initialized at the gateway.
EOF

# code-review SKILL.md
write_template_safe ".agents/skills/code-review/SKILL.md" << 'EOF'
---
name: code-review
description: Audits production code modifications for type cleanliness, security, architectural boundaries, Swagger documentation, and unit test compliance.
---

# Code Review & Quality Gate Skill

## 1. Input Specification
- **Modified Diffs**: Git diff list of staged or modified files.
- **Project Blueprints**: Config schemas, API docs specifications, and architectural rules.

## 2. Operational Procedures
1. **Source Code Auditing (Diff Check)**:
   - Run line-by-line checks on modified blocks to ensure:
     - No debugging remnants are left (`console.log`, `print`, `debugger`, raw print statements).
     - No hardcoded access credentials, passwords, or S3 key strings.
     - Comments are clean, professional, and explain non-obvious code paths.
2. **Type Safety & Cleanliness Audit**:
   - Verify that no type bypass methods are used (e.g. `any` in TypeScript, raw interface{} in Go, untyped variables where strict types are available).
   - Ensure all type casting is safe, and edge cases are handled (e.g. avoiding unchecked null/undefined property lookups).
3. **Architectural Boundary Gate**:
   - Check if database operations, frameworks, or security packages bleed into business use cases or core domain entities.
   - For web apps: Check if presenter UI components import network client classes (Axios, Fetch) directly instead of utilizing service wrappers or React Query adapters.
4. **Contract and API Docs Compliance**:
   - Confirm that DTOs utilize correct validation rules.
   - Confirm that API endpoints are decorated with clear descriptions, route mappings, and explicit return type schemas.
5. **Testing & Coverage Audit**:
   - Verify that test suites cover all newly added or modified methods.
   - Ensure mocks correctly isolate tests from running local databases or calling external third-party services.
   - Confirm global unit tests pass with zero failures.

## 3. Decision Matrix
- **Is there a type bypass or lint warning?**
  - **YES**: Stop the review. Reject the check. Instruct the agent/developer to declare strict interfaces or union types, and resolve lints.
- **Does the code bleed across boundaries?**
  - **YES**: Reject. Instruct to refactor using service/repository wrappers to keep layers decoupled.
- **Does it pass all checks and verification suites?**
  - **YES**: Accept. Approve the commit/PR.

## 4. Error Mitigation Tree
- **Global test suite fails during pre-commit checks**:
  - *Mitigation*: Identify the broken tests from console logs. If the error is due to changed mock inputs, update the specs. If it's a regression bug, revert the code change, diagnose, and fix.

## 5. Output Verification Gate
- [ ] Staged code compiles clean with no warnings/errors.
- [ ] Secrets and credential configurations are fully isolated.
- [ ] Newly added lines satisfy target code coverage limits.
- [ ] PR Review Handover document generated.
EOF

# Write impact-analysis SKILL.md
write_template_safe ".agents/skills/impact-analysis/SKILL.md" << 'EOF'
---
name: impact-analysis
description: Audits the long-term architectural, performance, security, and maintainability impacts of any feature design or code mutation.
---

# Long-Term Impact & Dependency Analysis Skill

## 1. Input Specification
- **Proposed Mutation/Feature**: Description of the changes to be made.
- **Affected Domain/Modules**: List of files, databases, routes, or interfaces that interact with the modified sections.
- **Project Lifespan Context**: Designing with a long-term (up to 10-year) maintainability and scalability horizon.

## 2. Operational Procedures
1. **Critical Thinking Assessment**:
   - Before writing any code, write down a mental or scratchpad analysis of the proposed implementation path.
   - Run a multi-dimensional analysis on:
     - **Architectural Coupling**: Ensure zero leakages. Core business domains must remain completely framework-agnostic.
     - **Performance & Resource Scalability**: Analyze database query count (avoid N+1), index usages, network roundtrips, and memory consumption.
     - **Security & Data Privacy**: Check inputs for injection, cross-site scripting, rate-limiting violations, data access authorization, and credential leakages.
     - **Backward Compatibility**: Verify that existing clients, APIs, or database records are not broken.
     - **10-Year Maintainability**: Avoid convoluted patterns, unchecked external dependencies, or unverified imports. Write clean, self-documenting code.
2. **Structural Dependency Mapping**:
   - Scan downstream dependencies of any file being modified using `grep_search` or code analysis to trace what else might break.
3. **Interactive Validation Gate**:
   - If any potential high-risk impact is detected (e.g., database schema changes, backward-incompatible API changes, high latency operations, or major security risks), the agent MUST halt execution and consult the user using a clear multiple-choice list of alternatives before proceeding.

## 3. Decision Matrix
- **Does the task involve changing database columns or relational constraints?**
  - **YES**: Write a migration plan, check database compatibility, and ask the user for approval.
- **Does the task introduce a new third-party package?**
  - **YES**: Analyze the package's security posture, active maintainer status, bundle size, and license compliance before importing.
- **Does the code bleed boundary layers (e.g., ORM annotations in domain structs, HTTP logic in services)?**
  - **YES**: Refactor to introduce proper abstraction layers (like Repository patterns or interfaces).

## 4. Output Protocol
For all major features or architectural shifts, record the design choices and downstream analysis under a new Architectural Decision Record (ADR) in `.agents/adr.md` or a workflows folder before writing code.
EOF

# 9. Write helper.sh script
write_template_safe ".agents/scripts/helper.sh" << 'EOF'
#!/usr/bin/env bash
# Antigravity Agent Core Helper Script
set -euo pipefail

MEMORY_FILE=".agents/memory.md"
LOCKS_DIR=".agents/locks"
ARCHIVE_DIR=".agents/archive"

show_help() {
    echo "Usage: \$0 [command] [args]"
    echo ""
    echo "Commands:"
    echo "  init [name] [stack] [arch] Initialize the workspace interactively or with parameters"
    echo "  recon             Run autonomous codebase stack and directory structure detection"
    echo "  validate          Perform security audit, lock checks, and memory size validation"
    echo "  doctor            Diagnose workspace health and verify system executables"
    echo "  commit            Verify code tests, run security checks, and execute conventional commit"
    echo "  sync-git          Synchronize Git branch and last commit hash with memory.md"
    echo "  lock [module]     Acquire a lock on a module"
    echo "  unlock [module]   Release a lock on a module"
    echo "  archive           Archive completed sprint tasks and reset memory.md checklist"
    echo "  migrate           Migrate workspace from older agent versions to version 1.4.0"
    echo "  build             Run monorepo-aware project compilation/build commands"
    echo "  lint              Run monorepo-aware linter validations on modified folders"
    echo "  test              Run monorepo-aware testing runner suites on modified folders"
    echo "  help              Show this help message"
}

cmd_sync_git() {
    if [ ! -f "$MEMORY_FILE" ]; then
        echo "Error: Memory file $MEMORY_FILE not found." >&2
        exit 1
    fi
    local branch
    branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached")
    local commit
    commit=$(git log -n 1 --format="%h" 2>/dev/null || echo "none")

    # Update memory.md using sed
    sed -i -E "s|- \*\*Active Branch\*\*: .*|- **Active Branch**: $branch|" "$MEMORY_FILE"
    sed -i -E "s|- \*\*Last Commit Reference\*\*: .*|- **Last Commit Reference**: $commit|" "$MEMORY_FILE"
    echo "Synchronized: Branch=$branch, Commit=$commit in $MEMORY_FILE"
}

cmd_lock() {
    local module="${1:-}"
    if [ -z "$module" ]; then
        echo "Error: Please specify a module name to lock." >&2
        exit 1
    fi
    mkdir -p "$LOCKS_DIR"
    # Replace slashes with underscores for nested monorepo paths
    local lock_name="${module//\//_}"
    local lockfile="$LOCKS_DIR/$lock_name.lock"
    if [ -f "$lockfile" ]; then
        echo "Error: Module '$module' is already locked!" >&2
        cat "$lockfile" >&2
        exit 1
    fi

    local branch
    branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached")
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    cat << INNER_EOF > "$lockfile"
Branch: $branch
Owner: Agent
Timestamp: $timestamp
INNER_EOF
    echo "Acquired lock for module '$module' at $lockfile"
}

cmd_unlock() {
    local module="${1:-}"
    if [ -z "$module" ]; then
        echo "Error: Please specify a module name to unlock." >&2
        exit 1
    fi
    # Replace slashes with underscores for nested monorepo paths
    local lock_name="${module//\//_}"
    local lockfile="$LOCKS_DIR/$lock_name.lock"
    if [ ! -f "$lockfile" ]; then
        echo "Warning: Module '$module' is not locked." >&2
        exit 0
    fi
    rm -f "$lockfile"
    echo "Released lock for module '$module'"
}

cmd_build() {
    local subprojects_file=".agents/subprojects.sh"
    if [ -f "$subprojects_file" ]; then
        source "$subprojects_file"
        echo "Monorepo detected. Running build compilation..."
        local failed=0
        for sp in "${SUBPROJECTS[@]}"; do
            local path=$(echo "$sp" | cut -d'|' -f1)
            local build_cmd=$(echo "$sp" | cut -d'|' -f3)
            echo "  Building $path ($build_cmd)..."
            if ! (cd "$path" && eval "$build_cmd"); then
                echo "  [FAIL] Build failed in $path" >&2
                failed=1
            fi
        done
        return $failed
    else
        # Fallback to project_rules build command
        local build_line=$(grep "Build validation" .agents/project_rules.md || echo "")
        local build_cmd=$(echo "$build_line" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^`//' -e 's/`$//')
        if [ -n "$build_cmd" ] && [ "$build_cmd" != "echo 'No build command needed'" ]; then
            eval "$build_cmd"
        else
            echo "No build configuration found."
        fi
    fi
}

cmd_lint() {
    local subprojects_file=".agents/subprojects.sh"
    if [ -f "$subprojects_file" ]; then
        source "$subprojects_file"
        local changed_files=""
        changed_files=$(git diff --cached --name-only 2>/dev/null || echo "")
        local failed=0
        local run_all=0
        if [ -z "$changed_files" ]; then
            run_all=1
            echo "No staged changes detected. Running linter on all monorepo modules..."
        else
            echo "Analyzing staged file boundaries for monorepo-aware linting..."
        fi
        
        for sp in "${SUBPROJECTS[@]}"; do
            local path=$(echo "$sp" | cut -d'|' -f1)
            local lint_cmd=$(echo "$sp" | cut -d'|' -f5)
            local should_run=$run_all
            if [ "$should_run" = "0" ]; then
                if echo "$changed_files" | grep -q "^$path/"; then
                    should_run=1
                fi
            fi
            if [ "$should_run" = "1" ]; then
                echo "  Linting $path ($lint_cmd)..."
                if ! (cd "$path" && eval "$lint_cmd"); then
                    echo "  [FAIL] Linter errors found in $path" >&2
                    failed=1
                fi
            else
                echo "  Skipping $path (no staged modifications)."
            fi
        done
        return $failed
    else
        # Fallback to project_rules linter
        local linter_line=$(grep "Linter command" .agents/project_rules.md || echo "")
        local linter_cmd=$(echo "$linter_line" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^`//' -e 's/`$//')
        if [ -n "$linter_cmd" ] && [ "$linter_cmd" != "echo 'No linter found'" ]; then
            eval "$linter_cmd"
        else
            echo "No linter configuration found."
        fi
    fi
}

cmd_test() {
    local subprojects_file=".agents/subprojects.sh"
    if [ -f "$subprojects_file" ]; then
        source "$subprojects_file"
        local changed_files=""
        changed_files=$(git diff --cached --name-only 2>/dev/null || echo "")
        local failed=0
        local run_all=0
        if [ -z "$changed_files" ]; then
            run_all=1
            echo "No staged changes detected. Running tests on all monorepo modules..."
        else
            echo "Analyzing staged file boundaries for monorepo-aware testing..."
        fi
        
        for sp in "${SUBPROJECTS[@]}"; do
            local path=$(echo "$sp" | cut -d'|' -f1)
            local test_cmd=$(echo "$sp" | cut -d'|' -f4)
            local should_run=$run_all
            if [ "$should_run" = "0" ]; then
                if echo "$changed_files" | grep -q "^$path/"; then
                    should_run=1
                fi
            fi
            if [ "$should_run" = "1" ]; then
                echo "  Testing $path ($test_cmd)..."
                if ! (cd "$path" && eval "$test_cmd"); then
                    echo "  [FAIL] Testing suite failed in $path" >&2
                    failed=1
                fi
            else
                echo "  Skipping $path (no staged modifications)."
            fi
        done
        return $failed
    else
        # Fallback to project_rules test runner
        local test_line=$(grep "Test runner command" .agents/project_rules.md || echo "")
        local test_runner=$(echo "$test_line" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^`//' -e 's/`$//')
        if [ -n "$test_runner" ] && [ "$test_runner" != "echo 'No test suite found'" ]; then
            eval "$test_runner"
        else
            echo "No test runner configuration found."
        fi
    fi
}

cmd_archive() {
    if [ ! -f "$MEMORY_FILE" ]; then
        echo "Error: Memory file $MEMORY_FILE not found." >&2
        exit 1
    fi
    mkdir -p "$ARCHIVE_DIR"
    local branch
    branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached")
    # replace slashes in branch name to avoid path issues
    branch_clean=${branch//\//_}
    local archive_file="$ARCHIVE_DIR/sprint_${branch_clean}.md"

    echo "Archiving tasks to $archive_file..."
    
    # Extract checklist from memory.md
    sed -n '/### Sprint Tasks Checklist/,/---/p' "$MEMORY_FILE" | grep -v -- '---' > "$archive_file"

    # Relocate workflow and PR review files to a branch-specific subdirectory
    local branch_archive_dir="$ARCHIVE_DIR/sprint_${branch_clean}"
    mkdir -p "$branch_archive_dir"
    echo "Archiving workflow and PR review files to $branch_archive_dir..."
    find .agents/workflows -maxdepth 1 -name "task_*.md" -exec mv {} "$branch_archive_dir/" \; 2>/dev/null || true
    find .agents/workflows -maxdepth 1 -name "pr_review_*.md" -exec mv {} "$branch_archive_dir/" \; 2>/dev/null || true


    # Reset checklist in memory.md
    local start_line
    start_line=$(grep -n "### Sprint Tasks Checklist" "$MEMORY_FILE" | cut -d: -f1)
    if [ -z "$start_line" ]; then
        echo "Error: Could not locate checklist section in $MEMORY_FILE" >&2
        exit 1
    fi

    local end_line
    end_line=$(tail -n +$start_line "$MEMORY_FILE" | grep -n "^---" | head -n 1 | cut -d: -f1)
    if [ -z "$end_line" ]; then
        end_line=$(wc -l < "$MEMORY_FILE")
    else
        end_line=$((start_line + end_line - 1))
    fi

    local temp_file
    temp_file=$(mktemp)
    head -n "$start_line" "$MEMORY_FILE" > "$temp_file"
    cat << 'INNER_EOF' >> "$temp_file"
- [ ] Implement core logic
- [ ] Write unit tests
- [ ] Verify build and tests pass
INNER_EOF
    tail -n +"$end_line" "$MEMORY_FILE" >> "$temp_file"
    mv "$temp_file" "$MEMORY_FILE"
    echo "Checklist reset successfully."
}

cmd_init() {
    echo "=========================================================="
    echo "  Antigravity Agent Core - Workspace Initialization"
    echo "=========================================================="
    
    local project_name="${2:-}"
    local tech_stack="${3:-}"
    local arch_pattern="${4:-}"
    local db_orm="${5:-}"
    local env_vars="${6:-}"
    local scaffold=""

    if [ -z "$project_name" ]; then
        read -p "Enter Project Name (default: My Project): " project_name
        if [ -z "$project_name" ]; then project_name="My Project"; fi
    fi
    
    if [ -z "$tech_stack" ]; then
        echo "Select Technology Stack:"
        echo "  [1] Next.js (TypeScript, Tailwind, App Router) [Recommended]"
        echo "  [2] Go Gin (Clean Architecture REST API)"
        echo "  [3] FastAPI (Python REST API with pytest)"
        echo "  [4] Node/TypeScript (Generic Node App)"
        echo "  [5] Go (Generic Main App)"
        echo "  [6] Python (Generic Script)"
        echo "  [7] Monorepo (Turborepo: Next.js Frontend + Go Gin Backend)"
        read -p "Select choice [1-7] (default: 1): " stack_choice
        case "$stack_choice" in
            2) tech_stack="Go Gin" ;;
            3) tech_stack="FastAPI" ;;
            4) tech_stack="Node/TypeScript" ;;
            5) tech_stack="Go" ;;
            6) tech_stack="Python" ;;
            7) tech_stack="Monorepo" ;;
            1|"") tech_stack="Next.js" ;;
            *) tech_stack="$stack_choice" ;;
        esac
    fi

    # Auto-suggest architecture based on stack
    local default_arch="MVC"
    if [ "$tech_stack" = "Next.js" ]; then
        default_arch="App Router"
    elif [ "$tech_stack" = "Go Gin" ]; then
        default_arch="Clean Architecture"
    elif [ "$tech_stack" = "FastAPI" ]; then
        default_arch="Modular REST"
    elif [ "$tech_stack" = "Monorepo" ]; then
        default_arch="Decoupled / Distributed"
    fi

    if [ -z "$arch_pattern" ]; then
        read -p "Enter Architectural Pattern (default: $default_arch): " arch_pattern
        if [ -z "$arch_pattern" ]; then arch_pattern="$default_arch"; fi
    fi

    # Auto-suggest env vars based on stack
    local default_env="PORT"
    if [ "$tech_stack" = "Go Gin" ] || [ "$tech_stack" = "FastAPI" ]; then
        default_env="PORT,ENV"
    elif [ "$tech_stack" = "Next.js" ]; then
        default_env="PORT"
    fi

    if [ -z "$db_orm" ]; then
        read -p "Enter Database/ORM (e.g. Prisma, PostgreSQL, None) (default: None): " db_orm
        if [ -z "$db_orm" ]; then db_orm="None"; fi
    fi

    if [ -z "$env_vars" ]; then
        read -p "Enter config variables (comma-separated) (default: $default_env): " env_vars
        if [ -z "$env_vars" ]; then env_vars="$default_env"; fi
    fi

    if [ -z "${7:-}" ]; then
        read -p "Scaffold initial project folders? (y/n) (default: y): " scaffold
        if [ -z "$scaffold" ]; then scaffold="y"; fi
    else
        scaffold="${7:-}"
    fi

    # Initialize Git if not present
    if [ ! -d .git ]; then
        echo "Initializing Git repository..."
        git init
        git branch -m main
    fi

    # Install Git hooks (pre-commit & post-commit)
    mkdir -p .git/hooks
    if [ -f .agents/hooks/pre-commit ]; then
        cp .agents/hooks/pre-commit .git/hooks/pre-commit
        chmod +x .git/hooks/pre-commit
        echo "Git pre-commit hook installed."
    fi
    if [ -f .agents/hooks/post-commit ]; then
        cp .agents/hooks/post-commit .git/hooks/post-commit
        chmod +x .git/hooks/post-commit
        echo "Git post-commit hook installed."
    fi
    if [ -f .agents/hooks/commit-msg ]; then
        cp .agents/hooks/commit-msg .git/hooks/commit-msg
        chmod +x .git/hooks/commit-msg
        echo "Git commit-msg hook installed."
    fi

    # Scaffolding folders if requested
    if [ "$scaffold" = "y" ] || [ "$scaffold" = "yes" ]; then
        echo "Scaffolding directory structure..."
        
        if [ "$tech_stack" = "Next.js" ]; then
            mkdir -p src/app src/components src/lib tests
            # Write package.json
            cat << 'JSON_EOF' > package.json
{
  "name": "nextjs-boilerplate",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "jest"
  },
  "dependencies": {
    "next": "^14.2.3",
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@types/node": "^20.12.12",
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.38",
    "tailwindcss": "^3.4.3",
    "typescript": "^5.4.5",
    "eslint": "^8.57.0",
    "eslint-config-next": "^14.2.3",
    "jest": "^29.7.0",
    "ts-jest": "^29.1.4"
  }
}
JSON_EOF
            # Write next.config.js
            cat << 'JS_EOF' > next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
};

module.exports = nextConfig;
JS_EOF
            # Write tailwind.config.js
            cat << 'JS_EOF' > tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
JS_EOF
            # Write postcss.config.js
            cat << 'JS_EOF' > postcss.config.js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
JS_EOF
            # Write tsconfig.json
            cat << 'JSON_EOF' > tsconfig.json
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
JSON_EOF
            # Write jest.config.js
            cat << 'JS_EOF' > jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testMatch: ['**/tests/**/*.test.ts'],
};
JS_EOF
            # Write src/app/globals.css
            cat << 'CSS_EOF' > src/app/globals.css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  color-scheme: dark;
}

body {
  margin: 0;
  padding: 0;
  background-color: #020617;
  color: #f8fafc;
}
CSS_EOF
            # Write src/app/layout.tsx
            cat << 'TSX_EOF' > src/app/layout.tsx
import React from 'react';
import './globals.css';

export const metadata = {
  title: 'Antigravity Next.js Boilerplate',
  description: 'Scaffolded Next.js workspace for AI software agents',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
TSX_EOF
            # Write src/app/page.tsx
            cat << 'TSX_EOF' > src/app/page.tsx
import React from 'react';

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6 font-sans">
      <div className="max-w-4xl w-full text-center space-y-8">
        <header className="space-y-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-sm font-semibold tracking-wide animate-pulse">
            🚀 Antigravity Workspace Active
          </div>
          <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
            Antigravity Next.js Boilerplate
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Your production-ready Next.js application, scaffolded and pre-configured for seamless development with AI coding agents.
          </p>
        </header>

        <main className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
          <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm hover:border-indigo-500/30 transition-all duration-300">
            <h2 className="text-xl font-bold text-slate-100 mb-2">⚡ App Router</h2>
            <p className="text-slate-400 text-sm">
              Scaffolded with React Server Components, layout sharing, and clean directory structure inside <code className="text-indigo-400">src/app</code>.
            </p>
          </div>
          <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm hover:border-purple-500/30 transition-all duration-300">
            <h2 className="text-xl font-bold text-slate-100 mb-2">🎨 Styling & UI</h2>
            <p className="text-slate-400 text-sm">
              Pre-integrated with Tailwind CSS, custom fonts, CSS variables, and modern dark-mode aesthetics ready for immediate extension.
            </p>
          </div>
          <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm hover:border-pink-500/30 transition-all duration-300">
            <h2 className="text-xl font-bold text-slate-100 mb-2">🛡️ AI Agent Guard</h2>
            <p className="text-slate-400 text-sm">
              Wrapped inside Antigravity's cognitive alignment gates (automated pre-commit validators, secret scanning, and memory sync).
            </p>
          </div>
        </main>

        <footer className="text-slate-500 text-sm border-t border-slate-900 pt-8 mt-12 flex justify-between items-center">
          <div> Muhammad Rafael Ghifari &copy; 2026</div>
          <div className="flex gap-4">
            <a href="https://github.com/rafaelghif/antigravity-agents" target="_blank" rel="noopener noreferrer" className="hover:text-indigo-400 transition-colors">GitHub Repository</a>
            <a href="/api/health" className="hover:text-indigo-400 transition-colors">API Health Check</a>
          </div>
        </footer>
      </div>
    </div>
  );
}
TSX_EOF
            # Write src/app/api/health/route.ts
            mkdir -p src/app/api/health
            cat << 'TS_EOF' > src/app/api/health/route.ts
import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    status: 'HEALTHY',
    timestamp: new Date().toISOString(),
    system: 'Antigravity Workspace Core',
  });
}
TS_EOF
            # Write tests/health.test.ts
            cat << 'TS_EOF' > tests/health.test.ts
describe('Next.js Boilerplate Test Suite', () => {
  it('should pass initial unit test check', () => {
    expect(true).toBe(true);
  });
});
TS_EOF
            echo "Scaffolded Next.js application template successfully!"

        elif [ "$tech_stack" = "Go Gin" ]; then
            mkdir -p src/cmd/server src/internal/controller src/internal/config tests
            # Write go.mod
            cat << 'GO_EOF' > go.mod
module project

go 1.20

require (
	github.com/gin-gonic/gin v1.9.1
)
GO_EOF
            # Write src/cmd/server/main.go
            cat << 'GO_EOF' > src/cmd/server/main.go
package main

import (
	"fmt"
	"log"
	"net/http"
	"project/src/internal/config"
	"project/src/internal/controller"

	"github.com/gin-gonic/gin"
)

func main() {
	cfg := config.LoadConfig()

	if cfg.Env == "production" {
		gin.SetMode(gin.ReleaseMode)
	}

	r := gin.Default()
	r.Use(gin.Recovery())

	healthCtrl := controller.NewHealthController()

	api := r.Group("/api")
	{
		api.GET("/health", healthCtrl.Check)
	}

	r.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"message": "Welcome to Antigravity Go Gin Boilerplate!",
			"status":  "Active",
		})
	})

	addr := fmt.Sprintf(":%s", cfg.Port)
	log.Printf("Server starting on port %s...", cfg.Port)
	if err := r.Run(addr); err != nil {
		log.Fatalf("Failed to run server: %v", err)
	}
}
GO_EOF
            # Write src/internal/config/config.go
            cat << 'GO_EOF' > src/internal/config/config.go
package config

import "os"

type Config struct {
	Port string
	Env  string
}

func LoadConfig() *Config {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	env := os.Getenv("ENV")
	if env == "" {
		env = "development"
	}
	return &Config{
		Port: port,
		Env:  env,
	}
}
GO_EOF
            # Write src/internal/controller/health_controller.go
            cat << 'GO_EOF' > src/internal/controller/health_controller.go
package controller

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

type HealthController struct{}

func NewHealthController() *HealthController {
	return &HealthController{}
}

func (h *HealthController) Check(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":    "HEALTHY",
		"timestamp": time.Now().Format(time.RFC3339),
		"system":    "Antigravity Go Gin Core",
	})
}
GO_EOF
            # Write tests/health_test.go
            cat << 'GO_EOF' > tests/health_test.go
package tests

import (
	"net/http"
	"net/http/httptest"
	"project/src/internal/controller"
	"testing"

	"github.com/gin-gonic/gin"
)

func TestHealthCheck(t *testing.T) {
	gin.SetMode(gin.TestMode)
	r := gin.Default()
	healthCtrl := controller.NewHealthController()
	r.GET("/api/health", healthCtrl.Check)

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/api/health", nil)
	r.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status code 200, got %d", w.Code)
	}
}
GO_EOF
            # Write Makefile
            cat << 'MAKE_EOF' > Makefile
.PHONY: run test build clean

run:
	go run src/cmd/server/main.go

test:
	go test -v ./tests/...

build:
	go build -o bin/server src/cmd/server/main.go

clean:
	rm -rf bin/
MAKE_EOF
            echo "Scaffolded Go Gin application template successfully!"

        elif [ "$tech_stack" = "FastAPI" ]; then
            mkdir -p src/app/core src/app/api/endpoints tests
            # Write requirements.txt
            cat << 'TXT_EOF' > requirements.txt
fastapi>=0.110.0
uvicorn[standard]>=0.28.0
pydantic>=2.6.4
pytest>=8.1.1
httpx>=0.27.0
TXT_EOF
            # Write pyproject.toml
            cat << 'TOML_EOF' > pyproject.toml
[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
TOML_EOF
            # Write src/app/main.py
            cat << 'PY_EOF' > src/app/main.py
import uvicorn
from fastapi import FastAPI
from src.app.core.config import settings
from src.app.api.endpoints import health

app = FastAPI(
    title="Antigravity FastAPI Boilerplate",
    description="Production-ready FastAPI setup for AI software agents",
    version="1.0.0",
)

app.include_router(health.router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Antigravity FastAPI Boilerplate!",
        "status": "Active",
    }

if __name__ == "__main__":
    uvicorn.run("src.app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
PY_EOF
            # Write src/app/core/config.py
            cat << 'PY_EOF' > src/app/core/config.py
import os

class Settings:
    PORT: int = int(os.getenv("PORT", 8000))
    ENV: str = os.getenv("ENV", "development")

settings = Settings()
PY_EOF
            # Write src/app/api/endpoints/health.py
            cat << 'PY_EOF' > src/app/api/endpoints/health.py
from datetime import datetime
from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["system"])
def check_health():
    return {
        "status": "HEALTHY",
        "timestamp": datetime.utcnow().isoformat(),
        "system": "Antigravity FastAPI Core",
    }
PY_EOF
            # Write tests/test_health.py
            cat << 'PY_EOF' > tests/test_health.py
from fastapi.testclient import TestClient
from src.app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "timestamp" in data
    assert data["system"] == "Antigravity FastAPI Core"
PY_EOF
            echo "Scaffolded FastAPI application template successfully!"

        elif [ "$tech_stack" = "Monorepo" ]; then
            # Scaffold Turborepo monorepo structure
            mkdir -p apps/web apps/api packages/shared

            # Write root pnpm-workspace.yaml
            cat << 'YAML_EOF' > pnpm-workspace.yaml
packages:
  - 'apps/*'
  - 'packages/*'
YAML_EOF

            # Write root turbo.json
            cat << 'JSON_EOF' > turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "dist/**", "bin/**"]
    },
    "lint": {},
    "test": {},
    "dev": {
      "cache": false,
      "persistent": true
    }
  }
}
JSON_EOF

            # Write root package.json
            cat << 'JSON_EOF' > package.json
{
  "name": "monorepo-root",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "build": "turbo run build",
    "dev": "turbo run dev",
    "lint": "turbo run lint",
    "test": "turbo run test"
  },
  "devDependencies": {
    "turbo": "^2.0.0"
  }
}
JSON_EOF

            # ----------------------------------------------------
            # 1. Apps: apps/web (Next.js)
            # ----------------------------------------------------
            mkdir -p apps/web/src/app apps/web/src/components apps/web/src/lib apps/web/tests
            
            # package.json for web app
            cat << 'JSON_EOF' > apps/web/package.json
{
  "name": "web",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "jest"
  },
  "dependencies": {
    "next": "^14.2.3",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "@monorepo/shared": "workspace:*"
  },
  "devDependencies": {
    "@types/node": "^20.12.12",
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.38",
    "tailwindcss": "^3.4.3",
    "typescript": "^5.4.5",
    "eslint": "^8.57.0",
    "eslint-config-next": "^14.2.3",
    "jest": "^29.7.0",
    "ts-jest": "^29.1.4"
  }
}
JSON_EOF

            # next.config.js for web app
            cat << 'JS_EOF' > apps/web/next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
};
module.exports = nextConfig;
JS_EOF

            # tailwind.config.js for web app
            cat << 'JS_EOF' > apps/web/tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
JS_EOF

            # postcss.config.js for web app
            cat << 'JS_EOF' > apps/web/postcss.config.js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
JS_EOF

            # tsconfig.json for web app
            cat << 'JSON_EOF' > apps/web/tsconfig.json
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
JSON_EOF

            # jest.config.js for web app
            cat << 'JS_EOF' > apps/web/jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testMatch: ['**/tests/**/*.test.ts'],
};
JS_EOF

            # globals.css for web app
            cat << 'CSS_EOF' > apps/web/src/app/globals.css
@tailwind base;
@tailwind components;
@tailwind utilities;
:root {
  color-scheme: dark;
}
body {
  margin: 0;
  padding: 0;
  background-color: #020617;
  color: #f8fafc;
}
CSS_EOF

            # layout.tsx for web app
            cat << 'TSX_EOF' > apps/web/src/app/layout.tsx
import React from 'react';
import './globals.css';
export const metadata = {
  title: 'Antigravity Monorepo Frontend',
  description: 'Scaffolded Turborepo Frontend Web Application',
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
TSX_EOF

            # page.tsx for web app
            cat << 'TSX_EOF' > apps/web/src/app/page.tsx
import React from 'react';
import { appName, version } from '@monorepo/shared';

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6 font-sans">
      <div className="max-w-4xl w-full text-center space-y-8">
        <header className="space-y-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-sm font-semibold tracking-wide animate-pulse">
            🚀 Antigravity Monorepo Active
          </div>
          <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
            {appName}
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Monorepo Web Client (v{version}) running alongside an isolated Go Gin backend service.
          </p>
        </header>
        <main className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
          <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm hover:border-indigo-500/30 transition-all duration-300">
            <h2 className="text-xl font-bold text-slate-100 mb-2">⚡ Next.js</h2>
            <p className="text-slate-400 text-sm">
              Frontend web client running Next.js App Router inside <code className="text-indigo-400">apps/web</code>.
            </p>
          </div>
          <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm hover:border-purple-500/30 transition-all duration-300">
            <h2 className="text-xl font-bold text-slate-100 mb-2">🐹 Go Gin API</h2>
            <p className="text-slate-400 text-sm">
              Isolated REST API backend service with Go Gin inside <code className="text-purple-400">apps/api</code>.
            </p>
          </div>
          <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm hover:border-pink-500/30 transition-all duration-300">
            <h2 className="text-xl font-bold text-slate-100 mb-2">📦 Shared Workspace</h2>
            <p className="text-slate-400 text-sm">
              Shared package containing index exports, interfaces, and types inside <code className="text-pink-400">packages/shared</code>.
            </p>
          </div>
        </main>
      </div>
    </div>
  );
}
TSX_EOF

            # health route for web app
            mkdir -p apps/web/src/app/api/health
            cat << 'TS_EOF' > apps/web/src/app/api/health/route.ts
import { NextResponse } from 'next/server';
export async function GET() {
  return NextResponse.json({
    status: 'HEALTHY',
    timestamp: new Date().toISOString(),
    system: 'Antigravity Monorepo Frontend',
  });
}
TS_EOF

            # tests for web app
            cat << 'TS_EOF' > apps/web/tests/health.test.ts
describe('Monorepo Web Client Test Suite', () => {
  it('should pass initial tests', () => {
    expect(true).toBe(true);
  });
});
TS_EOF

            # ----------------------------------------------------
            # 2. Apps: apps/api (Go Gin)
            # ----------------------------------------------------
            mkdir -p apps/api/src/cmd/server apps/api/src/internal/controller apps/api/src/internal/config apps/api/tests

            # go.mod for api app
            cat << 'GO_EOF' > apps/api/go.mod
module api

go 1.20

require (
	github.com/gin-gonic/gin v1.9.1
)
GO_EOF

            # main.go for api app
            cat << 'GO_EOF' > apps/api/src/cmd/server/main.go
package main
import (
	"fmt"
	"log"
	"net/http"
	"api/src/internal/config"
	"api/src/internal/controller"
	"github.com/gin-gonic/gin"
)
func main() {
	cfg := config.LoadConfig()
	if cfg.Env == "production" {
		gin.SetMode(gin.ReleaseMode)
	}
	r := gin.Default()
	r.Use(gin.Recovery())
	healthCtrl := controller.NewHealthController()
	api := r.Group("/api")
	{
		api.GET("/health", healthCtrl.Check)
	}
	r.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"message": "Welcome to Antigravity Go Gin Backend in Monorepo!",
			"status":  "Active",
		})
	})
	addr := fmt.Sprintf(":%s", cfg.Port)
	log.Printf("Backend starting on port %s...", cfg.Port)
	if err := r.Run(addr); err != nil {
		log.Fatalf("Failed to run server: %v", err)
	}
}
GO_EOF

            # config.go for api app
            cat << 'GO_EOF' > apps/api/src/internal/config/config.go
package config
import "os"
type Config struct {
	Port string
	Env  string
}
func LoadConfig() *Config {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	env := os.Getenv("ENV")
	if env == "" {
		env = "development"
	}
	return &Config{
		Port: port,
		Env:  env,
	}
}
GO_EOF

            # health_controller.go for api app
            cat << 'GO_EOF' > apps/api/src/internal/controller/health_controller.go
package controller
import (
	"net/http"
	"time"
	"github.com/gin-gonic/gin"
)
type HealthController struct{}
func NewHealthController() *HealthController {
	return &HealthController{}
}
func (h *HealthController) Check(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":    "HEALTHY",
		"timestamp": time.Now().Format(time.RFC3339),
		"system":    "Antigravity Monorepo Backend API",
	})
}
GO_EOF

            # test for api app
            cat << 'GO_EOF' > apps/api/tests/health_test.go
package tests
import (
	"net/http"
	"net/http/httptest"
	"api/src/internal/controller"
	"testing"
	"github.com/gin-gonic/gin"
)
func TestHealthCheck(t *testing.T) {
	gin.SetMode(gin.TestMode)
	r := gin.Default()
	healthCtrl := controller.NewHealthController()
	r.GET("/api/health", healthCtrl.Check)
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/api/health", nil)
	r.ServeHTTP(w, req)
	if w.Code != http.StatusOK {
		t.Errorf("Expected status code 200, got %d", w.Code)
	}
}
GO_EOF

            # Makefile for api app
            cat << 'MAKE_EOF' > apps/api/Makefile
.PHONY: run test build clean
run:
	go run src/cmd/server/main.go
test:
	go test -v ./tests/...
build:
	go build -o bin/server src/cmd/server/main.go
clean:
	rm -rf bin/
MAKE_EOF

            # ----------------------------------------------------
            # 3. Packages: packages/shared
            # ----------------------------------------------------
            cat << 'JSON_EOF' > packages/shared/package.json
{
  "name": "@monorepo/shared",
  "version": "1.0.0",
  "private": true,
  "main": "index.js",
  "types": "index.d.ts"
}
JSON_EOF

            cat << 'JS_EOF' > packages/shared/index.js
module.exports = {
  appName: "Antigravity Monorepo",
  version: "1.0.0"
};
JS_EOF

            cat << 'TS_EOF' > packages/shared/index.d.ts
export const appName: string;
export const version: string;
TS_EOF

            echo "Scaffolded Monorepo application template successfully!"

        else
            # Generic/Basic Scaffolding Fallback
            mkdir -p src tests config
            if [[ "$tech_stack" =~ "Node" || "$tech_stack" =~ "TypeScript" || "$tech_stack" =~ "TS" ]]; then
                if [ ! -f package.json ]; then
                    cat << 'JSON_EOF' > package.json
{
  "name": "project",
  "version": "1.0.0",
  "description": "",
  "main": "src/index.js",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "test": "jest",
    "lint": "eslint 'src/**/*.ts'"
  },
  "dependencies": {},
  "devDependencies": {}
}
JSON_EOF
                    echo "Created package.json scaffolding"
                fi
            fi
            
            if [[ "$tech_stack" =~ "Go" || "$tech_stack" =~ "Golang" ]]; then
                if [ ! -f go.mod ]; then
                    cat << 'GO_EOF' > go.mod
module project

go 1.20
GO_EOF
                    echo "Created go.mod scaffolding"
                fi
                if [ ! -f src/main.go ]; then
                    cat << 'GO_EOF' > src/main.go
package main

import "fmt"

func main() {
    fmt.Println("Hello, Antigravity!")
}
GO_EOF
                    echo "Created src/main.go template"
                fi
            fi

            if [[ "$tech_stack" =~ "Python" || "$tech_stack" =~ "Py" ]]; then
                if [ ! -f src/main.py ]; then
                    cat << 'PY_EOF' > src/main.py
def main():
    print("Hello, Antigravity!")

if __name__ == "__main__":
    main()
PY_EOF
                    echo "Created src/main.py template"
                fi
            fi
        fi
    fi


    # Create .env and .env.example if env_vars exist
    if [ -n "$env_vars" ]; then
        echo "Writing configuration environment variables..."
        IFS=',' read -ra ADDR <<< "$env_vars"
        # Reset files
        > .env.example
        > .env
        for i in "${ADDR[@]}"; do
            echo "$i=" >> .env.example
            echo "$i=" >> .env
        done
        echo "Created .env and .env.example templates"
    fi

    # Run auto-recon to generate the blueprints
    echo "Running autonomous reconnaissance to populate blueprint files..."
    if [ -f .agents/scripts/recon.sh ]; then
        .agents/scripts/recon.sh -f
    fi

    echo "=========================================================="
    echo "Workspace initialized successfully for '$project_name'!"
    echo "=========================================================="
}

cmd_recon() {
    if [ -f .agents/scripts/recon.sh ]; then
        .agents/scripts/recon.sh
    else
        echo "Error: recon.sh not found at .agents/scripts/recon.sh" >&2
        exit 1
    fi
}

cmd_validate() {
    if [ -f .agents/scripts/validate.sh ]; then
        .agents/scripts/validate.sh
    else
        echo "Error: validate.sh not found at .agents/scripts/validate.sh" >&2
        exit 1
    fi
}

cmd_doctor() {
    echo "=========================================================="
    echo "  Antigravity Workspace Doctor Diagnostics"
    echo "=========================================================="
    
    local errors=0
    
    # Check Git Repository
    if [ -d .git ]; then
        echo "  [PASS] Git repository initialized."
    else
        echo "  [FAIL] Git repository not initialized!"
        errors=$((errors + 1))
    fi
    
    # Check Git hooks
    if [ -f .git/hooks/pre-commit ] && [ -x .git/hooks/pre-commit ]; then
        echo "  [PASS] pre-commit Git hook is installed and executable."
    else
        echo "  [WARNING] Git pre-commit hook is missing or not executable."
        echo "            To install: cp .agents/hooks/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit"
    fi
    if [ -f .git/hooks/post-commit ] && [ -x .git/hooks/post-commit ]; then
        echo "  [PASS] post-commit Git hook is installed and executable."
    else
        echo "  [WARNING] Git post-commit hook is missing or not executable."
        echo "            To install: cp .agents/hooks/post-commit .git/hooks/post-commit && chmod +x .git/hooks/post-commit"
    fi
    if [ -f .git/hooks/commit-msg ] && [ -x .git/hooks/commit-msg ]; then
        echo "  [PASS] commit-msg Git hook is installed and executable."
    else
        echo "  [WARNING] Git commit-msg hook is missing or not executable."
        echo "            To install: cp .agents/hooks/commit-msg .git/hooks/commit-msg && chmod +x .git/hooks/commit-msg"
    fi
    
    # Check helper script executability
    if [ -x .agents/scripts/helper.sh ]; then
        echo "  [PASS] helper.sh is executable."
    else
        echo "  [WARNING] helper.sh is not executable."
        chmod +x .agents/scripts/helper.sh
    fi
    
    # Check recon script
    if [ -f .agents/scripts/recon.sh ]; then
        if [ -x .agents/scripts/recon.sh ]; then
            echo "  [PASS] recon.sh is executable."
        else
            echo "  [WARNING] recon.sh is not executable. Auto-correcting..."
            chmod +x .agents/scripts/recon.sh
        fi
    else
        echo "  [FAIL] recon.sh is missing!"
        errors=$((errors + 1))
    fi

    # Check validate script
    if [ -f .agents/scripts/validate.sh ]; then
        if [ -x .agents/scripts/validate.sh ]; then
            echo "  [PASS] validate.sh is executable."
        else
            echo "  [WARNING] validate.sh is not executable. Auto-correcting..."
            chmod +x .agents/scripts/validate.sh
        fi
    else
        echo "  [FAIL] validate.sh is missing!"
        errors=$((errors + 1))
    fi

    # Run validate.sh checks
    if [ -f .agents/scripts/validate.sh ]; then
        echo "----------------------------------------------------------"
        if ! .agents/scripts/validate.sh; then
            errors=$((errors + 1))
        fi
    fi
    
    echo "=========================================================="
    if [ $errors -eq 0 ]; then
        echo "Doctor diagnostics: ALL SYSTEMS HEALTHY"
        exit 0
    else
        echo "Doctor diagnostics: FOUND $errors ERROR(S) / WARNING(S)"
        exit 1
    fi
}

cmd_commit() {
    local no_test_flag="false"
    local stage_files=()
    local type=""
    local scope=""
    local desc=""

    # Parse arguments
    while [ $# -gt 0 ]; do
        case "$1" in
            --no-test|--no-verify)
                no_test_flag="true"
                shift
                ;;
            *)
                if [ "$1" = "commit" ]; then
                    shift
                elif [ -z "$type" ]; then
                    type="$1"
                    shift
                elif [ -z "$scope" ]; then
                    scope="$1"
                    shift
                elif [ -z "$desc" ]; then
                    desc="$1"
                    shift
                else
                    stage_files+=("$1")
                    shift
                fi
                ;;
        esac
    done

    # Interactive inputs if parameters are missing
    if [ -z "$type" ]; then
        echo "Choose commit type:"
        echo "  [1] feat:     A new feature"
        echo "  [2] fix:      A bug fix"
        echo "  [3] refactor: A code change that neither fixes a bug nor adds a feature"
        echo "  [4] chore:    Changes to the build process or auxiliary tools and libraries"
        echo "  [5] docs:     Documentation only changes"
        echo "  [6] test:     Adding missing tests or correcting existing tests"
        echo "  [7] perf:     A code change that improves performance"
        read -p "Select number or type string (default: feat): " type_choice
        case "$type_choice" in
            1) type="feat" ;;
            2) type="fix" ;;
            3) type="refactor" ;;
            4) type="chore" ;;
            5) type="docs" ;;
            6) type="test" ;;
            7) type="perf" ;;
            "") type="feat" ;;
            *) type="$type_choice" ;;
        esac
    fi

    if [ -z "$scope" ]; then
        read -p "Enter commit scope (e.g. core, auth, db, shared) (default: core): " scope
        if [ -z "$scope" ]; then scope="core"; fi
    fi

    if [ -z "$desc" ]; then
        read -p "Enter brief description of change: " desc
        if [ -z "$desc" ]; then
            echo "Error: Description cannot be empty." >&2
            exit 1
        fi
    fi

    # Workspace Validation
    echo "Running workspace validation checks..."
    if ! .agents/scripts/validate.sh; then
        echo "Error: Workspace validation failed. Aborting commit." >&2
        exit 1
    fi

    # Linter Execution
    if [ "$no_test_flag" = "false" ]; then
        local linter_cmd=""
        if [ -f .agents/project_rules.md ]; then
            local linter_line
            linter_line=$(grep "Linter command" .agents/project_rules.md || echo "")
            linter_cmd=$(echo "$linter_line" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^`//' -e 's/`$//')
        fi

        if [ -n "$linter_cmd" ] && [ "$linter_cmd" != "echo 'No linter found'" ]; then
            echo "Running linter command: $linter_cmd..."
            if ! eval "$linter_cmd"; then
                echo "Error: Linter check failed. Aborting commit." >&2
                exit 1
            fi
            echo "  [PASS] Linter check passed successfully."
        else
            echo "No linter configured in project_rules.md. Skipping linting."
        fi
    else
        echo "Linter check bypassed via --no-test / --no-verify."
    fi

    # Test Execution
    if [ "$no_test_flag" = "false" ]; then
        local test_runner=""
        if [ -f .agents/project_rules.md ]; then
            local test_line
            test_line=$(grep "Test runner command" .agents/project_rules.md || echo "")
            test_runner=$(echo "$test_line" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^`//' -e 's/`$//')
        fi

        if [ -n "$test_runner" ] && [ "$test_runner" != "echo 'No test suite found'" ]; then
            echo "Running test suite: $test_runner..."
            if ! eval "$test_runner"; then
                echo "Error: Test runner suite failed. Aborting commit." >&2
                exit 1
            fi
            echo "  [PASS] All tests passed successfully."
        else
            echo "No test runner configured in project_rules.md. Skipping tests."
        fi
    else
        echo "Test execution bypassed via --no-test / --no-verify."
    fi

    # File Staging
    if [ ${#stage_files[@]} -gt 0 ]; then
        echo "Staging specified files: ${stage_files[*]}..."
        git add "${stage_files[@]}"
    else
        echo "Staging all modified and untracked files..."
        # Check if there are changes to stage
        if [ -n "$(git status --porcelain | grep -v '^\?\? .agents/locks/')" ]; then
            git add -A -- ':!.agents/locks/*'
        fi
    fi

    # Conventional Commit Execution
    local commit_msg="$type($scope): $desc"
    echo "Executing conventional commit: '$commit_msg'..."
    if git commit -m "$commit_msg"; then
        echo "Commit successful."
    else
        echo "Error: Git commit failed." >&2
        exit 1
    fi
}

cmd_migrate() {
    echo "=========================================================="
    echo "  Antigravity Agent Core - Workspace Migration (V1.4.0)"
    echo "=========================================================="

    local backup_suffix=".backup"

    # 1. Back up user-controlled files if they exist
    if [ -f "$MEMORY_FILE" ]; then
        echo "Warning: Existing memory file found. Backing up to ${MEMORY_FILE}${backup_suffix}"
        cp "$MEMORY_FILE" "${MEMORY_FILE}${backup_suffix}"
    fi

    if [ -f ".agents/project_rules.md" ]; then
        echo "Warning: Existing project rules blueprint found. Backing up to .agents/project_rules.md${backup_suffix}"
        cp ".agents/project_rules.md" ".agents/project_rules.md${backup_suffix}"
    fi

    if [ -f ".agents/schema.md" ]; then
        echo "Warning: Existing schema index found. Backing up to .agents/schema.md${backup_suffix}"
        cp ".agents/schema.md" ".agents/schema.md${backup_suffix}"
    fi

    # 2. Ensure directories exist
    echo "Re-creating directory structure..."
    mkdir -p .agents/skills/codebase-recon
    mkdir -p .agents/skills/git-ops
    mkdir -p .agents/skills/test-driven-patch
    mkdir -p .agents/skills/infra-provisioner
    mkdir -p .agents/skills/security-ci-audit
    mkdir -p .agents/skills/code-review
    mkdir -p .agents/skills/impact-analysis
    mkdir -p .agents/workflows
    mkdir -p .agents/archive
    mkdir -p .agents/locks
    mkdir -p .agents/schemas
    mkdir -p .agents/scripts
    mkdir -p .agents/hooks

    # 3. Update Git Hooks
    echo "Updating local Git hooks..."
    if [ -f .agents/hooks/pre-commit ]; then
        cp .agents/hooks/pre-commit .git/hooks/pre-commit
        chmod +x .git/hooks/pre-commit
        echo "  - Installed pre-commit hook"
    fi
    if [ -f .agents/hooks/post-commit ]; then
        cp .agents/hooks/post-commit .git/hooks/post-commit
        chmod +x .git/hooks/post-commit
        echo "  - Installed post-commit hook"
    fi
    if [ -f .agents/hooks/commit-msg ]; then
        cp .agents/hooks/commit-msg .git/hooks/commit-msg
        chmod +x .git/hooks/commit-msg
        echo "  - Installed commit-msg hook"
    fi

    # 4. Update memory.md schema version
    if [ -f "$MEMORY_FILE" ]; then
        echo "Updating memory ledger schema version to 5.0.0..."
        if grep -Fq "Memory Schema Version" "$MEMORY_FILE"; then
            local temp_mem
            temp_mem=$(mktemp)
            sed -E "s|Memory Schema Version\*\*: [0-9]+\.[0-9]+\.[0-9]+|Memory Schema Version**: 5.0.0|" "$MEMORY_FILE" > "$temp_mem"
            mv "$temp_mem" "$MEMORY_FILE"
        else
            # Prepend schema version header if not found
            local temp_mem
            temp_mem=$(mktemp)
            echo -e "# Agent Core Memory\n\n> **Memory Schema Version**: 5.0.0  \n> **Target System**: Antigravity Agent Core\n> **Active Guidelines**: Read [AGENTS.md](file://../AGENTS.md) and [.agents/project_rules.md](file://./project_rules.md) for execution details. Keep this file under 100 lines at all times.\n" > "$temp_mem"
            tail -n +2 "$MEMORY_FILE" >> "$temp_mem"
            mv "$temp_mem" "$MEMORY_FILE"
        fi
    fi

    # 5. Fix .gitignore configuration
    if [ -f ".gitignore" ]; then
        echo "Validating .gitignore compliance..."
        local temp_git
        temp_git=$(mktemp)
        # remove any lines that ignore .agents or AGENTS.md globally
        grep -v -E "^\.agents/?$" .gitignore | grep -v "^AGENTS.md$" > "$temp_git" || true
        # ensure Locks directory is ignored
        if ! grep -E -q "^\.agents/locks/?" "$temp_git"; then
            echo -e "\n# Ignore agent transient locks\n.agents/locks/" >> "$temp_git"
        fi
        mv "$temp_git" ".gitignore"
        echo "  - .gitignore updated."
    else
        echo "Creating default compliant .gitignore..."
        cat << 'GIT_EOF' > .gitignore
# Ignore agent transient locks
.agents/locks/
GIT_EOF
    fi

    # 6. Re-run codebase stack reconstruction (forces regeneration of blueprints)
    echo "Running autonomous stack reconstruction..."
    if [ -f .agents/scripts/recon.sh ]; then
        .agents/scripts/recon.sh -f
    fi

    echo "=========================================================="
    echo "Migration Complete! Workspace successfully upgraded."
    echo "=========================================================="
}

# Dispatch command
if [ $# -lt 1 ]; then
    show_help
    exit 1
fi

case "$1" in
    init)
        cmd_init "$@"
        ;;
    recon)
        cmd_recon
        ;;
    validate)
        cmd_validate
        ;;
    doctor)
        cmd_doctor
        ;;
    commit)
        cmd_commit "$@"
        ;;
    sync-git)
        cmd_sync_git
        ;;
    lock)
        cmd_lock "${2:-}"
        ;;
    unlock)
        cmd_unlock "${2:-}"
        ;;
    archive)
        cmd_archive
        ;;
    migrate)
        cmd_migrate
        ;;
    build)
        cmd_build
        ;;
    lint)
        cmd_lint
        ;;
    test)
        cmd_test
        ;;
    help)
        show_help
        ;;
    *)
        echo "Unknown command: $1" >&2
        show_help
        exit 1
        ;;
esac
EOF

# 10. Write recon.sh script
write_template_safe ".agents/scripts/recon.sh" << 'EOF'
#!/usr/bin/env bash
# Antigravity Agent Core - Autonomous Reconnaissance Script
# Scans the target workspace to automatically configure the agent environment blueprints.

set -euo pipefail

# Parse arguments
FORCE_OVERWRITE=false
while [ $# -gt 0 ]; do
    case "$1" in
        -f|--force)
            FORCE_OVERWRITE=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# Helper function to write templates safely (preserves existing files unless -f/--force is specified)
write_recon_file_safe() {
    local target_file="$1"
    if [ -f "$target_file" ] && [ "$FORCE_OVERWRITE" = "false" ]; then
        echo "  [PRESERVE] $target_file already exists. Preserving current file."
    else
        echo "  [WRITE] Writing $target_file..."
        cat > "$target_file"
    fi
}

PROJECT_RULES_FILE=".agents/project_rules.md"
SCHEMA_INDEX_FILE=".agents/schema.md"
SCHEMAS_DIR=".agents/schemas"

echo "=========================================================="
echo "Running Autonomous Codebase Reconnaissance..."
echo "=========================================================="

# 1. Tech Stack Detection
TECH_STACK="Unknown"
BUILD_CMD="echo 'No build command needed'"
TEST_CMD="echo 'No test suite found'"
LINT_CMD="echo 'No linter found'"
ARCH_PATTERN="Standard Model-View-Controller (MVC)"

IS_MONOREPO=false
SUBPROJECTS_FILE=".agents/subprojects.sh"
rm -f "$SUBPROJECTS_FILE"

# Detect if monorepo
if [ -f pnpm-workspace.yaml ] || [ -f turbo.json ] || [ -f lerna.json ] || [ -f go.work ] || ( [ -f package.json ] && grep -q '"workspaces"' package.json ) || ( [ -f Cargo.toml ] && grep -q "\[workspace\]" Cargo.toml ); then
    IS_MONOREPO=true
fi

if [ "$IS_MONOREPO" = "true" ]; then
    TECH_STACK="Monorepo"
    ARCH_PATTERN="Decoupled / Distributed Architecture"
    BUILD_CMD="./.agents/scripts/helper.sh build"
    TEST_CMD="./.agents/scripts/helper.sh test"
    LINT_CMD="./.agents/scripts/helper.sh lint"
    
    # Discovery loop
    discovered_projects=""
    declare -a sp_list=()
    NL=$'\n'
    
    # Find all sub-directories under apps/, packages/, services/ up to 1 level deep
    for dir in apps/* packages/* services/*; do
        if [ -d "$dir" ]; then
            # Signature check in sub-directory
            sub_stack="Unknown"
            sub_build="echo 'No build command'"
            sub_test="echo 'No test command'"
            sub_lint="echo 'No lint command'"
            
            if [ -f "$dir/package.json" ]; then
                sub_stack="Node.js"
                if grep -q '"typescript"' "$dir/package.json"; then sub_stack="Node.js (TypeScript)"; fi
                if grep -q '"next"' "$dir/package.json"; then sub_stack="Next.js"; fi
                if grep -q '"build"' "$dir/package.json"; then sub_build="npm run build"; else sub_build="echo 'No build step'"; fi
                if grep -q '"test"' "$dir/package.json"; then sub_test="npm run test"; fi
                if grep -q '"lint"' "$dir/package.json"; then sub_lint="npm run lint"; fi
            elif [ -f "$dir/go.mod" ]; then
                sub_stack="Go"
                sub_build="go build -o bin/server src/cmd/server/main.go 2>/dev/null || go build ./..."
                sub_test="go test ./..."
                sub_lint="golangci-lint run ./..."
                if [ -f "$dir/Makefile" ]; then
                    sub_build="make build"
                    sub_test="make test"
                fi
            elif [ -f "$dir/requirements.txt" ] || [ -f "$dir/pyproject.toml" ]; then
                sub_stack="Python"
                sub_build="echo 'No build step'"
                if grep -q "fastapi" "$dir/requirements.txt" 2>/dev/null || grep -q "fastapi" "$dir/pyproject.toml" 2>/dev/null; then
                    sub_stack="Python (FastAPI)"
                fi
                if grep -q "pytest" "$dir/requirements.txt" 2>/dev/null || grep -q "pytest" "$dir/pyproject.toml" 2>/dev/null; then
                    sub_test="pytest"
                else
                    sub_test="python -m unittest discover"
                fi
                sub_lint="flake8 . || black --check ."
            fi
            
            if [ "$sub_stack" != "Unknown" ]; then
                sp_list+=("$dir|$sub_stack|$sub_build|$sub_test|$sub_lint")
                discovered_projects="${discovered_projects}${NL}  - \`$dir/\` -> $sub_stack"
            fi
        fi
    done
    
    # Save the subprojects configuration file
    if [ ${#sp_list[@]} -gt 0 ]; then
        echo "SUBPROJECTS=(" > "$SUBPROJECTS_FILE"
        for sp in "${sp_list[@]}"; do
            echo "  \"$sp\"" >> "$SUBPROJECTS_FILE"
        done
        echo ")" >> "$SUBPROJECTS_FILE"
    fi
else
    if [ -f package.json ]; then
        TECH_STACK="Node.js"
        if grep -q '"typescript"' package.json; then
            TECH_STACK="Node.js (TypeScript)"
        fi
        if grep -q '"next"' package.json; then
            TECH_STACK="Next.js / React"
            ARCH_PATTERN="Next.js App Router Architecture"
        elif grep -q '"nest"' package.json; then
            TECH_STACK="NestJS (TypeScript)"
            ARCH_PATTERN="Modular NestJS Dependency Injection Architecture"
        elif grep -q '"react"' package.json; then
            TECH_STACK="React SPA"
            ARCH_PATTERN="Component-Driven SPA Architecture"
        elif grep -q '"express"' package.json; then
            TECH_STACK="Express API"
            ARCH_PATTERN="Express Layered Routing Architecture"
        fi
        
        # Extract package.json scripts
        if grep -q '"build"' package.json; then BUILD_CMD="npm run build"; fi
        if grep -q '"test"' package.json; then TEST_CMD="npm run test"; fi
        if grep -q '"lint"' package.json; then LINT_CMD="npm run lint"; fi
    elif [ -f go.mod ]; then
        TECH_STACK="Go"
        module_name=$(grep "^module " go.mod | cut -d' ' -f2 || echo "project")
        TECH_STACK="Go Module: $module_name"
        ARCH_PATTERN="Hexagonal / Domain-Driven Design in Go"
        BUILD_CMD="go build ./..."
        TEST_CMD="go test ./..."
        LINT_CMD="golangci-lint run"
        if grep -q "gin-gonic/gin" go.mod; then
            TECH_STACK="Go (Gin)"
            ARCH_PATTERN="Clean Architecture REST API"
            if [ -f Makefile ]; then
                BUILD_CMD="make build"
                TEST_CMD="make test"
            else
                BUILD_CMD="go build -o bin/server src/cmd/server/main.go"
                TEST_CMD="go test -v ./tests/..."
            fi
        fi
    elif [ -f Cargo.toml ]; then
        TECH_STACK="Rust"
        ARCH_PATTERN="Modular Cargo Workspace Architecture"
        BUILD_CMD="cargo build"
        TEST_CMD="cargo test"
        LINT_CMD="cargo clippy"
    elif [ -f requirements.txt ] || [ -f pyproject.toml ] || [ -f Pipfile ]; then
        TECH_STACK="Python"
        BUILD_CMD="echo 'No build step required'"
        
        if [ -f pyproject.toml ] && grep -q "fastapi" pyproject.toml; then
            TECH_STACK="Python (FastAPI)"
            ARCH_PATTERN="Asynchronous layered API structure"
        elif [ -f requirements.txt ] && grep -q "fastapi" requirements.txt; then
            TECH_STACK="Python (FastAPI)"
            ARCH_PATTERN="Asynchronous layered API structure"
        elif [ -f requirements.txt ] && grep -q "django" requirements.txt; then
            TECH_STACK="Python (Django)"
            ARCH_PATTERN="Django MTV Pattern"
        fi

        if [ -f requirements.txt ] && grep -q "pytest" requirements.txt; then
            TEST_CMD="pytest"
        else
            TEST_CMD="python -m unittest discover"
        fi
        LINT_CMD="flake8 . || black --check ."
    elif [ -f composer.json ]; then
        TECH_STACK="PHP"
        if grep -q '"laravel/framework"' composer.json; then
            TECH_STACK="PHP (Laravel)"
            ARCH_PATTERN="Laravel MVC / Eloquent Architecture"
        fi
        BUILD_CMD="composer install"
        TEST_CMD="vendor/bin/phpunit"
        LINT_CMD="vendor/bin/php-cs-fixer fix --dry-run"
    elif [ -f Gemfile ]; then
        TECH_STACK="Ruby"
        if grep -q "rails" Gemfile; then
            TECH_STACK="Ruby on Rails"
            ARCH_PATTERN="Rails Convention-over-Configuration MVC"
        fi
        BUILD_CMD="bundle install"
        TEST_CMD="bundle exec rake test"
        LINT_CMD="bundle exec rubocop"
    fi
fi

echo "Detected Stack: $TECH_STACK"
echo "Detected Build: $BUILD_CMD"
echo "Detected Test:  $TEST_CMD"
echo "Detected Lint:  $LINT_CMD"

# 2. Directory Structure Mapping
NL=$'\n'
DIRS=""
if [ "$IS_MONOREPO" = "true" ]; then
    DIRS="$discovered_projects"
else
    for d in src lib app apps controllers views handlers models services repositories routes tests test config pkg cmd; do
        if [ -d "$d" ]; then
            DIRS="${DIRS}${NL}  - \`$d/\` -> Project workspace component"
        fi
    done
fi

if [ -z "$DIRS" ]; then
    DIRS="${NL}  - Root directory contains project files."
fi

# 3. Database & ORM Detection
DB_STACK="None detected"
if [ -f prisma/schema.prisma ]; then
    DB_STACK="Prisma ORM (schema: prisma/schema.prisma)"
elif grep -r -q "sequelize" package.json 2>/dev/null || [ -d models ] && grep -r -q "Sequelize" models/ 2>/dev/null; then
    DB_STACK="Sequelize ORM"
elif grep -r -q "typeorm" package.json 2>/dev/null; then
    DB_STACK="TypeORM"
elif grep -r -q "sqlalchemy" requirements.txt pyproject.toml 2>/dev/null; then
    DB_STACK="SQLAlchemy ORM"
elif grep -r -q "gorm.io" go.mod 2>/dev/null; then
    DB_STACK="GORM (Go)"
elif [ -d db/migrate ]; then
    DB_STACK="Rails ActiveRecord Migrations"
elif [ -d database/migrations ]; then
    DB_STACK="Laravel Eloquent Migrations"
fi

echo "Detected Database/ORM: $DB_STACK"

# 4. Environment Template Variable Extraction
ENV_VARS=""
if [ -f .env.example ]; then
    ENV_VARS=$(grep -v '^#' .env.example | grep '=' | cut -d'=' -f1 | sed 's/^/  - /' || true)
elif [ -f .env ]; then
    ENV_VARS=$(grep -v '^#' .env | grep '=' | cut -d'=' -f1 | sed 's/^/  - /' || true)
fi

if [ -z "$ENV_VARS" ]; then
    ENV_VARS="  - No configuration parameters detected."
fi

# 5. Populate .agents/project_rules.md
write_recon_file_safe "$PROJECT_RULES_FILE" << PAB_EOF
# Project Architecture Blueprint (PAB)

This file defines the specific technical stack, directory boundaries, coding standards, and system dependencies for this project.

---

## 1. Stack & Directory Boundaries
- **Primary Language/Framework**: $TECH_STACK
- **Directory Structure**:$DIRS

## 2. Architectural Conventions
- **Architectural Pattern**: $ARCH_PATTERN
- **Boundary insulation**: Core domain logic must remain completely independent of external libraries, databases, and frameworks.

## 3. Spacing & Styling Standards
- **Linter command**: \`$LINT_CMD\`
- **Build validation**: \`$BUILD_CMD\`
- **Test runner command**: \`$TEST_CMD\`
- **Follow formatting**: Follow standard formatting guidelines for $TECH_STACK development.

## 4. Security & External Services
- **Database/ORM**: $DB_STACK
- **Required Configuration Variables**:
$ENV_VARS

## 5. Long-Term Impact & 10-Year Maintainability Gates
- **Impact-Analysis Check**: Before installing new packages, modifying database structures, or altering cross-domain APIs, the agent must run the \`impact-analysis\` skill and document design rationales.
- **Architectural Boundary Gate**: Domain business logic must remain completely independent of libraries and frameworks (e.g. database schemas, server frameworks).
- **Code Sustainability**: Code must prioritize long-term readability over brevity. Avoid complex runtime assumptions, unverified imports, or undocumented configuration requirements.
- **Ambiguity Gate**: If any implementation details are unclear, halt and ask the user for confirmation first.

## 6. Multi-Agent & Teamwork Constraints
- **Autonomous Bootstrapping Sequence**: Before performing any edit or script action, you MUST read the core files in sequence: \`AGENTS.md\`, \`.agents/project_rules.md\`, \`.agents/schema.md\`, and \`.agents/memory.md\`. No file writes or terminal runs are allowed prior to this initialization.
- **Workspace Git Tracking**: Never ignore \`.agents/\` or \`AGENTS.md\` in \`.gitignore\` (except \`.agents/locks/\`). Commit all memory, schemas, dynamic workflows, and ADR files to Git to ensure proper multi-agent synchronization.
- **Upstream Sync Gate**: You must run \`./.agents/scripts/helper.sh validate\` before beginning code changes to check if the branch is behind origin. If it is behind, stop and ask the user to pull first.
- **Discussion and Design Plans**: Document all \`/grill-me\` outcomes and execution plans under \`.agents/workflows/task_<task_name>.md\`. Never log task-specific plans or checklists globally or in the main memory ledger.
- **Real-Time Schema & Dependency Updates**: Any discussion on database models, API routes, or third-party libraries must be documented in the repository *immediately* before starting code edits:
  - Database structures must be saved under \`.agents/schemas/\` and registered in \`.agents/schema.md\`.
  - Technologies/libraries must be documented in \`.agents/project_rules.md\` and their respective workspace configuration files (\`package.json\`, \`go.mod\`, etc.).
  - Architectural decisions must be documented as a new ADR entry in \`.agents/adr.md\`.
- **Strict Checklist Checkbox Rules**: Checklists must follow a strict 3-state lifecycle. Only ONE task can be marked \`[/]\` at a time across the entire workspace. Do not change a task checklist state to \`[x]\` until verification has passed and the changes have been staged and committed in the completed state.
- **Handover Relayed Context**: Before logging off or ending a turn, you MUST write concise handover notes (under 5 lines) in the active memory ledger under \`## 3. Relayed Context & Handover Notes\`. This ensures any incoming agent or new account knows exactly where to resume work without token waste.
PAB_EOF

# 6. Database schema domain mapping (Auto-discover domain tables or modules)
mkdir -p "$SCHEMAS_DIR"

# Write a basic schema.md index file
if [ "$DB_STACK" = "Prisma ORM (schema: prisma/schema.prisma)" ]; then
    write_recon_file_safe "$SCHEMA_INDEX_FILE" << SRD_EOF
# Technical Schema & Reference Database (SRD) - Index Map

This file serves as the high-level index for the project's technical schemas, database specifications, and API contracts.

---

## 1. Domain Schemas Index
- [Default Module](file://./schemas/default_module.md) -> Reference: [default_module.md](file://./schemas/default_module.md)
- [Database Schema (Prisma)](file://./schemas/database_schema.md) -> Reference: [database_schema.md](file://./schemas/database_schema.md)
SRD_EOF
else
    write_recon_file_safe "$SCHEMA_INDEX_FILE" << SRD_EOF
# Technical Schema & Reference Database (SRD) - Index Map

This file serves as the high-level index for the project's technical schemas, database specifications, and API contracts.

---

## 1. Domain Schemas Index
- [Default Module](file://./schemas/default_module.md) -> Reference: [default_module.md](file://./schemas/default_module.md)
SRD_EOF
fi

# Check for custom schema files
if [ "$DB_STACK" = "Prisma ORM (schema: prisma/schema.prisma)" ]; then
    # Create prisma schema domain layout
    write_recon_file_safe "$SCHEMAS_DIR/database_schema.md" << PRISMA_EOF
# Schema: Database Models (Prisma)

Automatically discovered Prisma model entities:

---

## 1. Relational Database Tables / Models
$(grep -E "^model " prisma/schema.prisma | cut -d' ' -f2 | sed 's/^/- /' || true)
PRISMA_EOF
fi

echo "=========================================================="
echo "Reconnaissance Complete! Blueprints updated successfully."
echo "=========================================================="
EOF

# 11. Write validate.sh script
write_template_safe ".agents/scripts/validate.sh" << 'EOF'
#!/usr/bin/env bash
# Antigravity Agent Core - Workspace & Security Validator
# Validates workspace rules, scans for credentials, checks memory size, and details active locks.

set -euo pipefail

MEMORY_FILE=".agents/memory.md"
LOCKS_DIR=".agents/locks"
PROJECT_RULES=".agents/project_rules.md"

echo "=========================================================="
echo "Starting Antigravity Agent Workspace Validation..."
echo "=========================================================="

FAILED=0

# 1. Check Active Memory Size
if [ -f "$MEMORY_FILE" ]; then
    LINE_COUNT=$(wc -l < "$MEMORY_FILE" | tr -d ' ')
    echo "Check 1: Memory File Line Count: $LINE_COUNT lines"
    if [ "$LINE_COUNT" -gt 100 ]; then
        echo "  [WARNING] Memory file '$MEMORY_FILE' exceeds the 100-line limit ($LINE_COUNT lines)!"
        echo "            Please run './.agents/scripts/helper.sh archive' to compact your memory."
    else
        echo "  [PASS] Memory file size is within recommended limits."
    fi
else
    echo "  [FAIL] Memory file '$MEMORY_FILE' does not exist!"
    FAILED=1
fi

# 2. Check Active Lockfiles
echo "Check 2: Active Module Locks"
if [ -d "$LOCKS_DIR" ] && [ "$(ls -A "$LOCKS_DIR")" ]; then
    echo "  Found active locks:"
    for lock in "$LOCKS_DIR"/*.lock; do
        if [ -f "$lock" ]; then
            mod=$(basename "$lock" .lock)
            echo "  - Module '$mod':"
            sed 's/^/    /' "$lock"
        fi
    done
else
    echo "  [PASS] No active locks found."
fi

# 3. Secret and Credential Scanning (Pre-commit / Validation)
echo "Check 3: Hardcoded Credentials Scan (excluding .agents/ and .git/)"
SECRET_FOUND=0
# Search for API keys, secrets, private keys, passwords
# Match common secret variables and high entropy patterns
SECRET_PATTERNS=("apikey" "api_key" "secret" "password" "passwd" "private_key" "jwt_secret")
FILES_TO_SCAN=$(find . -type f \
    -not -path '*/.*' \
    -not -path './.agents/*' \
    -not -path './node_modules/*' \
    -not -path './dist/*' \
    -not -path './build/*' \
    -not -name 'bootstrap.sh' \
    -not -path '*.md' \
    -not -path '*.json' \
    -not -path '*.lock' \
    -not -path '*.png' \
    -not -path '*.jpg' \
    -not -path '*.gif' 2>/dev/null || true)

if [ -n "$FILES_TO_SCAN" ]; then
    for pattern in "${SECRET_PATTERNS[@]}"; do
        # search for assignment of secrets like API_KEY = "xxx"
        # avoid false positives by ensuring there is an assignment with quotation marks
        res=$(echo "$FILES_TO_SCAN" | xargs grep -rnEi "$pattern\s*=\s*['\"][a-zA-Z0-9_\-\.]{8,}['\"]" 2>/dev/null || true)
        if [ -n "$res" ]; then
            echo "  [FAIL] Potential hardcoded credential found for pattern '$pattern':"
            echo "$res" | sed 's/^/    /'
            SECRET_FOUND=1
        fi
    done
    
    # Scan for RSA/PEM private key headers
    private_key_res=$(echo "$FILES_TO_SCAN" | xargs grep -rn "BEGIN PRIVATE KEY" 2>/dev/null || true)
    if [ -n "$private_key_res" ]; then
        echo "  [FAIL] Hardcoded Private Key Block found:"
        echo "$private_key_res" | sed 's/^/    /'
        SECRET_FOUND=1
    fi
fi

if [ "$SECRET_FOUND" -eq 0 ]; then
    echo "  [PASS] No hardcoded credentials detected in scan scope."
else
    FAILED=1
fi

# 4. Check for Raw Environment Variable Reads
echo "Check 4: Raw Environment Access Scan (domain-purity verification)"
RAW_ENV_FOUND=0
# Scanning JS/TS, Go, Python files for raw env variable access
JS_FILES=$(find . -name "*.js" -o -name "*.ts" -o -name "*.tsx" -not -path './.agents/*' -not -path './node_modules/*' -not -path './dist/*' 2>/dev/null || true)
if [ -n "$JS_FILES" ]; then
    # Look for process.env.something, but ignore common config folders
    raw_js_env=$(echo "$JS_FILES" | grep -v "config" | xargs grep -rn "process\.env\.[A-Za-z0-9_]" 2>/dev/null || true)
    if [ -n "$raw_js_env" ]; then
        echo "  [WARNING] Raw 'process.env' access found outside configuration modules:"
        echo "$raw_js_env" | sed 's/^/    /'
        RAW_ENV_FOUND=1
    fi
fi

GO_FILES=$(find . -name "*.go" -not -path './.agents/*' 2>/dev/null || true)
if [ -n "$GO_FILES" ]; then
    raw_go_env=$(echo "$GO_FILES" | grep -v "config" | xargs grep -rn "os\.Getenv" 2>/dev/null || true)
    if [ -n "$raw_go_env" ]; then
        echo "  [WARNING] Raw 'os.Getenv' access found outside configuration modules:"
        echo "$raw_go_env" | sed 's/^/    /'
        RAW_ENV_FOUND=1
    fi
fi

if [ "$RAW_ENV_FOUND" -eq 0 ]; then
    echo "  [PASS] Domain isolation looks healthy (no scattered raw env reads)."
fi

# 5. Check Git Upstream Synchronization
echo "Check 5: Git Upstream Synchronization Check"
# Attempt to fetch upstream changes silently to check sync state (gracefully handle failures/offline)
if command -v timeout >/dev/null 2>&1; then
    GIT_TERMINAL_PROMPT=0 GIT_SSH_COMMAND="ssh -o BatchMode=yes" timeout 5 git fetch origin >/dev/null 2>&1 || true
elif command -v gtimeout >/dev/null 2>&1; then
    GIT_TERMINAL_PROMPT=0 GIT_SSH_COMMAND="ssh -o BatchMode=yes" gtimeout 5 git fetch origin >/dev/null 2>&1 || true
else
    GIT_TERMINAL_PROMPT=0 GIT_SSH_COMMAND="ssh -o BatchMode=yes" git -c transfer.timeout=5 fetch origin >/dev/null 2>&1 || true
fi

LOCAL=$(git rev-parse HEAD 2>/dev/null || echo "none")
REMOTE=$(git rev-parse @{u} 2>/dev/null || echo "none")
BASE=$(git merge-base HEAD @{u} 2>/dev/null || echo "none")

if [ "$LOCAL" = "none" ] || [ "$REMOTE" = "none" ]; then
    echo "  [WARNING] No upstream tracking branch set or Git repository not initialized."
elif [ "$LOCAL" = "$REMOTE" ]; then
    echo "  [PASS] Local branch is up-to-date with upstream."
elif [ "$LOCAL" = "$BASE" ]; then
    echo "  [FAIL] Workspace is behind upstream! Run 'git pull' before letting the agent modify files."
    FAILED=1
elif [ "$REMOTE" = "$BASE" ]; then
    echo "  [PASS] Local branch is ahead of upstream (unpushed commits)."
else
    echo "  [FAIL] Workspace has diverged from upstream! Please reconcile branches before modifying files."
    FAILED=1
fi

# 6. Check Schema Index Registration Compliance
echo "Check 6: Schema Index Registration Compliance"
SCHEMA_ERRORS=0
if [ -f ".agents/schema.md" ]; then
    if [ -d ".agents/schemas" ]; then
        for schema_file in .agents/schemas/*.md; do
            if [ -f "$schema_file" ]; then
                base_name=$(basename "$schema_file")
                # Verify registration in schema.md
                if ! grep -q "$base_name" ".agents/schema.md"; then
                    echo "  [FAIL] Domain schema file '$base_name' is NOT registered in '.agents/schema.md'!"
                    SCHEMA_ERRORS=$((SCHEMA_ERRORS + 1))
                fi
            fi
        done
    fi
else
    echo "  [FAIL] Primary schema index '.agents/schema.md' is missing!"
    SCHEMA_ERRORS=$((SCHEMA_ERRORS + 1))
fi

if [ "$SCHEMA_ERRORS" -eq 0 ]; then
    echo "  [PASS] All domain schemas are correctly indexed."
else
    FAILED=1
fi

# 7. Check Gitignore Configuration Compliance
echo "Check 7: Gitignore Configuration Compliance"
GITIGNORE_ERRORS=0
if [ -f ".gitignore" ]; then
    # Verify that .gitignore does NOT ignore .agents/ or AGENTS.md globally
    if grep -E -q "^\.agents/?$" .gitignore; then
        echo "  [FAIL] .gitignore ignores '.agents/' folder globally! Please remove it."
        GITIGNORE_ERRORS=$((GITIGNORE_ERRORS + 1))
    fi
    if grep -q "^AGENTS.md$" .gitignore; then
        echo "  [FAIL] .gitignore ignores 'AGENTS.md'! Please remove it."
        GITIGNORE_ERRORS=$((GITIGNORE_ERRORS + 1))
    fi
    # Verify that .agents/locks/ is ignored
    if ! grep -E -q "^\.agents/locks/?" .gitignore; then
        echo "  [WARNING] .gitignore does not ignore transient locks ('.agents/locks/')."
    fi
else
    echo "  [WARNING] No .gitignore file found in project root."
fi

if [ "$GITIGNORE_ERRORS" -eq 0 ]; then
    echo "  [PASS] Gitignore is correctly configured."
else
    FAILED=1
fi

# 8. Check Memory State Flag Enforcement
echo "Check 8: Memory State Flag Enforcement"
STATE_ERRORS=0
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached")
if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ]; then
    if [ -f "$MEMORY_FILE" ]; then
        if grep -Fq -- "- **State Flag**:" "$MEMORY_FILE"; then
            if ! grep -Ei -- "- \*\*State Flag\*\*:\s*\`?COMPLETED\`?" "$MEMORY_FILE" >/dev/null; then
                echo "  [FAIL] Commit rejected on branch '$CURRENT_BRANCH' because State Flag is not 'COMPLETED'!"
                echo "         Please complete your tasks and update memory.md State Flag to 'COMPLETED' first."
                STATE_ERRORS=$((STATE_ERRORS + 1))
            fi
        fi
    fi
else
    echo "  [PASS] Memory state flag checks bypassed on local feature branch '$CURRENT_BRANCH'."
fi

if [ "$STATE_ERRORS" -eq 0 ]; then
    if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ]; then
        echo "  [PASS] Memory state flag is 'COMPLETED' for production commit."
    fi
else
    FAILED=1
fi

echo "=========================================================="
if [ "$FAILED" -eq 0 ]; then
    echo "Workspace Status: VALIDATED"
    exit 0
else
    echo "Workspace Status: DEGRADED (Check issues detailed above)"
    exit 1
fi
EOF



# 12. Write Git hooks templates
write_template_safe ".agents/hooks/pre-commit" << 'EOF'
#!/usr/bin/env bash
# Antigravity Agent Git Hook
# Git pre-commit hook: Auto-run validations and tests
set -e

if [ -f .agents/scripts/validate.sh ]; then
    echo "Running workspace validation checks..."
    if ! .agents/scripts/validate.sh; then
        echo "Error: Workspace validation failed! Aborting commit." >&2
        exit 1
    fi
fi

if [ -f .agents/project_rules.md ]; then
    linter_line=$(grep "Linter command" .agents/project_rules.md || echo "")
    linter_cmd=$(echo "$linter_line" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^`//' -e 's/`$//')
    if [ -n "$linter_cmd" ] && [ "$linter_cmd" != "echo 'No linter found'" ]; then
        echo "Running linter: $linter_cmd..."
        if ! eval "$linter_cmd"; then
            echo "Error: Linter check failed! Aborting commit." >&2
            exit 1
        fi
        echo "  [PASS] Linter check passed."
    fi

    test_line=$(grep "Test runner command" .agents/project_rules.md || echo "")
    test_runner=$(echo "$test_line" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^`//' -e 's/`$//')
    if [ -n "$test_runner" ] && [ "$test_runner" != "echo 'No test suite found'" ]; then
        echo "Running test suite: $test_runner..."
        if ! eval "$test_runner"; then
            echo "Error: Tests failed! Aborting commit." >&2
            exit 1
        fi
        echo "  [PASS] All tests passed."
    fi
fi

# Chain to backup pre-commit hook if it exists
if [ -f .git/hooks/pre-commit.backup ]; then
    if [ -x .git/hooks/pre-commit.backup ]; then
        .git/hooks/pre-commit.backup "$@"
    else
        sh .git/hooks/pre-commit.backup "$@"
    fi
fi
EOF

write_template_safe ".agents/hooks/post-commit" << 'EOF'
#!/usr/bin/env bash
# Antigravity Agent Git Hook
# Auto-sync Git branch and commit hash to agent memory ledger
if [ -f .agents/scripts/helper.sh ]; then
    .agents/scripts/helper.sh sync-git
fi

# Auto-unlock all locks after a successful commit
if [ -d .agents/locks ] && [ "$(ls -A .agents/locks)" ]; then
    echo "Releasing active module locks..."
    for lock in .agents/locks/*.lock; do
        if [ -f "$lock" ]; then
            rm -f "$lock"
        fi
    done
    echo "  [PASS] All active locks released."
fi

# Chain to backup post-commit hook if it exists
if [ -f .git/hooks/post-commit.backup ]; then
    if [ -x .git/hooks/post-commit.backup ]; then
        .git/hooks/post-commit.backup "$@"
    else
        sh .git/hooks/post-commit.backup "$@"
    fi
fi
EOF

write_template_safe ".agents/hooks/commit-msg" << 'EOF'
#!/usr/bin/env bash
# Antigravity Agent Git Hook
# Git commit-msg hook: Enforce Conventional Commits specification
set -e

commit_msg_file="$1"
# Read commit message, ignoring comments
commit_msg=$(grep -v '^#' "$commit_msg_file" | tr -d '\n' || true)

# Ignore empty messages or automatic merge commits
if [ -z "$commit_msg" ] || [[ "$commit_msg" =~ ^Merge\ branch ]] || [[ "$commit_msg" =~ ^Merge\ remote-tracking\ branch ]]; then
    exit 0
fi

# Conventional Commits regex: type(scope): description
convention_regex="^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert|merge)(\([A-Za-z0-9_\-\/]+\))?: .+$"

if ! echo "$commit_msg" | grep -E -q "$convention_regex"; then
    echo "==========================================================" >&2
    echo "  [FAIL] Commit Message Format Rejected!" >&2
    echo "==========================================================" >&2
    echo "Your commit message: '$commit_msg'" >&2
    echo "Does not conform to the Conventional Commits specification." >&2
    echo "" >&2
    echo "Standard format: <type>(<scope>): <description>" >&2
    echo "Example: feat(auth): add google OAuth login flow" >&2
    echo "Example: fix(db): resolve migration lock issue" >&2
    echo "" >&2
    echo "Allowed types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert, merge" >&2
    echo "==========================================================" >&2
    exit 1
fi

# Chain to backup commit-msg hook if it exists
if [ -f .git/hooks/commit-msg.backup ]; then
    if [ -x .git/hooks/commit-msg.backup ]; then
        .git/hooks/commit-msg.backup "$@"
    else
        sh .git/hooks/commit-msg.backup "$@"
    fi
fi
EOF

if [ -f .agents/bootstrap.sh ]; then chmod +x .agents/bootstrap.sh; fi
if [ -f .agents/scripts/helper.sh ]; then chmod +x .agents/scripts/helper.sh; fi
if [ -f .agents/scripts/recon.sh ]; then chmod +x .agents/scripts/recon.sh; fi
if [ -f .agents/scripts/validate.sh ]; then chmod +x .agents/scripts/validate.sh; fi
if [ -f .agents/hooks/pre-commit ]; then chmod +x .agents/hooks/pre-commit; fi
if [ -f .agents/hooks/post-commit ]; then chmod +x .agents/hooks/post-commit; fi
if [ -f .agents/hooks/commit-msg ]; then chmod +x .agents/hooks/commit-msg; fi

if [ -d .git ]; then
    mkdir -p .git/hooks
    install_git_hook_safe "pre-commit"
    install_git_hook_safe "post-commit"
    install_git_hook_safe "commit-msg"
    log_success "Git pre-commit, post-commit, and commit-msg hooks processed."
fi



# Run auto-recon immediately to initialize configuration blueprints
log_info "Running autonomous reconnaissance to initialize workspace..."
if [ -f .agents/scripts/recon.sh ]; then
    if [ "$FORCE_OVERWRITE" = "true" ]; then
        .agents/scripts/recon.sh --force
    else
        .agents/scripts/recon.sh
    fi
fi

echo "=========================================================="
echo "Workspace Initialization Complete!"
echo "Global Agent Protocol written to: AGENTS.md"
echo "Active Memory Ledger written to: .agents/memory.md"
echo "Technical Schema Reference written to: .agents/schema.md"
echo "Architectural Blueprint written to: .agents/project_rules.md"
echo "Architectural Decision Records template written to: .agents/adr.md"
echo "Locks folder created at: .agents/locks/"
echo "Schemas folder created at: .agents/schemas/"
echo "Helper Scripts created at: .agents/scripts/"
echo "Git Hooks created at: .agents/hooks/"
echo "Generalized Skills loaded in: .agents/skills/"
echo "=========================================================="
echo "Workspace diagnostics status:"
.agents/scripts/helper.sh doctor || true
echo "=========================================================="

# Save a copy of the bootstrapper inside .agents/ for future updates/resets
if [ -f "$0" ]; then
    cp "$0" .agents/bootstrap.sh
    chmod +x .agents/bootstrap.sh
elif [ -f bootstrap.sh ]; then
    cp bootstrap.sh .agents/bootstrap.sh
    chmod +x .agents/bootstrap.sh
fi

# Self-cleanup if bootstrap.sh is executed from the project root (unless we are in the template development repository)
if [ -f bootstrap.sh ]; then
    is_dev=false
    if [ -d .git ]; then
        origin=$(git config --get remote.origin.url || echo "")
        if [[ "$origin" =~ "antigravity-agents" ]]; then
            is_dev=true
        fi
    fi
    if [ "$is_dev" = "false" ]; then
        log_info "Cleaning up root bootstrapper script..."
        rm -f bootstrap.sh
    fi
fi

