#!/usr/bin/env bash

# Antigravity Agent Workspace Bootstrapper
# This script initializes a clean, decoupled agent memory and protocol setup in any project repository.

set -euo pipefail

# Parse arguments
FORCE_OVERWRITE=false
UPDATE_ONLY=false
CREATE_VENV=false
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
        -v|--venv|--create-venv)
            CREATE_VENV=true
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

echo -e "${BLUE}==========================================================${NC}"
echo -e "${CYAN}${BOLD}   🚀  ANTIGRAVITY AGENT WORKSPACE SETUP INITIALIZER   ${NC}"
echo -e "${BLUE}==========================================================${NC}"
log_info "Checking System Prerequisites..."
echo -e "${BLUE}----------------------------------------------------------${NC}"

if ! command -v git >/dev/null 2>&1; then
    log_error "Git is required but not installed! Please install Git first."
    exit 1
fi
log_success "Git is installed."

if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
    log_error "Python 3 is required but not installed! Please install Python 3 first."
    exit 1
fi

PY_CMD="python3"
if ! command -v python3 >/dev/null 2>&1; then
    PY_CMD="python"
fi

PY_VERSION=$($PY_CMD -c 'import sys; print(sys.version_info[0])' 2>/dev/null)
if [ "$PY_VERSION" != "3" ]; then
    log_error "Python 3 is required! Found Python version $PY_VERSION. Please install Python 3."
    exit 1
fi
log_success "Python 3 is installed."

if [ "$CREATE_VENV" = "true" ]; then
    log_info "Creating Python virtual environment (.venv)..."
    if ! $PY_CMD -m venv .venv; then
        log_warning "Failed to create virtual environment! Continuing with system Python."
    else
        log_success "Virtual environment (.venv) created successfully."
        if [ -f ".venv/bin/python" ]; then
            PY_CMD=".venv/bin/python"
        elif [ -f ".venv/bin/python3" ]; then
            PY_CMD=".venv/bin/python3"
        fi
    fi
fi

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
mkdir -p .agents/rules
mkdir -p .agents/adrs
mkdir -p .github/workflows

# Check for legacy rules folder and migrate
if [ -d ".agent/rules" ]; then
    log_info "Legacy rules folder .agent/rules found. Migrating to .agents/rules/..."
    if [ "$(ls -A .agent/rules 2>/dev/null)" ]; then
        cp -r .agent/rules/* .agents/rules/
        log_info "  - Migrated rule files: $(ls -A .agent/rules | tr '\n' ' ')"
    fi
    rm -rf .agent/rules
    if [ -d ".agent" ] && [ ! "$(ls -A .agent 2>/dev/null)" ]; then
        rm -rf .agent
    fi
    log_success "Migration of legacy rules complete."
    if [ -f .agents/memory.md ]; then
        if ! grep -q "Legacy rules migrated" .agents/memory.md; then
            sed -i '/## 3. Relayed Context/a - **Migration Log**: Legacy rules migrated from .agent/rules to .agents/rules.' .agents/memory.md
        fi
    fi
fi

# 2. Write AGENTS.md (Global Agent Protocol) to project root
write_template_safe "AGENTS.md" << 'EOF'
# Global Agent Protocol (GAP)

This document dictates the absolute boundaries, operational procedures, memory constraints, and quality gates for all AI agent operations in this workspace. Compliance is mandatory for every agent execution.

---

## 1. Bootstrapping & Cognitive Alignment
- **Autonomous Bootstrapping**: At the beginning of any session or task context, the agent MUST read the core files. The agent MUST NOT perform any file edits, command execution, or code modifications prior to reading these files. To maximize prompt prefix cache hits, the agent or the loading interface MUST retrieve these files in the exact sequence from *Most Static* to *Most Dynamic*:
  1. The Global Agent Protocol (this file: [AGENTS.md](file://./AGENTS.md)).
  2. The Project-Specific Rules, if available (e.g. [.agents/rules/project_rules.md](file://./.agents/rules/project_rules.md)).
  3. The Schema Reference database, if available (e.g. [.agents/schema.md](file://./.agents/schema.md)).
  4. The Active Memory Ledger ([.agents/memory.md](file://./.agents/memory.md)).
- **Strict Adherence to .agents Workspace Blueprints**: The agent must strictly follow all files, guidelines, and directories under the `.agents/` folder. This includes:
  * **Memory & Sprints**: Aligning checklists and state flags in [memory.md](file://./.agents/memory.md).
  * **Architectural Blueprint**: Strictly following stack directories, lint/build/test scripts, and layers defined in [project_rules.md](file://./rules/project_rules.md).
  * **Domain Schemas Index**: Reading database models and API specs mapped in [schema.md](file://./.agents/schema.md) and domain schemas under `schemas/`.
  * **Architectural Decisions**: Logging and respecting design decisions recorded in [adr.md](file://./.agents/adr.md).
  * **Task Workflows**: Reading/writing granular implementation plans under `workflows/task_*.md`.
  * **Decoupled Skills**: Executing specialized commands and routines according to instructions under `skills/`.
  * **Hooks & Verification**: Relying on Git pre-commit/post-commit/commit-msg hooks inside `hooks/` and the validate script `validate.sh`.
- **Autonomy Principle & Strict Alignment**: The agent must rely on these documents and the codebase layout rather than asking the user repetitive or basic design questions. If a design pattern is missing or a user's instruction is ambiguous, default to standard industry best practices or ask a direct, clear multiple-choice question using the `ask_question` tool.
- **Strict Zero-Hallucination Rule**: Under no circumstances should the agent make assumptions or guess about dependencies, compiler configurations, path routes, API structures, or command options. If they are not detailed in the files read during bootstrapping, verify them programmatically using search and read tools before taking any actions.

## 2. Zero-Hallucination & Import Verification Gates
- **Fact-Checking over Guessing**: Never assume a file exists, a package is installed, or a function signature is correct. If a detail is missing, search and verify it.
- **Symbol & Command Verification Gate**: Before writing an import statement, invoking a method/function, or proposing a terminal command/script to execute, the agent MUST run `view_file` or `grep_search` to verify:
  1. The file path and module export spelling are correct.
  2. The package, linter, or script command exists in the workspace configuration files (e.g., `package.json`, `go.mod`, or `.agents/rules/project_rules.md`). Do not guess or execute unverified third-party commands.
- **Interactive Clarification Gate**: If the requirements, symbols, or parameters of a task remain ambiguous even after searching the codebase, the agent MUST present a clear, multiple-choice question using the `ask_question` tool to resolve the ambiguity with the user rather than guessing or hallucinating the path forward.
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
  - Technology or library dependencies (e.g. npm package additions, go modules) must immediately update `.agents/rules/project_rules.md` and the workspace package configuration files (e.g. `package.json`, `go.mod`).
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
4. **Documentation Gate**: If the changes introduce or modify features, CLI subcommands, prerequisites, or installation requirements, the agent MUST immediately update `README.md`. For every feature, bugfix, or chore task completed, the agent MUST record the changes under the current version section in `CHANGELOG.md` following the "Keep a Changelog" format.
5. **Commit Preparation**: Update the task checklist state to `[x]` and state flag to `COMPLETED` in `memory.md` (or the dynamic workflow checklist).
6. **Commit**: Stage files and execute the commit using the helper command: `./.agents/scripts/helper.sh commit <type> <scope> "description" [files...]` to enforce automated Git profile and SSH key rotation. **Raw `git commit` is strictly forbidden** for agents and developers to prevent profile or authentication key misalignment.
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
- **Refinement Triggers**: If a lint error, type mismatch, or testing bottleneck repeats more than 3 times, the agent MUST immediately refine [.agents/rules/project_rules.md](file://./.agents/rules/project_rules.md) or update the respective skill file to document the solution permanently.
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
When the agent starts execution in a workspace, it must check if the project-specific blueprints (.agents/rules/project_rules.md and .agents/schema.md) are either missing, empty, or contain default templates.
If the blueprints are not initialized for the current project:
1. **Trigger Autonomous Reconnaissance**: Immediately execute `./.agents/scripts/helper.sh recon` to automatically discover the tech stack, directory boundaries, build/test/lint commands, Relational DB/ORM integrations, and environment variable configuration template.
2. **Interactive User Alignment**: Present the auto-detected stack and boundaries to the user for quick confirmation or adjustments.
3. **Refine Blueprint**: Adjust [.agents/rules/project_rules.md](file://./.agents/rules/project_rules.md) and [.agents/schema.md](file://./.agents/schema.md) based on user confirmation.
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
- **Self-Improving Memory Feedback Loop**: The agent must continuously audit its performance. If any structural bugs or compilation failures occur multiple times, the agent must proactively update `.agents/rules/project_rules.md` to prevent future errors.

EOF
write_template_safe ".agents/memory.md" << 'EOF'
# Agent Core Memory

> **Memory Schema Version**: 5.0.0  
> **Target System**: Antigravity Agent Core
> **Active Guidelines**: Read [AGENTS.md](file://../AGENTS.md) and [.agents/rules/project_rules.md](file://./rules/project_rules.md) for execution details. Keep this file under 100 lines at all times.

---

## 1. Git State & Infrastructure Runtime
- **Active Branch**: main
- **Last Commit Reference**: 7b797b1
- **Active Pull Request Target**: `main`
- **Infrastructure Health Status**:
  - Database: `HEALTHY`
  - Cache/Broker: `HEALTHY`
  - Primary API Server: `HEALTHY`

---

## 2. Active Epic & Sub-Tasks Execution Matrix
- **Primary Epic**: Initial Setup
- **Current Task Target**: Optimize validate.sh find precedence and add Python env scan
- **State Flag**: `COMPLETED`

### Sprint Tasks Checklist
- [x] Configure workspace rules and verify stack
- [x] Run health check doctor
- [x] Optimize validate.sh find precedence and add Python env scan

---

## 3. Relayed Context & Handover Notes
- **Last Active Agent**: None
- **Last Action Completed**: Initialized clean Antigravity Agent Core workspace.
- **Next Planned Action**: None. Ready for new features or tasks.
- **Blockers / Runtime Notes**: None.

---

## 4. Reference Links Index
- **Core Guidelines**: [AGENTS.md](file://../AGENTS.md)
- **Project Specific Rules**: [project_rules.md](file://./rules/project_rules.md)
- **Database Schema**: [schema.md](file://./schema.md)
- **Design Decisions**: [adr.md](file://./adr.md)
- **Sprint Archives**: [archive/](file://./archive/)

EOF

# 4. Write .agents/rules/project_rules.md template
write_template_safe ".agents/rules/project_rules.md" << 'EOF'
---
name: project-rules
activation: Always On
description: "Project architecture blueprint and technical stack rules."
---

# Project Architecture Blueprint (PAB)

This file defines the specific technical stack, directory boundaries, coding standards, and system dependencies for this project.


---

## 1. Stack & Directory Boundaries
- **Primary Language/Framework**: Python 3 & Shell Scripting (Bash / PowerShell)
- **Directory Structure**:
  - `tests/` -> Project workspace component
  - `config/` -> Project workspace component

## 2. Architectural Conventions
- **Architectural Pattern**: Standard Model-View-Controller (MVC)
- **Boundary insulation**: Core domain logic must remain completely independent of external libraries, databases, and frameworks.

## 3. Spacing & Styling Standards
- **Linter command**: `python3 -m py_compile tests/test_rotation.py`
- **Build validation**: `echo 'No build command needed'`
- **Test runner command**: `python3 tests/test_rotation.py`
- **Follow formatting**: Follow PEP 8 guidelines for Python and standard style for shell scripts.

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
- **Git Profile Rotation Enforcement**: All commits MUST be executed via `./.agents/scripts/helper.sh commit` to enforce round-robin profile and SSH key rotation. Running raw `git commit` directly is prohibited.
- **README & Changelog Update Gate**: Any functional change affecting CLI subcommands, options, prerequisites, or core behavior MUST immediately be documented in `README.md`. Every completed sprint task must add a changelog entry to `CHANGELOG.md` under the current version section following "Keep a Changelog" standards.
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
# Architectural Decision Records (ADR) - Index Map

This document registers the historical technical design decisions, rationales, and consequences accepted in this project.

---

## 1. Architectural Decisions Index
- [ADR-001: Initial Workspace Protocol Adoption](file://./adrs/001-initial-workspace-protocol.md) - Status: Accepted
- [ADR-002: Introduce Modular ADRs and Validation](file://./adrs/002-introduce-modular-adrs-and-validation.md) - Status: Accepted
- [ADR-003: API Key Rotation and PowerShell Wrappers](file://./adrs/003-api-key-rotation-and-powershell-wrappers.md) - Status: Accepted
- [ADR-004: Clean Project Isolation for Injected Agent Setup](file://./adrs/004-framework-isolation.md) - Status: Accepted
- [ADR-005: Standardize Documentation Layout](file://./adrs/005-standardize-documentation-layout.md) - Status: Accepted

EOF

# 7.2 Write .agents/adrs/001-initial-workspace-protocol.md template
write_template_safe ".agents/adrs/001-initial-workspace-protocol.md" << 'EOF'
# ADR-001: Initial Workspace Protocol Adoption

- **Date**: 2026-06-13
- **Status**: Accepted

## Context
The workspace needs a structured operational protocol for AI engineering agents to ensure version alignment, zero-hallucination execution, and high token efficiency.

## Decision
Adopt the Antigravity Agent Core (AAC) protocol, establishing `AGENTS.md` and the `.agents/` structure containing locks, rules, schemas, and active task memory ledgers.

## Consequences
Developers and agents must follow strict bootstrapping sequences and use the helper scripts/Git hooks for validated, atomic commits.

EOF

# 7.2 Write .agents/adrs/002-introduce-modular-adrs-and-validation.md template
write_template_safe ".agents/adrs/002-introduce-modular-adrs-and-validation.md" << 'EOF'
# ADR-002: Introduce Modular ADRs and Validation

- **Date**: 2026-06-14
- **Status**: Accepted

## Context
Architectural Decision Records (ADRs) were previously documented inside a monolithic `.agents/adr.md` file. As the workspace expands with more features, this monolithic file becomes cluttered, makes parsing difficult, and does not support granular tracking.

## Decision
Modularize the ADR structure:
1. Store individual ADR files inside `.agents/adrs/` with chronological numerical slug filenames (e.g., `002-introduce-modular-adrs-and-validation.md`).
2. Keep `.agents/adr.md` strictly as a high-level index map.
3. Introduce `./.agents/scripts/helper.sh create-adr <title> [status]` to automate ADR creation and index registration.
4. Add automated ADR compliance verification in `validate.sh` (Check 10).

## Consequences
- Workspace decisions are easily searchable, modular, and trackable.
- Automatically prevents committing incomplete ADRs containing placeholders.
- Simplifies bootstrapping and workspace upgrades.

EOF

# 7.2 Write .agents/adrs/003-api-key-rotation-and-powershell-wrappers.md template
write_template_safe ".agents/adrs/003-api-key-rotation-and-powershell-wrappers.md" << 'EOF'
# ADR-003: API Key Rotation and PowerShell Wrappers

## Context
When running agent operations in environments subject to rate limits or API credit boundaries (such as Gemini/OpenAI), hard limits can block task completion. In multi-platform environments (both Linux and Windows PowerShell), a consistent mechanism is required to automatically rotate API credentials and track per-profile token budgets.

## Decision
We implemented a hybrid API profile rotation framework consisting of:
1. **Local Key File (`.agents/api_keys`)**: Configured with multiple named profiles (e.g., `personal`, `work`, `backup`).
2. **Bash Wrapper (`api-rotate-wrapper.sh`)**: Intercepts command executions on Unix, catches rate limit status codes (including `429`, `129`, `3`, and Unix modulo `173`), and rotates keys at runtime.
3. **PowerShell Wrapper (`api-rotate-wrapper.ps1`)**: Intercepts command executions on Windows PowerShell, supports equivalent rotation, and allows dot-source auto-loading of keys.
4. **Token Budget Guard**: Tracks per-profile token consumption dynamically inside `.agents/token_budget.json`, checking usage before requests (proactive) and tracking after success.

## Consequences
- **Positive**: Seamless rate-limit bypass across both Unix (Bash) and Windows (PowerShell) development setups.
- **Positive**: Prevention of budget overruns via profile-level tracking.
- **Neutral**: Modulo wrapping logic (exiting with 173 instead of 429 on Linux) must be accounted for in Unix test suites.
- **Negative**: Key configuration requires manual setup of `.agents/api_keys` before wrappers can function.

EOF

# 7.3 Write .agents/git_profiles.example template
write_template_safe ".agents/git_profiles.example" << 'EOF'
# Antigravity Git Profiles Template
# Copy this file to '.agents/git_profiles' and fill in your git accounts
# to enable easy profile switching, automated round-robin commit rotation, and SSH key rotation.

# Profile 1 (e.g. Work account)
work.name=Developer Work Name
work.email=work@company.com
# Optional: Add SSH key path to automatically rotate SSH authentication for Git operations
# work.ssh_key=~/.ssh/id_rsa_work

# Profile 2 (e.g. Personal account)
personal.name=Developer Personal Name
personal.email=personal@gmail.com
# personal.ssh_key=~/.ssh/id_rsa_personal

# Profile 3 (e.g. Side project / alternative account)
sideproject.name=Side Project Name
sideproject.email=side@project.com
# sideproject.ssh_key=~/.ssh/id_rsa_side

EOF

# 7.4 Write .agents/api_keys.example template
write_template_safe ".agents/api_keys.example" << 'EOF'
# Antigravity API Profiles Template
# Copy this file to '.agents/api_keys' and fill in your API tokens/keys.
# This file is used by the 'api-profile' subcommand to switch or rotate 
# API keys locally (e.g. GEMINI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY).
#
# IMPORTANT: Keep '.agents/api_keys' private and never commit it to Git.
# The default gitignore and validation rules will block it.

# Profile 1: Personal Account
personal.GEMINI_API_KEY=AIzaSyA_personal_key_here
personal.OPENAI_API_KEY=sk-proj-personal_key_here

# Profile 2: Work / Company Account
work.GEMINI_API_KEY=AIzaSyB_work_key_here
work.OPENAI_API_KEY=sk-proj-work_key_here
work.ANTHROPIC_API_KEY=sk-ant-work_key_here

# Profile 3: Backup / Alternative Account
backup.GEMINI_API_KEY=AIzaSyC_backup_key_here
backup.OPENAI_API_KEY=sk-proj-backup_key_here

EOF

# 7.1 Write .github/workflows/antigravity.yml template
write_template_safe ".github/workflows/antigravity.yml" << 'EOF'
name: Antigravity Workspace Validator

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Git config
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"

      - name: Run Antigravity Workspace Validation
        run: |
          chmod +x .agents/scripts/validate.sh
          ./.agents/scripts/validate.sh

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

# Write .agents/skills/api-rotator/SKILL.md
write_template_safe ".agents/skills/api-rotator/SKILL.md" << 'EOF'
---
name: api-rotator
description: Auto-rotate API keys and profiles when encountering rate-limiting
scripts:
  - scripts/main.py
---

# api-rotator Skill

This skill provides a high-fidelity wrapper script in Python to execute agent LLM API calls with built-in hybrid rotation. It proactively checks the token budget for the active profile before requests and reactively rotates profiles on rate limits (HTTP 429).

## 1. Input Specification
- `--prompt` (`-p`): Prompt text to send to the LLM (default: "Hello, World!").
- `--provider`: LLM provider (`gemini` or `openai`).
- `--model`: Model name to use.
- `--tokens`: Quota/token consumption count to log upon successful execution (default: 150).
- `--simulate-limit`: Simulated rate-limit retry count (useful for testing rotation without API keys).
- `--debug`: Enable verbose debug logging.

## 2. Operational Procedures
1. Ensure API profiles are configured in `.agents/api_keys`.
2. Activate a profile using `./.agents/scripts/helper.sh api-profile [name]`.
3. Run the rotator skill:
   ```bash
   python3 .agents/skills/api-rotator/scripts/main.py --prompt "Test prompt" --simulate-limit 1
   ```
4. Verify that the script automatically rotates to the next profile, reloads the keys, retries, and successfully outputs the result.

## 3. Decision Matrix
- **Check Budget**: If the active profile's token budget is exhausted, rotate to the next profile.
- **Catch Rate Limit**: If the execution fails with HTTP 429 or equivalent quota error, rotate the profile, reload, and retry.
- **Log Usage**: If successful, log the token usage under the active profile name.

## 4. Error Mitigation Tree
- If all profiles are exhausted or an unhandled exception occurs, log the error details and exit with status code 1.

## 5. Output Verification Gate
- [x] Executable script auto-rotates keys successfully under rate-limiting simulation.

EOF

# Write .agents/skills/api-rotator/scripts/main.py
write_template_safe ".agents/skills/api-rotator/scripts/main.py" << 'EOF'
#!/usr/bin/env python3
import argparse
import sys
import json
import logging
import os
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_active_api_keys():
    """
    Parses .agents/active_api_keys to load active API keys into the environment.
    """
    path = ".agents/active_api_keys"
    if os.path.exists(path):
        logging.info(f"Loading active API keys from {path}...")
        with open(path, "r") as f:
            for line in f:
                if line.startswith("export "):
                    # strip 'export ' and split on first '='
                    parts = line[7:].strip().split("=")
                    if len(parts) >= 2:
                        var_name = parts[0]
                        # join remaining parts in case value contains '='
                        var_val = "=".join(parts[1:]).strip('"\'')
                        os.environ[var_name] = var_val
                        logging.debug(f"Loaded env var: {var_name}")
    else:
        logging.warning("No active API keys file found at .agents/active_api_keys.")

def check_and_rotate_budget():
    """
    Proactively checks the current active profile's token budget.
    Rotates to the next profile if the limit is exceeded.
    """
    profile_file = ".agents/active_api_profile_name"
    if not os.path.exists(profile_file):
        return
        
    with open(profile_file, "r") as f:
        profile = f.read().strip()
        
    # Import CLI utils dynamically
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cli_dir = os.path.abspath(os.path.join(script_dir, "../../../scripts/cli"))
    if cli_dir not in sys.path:
        sys.path.insert(0, cli_dir)
        
    try:
        import utils
        budget = utils.load_budget()
    except Exception as e:
        logging.warning(f"Failed to load budget via CLI utils: {e}. Falling back to manual read.")
        budget_file = ".agents/token_budget.json"
        if not os.path.exists(budget_file):
            return
        try:
            with open(budget_file, "r") as f:
                budget = json.load(f)
        except Exception:
            return
        
    profiles = budget.get("profiles", {})
    if profile in profiles:
        prof_data = profiles[profile]
        usage = prof_data.get("current_token_usage", 0)
        limit = prof_data.get("max_token_budget", 500000)
        if usage >= limit:
            logging.info(f"Quota limit reached for profile '{profile}' ({usage}/{limit}). Proactively rotating...")
            # Rotate using helper.sh
            subprocess.run(["./.agents/scripts/helper.sh", "api-profile", "rotate"], check=True)
            load_active_api_keys()

def run_skill(args):
    """
    Main logic of the skill script.
    """
    # 1. Proactive Budget Check & Initial Key Load
    check_and_rotate_budget()
    load_active_api_keys()

    prompt = args.prompt
    provider = args.provider
    model = args.model
    simulate_limit = args.simulate_limit
    
    max_retries = 3
    # Try parsing number of API profiles configured to set max_retries dynamically
    api_keys_file = ".agents/api_keys"
    if os.path.exists(api_keys_file):
        try:
            with open(api_keys_file, "r") as f:
                prefixes = set()
                for line in f:
                    if line.strip() and not line.strip().startswith("#") and "=" in line:
                        prefix = line.split(".")[0].strip()
                        prefixes.add(prefix)
                if prefixes:
                    max_retries = len(prefixes)
        except Exception:
            pass

    for attempt in range(max_retries):
        # Read the current profile name for log visibility
        profile_file = ".agents/active_api_profile_name"
        profile_name = "default"
        if os.path.exists(profile_file):
            with open(profile_file, "r") as f:
                profile_name = f.read().strip()
                
        logging.info(f"Attempt {attempt + 1}/{max_retries} using profile: '{profile_name}'")
        
        # 2. Simulate or execute API request
        try:
            # Check if simulation is requested
            if simulate_limit is not None and attempt < simulate_limit:
                logging.warning(f"Simulating API rate-limit error (HTTP 429) for attempt {attempt + 1}...")
                # Raise custom exception that mimics a rate limit/quota limit
                raise Exception("API rate limit exceeded. Status code: 429")
                
            # Try real imports/execution if packages are available
            if provider == "gemini":
                api_key = os.environ.get("GEMINI_API_KEY")
                if not api_key or api_key.endswith("_key_here") or "personal_key" in api_key:
                    # Treat mock keys as simulated success
                    logging.info("GEMINI_API_KEY is a placeholder/simulation key. Simulating successful call...")
                    response_text = f"[Simulated Response for prompt: '{prompt}']"
                else:
                    try:
                        import google.generativeai as genai
                        genai.configure(api_key=api_key)
                        gemini_model = genai.GenerativeModel(model)
                        response = gemini_model.generate_content(prompt)
                        response_text = response.text
                    except ImportError:
                        logging.warning("google-generativeai library is not installed. Falling back to simulation.")
                        response_text = f"[Simulated Response for prompt: '{prompt}']"
            elif provider == "openai":
                api_key = os.environ.get("OPENAI_API_KEY")
                if not api_key or api_key.endswith("_key_here") or "personal_key" in api_key:
                    logging.info("OPENAI_API_KEY is a placeholder/simulation key. Simulating successful call...")
                    response_text = f"[Simulated Response for prompt: '{prompt}']"
                else:
                    try:
                        import openai
                        client = openai.OpenAI(api_key=api_key)
                        response = client.chat.completions.create(
                            model=model,
                            messages=[{"role": "user", "content": prompt}]
                        )
                        response_text = response.choices[0].message.content
                    except ImportError:
                        logging.warning("openai library is not installed. Falling back to simulation.")
                        response_text = f"[Simulated Response for prompt: '{prompt}']"
            else:
                response_text = f"[Simulated Response for prompt: '{prompt}' on unsupported provider {provider}]"

            # 3. Successful execution: Log Token Usage
            tokens_used = args.tokens
            logging.info(f"API call successful! Logging {tokens_used} tokens for profile '{profile_name}'...")
            subprocess.run(["./.agents/scripts/helper.sh", "log-usage", str(tokens_used)], check=True)
            
            return {
                "status": "success",
                "profile": profile_name,
                "provider": provider,
                "model": model,
                "response": response_text,
                "tokens_logged": tokens_used
            }
            
        except Exception as e:
            # 4. Reactive Rotation: Check if it's a rate-limit / resource exhaustion error
            error_msg = str(e)
            is_rate_limit = False
            
            # Check for typical rate limit indicators in error message
            rate_limit_keywords = ["429", "rate limit", "resource_exhausted", "quota exceeded", "limit exceeded"]
            if any(kw in error_msg.lower() for kw in rate_limit_keywords):
                is_rate_limit = True
                
            if is_rate_limit and attempt < max_retries - 1:
                logging.warning(f"Rate limit hit: {error_msg}. Rotating API profile and retrying...")
                # Rotate profile
                subprocess.run(["./.agents/scripts/helper.sh", "api-profile", "rotate", "--rate-limited"], check=True)
                # Reload updated environment keys
                load_active_api_keys()
            else:
                # Re-raise the exception if not rate limited or if we ran out of profiles
                raise e

def main():
    parser = argparse.ArgumentParser(description="Python wrapper for api-rotator skill execution with hybrid rotation.")
    parser.add_argument('--prompt', '-p', type=str, default="Hello, World!", help="Prompt text to send to LLM")
    parser.add_argument('--provider', type=str, default="gemini", choices=["gemini", "openai"], help="LLM Provider")
    parser.add_argument('--model', type=str, default="gemini-1.5-flash", help="Model name")
    parser.add_argument('--tokens', type=int, default=150, help="Simulated token usage count")
    parser.add_argument('--simulate-limit', type=int, default=None, help="Number of attempts to simulate rate limits (e.g. 1)")
    parser.add_argument('--debug', action='store_true', help="Enable debug mode")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        
    try:
        output = run_skill(args)
        print(json.dumps(output, indent=2))
        sys.exit(0)
    except Exception as e:
        logging.error(f"Execution failed: {str(e)}")
        error_output = {
            "status": "error",
            "message": str(e)
        }
        print(json.dumps(error_output, indent=2))
        sys.exit(1)

if __name__ == '__main__':
    main()

EOF

# 9. Write helper.sh script
write_template_safe ".agents/scripts/helper.sh" << 'EOF'
#!/usr/bin/env bash

# Check for Python 3 (prefer virtual environment if available)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if [ -f "$PROJECT_ROOT/.venv/bin/python" ] && [ -x "$PROJECT_ROOT/.venv/bin/python" ]; then
    PY_CMD="$PROJECT_ROOT/.venv/bin/python"
elif [ -f "$PROJECT_ROOT/.venv/bin/python3" ] && [ -x "$PROJECT_ROOT/.venv/bin/python3" ]; then
    PY_CMD="$PROJECT_ROOT/.venv/bin/python3"
elif command -v python3 >/dev/null 2>&1; then
    PY_CMD="python3"
elif command -v python >/dev/null 2>&1 && [ "$(python -c 'import sys; print(sys.version_info[0])' 2>/dev/null)" = "3" ]; then
    PY_CMD="python"
else
    echo "Error: Python 3 is required to run the Antigravity helper CLI." >&2
    echo "Please install Python 3 and ensure it is in your PATH." >&2
    exit 1
fi

"$PY_CMD" "$(dirname "${BASH_SOURCE[0]}")/cli/helper.py" "$@"

EOF

# Write .agents/scripts/cli/commands/clean.py
write_template_safe ".agents/scripts/cli/commands/clean.py" << 'EOF'
import os
import sys
import subprocess
import shutil
import json
import utils

def run(args):
    print("==========================================================")
    print("  Starting Antigravity Agent Workspace Clean-up...        ")
    print("==========================================================")

    # 1. Clear locks directory (except cli.lock)
    locks_dir = os.path.join(utils.get_agents_dir(), "locks")
    if os.path.exists(locks_dir):
        print("Cleaning locks...")
        for item in os.listdir(locks_dir):
            if item == "cli.lock":
                continue
            item_path = os.path.join(locks_dir, item)
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
                print(f"  Removed lock: {item}")
            except Exception as e:
                print(f"  Warning: Failed to remove lock {item}: {e}", file=sys.stderr)

    # 2. Clear archives directory
    archive_dir = os.path.join(utils.get_agents_dir(), "archive")
    if os.path.exists(archive_dir):
        print("Cleaning sprint archives...")
        for item in os.listdir(archive_dir):
            item_path = os.path.join(archive_dir, item)
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
                print(f"  Removed archive: {item}")
            except Exception as e:
                print(f"  Warning: Failed to remove archive {item}: {e}", file=sys.stderr)

    # 3. Clear workflows (except task_workspace_cleanup_command.md)
    workflows_dir = os.path.join(utils.get_agents_dir(), "workflows")
    if os.path.exists(workflows_dir):
        print("Cleaning task workflows...")
        for item in os.listdir(workflows_dir):
            if item == "task_workspace_cleanup_command.md":
                continue
            item_path = os.path.join(workflows_dir, item)
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
                print(f"  Removed workflow: {item}")
            except Exception as e:
                print(f"  Warning: Failed to remove workflow {item}: {e}", file=sys.stderr)

    # 4. Reset token budget json
    budget_file = os.path.join(utils.get_agents_dir(), "token_budget.json")
    print("Resetting token budget...")
    default_budget = {
        "max_token_budget": 500000,
        "current_token_usage": 0,
        "alert_threshold_percent": 90,
        "profiles": {}
    }
    try:
        with open(budget_file, "w") as f:
            json.dump(default_budget, f, indent=2)
        print("  [SUCCESS] Token budget reset to default limits.")
    except Exception as e:
        print(f"  Error: Failed to reset token budget: {e}", file=sys.stderr)

    # 5. Reset API profile name and active keys
    profile_name_file = os.path.join(utils.get_agents_dir(), "active_api_profile_name")
    active_keys_sh = os.path.join(utils.get_agents_dir(), "active_api_keys")
    active_keys_ps1 = os.path.join(utils.get_agents_dir(), "active_api_keys.ps1")

    print("Resetting active API key configurations...")
    try:
        with open(profile_name_file, "w") as f:
            f.write("default\n")
            
        with open(active_keys_sh, "w") as f:
            f.write("# Active API Keys configuration\n")
            f.write("export GEMINI_API_KEY=\"\"\n")
            f.write("export OPENAI_API_KEY=\"\"\n")
            f.write("export ANTHROPIC_API_KEY=\"\"\n")
            
        with open(active_keys_ps1, "w") as f:
            f.write("# Active API Keys configuration for Windows PowerShell\n")
            f.write("$env:GEMINI_API_KEY=\"\"\n")
            f.write("$env:OPENAI_API_KEY=\"\"\n")
            f.write("$env:ANTHROPIC_API_KEY=\"\"\n")
        print("  [SUCCESS] API profile configurations and keys reset to clean templates.")
    except Exception as e:
        print(f"  Error: Failed to reset active API keys: {e}", file=sys.stderr)

    # 6. Reset memory.md to clean template
    memory_file = utils.get_memory_file()
    print("Resetting active memory ledger...")
    
    # Resolve branch and commit
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], 
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except:
        branch = "main"
        
    try:
        commit = subprocess.check_output(
            ["git", "log", "-n", "1", "--format=%h"], 
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except:
        commit = "none"

    clean_memory_content = f"""# Agent Core Memory

> **Memory Schema Version**: 5.0.0  
> **Target System**: Antigravity Agent Core
> **Active Guidelines**: Read [AGENTS.md](file://../AGENTS.md) and [.agents/rules/project_rules.md](file://./rules/project_rules.md) for execution details. Keep this file under 100 lines at all times.

---

## 1. Git State & Infrastructure Runtime
- **Active Branch**: {branch}
- **Last Commit Reference**: {commit}
- **Active Pull Request Target**: `main`
- **Infrastructure Health Status**:
  - Database: `HEALTHY`
  - Cache/Broker: `HEALTHY`
  - Primary API Server: `HEALTHY`

---

## 2. Active Epic & Sub-Tasks Execution Matrix
- **Primary Epic**: Initial Setup
- **Current Task Target**: Configure workspace rules and verify stack
- **State Flag**: `COMPLETED`

### Sprint Tasks Checklist
- [x] Configure workspace rules and verify stack
- [x] Run health check doctor

---

## 3. Relayed Context & Handover Notes
- **Last Active Agent**: None
- **Last Action Completed**: Initialized clean Antigravity Agent Core workspace.
- **Next Planned Action**: None. Ready for new features or tasks.
- **Blockers / Runtime Notes**: None.

---

## 4. Reference Links Index
- **Core Guidelines**: [AGENTS.md](file://../AGENTS.md)
- **Project Specific Rules**: [project_rules.md](file://./rules/project_rules.md)
- **Database Schema**: [schema.md](file://./schema.md)
- **Design Decisions**: [adr.md](file://./adr.md)
- **Sprint Archives**: [archive/](file://./archive/)
"""
    try:
        with open(memory_file, "w") as f:
            f.write(clean_memory_content)
        print("  [SUCCESS] memory.md reset to default clean template.")
    except Exception as e:
        print(f"  Error: Failed to reset memory.md: {e}", file=sys.stderr)

    print("==========================================================")
    print("  Workspace clean-up completed successfully!             ")
    print("==========================================================")

EOF

# Write .agents/scripts/cli/commands/menu.py
write_template_safe ".agents/scripts/cli/commands/menu.py" << 'EOF'
import os
import sys
import subprocess
import shutil
import utils

# ANSI Color Escape Codes
C_HEADER = '\033[95m'
C_BLUE = '\033[94m'
C_CYAN = '\033[96m'
C_GREEN = '\033[92m'
C_YELLOW = '\033[93m'
C_RED = '\033[91m'
C_GRAY = '\033[90m'
C_BOLD = '\033[1m'
C_END = '\033[0m'

def color(text, ansi_code):
    """Wrap text in ANSI color codes if stdout is a TTY."""
    if sys.stdout.isatty():
        return f"{ansi_code}{text}{C_END}"
    return text

def get_progress_bar(pct, length=15):
    """Generate a visual progress bar string."""
    filled = int(round(length * pct / 100))
    filled = max(0, min(filled, length))
    bar = "█" * filled + "░" * (length - filled)
    
    # Color the progress bar based on percentage
    if pct >= 90:
        return color(bar, C_RED)
    elif pct >= 75:
        return color(bar, C_YELLOW)
    return color(bar, C_GREEN)

def get_git_info():
    """Resolve active branch and local config email."""
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], 
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except:
        branch = "unknown"
        
    try:
        email = subprocess.check_output(
            ["git", "config", "user.email"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except:
        email = "not set"
        
    return branch, email

def get_active_api_profile():
    """Resolve active API profile name."""
    profile_file = os.path.join(utils.get_agents_dir(), 'active_api_profile_name')
    if os.path.exists(profile_file):
        try:
            with open(profile_file, 'r') as f:
                return f.read().strip()
        except:
            pass
    return "default"

def get_active_locks():
    """Scan and return active lock names."""
    locks_dir = os.path.join(utils.get_agents_dir(), 'locks')
    locks = []
    if os.path.exists(locks_dir):
        for item in os.listdir(locks_dir):
            if item.endswith('.lock'):
                locks.append(item[:-5].replace('_', '/'))
    return sorted(locks)

def run_subcommand(cmd_name, args_list=None):
    """Dynamically import and run a subcommand, trapping SystemExit."""
    if args_list is None:
        args_list = []
    
    cmd_map = {
        "lock": "lock",
        "unlock": "lock",
        "validate": "validate",
        "doctor": "doctor",
        "migrate": "migrate",
        "push": "push",
        "clean": "clean",
        "git-profile": "git_profile",
        "api-profile": "api_profile",
        "log-usage": "log_usage",
        "archive": "archive",
        "recon": "recon",
        "list-skills": "skills",
        "create-skill": "skills",
        "list-rules": "rules",
        "create-rule": "rules",
        "init": "init",
        "commit": "commit",
        "sync-git": "sync_git",
        "build": "build",
        "lint": "lint",
        "test": "test",
        "sync-api": "sync_api",
        "create-adr": "create_adr",
        "adr-wizard": "adr_wizard",
        "release": "release",
        "autocomplete": "autocomplete",
        "guide": "guide"
    }
    
    module_name = cmd_map.get(cmd_name)
    if not module_name:
        print(color(f"Error: Unknown subcommand mapping for '{cmd_name}'", C_RED), file=sys.stderr)
        return False
        
    try:
        # Import the command module dynamically
        cmd_module = __import__(f"commands.{module_name}", fromlist=[module_name])
        # Execute the run function
        cmd_module.run([cmd_name] + args_list)
        return True
    except SystemExit as e:
        if e.code != 0:
            print(color(f"\n[INFO] Command '{cmd_name}' finished with exit code {e.code}", C_YELLOW))
            return False
        return True
    except Exception as e:
        print(color(f"\n[ERROR] Failed to execute '{cmd_name}': {e}", C_RED), file=sys.stderr)
        return False

def show_git_profile_menu():
    """Interactive selector for git profiles."""
    profiles_file = ""
    agents_profiles = os.path.join(utils.get_agents_dir(), 'git_profiles')
    home_profiles = os.path.expanduser('~/.git_profiles')
    
    if os.path.exists(agents_profiles):
        profiles_file = agents_profiles
    elif os.path.exists(home_profiles):
        profiles_file = home_profiles
        
    config = {}
    if os.path.exists(profiles_file):
        with open(profiles_file, 'r') as f:
            for line in f:
                if line.strip() and not line.strip().startswith('#') and '=' in line:
                    parts = line.strip().split('=', 1)
                    config[parts[0].strip()] = parts[1].strip()
                    
    keys = sorted(list(set(k.split('.')[0] for k in config.keys() if k.endswith('.name'))))
    
    print(color("\n--- 👥 Git Identity Profiles ---", C_BOLD + C_CYAN))
    for i, k in enumerate(keys):
        p_n = config[f"{k}.name"]
        p_e = config.get(f"{k}.email", "")
        print(f"  [{color(str(i+1), C_GREEN)}] Switch to {color(k, C_BOLD)}: \"{p_n}\" <{p_e}>")
    
    offset = len(keys)
    print(f"  [{color(str(offset+1), C_GREEN)}] Rotate Profiles (round-robin)")
    print(f"  [{color(str(offset+2), C_GREEN)}] Manually enter new Name & Email")
    print(f"  [{color('0', C_YELLOW)}] Cancel")
    
    try:
        val = input(color("\nSelect choice: ", C_BOLD)).strip()
        if not val or val == "0":
            return
            
        choice = int(val)
        if 1 <= choice <= len(keys):
            selected_profile = keys[choice - 1]
            run_subcommand("git-profile", [selected_profile])
        elif choice == offset + 1:
            run_subcommand("git-profile", ["rotate"])
        elif choice == offset + 2:
            name = input("Enter git user.name: ").strip()
            email = input("Enter git user.email: ").strip()
            if name and email:
                run_subcommand("git-profile", [name, email])
            else:
                print(color("Error: name and email cannot be empty.", C_RED))
    except ValueError:
        print(color("Invalid choice.", C_RED))
    except KeyboardInterrupt:
        print("\nCancelled.")

def show_api_profile_menu():
    """Interactive selector for API key profiles."""
    api_keys_file = ""
    agents_keys = os.path.join(utils.get_agents_dir(), 'api_keys')
    home_keys = os.path.expanduser('~/.antigravity_api_keys')
    if os.path.exists(agents_keys):
        api_keys_file = agents_keys
    elif os.path.exists(home_keys):
        api_keys_file = home_keys
        
    config = {}
    if os.path.exists(api_keys_file):
        with open(api_keys_file, 'r') as f:
            for line in f:
                if line.strip() and not line.strip().startswith('#') and '=' in line:
                    parts = line.strip().split('=', 1)
                    config[parts[0].strip()] = parts[1].strip()
                    
    profiles_list = sorted(list(set(k.split('.')[0] for k in config.keys() if '.' in k)))
    
    print(color("\n--- 🔑 API Provider Key Profiles ---", C_BOLD + C_CYAN))
    for i, p in enumerate(profiles_list):
        keys = [k.split('.', 1)[1] for k in config.keys() if k.startswith(f"{p}.")]
        print(f"  [{color(str(i+1), C_GREEN)}] Switch to {color(p, C_BOLD)} ({', '.join(keys)})")
        
    offset = len(profiles_list)
    print(f"  [{color(str(offset+1), C_GREEN)}] Rotate Active API Profiles")
    print(f"  [{color('0', C_YELLOW)}] Cancel")
    
    try:
        val = input(color("\nSelect choice: ", C_BOLD)).strip()
        if not val or val == "0":
            return
            
        choice = int(val)
        if 1 <= choice <= len(profiles_list):
            selected_profile = profiles_list[choice - 1]
            run_subcommand("api-profile", [selected_profile])
        elif choice == offset + 1:
            run_subcommand("api-profile", ["rotate"])
    except ValueError:
        print(color("Invalid choice.", C_RED))
    except KeyboardInterrupt:
        print("\nCancelled.")

def run(args):
    """Main interactive menu loop."""
    while True:
        branch, email = get_git_info()
        api_profile = get_active_api_profile()
        locks = get_active_locks()
        
        # Load token budget statistics
        budget = utils.load_budget()
        global_usage = budget.get("current_token_usage", 0)
        global_limit = budget.get("max_token_budget", 500000)
        pct = (global_usage / global_limit) * 100 if global_limit > 0 else 0
        bar = get_progress_bar(pct, length=12)
        
        # Draw Beautiful Card Header
        print("\n" + color("+" + "="*58 + "+", C_BLUE))
        print(color("|", C_BLUE) + color(f"   🚀  ANTIGRAVITY AGENT WORKSPACE CONTROL PANEL   ", C_BOLD + C_HEADER) + " "*7 + color("|", C_BLUE))
        print(color("+" + "="*58 + "+", C_BLUE))
        
        branch_colored = color(branch, C_GREEN if branch != "unknown" else C_GRAY)
        email_colored = color(email, C_CYAN if email != "not set" else C_GRAY)
        api_profile_colored = color(api_profile, C_GREEN)
        
        if locks:
            locks_colored = color(f"⚠️  Locked: {', '.join(locks)}", C_YELLOW)
        else:
            locks_colored = color("🔓 Open", C_GREEN)
            
        print(f"  Branch:      {branch_colored:<25} |  API Profile:  {api_profile_colored}")
        print(f"  Git Email:   {email_colored:<25} |  Locks:        {locks_colored}")
        print(f"  Token Limit: {global_usage:,} / {global_limit:,} tokens [{bar}] {pct:.1f}%")
        print(color("+" + "-"*58 + "+", C_BLUE))
        
        print(color("\n  --- 🛠️  DAILY DEVELOPMENT ---", C_BOLD + C_BLUE))
        print(f"  [{color('1', C_GREEN)}] 🔒 Lock a folder for editing (prevent parallel edits)")
        print(f"  [{color('2', C_GREEN)}] 🔓 Unlock a folder (make it available again)")
        print(f"  [{color('3', C_GREEN)}] 💾 Save & Commit changes (auto-rotates Git profiles + checks)")
        print(f"  [{color('4', C_GREEN)}] 🚀 Push to Git Repository (runs security checks + pushes)")
        
        print(color("\n  --- 🩺 DIAGNOSTICS & SECURITY ---", C_BOLD + C_BLUE))
        print(f"  [{color('5', C_GREEN)}] 🩺 Run Doctor Health diagnostics (checks hooks & permissions)")
        print(f"  [{color('6', C_GREEN)}] 🛡️  Validate Compliance (scan for secrets, budget & rules)")
        
        print(color("\n  --- ⚙️  CONFIGURATIONS & PROFILES ---", C_BOLD + C_BLUE))
        print(f"  [{color('7', C_GREEN)}] 👤 Switch/Rotate local Git identity profiles")
        print(f"  [{color('8', C_GREEN)}] 🔑 Switch/Rotate API key credentials profiles")
        print(f"  [{color('9', C_GREEN)}] 📝 Run guided ADR Wizard (document architectural decisions)")
        
        print(color("\n  --- 📚 UTILITIES & HELP ---", C_BOLD + C_BLUE))
        print(f"  [{color('10', C_GREEN)}] 📖 View Step-by-Step Onboarding Tutorial")
        print(f"  [{color('11', C_GREEN)}] 🧹 Clean Workspace (prepare repo for a clean public clone)")
        print(f"  [{color('12', C_GREEN)}] 📦 Archive sprint checkpoints (prevents memory merge conflicts)")
        print(f"  [{color('13', C_GREEN)}] 🔍 Scan codebase tech-stack topology")
        
        print(color(f"\n  [{color('0', C_YELLOW)}] Exit Dashboard", C_BOLD))
        print(color("+" + "="*58 + "+", C_BLUE))
        
        try:
            choice = input(color("Select choice [0-13]: ", C_BOLD)).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break
            
        if choice == "0":
            print("Goodbye!")
            break
        elif choice == "1":
            module = input("\nEnter folder/module name to lock (e.g. core, auth, apps/backend) or [0] to cancel: ").strip()
            if module and module != "0":
                run_subcommand("lock", [module])
        elif choice == "2":
            active_locks = get_active_locks()
            if not active_locks:
                print(color("\n[INFO] No active locks found.", C_CYAN))
                input("\nPress Enter to continue...")
                continue
                
            print(color("\n--- Active Module Locks ---", C_BOLD + C_CYAN))
            for i, lock in enumerate(active_locks):
                print(f"  [{color(str(i+1), C_GREEN)}] Unlock '{color(lock, C_BOLD)}'")
            print(f"  [{color('0', C_YELLOW)}] Cancel")
            
            try:
                sel = input(color("\nSelect lock to release: ", C_BOLD)).strip()
                if sel and sel != "0":
                    idx = int(sel) - 1
                    if 0 <= idx < len(active_locks):
                        run_subcommand("unlock", [active_locks[idx]])
            except ValueError:
                print(color("Invalid choice.", C_RED))
        elif choice == "3":
            run_subcommand("commit")
        elif choice == "4":
            print(color("\n--- Secure Push Actions ---", C_BOLD + C_CYAN))
            print(f"  [{color('1', C_GREEN)}] Standard push (runs validation, rotates SSH key) [Recommended]")
            print(f"  [{color('2', C_GREEN)}] Force push (--force)")
            print(f"  [{color('3', C_GREEN)}] Skip validation checks (--no-validate)")
            print(f"  [{color('0', C_YELLOW)}] Cancel")
            push_sel = input(color("\nSelect push action: ", C_BOLD)).strip()
            if push_sel == "1":
                run_subcommand("push")
            elif push_sel == "2":
                run_subcommand("push", ["--force"])
            elif push_sel == "3":
                run_subcommand("push", ["--no-validate"])
        elif choice == "5":
            run_subcommand("doctor")
            input("\nPress Enter to return to menu...")
        elif choice == "6":
            run_subcommand("validate")
            input("\nPress Enter to return to menu...")
        elif choice == "7":
            show_git_profile_menu()
        elif choice == "8":
            show_api_profile_menu()
        elif choice == "9":
            run_subcommand("adr-wizard")
        elif choice == "10":
            run_subcommand("guide")
            input("\nPress Enter to return to menu...")
        elif choice == "11":
            print(color("\n⚠️  WARNING: Workspace Clean-up", C_YELLOW + C_BOLD))
            print("This will delete active lock files, sprint archives, and reset")
            print("token budgets and active API configuration keys.")
            confirm = input(color("Are you sure you want to clean the workspace? (y/N): ", C_BOLD)).strip().lower()
            if confirm in ("y", "yes"):
                run_subcommand("clean")
                input("\nPress Enter to return to menu...")
        elif choice == "12":
            run_subcommand("archive")
            input("\nPress Enter to return to menu...")
        elif choice == "13":
            run_subcommand("recon")
            input("\nPress Enter to return to menu...")
        else:
            print(color("Invalid selection. Please enter a number from 0 to 13.", C_RED))
            
        print("\n" + color("-" * 60, C_BLUE))

EOF

# Write .agents/scripts/cli/commands/commit.py
write_template_safe ".agents/scripts/cli/commands/commit.py" << 'EOF'
import os
import sys
import subprocess
import re
import utils

def run(args):
    no_test_flag = False
    stage_files = []
    commit_type = ""
    scope = ""
    desc = ""
    
    # Parse arguments
    idx = 1
    while idx < len(args):
        arg = args[idx]
        if arg in ("--no-test", "--no-verify"):
            no_test_flag = True
            idx += 1
        elif arg == "commit":
            idx += 1
        elif not commit_type:
            commit_type = arg
            idx += 1
        elif not scope:
            scope = arg
            idx += 1
        elif not desc:
            desc = arg
            idx += 1
        else:
            stage_files.append(arg)
            idx += 1
            
    # Interactive inputs
    if not commit_type:
        print("Choose commit type:")
        print("  [1] feat:     A new feature")
        print("  [2] fix:      A bug fix")
        print("  [3] refactor: A code change that neither fixes a bug nor adds a feature")
        print("  [4] chore:    Changes to the build process or auxiliary tools and libraries")
        print("  [5] docs:     Documentation only changes")
        print("  [6] test:     Adding missing tests or correcting existing tests")
        print("  [7] perf:     A code change that improves performance")
        try:
            type_choice = input("Select number or type string (default: feat): ").strip()
        except KeyboardInterrupt:
            print("\nCancelled.")
            sys.exit(1)
            
        mapping = {
            "1": "feat", "2": "fix", "3": "refactor", "4": "chore",
            "5": "docs", "6": "test", "7": "perf", "": "feat"
        }
        commit_type = mapping.get(type_choice, type_choice)
        
    if not scope:
        try:
            scope = input("Enter commit scope (e.g. core, auth, db, shared) (default: core): ").strip()
        except KeyboardInterrupt:
            print("\nCancelled.")
            sys.exit(1)
        if not scope:
            scope = "core"
            
    if not desc:
        try:
            desc = input("Enter brief description of change: ").strip()
        except KeyboardInterrupt:
            print("\nCancelled.")
            sys.exit(1)
        if not desc:
            print("Error: Description cannot be empty.", file=sys.stderr)
            sys.exit(1)
            
    # Workspace Validation
    print("Running workspace validation checks...")
    validate_sh = os.path.join(utils.get_agents_dir(), "scripts", "validate.sh")
    if os.path.exists(validate_sh):
        proc = subprocess.run([validate_sh])
        if proc.returncode != 0:
            print("Error: Workspace validation failed. Aborting commit.", file=sys.stderr)
            sys.exit(1)
            
    # Linter and Test commands from project_rules.md
    linter_cmd = ""
    test_runner = ""
    rules_file = os.path.join(utils.get_agents_dir(), "rules", "project_rules.md")
    if os.path.exists(rules_file):
        try:
            with open(rules_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if "Linter command" in line:
                        m = re.search(r"`([^`]+)`", line)
                        if m: linter_cmd = m.group(1)
                    elif "Test runner command" in line:
                        m = re.search(r"`([^`]+)`", line)
                        if m: test_runner = m.group(1)
        except Exception as e:
            print(f"Warning: Failed to read project rules for lint/test commands: {e}", file=sys.stderr)
            
    if not no_test_flag:
        if linter_cmd and linter_cmd != "echo 'No linter found'":
            print(f"Running linter command: {linter_cmd}...")
            proc = subprocess.run(linter_cmd, shell=True)
            if proc.returncode != 0:
                print("Error: Linter check failed. Aborting commit.", file=sys.stderr)
                sys.exit(1)
            print("  [PASS] Linter check passed successfully.")
            
        if test_runner and test_runner != "echo 'No test suite found'":
            print(f"Running test suite: {test_runner}...")
            proc = subprocess.run(test_runner, shell=True)
            if proc.returncode != 0:
                print("Error: Test runner suite failed. Aborting commit.", file=sys.stderr)
                sys.exit(1)
            print("  [PASS] All tests passed successfully.")
    else:
        print("Linter and Test checks bypassed via --no-test / --no-verify.")
        
    # File Staging
    if stage_files:
        print(f"Staging specified files: {' '.join(stage_files)}...")
        subprocess.run(["git", "add"] + stage_files)
    else:
        print("Staging all modified and untracked files...")
        status = subprocess.check_output(["git", "status", "--porcelain"]).decode()
        # filter out lock files
        has_changes = False
        for line in status.splitlines():
            if not line.strip().endswith(".lock") or ".agents/locks/" not in line:
                has_changes = True
                break
        if has_changes:
            subprocess.run(["git", "add", "-A", "--", ":!.agents/locks/*"])
            
    # Auto-rotate profiles
    profiles_file = ""
    local_pf = os.path.join(utils.get_agents_dir(), "git_profiles")
    home_pf = os.path.expanduser("~/.git_profiles")
    if os.path.exists(local_pf):
        profiles_file = local_pf
    elif os.path.exists(home_pf):
        profiles_file = home_pf
        
    if profiles_file:
        profiles = {}
        try:
            with open(profiles_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line_strip = line.strip()
                    m = re.match(r"^([a-zA-Z0-9_\-]+)\.(name|email|ssh_key)\s*=\s*(.+)$", line_strip)
                    if m:
                        prof_key = m.group(1)
                        field = m.group(2)
                        val = m.group(3).strip('\'"')
                        profiles.setdefault(prof_key, {})[field] = val
        except Exception as e:
            print(f"Warning: Failed to parse Git profiles: {e}", file=sys.stderr)
            
        profile_keys = sorted(list(profiles.keys()))
        if profile_keys:
            try:
                last_email = subprocess.check_output(
                    ["git", "log", "-n", 1, "--format=%ae"], 
                    stderr=subprocess.DEVNULL
                ).decode().strip()
            except:
                last_email = ""
                
            selected_idx = 0
            for i, pk in enumerate(profile_keys):
                if profiles[pk].get("email") == last_email:
                    selected_idx = (i + 1) % len(profile_keys)
                    break
                    
            selected_profile = profile_keys[selected_idx]
            p_name = profiles[selected_profile].get("name")
            p_email = profiles[selected_profile].get("email")
            p_ssh = profiles[selected_profile].get("ssh_key", "")
            
            if not p_name or not p_email:
                print(f"Error: Profile '{selected_profile}' is misconfigured in {profiles_file}.", file=sys.stderr)
                sys.exit(1)
                
            print(f"Auto-selecting Git profile: '{selected_profile}' (\"{p_name}\" <{p_email}>) for round-robin commit rotation.")
            subprocess.run(["git", "config", "--local", "user.name", p_name])
            subprocess.run(["git", "config", "--local", "user.email", p_email])
            
            if p_ssh:
                p_ssh_expanded = os.path.expanduser(p_ssh)
                if os.path.exists(p_ssh_expanded):
                    print(f"Auto-selecting SSH key: '{p_ssh}' for profile '{selected_profile}'.")
                    subprocess.run(["git", "config", "--local", "core.sshCommand", f"ssh -i \"{p_ssh_expanded}\" -o IdentitiesOnly=yes"])
                else:
                    print(f"Warning: SSH key file at '{p_ssh}' specified for profile '{selected_profile}' does not exist. Bypassing SSH setup.", file=sys.stderr)
                    subprocess.run(["git", "config", "--local", "--unset", "core.sshCommand"])
            else:
                subprocess.run(["git", "config", "--local", "--unset", "core.sshCommand"])
        else:
            print(f"Error: Git profiles file found at {profiles_file} but no valid profiles were parsed.", file=sys.stderr)
            sys.exit(1)
    else:
        # Fallbacks
        try:
            active_name = subprocess.check_output(["git", "config", "user.name"]).decode().strip()
        except:
            active_name = ""
        try:
            active_email = subprocess.check_output(["git", "config", "user.email"]).decode().strip()
        except:
            active_email = ""
            
        if not active_name or not active_email:
            print("Warning: No Git profiles config found (.agents/git_profiles) and no default Git identity (user.name/user.email) is configured.", file=sys.stderr)
            print("  [FALLBACK] Configuring temporary local-only identity: \"Local Developer\" <local-dev@localhost>", file=sys.stderr)
            subprocess.run(["git", "config", "--local", "user.name", "Local Developer"])
            subprocess.run(["git", "config", "--local", "user.email", "local-dev@localhost"])
            subprocess.run(["git", "config", "--local", "--unset", "core.sshCommand"])
        else:
            if re.match(r"^[a-zA-Z0-9_\.-]+@(company\.com|gmail\.com|example\.com)$", active_email) and re.match(r"^(Developer|Test|Alice|Bob).*", active_name):
                print("Warning: Active Git configuration appears to be using a template or placeholder:", file=sys.stderr)
                print(f"  Name:  {active_name}", file=sys.stderr)
                print(f"  Email: {active_email}", file=sys.stderr)
                print("  Please update your credentials or set up '.agents/git_profiles' for enterprise-grade compliance.", file=sys.stderr)
            print(f"[INFO] Auto-rotation bypassed (no profiles config). Using active Git identity: \"{active_name}\" <{active_email}>")

    # Conventional Commit
    commit_msg = f"{commit_type}({scope}): {desc}"
    print(f"Executing conventional commit: '{commit_msg}'...")
    proc = subprocess.run(["git", "commit", "-m", commit_msg])
    if proc.returncode == 0:
        print("Commit successful.")
    else:
        print("Error: Git commit failed.", file=sys.stderr)
        sys.exit(1)

EOF

# Write .agents/scripts/cli/commands/sync_api.py
write_template_safe ".agents/scripts/cli/commands/sync_api.py" << 'EOF'
import os
import sys
import subprocess
import utils
import re

def run(args):
    print("==========================================================")
    print("Starting API Contract Synchronization...")
    print("==========================================================")
    
    subprojects_file = os.path.join(utils.get_agents_dir(), "subprojects.sh")
    be_path = ""
    fe_path = ""
    be_stack = ""
    
    if os.path.exists(subprojects_file):
        try:
            with open(subprojects_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except:
            lines = []
            
        for line in lines:
            line_strip = line.strip()
            if '|' in line_strip:
                clean_line = re.sub(r'^[A-Z_a-z0-9\+]+=\s*\(?\s*', '', line_strip).strip(') \'"')
                parts = clean_line.split('|')
                if len(parts) >= 2:
                    path = parts[0]
                    stack = parts[1]
                    if any(x in path or x in stack for x in ("api", "backend", "Go", "Python")):
                        be_path = path
                        be_stack = stack
                    elif any(x in path or x in stack for x in ("web", "frontend", "Next.js")):
                        fe_path = path
    else:
        # Fallbacks
        if os.path.isdir("apps/backend"): be_path = "apps/backend"
        if os.path.isdir("apps/frontend"): fe_path = "apps/frontend"
        if os.path.isdir("apps/api"): be_path = "apps/api"
        if os.path.isdir("apps/web"): fe_path = "apps/web"
        
    if not be_path:
        if os.path.isfile("go.mod") or os.path.isfile("main.go"):
            be_path = "."
            be_stack = "Go"
        elif os.path.isfile("requirements.txt") or os.path.isfile("pyproject.toml"):
            be_path = "."
            be_stack = "Python"
            
    if not fe_path:
        if os.path.isdir("src/app") or os.path.isfile("package.json"):
            fe_path = "."
            
    if not be_path:
        print("  [INFO] Backend application path could not be auto-detected. Operating in root fallback mode.")
        be_path = "."
        be_stack = "Unknown"
        
    print(f"  Detected Backend: {be_path} ({be_stack})")
    if fe_path:
        print(f"  Detected Frontend: {fe_path}")
        
    openapi_file = "openapi.json"
    print("  Extracting OpenAPI contract schema...")
    
    extracted = False
    
    # Python
    if "Python" in be_stack or os.path.isfile(os.path.join(be_path, "requirements.txt")) or os.path.isfile(os.path.join(be_path, "pyproject.toml")):
        cmd1 = f"python3 -c \"import json; from src.app.main import app; print(json.dumps(app.openapi()))\" > {openapi_file}"
        cmd2 = f"python3 -c \"import json; from app.main import app; print(json.dumps(app.openapi()))\" > {openapi_file}"
        
        cwd = None if be_path == "." else be_path
        target_path = openapi_file if be_path == "." else os.path.join("..", "..", "..", openapi_file)
        
        cmd1_run = f"python3 -c \"import json; from src.app.main import app; print(json.dumps(app.openapi()))\" > {target_path}"
        cmd2_run = f"python3 -c \"import json; from app.main import app; print(json.dumps(app.openapi()))\" > {target_path}"
        
        proc = subprocess.run(cmd1_run, shell=True, cwd=cwd, stderr=subprocess.DEVNULL)
        if proc.returncode == 0:
            extracted = True
        else:
            proc = subprocess.run(cmd2_run, shell=True, cwd=cwd, stderr=subprocess.DEVNULL)
            if proc.returncode == 0:
                extracted = True
                
    # Go
    elif "Go" in be_stack or os.path.isfile(os.path.join(be_path, "go.mod")):
        # check if swag command exists
        try:
            subprocess.run(["swag", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            swag_exists = True
        except:
            swag_exists = False
            
        if swag_exists:
            print(f"  Running swag init in {be_path}...")
            cwd = None if be_path == "." else be_path
            # try different main locations
            proc1 = subprocess.run("swag init -g src/cmd/server/main.go -o . --ot json", shell=True, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if proc1.returncode == 0:
                shutil_copy = True
            else:
                proc2 = subprocess.run("swag init -g cmd/server/main.go -o . --ot json", shell=True, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                shutil_copy = proc2.returncode == 0
                
            if shutil_copy:
                src_swagger = os.path.join(be_path, "swagger.json")
                if os.path.exists(src_swagger):
                    import shutil
                    shutil.copy(src_swagger, openapi_file)
                    extracted = True
                    
    if not extracted or not os.path.exists(openapi_file) or os.path.getsize(openapi_file) == 0:
        print("  Warning: Schema extraction returned empty. Writing a compliant mock/fallback openapi.json...")
        mock_content = """{
  "openapi": "3.0.0",
  "info": {
    "title": "Antigravity Mock API",
    "version": "1.0.0"
  },
  "servers": [
    {
      "url": "http://localhost:3000"
    }
  ],
  "paths": {
    "/api/users": {
      "get": {
        "operationId": "get_users",
        "responses": {
          "200": {
            "description": "Success",
            "content": {
              "application/json": {
                "schema": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/User"
                  }
                }
              }
            }
          }
        }
      },
      "post": {
        "operationId": "create_user",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/User"
              }
            }
          }
        },
        "responses": {
          "201": {
            "description": "Created",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/User"
                }
              }
            }
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "User": {
        "type": "object",
        "required": ["id", "name"],
        "properties": {
          "id": {
            "type": "integer"
          },
          "name": {
            "type": "string"
          },
          "email": {
            "type": "string"
          }
        }
      }
    }
  }
}
"""
        with open(openapi_file, 'w', encoding='utf-8') as f:
            f.write(mock_content)
            
    # Generate client
    if fe_path and os.path.isdir(fe_path):
        target_client = os.path.join(fe_path, "src", "lib", "api-client.ts")
        if fe_path == "." and os.path.isdir("src/app"):
            target_client = os.path.join("src", "lib", "api-client.ts")
            
        print(f"  Generating TypeScript client wrapper to {target_client}...")
        client_js = os.path.join(utils.get_agents_dir(), "scripts", "generate-client.js")
        proc = subprocess.run(["node", client_js, openapi_file, target_client])
        sys.exit(proc.returncode)
    else:
        print("  Frontend directory not detected. Generated openapi.json is saved in root.")
        sys.exit(0)

EOF

# Write .agents/scripts/cli/commands/autocomplete.py
write_template_safe ".agents/scripts/cli/commands/autocomplete.py" << 'EOF'
import sys

def get_bash_completion():
    return """_helper_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    opts="lock unlock validate doctor migrate git-profile api-profile log-usage archive recon list-skills create-skill list-rules create-rule init commit sync-git build lint test sync-api create-adr release"

    if [[ ${cur} == * ]] ; then
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi
}
complete -F _helper_completion helper.sh
complete -F _helper_completion ./.agents/scripts/helper.sh
"""

def get_zsh_completion():
    return """#compdef helper.sh ./.agents/scripts/helper.sh

_helper_completion() {
    local -a commands
    commands=(
        'lock:Acquire a module edit lock'
        'unlock:Release a module edit lock'
        'validate:Validate workspace compliance, budget, and configurations'
        'doctor:Run complete diagnostic validation on the workspace'
        'migrate:Upgrade workspaces to V1.9.0 format'
        'git-profile:Switch Git user config profiles locally'
        'api-profile:Switch API configurations locally'
        'log-usage:Log token usage to budget tracker'
        'archive:Archive completed sprint checklists to history'
        'recon:Run autonomous codebase stack discovery'
        'list-skills:List all registered modular skills'
        'create-skill:Scaffold a new skill structure'
        'list-rules:List all project-specific blueprints and rules'
        'create-rule:Scaffold a new project rule blueprint'
        'init:Initialize a new workspace with template blueprints'
        'commit:Execute conventional commit and verification checks'
        'sync-git:Synchronize local repository configuration with Git'
        'build:Run project build verification'
        'lint:Run project workspace linter'
        'test:Run project unit tests'
        'sync-api:Synchronize API schemas and configurations'
        'create-adr:Create a new Architectural Decision Record'
        'release:Perform a project semantic release bump'
    )
    _describe -t commands 'helper command' commands
}

_helper_completion "$@"
"""

def run(args):
    if len(args) < 2:
        print("Usage: helper.sh autocomplete [bash|zsh]")
        print("To load autocomplete, run:")
        print("  source <(./.agents/scripts/helper.sh autocomplete bash)")
        sys.exit(1)
        
    shell = args[1].lower()
    if shell == "bash":
        print(get_bash_completion())
    elif shell == "zsh":
        print(get_zsh_completion())
    else:
        print(f"Unsupported shell: {shell}. Only 'bash' and 'zsh' are supported.", file=sys.stderr)
        sys.exit(1)

EOF

# Write .agents/scripts/cli/commands/migrate.py
write_template_safe ".agents/scripts/cli/commands/migrate.py" << 'EOF'
import os
import sys
import shutil
import subprocess
import utils

def run(args):
    utils.print_title("Antigravity Agent Core - Workspace Migration (V1.9.0)")
    
    backup_suffix = ".backup"
    agents_dir = utils.get_agents_dir()
    
    # 1. Back up files if they exist
    memory_file = utils.get_memory_file()
    if os.path.exists(memory_file):
        print(f"Warning: Existing memory file found. Backing up to {memory_file}{backup_suffix}")
        shutil.copy(memory_file, memory_file + backup_suffix)
        
    project_rules = os.path.join(agents_dir, 'rules', 'project_rules.md')
    if os.path.exists(project_rules):
        print(f"Warning: Existing project rules blueprint found. Backing up to {project_rules}{backup_suffix}")
        shutil.copy(project_rules, project_rules + backup_suffix)
        
    schema_index = os.path.join(agents_dir, 'schema.md')
    if os.path.exists(schema_index):
        print(f"Warning: Existing schema index found. Backing up to {schema_index}{backup_suffix}")
        shutil.copy(schema_index, schema_index + backup_suffix)
        
    # 2. Re-create directory structure
    print("Re-creating directory structure...")
    skills = ['codebase-recon', 'git-ops', 'test-driven-patch', 'infra-provisioner', 'security-ci-audit', 'code-review', 'impact-analysis']
    for s in skills:
        os.makedirs(os.path.join(agents_dir, 'skills', s), exist_ok=True)
        
    os.makedirs(os.path.join(agents_dir, 'workflows'), exist_ok=True)
    os.makedirs(os.path.join(agents_dir, 'archive'), exist_ok=True)
    os.makedirs(os.path.join(agents_dir, 'locks'), exist_ok=True)
    os.makedirs(os.path.join(agents_dir, 'schemas'), exist_ok=True)
    os.makedirs(os.path.join(agents_dir, 'scripts'), exist_ok=True)
    os.makedirs(os.path.join(agents_dir, 'hooks'), exist_ok=True)
    os.makedirs(os.path.join(agents_dir, 'rules'), exist_ok=True)
    
    # 3. Update Git Hooks with custom backup checks
    print("Updating local Git hooks...")
    hooks = ['pre-commit', 'post-commit', 'commit-msg']
    for h in hooks:
        src_hook = os.path.join(agents_dir, 'hooks', h)
        dest_hook = os.path.join('.git', 'hooks', h)
        if os.path.exists(src_hook):
            # Check if custom hooks exist and backup if not ours
            if os.path.exists(dest_hook):
                is_ours = False
                try:
                    with open(dest_hook, 'r') as f:
                        if "Antigravity Agent Git Hook" in f.read():
                            is_ours = True
                except: pass
                
                if not is_ours:
                    print(f"  - Backing up existing custom {h} hook")
                    shutil.move(dest_hook, dest_hook + ".backup")
                    
            shutil.copy(src_hook, dest_hook)
            try:
                os.chmod(dest_hook, 0o755)
            except: pass
            print(f"  - Installed {h} hook")
            
    # 4. Update memory.md schema version
    if os.path.exists(memory_file):
        print("Updating memory ledger schema version to 5.0.0...")
        try:
            with open(memory_file, 'r') as f:
                content = f.read()
            if "Memory Schema Version" in content:
                import re
                content = re.sub(r"Memory Schema Version\*\*: [0-9]+\.[0-9]+\.[0-9]+", "Memory Schema Version**: 5.0.0", content)
            else:
                header = "# Agent Core Memory\n\n> **Memory Schema Version**: 5.0.0  \n> **Target System**: Antigravity Agent Core\n> **Active Guidelines**: Read [AGENTS.md](file://../AGENTS.md) and [.agents/rules/project_rules.md](file://./rules/project_rules.md) for execution details. Keep this file under 100 lines at all times.\n\n"
                # skip first line if it's the title
                lines = content.splitlines()
                if lines and lines[0].startswith("# "):
                    content = header + "\n".join(lines[1:])
                else:
                    content = header + content
            with open(memory_file, 'w') as f:
                f.write(content)
        except Exception as e:
            print(f"Warning: Failed to update memory schema version: {e}", file=sys.stderr)
            
    # 5. Fix .gitignore configuration
    gitignore = ".gitignore"
    if os.path.exists(gitignore):
        print("Validating .gitignore compliance...")
        try:
            with open(gitignore, 'r') as f:
                content = f.read()
            block = """# <<< ANTIGRAVITY AGENT START >>>
# Ignore agent transient locks
.agents/locks/

# Ignore local agent API key configuration and active state files
.agents/api_keys
.agents/active_api_keys
.agents/active_api_keys.ps1
.agents/active_api_profile_name
# <<< ANTIGRAVITY AGENT END >>>"""

            start_guard = '# <<< ANTIGRAVITY AGENT START >>>'
            end_guard = '# <<< ANTIGRAVITY AGENT END >>>'
            
            ignored_patterns = {
                '.agents', '.agents/', 'AGENTS.md', '.agents/locks/', '.agents/locks',
                '.agents/git_profiles', '.agents/api_keys', '.agents/active_api_keys',
                '.agents/active_api_keys.ps1', '.agents/active_api_profile_name'
            }
            
            lines = content.splitlines()
            lines = [l for l in lines if l.strip() not in ignored_patterns]
            content = '\n'.join(lines) + '\n'
            
            if start_guard in content and end_guard in content:
                start_idx = content.find(start_guard)
                end_idx = content.find(end_guard) + len(end_guard)
                new_content = content[:start_idx] + block + content[end_idx:]
            else:
                if not content.endswith('\n'):
                    content += '\n'
                new_content = content + '\n' + block + '\n'
                
            while new_content.endswith('\n\n'):
                new_content = new_content[:-1]
                
            with open(gitignore, 'w') as f:
                f.write(new_content)
            print("  - .gitignore updated with Antigravity Agent block guards.")
        except Exception as e:
            print(f"Warning: Failed to update .gitignore: {e}", file=sys.stderr)
    else:
        print("Creating default compliant .gitignore...")
        try:
            with open(gitignore, 'w') as f:
                f.write("""# <<< ANTIGRAVITY AGENT START >>>
# Ignore agent transient locks
.agents/locks/

# Ignore local agent API key configuration and active state files
.agents/api_keys
.agents/active_api_keys
.agents/active_api_keys.ps1
.agents/active_api_profile_name
# <<< ANTIGRAVITY AGENT END >>>
""")
        except Exception as e:
            print(f"Warning: Failed to create default .gitignore: {e}", file=sys.stderr)
            
    # 6. Re-run stack discovery
    print("Running autonomous stack reconstruction...")
    recon_sh = os.path.join(agents_dir, 'scripts', 'recon.sh')
    if os.path.exists(recon_sh):
        subprocess.run([recon_sh, "-f"])
        
    print("==========================================================")
    print("Migration Complete! Workspace successfully upgraded.")
    print("==========================================================")

EOF

# Write .agents/scripts/cli/commands/__init__.py
write_template_safe ".agents/scripts/cli/commands/__init__.py" << 'EOF'


EOF

# Write .agents/scripts/cli/commands/push.py
write_template_safe ".agents/scripts/cli/commands/push.py" << 'EOF'
import os
import sys
import subprocess
import utils

def run(args):
    # Parse options
    force = False
    no_validate = False
    
    if len(args) > 1:
        if '--help' in args[1:] or '-h' in args[1:]:
            print("==========================================================")
            print("  Antigravity Helper CLI - git push wrapper")
            print("==========================================================")
            print("Usage: helper.sh push [options]")
            print("")
            print("Options:")
            print("  -f, --force         Force push to remote origin")
            print("  -n, --no-validate   Skip workspace validation and Git profile warnings")
            print("  -h, --help          Show this help message")
            sys.exit(0)
            
        for arg in args[1:]:
            if arg in ('--force', '-f'):
                force = True
            elif arg in ('--no-validate', '-n'):
                no_validate = True

    # 1. Run Workspace Validation
    if not no_validate:
        validate_sh = os.path.join(utils.get_agents_dir(), 'scripts', 'validate.sh')
        if os.path.exists(validate_sh):
            print("Running workspace validation...")
            proc = subprocess.run([validate_sh])
            if proc.returncode != 0:
                print("Error: Workspace validation failed. Push aborted.", file=sys.stderr)
                sys.exit(proc.returncode)
        else:
            print(f"Warning: validate.sh not found at {validate_sh}. Skipping validation.", file=sys.stderr)

    # 2. Check Git user profile mapping
    agents_profiles = os.path.join(utils.get_agents_dir(), 'git_profiles')
    home_profiles = os.path.expanduser('~/.git_profiles')
    
    profiles_file = ""
    if os.path.exists(agents_profiles):
        profiles_file = agents_profiles
    elif os.path.exists(home_profiles):
        profiles_file = home_profiles
        
    config = {}
    if profiles_file:
        try:
            with open(profiles_file, 'r') as f:
                for line in f:
                    if line.strip() and not line.strip().startswith('#') and '=' in line:
                        parts = line.strip().split('=', 1)
                        config[parts[0].strip()] = parts[1].strip()
        except Exception as e:
            print(f"Warning: Failed to read profiles from {profiles_file}: {e}", file=sys.stderr)

    current_email = ""
    try:
        current_email = subprocess.check_output(
            ["git", "config", "user.email"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception as e:
        pass

    matching_profile = None
    ssh_key_path = None

    if config:
        profile_names = sorted(list(set(k.split('.')[0] for k in config.keys() if k.endswith('.name'))))
        for p_name in profile_names:
            p_email = config.get(f"{p_name}.email", "")
            if current_email and p_email == current_email:
                matching_profile = p_name
                p_ssh = config.get(f"{p_name}.ssh_key", "")
                if p_ssh:
                    resolved_ssh = os.path.expanduser(p_ssh)
                    if os.path.exists(resolved_ssh):
                        ssh_key_path = resolved_ssh
                    else:
                        print(f"[WARNING] SSH key file for profile '{p_name}' at '{p_ssh}' was not found.", file=sys.stderr)
                break

    if not no_validate:
        if not profiles_file:
            print("[WARNING] No Git profiles configuration found. Cannot verify user profile alignment.", file=sys.stderr)
        elif not matching_profile:
            print(f"[WARNING] Current Git user email '{current_email}' does not match any profile in {profiles_file}.", file=sys.stderr)
        else:
            print(f"[INFO] Active Git profile matched: '{matching_profile}'")

    # 3. Detect current branch
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], 
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception as e:
        print(f"Error: Failed to resolve current Git branch: {e}", file=sys.stderr)
        sys.exit(1)

    if not branch or branch == "HEAD":
        print("Error: Cannot push in detached HEAD state.", file=sys.stderr)
        sys.exit(1)

    # 4. Prepare and run git push
    cmd = ["git", "push", "origin", branch]
    if force:
        cmd.append("--force")

    env = os.environ.copy()
    if ssh_key_path:
        env["GIT_SSH_COMMAND"] = f"ssh -i \"{ssh_key_path}\" -o IdentitiesOnly=yes"
        print(f"[INFO] Using SSH key rotation: '{ssh_key_path}'")

    print(f"Running: {' '.join(cmd)}")
    proc = subprocess.run(cmd, env=env)
    sys.exit(proc.returncode)

EOF

# Write .agents/scripts/cli/commands/skills.py
write_template_safe ".agents/scripts/cli/commands/skills.py" << 'EOF'
import os
import sys
import re
import utils

def run(args):
    if len(args) == 0:
        print("Usage: helper.py <command> [arguments...]", file=sys.stderr)
        sys.exit(1)
        
    command = args[0]
    
    if command == "create-skill":
        create_skill(args)
    elif command == "list-skills":
        list_skills(args)
    else:
        print(f"Unknown skills command: {command}", file=sys.stderr)
        sys.exit(1)

def create_skill(args):
    if len(args) < 2:
        print("Usage: helper.py create-skill <name> [description]", file=sys.stderr)
        sys.exit(1)
        
    name = args[1]
    desc = args[2] if len(args) > 2 else ""
    
    if not re.match(r"^[a-z0-9-]+$", name):
        print("Error: Skill name must be lowercase kebab-case (e.g., custom-skill-name).", file=sys.stderr)
        sys.exit(1)
        
    workspace_root = utils.find_workspace_root()
    skill_dir = os.path.join(workspace_root, ".agents", "skills", name)
    
    if os.path.exists(skill_dir):
        print(f"Error: Skill '{name}' already exists at {skill_dir}.", file=sys.stderr)
        sys.exit(1)
        
    os.makedirs(os.path.join(skill_dir, "scripts"), exist_ok=True)
    
    skill_md_content = f"""---
name: {name}
description: {desc if desc else f"Specialized skill for {name} automation."}
scripts:
  - scripts/main.py
---

# {name} Skill

## 1. Input Specification
- Specify required inputs (e.g., target file paths, options).

## 2. Operational Procedures
1. Run the associated script.
2. Verify results.

## 3. Decision Matrix
- If the script returns success (exit code 0), the action is accepted.
- If the script returns error, it fails.

## 4. Error Mitigation Tree
- Retry execution.
- If it fails, report details back to the user.

## 5. Output Verification Gate
- [ ] Executable script passes all internal checks.
"""

    script_content = f"""#!/usr/bin/env python3
import argparse
import sys
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_skill(args):
    \"\"\"
    Main logic of the skill script.
    \"\"\"
    logging.info(f"Running skill with arguments: {{args}}")
    # Implement operational logic here
    
    result = {{
        "status": "success",
        "message": "Skill {name} executed successfully",
        "data": {{}}
    }}
    return result

def main():
    parser = argparse.ArgumentParser(description="Default Python script for agent skill {name}.")
    parser.add_argument('--target', type=str, help="Target path or resource")
    parser.add_argument('--debug', action='store_true', help="Enable debug mode")
    
    args = parser.parse_args()
    
    try:
        output = run_skill(args)
        print(json.dumps(output, indent=2))
        sys.exit(0)
    except Exception as e:
        logging.error(f"Execution failed: {{str(e)}}")
        error_output = {{
            "status": "error",
            "message": str(e)
        }}
        print(json.dumps(error_output, indent=2))
        sys.exit(1)

if __name__ == '__main__':
    main()
"""

    skill_md_path = os.path.join(skill_dir, "SKILL.md")
    script_path = os.path.join(skill_dir, "scripts", "main.py")
    
    with open(skill_md_path, 'w', encoding='utf-8') as f:
        f.write(skill_md_content)
        
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
        
    os.chmod(script_path, 0o755)
    
    # Scaffold skeleton unit test for the skill
    tests_dir = os.path.join(workspace_root, "tests")
    os.makedirs(tests_dir, exist_ok=True)
    name_with_underscores = name.replace("-", "_")
    test_file_path = os.path.join(tests_dir, f"test_skill_{name_with_underscores}.py")
    
    camel_name = "".join(part.capitalize() for part in name.split("-"))
    test_content = f"""import unittest
import subprocess
import os

class TestSkill{camel_name}(unittest.TestCase):
    def test_help_execution(self):
        \"\"\"Verify that the skill script can be executed with --help.\"\"\"
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            ".agents", "skills", "{name}", "scripts", "main.py"
        )
        self.assertTrue(os.path.exists(script_path), f"Script not found at {{script_path}}")
        
        proc = subprocess.run([script_path, "--help"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("Default Python script for agent skill {name}", proc.stdout)

if __name__ == '__main__':
    unittest.main()
"""
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write(test_content)
        
    print(f"Skill '{name}' created successfully at {skill_dir}")
    print(f"Skeleton unit test scaffolded at {test_file_path}")

def audit_skill(skill_dir):
    skill_name = os.path.basename(skill_dir)
    skill_md = os.path.join(skill_dir, "SKILL.md")
    
    # Check 1: SKILL.md exists
    if not os.path.isfile(skill_md):
        return False, f"{skill_name} is missing SKILL.md"
        
    # Check 2: Parse YAML frontmatter
    try:
        with open(skill_md, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return False, f"failed to read SKILL.md: {e}"
        
    if not lines or lines[0].strip() != "---":
        return False, f"{skill_name} SKILL.md does not start with YAML frontmatter delimiter (---)"
        
    closing_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            closing_idx = i
            break
            
    if closing_idx == -1:
        return False, f"{skill_name} SKILL.md has unclosed YAML frontmatter"
        
    frontmatter_lines = lines[1:closing_idx]
    frontmatter_text = "".join(frontmatter_lines)
    
    # Parse fields
    parsed_name = None
    parsed_desc = None
    for line in frontmatter_lines:
        line_strip = line.strip()
        if line_strip.startswith("name:"):
            parsed_name = line_strip[len("name:"):].strip().strip("'\"")
        elif line_strip.startswith("description:"):
            parsed_desc = line_strip[len("description:"):].strip().strip("'\"")
            
    if not parsed_name:
        return False, f"{skill_name} frontmatter missing 'name'"
    if not parsed_desc:
        return False, f"{skill_name} frontmatter missing 'description'"
        
    # Check 3: Check for placeholders in SKILL.md
    try:
        with open(skill_md, 'r', encoding='utf-8') as f:
            full_content = f.read()
    except Exception as e:
        return False, f"failed to read SKILL.md content: {e}"
        
    if re.search(r"TODO|FIXME|\[placeholder\]", full_content, re.IGNORECASE):
        return False, f"{skill_name} SKILL.md contains placeholder text (TODO/FIXME/placeholder)"
        
    # Check 4: Verify referenced scripts
    in_scripts = False
    script_paths = []
    for line in frontmatter_lines:
        line_strip = line.strip()
        if line_strip.startswith("scripts:"):
            in_scripts = True
            continue
        elif in_scripts and ":" in line_strip and not line_strip.startswith("-"):
            in_scripts = False
            
        if in_scripts:
            if line_strip.startswith("-"):
                script_path_val = line_strip[1:].strip().strip("'\"")
                if script_path_val:
                    script_paths.append(script_path_val)
                    
    for s_path in script_paths:
        full_script_path = os.path.join(skill_dir, s_path)
        if not os.path.isfile(full_script_path):
            return False, f"{skill_name} referenced script {s_path} does not exist"
        if not os.access(full_script_path, os.X_OK):
            return False, f"{skill_name} referenced script {s_path} is not executable (missing chmod +x)"
            
    # Check the scripts directory files if scripts dir exists
    scripts_dir = os.path.join(skill_dir, "scripts")
    if os.path.isdir(scripts_dir):
        for entry in os.listdir(scripts_dir):
            entry_path = os.path.join(scripts_dir, entry)
            if os.path.isfile(entry_path):
                if not os.access(entry_path, os.X_OK):
                    return False, f"{skill_name} script {entry} is not executable"
                try:
                    with open(entry_path, 'r', encoding='utf-8', errors='ignore') as f:
                        script_code = f.read()
                except Exception as e:
                    return False, f"failed to read script {entry}: {e}"
                if re.search(r"TODO|FIXME|\[placeholder\]", script_code, re.IGNORECASE):
                    return False, f"{skill_name} script {entry} contains placeholder text (TODO/FIXME/placeholder)"
                    
    return True, parsed_desc

def list_skills(args):
    skills_dir = os.path.join(utils.get_agents_dir(), "skills")
    if not os.path.isdir(skills_dir):
        print(f"Error: Skills directory {skills_dir} not found.", file=sys.stderr)
        sys.exit(1)
        
    print("==========================================================")
    print("          Antigravity Agent Skills Audit & Registry")
    print("==========================================================")
    
    audit_failed = 0
    print(f"{'Skill Name':<25} | {'Status':<12} | Description")
    print("----------------------------------------------------------")
    
    entries = sorted(os.listdir(skills_dir))
    for entry in entries:
        dir_path = os.path.join(skills_dir, entry)
        if os.path.isdir(dir_path):
            passed, detail = audit_skill(dir_path)
            status = "[PASS]" if passed else "[FAIL]"
            if not passed:
                audit_failed += 1
            print(f"{entry:<25} | {status:<12} | {detail}")
            
    print("==========================================================")
    if audit_failed == 0:
        print("All skills are compliant and ready for use.")
        sys.exit(0)
    else:
        print(f"Audit failed! Found {audit_failed} non-compliant skill(s).", file=sys.stderr)
        sys.exit(1)

EOF

# Write .agents/scripts/cli/commands/archive.py
write_template_safe ".agents/scripts/cli/commands/archive.py" << 'EOF'
import os
import sys
import subprocess
import shutil
import utils

def run(args):
    memory_file = utils.get_memory_file()
    if not os.path.exists(memory_file):
        print(f"Error: Memory file {memory_file} not found.", file=sys.stderr)
        sys.exit(1)
        
    archive_dir = os.path.join(utils.get_agents_dir(), 'archive')
    os.makedirs(archive_dir, exist_ok=True)
    
    # Get git branch
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], 
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except:
        branch = "detached"
        
    branch_clean = branch.replace('/', '_')
    archive_file = os.path.join(archive_dir, f"sprint_{branch_clean}.md")
    
    print(f"Archiving tasks to {archive_file}...")
    
    # Read memory.md
    with open(memory_file, 'r') as f:
        lines = f.readlines()
        
    checklist_lines = []
    in_checklist = False
    
    # Extract the checklist
    for line in lines:
        if "### Sprint Tasks Checklist" in line:
            in_checklist = True
            checklist_lines.append(line)
            continue
        if in_checklist:
            if line.strip() == "---" or line.startswith("## "):
                in_checklist = False
            else:
                checklist_lines.append(line)
                
    # Save/append the checklist to the archive file
    if checklist_lines:
        mode = 'a' if os.path.exists(archive_file) else 'w'
        with open(archive_file, mode) as f:
            f.write("".join(checklist_lines))
            f.write("\n")
            
    # Relocate workflow and PR files
    branch_archive_dir = os.path.join(archive_dir, f"sprint_{branch_clean}")
    os.makedirs(branch_archive_dir, exist_ok=True)
    
    workflows_dir = os.path.join(utils.get_agents_dir(), 'workflows')
    print(f"Archiving workflow and PR review files to {branch_archive_dir}...")
    
    if os.path.exists(workflows_dir):
        for item in os.listdir(workflows_dir):
            item_path = os.path.join(workflows_dir, item)
            # Match task_* or pr_review_* files
            if os.path.isfile(item_path) and (item.startswith("task_") or item.startswith("pr_review_")):
                shutil.move(item_path, os.path.join(branch_archive_dir, item))
                
    # Reset checklist in memory.md
    new_lines = []
    skip = False
    for line in lines:
        if "### Sprint Tasks Checklist" in line:
            new_lines.append(line)
            new_lines.append("- [ ] Implement core logic\n")
            new_lines.append("- [ ] Write unit tests\n")
            new_lines.append("- [ ] Verify build and tests pass\n")
            skip = True
            continue
        if skip:
            if line.strip() == "---":
                skip = False
                new_lines.append(line)
            continue
        new_lines.append(line)
        
    with open(memory_file, 'w') as f:
        f.writelines(new_lines)
        
    print("Checklist reset successfully.")

EOF

# Write .agents/scripts/cli/commands/doctor.py
write_template_safe ".agents/scripts/cli/commands/doctor.py" << 'EOF'
import os
import sys
import subprocess
import utils

# ANSI color codes
C_GREEN = '\033[92m'
C_YELLOW = '\033[93m'
C_RED = '\033[91m'
C_BOLD = '\033[1m'
C_END = '\033[0m'

def color(text, ansi_code):
    if sys.stdout.isatty():
        return f"{ansi_code}{text}{C_END}"
    return text

def run(args):
    utils.print_title("Antigravity Workspace Doctor Diagnostics")
    
    errors = 0
    
    # Check Git Repository
    if os.path.isdir('.git'):
        print(f"  {color('[PASS]', C_GREEN + C_BOLD)} Git repository initialized.")
    else:
        print(f"  {color('[FAIL]', C_RED + C_BOLD)} Git repository not initialized!")
        errors += 1
        
    def check_hook(hook_name):
        hook_path = os.path.join('.git', 'hooks', hook_name)
        if os.path.isfile(hook_path) and os.access(hook_path, os.X_OK):
            print(f"  {color('[PASS]', C_GREEN + C_BOLD)} {hook_name} Git hook is installed and executable.")
        else:
            print(f"  {color('[WARNING]', C_YELLOW + C_BOLD)} Git {hook_name} hook is missing or not executable.")
            print(f"            To install: cp .agents/hooks/{hook_name} .git/hooks/{hook_name} && chmod +x .git/hooks/{hook_name}")
            
    check_hook("pre-commit")
    check_hook("post-commit")
    check_hook("commit-msg")
    
    def check_script(script_name):
        nonlocal errors
        script_path = os.path.join(utils.get_agents_dir(), 'scripts', script_name)
        if os.path.exists(script_path):
            if os.access(script_path, os.X_OK):
                print(f"  {color('[PASS]', C_GREEN + C_BOLD)} {script_name} is executable.")
            else:
                print(f"  {color('[WARNING]', C_YELLOW + C_BOLD)} {script_name} is not executable. Auto-correcting...")
                try:
                    os.chmod(script_path, 0o755)
                except Exception as e:
                    print(f"            Failed to set executable permission: {e}", file=sys.stderr)
        else:
            print(f"  {color('[FAIL]', C_RED + C_BOLD)} {script_name} is missing!")
            errors += 1
            
    check_script("helper.sh")
    check_script("recon.sh")
    check_script("validate.sh")
    
    validate_sh = os.path.join(utils.get_agents_dir(), 'scripts', 'validate.sh')
    if os.path.exists(validate_sh):
        print("----------------------------------------------------------")
        proc = subprocess.run([validate_sh])
        if proc.returncode != 0:
            errors += 1
            
    print("==========================================================")
    if errors == 0:
        print(color("Doctor diagnostics: ALL SYSTEMS HEALTHY", C_GREEN + C_BOLD))
        sys.exit(0)
    else:
        print(color(f"Doctor diagnostics: FOUND {errors} ERROR(S) / WARNING(S)", C_YELLOW + C_BOLD))
        sys.exit(1)

EOF

# Write .agents/scripts/cli/commands/lock.py
write_template_safe ".agents/scripts/cli/commands/lock.py" << 'EOF'
import os
import sys
import subprocess
from datetime import datetime
import utils

def run(args):
    command = args[0]
    
    if len(args) < 2:
        print(f"Error: Please specify a module name to {command}.", file=sys.stderr)
        sys.exit(1)
        
    module = args[1]
    # Replace slashes with underscores for nested monorepo paths
    lock_name = module.replace('/', '_')
    locks_dir = os.path.join(utils.get_agents_dir(), 'locks')
    os.makedirs(locks_dir, exist_ok=True)
    lockfile = os.path.join(locks_dir, f"{lock_name}.lock")
    
    if command == "lock":
        if os.path.exists(lockfile):
            print(f"Error: Module '{module}' is already locked!", file=sys.stderr)
            with open(lockfile, 'r') as f:
                print(f.read(), file=sys.stderr)
            sys.exit(1)
            
        # Get git branch
        try:
            branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], 
                stderr=subprocess.DEVNULL
            ).decode().strip()
        except:
            branch = "detached"
            
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        with open(lockfile, 'w') as f:
            f.write(f"Branch: {branch}\n")
            f.write(f"Owner: Agent\n")
            f.write(f"Timestamp: {timestamp}\n")
            
        print(f"Acquired lock for module '{module}' at {lockfile}")
        
    elif command == "unlock":
        if os.path.exists(lockfile):
            os.remove(lockfile)
            print(f"Released lock for module '{module}'")
        else:
            print(f"Warning: No active lock found for module '{module}'")

EOF

# Write .agents/scripts/cli/commands/log_usage.py
write_template_safe ".agents/scripts/cli/commands/log_usage.py" << 'EOF'
import sys
import utils

def run(args):
    if len(args) < 2:
        print("Usage: helper.py log-usage <token_count>", file=sys.stderr)
        sys.exit(1)
        
    try:
        tokens = int(args[1])
    except ValueError:
        print("Error: Token count must be an integer.", file=sys.stderr)
        sys.exit(1)
        
    utils.log_token_usage(tokens)

EOF

# Write .agents/scripts/cli/commands/lint.py
write_template_safe ".agents/scripts/cli/commands/lint.py" << 'EOF'
import os
import sys
import subprocess
import utils
import re

def run(args):
    subprojects_file = os.path.join(utils.get_agents_dir(), "subprojects.sh")
    if os.path.exists(subprojects_file):
        try:
            with open(subprojects_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading {subprojects_file}: {e}", file=sys.stderr)
            sys.exit(1)
            
        try:
            changed_files = subprocess.check_output(
                ["git", "diff", "--cached", "--name-only"], 
                stderr=subprocess.DEVNULL
            ).decode().strip()
        except:
            changed_files = ""
            
        run_all = 0
        if not changed_files:
            run_all = 1
            print("No staged changes detected. Running linter on all monorepo modules...")
        else:
            print("Analyzing staged file boundaries for monorepo-aware linting...")
            
        failed = 0
        for line in lines:
            line_strip = line.strip()
            if '|' in line_strip:
                clean_line = re.sub(r'^[A-Z_a-z0-9\+]+=\s*\(?\s*', '', line_strip).strip(') \'"')
                parts = clean_line.split('|')
                if len(parts) >= 5:
                    path = parts[0]
                    lint_cmd = parts[4]
                    
                    should_run = run_all
                    if should_run == 0:
                        # check if any changed file starts with path/
                        if any(f.startswith(f"{path}/") for f in changed_files.splitlines()):
                            should_run = 1
                            
                    if should_run == 1:
                        print(f"  Linting {path} ({lint_cmd})...")
                        proc = subprocess.run(lint_cmd, shell=True, cwd=path)
                        if proc.returncode != 0:
                            print(f"  [FAIL] Linter errors found in {path}", file=sys.stderr)
                            failed = 1
                    else:
                        print(f"  Skipping {path} (no staged modifications).")
        sys.exit(failed)
    else:
        rules_file = os.path.join(utils.get_agents_dir(), "rules", "project_rules.md")
        if not os.path.exists(rules_file):
            print("No project rules found.", file=sys.stderr)
            sys.exit(0)
            
        linter_cmd = None
        try:
            with open(rules_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if "Linter command" in line:
                        m = re.search(r"`([^`]+)`", line)
                        if m:
                            linter_cmd = m.group(1)
                            break
        except Exception as e:
            print(f"Error reading project rules: {e}", file=sys.stderr)
            sys.exit(1)
            
        if linter_cmd and linter_cmd != "echo 'No linter found'":
            print(f"Running linter command: {linter_cmd}...")
            proc = subprocess.run(linter_cmd, shell=True)
            sys.exit(proc.returncode)
        else:
            print("No linter configuration found.")
            sys.exit(0)

EOF

# Write .agents/scripts/cli/commands/sync_git.py
write_template_safe ".agents/scripts/cli/commands/sync_git.py" << 'EOF'
import os
import sys
import subprocess
import utils
import re

def run(args):
    memory_file = utils.get_memory_file()
    if not os.path.exists(memory_file):
        print(f"Error: Memory file {memory_file} not found.", file=sys.stderr)
        sys.exit(1)
        
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], 
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except:
        branch = "detached"
        
    try:
        commit = subprocess.check_output(
            ["git", "log", "-n", "1", "--format=%h"], 
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except:
        commit = "none"
        
    with open(memory_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    content = re.sub(r"- \*\*Active Branch\*\*: .*", f"- **Active Branch**: {branch}", content)
    content = re.sub(r"- \*\*Last Commit Reference\*\*: .*", f"- **Last Commit Reference**: {commit}", content)
    
    with open(memory_file, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Synchronized: Branch={branch}, Commit={commit} in {memory_file}")

EOF

# Write .agents/scripts/cli/commands/test.py
write_template_safe ".agents/scripts/cli/commands/test.py" << 'EOF'
import os
import sys
import subprocess
import utils
import re

def run(args):
    subprojects_file = os.path.join(utils.get_agents_dir(), "subprojects.sh")
    if os.path.exists(subprojects_file):
        try:
            with open(subprojects_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading {subprojects_file}: {e}", file=sys.stderr)
            sys.exit(1)
            
        try:
            changed_files = subprocess.check_output(
                ["git", "diff", "--cached", "--name-only"], 
                stderr=subprocess.DEVNULL
            ).decode().strip()
        except:
            changed_files = ""
            
        run_all = 0
        if not changed_files:
            run_all = 1
            print("No staged changes detected. Running tests on all monorepo modules...")
        else:
            print("Analyzing staged file boundaries for monorepo-aware testing...")
            
        failed = 0
        for line in lines:
            line_strip = line.strip()
            if '|' in line_strip:
                clean_line = re.sub(r'^[A-Z_a-z0-9\+]+=\s*\(?\s*', '', line_strip).strip(') \'"')
                parts = clean_line.split('|')
                if len(parts) >= 4:
                    path = parts[0]
                    test_cmd = parts[3]
                    
                    should_run = run_all
                    if should_run == 0:
                        if any(f.startswith(f"{path}/") for f in changed_files.splitlines()):
                            should_run = 1
                            
                    if should_run == 1:
                        print(f"  Testing {path} ({test_cmd})...")
                        proc = subprocess.run(test_cmd, shell=True, cwd=path)
                        if proc.returncode != 0:
                            print(f"  [FAIL] Testing suite failed in {path}", file=sys.stderr)
                            failed = 1
                    else:
                        print(f"  Skipping {path} (no staged modifications).")
        sys.exit(failed)
    else:
        rules_file = os.path.join(utils.get_agents_dir(), "rules", "project_rules.md")
        if not os.path.exists(rules_file):
            print("No project rules found.", file=sys.stderr)
            sys.exit(0)
            
        test_runner = None
        try:
            with open(rules_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if "Test runner command" in line:
                        m = re.search(r"`([^`]+)`", line)
                        if m:
                            test_runner = m.group(1)
                            break
        except Exception as e:
            print(f"Error reading project rules: {e}", file=sys.stderr)
            sys.exit(1)
            
        if test_runner and test_runner != "echo 'No test suite found'":
            print(f"Running test suite: {test_runner}...")
            proc = subprocess.run(test_runner, shell=True)
            sys.exit(proc.returncode)
        else:
            print("No test runner configuration found.")
            sys.exit(0)

EOF

# Write .agents/scripts/cli/commands/create_adr.py
write_template_safe ".agents/scripts/cli/commands/create_adr.py" << 'EOF'
import os
import sys
import glob
import re
from datetime import datetime
import utils

def run(args):
    if len(args) < 2:
        print("Usage: helper.py create-adr <title> [proposed|accepted|superseded]", file=sys.stderr)
        sys.exit(1)
        
    title = args[1]
    status = args[2].lower() if len(args) > 2 else "proposed"
    
    if status not in ("proposed", "accepted", "superseded"):
        print("Error: Status must be one of: proposed, accepted, superseded", file=sys.stderr)
        sys.exit(1)
        
    status_cap = status.capitalize()
    adrs_dir = os.path.join(utils.get_agents_dir(), "adrs")
    os.makedirs(adrs_dir, exist_ok=True)
    
    # Determine next ADR number
    count = 1
    existing_files = glob.glob(os.path.join(adrs_dir, "[0-9][0-9][0-9]-*.md"))
    count = len(existing_files) + 1
    
    num = f"{count:03d}"
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    filename = os.path.join(adrs_dir, f"{num}-{slug}.md")
    
    adr_date = datetime.now().strftime("%Y-%m-%d")
    
    adr_content = f"""# ADR-{num}: {title}

- **Date**: {adr_date}
- **Status**: {status_cap}

## Context
[Describe the problem context and alternatives]

## Decision
[Describe the decision made]

## Consequences
[Describe the result and impact of this decision]
"""

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(adr_content)
        
    index_file = os.path.join(utils.get_agents_dir(), "adr.md")
    if os.path.isfile(index_file):
        with open(index_file, 'r', encoding='utf-8') as f:
            index_content = f.read()
            
        if "## 1. Architectural Decisions Index" not in index_content:
            if not index_content.endswith('\n'):
                index_content += '\n'
            index_content += "\n## 1. Architectural Decisions Index\n"
            
        if not index_content.endswith('\n'):
            index_content += '\n'
            
        index_content += f"- [ADR-{num}: {title}](file://./adrs/{num}-{slug}.md) - Status: {status_cap}\n"
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_content)
            
    print(f"Created ADR-{num} at {filename} and registered in {index_file}")

EOF

# Write .agents/scripts/cli/commands/rules.py
write_template_safe ".agents/scripts/cli/commands/rules.py" << 'EOF'
import os
import sys
import re
import utils

def run(args):
    if len(args) == 0:
        print("Usage: helper.py <command> [arguments...]", file=sys.stderr)
        sys.exit(1)
        
    command = args[0]
    
    if command == "create-rule":
        create_rule(args)
    elif command == "list-rules":
        list_rules(args)
    else:
        print(f"Unknown rules command: {command}", file=sys.stderr)
        sys.exit(1)

def create_rule(args):
    if len(args) < 3:
        print("Usage: helper.py create-rule <name> <activation> [description_or_pattern]", file=sys.stderr)
        sys.exit(1)
        
    name = args[1]
    activation = args[2]
    param = args[3] if len(args) > 3 else ""
    
    if not re.match(r"^[a-z0-9-]+$", name):
        print("Error: Rule name must be lowercase kebab-case (e.g., custom-rule-name).", file=sys.stderr)
        sys.exit(1)
        
    activation_mode = ""
    if activation == "manual":
        activation_mode = "Manual"
    elif activation == "always-on":
        activation_mode = "Always On"
    elif activation == "model-decision":
        activation_mode = "Model Decision"
    elif activation == "glob":
        activation_mode = "Glob"
    else:
        print(f"Error: Invalid activation mode '{activation}'. Must be: manual, always-on, model-decision, or glob.", file=sys.stderr)
        sys.exit(1)
        
    pattern = ""
    description = ""
    if activation_mode == "Glob":
        if not param:
            print("Error: Glob activation requires a glob pattern parameter (e.g., 'src/**/*.ts').", file=sys.stderr)
            sys.exit(1)
        pattern = param
    elif activation_mode == "Model Decision":
        if not param:
            print("Error: Model Decision activation requires a natural language description parameter.", file=sys.stderr)
            sys.exit(1)
        description = param
        
    workspace_root = utils.find_workspace_root()
    rule_file = os.path.join(workspace_root, ".agents", "rules", f"{name}.md")
    
    if os.path.exists(rule_file):
        print(f"Error: Rule '{name}' already exists at {rule_file}.", file=sys.stderr)
        sys.exit(1)
        
    os.makedirs(os.path.dirname(rule_file), exist_ok=True)
    
    frontmatter_lines = [
        "---",
        f"name: {name}",
        f"activation: {activation_mode}"
    ]
    if pattern:
        frontmatter_lines.append(f'pattern: "{pattern}"')
    if description:
        frontmatter_lines.append(f'description: "{description}"')
    frontmatter_lines.append("---")
    
    rule_content = "\n".join(frontmatter_lines) + f"""

# {name} Workspace Rule

## Guidelines
- Define the coding standard or instructions for this rule here.
- Example: Prefer arrow functions over traditional function syntax.
"""

    with open(rule_file, 'w', encoding='utf-8') as f:
        f.write(rule_content)
        
    print(f"Rule '{name}' created successfully at {rule_file}")

def audit_rule(rule_file):
    rule_name = os.path.splitext(os.path.basename(rule_file))[0]
    
    if not rule_file.endswith(".md"):
        return False, f"{rule_name} is not a markdown file"
        
    try:
        with open(rule_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return False, f"failed to read rule: {e}"
        
    if not lines or lines[0].strip() != "---":
        return False, f"{rule_name} does not start with YAML frontmatter delimiter (---)"
        
    closing_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            closing_idx = i
            break
            
    if closing_idx == -1:
        return False, f"{rule_name} has unclosed YAML frontmatter"
        
    frontmatter_lines = lines[1:closing_idx]
    
    # Parse fields
    parsed_name = None
    parsed_activation = None
    parsed_pattern = None
    parsed_desc = None
    
    for line in frontmatter_lines:
        line_strip = line.strip()
        if line_strip.startswith("name:"):
            parsed_name = line_strip[len("name:"):].strip().strip("'\"")
        elif line_strip.startswith("activation:"):
            parsed_activation = line_strip[len("activation:"):].strip().strip("'\"")
        elif line_strip.startswith("pattern:"):
            parsed_pattern = line_strip[len("pattern:"):].strip().strip("'\"")
        elif line_strip.startswith("description:"):
            parsed_desc = line_strip[len("description:"):].strip().strip("'\"")
            
    if not parsed_name:
        return False, f"{rule_name} frontmatter missing 'name'"
    if not parsed_activation:
        return False, f"{rule_name} frontmatter missing 'activation'"
        
    if parsed_activation in ("Manual", "Always On"):
        pass
    elif parsed_activation == "Glob":
        if not parsed_pattern:
            return False, f"{rule_name} activation is Glob but missing 'pattern'"
    elif parsed_activation == "Model Decision":
        if not parsed_desc:
            return False, f"{rule_name} activation is Model Decision but missing 'description'"
    else:
        return False, f"{rule_name} has invalid activation mode '{parsed_activation}'"
        
    # Check body for placeholders
    try:
        with open(rule_file, 'r', encoding='utf-8') as f:
            full_content = f.read()
    except Exception as e:
        return False, f"failed to read rule content: {e}"
        
    if re.search(r"TODO|FIXME|\[placeholder\]", full_content, re.IGNORECASE):
        return False, f"{rule_name} contains placeholder text (TODO/FIXME/placeholder)"
        
    # Return activation details
    details = parsed_activation
    if parsed_activation == "Glob":
        details = f"Glob ({parsed_pattern})"
    elif parsed_activation == "Model Decision":
        details = f"Model Decision ({parsed_desc})"
        
    return True, details

def list_rules(args):
    rules_dir = os.path.join(utils.get_agents_dir(), "rules")
    if not os.path.isdir(rules_dir):
        print(f"Error: Rules directory {rules_dir} not found.", file=sys.stderr)
        sys.exit(1)
        
    print("==========================================================")
    print("          Antigravity Agent Rules Audit & Registry")
    print("==========================================================")
    
    audit_failed = 0
    print(f"{'Rule Name':<25} | {'Status':<12} | Activation Mode")
    print("----------------------------------------------------------")
    
    file_found = False
    entries = sorted(os.listdir(rules_dir))
    for entry in entries:
        file_path = os.path.join(rules_dir, entry)
        if os.path.isfile(file_path):
            file_found = True
            passed, detail = audit_rule(file_path)
            status = "[PASS]" if passed else "[FAIL]"
            if not passed:
                audit_failed += 1
            print(f"{entry:<25} | {status:<12} | {detail}")
            
    if not file_found:
        print(f"No rules registered in {rules_dir}.")
        
    print("==========================================================")
    if audit_failed == 0:
        print("All rules are compliant and active.")
        sys.exit(0)
    else:
        print(f"Audit failed! Found {audit_failed} non-compliant rule(s).", file=sys.stderr)
        sys.exit(1)

EOF

# Write .agents/scripts/cli/commands/git_profile.py
write_template_safe ".agents/scripts/cli/commands/git_profile.py" << 'EOF'
import os
import sys
import subprocess
import utils

def run(args):
    # args[0] is 'git-profile'
    if not os.path.isdir('.git'):
        print("Error: Not a Git repository.", file=sys.stderr)
        sys.exit(1)
        
    name = ""
    email = ""
    if len(args) > 1:
        name = args[1]
    if len(args) > 2:
        email = args[2]
        
    profiles_file = ""
    agents_profiles = os.path.join(utils.get_agents_dir(), 'git_profiles')
    home_profiles = os.path.expanduser('~/.git_profiles')
    
    if os.path.exists(agents_profiles):
        profiles_file = agents_profiles
    elif os.path.exists(home_profiles):
        profiles_file = home_profiles
        
    # Read profiles config key-values
    config = {}
    if os.path.exists(profiles_file):
        with open(profiles_file, 'r') as f:
            for line in f:
                if line.strip() and not line.strip().startswith('#') and '=' in line:
                    parts = line.strip().split('=', 1)
                    config[parts[0].strip()] = parts[1].strip()
                    
    is_key_rotate = "rotate.name" in config
    
    if (name == "rotate" or name == "--rotate") and not is_key_rotate:
        if os.path.exists(profiles_file):
            keys = sorted(list(set(k.split('.')[0] for k in config.keys() if k.endswith('.name'))))
            if keys:
                try:
                    last_email = subprocess.check_output(
                        ["git", "log", "-n", "1", "--format=%ae"],
                        stderr=subprocess.DEVNULL
                    ).decode().strip()
                except:
                    last_email = ""
                    
                selected_idx = 0
                for i, k in enumerate(keys):
                    p_e = config.get(f"{k}.email", "")
                    if p_e == last_email:
                        selected_idx = (i + 1) % len(keys)
                        break
                name = keys[selected_idx]
                print(f"Rotating local Git profile to: '{name}'...")
            else:
                print(f"Error: No profiles defined in {profiles_file}.", file=sys.stderr)
                sys.exit(1)
        else:
            print("Error: No Git profiles configuration found to rotate.", file=sys.stderr)
            sys.exit(1)
            
    # Check if name is a profile key
    profile_name_key = f"{name}.name"
    if name and not email and os.path.exists(profiles_file) and profile_name_key in config:
        p_n = config[profile_name_key]
        p_e = config.get(f"{name}.email", "")
        p_s = config.get(f"{name}.ssh_key", "")
        
        print(f"Setting local repository Git configuration to profile '{name}'...")
        subprocess.run(["git", "config", "--local", "user.name", p_n], check=True)
        subprocess.run(["git", "config", "--local", "user.email", p_e], check=True)
        
        if p_s:
            resolved_ssh = os.path.expanduser(p_s)
            if os.path.exists(resolved_ssh):
                subprocess.run(["git", "config", "--local", "core.sshCommand", f"ssh -i \"{p_s}\" -o IdentitiesOnly=yes"], check=True)
            else:
                print(f"  [WARNING] SSH key file at '{p_s}' was not found. Bypassing SSH command setup.", file=sys.stderr)
                subprocess.run(["git", "config", "--local", "--unset", "core.sshCommand"], stderr=subprocess.DEVNULL)
        else:
            subprocess.run(["git", "config", "--local", "--unset", "core.sshCommand"], stderr=subprocess.DEVNULL)
            
        print("  [SUCCESS] Local Git profile updated.")
        name = ""
        email = ""
        
    if name and email:
        print("Setting local repository Git configuration...")
        subprocess.run(["git", "config", "--local", "user.name", name], check=True)
        subprocess.run(["git", "config", "--local", "user.email", email], check=True)
        subprocess.run(["git", "config", "--local", "--unset", "core.sshCommand"], stderr=subprocess.DEVNULL)
        print("  [SUCCESS] Local Git profile updated.")
    elif name or email:
        if os.path.exists(profiles_file):
            print(f"Error: Profile '{name}' not found in {profiles_file}.", file=sys.stderr)
        else:
            print("Error: Both name and email are required to set a profile.", file=sys.stderr)
        sys.exit(1)
        
    # Display configuration
    utils.print_title("Current Git User Configuration")
    
    def get_git_config(scope, key):
        try:
            return subprocess.check_output(["git", "config", f"--{scope}", key], stderr=subprocess.DEVNULL).decode().strip()
        except:
            return "<not set>"
            
    print("Local Profile (This Repository):")
    print(f"  user.name:        {get_git_config('local', 'user.name')}")
    print(f"  user.email:       {get_git_config('local', 'user.email')}")
    print(f"  core.sshCommand:  {get_git_config('local', 'core.sshCommand')}")
    print("")
    print("Global Profile (Default):")
    print(f"  user.name:        {get_git_config('global', 'user.name')}")
    print(f"  user.email:       {get_git_config('global', 'user.email')}")
    print(f"  core.sshCommand:  {get_git_config('global', 'core.sshCommand')}")
    print("")
    
    if os.path.exists(profiles_file):
        print(f"Available Profiles (from {profiles_file}):")
        keys = sorted(list(set(k.split('.')[0] for k in config.keys() if k.endswith('.name'))))
        for k in keys:
            p_n = config[f"{k}.name"]
            p_e = config.get(f"{k}.email", "")
            p_s = config.get(f"{k}.ssh_key", "")
            if p_s:
                print(f"  - {k}: \"{p_n}\" <{p_e}> (ssh_key: {p_s})")
            else:
                print(f"  - {k}: \"{p_n}\" <{p_e}>")

EOF

# Write .agents/scripts/cli/commands/adr_wizard.py
write_template_safe ".agents/scripts/cli/commands/adr_wizard.py" << 'EOF'
import os
import sys
import subprocess
import utils

def run(args):
    """
    Delegate command to the adr-wizard skill main script.
    """
    # Find workspace root
    workspace_root = utils.find_workspace_root()
    script_path = os.path.join(
        workspace_root, ".agents", "skills", "adr-wizard", "scripts", "main.py"
    )
    
    if not os.path.exists(script_path):
        print(f"Error: adr-wizard skill main script not found at {script_path}", file=sys.stderr)
        sys.exit(1)
        
    # Forward all CLI arguments passed after 'adr-wizard'
    cmd = [sys.executable, script_path] + args[1:]
    
    # Execute and connect standard streams to allow interactive console prompts
    proc = subprocess.run(cmd, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
    sys.exit(proc.returncode)

EOF

# Write .agents/scripts/cli/commands/validate.py
write_template_safe ".agents/scripts/cli/commands/validate.py" << 'EOF'
import os
import sys
import subprocess
import utils

def run(args):
    validate_sh = os.path.join(utils.get_agents_dir(), 'scripts', 'validate.sh')
    if not os.path.exists(validate_sh):
        print(f"Error: validate.sh not found at {validate_sh}", file=sys.stderr)
        sys.exit(1)
        
    proc = subprocess.run([validate_sh])
    sys.exit(proc.returncode)

EOF

# Write .agents/scripts/cli/commands/release.py
write_template_safe ".agents/scripts/cli/commands/release.py" << 'EOF'
import os
import sys
import re
from datetime import datetime
import utils

def run(args):
    if len(args) < 2:
        print("Usage: helper.py release <major|minor|patch>", file=sys.stderr)
        sys.exit(1)
        
    bump_type = args[1].lower()
    changelog_file = "CHANGELOG.md"
    
    if not os.path.exists(changelog_file):
        print("Error: CHANGELOG.md not found!", file=sys.stderr)
        sys.exit(1)
        
    with open(changelog_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Extract latest version
    m = re.search(r'^##\s+\[([0-9]+\.[0-9]+\.[0-9]+)\]', content, re.MULTILINE)
    if not m:
        print("Error: Could not parse current version from CHANGELOG.md.", file=sys.stderr)
        sys.exit(1)
        
    current_version = m.group(1)
    major, minor, patch = map(int, current_version.split('.'))
    
    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        print(f"Error: Invalid bump type '{bump_type}'. Must be major, minor, or patch.", file=sys.stderr)
        sys.exit(1)
        
    next_version = f"{major}.{minor}.{patch}"
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"Bumping version: {current_version} -> {next_version} ({bump_type})")
    
    # 1. Insert new version section at the top of version list (right before the first ## [version])
    # We find the first line starting with ## [version]
    lines = content.splitlines()
    new_lines = []
    inserted_version = False
    
    for line in lines:
        if line.startswith("## [") and not inserted_version:
            new_lines.append(f"## [{next_version}] - {current_date}")
            new_lines.append("### Added")
            new_lines.append("- ")
            new_lines.append("")
            inserted_version = True
        new_lines.append(line)
        
    # 2. Update version comparison links at the bottom (right before the first link mapping [version]: )
    content = "\n".join(new_lines)
    lines = content.splitlines()
    final_lines = []
    inserted_link = False
    repo_url = "https://github.com/rafaelghif/antigravity-agents"
    
    for line in lines:
        if re.match(r'^\[[0-9]+\.[0-9]+\.[0-9]+\]:', line) and not inserted_link:
            final_lines.append(f"[{next_version}]: {repo_url}/compare/v{current_version}...v{next_version}")
            inserted_link = True
        final_lines.append(line)
        
    new_content = "\n".join(final_lines)
    if not new_content.endswith('\n'):
        new_content += '\n'
        
    with open(changelog_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f"Successfully bumped version to {next_version} and updated CHANGELOG.md.")

EOF

# Write .agents/scripts/cli/commands/build.py
write_template_safe ".agents/scripts/cli/commands/build.py" << 'EOF'
import os
import sys
import subprocess
import utils
import re

def run(args):
    subprojects_file = os.path.join(utils.get_agents_dir(), "subprojects.sh")
    if os.path.exists(subprojects_file):
        print("Monorepo detected. Running build compilation...")
        try:
            with open(subprojects_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading {subprojects_file}: {e}", file=sys.stderr)
            sys.exit(1)
            
        failed = 0
        for line in lines:
            line_strip = line.strip()
            if '|' in line_strip:
                # remove any array syntax like SUBPROJECTS+=(...)
                clean_line = re.sub(r'^[A-Z_a-z0-9\+]+=\s*\(?\s*', '', line_strip).strip(') \'"')
                parts = clean_line.split('|')
                if len(parts) >= 3:
                    path = parts[0]
                    build_cmd = parts[2]
                    print(f"  Building {path} ({build_cmd})...")
                    proc = subprocess.run(build_cmd, shell=True, cwd=path)
                    if proc.returncode != 0:
                        print(f"  [FAIL] Build failed in {path}", file=sys.stderr)
                        failed = 1
        sys.exit(failed)
    else:
        rules_file = os.path.join(utils.get_agents_dir(), "rules", "project_rules.md")
        if not os.path.exists(rules_file):
            print("No project rules found.", file=sys.stderr)
            sys.exit(0)
            
        build_cmd = None
        try:
            with open(rules_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if "Build validation" in line:
                        m = re.search(r"`([^`]+)`", line)
                        if m:
                            build_cmd = m.group(1)
                            break
        except Exception as e:
            print(f"Error reading project rules: {e}", file=sys.stderr)
            sys.exit(1)
            
        if build_cmd and build_cmd != "echo 'No build command needed'":
            print(f"Running build command: {build_cmd}...")
            proc = subprocess.run(build_cmd, shell=True)
            sys.exit(proc.returncode)
        else:
            print("No build configuration found.")
            sys.exit(0)

EOF

# Write .agents/scripts/cli/commands/api_profile.py
write_template_safe ".agents/scripts/cli/commands/api_profile.py" << 'EOF'
import os
import sys
import json
import time
import utils

def run(args):
    # args[0] is 'api-profile'
    target_profile = ""
    if len(args) > 1:
        target_profile = args[1]
        
    api_keys_file = ""
    agents_keys = os.path.join(utils.get_agents_dir(), 'api_keys')
    home_keys = os.path.expanduser('~/.antigravity_api_keys')
    if os.path.exists(agents_keys):
        api_keys_file = agents_keys
    elif os.path.exists(home_keys):
        api_keys_file = home_keys
        
    rate_limited = "--rate-limited" in args
    
    # Parse available profiles prefix (e.g. name.GEMINI_API_KEY=val)
    config = {}
    if os.path.exists(api_keys_file):
        with open(api_keys_file, 'r') as f:
            for line in f:
                if line.strip() and not line.strip().startswith('#') and '=' in line:
                    parts = line.strip().split('=', 1)
                    config[parts[0].strip()] = parts[1].strip()
                    
    profiles_list = sorted(list(set(k.split('.')[0] for k in config.keys() if '.' in k)))
    num_profiles = len(profiles_list)
    
    if target_profile in ("rotate", "--rotate"):
        if not api_keys_file or not os.path.exists(api_keys_file):
            print("Error: No API keys configuration found (.agents/api_keys or ~/.antigravity_api_keys) to rotate.", file=sys.stderr)
            sys.exit(1)
            
        if num_profiles == 0:
            print(f"Error: No API profiles found in {api_keys_file}.", file=sys.stderr)
            sys.exit(1)
            
        current_profile = "none"
        profile_name_file = os.path.join(utils.get_agents_dir(), 'active_api_profile_name')
        if os.path.exists(profile_name_file):
            with open(profile_name_file, 'r') as f:
                current_profile = f.read().strip()
                
        if rate_limited:
            current_time = int(time.time())
            cooldown_sec = int(os.environ.get("API_ROTATION_COOLDOWN_SEC", 60))
            expiry_time = current_time + cooldown_sec
            
            cooldowns_file = os.path.join(utils.get_agents_dir(), 'cooldowns.json')
            
            if current_profile != "none":
                print(f"Putting profile '{current_profile}' on cooldown for {cooldown_sec} seconds...")
                cooldowns = {}
                if os.path.exists(cooldowns_file):
                    try:
                        with open(cooldowns_file, 'r') as f:
                            cooldowns = json.load(f)
                    except: pass
                cooldowns[current_profile] = expiry_time
                with open(cooldowns_file, 'w') as f:
                    json.dump(cooldowns, f, indent=2)
                    
            # Choose next profile that is NOT on cooldown
            cooldowns = {}
            if os.path.exists(cooldowns_file):
                try:
                    with open(cooldowns_file, 'r') as f:
                        cooldowns = json.load(f)
                except: pass
            # Clean expired cooldowns
            cooldowns = {p: exp for p, exp in cooldowns.items() if exp > current_time}
            with open(cooldowns_file, 'w') as f:
                json.dump(cooldowns, f, indent=2)
                
            if current_profile in profiles_list:
                start_idx = profiles_list.index(current_profile)
                ordered_candidates = profiles_list[start_idx+1:] + profiles_list[:start_idx]
            else:
                ordered_candidates = profiles_list
                
            selected = None
            for p in ordered_candidates:
                if p not in cooldowns:
                    selected = p
                    break
                    
            if selected:
                target_profile = selected
                print(f"Rotating active API profile to: '{target_profile}'...")
            else:
                # All profiles in cooldown
                if cooldowns:
                    earliest_profile = min(cooldowns, key=cooldowns.get)
                    earliest_expiry = cooldowns[earliest_profile]
                    
                    now_time = int(time.time())
                    sleep_sec = earliest_expiry - now_time
                    if sleep_sec > 0:
                        print(f"All API profiles are in cooldown! Earliest available is '{earliest_profile}' in {sleep_sec}s.")
                        print(f"Waiting/sleeping for {sleep_sec} seconds before retrying...")
                        for i in range(sleep_sec, 0, -1):
                            sys.stdout.write(f"  Retrying in {i} seconds...\r")
                            sys.stdout.flush()
                            time.sleep(1)
                        print(f"\n  Cooldown finished. Selecting profile '{earliest_profile}'...")
                        
                    # Clear cooldown entry
                    if earliest_profile in cooldowns:
                        del cooldowns[earliest_profile]
                    with open(cooldowns_file, 'w') as f:
                        json.dump(cooldowns, f, indent=2)
                    target_profile = earliest_profile
                else:
                    target_profile = profiles_list[0]
                    print(f"Rotating active API profile to: '{target_profile}'...")
        else:
            # Standard round robin
            selected_idx = 0
            if current_profile in profiles_list:
                selected_idx = (profiles_list.index(current_profile) + 1) % num_profiles
            target_profile = profiles_list[selected_idx]
            print(f"Rotating active API profile to: '{target_profile}'...")
            
    if target_profile and target_profile != "--rate-limited":
        if os.path.exists(api_keys_file):
            # Check if profile exists
            profile_keys = [k for k in config.keys() if k.startswith(f"{target_profile}.")]
            if profile_keys:
                print(f"Setting active API profile to '{target_profile}'...")
                
                active_keys_sh = os.path.join(utils.get_agents_dir(), 'active_api_keys')
                active_keys_ps1 = os.path.join(utils.get_agents_dir(), 'active_api_keys.ps1')
                profile_name_file = os.path.join(utils.get_agents_dir(), 'active_api_profile_name')
                
                # Write bash file
                with open(active_keys_sh, 'w') as f_sh, open(active_keys_ps1, 'w') as f_ps:
                    f_sh.write(f"# Active API keys for profile: {target_profile}\n")
                    f_ps.write(f"# Active API keys for profile: {target_profile}\n")
                    
                    for k in profile_keys:
                        var_name = k.split('.', 1)[1]
                        var_val = config[k]
                        f_sh.write(f"export {var_name}=\"{var_val}\"\n")
                        f_ps.write(f"$env:{var_name} = \"{var_val}\"\n")
                        
                with open(profile_name_file, 'w') as f:
                    f.write(target_profile)
                    
                print("  [SUCCESS] Active API keys updated in .agents/active_api_keys and .agents/active_api_keys.ps1")
            else:
                print(f"Error: Profile '{target_profile}' not found in {api_keys_file}.", file=sys.stderr)
                sys.exit(1)
        else:
            print("Error: API keys file not found.", file=sys.stderr)
            sys.exit(1)
            
    # Display configuration
    utils.print_title("Current API Profile Configuration")
    
    current_profile = "none"
    profile_name_file = os.path.join(utils.get_agents_dir(), 'active_api_profile_name')
    if os.path.exists(profile_name_file):
        with open(profile_name_file, 'r') as f:
            current_profile = f.read().strip()
            
    print(f"Active Profile: {current_profile}")
    print("")
    
    # Mask key values for display
    print("Active Keys (masked for security):")
    for k, v in config.items():
        if k.startswith(f"{current_profile}."):
            var_name = k.split('.', 1)[1]
            masked = v
            if len(v) > 8:
                masked = v[:4] + "****" + v[-4:]
            print(f"  {var_name}: {masked}")
    print("")
    
    if os.path.exists(api_keys_file):
        print(f"Available API Profiles (from {api_keys_file}):")
        for p in profiles_list:
            keys = [k.split('.', 1)[1] for k in config.keys() if k.startswith(f"{p}.")]
            print(f"  - {p} ({' '.join(keys)} )")

EOF

# Write .agents/scripts/cli/commands/init.py
write_template_safe ".agents/scripts/cli/commands/init.py" << 'EOF'
import os
import sys
import shutil
import subprocess
import utils

NEXT_TEMPLATES = {
  "package.json": "{\n  \"name\": \"nextjs-boilerplate\",\n  \"version\": \"1.0.0\",\n  \"private\": true,\n  \"scripts\": {\n    \"dev\": \"next dev\",\n    \"build\": \"next build\",\n    \"start\": \"next start\",\n    \"lint\": \"next lint\",\n    \"test\": \"jest\"\n  },\n  \"dependencies\": {\n    \"next\": \"^14.2.3\",\n    \"react\": \"^18.3.1\",\n    \"react-dom\": \"^18.3.1\"\n  },\n  \"devDependencies\": {\n    \"@types/node\": \"^20.12.12\",\n    \"@types/react\": \"^18.3.3\",\n    \"@types/react-dom\": \"^18.3.0\",\n    \"autoprefixer\": \"^10.4.19\",\n    \"postcss\": \"^8.4.38\",\n    \"tailwindcss\": \"^3.4.3\",\n    \"typescript\": \"^5.4.5\",\n    \"eslint\": \"^8.57.0\",\n    \"eslint-config-next\": \"^14.2.3\",\n    \"jest\": \"^29.7.0\",\n    \"ts-jest\": \"^29.1.4\"\n  }\n}\n",
  "next.config.js": "/** @type {import('next').NextConfig} */\nconst nextConfig = {\n  reactStrictMode: true,\n};\n\nmodule.exports = nextConfig;\n",
  "tailwind.config.js": "/** @type {import('tailwindcss').Config} */\nmodule.exports = {\n  content: [\n    \"./src/app/**/*.{js,ts,jsx,tsx,mdx}\",\n    \"./src/components/**/*.{js,ts,jsx,tsx,mdx}\",\n  ],\n  theme: {\n    extend: {},\n  },\n  plugins: [],\n}\n",
  "postcss.config.js": "module.exports = {\n  plugins: {\n    tailwindcss: {},\n    autoprefixer: {},\n  },\n}\n",
  "tsconfig.json": "{\n  \"compilerOptions\": {\n    \"target\": \"es5\",\n    \"lib\": [\"dom\", \"dom.iterable\", \"esnext\"],\n    \"allowJs\": true,\n    \"skipLibCheck\": true,\n    \"strict\": true,\n    \"noEmit\": true,\n    \"esModuleInterop\": true,\n    \"module\": \"esnext\",\n    \"moduleResolution\": \"bundler\",\n    \"resolveJsonModule\": true,\n    \"isolatedModules\": true,\n    \"jsx\": \"preserve\",\n    \"incremental\": true,\n    \"plugins\": [\n      {\n        \"name\": \"next\"\n      }\n    ],\n    \"paths\": {\n      \"@/*\": [\"./src/*\"]\n    }\n  },\n  \"include\": [\"next-env.d.ts\", \"**/*.ts\", \"**/*.tsx\", \".next/types/**/*.ts\"],\n  \"exclude\": [\"node_modules\"]\n}\n",
  "jest.config.js": "module.exports = {\n  preset: 'ts-jest',\n  testEnvironment: 'node',\n  testMatch: ['**/tests/**/*.test.ts'],\n};\n",
  "src/app/globals.css": "@tailwind base;\n@tailwind components;\n@tailwind utilities;\n\n:root {\n  color-scheme: dark;\n}\n\nbody {\n  margin: 0;\n  padding: 0;\n  background-color: #020617;\n  color: #f8fafc;\n}\n",
  "src/app/layout.tsx": "import React from 'react';\nimport './globals.css';\n\nexport const metadata = {\n  title: 'Antigravity Next.js Boilerplate',\n  description: 'Scaffolded Next.js workspace for AI software agents',\n};\n\nexport default function RootLayout({\n  children,\n}: {\n  children: React.ReactNode;\n}) {\n  return (\n    <html lang=\"en\">\n      <body>{children}</body>\n    </html>\n  );\n}\n",
  "src/app/page.tsx": "import React from 'react';\n\nexport default function Home() {\n  return (\n    <div className=\"min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6 font-sans\">\n      <div className=\"max-w-4xl w-full text-center space-y-8\">\n        <header className=\"space-y-4\">\n          <div className=\"inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-sm font-semibold tracking-wide animate-pulse\">\n            \ud83d\ude80 Antigravity Workspace Active\n          </div>\n          <h1 className=\"text-5xl md:text-6xl font-extrabold tracking-tight bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent\">\n            Antigravity Next.js Boilerplate\n          </h1>\n          <p className=\"text-slate-400 text-lg max-w-2xl mx-auto\">\n            Your production-ready Next.js application, scaffolded and pre-configured for seamless development with AI coding agents.\n          </p>\n        </header>\n\n        <main className=\"grid grid-cols-1 md:grid-cols-3 gap-6 text-left\">\n          <div className=\"bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm hover:border-indigo-500/30 transition-all duration-300\">\n            <h2 className=\"text-xl font-bold text-slate-100 mb-2\">\u26a1 App Router</h2>\n            <p className=\"text-slate-400 text-sm\">\n              Scaffolded with React Server Components, layout sharing, and clean directory structure inside <code className=\"text-indigo-400\">src/app</code>.\n            </p>\n          </div>\n          <div className=\"bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm hover:border-purple-500/30 transition-all duration-300\">\n            <h2 className=\"text-xl font-bold text-slate-100 mb-2\">\ud83c\udfa8 Styling & UI</h2>\n            <p className=\"text-slate-400 text-sm\">\n              Pre-integrated with Tailwind CSS, custom fonts, CSS variables, and modern dark-mode aesthetics ready for immediate extension.\n            </p>\n          </div>\n          <div className=\"bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm hover:border-pink-500/30 transition-all duration-300\">\n            <h2 className=\"text-xl font-bold text-slate-100 mb-2\">\ud83d\udee1\ufe0f AI Agent Guard</h2>\n            <p className=\"text-slate-400 text-sm\">\n              Wrapped inside Antigravity's cognitive alignment gates (automated pre-commit validators, secret scanning, and memory sync).\n            </p>\n          </div>\n        </main>\n\n        <footer className=\"text-slate-500 text-sm border-t border-slate-900 pt-8 mt-12 flex justify-between items-center\">\n          <div> Muhammad Rafael Ghifari &copy; 2026</div>\n          <div className=\"flex gap-4\">\n            <a href=\"https://github.com/rafaelghif/antigravity-agents\" target=\"_blank\" rel=\"noopener noreferrer\" className=\"hover:text-indigo-400 transition-colors\">GitHub Repository</a>\n            <a href=\"/api/health\" className=\"hover:text-indigo-400 transition-colors\">API Health Check</a>\n          </div>\n        </footer>\n      </div>\n    </div>\n  );\n}\n",
  "src/app/api/health/route.ts": "import { NextResponse } from 'next/server';\n\nexport async function GET() {\n  return NextResponse.json({\n    status: 'HEALTHY',\n    timestamp: new Date().toISOString(),\n    system: 'Antigravity Workspace Core',\n  });\n}\n",
  "tests/health.test.ts": "describe('Next.js Boilerplate Test Suite', () => {\n  it('should pass initial unit test check', () => {\n    expect(true).toBe(true);\n  });\n});\n"
}
GOGIN_TEMPLATES = {
  "go.mod": "module project\n\ngo 1.20\n\nrequire (\n\tgithub.com/gin-gonic/gin v1.9.1\n)\n",
  "src/cmd/server/main.go": "package main\n\nimport (\n\t\"fmt\"\n\t\"log\"\n\t\"net/http\"\n\t\"project/src/internal/config\"\n\t\"project/src/internal/controller\"\n\n\t\"github.com/gin-gonic/gin\"\n)\n\nfunc main() {\n\tcfg := config.LoadConfig()\n\n\tif cfg.Env == \"production\" {\n\t\tgin.SetMode(gin.ReleaseMode)\n\t}\n\n\tr := gin.Default()\n\tr.Use(gin.Recovery())\n\n\thealthCtrl := controller.NewHealthController()\n\n\tapi := r.Group(\"/api\")\n\t{\n\t\tapi.GET(\"/health\", healthCtrl.Check)\n\t}\n\n\tr.GET(\"/\", func(c *gin.Context) {\n\t\tc.JSON(http.StatusOK, gin.H{\n\t\t\t\"message\": \"Welcome to Antigravity Go Gin Boilerplate!\",\n\t\t\t\"status\":  \"Active\",\n\t\t})\n\t})\n\n\taddr := fmt.Sprintf(\":%s\", cfg.Port)\n\tlog.Printf(\"Server starting on port %s...\", cfg.Port)\n\tif err := r.Run(addr); err != nil {\n\t\tlog.Fatalf(\"Failed to run server: %v\", err)\n\t}\n}\n",
  "src/internal/config/config.go": "package config\n\nimport \"os\"\n\ntype Config struct {\n\tPort string\n\tEnv  string\n}\n\nfunc LoadConfig() *Config {\n\tport := os.Getenv(\"PORT\")\n\tif port == \"\" {\n\t\tport = \"8080\"\n\t}\n\tenv := os.Getenv(\"ENV\")\n\tif env == \"\" {\n\t\tenv = \"development\"\n\t}\n\treturn &Config{\n\t\tPort: port,\n\t\tEnv:  env,\n\t}\n}\n",
  "src/internal/controller/health_controller.go": "package controller\n\nimport (\n\t\"net/http\"\n\t\"time\"\n\n\t\"github.com/gin-gonic/gin\"\n)\n\ntype HealthController struct{}\n\nfunc NewHealthController() *HealthController {\n\treturn &HealthController{}\n}\n\nfunc (h *HealthController) Check(c *gin.Context) {\n\tc.JSON(http.StatusOK, gin.H{\n\t\t\"status\":    \"HEALTHY\",\n\t\t\"timestamp\": time.Now().Format(time.RFC3339),\n\t\t\"system\":    \"Antigravity Go Gin Core\",\n\t})\n}\n",
  "tests/health_test.go": "package tests\n\nimport (\n\t\"net/http\"\n\t\"net/http/httptest\"\n\t\"project/src/internal/controller\"\n\t\"testing\"\n\n\t\"github.com/gin-gonic/gin\"\n)\n\nfunc TestHealthCheck(t *testing.T) {\n\tgin.SetMode(gin.TestMode)\n\tr := gin.Default()\n\thealthCtrl := controller.NewHealthController()\n\tr.GET(\"/api/health\", healthCtrl.Check)\n\n\tw := httptest.NewRecorder()\n\treq, _ := http.NewRequest(\"GET\", \"/api/health\", nil)\n\tr.ServeHTTP(w, req)\n\n\tif w.Code != http.StatusOK {\n\t\tt.Errorf(\"Expected status code 200, got %d\", w.Code)\n\t}\n}\n",
  "Makefile": ".PHONY: run test build clean\n\nrun:\n\tgo run src/cmd/server/main.go\n\ntest:\n\tgo test -v ./tests/...\n\nbuild:\n\tgo build -o bin/server src/cmd/server/main.go\n\nclean:\n\trm -rf bin/\n"
}
FASTAPI_TEMPLATES = {
  "requirements.txt": "fastapi>=0.110.0\nuvicorn[standard]>=0.28.0\npydantic>=2.6.4\npytest>=8.1.1\nhttpx>=0.27.0\n",
  "pyproject.toml": "[tool.pytest.ini_options]\npythonpath = [\".\"]\ntestpaths = [\"tests\"]\n",
  "src/app/main.py": "import uvicorn\nfrom fastapi import FastAPI\nfrom src.app.core.config import settings\nfrom src.app.api.endpoints import health\n\napp = FastAPI(\n    title=\"Antigravity FastAPI Boilerplate\",\n    description=\"Production-ready FastAPI setup for AI software agents\",\n    version=\"1.0.0\",\n)\n\napp.include_router(health.router, prefix=\"/api\")\n\n@app.get(\"/\")\ndef read_root():\n    return {\n        \"message\": \"Welcome to Antigravity FastAPI Boilerplate!\",\n        \"status\": \"Active\",\n    }\n\nif __name__ == \"__main__\":\n    uvicorn.run(\"src.app.main:app\", host=\"0.0.0.0\", port=settings.PORT, reload=True)\n",
  "src/app/core/config.py": "import os\n\nclass Settings:\n    PORT: int = int(os.getenv(\"PORT\", 8000))\n    ENV: str = os.getenv(\"ENV\", \"development\")\n\nsettings = Settings()\n",
  "src/app/api/endpoints/health.py": "from datetime import datetime\nfrom fastapi import APIRouter\n\nrouter = APIRouter()\n\n@router.get(\"/health\", tags=[\"system\"])\ndef check_health():\n    return {\n        \"status\": \"HEALTHY\",\n        \"timestamp\": datetime.utcnow().isoformat(),\n        \"system\": \"Antigravity FastAPI Core\",\n    }\n",
  "tests/test_health.py": "from fastapi.testclient import TestClient\nfrom src.app.main import app\n\nclient = TestClient(app)\n\ndef test_health_check():\n    response = client.get(\"/api/health\")\n    assert response.status_code == 200\n    data = response.json()\n    assert data[\"status\"] == \"HEALTHY\"\n    assert \"timestamp\" in data\n    assert data[\"system\"] == \"Antigravity FastAPI Core\"\n"
}
MONOREPO_TEMPLATES = {
  "pnpm-workspace.yaml": "packages:\n  - 'apps/*'\n  - 'packages/*'\n",
  "turbo.json": "{\n  \"$schema\": \"https://turbo.build/schema.json\",\n  \"tasks\": {\n    \"build\": {\n      \"dependsOn\": [\"^build\"],\n      \"outputs\": [\".next/**\", \"dist/**\", \"bin/**\"]\n    },\n    \"lint\": {},\n    \"test\": {},\n    \"dev\": {\n      \"cache\": false,\n      \"persistent\": true\n    }\n  }\n}\n",
  "package.json": "{\n  \"name\": \"monorepo-root\",\n  \"version\": \"1.0.0\",\n  \"private\": true,\n  \"scripts\": {\n    \"build\": \"turbo run build\",\n    \"dev\": \"turbo run dev\",\n    \"lint\": \"turbo run lint\",\n    \"test\": \"turbo run test\"\n  },\n  \"devDependencies\": {\n    \"turbo\": \"^2.0.0\"\n  }\n}\n",
  "apps/web/package.json": "{\n  \"name\": \"web\",\n  \"version\": \"1.0.0\",\n  \"private\": true,\n  \"scripts\": {\n    \"dev\": \"next dev\",\n    \"build\": \"next build\",\n    \"start\": \"next start\",\n    \"lint\": \"next lint\",\n    \"test\": \"jest\"\n  },\n  \"dependencies\": {\n    \"next\": \"^14.2.3\",\n    \"react\": \"^18.3.1\",\n    \"react-dom\": \"^18.3.1\",\n    \"@monorepo/shared\": \"workspace:*\"\n  },\n  \"devDependencies\": {\n    \"@types/node\": \"^20.12.12\",\n    \"@types/react\": \"^18.3.3\",\n    \"@types/react-dom\": \"^18.3.0\",\n    \"autoprefixer\": \"^10.4.19\",\n    \"postcss\": \"^8.4.38\",\n    \"tailwindcss\": \"^3.4.3\",\n    \"typescript\": \"^5.4.5\",\n    \"eslint\": \"^8.57.0\",\n    \"eslint-config-next\": \"^14.2.3\",\n    \"jest\": \"^29.7.0\",\n    \"ts-jest\": \"^29.1.4\"\n  }\n}\n",
  "apps/web/next.config.js": "/** @type {import('next').NextConfig} */\nconst nextConfig = {\n  reactStrictMode: true,\n};\nmodule.exports = nextConfig;\n",
  "apps/web/tailwind.config.js": "/** @type {import('tailwindcss').Config} */\nmodule.exports = {\n  content: [\n    \"./src/app/**/*.{js,ts,jsx,tsx,mdx}\",\n    \"./src/components/**/*.{js,ts,jsx,tsx,mdx}\",\n  ],\n  theme: {\n    extend: {},\n  },\n  plugins: [],\n}\n",
  "apps/web/postcss.config.js": "module.exports = {\n  plugins: {\n    tailwindcss: {},\n    autoprefixer: {},\n  },\n}\n",
  "apps/web/tsconfig.json": "{\n  \"compilerOptions\": {\n    \"target\": \"es5\",\n    \"lib\": [\"dom\", \"dom.iterable\", \"esnext\"],\n    \"allowJs\": true,\n    \"skipLibCheck\": true,\n    \"strict\": true,\n    \"noEmit\": true,\n    \"esModuleInterop\": true,\n    \"module\": \"esnext\",\n    \"moduleResolution\": \"bundler\",\n    \"resolveJsonModule\": true,\n    \"isolatedModules\": true,\n    \"jsx\": \"preserve\",\n    \"incremental\": true,\n    \"plugins\": [\n      {\n        \"name\": \"next\"\n      }\n    ],\n    \"paths\": {\n      \"@/*\": [\"./src/*\"]\n    }\n  },\n  \"include\": [\"next-env.d.ts\", \"**/*.ts\", \"**/*.tsx\", \".next/types/**/*.ts\"],\n  \"exclude\": [\"node_modules\"]\n}\n",
  "apps/web/jest.config.js": "module.exports = {\n  preset: 'ts-jest',\n  testEnvironment: 'node',\n  testMatch: ['**/tests/**/*.test.ts'],\n};\n",
  "apps/web/src/app/globals.css": "@tailwind base;\n@tailwind components;\n@tailwind utilities;\n:root {\n  color-scheme: dark;\n}\nbody {\n  margin: 0;\n  padding: 0;\n  background-color: #020617;\n  color: #f8fafc;\n}\n",
  "apps/web/src/app/layout.tsx": "import React from 'react';\nimport './globals.css';\nexport const metadata = {\n  title: 'Antigravity Monorepo Frontend',\n  description: 'Scaffolded Turborepo Frontend Web Application',\n};\nexport default function RootLayout({\n  children,\n}: {\n  children: React.ReactNode;\n}) {\n  return (\n    <html lang=\"en\">\n      <body>{children}</body>\n    </html>\n  );\n}\n",
  "apps/web/src/app/page.tsx": "import React from 'react';\nimport { appName, version } from '@monorepo/shared';\n\nexport default function Home() {\n  return (\n    <div className=\"min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6 font-sans\">\n      <div className=\"max-w-4xl w-full text-center space-y-8\">\n        <header className=\"space-y-4\">\n          <div className=\"inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-sm font-semibold tracking-wide animate-pulse\">\n            \ud83d\ude80 Antigravity Monorepo Active\n          </div>\n          <h1 className=\"text-5xl md:text-6xl font-extrabold tracking-tight bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent\">\n            {appName}\n          </h1>\n          <p className=\"text-slate-400 text-lg max-w-2xl mx-auto\">\n            Monorepo Web Client (v{version}) running alongside an isolated Go Gin backend service.\n          </p>\n        </header>\n        <main className=\"grid grid-cols-1 md:grid-cols-3 gap-6 text-left\">\n          <div className=\"bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm hover:border-indigo-500/30 transition-all duration-300\">\n            <h2 className=\"text-xl font-bold text-slate-100 mb-2\">\u26a1 Next.js</h2>\n            <p className=\"text-slate-400 text-sm\">\n              Frontend web client running Next.js App Router inside <code className=\"text-indigo-400\">apps/web</code>.\n            </p>\n          </div>\n          <div className=\"bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm hover:border-purple-500/30 transition-all duration-300\">\n            <h2 className=\"text-xl font-bold text-slate-100 mb-2\">\ud83d\udc39 Go Gin API</h2>\n            <p className=\"text-slate-400 text-sm\">\n              Isolated REST API backend service with Go Gin inside <code className=\"text-purple-400\">apps/api</code>.\n            </p>\n          </div>\n          <div className=\"bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm hover:border-pink-500/30 transition-all duration-300\">\n            <h2 className=\"text-xl font-bold text-slate-100 mb-2\">\ud83d\udce6 Shared Workspace</h2>\n            <p className=\"text-slate-400 text-sm\">\n              Shared package containing index exports, interfaces, and types inside <code className=\"text-pink-400\">packages/shared</code>.\n            </p>\n          </div>\n        </main>\n      </div>\n    </div>\n  );\n}\n",
  "apps/web/src/app/api/health/route.ts": "import { NextResponse } from 'next/server';\nexport async function GET() {\n  return NextResponse.json({\n    status: 'HEALTHY',\n    timestamp: new Date().toISOString(),\n    system: 'Antigravity Monorepo Frontend',\n  });\n}\n",
  "apps/web/tests/health.test.ts": "describe('Monorepo Web Client Test Suite', () => {\n  it('should pass initial tests', () => {\n    expect(true).toBe(true);\n  });\n});\n",
  "apps/api/go.mod": "module api\n\ngo 1.20\n\nrequire (\n\tgithub.com/gin-gonic/gin v1.9.1\n)\n",
  "apps/api/src/cmd/server/main.go": "package main\nimport (\n\t\"fmt\"\n\t\"log\"\n\t\"net/http\"\n\t\"api/src/internal/config\"\n\t\"api/src/internal/controller\"\n\t\"github.com/gin-gonic/gin\"\n)\nfunc main() {\n\tcfg := config.LoadConfig()\n\tif cfg.Env == \"production\" {\n\t\tgin.SetMode(gin.ReleaseMode)\n\t}\n\tr := gin.Default()\n\tr.Use(gin.Recovery())\n\thealthCtrl := controller.NewHealthController()\n\tapi := r.Group(\"/api\")\n\t{\n\t\tapi.GET(\"/health\", healthCtrl.Check)\n\t}\n\tr.GET(\"/\", func(c *gin.Context) {\n\t\tc.JSON(http.StatusOK, gin.H{\n\t\t\t\"message\": \"Welcome to Antigravity Go Gin Backend in Monorepo!\",\n\t\t\t\"status\":  \"Active\",\n\t\t})\n\t})\n\taddr := fmt.Sprintf(\":%s\", cfg.Port)\n\tlog.Printf(\"Backend starting on port %s...\", cfg.Port)\n\tif err := r.Run(addr); err != nil {\n\t\tlog.Fatalf(\"Failed to run server: %v\", err)\n\t}\n}\n",
  "apps/api/src/internal/config/config.go": "package config\nimport \"os\"\ntype Config struct {\n\tPort string\n\tEnv  string\n}\nfunc LoadConfig() *Config {\n\tport := os.Getenv(\"PORT\")\n\tif port == \"\" {\n\t\tport = \"8080\"\n\t}\n\tenv := os.Getenv(\"ENV\")\n\tif env == \"\" {\n\t\tenv = \"development\"\n\t}\n\treturn &Config{\n\t\tPort: port,\n\t\tEnv:  env,\n\t}\n}\n",
  "apps/api/src/internal/controller/health_controller.go": "package controller\nimport (\n\t\"net/http\"\n\t\"time\"\n\t\"github.com/gin-gonic/gin\"\n)\ntype HealthController struct{}\nfunc NewHealthController() *HealthController {\n\treturn &HealthController{}\n}\nfunc (h *HealthController) Check(c *gin.Context) {\n\tc.JSON(http.StatusOK, gin.H{\n\t\t\"status\":    \"HEALTHY\",\n\t\t\"timestamp\": time.Now().Format(time.RFC3339),\n\t\t\"system\":    \"Antigravity Monorepo Backend API\",\n\t})\n}\n",
  "apps/api/tests/health_test.go": "package tests\nimport (\n\t\"net/http\"\n\t\"net/http/httptest\"\n\t\"api/src/internal/controller\"\n\t\"testing\"\n\t\"github.com/gin-gonic/gin\"\n)\nfunc TestHealthCheck(t *testing.T) {\n\tgin.SetMode(gin.TestMode)\n\tr := gin.Default()\n\thealthCtrl := controller.NewHealthController()\n\tr.GET(\"/api/health\", healthCtrl.Check)\n\tw := httptest.NewRecorder()\n\treq, _ := http.NewRequest(\"GET\", \"/api/health\", nil)\n\tr.ServeHTTP(w, req)\n\tif w.Code != http.StatusOK {\n\t\tt.Errorf(\"Expected status code 200, got %d\", w.Code)\n\t}\n}\n",
  "apps/api/Makefile": ".PHONY: run test build clean\nrun:\n\tgo run src/cmd/server/main.go\ntest:\n\tgo test -v ./tests/...\nbuild:\n\tgo build -o bin/server src/cmd/server/main.go\nclean:\n\trm -rf bin/\n",
  "packages/shared/package.json": "{\n  \"name\": \"@monorepo/shared\",\n  \"version\": \"1.0.0\",\n  \"private\": true,\n  \"main\": \"index.js\",\n  \"types\": \"index.d.ts\"\n}\n",
  "packages/shared/index.js": "module.exports = {\n  appName: \"Antigravity Monorepo\",\n  version: \"1.0.0\"\n};\n",
  "packages/shared/index.d.ts": "export const appName: string;\nexport const version: string;\n"
}
LARAVEL_TEMPLATES = {
  "app/Http/Controllers/Controller.php": "<?php\n\nnamespace App\\Http\\Controllers;\n\nuse Illuminate\\Foundation\\Auth\\Access\\AuthorizesRequests;\nuse Illuminate\\Foundation\\Validation\\ValidatesRequests;\nuse Illuminate\\Routing\\Controller as BaseController;\n\nclass Controller extends BaseController\n{\n    use AuthorizesRequests, ValidatesRequests;\n}\n",
  "app/Models/User.php": "<?php\n\nnamespace App\\Models;\n\nuse Illuminate\\Database\\Eloquent\\Factories\\HasFactory;\nuse Illuminate\\Foundation\\Auth\\User as Authenticatable;\nuse Illuminate\\Notifications\\Notifiable;\nuse Laravel\\Sanctum\\HasApiTokens;\n\nclass User extends Authenticatable\n{\n    use HasApiTokens, HasFactory, Notifiable;\n\n    protected $fillable = [\n        'name',\n        'email',\n        'password',\n    ];\n\n    protected $hidden = [\n        'password',\n        'remember_token',\n    ];\n\n    protected $casts = [\n        'email_verified_at' => 'datetime',\n        'password' => 'hashed',\n    ];\n}\n",
  "composer.json": "{\n    \"name\": \"laravel/laravel\",\n    \"type\": \"project\",\n    \"description\": \"The Laravel Framework.\",\n    \"keywords\": [\"framework\", \"laravel\"],\n    \"license\": \"MIT\",\n    \"require\": {\n        \"php\": \"^8.1\",\n        \"guzzlehttp/guzzle\": \"^7.2\",\n        \"laravel/framework\": \"^10.0\",\n        \"laravel/sanctum\": \"^3.2\",\n        \"laravel/tinker\": \"^2.8\"\n    },\n    \"require-dev\": {\n        \"fakerphp/faker\": \"^1.9.1\",\n        \"laravel/pint\": \"^1.0\",\n        \"laravel/sail\": \"^1.18\",\n        \"mockery/mockery\": \"^1.4.4\",\n        \"nunomaduro/collision\": \"^7.0\",\n        \"phpunit/phpunit\": \"^10.0\",\n        \"spatie/laravel-ignition\": \"^2.0\"\n    },\n    \"autoload\": {\n        \"psr-4\": {\n            \"App\\\\\": \"app/\",\n            \"Database\\\\Factories\\\\\": \"database/factories/\",\n            \"Database\\\\Seeders\\\\\": \"database/seeders/\"\n        }\n    },\n    \"autoload-dev\": {\n        \"psr-4\": {\n            \"Tests\\\\\": \"tests/\"\n        }\n    },\n    \"scripts\": {\n        \"post-autoload-dump\": [\n            \"Illuminate\\\\Foundation\\\\ComposerScripts::postAutoloadDump\",\n            \"@php artisan package:discover --ansi\"\n        ],\n        \"post-update-cmd\": [\n            \"@php artisan vendor:publish --tag=laravel-assets --ansi --force\"\n        ],\n        \"post-root-package-install\": [\n            \"@php -r \\\"file_exists('.env') || copy('.env.example', '.env');\\\"\"\n        ],\n        \"post-create-project-cmd\": [\n            \"@php artisan key:generate --ansi\"\n        ]\n    },\n    \"extra\": {\n        \"laravel\": {\n            \"dont-discover\": []\n        }\n    },\n    \"config\": {\n        \"optimize-autoloader\": true,\n        \"preferred-install\": \"dist\",\n        \"sort-packages\": true,\n        \"allow-plugins\": {\n            \"pestphp/pest-plugin\": true,\n            \"php-http/discovery\": true\n        }\n    },\n    \"minimum-stability\": \"stable\",\n    \"prefer-stable\": true\n}\n",
  "package.json": "{\n    \"private\": true,\n    \"type\": \"module\",\n    \"scripts\": {\n        \"dev\": \"vite\",\n        \"build\": \"vite build\"\n    },\n    \"devDependencies\": {\n        \"axios\": \"^1.1.2\",\n        \"laravel-vite-plugin\": \"^0.7.5\",\n        \"vite\": \"^4.0.0\"\n    }\n}\n",
  ".env.example": "APP_NAME=Laravel\nAPP_ENV=local\nAPP_KEY=\nAPP_DEBUG=true\nAPP_URL=http://localhost\n\nLOG_CHANNEL=stack\nLOG_DEPRECATIONS_CHANNEL=null\nLOG_LEVEL=debug\n\nDB_CONNECTION=mysql\nDB_HOST=127.0.0.1\nDB_PORT=3306\nDB_DATABASE=laravel\nDB_USERNAME=root\nDB_PASSWORD=\n\nBROADCAST_DRIVER=log\nCACHE_DRIVER=file\nFILESYSTEM_DISK=local\nQUEUE_CONNECTION=sync\nSESSION_DRIVER=file\nSESSION_LIFETIME=120\n",
  "artisan": "#!/usr/bin/env php\n<?php\n\ndefine('LARAVEL_START', microtime(true));\n\nif (file_exists($maintenance = __DIR__.'/storage/framework/maintenance.php')) {\n    require $maintenance;\n}\n\nrequire __DIR__.'/vendor/autoload.php';\n\n$app = require_once __DIR__.'/bootstrap/app.php';\n\n$kernel = $app->make(Illuminate\\Contracts\\Console\\Kernel::class);\n\n$status = $kernel->handle(\n    $input = new Symfony\\Component\\Console\\Input\\ArgvInput,\n    new Symfony\\Component\\Console\\Output\\ConsoleOutput\n);\n\n$kernel->terminate($input, $status);\n\nexit($status);\n",
  "bootstrap/app.php": "<?php\n\n$app = new Illuminate\\Foundation\\Application(\n    $_ENV['APP_BASE_PATH'] ?? dirname(__DIR__)\n);\n\n$app->singleton(\n    Illuminate\\Contracts\\Http\\Kernel::class,\n    App\\Http\\Kernel::class\n);\n\n$app->singleton(\n    Illuminate\\Contracts\\Console\\Kernel::class,\n    App\\Http\\Console\\Kernel::class\n);\n\n$app->singleton(\n    Illuminate\\Contracts\\Debug\\ExceptionHandler::class,\n    App\\Exceptions\\Handler::class\n);\n\nreturn $app;\n",
  "app/Http/Kernel.php": "<?php\n\nnamespace App\\Http;\n\nuse Illuminate\\Foundation\\Http\\Kernel as HttpKernel;\n\nclass Kernel extends HttpKernel\n{\n    protected $middleware = [\n        \\Illuminate\\Http\\Middleware\\TrustProxies::class,\n        \\Illuminate\\Http\\Middleware\\HandleCors::class,\n        \\Illuminate\\Foundation\\Http\\Middleware\\PreventRequestsDuringMaintenance::class,\n        \\Illuminate\\Foundation\\Http\\Middleware\\ValidatePostSize::class,\n        \\App\\Http\\Middleware\\TrimStrings::class,\n        \\Illuminate\\Foundation\\Http\\Middleware\\ConvertEmptyStringsToNull::class,\n    ];\n\n    protected $middlewareGroups = [\n        'web' => [\n            \\App\\Http\\Middleware\\EncryptCookies::class,\n            \\Illuminate\\Cookie\\Middleware\\AddQueuedCookiesToResponse::class,\n            \\Illuminate\\Session\\Middleware\\StartSession::class,\n            \\Illuminate\\View\\Middleware\\ShareErrorsFromSession::class,\n            \\App\\Http\\Middleware\\VerifyCsrfToken::class,\n            \\Illuminate\\Routing\\Middleware\\SubstituteBindings::class,\n        ],\n        'api' => [\n            \\Laravel\\Sanctum\\Http\\Middleware\\EnsureFrontendRequestsAreStateful::class,\n            \\Illuminate\\Routing\\Middleware\\ThrottleRequests::class.':api',\n            \\Illuminate\\Routing\\Middleware\\SubstituteBindings::class,\n        ],\n    ];\n\n    protected $middlewareAliases = [\n        'auth' => \\App\\Http\\Middleware\\Authenticate::class,\n        'guest' => \\App\\Http\\Middleware\\RedirectIfAuthenticated::class,\n        'verified' => \\Illuminate\\Auth\\Middleware\\EnsureEmailIsVerified::class,\n    ];\n}\n",
  "app/Console/Kernel.php": "<?php\n\nnamespace App\\Console;\n\nuse Illuminate\\Foundation\\Console\\Kernel as ConsoleKernel;\n\nclass Kernel extends ConsoleKernel\n{\n    protected function commands(): void\n    {\n        $this->load(__DIR__.'/Commands');\n        require base_path('routes/console.php');\n    }\n}\n",
  "app/Exceptions/Handler.php": "<?php\n\nnamespace App\\Exceptions;\n\nuse Illuminate\\Foundation\\Exceptions\\Handler as ExceptionHandler;\nuse Throwable;\n\nclass Handler extends ExceptionHandler\n{\n    protected $dontFlash = [\n        'current_password',\n        'password',\n        'password_confirmation',\n    ];\n\n    public function register(): void\n    {\n        $this->reportable(function (Throwable $e) {\n            //\n        });\n    }\n}\n",
  "app/Http/Middleware/TrimStrings.php": "<?php\nnamespace App\\Http\\Middleware;\nuse Illuminate\\Foundation\\Http\\Middleware\\TrimStrings as Middleware;\nclass TrimStrings extends Middleware {}\n",
  "app/Http/Middleware/EncryptCookies.php": "<?php\nnamespace App\\Http\\Middleware;\nuse Illuminate\\Cookie\\Middleware\\EncryptCookies as Middleware;\nclass EncryptCookies extends Middleware {}\n",
  "app/Http/Middleware/VerifyCsrfToken.php": "<?php\nnamespace App\\Http\\Middleware;\nuse Illuminate\\Foundation\\Http\\Middleware\\VerifyCsrfToken as Middleware;\nclass VerifyCsrfToken extends Middleware {}\n",
  "app/Http/Middleware/Authenticate.php": "<?php\nnamespace App\\Http\\Middleware;\nuse Illuminate\\Auth\\Middleware\\Authenticate as Middleware;\nuse Illuminate\\Http\\Request;\nclass Authenticate extends Middleware {\n    protected function redirectTo(Request $request): ?string {\n        return $request->expectsJson() ? null : route('login');\n    }\n}\n",
  "app/Http/Middleware/RedirectIfAuthenticated.php": "<?php\nnamespace App\\Http\\Middleware;\nuse App\\Providers\\RouteServiceProvider;\nuse Closure;\nuse Illuminate\\Http\\Request;\nuse Illuminate\\Support\\Facades\\Auth;\nuse Symfony\\Component\\HttpFoundation\\Response;\nclass RedirectIfAuthenticated {\n    public function handle(Request $request, Closure $next, string ...$guards): Response {\n        $guards = empty($guards) ? [null] : $guards;\n        foreach ($guards as $guard) {\n            if (Auth::guard($guard)->check()) {\n                return redirect(RouteServiceProvider::HOME);\n            }\n        }\n        return $next($request);\n    }\n}\n",
  "app/Providers/RouteServiceProvider.php": "<?php\n\nnamespace App\\Providers;\n\nuse Illuminate\\Cache\\RateLimiting\\Limit;\nuse Illuminate\\Foundation\\Support\\Providers\\RouteServiceProvider as ServiceProvider;\nuse Illuminate\\Http\\Request;\nuse Illuminate\\Support\\Facades\\RateLimiter;\nuse Illuminate\\Support\\Facades\\Route;\n\nclass RouteServiceProvider extends ServiceProvider\n{\n    public const HOME = '/home';\n\n    public function boot(): void\n    {\n        RateLimiter::for('api', function (Request $request) {\n            return Limit::perMinute(60)->by($request->user()?->id ?: $request->ip());\n        });\n\n        $this->routes(function () {\n            Route::middleware('api')\n                ->prefix('api')\n                ->group(base_path('routes/api.php'));\n\n            Route::middleware('web')\n                ->group(base_path('routes/web.php'));\n        });\n    }\n}\n",
  "routes/web.php": "<?php\n\nuse Illuminate\\Support\\Facades\\Route;\n\nRoute::get('/', function () {\n    return view('welcome');\n});\n",
  "routes/api.php": "<?php\n\nuse Illuminate\\Support\\Facades\\Route;\nuse Illuminate\\Http\\Request;\n\nRoute::middleware('auth:sanctum')->get('/user', function (Request $request) {\n    return $request->user();\n});\n",
  "routes/console.php": "<?php\n\nuse Illuminate\\Support\\Facades\\Artisan;\n\nArtisan::command('inspire', function () {\n    $this->comment(Illuminate\\Foundation\\Inspiring::quote());\n})->purpose('Display an inspiring quote');\n",
  "resources/views/welcome.blade.php": "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n    <meta charset=\"UTF-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n    <title>Antigravity Laravel Application</title>\n    <style>\n        body {\n            font-family: 'Outfit', 'Inter', sans-serif;\n            background: radial-gradient(circle at top right, #1e1b4b, #0f172a);\n            color: #f8fafc;\n            min-height: 100vh;\n            display: flex;\n            align-items: center;\n            justify-content: center;\n            margin: 0;\n        }\n        .container {\n            text-align: center;\n            padding: 3rem;\n            background: rgba(255, 255, 255, 0.03);\n            backdrop-filter: blur(16px);\n            border: 1px solid rgba(255, 255, 255, 0.08);\n            border-radius: 24px;\n            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);\n            max-width: 500px;\n        }\n        h1 {\n            font-size: 2.5rem;\n            margin-bottom: 1rem;\n            background: linear-gradient(to right, #f43f5e, #fb7185);\n            -webkit-background-clip: text;\n            -webkit-text-fill-color: transparent;\n        }\n        p {\n            color: #94a3b8;\n            line-height: 1.6;\n        }\n        .badge {\n            display: inline-block;\n            padding: 0.5rem 1rem;\n            background: rgba(244, 63, 94, 0.1);\n            color: #f43f5e;\n            border-radius: 9999px;\n            font-size: 0.875rem;\n            font-weight: 600;\n            margin-bottom: 1.5rem;\n        }\n    </style>\n</head>\n<body>\n    <div class=\"container\">\n        <div class=\"badge\">Laravel 10.x + PHP</div>\n        <h1>\ud83d\ude80 Welcome to Antigravity Laravel</h1>\n        <p>Your production-ready Laravel full-stack MVC application, scaffolded and pre-configured for seamless development with AI coding agents.</p>\n    </div>\n</body>\n</html>\n",
  "phpunit.xml": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<phpunit xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n         xsi:noNamespaceSchemaLocation=\"./vendor/phpunit/phpunit/phpunit.xsd\"\n         bootstrap=\"vendor/autoload.php\"\n         colors=\"true\">\n    <testsuites>\n        <testsuite name=\"Unit\">\n            <directory suffix=\"Test.php\">./tests/Unit</directory>\n        </testsuite>\n        <testsuite name=\"Feature\">\n            <directory suffix=\"Test.php\">./tests/Feature</directory>\n        </testsuite>\n    </testsuites>\n</phpunit>\n"
}
FALLBACK_TEMPLATES = {
  "package.json": "{\n  \"name\": \"project\",\n  \"version\": \"1.0.0\",\n  \"description\": \"\",\n  \"main\": \"src/index.js\",\n  \"scripts\": {\n    \"build\": \"tsc\",\n    \"start\": \"node dist/index.js\",\n    \"test\": \"jest\",\n    \"lint\": \"eslint 'src/**/*.ts'\"\n  },\n  \"dependencies\": {},\n  \"devDependencies\": {}\n}\n",
  "go.mod": "module project\n\ngo 1.20\n",
  "src/main.go": "package main\n\nimport \"fmt\"\n\nfunc main() {\n    fmt.Println(\"Hello, Antigravity!\")\n}\n",
  "src/main.py": "def main():\n    print(\"Hello, Antigravity!\")\n\nif __name__ == \"__main__\":\n    main()\n"
}
DOCKER_TEMPLATES = {
  "db_postgres": "  postgres:\n    image: postgres:15-alpine\n    container_name: postgres_db\n    environment:\n      POSTGRES_USER: postgres\n      POSTGRES_PASSWORD: postgres\n      POSTGRES_DB: postgres\n    ports:\n      - \"5432:5432\"\n    volumes:\n      - pgdata:/var/lib/postgresql/data\n    healthcheck:\n      test: [\"CMD-SHELL\", \"pg_isready -U postgres\"]\n      interval: 5s\n      timeout: 5s\n      retries: 5\n",
  "db_mysql": "  mysql:\n    image: mysql:8.0\n    container_name: mysql_db\n    environment:\n      MYSQL_ROOT_PASSWORD: root\n      MYSQL_DATABASE: db\n    ports:\n      - \"3306:3306\"\n    volumes:\n      - mysql_data:/var/lib/mysql\n    healthcheck:\n      test: [\"CMD-SHELL\", \"mysqladmin ping -h localhost\"]\n      interval: 5s\n      timeout: 5s\n      retries: 5\n",
  "db_mongodb": "  mongodb:\n    image: mongo:6.0\n    container_name: mongodb_db\n    ports:\n      - \"27017:27017\"\n    volumes:\n      - mongo_data:/data/db\n    healthcheck:\n      test: [\"CMD-SHELL\", \"echo 'db.runCommand(\\\"ping\\\")' | mongosh localhost:27017/test --quiet\"]\n      interval: 5s\n      timeout: 5s\n      retries: 5\n",
  "db_redis": "  redis:\n    image: redis:7-alpine\n    container_name: redis_cache\n    ports:\n      - \"6379:6379\"\n    volumes:\n      - redis_data:/data\n    healthcheck:\n      test: [\"CMD-SHELL\", \"redis-cli ping | grep PONG\"]\n      interval: 5s\n      timeout: 5s\n      retries: 5\n",
  "nextjs_dockerfile": "FROM golang:1.20-alpine AS builder\nWORKDIR /app\nCOPY go.mod go.sum* ./\nRUN go mod download\nCOPY . .\nRUN CGO_ENABLED=0 GOOS=linux go build -o main ./src/cmd/server/main.go\n\nFROM alpine:latest\nWORKDIR /root/\nCOPY --from=builder /app/main .\nEXPOSE 8080\nCMD [\"./main\"]\n",
  "gogin_dockerfile": "FROM node:20-alpine AS builder\nWORKDIR /app\nCOPY package.json package-lock.json* ./\nRUN npm ci\nCOPY . .\nRUN npm run build\n\nFROM node:20-alpine AS runner\nWORKDIR /app\nENV NODE_ENV=production\nCOPY --from=builder /app/package.json ./\nCOPY --from=builder /app/dist ./dist\nCOPY --from=builder /app/node_modules ./node_modules\nEXPOSE 3000\nCMD [\"node\", \"dist/main\"]\n",
  "fastapi_dockerfile": "FROM golang:1.20-alpine AS builder\nWORKDIR /app\nCOPY go.mod go.sum* ./\nRUN go mod download\nCOPY . .\nRUN CGO_ENABLED=0 GOOS=linux go build -o main ./src/cmd/server/main.go\n\nFROM alpine:latest\nWORKDIR /root/\nCOPY --from=builder /app/main .\nEXPOSE 8080\nCMD [\"./main\"]\n",
  "laravel_dockerfile": "FROM node:20-alpine AS builder\nWORKDIR /app\nCOPY package.json package-lock.json* ./\nRUN npm ci\nCOPY . .\nRUN npm run build\n\nFROM nginx:alpine\nCOPY --from=builder /app/dist /usr/share/nginx/html\nEXPOSE 80\nCMD [\"nginx\", \"-g\", \"daemon off;\"]\n",
  "nextjs_dockerignore": "FROM node:20-alpine AS builder\nWORKDIR /app\nCOPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./\nRUN \\\n  if [ -f pnpm-lock.yaml ]; then corepack enable && pnpm i --frozen-lockfile; \\\n  elif [ -f package-lock.json ]; then npm ci; \\\n  elif [ -f yarn.lock ]; then yarn install --frozen-lockfile; \\\n  else npm install; \\\n  fi\nCOPY . .\nRUN \\\n  if [ -f pnpm-lock.yaml ]; then pnpm run build; \\\n  else npm run build; \\\n  fi\n\nFROM node:20-alpine AS runner\nWORKDIR /app\nENV NODE_ENV=production\nCOPY --from=builder /app/package.json ./\nCOPY --from=builder /app/.next ./.next\nCOPY --from=builder /app/public ./public\nCOPY --from=builder /app/node_modules ./node_modules\nEXPOSE 3000\nCMD [\"npm\", \"start\"]\n",
  "gogin_dockerignore": "FROM python:3.11-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\nCOPY . .\nEXPOSE 8000\nCMD [\"uvicorn\", \"src.app.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n",
  "fastapi_dockerignore": "FROM node:20-alpine AS builder\nWORKDIR /app\nCOPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./\nRUN \\\n  if [ -f pnpm-lock.yaml ]; then corepack enable && pnpm i --frozen-lockfile; \\\n  elif [ -f package-lock.json ]; then npm ci; \\\n  elif [ -f yarn.lock ]; then yarn install --frozen-lockfile; \\\n  else npm install; \\\n  fi\nCOPY . .\nRUN \\\n  if [ -f pnpm-lock.yaml ]; then pnpm run build; \\\n  else npm run build; \\\n  fi\n\nFROM node:20-alpine AS runner\nWORKDIR /app\nENV NODE_ENV=production\nCOPY --from=builder /app/package.json ./\nCOPY --from=builder /app/.next ./.next\nCOPY --from=builder /app/public ./public\nCOPY --from=builder /app/node_modules ./node_modules\nEXPOSE 3000\nCMD [\"npm\", \"start\"]\n",
  "fallback_node_dockerfile": "FROM node:20-alpine AS builder\nWORKDIR /app\nCOPY package.json package-lock.json* ./\nRUN npm ci\nCOPY . .\nRUN npm run build\n\nFROM node:20-alpine AS runner\nWORKDIR /app\nENV NODE_ENV=production\nCOPY --from=builder /app/package.json ./\nCOPY --from=builder /app/.next ./.next\nCOPY --from=builder /app/public ./public\nCOPY --from=builder /app/node_modules ./node_modules\nEXPOSE 3000\nCMD [\"npm\", \"start\"]\n",
  "fallback_go_dockerfile": "FROM golang:1.20-alpine AS builder\nWORKDIR /app\nCOPY go.mod go.sum* ./\nRUN go mod download\nCOPY . .\nRUN CGO_ENABLED=0 GOOS=linux go build -o main ./src/cmd/server/main.go\n\nFROM alpine:latest\nWORKDIR /root/\nCOPY --from=builder /app/main .\nEXPOSE 8080\nCMD [\"./main\"]\n",
  "fallback_py_dockerfile": "FROM python:3.11-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\nCOPY . .\nEXPOSE 8000\nCMD [\"uvicorn\", \"src.app.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n",
  "fallback_laravel_dockerfile": "FROM node:20-alpine AS builder\nWORKDIR /app\nCOPY package.json package-lock.json* ./\nRUN npm ci\nCOPY . .\nRUN npm run build\n\nFROM node:20-alpine AS runner\nWORKDIR /app\nENV NODE_ENV=production\nCOPY --from=builder /app/package.json ./\nCOPY --from=builder /app/dist ./dist\nCOPY --from=builder /app/node_modules ./node_modules\nEXPOSE 3000\nCMD [\"node\", \"dist/index.js\"]\n",
  "compose_multi": "version: '3.8'\n\nservices:\n",
  "compose_volume": "\nvolumes:\n  pgdata:\n  mysql_data:\n  mongo_data:\n  redis_data:\n",
  "compose_single": "version: '3.8'\n\nservices:\n"
}
MULTIPROJECT_FILES = {
  "apps/backend/package.json": "{\n  \"name\": \"backend\",\n  \"version\": \"1.0.0\",\n  \"private\": true,\n  \"scripts\": {\n    \"build\": \"nest build\",\n    \"start\": \"nest start\",\n    \"lint\": \"eslint 'src/**/*.ts'\",\n    \"test\": \"jest\"\n  },\n  \"dependencies\": {\n    \"@nestjs/common\": \"^10.0.0\",\n    \"@nestjs/core\": \"^10.0.0\",\n    \"reflect-metadata\": \"^0.1.13\",\n    \"rxjs\": \"^7.8.1\"\n  },\n  \"devDependencies\": {\n    \"@nestjs/cli\": \"^10.0.0\",\n    \"@nestjs/testing\": \"^10.0.0\",\n    \"@types/node\": \"^20.0.0\",\n    \"typescript\": \"^5.0.0\",\n    \"eslint\": \"^8.0.0\",\n    \"jest\": \"^29.0.0\"\n  }\n}\n",
  "apps/backend/src/main.ts": "import { NestFactory } from '@nestjs/core';\nimport { AppModule } from './app.module';\n\nasync function bootstrap() {\n  const app = await NestFactory.create(AppModule);\n  await app.listen(process.env.PORT || 3000);\n}\nbootstrap();\n",
  "apps/backend/src/app.module.ts": "import { Module } from '@nestjs/common';\n\n@Module({\n  imports: [],\n  controllers: [],\n  providers: [],\n})\nexport class AppModule {}\n",
  "apps/backend/requirements.txt": "fastapi>=0.110.0\nuvicorn[standard]>=0.28.0\npydantic>=2.6.4\npytest>=8.1.1\nhttpx>=0.27.0\n",
  "apps/backend/src/app/main.py": "from fastapi import FastAPI\n\napp = FastAPI(title=\"Antigravity Custom Backend\")\n\n@app.get(\"/\")\ndef read_root():\n    return {\"message\": \"Hello from Custom FastAPI Backend!\"}\n",
  "apps/backend/go.mod": "module backend\n\ngo 1.20\n\nrequire (\n\tgithub.com/gin-gonic/gin v1.9.1\n)\n",
  "apps/backend/src/cmd/server/main.go": "package main\n\nimport (\n\t\"github.com/gin-gonic/gin\"\n)\n\nfunc main() {\n\tr := gin.Default()\n\tr.GET(\"/\", func(c *gin.Context) {\n\t\tc.JSON(200, gin.H{\n\t\t\t\"message\": \"Hello from Custom Go Gin Backend!\",\n\t\t})\n\t})\n\tr.Run()\n}\n",
  "apps/frontend/package.json": "{\n  \"name\": \"frontend\",\n  \"version\": \"1.0.0\",\n  \"private\": true,\n  \"scripts\": {\n    \"dev\": \"vite\",\n    \"build\": \"tsc && vite build\",\n    \"lint\": \"eslint 'src/**/*.ts'\",\n    \"test\": \"jest\"\n  },\n  \"dependencies\": {\n    \"react\": \"^18.3.1\",\n    \"react-dom\": \"^18.3.1\"\n  },\n  \"devDependencies\": {\n    \"vite\": \"^5.0.0\",\n    \"@types/react\": \"^18.0.0\",\n    \"typescript\": \"^5.0.0\",\n    \"eslint\": \"^8.0.0\",\n    \"jest\": \"^29.0.0\"\n  }\n}\n",
  "apps/frontend/src/app/layout.tsx": "import type { Metadata } from 'next';\n\nexport const metadata: Metadata = {\n  title: 'Antigravity Custom Frontend',\n  description: 'Flexible separate frontend application',\n};\n\nexport default function RootLayout({\n  children,\n}: {\n  children: React.ReactNode;\n}) {\n  return (\n    <html lang=\"en\">\n      <body>{children}</body>\n    </html>\n  );\n}\n",
  "apps/frontend/src/app/page.tsx": "export default function Home() {\n  return (\n    <main style={{ padding: '2rem', fontFamily: 'sans-serif' }}>\n      <h1>\ud83d\ude80 Welcome to Antigravity Custom Frontend</h1>\n      <p>Running alongside a decoupled backend service in a clean modular layout.</p>\n    </main>\n  );\n}\n",
  "apps/frontend/index.html": "<!DOCTYPE html>\n<html lang=\"en\">\n  <head>\n    <meta charset=\"UTF-8\" />\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />\n    <title>Antigravity React SPA</title>\n  </head>\n  <body>\n    <div id=\"root\"></div>\n    <script type=\"module\" src=\"/src/main.tsx\"></script>\n  </body>\n</html>\n",
  "apps/frontend/src/main.tsx": "import React from 'react';\nimport ReactDOM from 'react-dom/client';\nimport App from './App';\n\nReactDOM.createRoot(document.getElementById('root')!).render(\n  <React.StrictMode>\n    <App />\n  </React.StrictMode>\n);\n",
  "apps/frontend/src/App.tsx": "import React from 'react';\n\nexport default function App() {\n  return (\n    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>\n      <h1>\ud83d\ude80 Welcome to Antigravity React SPA Frontend</h1>\n      <p>Decoupled single-page frontend application.</p>\n    </div>\n  );\n}\n",
  "apps/frontend/resources/views/welcome.blade.php": "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n    <meta charset=\"UTF-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n    <title>Antigravity Blade Frontend</title>\n    <style>\n        body { font-family: sans-serif; padding: 2rem; background-color: #f8fafc; color: #1e293b; }\n    </style>\n</head>\n<body>\n    <h1>\ud83d\ude80 Welcome to Antigravity Blade/HTML Frontend</h1>\n    <p>Flexible separate frontend application template.</p>\n</body>\n</html>\n"
}

def get_input(prompt, default):
    try:
        val = input(f"{prompt} (default: {default}): ").strip()
        return val if val else default
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(1)

def select_choice(prompt, options, default_choice="1"):
    print(prompt)
    for opt in options:
        print(f"  {opt}")
    try:
        val = input(f"Select choice (default: {default_choice}): ").strip()
        return val if val else default_choice
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(1)

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  Created {path}")

def run(args):
    print("==========================================================")
    print("  Antigravity Agent Core - Workspace Initialization")
    print("==========================================================")
    
    project_name = args[1] if len(args) > 1 else None
    tech_stack = args[2] if len(args) > 2 else None
    arch_pattern = args[3] if len(args) > 3 else None
    db_orm = args[4] if len(args) > 4 else None
    env_vars = args[5] if len(args) > 5 else None
    scaffold = args[6] if len(args) > 6 else None
    gen_docker = args[7] if len(args) > 7 else None
    
    be_choice = "1"
    be_arch_choice = "2"
    fe_choice = "1"
    fe_arch_choice = "2"
    
    if not project_name:
        project_name = get_input("Enter Project Name", "My Project")
        
    if not tech_stack:
        stack_opts = [
            "[1] Next.js (TypeScript, Tailwind, App Router) [Recommended]",
            "[2] Go Gin (Clean Architecture REST API)",
            "[3] FastAPI (Python REST API with pytest)",
            "[4] Node/TypeScript (Generic Node App)",
            "[5] Go (Generic Main App)",
            "[6] Python (Generic Script)",
            "[7] Monorepo (Turborepo: Next.js Frontend + Go Gin Backend)",
            "[8] Custom Multi-Project / Separate Apps (e.g. apps/backend + apps/frontend)",
            "[9] Laravel (PHP MVC Framework)"
        ]
        choice = select_choice("Select Technology Stack:", stack_opts, "1")
        mapping = {
            "1": "Next.js", "2": "Go Gin", "3": "FastAPI", "4": "Node/TypeScript",
            "5": "Go", "6": "Python", "7": "Monorepo", "8": "Multi-Project", "9": "Laravel"
        }
        tech_stack = mapping.get(choice, choice)
        
    if tech_stack == "Multi-Project":
        be_opts = ["[1] NestJS (TypeScript)", "[2] FastAPI (Python)", "[3] Go Gin", "[4] None"]
        be_choice = select_choice("--- Configure Backend Application ---", be_opts, "1")
        
        if be_choice != "4":
            arch_opts = ["[1] Hexagonal Architecture (Ports & Adapters)", "[2] Clean Architecture", "[3] Standard MVC / Modular"]
            be_arch_choice = select_choice("Configure Backend Architecture:", arch_opts, "2")
            
        fe_opts = ["[1] Next.js (TypeScript)", "[2] React SPA (Vite)", "[3] Laravel Blade / PHP HTML", "[4] None"]
        fe_choice = select_choice("--- Configure Frontend Application ---", fe_opts, "1")
        
        if fe_choice != "4":
            arch_opts = ["[1] Atomic Design", "[2] Standard Components / App Router Layout"]
            fe_arch_choice = select_choice("Configure Frontend Architecture:", arch_opts, "2")
            
        arch_pattern = "Decoupled / Distributed Architecture"
        db_orm = "None"
        env_vars = "PORT"
        
    default_arch = "MVC"
    if tech_stack == "Next.js":
        default_arch = "App Router"
    elif tech_stack == "Go Gin":
        default_arch = "Clean Architecture"
    elif tech_stack == "FastAPI":
        default_arch = "Modular REST"
    elif tech_stack == "Monorepo":
        default_arch = "Decoupled / Distributed"
    elif tech_stack == "Laravel":
        default_arch = "MVC"
        
    if not arch_pattern:
        arch_pattern = get_input("Enter Architectural Pattern", default_arch)
        
    default_env = "PORT"
    if tech_stack in ("Go Gin", "FastAPI"):
        default_env = "PORT,ENV"
    elif tech_stack == "Next.js":
        default_env = "PORT"
    elif tech_stack == "Laravel":
        default_env = "APP_KEY,DB_CONNECTION,DB_DATABASE"
        
    if not db_orm:
        db_orm = get_input("Enter Database/ORM (e.g. Prisma, PostgreSQL, None)", "None")
        
    if not env_vars:
        env_vars = get_input("Enter config variables (comma-separated)", default_env)
        
    if not scaffold:
        scaffold = get_input("Scaffold initial project folders? (y/n)", "y").lower()
        
    if not gen_docker:
        gen_docker = get_input("Generate Dockerfiles and docker-compose.yml? (y/n)", "y").lower()

    # 1. Initialize Git if not present
    if not os.path.exists(".git"):
        print("Initializing Git repository...")
        subprocess.run(["git", "init"])
        subprocess.run(["git", "branch", "-m", "main"])
        
    # 2. Install Git hooks
    agents_dir = utils.get_agents_dir()
    os.makedirs(".git/hooks", exist_ok=True)
    for h in ('pre-commit', 'post-commit', 'commit-msg'):
        src = os.path.join(agents_dir, 'hooks', h)
        dest = os.path.join('.git', 'hooks', h)
        if os.path.exists(src):
            shutil.copy(src, dest)
            os.chmod(dest, 0o755)
            print(f"Git {h} hook installed.")

    # 3. Scaffold folders if requested
    if scaffold in ("y", "yes"):
        print("Scaffolding directory structure...")
        
        if tech_stack == "Next.js":
            if "Atomic" in arch_pattern or "atomic" in arch_pattern:
                dirs = ['src/app', 'src/components/atoms', 'src/components/molecules', 'src/components/organisms', 'src/components/templates', 'src/lib', 'tests']
            elif "Clean" in arch_pattern or "clean" in arch_pattern:
                dirs = ['src/app', 'src/core/entities', 'src/core/usecases', 'src/infrastructure/db', 'src/infrastructure/api', 'src/lib', 'tests']
            else:
                dirs = ['src/app', 'src/components', 'src/lib', 'tests']
            for d in dirs:
                os.makedirs(d, exist_ok=True)
                
            for path, content in NEXT_TEMPLATES.items():
                write_file(path, content)
                
        elif tech_stack == "Go Gin":
            if any(x in arch_pattern for x in ("Hexagonal", "Ports", "Adapters")):
                dirs = ['src/cmd/server', 'src/internal/core/domain', 'src/internal/core/ports', 'src/internal/adapters/in/web', 'src/internal/adapters/out/db', 'src/internal/config', 'tests']
            elif "Clean" in arch_pattern:
                dirs = ['src/cmd/server', 'src/internal/domain/entity', 'src/internal/domain/usecase', 'src/internal/adapter/controller', 'src/internal/adapter/repository', 'src/internal/infrastructure/db', 'src/internal/config', 'tests']
            else:
                dirs = ['src/cmd/server', 'src/internal/model', 'src/internal/controller', 'src/internal/view', 'src/internal/config', 'tests']
            for d in dirs:
                os.makedirs(d, exist_ok=True)
                
            for path, content in GOGIN_TEMPLATES.items():
                write_file(path, content)
                
        elif tech_stack == "FastAPI":
            if any(x in arch_pattern for x in ("Hexagonal", "Ports", "Adapters")):
                dirs = ['src/app/domain', 'src/app/ports', 'src/app/adapters/in/api', 'src/app/adapters/out/db', 'src/app/core', 'tests']
            elif "Clean" in arch_pattern:
                dirs = ['src/app/entities', 'src/app/usecases', 'src/app/controllers', 'src/app/infrastructure/db', 'src/app/core', 'tests']
            else:
                dirs = ['src/app/core', 'src/app/api/endpoints', 'tests']
            for d in dirs:
                os.makedirs(d, exist_ok=True)
                
            for path, content in FASTAPI_TEMPLATES.items():
                write_file(path, content)
                
        elif tech_stack == "Monorepo":
            dirs = ['apps/web/src/app/api/health', 'apps/web/src/components', 'apps/web/src/lib', 'apps/web/tests',
                    'apps/api/src/cmd/server', 'apps/api/src/internal/controller', 'apps/api/src/internal/config', 'apps/api/tests',
                    'packages/shared']
            for d in dirs:
                os.makedirs(d, exist_ok=True)
                
            for path, content in MONOREPO_TEMPLATES.items():
                write_file(path, content)
                
        elif tech_stack == "Laravel":
            dirs = ['app/Http/Controllers', 'app/Models', 'app/Providers', 'bootstrap', 'config', 'database/migrations',
                    'database/seeders', 'database/factories', 'public', 'resources/views', 'resources/css', 'resources/js',
                    'routes', 'tests/Feature', 'tests/Unit', 'app/Http/Middleware', 'app/Exceptions', 'app/Console']
            for d in dirs:
                os.makedirs(d, exist_ok=True)
                
            for path, content in LARAVEL_TEMPLATES.items():
                write_file(path, content)
                
        elif tech_stack == "Multi-Project":
            os.makedirs("apps/backend", exist_ok=True)
            os.makedirs("apps/frontend", exist_ok=True)
            
            # 1. Backend
            if be_choice == "1":
                # NestJS
                if be_arch_choice == "1":
                    dirs = ['apps/backend/src/core/domain', 'apps/backend/src/core/ports', 'apps/backend/src/adapters/in/web', 'apps/backend/src/adapters/out/persistence']
                elif be_arch_choice == "2":
                    dirs = ['apps/backend/src/entities', 'apps/backend/src/usecases', 'apps/backend/src/controllers', 'apps/backend/src/infrastructure/db']
                else:
                    dirs = ['apps/backend/src/modules', 'apps/backend/src/common']
                for d in dirs: os.makedirs(d, exist_ok=True)
                write_file("apps/backend/package.json", MULTIPROJECT_FILES["apps/backend/package.json"])
                write_file("apps/backend/src/main.ts", MULTIPROJECT_FILES["apps/backend/src/main.ts"])
                write_file("apps/backend/src/app.module.ts", MULTIPROJECT_FILES["apps/backend/src/app.module.ts"])
            elif be_choice == "2":
                # FastAPI
                if be_arch_choice == "1":
                    dirs = ['apps/backend/src/domain', 'apps/backend/src/ports', 'apps/backend/src/adapters/in/api', 'apps/backend/src/adapters/out/db', 'apps/backend/src/core']
                elif be_arch_choice == "2":
                    dirs = ['apps/backend/src/entities', 'apps/backend/src/usecases', 'apps/backend/src/controllers', 'apps/backend/src/infrastructure/db', 'apps/backend/src/core']
                else:
                    dirs = ['apps/backend/src/core', 'apps/backend/src/api/endpoints']
                for d in dirs: os.makedirs(d, exist_ok=True)
                write_file("apps/backend/requirements.txt", MULTIPROJECT_FILES["apps/backend/requirements.txt"])
                write_file("apps/backend/src/app/main.py", MULTIPROJECT_FILES["apps/backend/src/app/main.py"])
            elif be_choice == "3":
                # Go Gin
                if be_arch_choice == "1":
                    dirs = ['apps/backend/src/cmd/server', 'apps/backend/src/internal/core/domain', 'apps/backend/src/internal/core/ports', 'apps/backend/src/internal/adapters/in/web', 'apps/backend/src/internal/adapters/out/db', 'apps/backend/src/internal/config']
                elif be_arch_choice == "2":
                    dirs = ['apps/backend/src/cmd/server', 'apps/backend/src/internal/domain/entity', 'apps/backend/src/internal/domain/usecase', 'apps/backend/src/internal/adapter/controller', 'apps/backend/src/internal/adapter/repository', 'apps/backend/src/internal/infrastructure/db', 'apps/backend/src/internal/config']
                else:
                    dirs = ['apps/backend/src/cmd/server', 'apps/backend/src/internal/model', 'apps/backend/src/internal/controller', 'apps/backend/src/internal/view', 'apps/backend/src/internal/config']
                for d in dirs: os.makedirs(d, exist_ok=True)
                write_file("apps/backend/go.mod", MULTIPROJECT_FILES["apps/backend/go.mod"])
                write_file("apps/backend/src/cmd/server/main.go", MULTIPROJECT_FILES["apps/backend/src/cmd/server/main.go"])
                
            # 2. Frontend
            if fe_choice == "1":
                # Next.js
                if fe_arch_choice == "1":
                    dirs = ['apps/frontend/src/app', 'apps/frontend/src/lib', 'apps/frontend/src/components/atoms', 'apps/frontend/src/components/molecules', 'apps/frontend/src/components/organisms', 'apps/frontend/src/components/templates']
                else:
                    dirs = ['apps/frontend/src/app', 'apps/frontend/src/lib', 'apps/frontend/src/components']
                for d in dirs: os.makedirs(d, exist_ok=True)
                write_file("apps/frontend/package.json", MULTIPROJECT_FILES["apps/frontend/package.json"])
                write_file("apps/frontend/src/app/layout.tsx", MULTIPROJECT_FILES["apps/frontend/src/app/layout.tsx"])
                write_file("apps/frontend/src/app/page.tsx", MULTIPROJECT_FILES["apps/frontend/src/app/page.tsx"])
            elif fe_choice == "2":
                # React SPA
                if fe_arch_choice == "1":
                    dirs = ['apps/frontend/src', 'apps/frontend/public', 'apps/frontend/src/components/atoms', 'apps/frontend/src/components/molecules', 'apps/frontend/src/components/organisms', 'apps/frontend/src/components/templates']
                else:
                    dirs = ['apps/frontend/src', 'apps/frontend/public', 'apps/frontend/src/components']
                for d in dirs: os.makedirs(d, exist_ok=True)
                write_file("apps/frontend/package.json", MULTIPROJECT_FILES["apps/frontend/package.json"])
                write_file("apps/frontend/index.html", MULTIPROJECT_FILES["apps/frontend/index.html"])
                write_file("apps/frontend/src/main.tsx", MULTIPROJECT_FILES["apps/frontend/src/main.tsx"])
                write_file("apps/frontend/src/App.tsx", MULTIPROJECT_FILES["apps/frontend/src/App.tsx"])
            elif fe_choice == "3":
                # Laravel Blade
                os.makedirs("apps/frontend/resources/views", exist_ok=True)
                write_file("apps/frontend/resources/views/welcome.blade.php", MULTIPROJECT_FILES["apps/frontend/resources/views/welcome.blade.php"])
                
        else:
            # Fallback (Generic/Basic)
            dirs = ['src', 'tests', 'config']
            for d in dirs: os.makedirs(d, exist_ok=True)
            
            stack_lower = tech_stack.lower()
            if any(x in stack_lower for x in ("node", "typescript", "ts")):
                write_file("package.json", FALLBACK_TEMPLATES["package.json"])
            if any(x in stack_lower for x in ("go", "golang")):
                write_file("go.mod", FALLBACK_TEMPLATES["go.mod"])
                write_file("src/main.go", FALLBACK_TEMPLATES["src/main.go"])
            if any(x in stack_lower for x in ("python", "py")):
                write_file("src/main.py", FALLBACK_TEMPLATES["src/main.py"])

    # 4. Generate Dockerfiles
    if gen_docker in ("y", "yes"):
        print("Generating Dockerfiles and docker-compose.yml...")
        
        db_service = ""
        db_envs = ""
        db_depends = ""
        db_lower = db_orm.lower()
        
        if "postgres" in db_lower:
            db_service = DOCKER_TEMPLATES["db_postgres"]
            db_envs = "      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/postgres\n      - DB_HOST=postgres\n      - DB_PORT=5432"
            db_depends = "    depends_on:\n      postgres:\n        condition: service_healthy"
        elif "mysql" in db_lower or "mariadb" in db_lower:
            db_service = DOCKER_TEMPLATES["db_mysql"]
            db_envs = "      - DATABASE_URL=mysql://root:root@mysql:3306/db\n      - DB_HOST=mysql\n      - DB_PORT=3306"
            db_depends = "    depends_on:\n      mysql:\n        condition: service_healthy"
        elif "mongo" in db_lower:
            db_service = DOCKER_TEMPLATES["db_mongodb"]
            db_envs = "      - DATABASE_URL=mongodb://mongodb:27017/db\n      - DB_HOST=mongodb\n      - DB_PORT=27017"
            db_depends = "    depends_on:\n      mongodb:\n        condition: service_healthy"
        elif "redis" in db_lower:
            db_service = DOCKER_TEMPLATES["db_redis"]
            db_envs = "      - REDIS_URL=redis://redis:6379/0\n      - REDIS_HOST=redis\n      - REDIS_PORT=6379"
            db_depends = "    depends_on:\n      redis:\n        condition: service_healthy"

        # Multi/Monorepos
        if tech_stack in ("Monorepo", "Multi-Project"):
            be_dir = "apps/api" if tech_stack == "Monorepo" else "apps/backend"
            fe_dir = "apps/web" if tech_stack == "Monorepo" else "apps/frontend"
            
            # Backend Dockerfile selection
            be_docker = ""
            if tech_stack == "Monorepo" or be_choice == "3":
                be_docker = DOCKER_TEMPLATES["gogin_dockerfile"]
            elif be_choice == "2":
                be_docker = DOCKER_TEMPLATES["fastapi_dockerfile"]
            elif be_choice == "1":
                # NestJS
                be_docker = "FROM node:18-alpine\nWORKDIR /app\nCOPY package*.json ./\nRUN npm install\nCOPY . .\nRUN npm run build\nCMD [\"npm\", \"run\", \"start:prod\"]"
                
            # Frontend Dockerfile selection
            fe_docker = ""
            if tech_stack == "Monorepo" or fe_choice == "1":
                fe_docker = DOCKER_TEMPLATES["nextjs_dockerfile"]
            elif fe_choice == "2":
                fe_docker = "FROM node:18-alpine\nWORKDIR /app\nCOPY package*.json ./\nRUN npm install\nCOPY . .\nRUN npm run build\nRUN npm install -g serve\nCMD [\"serve\", \"-s\", \"dist\"]"
            elif fe_choice == "3":
                fe_docker = DOCKER_TEMPLATES["laravel_dockerfile"]
                
            # Write Dockerfiles
            if be_choice != "4":
                write_file(f"{be_dir}/Dockerfile", be_docker.replace('\\n', '\n').replace('\"', '"'))
            if fe_choice != "4":
                write_file(f"{fe_dir}/Dockerfile", fe_docker.replace('\\n', '\n').replace('\"', '"'))
                
            # Compose
            services = ""
            if fe_choice != "4":
                services += f"  frontend:\n    build:\n      context: ./{fe_dir}\n      dockerfile: Dockerfile\n    ports:\n      - \"3000:3000\"\n"
            if be_choice != "4":
                services += f"  backend:\n    build:\n      context: ./{be_dir}\n      dockerfile: Dockerfile\n    ports:\n      - \"8080:8080\"\n"
                if db_depends:
                    services += f"{db_depends}\n"
                if db_envs:
                    services += f"    environment:\n{db_envs}\n"
                    
            if db_service:
                services += f"\n{db_service}\n"
                
            compose_content = f"version: '3.8'\n\nservices:\n{services}"
            if "postgres" in db_lower or "mysql" in db_lower or "mariadb" in db_lower or "mongo" in db_lower:
                vol_name = "pgdata" if "postgres" in db_lower else ("mysql_data" if "mysql" in db_lower or "mariadb" in db_lower else "mongo_data")
                compose_content += f"\nvolumes:\n  {vol_name}:\n"
                
            write_file("docker-compose.yml", compose_content.replace('\\n', '\n').replace('\"', '"'))
            
        else:
            # Single Project dockerfiles
            dockerfile_content = ""
            dockerignore_content = ""
            
            if tech_stack == "Next.js":
                dockerfile_content = DOCKER_TEMPLATES.get("nextjs_dockerfile", "")
                dockerignore_content = DOCKER_TEMPLATES.get("nextjs_dockerignore", "")
            elif tech_stack in ("Go Gin", "Go"):
                dockerfile_content = DOCKER_TEMPLATES.get("gogin_dockerfile", "")
                dockerignore_content = DOCKER_TEMPLATES.get("gogin_dockerignore", "")
            elif tech_stack in ("FastAPI", "Python"):
                dockerfile_content = DOCKER_TEMPLATES.get("fastapi_dockerfile", "")
                dockerignore_content = DOCKER_TEMPLATES.get("fastapi_dockerignore", "")
            elif tech_stack == "Laravel":
                dockerfile_content = DOCKER_TEMPLATES.get("laravel_dockerfile", "")
            elif any(x in tech_stack.lower() for x in ("node", "typescript", "ts")):
                dockerfile_content = DOCKER_TEMPLATES.get("fallback_node_dockerfile", "")
                
            if dockerfile_content:
                write_file("Dockerfile", dockerfile_content.replace('\\n', '\n').replace('\"', '"'))
            if dockerignore_content:
                write_file(".dockerignore", dockerignore_content.replace('\\n', '\n').replace('\"', '"'))
                
            # Compose
            port = "3000" if tech_stack == "Next.js" else ("8080" if tech_stack in ("Go Gin", "Go") else "8000")
            services = f"  app:\n    build:\n      context: .\n      dockerfile: Dockerfile\n    ports:\n      - \"{port}:{port}\"\n"
            if db_depends:
                services += f"{db_depends}\n"
            if db_envs:
                services += f"    environment:\n{db_envs}\n"
                
            if db_service:
                services += f"\n{db_service}\n"
                
            compose_content = f"version: '3.8'\n\nservices:\n{services}"
            if "postgres" in db_lower or "mysql" in db_lower or "mariadb" in db_lower or "mongo" in db_lower:
                vol_name = "pgdata" if "postgres" in db_lower else ("mysql_data" if "mysql" in db_lower or "mariadb" in db_lower else "mongo_data")
                compose_content += f"\nvolumes:\n  {vol_name}:\n"
                
            write_file("docker-compose.yml", compose_content.replace('\\n', '\n').replace('\"', '"'))

    # 5. Create .env and .env.example
    if env_vars:
        print("Writing configuration environment variables...")
        vars_list = [v.strip() for v in env_vars.split(',') if v.strip()]
        env_content = "\n".join([f"{v}=" for v in vars_list]) + "\n"
        with open(".env.example", 'w') as f:
            f.write(env_content)
        with open(".env", 'w') as f:
            f.write(env_content)
        print("Created .env and .env.example templates")

    # 6. Run auto-recon to generate the blueprints
    print("Running autonomous reconnaissance to populate blueprint files...")
    recon_sh = os.path.join(agents_dir, 'scripts', 'recon.sh')
    if os.path.exists(recon_sh):
        subprocess.run([recon_sh, "-f"])
        
    print("==========================================================")
    print(f"Workspace initialized successfully for '{project_name}'!")
    print("==========================================================")

EOF

# Write .agents/scripts/cli/commands/guide.py
write_template_safe ".agents/scripts/cli/commands/guide.py" << 'EOF'
import sys
import utils

# ANSI color codes
C_HEADER = '\033[95m'
C_BLUE = '\033[94m'
C_CYAN = '\033[96m'
C_GREEN = '\033[92m'
C_YELLOW = '\033[93m'
C_BOLD = '\033[1m'
C_END = '\033[0m'

def color(text, ansi_code):
    if sys.stdout.isatty():
        return f"{ansi_code}{text}{C_END}"
    return text

def run(args):
    print(color("=====================================================================", C_BLUE))
    print(color("   🚀 Welcome to Antigravity Agent Core Onboarding Guide 🚀", C_BOLD + C_HEADER))
    print(color("=====================================================================", C_BLUE))
    print("Antigravity Agent Core (AAC) is a developer protocol and workspace")
    print("layout designed to coordinate human-agent pair-programming safely,")
    print("cost-effectively, and securely.")
    print("")
    
    print(color("💡 THE 3-STEP DAILY WORKFLOW FOR DEVELOPERS & AGENTS", C_BOLD + C_CYAN))
    print(color("---------------------------------------------------------------------", C_BLUE))
    print("When modifying code in this workspace, follow this atomic sequence:")
    print("")
    
    print(f"{color('1. LOCK', C_BOLD + C_GREEN)} the module you want to edit:")
    print(f"   $ {color('./.agents/scripts/helper.sh lock <module-directory>', C_CYAN)}")
    print(f"   Example: {color('./.agents/scripts/helper.sh lock cli', C_GRAY if not sys.stdout.isatty() else '\033[90m')}")
    print("   (This tells other developers/agents not to modify this module.)")
    print("")
    
    print(f"{color('2. WRITE', C_BOLD + C_GREEN)} your code and tests (TDD is highly recommended).")
    print("")
    
    print(f"{color('3. COMMIT', C_BOLD + C_GREEN)} your changes using the helper commit command:")
    print(f"   $ {color('./.agents/scripts/helper.sh commit <type> <scope> \"description\" [files...]', C_CYAN)}")
    print(f"   Example: {color('./.agents/scripts/helper.sh commit feat cli \"add push subcommand\"', C_GRAY if not sys.stdout.isatty() else '\033[90m')}")
    print("   (This runs validation checks, rotates SSH keys/Git profiles, commits,")
    print("   and automatically releases your lock).")
    print("")
    
    print(color("🩺 KEY DIAGNOSTICS & SYSTEM COMMANDS", C_BOLD + C_CYAN))
    print(color("---------------------------------------------------------------------", C_BLUE))
    
    print(f"- {color('Run Health Checks', C_BOLD)}: {color('./.agents/scripts/helper.sh doctor', C_CYAN)}")
    print("  (Checks Git hooks, execution permissions, and workspace validation status.)")
    print("")
    
    print(f"- {color('Validate Compliance', C_BOLD)}: {color('./.agents/scripts/helper.sh validate', C_CYAN)}")
    print("  (Audits workspace for hardcoded secrets, environment purity, and budget limits.)")
    print("")
    
    print(f"- {color('Setup Profile Rotation', C_BOLD)}: {color('./.agents/scripts/helper.sh git-profile', C_CYAN)}")
    print("  (Manages multiple local git config identities and rotates SSH key bindings.)")
    print("")
    
    print(color("📚 DOCUMENTATION & RESOURCES", C_BOLD + C_CYAN))
    print(color("---------------------------------------------------------------------", C_BLUE))
    print("Detailed guides are located inside the root 'docs/' directory:")
    print(f"- Setup Guide:        {color('docs/setup_guide.md', C_GREEN)}")
    print(f"- CLI Reference:      {color('docs/cli_guide.md', C_GREEN)}")
    print(f"- Agent Workflows:    {color('docs/agent_workflow.md', C_GREEN)}")
    print(f"- Directory Layout:   {color('docs/directory_blueprint.md', C_GREEN)}")
    print(color("=====================================================================", C_BLUE))

EOF

# Write .agents/scripts/cli/commands/recon.py
write_template_safe ".agents/scripts/cli/commands/recon.py" << 'EOF'
import os
import sys
import subprocess
import utils

def run(args):
    recon_sh = os.path.join(utils.get_agents_dir(), 'scripts', 'recon.sh')
    if not os.path.exists(recon_sh):
        print(f"Error: recon.sh not found at {recon_sh}", file=sys.stderr)
        sys.exit(1)
        
    proc = subprocess.run([recon_sh] + args[1:])
    sys.exit(proc.returncode)

EOF

# Write .agents/scripts/cli/__init__.py
write_template_safe ".agents/scripts/cli/__init__.py" << 'EOF'


EOF

# Write .agents/scripts/cli/utils.py
write_template_safe ".agents/scripts/cli/utils.py" << 'EOF'
import os
import sys
import json
import time

def find_workspace_root():
    """
    Finds the directory containing the '.agents' folder, starting from the current directory
    and walking up. Defaults to the current directory if not found.
    """
    curr = os.path.abspath(os.getcwd())
    while True:
        if os.path.isdir(os.path.join(curr, '.agents')):
            return curr
        parent = os.path.dirname(curr)
        if parent == curr:
            break
        curr = parent
    return os.path.abspath(os.getcwd())

def get_agents_dir():
    return os.path.join(find_workspace_root(), '.agents')

def get_memory_file():
    return os.path.join(get_agents_dir(), 'memory.md')

def print_title(title):
    print("==========================================================")
    print(f"  {title}")
    print("==========================================================")

def load_budget():
    budget_file = os.path.join(get_agents_dir(), 'token_budget.json')
    budget = {
        "max_token_budget": 500000,
        "current_token_usage": 0,
        "alert_threshold_percent": 90,
        "profiles": {}
    }
    if os.path.exists(budget_file):
        try:
            with open(budget_file, 'r') as f:
                budget = json.load(f)
        except:
            pass
            
    # Process automatic budget resets if configured
    reset_interval = budget.get("reset_interval")
    if reset_interval and reset_interval != "none":
        # Determine interval duration in seconds
        interval_seconds = None
        if reset_interval == "hourly":
            interval_seconds = 3600
        elif reset_interval == "daily":
            interval_seconds = 86400
        elif reset_interval == "weekly":
            interval_seconds = 604800
        elif reset_interval == "monthly":
            interval_seconds = 2592000
        else:
            try:
                interval_seconds = int(reset_interval)
            except ValueError:
                pass
                
        if interval_seconds is not None:
            current_time = int(time.time())
            last_reset = budget.get("last_reset_timestamp")
            
            # If last reset is not set, initialize it to the current time
            if last_reset is None:
                budget["last_reset_timestamp"] = current_time
                save_budget(budget)
            else:
                try:
                    last_reset = int(last_reset)
                except ValueError:
                    last_reset = current_time
                    budget["last_reset_timestamp"] = current_time
                    save_budget(budget)
                    
                if current_time - last_reset >= interval_seconds:
                    print(f"\n[INFO] Token budget reset interval ('{reset_interval}') has expired.")
                    print("Resetting all current token usage counts to 0.")
                    budget["current_token_usage"] = 0
                    if "profiles" in budget:
                        for profile in budget["profiles"].values():
                            if isinstance(profile, dict):
                                profile["current_token_usage"] = 0
                    budget["last_reset_timestamp"] = current_time
                    save_budget(budget)
                    
    return budget

def save_budget(budget):
    budget_file = os.path.join(get_agents_dir(), 'token_budget.json')
    with open(budget_file, 'w') as f:
        json.dump(budget, f, indent=2)

def log_token_usage(tokens):
    """
    Log token usage for both the active profile and globally.
    """
    budget = load_budget()
    
    # Update global usage
    budget["current_token_usage"] = budget.get("current_token_usage", 0) + tokens
    
    # Read active profile
    profile_file = os.path.join(get_agents_dir(), 'active_api_profile_name')
    active_profile = "default"
    if os.path.exists(profile_file):
        with open(profile_file, 'r') as f:
            active_profile = f.read().strip()
            
    # Update profile usage
    profiles = budget.get("profiles", {})
    if active_profile not in profiles:
        profiles[active_profile] = {
            "current_token_usage": 0,
            "max_token_budget": 500000
        }
    profiles[active_profile]["current_token_usage"] = profiles[active_profile].get("current_token_usage", 0) + tokens
    
    budget["profiles"] = profiles
    save_budget(budget)
    
    # Calculate warning thresholds
    global_usage = budget["current_token_usage"]
    global_limit = budget["max_token_budget"]
    pct = (global_usage / global_limit) * 100
    alert_threshold = budget.get("alert_threshold_percent", 90)
    
    print(f"Logged {tokens} tokens to profile '{active_profile}'.")
    print(f"  Active Profile Usage: {profiles[active_profile]['current_token_usage']} / {profiles[active_profile]['max_token_budget']}")
    print(f"  Global Usage: {global_usage} / {global_limit} ({pct:.1f}%)")
    
    if pct >= alert_threshold:
        print(f"\n[WARNING] Token usage has reached {pct:.1f}% of budget! Threshold is {alert_threshold}%.")
        print("Please wrap up your task, stage and commit completed tasks, and hand over.")

EOF

# Write .agents/scripts/cli/helper.py
write_template_safe ".agents/scripts/cli/helper.py" << 'EOF'
#!/usr/bin/env python3
import sys
import os

# Ensure the cli directory is in the import path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def show_help():
    print("==========================================================")
    print("  Antigravity Agent Core Helper CLI (Python Edition)")
    print("==========================================================")
    print("Usage: helper.py <command> [arguments...]")
    print("")
    print("Core Commands:")
    print("  menu              Launch the interactive helper dashboard menu")
    print("  lock              Acquire a module edit lock (transient lock)")
    print("  unlock            Release a module edit lock")
    print("  validate          Validate workspace compliance, budget, and configurations")
    print("  doctor            Run complete diagnostic validation on the workspace")
    print("  migrate           Upgrade workspaces to V1.9.0 format")
    print("  push              Push local branch to remote repository securely")
    print("  clean             Purge workspace locks, archives, and reset memory/configs")
    print("  git-profile       Switch Git user config profiles locally")
    print("  api-profile       Switch API configurations locally (use 'rotate' to rotate)")
    print("  log-usage         Log token usage to budget tracker")
    print("  archive           Archive completed sprint checklists to history")
    print("  recon             Run autonomous codebase stack discovery")
    print("  list-skills       List all registered modular skills")
    print("  create-skill      Scaffold a new skill structure")
    print("  list-rules        List all project-specific blueprints and rules")
    print("  create-rule       Scaffold a new project rule blueprint")
    print("  init              Initialize a new workspace with template blueprints")
    print("  autocomplete      Output shell completion code (bash/zsh)")
    print("  adr-wizard        Interactive guided ADR wizard")
    print("  guide             Print step-by-step developer onboarding tutorial")
    print("==========================================================")
    print("Tip: Run 'helper.py guide' for a quick step-by-step developer tutorial!")
    print("==========================================================")

def main():
    if len(sys.argv) < 2:
        if sys.stdin.isatty():
            cmd = "menu"
        else:
            show_help()
            sys.exit(1)
    else:
        cmd = sys.argv[1]
        
    cmd_map = {
        "menu": "menu",
        "lock": "lock",
        "unlock": "lock",
        "validate": "validate",
        "doctor": "doctor",
        "migrate": "migrate",
        "push": "push",
        "clean": "clean",
        "git-profile": "git_profile",
        "api-profile": "api_profile",
        "log-usage": "log_usage",
        "archive": "archive",
        "recon": "recon",
        "list-skills": "skills",
        "create-skill": "skills",
        "list-rules": "rules",
        "create-rule": "rules",
        "init": "init",
        "commit": "commit",
        "sync-git": "sync_git",
        "build": "build",
        "lint": "lint",
        "test": "test",
        "sync-api": "sync_api",
        "create-adr": "create_adr",
        "adr-wizard": "adr_wizard",
        "release": "release",
        "autocomplete": "autocomplete",
        "guide": "guide"
    }
    
    if cmd not in cmd_map:
        print(f"Unknown command: '{cmd}'", file=sys.stderr)
        show_help()
        sys.exit(1)
        
    module_name = cmd_map[cmd]
    try:
        # Import the command module dynamically
        cmd_module = __import__(f"commands.{module_name}", fromlist=[module_name])
        # Execute the module's main function
        if cmd == "menu" and len(sys.argv) < 2:
            cmd_module.run(["menu"])
        else:
            cmd_module.run(sys.argv[1:])
    except ImportError as e:
        print(f"Failed to load command '{cmd}': {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error executing command '{cmd}': {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

EOF

# Write helper.ps1 wrapper script
write_template_safe ".agents/scripts/helper.ps1" << 'EOF'
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$helperPy = Join-Path $scriptPath "cli" "helper.py"

$projectRoot = Split-Path -Parent (Split-Path -Parent $scriptPath)
$venvPython1 = Join-Path $projectRoot ".venv" "Scripts" "python.exe"
$venvPython2 = Join-Path $projectRoot ".venv" "bin" "python"
$venvPython3 = Join-Path $projectRoot ".venv" "bin" "python3"

$pyCmd = ""
if (Test-Path $venvPython1) {
    $pyCmd = $venvPython1
} elseif (Test-Path $venvPython2) {
    $pyCmd = $venvPython2
} elseif (Test-Path $venvPython3) {
    $pyCmd = $venvPython3
} else {
    # Fallback to system Python
    if (Get-Command python3 -ErrorAction SilentlyContinue) {
        $pyCmd = "python3"
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        $pyVersion = & python -c 'import sys; print(sys.version_info[0])' 2>$null
        if ($pyVersion -eq "3") {
            $pyCmd = "python"
        } else {
            Write-Error "Error: Python 3 is required to run the Antigravity helper CLI. Please install Python 3 and ensure it is in your PATH."
            exit 1
        }
    } else {
        Write-Error "Error: Python 3 is required to run the Antigravity helper CLI. Please install Python 3 and ensure it is in your PATH."
        exit 1
    }
}

& $pyCmd $helperPy $args

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

PROJECT_RULES_FILE=".agents/rules/project_rules.md"
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

# Detect if monorepo or multi-project structure (e.g., apps/backend + apps/frontend)
if [ -f pnpm-workspace.yaml ] || [ -f turbo.json ] || [ -f lerna.json ] || [ -f go.work ] || ( [ -f package.json ] && grep -q '"workspaces"' package.json ) || ( [ -f Cargo.toml ] && grep -q "\[workspace\]" Cargo.toml ); then
    IS_MONOREPO=true
else
    # Fallback scan for folders under apps/, packages/, or services/ containing project signatures
    for check_dir in apps/* packages/* services/*; do
        if [ -d "$check_dir" ] && ( [ -f "$check_dir/package.json" ] || [ -f "$check_dir/go.mod" ] || [ -f "$check_dir/requirements.txt" ] || [ -f "$check_dir/pyproject.toml" ] || [ -f "$check_dir/composer.json" ] || [ -f "$check_dir/Gemfile" ] ); then
            IS_MONOREPO=true
            break
        fi
    done
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

# 5. Populate .agents/rules/project_rules.md
write_recon_file_safe "$PROJECT_RULES_FILE" << PAB_EOF
---
name: project-rules
activation: Always On
description: "Project architecture blueprint and technical stack rules."
---

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
- **Autonomous Bootstrapping Sequence**: Before performing any edit or script action, you MUST read the core files in sequence: \`AGENTS.md\`, \`.agents/rules/project_rules.md\`, \`.agents/schema.md\`, and \`.agents/memory.md\`. No file writes or terminal runs are allowed prior to this initialization.
- **Workspace Git Tracking**: Never ignore \`.agents/\` or \`AGENTS.md\` in \`.gitignore\` (except \`.agents/locks/\`). Commit all memory, schemas, dynamic workflows, and ADR files to Git to ensure proper multi-agent synchronization.
- **Upstream Sync Gate**: You must run \`./.agents/scripts/helper.sh validate\` before beginning code changes to check if the branch is behind origin. If it is behind, stop and ask the user to pull first.
- **Discussion and Design Plans**: Document all \`/grill-me\` outcomes and execution plans under \`.agents/workflows/task_<task_name>.md\`. Never log task-specific plans or checklists globally or in the main memory ledger.
- **Real-Time Schema & Dependency Updates**: Any discussion on database models, API routes, or third-party libraries must be documented in the repository *immediately* before starting code edits:
  - Database structures must be saved under \`.agents/schemas/\` and registered in \`.agents/schema.md\`.
  - Technologies/libraries must be documented in \`.agents/rules/project_rules.md\` and their respective workspace configuration files (\`package.json\`, \`go.mod\`, etc.).
  - Architectural decisions must be documented as a new ADR entry in \`.agents/adr.md\`.
- **Strict Checklist Checkbox Rules**: Checklists must follow a strict 3-state lifecycle. Only ONE task can be marked \`[/]\` at a time across the entire workspace. Do not change a task checklist state to \`[x]\` until verification has passed and the changes have been staged and committed in the completed state.
- **Handover Relayed Context**: Before logging off or ending a turn, you MUST write concise handover notes (under 5 lines) in the active memory ledger under \`## 3. Relayed Context & Handover Notes\`. This ensures any incoming agent or new account knows exactly where to resume work without token waste.

## 7. Autonomous Operational Scripts & Commands
The agent must execute workspace scripts automatically without manual user guidance or request under the following conditions:
- **Project Discovery**: If \`.agents/rules/project_rules.md\` is empty or generic, run \`./.agents/scripts/helper.sh recon\` immediately.
- **Initial Verification**: Run \`./.agents/scripts/helper.sh validate\` and \`./.agents/scripts/helper.sh doctor\` as the first step of any edit cycle.
- **Module Lock**: Before editing any code within a directory (e.g. \`apps/backend\`), run \`./.agents/scripts/helper.sh lock <module_name>\`.
- **API Synchronization**: When backend model schemas or API paths change, run \`./.agents/scripts/helper.sh sync-api\` to sync types to the frontend.
- **Code Validation**: Run \`./.agents/scripts/helper.sh validate\` before staging and preparing any commit.
- **Pre-Merge Cleanup**: Run \`./.agents/scripts/helper.sh archive\` before completing a pull request task to clean up dynamic workspaces.
- **Token Budget Compliance**: The agent must log its token usage using \`./.agents/scripts/helper.sh log-usage <token_count>\` at the end of each turn. If validation warns that token usage has reached the threshold, the agent must immediately save its progress, update the task checklist target in \`memory.md\` to \`IN_PROGRESS\`, and log off for handover.
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

# Color Definitions (TTY-aware)
if [ -t 1 ]; then
    RED='\033[91m'
    GREEN='\033[92m'
    YELLOW='\033[93m'
    BLUE='\033[94m'
    CYAN='\033[96m'
    BOLD='\033[1m'
    NC='\033[0m'
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    CYAN=''
    BOLD=''
    NC=''
fi

# Override echo to support colors dynamically
echo() {
    local msg="$*"
    if [ -t 1 ]; then
        msg="${msg//\[PASS\]/[${GREEN}${BOLD}PASS${NC}]}"
        msg="${msg//\[WARNING\]/[${YELLOW}${BOLD}WARNING${NC}]}"
        msg="${msg//\[FAIL\]/[${RED}${BOLD}FAIL${NC}]}"
        if [[ "$msg" =~ ^Check\ [0-9]+: ]]; then
            msg="${msg/Check /${CYAN}${BOLD}Check }"
            msg="${msg/: /:${NC} }"
        fi
        if [[ "$msg" == "Starting Antigravity Agent Workspace Validation..." ]]; then
            msg="${CYAN}${BOLD}${msg}${NC}"
        fi
        if [[ "$msg" == "Workspace Status:"* ]]; then
            if [[ "$msg" == *"VALIDATED"* ]]; then
                msg="${msg/VALIDATED/${GREEN}${BOLD}VALIDATED${NC}}"
            else
                msg="${msg/DEGRADED/${RED}${BOLD}DEGRADED${NC}}"
            fi
        fi
    fi
    command echo -e "$msg"
}

MEMORY_FILE=".agents/memory.md"
LOCKS_DIR=".agents/locks"
PROJECT_RULES=".agents/rules/project_rules.md"

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
    -not -path './venv/*' \
    -not -path './env/*' \
    -not -path './target/*' \
    -not -path './vendor/*' \
    -not -path './out/*' \
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
JS_FILES=$(find . \( -name "*.js" -o -name "*.ts" -o -name "*.tsx" \) -not -path './.agents/*' -not -path './node_modules/*' -not -path './dist/*' -not -path './venv/*' -not -path './env/*' -not -path './target/*' -not -path './vendor/*' -not -path './out/*' 2>/dev/null || true)
if [ -n "$JS_FILES" ]; then
    # Look for process.env.something, but ignore common config and test folders
    raw_js_env=$(echo "$JS_FILES" | grep -v "config" | grep -v "test" | xargs grep -rn "process\.env\.[A-Za-z0-9_]" 2>/dev/null || true)
    if [ -n "$raw_js_env" ]; then
        echo "  [WARNING] Raw 'process.env' access found outside configuration modules:"
        echo "$raw_js_env" | sed 's/^/    /'
        RAW_ENV_FOUND=1
    fi
fi

GO_FILES=$(find . -name "*.go" -not -path './.agents/*' -not -path './vendor/*' -not -path './venv/*' -not -path './env/*' 2>/dev/null || true)
if [ -n "$GO_FILES" ]; then
    raw_go_env=$(echo "$GO_FILES" | grep -v "config" | grep -v "test" | xargs grep -rn "os\.Getenv" 2>/dev/null || true)
    if [ -n "$raw_go_env" ]; then
        echo "  [WARNING] Raw 'os.Getenv' access found outside configuration modules:"
        echo "$raw_go_env" | sed 's/^/    /'
        RAW_ENV_FOUND=1
    fi
fi

PY_FILES=$(find . -name "*.py" -not -path './.agents/*' -not -path './venv/*' -not -path './env/*' 2>/dev/null || true)
if [ -n "$PY_FILES" ]; then
    raw_py_env=$(echo "$PY_FILES" | grep -v "config" | grep -v "test" | xargs grep -rnE "os\.(environ|getenv|environ\.get)\b" 2>/dev/null || true)
    if [ -n "$raw_py_env" ]; then
        echo "  [WARNING] Raw 'os.environ/os.getenv' access found outside configuration modules:"
        echo "$raw_py_env" | sed 's/^/    /'
        RAW_ENV_FOUND=1
    fi
fi

if [ "$RAW_ENV_FOUND" -eq 0 ]; then
    echo "  [PASS] Domain isolation looks healthy (no scattered raw env reads)."
fi

# 5. Check Git Upstream Synchronization
echo "Check 5: Git Upstream Synchronization Check"
# Attempt to fetch upstream changes silently to check sync state (gracefully handle failures/offline)
# Use a pure Bash background process watchdog to enforce a strict 5-second timeout and prevent hanging.
if git remote | grep -q "^origin$"; then
    (
        GIT_TERMINAL_PROMPT=0 GIT_SSH_COMMAND="ssh -o BatchMode=yes" git -c transfer.timeout=5 fetch origin >/dev/null 2>&1 &
        cmd_pid=$!
        (
            sleep 5
            kill -0 "$cmd_pid" 2>/dev/null && kill -9 "$cmd_pid" 2>/dev/null || true
        ) &
        watchdog_pid=$!
        wait "$cmd_pid" 2>/dev/null || true
        kill -9 "$watchdog_pid" 2>/dev/null || true
    ) || true
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

# 7. Check Gitignore & Antigravityignore Configuration Compliance
echo "Check 7: Gitignore & Antigravityignore Compliance"
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

    # Auto-heal transient files ignore in .gitignore
    HEALED_GI=0
    for pattern in ".agents/locks/" ".agents/api_keys" ".agents/active_api_keys" ".agents/active_api_keys.ps1" ".agents/active_api_profile_name" ".agents/cooldowns.json"; do
        if ! grep -q "^$pattern" .gitignore; then
            echo "  [WARNING] .gitignore does not ignore transient: '$pattern'. Auto-healing..."
            echo "$pattern" >> .gitignore
            HEALED_GI=1
        fi
    done
    if [ $HEALED_GI -eq 1 ]; then
        echo "  [PASS] .gitignore auto-healed successfully."
    fi
else
    echo "  [WARNING] No .gitignore file found in project root."
fi

if [ -f ".antigravityignore" ]; then
    # Auto-heal transient files ignore in .antigravityignore
    HEALED_AG=0
    for pattern in ".agents/locks/" ".agents/api_keys" ".agents/active_api_keys" ".agents/active_api_keys.ps1" ".agents/active_api_profile_name" ".agents/cooldowns.json"; do
        if ! grep -q "^$pattern" .antigravityignore; then
            echo "  [WARNING] .antigravityignore does not ignore transient: '$pattern'. Auto-healing..."
            echo "$pattern" >> .antigravityignore
            HEALED_AG=1
        fi
    done
    if [ $HEALED_AG -eq 1 ]; then
        echo "  [PASS] .antigravityignore auto-healed successfully."
    fi
fi

if [ "$GITIGNORE_ERRORS" -eq 0 ]; then
    echo "  [PASS] Gitignore & Antigravityignore configurations are validated."
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

# 9. Check Token Budget Guard
echo "Check 9: Token Budget Guard"
BUDGET_FILE=".agents/token_budget.json"
if command -v python3 >/dev/null 2>&1; then
    python3 -c "import sys; sys.path.insert(0, '.agents/scripts/cli'); import utils; utils.load_budget()" || true
fi
if [ -f "$BUDGET_FILE" ] && command -v jq >/dev/null 2>&1; then
    # Auto-detect profile from active_api_profile_name
    PROFILE=""
    if [ -f ".agents/active_api_profile_name" ]; then
        PROFILE=$(cat ".agents/active_api_profile_name" | xargs)
    fi

    # Check if profile exists in profiles
    HAS_PROFILE=0
    if [ -n "$PROFILE" ]; then
        if jq -e --arg prof "$PROFILE" '.profiles[$prof] != null' "$BUDGET_FILE" >/dev/null 2>&1; then
            HAS_PROFILE=1
        fi
    fi

    MAX_BUDGET=0
    CURRENT_USAGE=0
    THRESHOLD=$(jq -r '.alert_threshold_percent // 90' "$BUDGET_FILE")

    if [ $HAS_PROFILE -eq 1 ]; then
        MAX_BUDGET=$(jq -r --arg prof "$PROFILE" '.profiles[$prof].max_token_budget // 0' "$BUDGET_FILE")
        CURRENT_USAGE=$(jq -r --arg prof "$PROFILE" '.profiles[$prof].current_token_usage // 0' "$BUDGET_FILE")
        echo "  Checking budget for active API profile: '$PROFILE'"
    else
        MAX_BUDGET=$(jq -r '.max_token_budget // 0' "$BUDGET_FILE")
        CURRENT_USAGE=$(jq -r '.current_token_usage // 0' "$BUDGET_FILE")
        echo "  Checking global token budget"
    fi
    
    if [ "$MAX_BUDGET" -gt 0 ]; then
        PERCENT=$(( CURRENT_USAGE * 100 / MAX_BUDGET ))
        echo "  Current token usage: $CURRENT_USAGE / $MAX_BUDGET ($PERCENT%)"
        if [ "$CURRENT_USAGE" -ge "$MAX_BUDGET" ]; then
            echo "  [FAIL] Token budget exceeded! Current: $CURRENT_USAGE, Limit: $MAX_BUDGET."
            echo "         Please save your task checkpoint in workflows/ and handover the task."
            FAILED=1
        elif [ "$PERCENT" -ge 95 ]; then
            echo "  [FAIL] Token usage has reached critical threshold ($PERCENT% >= 95%)! All operations blocked."
            echo "         Please request a budget increase or manually reset the usage log."
            FAILED=1
        elif [ "$PERCENT" -ge "$THRESHOLD" ]; then
            echo "  [WARNING] Token usage is at $PERCENT% of budget. Consider saving and handing over."
        else
            echo "  [PASS] Token usage is within safe budget limits."
        fi
    fi
else
    echo "  [PASS] No active token budget file or jq tool found. Bypassing check."
fi

# 10. Check ADR Compliance Check
echo "Check 10: ADR Compliance Check"
ADR_ERRORS=0
if [ -f ".agents/adr.md" ]; then
    if [ -d ".agents/adrs" ]; then
        max_num=0
        for adr_file in .agents/adrs/*.md; do
            if [ -f "$adr_file" ]; then
                base_name=$(basename "$adr_file")
                # Verify registration in adr.md
                if ! grep -q "$base_name" ".agents/adr.md"; then
                    echo "  [FAIL] Architectural Decision Record file '$base_name' is NOT registered in '.agents/adr.md'!"
                    ADR_ERRORS=$((ADR_ERRORS + 1))
                fi
                # Check for placeholders and template defaults
                if grep -i -q -E "TODO|FIXME|\[placeholder\]|Describe the problem|Describe the decision|Describe the result" "$adr_file"; then
                    echo "  [FAIL] ADR file '$base_name' contains placeholder text (TODO/FIXME/placeholder/template default)!"
                    ADR_ERRORS=$((ADR_ERRORS + 1))
                fi
                # Check for required sections
                if ! grep -q "## Context" "$adr_file" || ! grep -q "## Decision" "$adr_file" || ! grep -q "## Consequences" "$adr_file"; then
                    echo "  [FAIL] ADR file '$base_name' is missing required sections (Context, Decision, Consequences)!"
                    ADR_ERRORS=$((ADR_ERRORS + 1))
                fi
                
                # Extract sequence number to check for gaps later
                if [[ "$base_name" =~ ^([0-9]{3})- ]]; then
                    num=$((10#${BASH_REMATCH[1]}))
                    if [ "$num" -gt "$max_num" ]; then
                        max_num=$num
                    fi
                fi
            fi
        done
        
        # Gaps check
        if [ "$max_num" -gt 0 ]; then
            for ((i=1; i<=max_num; i++)); do
                padded_num=$(printf "%03d" $i)
                found=0
                for f in .agents/adrs/${padded_num}-*.md; do
                    if [ -e "$f" ]; then
                        found=1
                        break
                    fi
                done
                if [ "$found" -eq 0 ]; then
                    echo "  [FAIL] Missing ADR in sequence: ADR-${padded_num} is not found!"
                    ADR_ERRORS=$((ADR_ERRORS + 1))
                fi
            done
        fi
        
        # Bidirectional sync: check if registered files in adr.md actually exist
        links=$(grep -o -E "file://\./adrs/[^)]+\.md" ".agents/adr.md" | sed 's|file://./||' || true)
        for link in $links; do
            if [ ! -f ".agents/$link" ]; then
                echo "  [FAIL] ADR index references non-existent file '.agents/$link'!"
                ADR_ERRORS=$((ADR_ERRORS + 1))
            fi
        done
    fi
else
    echo "  [FAIL] Primary ADR index '.agents/adr.md' is missing!"
    ADR_ERRORS=$((ADR_ERRORS + 1))
fi

if [ "$ADR_ERRORS" -eq 0 ]; then
    echo "  [PASS] All Architectural Decision Records are correctly indexed and complete."
else
    FAILED=1
fi

# 11. Check Git Configuration & Profile Compliance
echo "Check 11: Git Configuration & Profile Compliance"
GIT_ERRORS=0
PROFILES_FILE=".agents/git_profiles"
if [ -f "$PROFILES_FILE" ]; then
    # Verify profiles syntax and check for missing names/emails
    while IFS= read -r line || [ -n "$line" ]; do
        # Ignore comments and empty lines
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ "$line" =~ ^[[:space:]]*$ ]] && continue
        
        # Check if the line is a valid key-value pair
        if [[ "$line" =~ ^([a-zA-Z0-9_\-]+)\.(name|email|ssh_key)=(.*)$ ]]; then
            key="${BASH_REMATCH[1]}"
            prop="${BASH_REMATCH[2]}"
            val="${BASH_REMATCH[3]}"
            
            # Check for dummy/placeholder emails in defined profiles
            if [ "$prop" = "email" ]; then
                if [[ "$val" =~ ^(work@company\.com|personal@gmail\.com|side@project\.com)$ ]]; then
                    echo "  [WARNING] Profile '$key' uses a default template email: '$val'."
                fi
            fi
            
            # Verify if SSH key file path exists if specified
            if [ "$prop" = "ssh_key" ] && [ -n "$val" ]; then
                resolved_key="$val"
                if [[ "$resolved_key" == \~/* ]]; then
                    resolved_key="${resolved_key/\~/$HOME}"
                fi
                if [ ! -f "$resolved_key" ]; then
                    echo "  [WARNING] Profile '$key' specifies an SSH key file that does not exist: '$val'."
                fi
            fi
        fi
    done < "$PROFILES_FILE"
fi

local_name=$(git config --local user.name 2>/dev/null || echo "")
local_email=$(git config --local user.email 2>/dev/null || echo "")
if [ -n "$local_name" ] && [ -n "$local_email" ]; then
    # Warn if local config is a generic template
    if [[ "$local_email" =~ ^(work@company\.com|personal@gmail\.com|side@project\.com)$ ]]; then
        echo "  [WARNING] Local Git config user.email uses a placeholder email: '$local_email'."
    fi
fi

if [ "$GIT_ERRORS" -eq 0 ]; then
    echo "  [PASS] Git configurations and profiles are validated."
else
    FAILED=1
fi

# 12. Check API Configuration & Profile Compliance
echo "Check 12: API Configuration & Profile Compliance"
API_ERRORS=0
API_KEYS_FILE=".agents/api_keys"
if [ -f "$API_KEYS_FILE" ]; then
    # Verify profiles syntax and check for placeholder values
    while IFS= read -r line || [ -n "$line" ]; do
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ "$line" =~ ^[[:space:]]*$ ]] && continue
        
        if [[ "$line" =~ ^([a-zA-Z0-9_\-]+)\.([A-Z0-9_]+)=(.*)$ ]]; then
            key="${BASH_REMATCH[1]}"
            prop="${BASH_REMATCH[2]}"
            val="${BASH_REMATCH[3]}"
            
            if [[ "$val" =~ _key_here$ ]] || [ "$val" = "your_api_key_here" ]; then
                echo "  [WARNING] API Profile '$key' uses a placeholder value for '$prop': '$val'."
            fi
        else
            echo "  [FAIL] Invalid syntax in $API_KEYS_FILE: '$line'. Must be in format: profile.VARIABLE_NAME=value"
            API_ERRORS=$((API_ERRORS + 1))
        fi
    done < "$API_KEYS_FILE"
fi

# Ensure secrets and active state files are in .gitignore
if [ -f ".gitignore" ]; then
    for ignore_pattern in ".agents/api_keys" ".agents/active_api_keys" ".agents/active_api_keys.ps1" ".agents/active_api_profile_name"; do
        if ! grep -q "^$ignore_pattern" .gitignore; then
            echo "  [FAIL] .gitignore compliance: '$ignore_pattern' is not ignored. Please add it to your .gitignore to protect credentials."
            API_ERRORS=$((API_ERRORS + 1))
        fi
    done
fi

if [ "$API_ERRORS" -eq 0 ]; then
    echo "  [PASS] API configurations and profiles are validated and secure."
else
    FAILED=1
fi

# 13. Check CHANGELOG.md Format (Keep a Changelog Compliance)
echo "Check 13: Keep a Changelog Compliance"
CHANGELOG_ERRORS=0
if [ -f "CHANGELOG.md" ]; then
    if ! head -n 1 CHANGELOG.md | grep -q "^# Changelog" ; then
        echo "  [FAIL] CHANGELOG.md must start with '# Changelog' header."
        CHANGELOG_ERRORS=$((CHANGELOG_ERRORS + 1))
    fi
    INVALID_HEADERS=$(grep "^## " CHANGELOG.md | grep -Ev "^## \[(Unreleased|[0-9]+\.[0-9]+\.[0-9]+)\]( - [0-9]{4}-[0-9]{2}-[0-9]{2})?" || true)
    if [ -n "$INVALID_HEADERS" ]; then
        echo "  [FAIL] CHANGELOG.md contains invalid version headers:"
        echo "$INVALID_HEADERS" | sed 's/^/         /'
        CHANGELOG_ERRORS=$((CHANGELOG_ERRORS + 1))
    fi
else
    echo "  [WARNING] No CHANGELOG.md file found in project root."
fi

if [ "$CHANGELOG_ERRORS" -eq 0 ]; then
    echo "  [PASS] CHANGELOG.md matches Keep a Changelog compliance."
else
    FAILED=1
fi

# 14. Check for TODO/FIXME Annotations in Staged Code
echo "Check 14: Staged Code Quality (TODO/FIXME Guard)"
TODO_ERRORS=0
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    # Get staged files excluding .md files, bootstrap.sh, and files inside .agents/
    STAGED_CODE_FILES=$(git diff --cached --name-only | grep -Ev "\.md$" | grep -v "^bootstrap\.sh$" | grep -Ev "^\.agents/" || true)
    for file in $STAGED_CODE_FILES; do
        TODO_LINES=$(git diff --cached -- "$file" | grep "^+[^+]" | grep -Ei "\b(TODO|FIXME)\b" || true)
        if [ -n "$TODO_LINES" ]; then
            echo "  [FAIL] Quality Guard: Staged file '$file' contains TODO or FIXME annotations:"
            echo "$TODO_LINES" | sed 's/^/         /'
            TODO_ERRORS=$((TODO_ERRORS + 1))
        fi
    done
fi

if [ "$TODO_ERRORS" -eq 0 ]; then
    echo "  [PASS] Staged changes contain no TODO or FIXME annotations."
else
    FAILED=1
fi

# 15. Check for Staged Transient Files & Config Leak Guard
echo "Check 15: Staged Transient Files & Leak Guard"
LEAK_ERRORS=0
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    STAGED_FILES=$(git diff --cached --name-only)
    for file in $STAGED_FILES; do
        if [[ "$file" =~ \.lock$ ]] || [[ "$file" =~ active_api_keys ]] || [[ "$file" =~ cooldowns\.json$ ]]; then
            echo "  [FAIL] Leak Guard: Transient file '$file' is staged for commit! Please unstage it."
            LEAK_ERRORS=$((LEAK_ERRORS + 1))
        fi
    done
fi

if [ "$LEAK_ERRORS" -eq 0 ]; then
    echo "  [PASS] No transient files or credentials are staged."
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

# Write .agents/scripts/api-rotate-wrapper.sh
write_template_safe ".agents/scripts/api-rotate-wrapper.sh" << 'EOF'
#!/usr/bin/env bash
# Antigravity API Auto-Rotation Command Wrapper
# Wraps execution of any agent CLI or command, automatically rotating API profiles 
# from '.agents/api_keys' if the command fails with a rate-limit error (exit code 429).
set -uo pipefail

# Find the helper script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HELPER_SH="${SCRIPT_DIR}/helper.sh"

if [ $# -lt 1 ]; then
    echo "Usage: $0 [command_to_run] [args...]" >&2
    echo "Example: $0 npx antigravity-cli task-run" >&2
    exit 1
fi

# Find available API profiles to count max retries
API_KEYS_FILE=""
if [ -f ".agents/api_keys" ]; then
    API_KEYS_FILE=".agents/api_keys"
elif [ -f "$HOME/.antigravity_api_keys" ]; then
    API_KEYS_FILE="$HOME/.antigravity_api_keys"
fi

MAX_RETRIES=1
if [ -n "$API_KEYS_FILE" ] && [ -f "$API_KEYS_FILE" ]; then
    num_profiles=$(grep -E "^[a-zA-Z0-9_\-]+\.[A-Z0-9_]+=" "$API_KEYS_FILE" | cut -d'.' -f1 | sort -u | wc -l || echo "1")
    if [ "$num_profiles" -gt 0 ]; then
        MAX_RETRIES=$num_profiles
    fi
fi

retry_count=0
while [ $retry_count -lt $MAX_RETRIES ]; do
    # Ensure active API keys are loaded
    if [ -f ".agents/active_api_keys" ]; then
        source ".agents/active_api_keys"
    else
        # If no profile is active, initialize the first available profile
        echo "No active API profile set. Initializing first available profile..."
        "$HELPER_SH" api-profile rotate >/dev/null 2>&1 || true
        if [ -f ".agents/active_api_keys" ]; then
            source ".agents/active_api_keys"
        fi
    fi

    # Run the wrapped command
    echo "[API-WRAPPER] Running wrapped command..."
    # Disable exit on error temporarily so we can catch exit code
    set +e
    "$@"
    exit_code=$?
    set -e

    if [ $exit_code -eq 0 ]; then
        exit 0
    # Catch typical rate limit / exhaustion codes: 
    # - 429: Too Many Requests
    # - 129: Common custom agent rate-limit exit code
    # - 3: Resource exhausted (gRPC status code)
    elif [ $exit_code -eq 429 ] || [ $exit_code -eq 129 ] || [ $exit_code -eq 173 ] || [ $exit_code -eq 3 ]; then
        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $MAX_RETRIES ]; then
            echo "[API-WRAPPER] Command exited with code $exit_code (Rate Limited/Quota Exhausted)."
            echo "[API-WRAPPER] Rotating API profile and retrying ($retry_count/$MAX_RETRIES)..."
            "$HELPER_SH" api-profile rotate --rate-limited
            sleep 1
        else
            echo "[API-WRAPPER] Command exited with code $exit_code. All available API profiles exhausted." >&2
            exit $exit_code
        fi
    else
        # Exit immediately on other execution failures
        exit $exit_code
    fi
done

EOF

# Write .agents/scripts/api-rotate-wrapper.ps1
write_template_safe ".agents/scripts/api-rotate-wrapper.ps1" << 'EOF'
# Antigravity API Auto-Rotation Command Wrapper for Windows PowerShell
# Wraps execution of any PowerShell script or command, automatically rotating API profiles 
# from '.agents/api_keys' if the command fails with a rate-limit error (exit code 429).
param(
    [Parameter(Mandatory=$true, ValueFromRemainingArguments=$true)]
    [string[]]$Command
)

# Find the helper script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$helperPs1 = Join-Path $scriptPath "helper.ps1"

# Find available API profiles to count max retries
$apiKeysFile = ""
if (Test-Path ".agents/api_keys") {
    $apiKeysFile = ".agents/api_keys"
} elseif (Test-Path "$HOME/.antigravity_api_keys") {
    $apiKeysFile = "$HOME/.antigravity_api_keys"
}

$maxRetries = 1
if ($apiKeysFile -and (Test-Path $apiKeysFile)) {
    # Count unique profiles from key prefix (e.g. name.VAR=val)
    $profiles = Get-Content $apiKeysFile | Where-Object { $_ -match '^[a-zA-Z0-9_\-]+\.[A-Z0-9_]+=' } | ForEach-Object {
        $_.Split('.')[0].Trim()
    } | Select-Object -Unique
    if ($profiles) {
        $maxRetries = @($profiles).Count
    }
}

$retryCount = 0
$success = $false

while ($retryCount -lt $maxRetries) {
    # Ensure active API keys are loaded in current process env
    $activeKeysFile = Join-Path (Split-Path $scriptPath) "active_api_keys.ps1"
    if (Test-Path $activeKeysFile) {
        . $activeKeysFile
    } else {
        # If no profile is active, initialize the first available profile
        Write-Host "No active API profile set. Initializing first available profile..."
        & $helperPs1 api-profile rotate | Out-Null
        if (Test-Path $activeKeysFile) {
            . $activeKeysFile
        }
    }

    Write-Host "[API-WRAPPER] Running wrapped command..."
    
    # Disable exit on error behavior during execution
    $exitCode = 0
    try {
        if ($Command.Count -gt 1) {
            & $Command[0] $Command[1..($Command.Count - 1)]
        } else {
            & $Command[0]
        }
        $exitCode = $LASTEXITCODE
    } catch {
        Write-Warning "Failed to execute command: $_"
        $exitCode = 1
    }

    if ($exitCode -eq 0 -or $null -eq $exitCode) {
        exit 0
    # Catch typical rate limit / exhaustion codes: 
    # - 429: Too Many Requests
    # - 129: Common custom agent rate-limit exit code
    # - 3: Resource exhausted (gRPC status code)
    } elseif ($exitCode -eq 429 -or $exitCode -eq 129 -or $exitCode -eq 173 -or $exitCode -eq 3) {
        $retryCount++
        if ($retryCount -lt $maxRetries) {
            Write-Warning "[API-WRAPPER] Command exited with code $exitCode (Rate Limited/Quota Exhausted)."
            Write-Host "[API-WRAPPER] Rotating API profile and retrying ($retryCount/$maxRetries)..."
            & $helperPs1 api-profile rotate --rate-limited
            Start-Sleep -Seconds 1
        } else {
            Write-Error "[API-WRAPPER] Command exited with code $exitCode. All available API profiles exhausted."
            exit $exitCode
        }
    } else {
        # Exit immediately on other execution failures
        exit $exitCode
    }
}

EOF

# 11.5. Write generate-client.js script
write_template_safe ".agents/scripts/generate-client.js" << 'CLIENT_GEN_EOF'
const fs = require('fs');
const path = require('path');

const openapiPath = process.argv[2];
const outputPath = process.argv[3];

if (!openapiPath || !outputPath) {
  console.error("Usage: node generate-client.js <openapi.json> <output.ts>");
  process.exit(1);
}

if (!fs.existsSync(openapiPath)) {
  console.error(`Error: openapi file not found at ${openapiPath}`);
  process.exit(1);
}

const schema = JSON.parse(fs.readFileSync(openapiPath, 'utf8'));
let code = `/**
 * Auto-generated API client by Antigravity Agent Core.
 * DO NOT EDIT DIRECTLY.
 */

`;

const baseUrl = schema.servers && schema.servers[0] ? schema.servers[0].url : '/';

function mapType(prop) {
  if (!prop) return 'any';
  if (prop.$ref) {
    return prop.$ref.split('/').pop();
  }
  if (prop.type === 'array') {
    return `${mapType(prop.items)}[]`;
  }
  if (prop.type === 'string') return 'string';
  if (prop.type === 'integer' || prop.type === 'number') return 'number';
  if (prop.type === 'boolean') return 'boolean';
  if (prop.type === 'object') {
    if (prop.properties) {
      let sub = '{ ';
      for (const [k, v] of Object.entries(prop.properties)) {
        const req = prop.required && prop.required.includes(k) ? '' : '?';
        sub += `${k}${req}: ${mapType(v)}; `;
      }
      sub += '}';
      return sub;
    }
    return 'Record<string, any>';
  }
  return 'any';
}

if (schema.components && schema.components.schemas) {
  for (const [name, definition] of Object.entries(schema.components.schemas)) {
    code += `export interface ${name} {\n`;
    if (definition.properties) {
      for (const [propName, propDef] of Object.entries(definition.properties)) {
        const required = definition.required && definition.required.includes(propName) ? '' : '?';
        code += `  ${propName}${required}: ${mapType(propDef)};\n`;
      }
    }
    code += `}\n\n`;
  }
}

code += `export class APIClient {\n`;
code += `  private baseUrl: string;\n`;
code += `  private headers: Record<string, string>;\n\n`;
code += `  constructor(baseUrl: string = '${baseUrl}', headers: Record<string, string> = {}) {\n`;
code += `    this.baseUrl = baseUrl.replace(/\\/$/, '');\n`;
code += `    this.headers = {\n`;
code += `      'Content-Type': 'application/json',\n`;
code += `      ...headers\n`;
code += `    };\n`;
code += `  }\n\n`;
code += `  setToken(token: string) {\n`;
code += `    this.headers['Authorization'] = \`Bearer \${token}\`;\n`;
code += `  }\n\n`;

if (schema.paths) {
  for (const [pathStr, pathObj] of Object.entries(schema.paths)) {
    for (const [method, operation] of Object.entries(pathObj)) {
      if (!['get', 'post', 'put', 'delete', 'patch'].includes(method.toLowerCase())) continue;
      
      const operationId = operation.operationId || `${method}${pathStr.replace(/[^a-zA-Z0-9]/g, '_')}`;
      const cleanMethodName = operationId
        .replace(/_([a-z])/g, (g) => g[1].toUpperCase())
        .replace(/[^a-zA-Z0-9]/g, '')
        .replace(/^[A-Z]/, (c) => c.toLowerCase());
      
      const parameters = operation.parameters || [];
      const pathParams = parameters.filter(p => p.in === 'path');
      const queryParams = parameters.filter(p => p.in === 'query');
      
      let methodArgs = [];
      let pathInterpolation = pathStr;
      
      for (const p of pathParams) {
        methodArgs.push(`${p.name}: ${mapType(p)}`);
        pathInterpolation = pathInterpolation.replace(`{${p.name}}`, `\${${p.name}}`);
      }
      
      let hasBody = false;
      let bodyType = 'any';
      if (operation.requestBody) {
        hasBody = true;
        const content = operation.requestBody.content;
        if (content && content['application/json'] && content['application/json'].schema) {
          bodyType = mapType(content['application/json'].schema);
        }
        methodArgs.push(`body: ${bodyType}`);
      }
      
      let hasQuery = queryParams.length > 0;
      if (hasQuery) {
        let qType = '{ ';
        for (const q of queryParams) {
          const req = q.required ? '' : '?';
          qType += `${q.name}${req}: ${mapType(q)}; `;
        }
        qType += '}';
        methodArgs.push(`query?: ${qType}`);
      }
      
      let responseType = 'any';
      if (operation.responses && operation.responses['200'] && operation.responses['200'].content) {
        const content = operation.responses['200'].content;
        if (content['application/json'] && content['application/json'].schema) {
          responseType = mapType(content['application/json'].schema);
        }
      } else if (operation.responses && operation.responses['201'] && operation.responses['201'].content) {
        const content = operation.responses['201'].content;
        if (content['application/json'] && content['application/json'].schema) {
          responseType = mapType(content['application/json'].schema);
        }
      }

      code += `  async ${cleanMethodName}(${methodArgs.join(', ')}): Promise<${responseType}> {\n`;
      
      if (hasQuery) {
        code += `    const queryParams = new URLSearchParams();\n`;
        code += `    if (query) {\n`;
        code += `      for (const [key, value] of Object.entries(query)) {\n`;
        code += `        if (value !== undefined && value !== null) {\n`;
        code += `          queryParams.append(key, String(value));\n`;
        code += `        }\n`;
        code += `      }\n`;
        code += `    }\n`;
        code += `    const queryString = queryParams.toString() ? \`?\${queryParams.toString()}\` : '';\n`;
      } else {
        code += `    const queryString = '';\n`;
      }
      
      code += `    const url = \`\${this.baseUrl}${pathInterpolation}\${queryString}\`;\n`;
      
      code += `    const options: RequestInit = {\n`;
      code += `      method: '${method.toUpperCase()}',\n`;
      code += `      headers: this.headers,\n`;
      if (hasBody) {
        code += `      body: JSON.stringify(body),\n`;
      }
      code += `    };\n\n`;
      
      code += `    const response = await fetch(url, options);\n`;
      code += `    if (!response.ok) {\n`;
      code += `      throw new Error(\`HTTP Error \${response.status}: \${response.statusText}\`);\n`;
      code += `    }\n`;
      code += `    return response.json();\n`;
      code += `  }\n\n`;
    }
  }
}

code += `}\n`;

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, code, 'utf8');
console.log(`Successfully generated API client with ${Object.keys(schema.components?.schemas || {}).length} types to ${outputPath}`);

CLIENT_GEN_EOF


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

if [ -f .agents/rules/project_rules.md ]; then
    linter_line=$(grep "Linter command" .agents/rules/project_rules.md || echo "")
    linter_cmd=$(echo "$linter_line" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^`//' -e 's/`$//')
    if [ -n "$linter_cmd" ] && [ "$linter_cmd" != "echo 'No linter found'" ]; then
        echo "Running linter: $linter_cmd..."
        if ! eval "$linter_cmd"; then
            echo "Error: Linter check failed! Aborting commit." >&2
            exit 1
        fi
        echo "  [PASS] Linter check passed."
    fi

    test_line=$(grep "Test runner command" .agents/rules/project_rules.md || echo "")
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
convention_regex="^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert|merge)(\([A-Za-z0-9_\/-]+\))?: .+$"

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
if [ -f .agents/skills/api-rotator/scripts/main.py ]; then chmod +x .agents/skills/api-rotator/scripts/main.py; fi
if [ -f .agents/scripts/api-rotate-wrapper.sh ]; then chmod +x .agents/scripts/api-rotate-wrapper.sh; fi
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

# Synchronize Git branch and commit reference to memory.md
if [ -f .agents/scripts/helper.sh ]; then
    .agents/scripts/helper.sh sync-git >/dev/null 2>&1 || true
fi

echo -e "${BLUE}==========================================================${NC}"
echo -e "${GREEN}${BOLD}🎉  Workspace Initialization Complete!${NC}"
echo -e "${BLUE}==========================================================${NC}"
echo -e "  ${GREEN}✓${NC} Global Agent Protocol written to:      ${CYAN}AGENTS.md${NC}"
echo -e "  ${GREEN}✓${NC} Active Memory Ledger written to:       ${CYAN}.agents/memory.md${NC}"
echo -e "  ${GREEN}✓${NC} Technical Schema Reference written to:  ${CYAN}.agents/schema.md${NC}"
echo -e "  ${GREEN}✓${NC} Architectural Blueprint written to:    ${CYAN}.agents/rules/project_rules.md${NC}"
echo -e "  ${GREEN}✓${NC} Architectural Decision Records to:     ${CYAN}.agents/adr.md${NC}"
echo -e "  ${GREEN}✓${NC} Locks folder created at:               ${CYAN}.agents/locks/${NC}"
echo -e "  ${GREEN}✓${NC} Schemas folder created at:             ${CYAN}.agents/schemas/${NC}"
echo -e "  ${GREEN}✓${NC} Helper Scripts created at:             ${CYAN}.agents/scripts/${NC}"
echo -e "  ${GREEN}✓${NC} Git Hooks created at:                  ${CYAN}.agents/hooks/${NC}"
echo -e "  ${GREEN}✓${NC} Generalized Skills loaded in:          ${CYAN}.agents/skills/${NC}"
echo -e "${BLUE}==========================================================${NC}"
echo -e "${YELLOW}${BOLD}🩺  Workspace Diagnostics Status:${NC}"
.agents/scripts/helper.sh doctor || true
echo -e "${BLUE}==========================================================${NC}"
echo -e "${CYAN}${BOLD}👉  To get started, launch the Interactive TUI Dashboard:${NC}"
echo -e "    ${BOLD}./.agents/scripts/helper.sh${NC}"
echo -e "${BLUE}==========================================================${NC}"

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

