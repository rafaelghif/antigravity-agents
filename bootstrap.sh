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
# 3. Write .agents/memory.md template
write_template_safe ".agents/memory.md" << 'EOF'
# Agent Core Memory

> **Memory Schema Version**: 5.0.0  
> **Target System**: [Project Name]
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
# Architectural Decision Records (ADR) - Index Map

This document registers the historical technical design decisions, rationales, and consequences accepted in this project.

---

## 1. Architectural Decisions Index
- [ADR-001: Initial Workspace Protocol Adoption](file://./adrs/001-initial-workspace-protocol.md) - Status: Accepted
EOF

# 7.2 Write .agents/adrs/001-initial-workspace-protocol.md template
write_template_safe ".agents/adrs/001-initial-workspace-protocol.md" << 'EOF'
# ADR-001: Initial Workspace Protocol Adoption

- **Date**: 2026-06-13
- **Status**: Accepted
- **Context**: The workspace needs a structured operational protocol for AI engineering agents to ensure version alignment, zero-hallucination execution, and high token efficiency.
- **Decision**: Adopt the Antigravity Agent Core (AAC) protocol, establishing `AGENTS.md` and the `.agents/` structure containing locks, rules, schemas, and active task memory ledgers.
- **Consequences**: Developers and agents must follow strict bootstrapping sequences and use the helper scripts/Git hooks for validated, atomic commits.
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
    echo "  sync-api          Synchronize API contracts and generate typed TypeScript client"
    echo "  create-skill      Scaffold a new specialized skill directory"
    echo "  list-skills       Audit and list all registered skills for compliance"
    echo "  create-rule       Scaffold a new workspace rule file under .agents/rules/"
    echo "  list-rules        Audit and list all workspace rules for compliance"
    echo "  log-usage         Log token usage stats to token_budget.json"
    echo "  release           Auto-increment version and scaffold next release in CHANGELOG.md"
    echo "  create-adr        Scaffold a new Architectural Decision Record under .agents/adrs/"
    echo "  git-profile [name] [email] Switch or display local repository Git user configuration"
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
        local build_line=$(grep "Build validation" .agents/rules/project_rules.md || echo "")
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
        local linter_line=$(grep "Linter command" .agents/rules/project_rules.md || echo "")
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
        local test_line=$(grep "Test runner command" .agents/rules/project_rules.md || echo "")
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
    local be_choice="1"
    local be_arch_choice="2"
    local fe_choice="1"
    local fe_arch_choice="2"
    local gen_docker=""

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
        echo "  [8] Custom Multi-Project / Separate Apps (e.g. apps/backend + apps/frontend)"
        echo "  [9] Laravel (PHP MVC Framework)"
        read -p "Select choice [1-9] (default: 1): " stack_choice
        case "$stack_choice" in
            2) tech_stack="Go Gin" ;;
            3) tech_stack="FastAPI" ;;
            4) tech_stack="Node/TypeScript" ;;
            5) tech_stack="Go" ;;
            6) tech_stack="Python" ;;
            7) tech_stack="Monorepo" ;;
            8) tech_stack="Multi-Project" ;;
            9) tech_stack="Laravel" ;;
            1|"") tech_stack="Next.js" ;;
            *) tech_stack="$stack_choice" ;;
        esac
    fi

    if [ "$tech_stack" = "Multi-Project" ]; then
        echo ""
        echo "--- Configure Backend Application ---"
        echo "  [1] NestJS (TypeScript)"
        echo "  [2] FastAPI (Python)"
        echo "  [3] Go Gin"
        echo "  [4] None"
        read -p "Select Backend Choice [1-4] (default: 1): " be_choice
        if [ -z "$be_choice" ]; then be_choice="1"; fi

        if [ "$be_choice" != "4" ]; then
            echo "Configure Backend Architecture:"
            echo "  [1] Hexagonal Architecture (Ports & Adapters)"
            echo "  [2] Clean Architecture"
            echo "  [3] Standard MVC / Modular"
            read -p "Select Architecture [1-3] (default: 2): " be_arch_choice
            if [ -z "$be_arch_choice" ]; then be_arch_choice="2"; fi
        fi

        echo ""
        echo "--- Configure Frontend Application ---"
        echo "  [1] Next.js (TypeScript)"
        echo "  [2] React SPA (Vite)"
        echo "  [3] Laravel Blade / PHP HTML"
        echo "  [4] None"
        read -p "Select Frontend Choice [1-4] (default: 1): " fe_choice
        if [ -z "$fe_choice" ]; then fe_choice="1"; fi

        if [ "$fe_choice" != "4" ]; then
            echo "Configure Frontend Architecture:"
            echo "  [1] Atomic Design"
            echo "  [2] Standard Components / App Router Layout"
            read -p "Select Architecture [1-2] (default: 2): " fe_arch_choice
            if [ -z "$fe_arch_choice" ]; then fe_arch_choice="2"; fi
        fi
        
        arch_pattern="Decoupled / Distributed Architecture"
        db_orm="None"
        env_vars="PORT"
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
    elif [ "$tech_stack" = "Laravel" ]; then
        default_arch="MVC"
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
    elif [ "$tech_stack" = "Laravel" ]; then
        default_env="APP_KEY,DB_CONNECTION,DB_DATABASE"
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

    if [ -z "${8:-}" ]; then
        read -p "Generate Dockerfiles and docker-compose.yml? (y/n) (default: y): " gen_docker
        if [ -z "$gen_docker" ]; then gen_docker="y"; fi
    else
        gen_docker="${8:-}"
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
            if [[ "$arch_pattern" =~ "Atomic" || "$arch_pattern" =~ "atomic" ]]; then
                mkdir -p src/app src/components/atoms src/components/molecules src/components/organisms src/components/templates src/lib tests
            elif [[ "$arch_pattern" =~ "Clean" || "$arch_pattern" =~ "clean" ]]; then
                mkdir -p src/app src/core/entities src/core/usecases src/infrastructure/db src/infrastructure/api src/lib tests
            else
                mkdir -p src/app src/components src/lib tests
            fi
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
            if [[ "$arch_pattern" =~ "Hexagonal" || "$arch_pattern" =~ "hexagonal" || "$arch_pattern" =~ "Ports" || "$arch_pattern" =~ "ports" ]]; then
                mkdir -p src/cmd/server src/internal/core/domain src/internal/core/ports src/internal/adapters/in/web src/internal/adapters/out/db src/internal/config tests
            elif [[ "$arch_pattern" =~ "Clean" || "$arch_pattern" =~ "clean" ]]; then
                mkdir -p src/cmd/server src/internal/domain/entity src/internal/domain/usecase src/internal/adapter/controller src/internal/adapter/repository src/internal/infrastructure/db src/internal/config tests
            else
                mkdir -p src/cmd/server src/internal/model src/internal/controller src/internal/view src/internal/config tests
            fi
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
            if [[ "$arch_pattern" =~ "Hexagonal" || "$arch_pattern" =~ "hexagonal" || "$arch_pattern" =~ "Ports" || "$arch_pattern" =~ "ports" ]]; then
                mkdir -p src/app/domain src/app/ports src/app/adapters/in/api src/app/adapters/out/db src/app/core tests
            elif [[ "$arch_pattern" =~ "Clean" || "$arch_pattern" =~ "clean" ]]; then
                mkdir -p src/app/entities src/app/usecases src/app/controllers src/app/infrastructure/db src/app/core tests
            else
                mkdir -p src/app/core src/app/api/endpoints tests
            fi
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

        elif [ "$tech_stack" = "Multi-Project" ]; then
            # Scaffold Custom Multi-Project / Separate Apps layout
            mkdir -p apps/backend apps/frontend
            
            echo "Scaffolding Custom Multi-Project layout..."

            # 1. Scaffold Backend App
            if [ "$be_choice" = "1" ]; then
                # NestJS Boilerplate
                echo "  Scaffolding NestJS backend..."
                mkdir -p apps/backend/src
                
                # Check Architecture
                if [ "$be_arch_choice" = "1" ]; then
                    # Hexagonal Architecture
                    mkdir -p apps/backend/src/core/domain apps/backend/src/core/ports apps/backend/src/adapters/in/web apps/backend/src/adapters/out/persistence
                elif [ "$be_arch_choice" = "2" ]; then
                    # Clean Architecture
                    mkdir -p apps/backend/src/entities apps/backend/src/usecases apps/backend/src/controllers apps/backend/src/infrastructure/db
                else
                    # Standard NestJS Modular
                    mkdir -p apps/backend/src/modules apps/backend/src/common
                fi
                
                cat << 'JSON_EOF' > apps/backend/package.json
{
  "name": "backend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "build": "nest build",
    "start": "nest start",
    "lint": "eslint 'src/**/*.ts'",
    "test": "jest"
  },
  "dependencies": {
    "@nestjs/common": "^10.0.0",
    "@nestjs/core": "^10.0.0",
    "reflect-metadata": "^0.1.13",
    "rxjs": "^7.8.1"
  },
  "devDependencies": {
    "@nestjs/cli": "^10.0.0",
    "@nestjs/testing": "^10.0.0",
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0",
    "eslint": "^8.0.0",
    "jest": "^29.0.0"
  }
}
JSON_EOF

                cat << 'TS_EOF' > apps/backend/src/main.ts
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  await app.listen(process.env.PORT || 3000);
}
bootstrap();
TS_EOF

                cat << 'TS_EOF' > apps/backend/src/app.module.ts
import { Module } from '@nestjs/common';

@Module({
  imports: [],
  controllers: [],
  providers: [],
})
export class AppModule {}
TS_EOF

            elif [ "$be_choice" = "2" ]; then
                # FastAPI Boilerplate
                echo "  Scaffolding FastAPI backend..."
                mkdir -p apps/backend/src/app
                
                if [ "$be_arch_choice" = "1" ]; then
                    # Hexagonal Architecture
                    mkdir -p apps/backend/src/app/domain apps/backend/src/app/ports apps/backend/src/app/adapters/in/api apps/backend/src/app/adapters/out/db apps/backend/src/app/core
                elif [ "$be_arch_choice" = "2" ]; then
                    # Clean Architecture
                    mkdir -p apps/backend/src/app/entities apps/backend/src/app/usecases apps/backend/src/app/controllers apps/backend/src/app/infrastructure/db apps/backend/src/app/core
                else
                    # Standard Modular API
                    mkdir -p apps/backend/src/app/core apps/backend/src/app/api/endpoints
                fi
                
                cat << 'TXT_EOF' > apps/backend/requirements.txt
fastapi>=0.110.0
uvicorn[standard]>=0.28.0
pydantic>=2.6.4
pytest>=8.1.1
httpx>=0.27.0
TXT_EOF

                cat << 'PY_EOF' > apps/backend/src/app/main.py
from fastapi import FastAPI

app = FastAPI(title="Antigravity Custom Backend")

@app.get("/")
def read_root():
    return {"message": "Hello from Custom FastAPI Backend!"}
PY_EOF

            elif [ "$be_choice" = "3" ]; then
                # Go Gin Boilerplate
                echo "  Scaffolding Go Gin backend..."
                mkdir -p apps/backend/src/cmd/server
                
                if [ "$be_arch_choice" = "1" ]; then
                    # Hexagonal Architecture
                    mkdir -p apps/backend/src/internal/core/domain apps/backend/src/internal/core/ports apps/backend/src/internal/adapters/in/web apps/backend/src/internal/adapters/out/db apps/backend/src/internal/config
                elif [ "$be_arch_choice" = "2" ]; then
                    # Clean Architecture
                    mkdir -p apps/backend/src/internal/domain/entity apps/backend/src/internal/domain/usecase apps/backend/src/internal/adapter/controller apps/backend/src/internal/adapter/repository apps/backend/src/internal/infrastructure/db apps/backend/src/internal/config
                else
                    # Standard Go Gin MVC
                    mkdir -p apps/backend/src/internal/model apps/backend/src/internal/controller apps/backend/src/internal/view apps/backend/src/internal/config
                fi
                
                cat << 'GO_EOF' > apps/backend/go.mod
module backend

go 1.20

require (
	github.com/gin-gonic/gin v1.9.1
)
GO_EOF

                cat << 'GO_EOF' > apps/backend/src/cmd/server/main.go
package main

import (
	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()
	r.GET("/", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"message": "Hello from Custom Go Gin Backend!",
		})
	})
	r.Run()
}
GO_EOF
            fi

            # 2. Scaffold Frontend App
            if [ "$fe_choice" = "1" ]; then
                # Next.js Boilerplate
                echo "  Scaffolding Next.js frontend..."
                mkdir -p apps/frontend/src/app apps/frontend/src/lib
                
                if [ "$fe_arch_choice" = "1" ]; then
                    # Atomic Design
                    mkdir -p apps/frontend/src/components/atoms apps/frontend/src/components/molecules apps/frontend/src/components/organisms apps/frontend/src/components/templates
                else
                    # Standard Next.js App Router
                    mkdir -p apps/frontend/src/components
                fi
                
                cat << 'JSON_EOF' > apps/frontend/package.json
{
  "name": "frontend",
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
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "typescript": "^5.0.0",
    "eslint": "^8.0.0",
    "jest": "^29.0.0"
  }
}
JSON_EOF

                cat << 'TSX_EOF' > apps/frontend/src/app/layout.tsx
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Antigravity Custom Frontend',
  description: 'Flexible separate frontend application',
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

                cat << 'TSX_EOF' > apps/frontend/src/app/page.tsx
export default function Home() {
  return (
    <main style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>🚀 Welcome to Antigravity Custom Frontend</h1>
      <p>Running alongside a decoupled backend service in a clean modular layout.</p>
    </main>
  );
}
TSX_EOF

            elif [ "$fe_choice" = "2" ]; then
                # React SPA (Vite) Boilerplate
                echo "  Scaffolding React SPA frontend..."
                mkdir -p apps/frontend/src apps/frontend/public
                
                if [ "$fe_arch_choice" = "1" ]; then
                    # Atomic Design
                    mkdir -p apps/frontend/src/components/atoms apps/frontend/src/components/molecules apps/frontend/src/components/organisms apps/frontend/src/components/templates
                else
                    # Standard React Components
                    mkdir -p apps/frontend/src/components
                fi
                
                cat << 'JSON_EOF' > apps/frontend/package.json
{
  "name": "frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "lint": "eslint 'src/**/*.ts'",
    "test": "jest"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@types/react": "^18.0.0",
    "typescript": "^5.0.0",
    "eslint": "^8.0.0",
    "jest": "^29.0.0"
  }
}
JSON_EOF

                cat << 'HTML_EOF' > apps/frontend/index.html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Antigravity React SPA</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
HTML_EOF

                cat << 'TSX_EOF' > apps/frontend/src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
TSX_EOF

                cat << 'TSX_EOF' > apps/frontend/src/App.tsx
import React from 'react';

export default function App() {
  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>🚀 Welcome to Antigravity React SPA Frontend</h1>
      <p>Decoupled single-page frontend application.</p>
    </div>
  );
}
TSX_EOF

            elif [ "$fe_choice" = "3" ]; then
                # Laravel Blade / PHP HTML Boilerplate
                echo "  Scaffolding Laravel Blade/HTML frontend..."
                mkdir -p apps/frontend/resources/views apps/frontend/public/css apps/frontend/public/js
                
                cat << 'HTML_EOF' > apps/frontend/resources/views/welcome.blade.php
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Antigravity Blade Frontend</title>
    <style>
        body { font-family: sans-serif; padding: 2rem; background-color: #f8fafc; color: #1e293b; }
    </style>
</head>
<body>
    <h1>🚀 Welcome to Antigravity Blade/HTML Frontend</h1>
    <p>Flexible separate frontend application template.</p>
</body>
</html>
HTML_EOF
            fi

            echo "Scaffolded Custom Multi-Project application template successfully!"

        elif [ "$tech_stack" = "Laravel" ]; then
            # Scaffold Laravel Full-stack PHP application
            echo "Scaffolding Laravel Application..."
            # Create standard Laravel directories
            mkdir -p app/Http/Controllers app/Models app/Providers bootstrap config database/migrations database/seeders database/factories public resources/views resources/css resources/js routes tests/Feature tests/Unit
            
            # Write Controller.php
            cat << 'PHP_EOF' > app/Http/Controllers/Controller.php
<?php

namespace App\Http\Controllers;

use Illuminate\Foundation\Auth\Access\AuthorizesRequests;
use Illuminate\Foundation\Validation\ValidatesRequests;
use Illuminate\Routing\Controller as BaseController;

class Controller extends BaseController
{
    use AuthorizesRequests, ValidatesRequests;
}
PHP_EOF

            # Write User.php Model
            cat << 'PHP_EOF' > app/Models/User.php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Laravel\Sanctum\HasApiTokens;

class User extends Authenticatable
{
    use HasApiTokens, HasFactory, Notifiable;

    protected $fillable = [
        'name',
        'email',
        'password',
    ];

    protected $hidden = [
        'password',
        'remember_token',
    ];

    protected $casts = [
        'email_verified_at' => 'datetime',
        'password' => 'hashed',
    ];
}
PHP_EOF

            # Write composer.json
            cat << 'JSON_EOF' > composer.json
{
    "name": "laravel/laravel",
    "type": "project",
    "description": "The Laravel Framework.",
    "keywords": ["framework", "laravel"],
    "license": "MIT",
    "require": {
        "php": "^8.1",
        "guzzlehttp/guzzle": "^7.2",
        "laravel/framework": "^10.0",
        "laravel/sanctum": "^3.2",
        "laravel/tinker": "^2.8"
    },
    "require-dev": {
        "fakerphp/faker": "^1.9.1",
        "laravel/pint": "^1.0",
        "laravel/sail": "^1.18",
        "mockery/mockery": "^1.4.4",
        "nunomaduro/collision": "^7.0",
        "phpunit/phpunit": "^10.0",
        "spatie/laravel-ignition": "^2.0"
    },
    "autoload": {
        "psr-4": {
            "App\\": "app/",
            "Database\\Factories\\": "database/factories/",
            "Database\\Seeders\\": "database/seeders/"
        }
    },
    "autoload-dev": {
        "psr-4": {
            "Tests\\": "tests/"
        }
    },
    "scripts": {
        "post-autoload-dump": [
            "Illuminate\\Foundation\\ComposerScripts::postAutoloadDump",
            "@php artisan package:discover --ansi"
        ],
        "post-update-cmd": [
            "@php artisan vendor:publish --tag=laravel-assets --ansi --force"
        ],
        "post-root-package-install": [
            "@php -r \"file_exists('.env') || copy('.env.example', '.env');\""
        ],
        "post-create-project-cmd": [
            "@php artisan key:generate --ansi"
        ]
    },
    "extra": {
        "laravel": {
            "dont-discover": []
        }
    },
    "config": {
        "optimize-autoloader": true,
        "preferred-install": "dist",
        "sort-packages": true,
        "allow-plugins": {
            "pestphp/pest-plugin": true,
            "php-http/discovery": true
        }
    },
    "minimum-stability": "stable",
    "prefer-stable": true
}
JSON_EOF

            # Write package.json
            cat << 'JSON_EOF' > package.json
{
    "private": true,
    "type": "module",
    "scripts": {
        "dev": "vite",
        "build": "vite build"
    },
    "devDependencies": {
        "axios": "^1.1.2",
        "laravel-vite-plugin": "^0.7.5",
        "vite": "^4.0.0"
    }
}
JSON_EOF

            # Write .env.example
            cat << 'ENV_EOF' > .env.example
APP_NAME=Laravel
APP_ENV=local
APP_KEY=
APP_DEBUG=true
APP_URL=http://localhost

LOG_CHANNEL=stack
LOG_DEPRECATIONS_CHANNEL=null
LOG_LEVEL=debug

DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=laravel
DB_USERNAME=root
DB_PASSWORD=

BROADCAST_DRIVER=log
CACHE_DRIVER=file
FILESYSTEM_DISK=local
QUEUE_CONNECTION=sync
SESSION_DRIVER=file
SESSION_LIFETIME=120
ENV_EOF

            cp .env.example .env

            # Write Artisan executable
            cat << 'ARTISAN_EOF' > artisan
#!/usr/bin/env php
<?php

define('LARAVEL_START', microtime(true));

if (file_exists($maintenance = __DIR__.'/storage/framework/maintenance.php')) {
    require $maintenance;
}

require __DIR__.'/vendor/autoload.php';

$app = require_once __DIR__.'/bootstrap/app.php';

$kernel = $app->make(Illuminate\Contracts\Console\Kernel::class);

$status = $kernel->handle(
    $input = new Symfony\Component\Console\Input\ArgvInput,
    new Symfony\Component\Console\Output\ConsoleOutput
);

$kernel->terminate($input, $status);

exit($status);
ARTISAN_EOF
            chmod +x artisan

            # Write bootstrap/app.php
            cat << 'BOOTSTRAP_EOF' > bootstrap/app.php
<?php

$app = new Illuminate\Foundation\Application(
    $_ENV['APP_BASE_PATH'] ?? dirname(__DIR__)
);

$app->singleton(
    Illuminate\Contracts\Http\Kernel::class,
    App\Http\Kernel::class
);

$app->singleton(
    Illuminate\Contracts\Console\Kernel::class,
    App\Http\Console\Kernel::class
);

$app->singleton(
    Illuminate\Contracts\Debug\ExceptionHandler::class,
    App\Exceptions\Handler::class
);

return $app;
BOOTSTRAP_EOF

            # Write App HTTP Kernel, Exceptions, Console, Web routes, Controllers, Welcome views etc.
            mkdir -p app/Http app/Exceptions app/Console
            
            cat << 'KERNEL_EOF' > app/Http/Kernel.php
<?php

namespace App\Http;

use Illuminate\Foundation\Http\Kernel as HttpKernel;

class Kernel extends HttpKernel
{
    protected $middleware = [
        \Illuminate\Http\Middleware\TrustProxies::class,
        \Illuminate\Http\Middleware\HandleCors::class,
        \Illuminate\Foundation\Http\Middleware\PreventRequestsDuringMaintenance::class,
        \Illuminate\Foundation\Http\Middleware\ValidatePostSize::class,
        \App\Http\Middleware\TrimStrings::class,
        \Illuminate\Foundation\Http\Middleware\ConvertEmptyStringsToNull::class,
    ];

    protected $middlewareGroups = [
        'web' => [
            \App\Http\Middleware\EncryptCookies::class,
            \Illuminate\Cookie\Middleware\AddQueuedCookiesToResponse::class,
            \Illuminate\Session\Middleware\StartSession::class,
            \Illuminate\View\Middleware\ShareErrorsFromSession::class,
            \App\Http\Middleware\VerifyCsrfToken::class,
            \Illuminate\Routing\Middleware\SubstituteBindings::class,
        ],
        'api' => [
            \Laravel\Sanctum\Http\Middleware\EnsureFrontendRequestsAreStateful::class,
            \Illuminate\Routing\Middleware\ThrottleRequests::class.':api',
            \Illuminate\Routing\Middleware\SubstituteBindings::class,
        ],
    ];

    protected $middlewareAliases = [
        'auth' => \App\Http\Middleware\Authenticate::class,
        'guest' => \App\Http\Middleware\RedirectIfAuthenticated::class,
        'verified' => \Illuminate\Auth\Middleware\EnsureEmailIsVerified::class,
    ];
}
KERNEL_EOF

            cat << 'CONSOLE_EOF' > app/Console/Kernel.php
<?php

namespace App\Console;

use Illuminate\Foundation\Console\Kernel as ConsoleKernel;

class Kernel extends ConsoleKernel
{
    protected function commands(): void
    {
        $this->load(__DIR__.'/Commands');
        require base_path('routes/console.php');
    }
}
CONSOLE_EOF

            cat << 'HANDLER_EOF' > app/Exceptions/Handler.php
<?php

namespace App\Exceptions;

use Illuminate\Foundation\Exceptions\Handler as ExceptionHandler;
use Throwable;

class Handler extends ExceptionHandler
{
    protected $dontFlash = [
        'current_password',
        'password',
        'password_confirmation',
    ];

    public function register(): void
    {
        $this->reportable(function (Throwable $e) {
            //
        });
    }
}
HANDLER_EOF

            # Middlewares: app/Http/Middleware/
            mkdir -p app/Http/Middleware
            cat << 'MIDDLEWARE_EOF' > app/Http/Middleware/TrimStrings.php
<?php
namespace App\Http\Middleware;
use Illuminate\Foundation\Http\Middleware\TrimStrings as Middleware;
class TrimStrings extends Middleware {}
MIDDLEWARE_EOF

            cat << 'MIDDLEWARE_EOF' > app/Http/Middleware/EncryptCookies.php
<?php
namespace App\Http\Middleware;
use Illuminate\Cookie\Middleware\EncryptCookies as Middleware;
class EncryptCookies extends Middleware {}
MIDDLEWARE_EOF

            cat << 'MIDDLEWARE_EOF' > app/Http/Middleware/VerifyCsrfToken.php
<?php
namespace App\Http\Middleware;
use Illuminate\Foundation\Http\Middleware\VerifyCsrfToken as Middleware;
class VerifyCsrfToken extends Middleware {}
MIDDLEWARE_EOF

            cat << 'MIDDLEWARE_EOF' > app/Http/Middleware/Authenticate.php
<?php
namespace App\Http\Middleware;
use Illuminate\Auth\Middleware\Authenticate as Middleware;
use Illuminate\Http\Request;
class Authenticate extends Middleware {
    protected function redirectTo(Request $request): ?string {
        return $request->expectsJson() ? null : route('login');
    }
}
MIDDLEWARE_EOF

            cat << 'MIDDLEWARE_EOF' > app/Http/Middleware/RedirectIfAuthenticated.php
<?php
namespace App\Http\Middleware;
use App\Providers\RouteServiceProvider;
use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Symfony\Component\HttpFoundation\Response;
class RedirectIfAuthenticated {
    public function handle(Request $request, Closure $next, string ...$guards): Response {
        $guards = empty($guards) ? [null] : $guards;
        foreach ($guards as $guard) {
            if (Auth::guard($guard)->check()) {
                return redirect(RouteServiceProvider::HOME);
            }
        }
        return $next($request);
    }
}
MIDDLEWARE_EOF

            # Providers: app/Providers/
            mkdir -p app/Providers
            cat << 'PROVIDER_EOF' > app/Providers/RouteServiceProvider.php
<?php

namespace App\Providers;

use Illuminate\Cache\RateLimiting\Limit;
use Illuminate\Foundation\Support\Providers\RouteServiceProvider as ServiceProvider;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\RateLimiter;
use Illuminate\Support\Facades\Route;

class RouteServiceProvider extends ServiceProvider
{
    public const HOME = '/home';

    public function boot(): void
    {
        RateLimiter::for('api', function (Request $request) {
            return Limit::perMinute(60)->by($request->user()?->id ?: $request->ip());
        });

        $this->routes(function () {
            Route::middleware('api')
                ->prefix('api')
                ->group(base_path('routes/api.php'));

            Route::middleware('web')
                ->group(base_path('routes/web.php'));
        });
    }
}
PROVIDER_EOF

            # Write standard routes
            cat << 'ROUTES_EOF' > routes/web.php
<?php

use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return view('welcome');
});
ROUTES_EOF

            cat << 'ROUTES_EOF' > routes/api.php
<?php

use Illuminate\Support\Facades\Route;
use Illuminate\Http\Request;

Route::middleware('auth:sanctum')->get('/user', function (Request $request) {
    return $request->user();
});
ROUTES_EOF

            cat << 'ROUTES_EOF' > routes/console.php
<?php

use Illuminate\Support\Facades\Artisan;

Artisan::command('inspire', function () {
    $this->comment(Illuminate\Foundation\Inspiring::quote());
})->purpose('Display an inspiring quote');
ROUTES_EOF

            # Write welcome view
            cat << 'HTML_EOF' > resources/views/welcome.blade.php
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Antigravity Laravel Application</title>
    <style>
        body {
            font-family: 'Outfit', 'Inter', sans-serif;
            background: radial-gradient(circle at top right, #1e1b4b, #0f172a);
            color: #f8fafc;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
        }
        .container {
            text-align: center;
            padding: 3rem;
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 24px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            max-width: 500px;
        }
        h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            background: linear-gradient(to right, #f43f5e, #fb7185);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        p {
            color: #94a3b8;
            line-height: 1.6;
        }
        .badge {
            display: inline-block;
            padding: 0.5rem 1rem;
            background: rgba(244, 63, 94, 0.1);
            color: #f43f5e;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="badge">Laravel 10.x + PHP</div>
        <h1>🚀 Welcome to Antigravity Laravel</h1>
        <p>Your production-ready Laravel full-stack MVC application, scaffolded and pre-configured for seamless development with AI coding agents.</p>
    </div>
</body>
</html>
HTML_EOF

            # Write phpunit.xml
            cat << 'XML_EOF' > phpunit.xml
<?xml version="1.0" encoding="UTF-8"?>
<phpunit xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:noNamespaceSchemaLocation="./vendor/phpunit/phpunit/phpunit.xsd"
         bootstrap="vendor/autoload.php"
         colors="true">
    <testsuites>
        <testsuite name="Unit">
            <directory suffix="Test.php">./tests/Unit</directory>
        </testsuite>
        <testsuite name="Feature">
            <directory suffix="Test.php">./tests/Feature</directory>
        </testsuite>
    </testsuites>
</phpunit>
XML_EOF

            echo "Scaffolded Laravel application template successfully!"

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

        if [ "$gen_docker" = "y" ] || [ "$gen_docker" = "yes" ]; then
            echo "Generating Dockerfiles and docker-compose.yml..."
            
            # Helper variables for database
            local db_service=""
            local db_envs=""
            local db_depends=""
            
            local db_lower
            db_lower=$(echo "$db_orm" | tr '[:upper:]' '[:lower:]')
            
            if [[ "$db_lower" =~ "postgres" ]]; then
                db_service=$(cat << 'DB_POSTGRES'
  postgres:
    image: postgres:15-alpine
    container_name: postgres_db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: postgres
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
DB_POSTGRES
)
                db_envs="      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/postgres\n      - DB_HOST=postgres\n      - DB_PORT=5432"
                db_depends="    depends_on:\n      postgres:\n        condition: service_healthy"
            elif [[ "$db_lower" =~ "mysql" || "$db_lower" =~ "mariadb" ]]; then
                db_service=$(cat << 'DB_MYSQL'
  mysql:
    image: mysql:8.0
    container_name: mysql_db
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: db
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD-SHELL", "mysqladmin ping -h localhost"]
      interval: 5s
      timeout: 5s
      retries: 5
DB_MYSQL
)
                db_envs="      - DATABASE_URL=mysql://root:root@mysql:3306/db\n      - DB_HOST=mysql\n      - DB_PORT=3306"
                db_depends="    depends_on:\n      mysql:\n        condition: service_healthy"
            elif [[ "$db_lower" =~ "mongo" ]]; then
                db_service=$(cat << 'DB_MONGO'
  mongodb:
    image: mongo:6.0
    container_name: mongodb_db
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    healthcheck:
      test: ["CMD-SHELL", "echo 'db.runCommand(\"ping\")' | mongosh localhost:27017/test --quiet"]
      interval: 5s
      timeout: 5s
      retries: 5
DB_MONGO
)
                db_envs="      - DATABASE_URL=mongodb://mongodb:27017/db\n      - DB_HOST=mongodb\n      - DB_PORT=27017"
                db_depends="    depends_on:\n      mongodb:\n        condition: service_healthy"
            elif [[ "$db_lower" =~ "redis" ]]; then
                db_service=$(cat << 'DB_REDIS'
  redis:
    image: redis:7-alpine
    container_name: redis_cache
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD-SHELL", "redis-cli ping | grep PONG"]
      interval: 5s
      timeout: 5s
      retries: 5
DB_REDIS
)
                db_envs="      - REDIS_URL=redis://redis:6379"
                db_depends="    depends_on:\n      redis:\n        condition: service_healthy"
            fi

            # 1. Monorepo / Multi-Project Scaffolding
            if [ "$tech_stack" = "Monorepo" ] || [ "$tech_stack" = "Multi-Project" ]; then
                local be_dir=""
                local fe_dir=""
                local be_port="3000"
                local fe_port="3000"
                local be_dockerfile=""
                local fe_dockerfile=""
                
                if [ "$tech_stack" = "Monorepo" ]; then
                    be_dir="apps/api"
                    fe_dir="apps/web"
                    be_port="8080" # Go Gin
                    fe_port="3000" # Next.js
                    
                    be_dockerfile=$(cat << 'MONO_BE'
FROM golang:1.20-alpine AS builder
WORKDIR /app
COPY go.mod go.sum* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o main ./src/cmd/server/main.go

FROM alpine:latest
WORKDIR /root/
COPY --from=builder /app/main .
EXPOSE 8080
CMD ["./main"]
MONO_BE
)
                    fe_dockerfile=$(cat << 'MONO_FE'
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./
RUN \
  if [ -f pnpm-lock.yaml ]; then corepack enable && pnpm i --frozen-lockfile; \
  elif [ -f package-lock.json ]; then npm ci; \
  elif [ -f yarn.lock ]; then yarn install --frozen-lockfile; \
  else npm install; \
  fi
COPY . .
RUN \
  if [ -f pnpm-lock.yaml ]; then pnpm run build; \
  else npm run build; \
  fi

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/package.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["npm", "start"]
MONO_FE
)
                else
                    # Multi-Project
                    be_dir="apps/backend"
                    fe_dir="apps/frontend"
                    
                    # Backend Dockerfile selection
                    if [ "$be_choice" = "1" ]; then
                        be_port="3000"
                        be_dockerfile=$(cat << 'MULTI_NEST'
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/package.json ./
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node", "dist/main"]
MULTI_NEST
)
                    elif [ "$be_choice" = "2" ]; then
                        be_port="8000"
                        be_dockerfile=$(cat << 'MULTI_PY'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
MULTI_PY
)
                    elif [ "$be_choice" = "3" ]; then
                        be_port="8080"
                        be_dockerfile=$(cat << 'MULTI_GO'
FROM golang:1.20-alpine AS builder
WORKDIR /app
COPY go.mod go.sum* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o main ./src/cmd/server/main.go

FROM alpine:latest
WORKDIR /root/
COPY --from=builder /app/main .
EXPOSE 8080
CMD ["./main"]
MULTI_GO
)
                    fi

                    # Frontend Dockerfile selection
                    if [ "$fe_choice" = "1" ]; then
                        fe_port="3000"
                        fe_dockerfile=$(cat << 'MULTI_NEXT'
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./
RUN \
  if [ -f pnpm-lock.yaml ]; then corepack enable && pnpm i --frozen-lockfile; \
  elif [ -f package-lock.json ]; then npm ci; \
  elif [ -f yarn.lock ]; then yarn install --frozen-lockfile; \
  else npm install; \
  fi
COPY . .
RUN \
  if [ -f pnpm-lock.yaml ]; then pnpm run build; \
  else npm run build; \
  fi

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/package.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["npm", "start"]
MULTI_NEXT
)
                    elif [ "$fe_choice" = "2" ]; then
                        fe_port="80"
                        fe_dockerfile=$(cat << 'MULTI_VITE'
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
MULTI_VITE
)
                    elif [ "$fe_choice" = "3" ]; then
                        fe_port="80"
                        fe_dockerfile=$(cat << 'MULTI_PHP'
FROM php:8.2-apache
COPY . /var/www/html/
RUN chown -R www-data:www-data /var/www/html
EXPOSE 80
MULTI_PHP
)
                    fi
                fi
                
                # Write Dockerfiles
                if [ -n "$be_dockerfile" ] && [ -d "$be_dir" ]; then
                    echo "$be_dockerfile" > "$be_dir/Dockerfile"
                    echo "  Created $be_dir/Dockerfile"
                fi
                if [ -n "$fe_dockerfile" ] && [ -d "$fe_dir" ]; then
                    echo "$fe_dockerfile" > "$fe_dir/Dockerfile"
                    echo "  Created $fe_dir/Dockerfile"
                fi

                # Build docker-compose services
                local services=""
                if [ -d "$be_dir" ] && [ "$be_choice" != "4" ]; then
                    services="${services}\n  backend:\n    build:\n      context: ./${be_dir}\n    ports:\n      - \"${be_port}:${be_port}\"\n"
                    if [ -n "$db_depends" ]; then
                        services="${services}$(echo -e "$db_depends")\n"
                    fi
                    if [ -n "$db_envs" ]; then
                        services="${services}    environment:\n$(echo -e "$db_envs")\n"
                    fi
                fi
                
                if [ -d "$fe_dir" ] && [ "$fe_choice" != "4" ]; then
                    local host_fe_port="3000"
                    if [ "$be_choice" != "4" ] && [ "$be_port" = "3000" ]; then
                        host_fe_port="3001"
                    fi
                    services="${services}\n  frontend:\n    build:\n      context: ./${fe_dir}\n    ports:\n      - \"${host_fe_port}:${fe_port}\"\n"
                    if [ -d "$be_dir" ] && [ "$be_choice" != "4" ]; then
                        services="${services}    depends_on:\n      backend:\n        condition: service_started\n"
                        services="${services}    environment:\n      - BACKEND_URL=http://backend:${be_port}\n"
                    fi
                fi
                
                if [ -n "$db_service" ]; then
                    services="${services}\n$(echo -e "$db_service")"
                fi
                
                # Write docker-compose.yml
                cat << 'COMPOSE_MULTI' > docker-compose.yml
version: '3.8'

services:
COMPOSE_MULTI
                echo -e "$services" >> docker-compose.yml
                cat << 'COMPOSE_VOLUME' >> docker-compose.yml

volumes:
  pgdata:
  mysql_data:
  mongo_data:
  redis_data:
COMPOSE_VOLUME
                echo "  Created docker-compose.yml at root"

            else
                # 2. Single Project Scaffolding
                local port="3000"
                local dockerfile=""
                
                if [ "$tech_stack" = "Next.js" ]; then
                    port="3000"
                    dockerfile=$(cat << 'SINGLE_NEXT'
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/package.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["npm", "start"]
SINGLE_NEXT
)
                elif [ "$tech_stack" = "Go Gin" ] || [ "$tech_stack" = "Go" ]; then
                    port="8080"
                    dockerfile=$(cat << 'SINGLE_GO'
FROM golang:1.20-alpine AS builder
WORKDIR /app
COPY go.mod go.sum* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o main ./src/cmd/server/main.go

FROM alpine:latest
WORKDIR /root/
COPY --from=builder /app/main .
EXPOSE 8080
CMD ["./main"]
SINGLE_GO
)
                elif [ "$tech_stack" = "FastAPI" ] || [ "$tech_stack" = "Python" ]; then
                    port="8000"
                    dockerfile=$(cat << 'SINGLE_PY'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
SINGLE_PY
)
                elif [ "$tech_stack" = "Node/TypeScript" ]; then
                    port="3000"
                    dockerfile=$(cat << 'SINGLE_NODE'
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/package.json ./
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node", "dist/index.js"]
SINGLE_NODE
)
                fi
                
                if [ -n "$dockerfile" ]; then
                    echo "$dockerfile" > Dockerfile
                    echo "  Created Dockerfile"
                fi

                # Build services for docker-compose.yml
                local services="  app:\n    build:\n      context: .\n    ports:\n      - \"${port}:${port}\"\n"
                if [ -n "$db_depends" ]; then
                    services="${services}$(echo -e "$db_depends")\n"
                fi
                if [ -n "$db_envs" ]; then
                    services="${services}    environment:\n$(echo -e "$db_envs")\n"
                fi
                if [ -n "$db_service" ]; then
                    services="${services}\n$(echo -e "$db_service")"
                fi
                
                # Write docker-compose.yml
                cat << 'COMPOSE_SINGLE' > docker-compose.yml
version: '3.8'

services:
COMPOSE_SINGLE
                echo -e "$services" >> docker-compose.yml
                cat << 'COMPOSE_VOLUME' >> docker-compose.yml

volumes:
  pgdata:
  mysql_data:
  mongo_data:
  redis_data:
COMPOSE_VOLUME
                echo "  Created docker-compose.yml"
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
        if [ -f .agents/rules/project_rules.md ]; then
            local linter_line
            linter_line=$(grep "Linter command" .agents/rules/project_rules.md || echo "")
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
        if [ -f .agents/rules/project_rules.md ]; then
            local test_line
            test_line=$(grep "Test runner command" .agents/rules/project_rules.md || echo "")
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

    # Auto-rotate profiles if configured
    local profiles_file=""
    if [ -f ".agents/git_profiles" ]; then
        profiles_file=".agents/git_profiles"
    elif [ -f "$HOME/.git_profiles" ]; then
        profiles_file="$HOME/.git_profiles"
    fi

    if [ -n "$profiles_file" ] && [ -f "$profiles_file" ]; then
        # Get list of profile keys
        local profile_keys
        profile_keys=$(grep -E "^[a-zA-Z0-9_\-]+\.name=" "$profiles_file" | cut -d'.' -f1 | sort -u || echo "")
        
        # Convert to array or list
        local keys_arr=($profile_keys)
        local num_profiles=${#keys_arr[@]}
        
        if [ $num_profiles -gt 0 ]; then
            # Get last commit's author email
            local last_email
            last_email=$(git log -n 1 --format="%ae" 2>/dev/null || echo "")
            
            local selected_idx=0
            # Search if last_email matches any profile's email
            for i in "${!keys_arr[@]}"; do
                local p="${keys_arr[$i]}"
                local p_e=$(grep "^${p}\.email=" "$profiles_file" | cut -d'=' -f2-)
                if [ "$p_e" = "$last_email" ]; then
                    # Select the next profile (round-robin)
                    selected_idx=$(( (i + 1) % num_profiles ))
                    break
                fi
            done
            
            local selected_profile="${keys_arr[$selected_idx]}"
            local p_name=$(grep "^${selected_profile}\.name=" "$profiles_file" | cut -d'=' -f2-)
            local p_email=$(grep "^${selected_profile}\.email=" "$profiles_file" | cut -d'=' -f2-)
            
            echo "Auto-selecting Git profile: '$selected_profile' (\"$p_name\" <$p_email>) for round-robin commit rotation."
            # Set locally
            git config --local user.name "$p_name"
            git config --local user.email "$p_email"
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

    if [ -f ".agents/rules/project_rules.md" ]; then
        echo "Warning: Existing project rules blueprint found. Backing up to .agents/rules/project_rules.md${backup_suffix}"
        cp ".agents/rules/project_rules.md" ".agents/rules/project_rules.md${backup_suffix}"
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
    mkdir -p .agents/rules

    # Check for legacy rules folder and migrate
    if [ -d ".agent/rules" ]; then
        echo "Legacy rules folder .agent/rules found. Migrating to .agents/rules/..."
        if [ "$(ls -A .agent/rules 2>/dev/null)" ]; then
            cp -r .agent/rules/* .agents/rules/
        fi
        rm -rf .agent/rules
        if [ -d ".agent" ] && [ ! "$(ls -A .agent 2>/dev/null)" ]; then
            rm -rf .agent
        fi
        echo "Migration of legacy rules complete."
        if [ -f "$MEMORY_FILE" ]; then
            if ! grep -q "Legacy rules migrated" "$MEMORY_FILE"; then
                sed -i '/## 3. Relayed Context/a - **Migration Log**: Legacy rules migrated from .agent/rules to .agents/rules.' "$MEMORY_FILE"
            fi
        fi
    fi

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
            echo -e "# Agent Core Memory\n\n> **Memory Schema Version**: 5.0.0  \n> **Target System**: Antigravity Agent Core\n> **Active Guidelines**: Read [AGENTS.md](file://../AGENTS.md) and [.agents/rules/project_rules.md](file://./rules/project_rules.md) for execution details. Keep this file under 100 lines at all times.\n" > "$temp_mem"
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
        # ensure local Git profiles config is ignored
        if ! grep -E -q "^\.agents/git_profiles" "$temp_git"; then
            echo -e "\n# Ignore local agent git profiles configuration\n.agents/git_profiles" >> "$temp_git"
        fi
        mv "$temp_git" ".gitignore"
        echo "  - .gitignore updated."
    else
        echo "Creating default compliant .gitignore..."
        cat << 'GIT_EOF' > .gitignore
# Ignore agent transient locks
.agents/locks/

# Ignore local agent git profiles configuration
.agents/git_profiles
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

cmd_sync_api() {
    echo "=========================================================="
    echo "Starting API Contract Synchronization..."
    echo "=========================================================="
    
    local subprojects_file=".agents/subprojects.sh"
    local be_path=""
    local fe_path=""
    local be_stack=""
    
    # 1. Detect backend and frontend directories
    if [ -f "$subprojects_file" ]; then
        source "$subprojects_file"
        for sp in "${SUBPROJECTS[@]}"; do
            local path=$(echo "$sp" | cut -d'|' -f1)
            local stack=$(echo "$sp" | cut -d'|' -f2)
            
            # Simple heuristics to identify backend vs frontend
            if [[ "$path" =~ "api" || "$path" =~ "backend" || "$stack" =~ "Go" || "$stack" =~ "Python" ]]; then
                be_path="$path"
                be_stack="$stack"
            elif [[ "$path" =~ "web" || "$path" =~ "frontend" || "$stack" =~ "Next.js" ]]; then
                fe_path="$path"
            fi
        done
    else
        # Fallback search if no subprojects config file
        if [ -d "apps/backend" ]; then be_path="apps/backend"; fi
        if [ -d "apps/frontend" ]; then fe_path="apps/frontend"; fi
        if [ -d "apps/api" ]; then be_path="apps/api"; fi
        if [ -d "apps/web" ]; then fe_path="apps/web"; fi
    fi
    
    # If still not found, search directories
    if [ -z "$be_path" ]; then
        if [ -f "go.mod" ] || [ -f "main.go" ]; then
            be_path="."
            be_stack="Go"
        elif [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
            be_path="."
            be_stack="Python"
        fi
    fi
    if [ -z "$fe_path" ]; then
        if [ -d "src/app" ] || [ -f "package.json" ]; then
            fe_path="."
        fi
    fi

    if [ -z "$be_path" ]; then
        echo "  [INFO] Backend application path could not be auto-detected. Operating in root fallback mode."
        be_path="."
        be_stack="Unknown"
    fi
    
    echo "  Detected Backend: $be_path ($be_stack)"
    if [ -n "$fe_path" ]; then
        echo "  Detected Frontend: $fe_path"
    fi

    local openapi_file="openapi.json"
    
    # 2. Extract OpenAPI schema from backend
    echo "  Extracting OpenAPI contract schema..."
    
    if [[ "$be_stack" =~ "Python" || -f "$be_path/requirements.txt" || -f "$be_path/pyproject.toml" ]]; then
        # Python / FastAPI extraction
        if [ "$be_path" = "." ]; then
            python3 -c "import json; from src.app.main import app; print(json.dumps(app.openapi()))" > "$openapi_file" 2>/dev/null || \
            python3 -c "import json; from app.main import app; print(json.dumps(app.openapi()))" > "$openapi_file" 2>/dev/null || \
            echo "Failed to extract FastAPI schema. Ensure FastAPI app is importable."
        else
            (cd "$be_path" && python3 -c "import json; from src.app.main import app; print(json.dumps(app.openapi()))" > "../../../$openapi_file" 2>/dev/null || \
            (cd "$be_path" && python3 -c "import json; from app.main import app; print(json.dumps(app.openapi()))" > "../../../$openapi_file" 2>/dev/null)) || \
            echo "Failed to extract FastAPI schema. Ensure FastAPI app is importable."
        fi
    elif [[ "$be_stack" =~ "Go" || -f "$be_path/go.mod" ]]; then
        # Go Swagger check
        if command -v swag &> /dev/null; then
            echo "  Running swag init in $be_path..."
            (cd "$be_path" && swag init -g src/cmd/server/main.go -o . --ot json && cp swagger.json ../../$openapi_file) 2>/dev/null || \
            (cd "$be_path" && swag init -g cmd/server/main.go -o . --ot json && cp swagger.json ../../$openapi_file) 2>/dev/null || \
            echo "Swag command failed. Creating mockup/fallback schema."
        fi
    fi

    # Fallback/Mockup schema if extraction failed or file is empty/missing
    if [ ! -f "$openapi_file" ] || [ ! -s "$openapi_file" ]; then
        echo "  Warning: Schema extraction returned empty. Writing a compliant mock/fallback openapi.json..."
        cat << 'MOCK_OPENAPI' > "$openapi_file"
{
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
MOCK_OPENAPI
    fi

    # 3. Generate TypeScript API client
    if [ -n "$fe_path" ] && [ -d "$fe_path" ]; then
        local target_client="$fe_path/src/lib/api-client.ts"
        if [ "$fe_path" = "." ] && [ -d "src/app" ]; then
            target_client="src/lib/api-client.ts"
        fi
        
        echo "  Generating TypeScript client wrapper to $target_client..."
        node .agents/scripts/generate-client.js "$openapi_file" "$target_client"
    else
        echo "  Frontend directory not detected. Generated openapi.json is saved in root."
    fi

    echo "=========================================================="
    echo "API Sync Complete!"
    echo "=========================================================="
}

cmd_log_usage() {
    if [ $# -lt 2 ]; then
        echo "Usage: $0 log-usage <token_count>"
        exit 1
    fi
    local count="$2"
    local file=".agents/token_budget.json"
    if [ ! -f "$file" ]; then
        echo "{\"max_token_budget\": 500000, \"current_token_usage\": 0, \"alert_threshold_percent\": 90}" > "$file"
    fi
    if command -v jq >/dev/null 2>&1; then
        local current=$(jq -r '.current_token_usage' "$file")
        local new_usage=$((current + count))
        local temp=$(mktemp)
        jq --argjson usage "$new_usage" '.current_token_usage = $usage' "$file" > "$temp"
        mv "$temp" "$file"
        echo "Logged $count tokens. Total usage: $new_usage."
    else
        # fallback parsing using sed if jq not found
        local current=$(grep -o '"current_token_usage":\s*[0-9]*' "$file" | grep -o '[0-9]*' || echo "0")
        local new_usage=$((current + count))
        sed -i "s/\"current_token_usage\":\s*[0-9]*/\"current_token_usage\": $new_usage/" "$file"
        echo "Logged $count tokens (fallback). Total usage: $new_usage."
    fi
}

cmd_create_adr() {
    if [ $# -lt 2 ]; then
        echo "Usage: $0 create-adr <title> [proposed|accepted|superseded]"
        exit 1
    fi
    local title="$2"
    local status="${3:-proposed}"
    
    # Normalize status to lowercase
    status=$(echo "$status" | tr '[:upper:]' '[:lower:]')
    
    if [ "$status" != "proposed" ] && [ "$status" != "accepted" ] && [ "$status" != "superseded" ]; then
        echo "Error: Status must be one of: proposed, accepted, superseded" >&2
        exit 1
    fi
    
    # Capitalize status for presentation (Proposed, Accepted, Superseded)
    local status_cap
    if [ "$status" = "proposed" ]; then
        status_cap="Proposed"
    elif [ "$status" = "accepted" ]; then
        status_cap="Accepted"
    else
        status_cap="Superseded"
    fi

    local adrs_dir=".agents/adrs"
    mkdir -p "$adrs_dir"
    
    # Determine the next ADR number
    local count=1
    for f in "$adrs_dir"/[0-9][0-9][0-9]-*.md; do
        if [ -e "$f" ]; then
            count=$((count + 1))
        fi
    done
    
    local num
    num=$(printf "%03d" "$count")
    
    # Convert title to kebab-case for filename (lowercase, replace non-alphanumeric with hyphens)
    local slug
    slug=$(echo "$title" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g' | sed -E 's/^-+|-+$//g')
    
    local filename="$adrs_dir/${num}-${slug}.md"
    
    local adr_date
    adr_date=$(date +%Y-%m-%d)
    
    # Write ADR template
    cat << INNER_EOF > "$filename"
# ADR-${num}: ${title}

- **Date**: ${adr_date}
- **Status**: ${status_cap}

## Context
[Describe the problem context and alternatives]

## Decision
[Describe the decision made]

## Consequences
[Describe the result and impact of this decision]
INNER_EOF

    # Register in .agents/adr.md
    local index_file=".agents/adr.md"
    if [ -f "$index_file" ]; then
        # Check if "## 1. Architectural Decisions Index" exists, if not create it
        if ! grep -q "## 1. Architectural Decisions Index" "$index_file"; then
            echo -e "\n## 1. Architectural Decisions Index" >> "$index_file"
        fi
        # Append the link
        echo "- [ADR-${num}: ${title}](file://./adrs/${num}-${slug}.md) - Status: ${status_cap}" >> "$index_file"
    fi
    
    echo "Created ADR-${num} at $filename and registered in $index_file"
}

cmd_release() {
    if [ $# -lt 2 ]; then
        echo "Usage: $0 release <major|minor|patch>"
        exit 1
    fi
    local bump_type="$2"
    local changelog_file="CHANGELOG.md"
    
    if [ ! -f "$changelog_file" ]; then
        echo "Error: CHANGELOG.md not found!"
        exit 1
    fi
    
    # Extract latest version from CHANGELOG.md (e.g. ## [1.4.0] - 2026-06-13)
    local current_version
    current_version=$(grep -m 1 -E '^## \[[0-9]+\.[0-9]+\.[0-9]+\]' "$changelog_file" | grep -o -E '[0-9]+\.[0-9]+\.[0-9]+')
    
    if [ -z "$current_version" ]; then
        echo "Error: Could not parse current version from CHANGELOG.md."
        exit 1
    fi
    
    local major=$(echo "$current_version" | cut -d. -f1)
    local minor=$(echo "$current_version" | cut -d. -f2)
    local patch=$(echo "$current_version" | cut -d. -f3)
    
    case "$bump_type" in
        major)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        patch)
            patch=$((patch + 1))
            ;;
        *)
            echo "Error: Invalid bump type '$bump_type'. Must be major, minor, or patch."
            exit 1
            ;;
    esac
    
    local next_version="$major.$minor.$patch"
    local current_date=$(date +%Y-%m-%d)
    
    echo "Bumping version: $current_version -> $next_version ($bump_type)"
    
    # 1. Insert new version section at the top of the version list in CHANGELOG.md
    local temp_changelog=$(mktemp)
    awk -v next_ver="$next_version" -v date="$current_date" '
        BEGIN { done = 0 }
        /^## \[[0-9]+\.[0-9]+\.[0-9]+\]/ && done == 0 {
            print "## [" next_ver "] - " date;
            print "### Added";
            print "- ";
            print "";
            done = 1
        }
        { print }
    ' "$changelog_file" > "$temp_changelog"
    
    # 2. Update version comparison links at the bottom
    local repo_url="https://github.com/rafaelghif/antigravity-agents"
    local temp_links=$(mktemp)
    awk -v next_ver="$next_version" -v curr_ver="$current_version" -v url="$repo_url" '
        BEGIN { link_inserted = 0 }
        /^\[[0-9]+\.[0-9]+\.[0-9]+\]:/ && link_inserted == 0 {
            print "[" next_ver "]: " url "/compare/v" curr_ver "...v" next_ver;
            link_inserted = 1
        }
        { print }
    ' "$temp_changelog" > "$temp_links"
    
    mv "$temp_links" "$changelog_file"
    rm -f "$temp_changelog"
    
    echo "Successfully bumped version to $next_version and updated CHANGELOG.md."
}

audit_skill() {
    local skill_dir="$1"
    local skill_name=$(basename "$skill_dir")
    local skill_md="$skill_dir/SKILL.md"
    
    # Check 1: SKILL.md exists
    if [ ! -f "$skill_md" ]; then
        echo "FAIL: $skill_name is missing SKILL.md"
        return 1
    fi
    
    # Check 2: Parse YAML frontmatter
    local line1=$(head -n 1 "$skill_md" | tr -d '\r')
    if [ "$line1" != "---" ]; then
        echo "FAIL: $skill_name SKILL.md does not start with YAML frontmatter delimiter (---)"
        return 1
    fi
    
    local closing_line=$(grep -n "^---" "$skill_md" | sed -n '2p' | cut -d':' -f1)
    if [ -z "$closing_line" ]; then
        echo "FAIL: $skill_name SKILL.md has unclosed YAML frontmatter"
        return 1
    fi
    
    local frontmatter=$(sed -n "2,$((closing_line - 1))p" "$skill_md")
    
    local parsed_name=$(echo "$frontmatter" | grep "^name:" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e "s/^'//" -e "s/'$//" -e 's/^"//' -e 's/"$//')
    local parsed_desc=$(echo "$frontmatter" | grep "^description:" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e "s/^'//" -e "s/'$//" -e 's/^"//' -e 's/"$//')
    
    if [ -z "$parsed_name" ]; then
        echo "FAIL: $skill_name frontmatter missing 'name'"
        return 1
    fi
    if [ -z "$parsed_desc" ]; then
        echo "FAIL: $skill_name frontmatter missing 'description'"
        return 1
    fi
    
    # Check 3: Check for placeholders in SKILL.md
    if grep -i -q -E "TODO|FIXME|\[placeholder\]" "$skill_md"; then
        echo "FAIL: $skill_name SKILL.md contains placeholder text (TODO/FIXME/placeholder)"
        return 1
    fi
    
    # Check 4: Verify referenced scripts
    local in_scripts=0
    local script_lines=""
    while IFS= read -r line; do
        if [[ "$line" =~ ^scripts:[[:space:]]*$ ]]; then
            in_scripts=1
            continue
        elif [[ "$line" =~ ^[a-zA-Z_]+: ]]; then
            in_scripts=0
        fi
        
        if [ "$in_scripts" -eq 1 ]; then
            script_lines="$script_lines"$'\n'"$line"
        fi
    done <<INNER_EOF
$frontmatter
INNER_EOF

    while IFS= read -r s_line; do
        s_line=$(echo "$s_line" | sed -e 's/^[[:space:]]*-//' -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
        if [ -n "$s_line" ]; then
            local script_path="$skill_dir/$s_line"
            if [ ! -f "$script_path" ]; then
                echo "FAIL: $skill_name referenced script $s_line does not exist"
                return 1
            fi
            if [ ! -x "$script_path" ]; then
                echo "FAIL: $skill_name referenced script $s_line is not executable (missing chmod +x)"
                return 1
            fi
        fi
    done <<INNER_EOF
$script_lines
INNER_EOF

    if [ -d "$skill_dir/scripts" ]; then
        for f in "$skill_dir/scripts"/*; do
            if [ -f "$f" ]; then
                if [ ! -x "$f" ]; then
                    echo "FAIL: $skill_name script $(basename "$f") is not executable"
                    return 1
                fi
                if grep -i -q -E "TODO|FIXME|\[placeholder\]" "$f"; then
                    echo "FAIL: $skill_name script $(basename "$f") contains placeholder text (TODO/FIXME/placeholder)"
                    return 1
                fi
            fi
        done
    fi
    
    echo "PASS: $parsed_name ($parsed_desc)"
    return 0
}

cmd_create_skill() {
    if [ $# -lt 2 ]; then
        echo "Usage: $0 create-skill <name> [description]"
        exit 1
    fi
    local name="$2"
    local desc="${3:-}"
    
    if [[ ! "$name" =~ ^[a-z0-9-]+$ ]]; then
        echo "Error: Skill name must be lowercase kebab-case (e.g., custom-skill-name)." >&2
        exit 1
    fi
    
    local skill_dir=".agents/skills/$name"
    if [ -d "$skill_dir" ]; then
        echo "Error: Skill '$name' already exists at $skill_dir." >&2
        exit 1
    fi
    
    mkdir -p "$skill_dir/scripts"
    
    cat << INNER_EOF > "$skill_dir/SKILL.md"
---
name: $name
description: ${desc:-Specialized skill for $name automation.}
scripts:
  - scripts/main.py
---

# ${name} Skill

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
INNER_EOF

    cat << INNER_EOF > "$skill_dir/scripts/main.py"
#!/usr/bin/env python3
import argparse
import sys
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_skill(args):
    """
    Main logic of the skill script.
    """
    logging.info(f"Running skill with arguments: {args}")
    # Implement operational logic here
    
    result = {
        "status": "success",
        "message": "Skill $name executed successfully",
        "data": {}
    }
    return result

def main():
    parser = argparse.ArgumentParser(description="Default Python script for agent skill $name.")
    parser.add_argument('--target', type=str, help="Target path or resource")
    parser.add_argument('--debug', action='store_true', help="Enable debug mode")
    
    args = parser.parse_args()
    
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
INNER_EOF

    chmod +x "$skill_dir/scripts/main.py"
    echo "Skill '$name' created successfully at $skill_dir"
}

cmd_list_skills() {
    local skills_dir=".agents/skills"
    if [ ! -d "$skills_dir" ]; then
        echo "Error: Skills directory $skills_dir not found." >&2
        exit 1
    fi
    
    echo "=========================================================="
    echo "          Antigravity Agent Skills Audit & Registry"
    echo "=========================================================="
    
    local audit_failed=0
    printf "%-25s | %-12s | %s\n" "Skill Name" "Status" "Description"
    echo "----------------------------------------------------------"
    
    for dir in "$skills_dir"/*; do
        if [ -d "$dir" ]; then
            local skill_name=$(basename "$dir")
            local audit_res
            local exit_code=0
            if ! audit_res=$(audit_skill "$dir" 2>&1); then
                exit_code=1
            fi
            
            local status="[PASS]"
            local detail=""
            if [ $exit_code -eq 0 ]; then
                detail=$(echo "$audit_res" | sed -E 's/^PASS: [^ ]+ \((.*)\)/\1/')
            else
                status="[FAIL]"
                detail=$(echo "$audit_res" | sed -E 's/^FAIL: //')
                audit_failed=$((audit_failed + 1))
            fi
            
            printf "%-25s | %-12s | %s\n" "$skill_name" "$status" "$detail"
        fi
    done
    
    echo "=========================================================="
    if [ $audit_failed -eq 0 ]; then
        echo "All skills are compliant and ready for use."
        return 0
    else
        echo "Audit failed! Found $audit_failed non-compliant skill(s)." >&2
        return 1
    fi
}

audit_rule() {
    local rule_file="$1"
    local rule_name=$(basename "$rule_file" .md)
    
    # Check 1: Must be .md extension
    if [[ ! "$rule_file" =~ \.md$ ]]; then
        echo "FAIL: $rule_name is not a markdown file"
        return 1
    fi
    
    # Check 2: Parse YAML frontmatter
    local line1=$(head -n 1 "$rule_file" | tr -d '\r')
    if [ "$line1" != "---" ]; then
        echo "FAIL: $rule_name does not start with YAML frontmatter delimiter (---)"
        return 1
    fi
    
    local closing_line=$(grep -n "^---" "$rule_file" | sed -n '2p' | cut -d':' -f1)
    if [ -z "$closing_line" ]; then
        echo "FAIL: $rule_name has unclosed YAML frontmatter"
        return 1
    fi
    
    local frontmatter=$(sed -n "2,$((closing_line - 1))p" "$rule_file")
    
    local parsed_name=$(echo "$frontmatter" | grep "^name:" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e "s/^'//" -e "s/'$//" -e 's/^"//' -e 's/"$//')
    local parsed_activation=$(echo "$frontmatter" | grep "^activation:" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e "s/^'//" -e "s/'$//" -e 's/^"//' -e 's/"$//')
    
    if [ -z "$parsed_name" ]; then
        echo "FAIL: $rule_name frontmatter missing 'name'"
        return 1
    fi
    
    if [ -z "$parsed_activation" ]; then
        echo "FAIL: $rule_name frontmatter missing 'activation'"
        return 1
    fi
    
    # Check 3: Validate activation parameters
    case "$parsed_activation" in
        "Manual"|"Always On")
            ;;
        "Glob")
            local parsed_pattern=$(echo "$frontmatter" | grep "^pattern:" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e "s/^'//" -e "s/'$//" -e 's/^"//' -e 's/"$//')
            if [ -z "$parsed_pattern" ]; then
                echo "FAIL: $rule_name activation is Glob but missing 'pattern'"
                return 1
            fi
            ;;
        "Model Decision")
            local parsed_desc=$(echo "$frontmatter" | grep "^description:" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e "s/^'//" -e "s/'$//" -e 's/^"//' -e 's/"$//')
            if [ -z "$parsed_desc" ]; then
                echo "FAIL: $rule_name activation is Model Decision but missing 'description'"
                return 1
            fi
            ;;
        *)
            echo "FAIL: $rule_name has invalid activation mode '$parsed_activation'"
            return 1
            ;;
    esac
    
    # Check 4: Check for placeholders in rule body
    if grep -i -q -E "TODO|FIXME|\[placeholder\]" "$rule_file"; then
        echo "FAIL: $rule_name contains placeholder text (TODO/FIXME/placeholder)"
        return 1
    fi
    
    # Return activation details for tabulated output
    local details="$parsed_activation"
    if [ "$parsed_activation" = "Glob" ]; then
        local parsed_pattern=$(echo "$frontmatter" | grep "^pattern:" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e "s/^'//" -e "s/'$//" -e 's/^"//' -e 's/"$//')
        details="Glob ($parsed_pattern)"
    elif [ "$parsed_activation" = "Model Decision" ]; then
        local parsed_desc=$(echo "$frontmatter" | grep "^description:" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e "s/^'//" -e "s/'$//" -e 's/^"//' -e 's/"$//')
        details="Model Decision ($parsed_desc)"
    fi
    
    echo "PASS: $parsed_name ($details)"
    return 0
}

cmd_create_rule() {
    if [ $# -lt 3 ]; then
        echo "Usage: $0 create-rule <name> <activation> [description_or_pattern]"
        exit 1
    fi
    local name="$2"
    local activation="$3"
    local param="${4:-}"
    
    if [[ ! "$name" =~ ^[a-z0-9-]+$ ]]; then
        echo "Error: Rule name must be lowercase kebab-case (e.g., custom-rule-name)." >&2
        exit 1
    fi
    
    local activation_mode=""
    case "$activation" in
        manual) activation_mode="Manual" ;;
        always-on) activation_mode="Always On" ;;
        model-decision) activation_mode="Model Decision" ;;
        glob) activation_mode="Glob" ;;
        *)
            echo "Error: Invalid activation mode '$activation'. Must be: manual, always-on, model-decision, or glob." >&2
            exit 1
            ;;
    esac
    
    local pattern=""
    local description=""
    if [ "$activation_mode" = "Glob" ]; then
        if [ -z "$param" ]; then
            echo "Error: Glob activation requires a glob pattern parameter (e.g., 'src/**/*.ts')." >&2
            exit 1
        fi
        pattern="$param"
    elif [ "$activation_mode" = "Model Decision" ]; then
        if [ -z "$param" ]; then
            echo "Error: Model Decision activation requires a natural language description parameter." >&2
            exit 1
        fi
        description="$param"
    fi
    
    local rule_file=".agents/rules/$name.md"
    if [ -f "$rule_file" ]; then
        echo "Error: Rule '$name' already exists at $rule_file." >&2
        exit 1
    fi
    
    mkdir -p ".agents/rules"
    
    cat << INNER_EOF > "$rule_file"
---
name: $name
activation: $activation_mode
$( [ -n "$pattern" ] && echo "pattern: \"$pattern\"" )
$( [ -n "$description" ] && echo "description: \"$description\"" )
---

# ${name} Workspace Rule

## Guidelines
- Define the coding standard or instructions for this rule here.
- Example: Prefer arrow functions over traditional function syntax.
INNER_EOF

    echo "Rule '$name' created successfully at $rule_file"
}

cmd_list_rules() {
    local rules_dir=".agents/rules"
    if [ ! -d "$rules_dir" ]; then
        echo "Error: Rules directory $rules_dir not found." >&2
        exit 1
    fi
    
    echo "=========================================================="
    echo "          Antigravity Agent Rules Audit & Registry"
    echo "=========================================================="
    
    local audit_failed=0
    printf "%-25s | %-12s | %s\n" "Rule Name" "Status" "Activation Mode"
    echo "----------------------------------------------------------"
    
    local file_found=0
    for file in "$rules_dir"/*; do
        if [ -f "$file" ]; then
            file_found=1
            local rule_name=$(basename "$file")
            local audit_res
            local exit_code=0
            if ! audit_res=$(audit_rule "$file" 2>&1); then
                exit_code=1
            fi
            
            local status="[PASS]"
            local detail=""
            if [ $exit_code -eq 0 ]; then
                detail=$(echo "$audit_res" | sed -E 's/^PASS: [^ ]+ \((.*)\)/\1/')
            else
                status="[FAIL]"
                detail=$(echo "$audit_res" | sed -E 's/^FAIL: //')
                audit_failed=$((audit_failed + 1))
            fi
            
            printf "%-25s | %-12s | %s\n" "$rule_name" "$status" "$detail"
        fi
    done
    
    if [ $file_found -eq 0 ]; then
        echo "No rules registered in $rules_dir."
    fi
    
    echo "=========================================================="
    if [ $audit_failed -eq 0 ]; then
        echo "All rules are compliant and active."
        return 0
    else
        echo "Audit failed! Found $audit_failed non-compliant rule(s)." >&2
        return 1
    fi
}

cmd_git_profile() {
    if [ ! -d .git ]; then
        echo "Error: Not a Git repository." >&2
        exit 1
    fi

    local name=""
    local email=""
    if [ "${2:-}" = "git-profile" ]; then
        name="${3:-}"
        email="${4:-}"
    else
        name="${2:-}"
        email="${3:-}"
    fi

    # Find profiles config file
    local profiles_file=""
    if [ -f ".agents/git_profiles" ]; then
        profiles_file=".agents/git_profiles"
    elif [ -f "$HOME/.git_profiles" ]; then
        profiles_file="$HOME/.git_profiles"
    fi

    # Check if a single argument matches a profile key in the config file
    if [ -n "$name" ] && [ -z "$email" ] && [ -n "$profiles_file" ] && grep -q "^${name}\.name=" "$profiles_file"; then
        local p_n=$(grep "^${name}\.name=" "$profiles_file" | cut -d'=' -f2-)
        local p_e=$(grep "^${name}\.email=" "$profiles_file" | cut -d'=' -f2-)
        echo "Setting local repository Git configuration to profile '$name'..."
        git config --local user.name "$p_n"
        git config --local user.email "$p_e"
        echo "  [SUCCESS] Local Git profile updated."
        name=""
        email=""
    fi

    if [ -n "$name" ] && [ -n "$email" ]; then
        echo "Setting local repository Git configuration..."
        git config --local user.name "$name"
        git config --local user.email "$email"
        echo "  [SUCCESS] Local Git profile updated."
    elif [ -n "$name" ] || [ -n "$email" ]; then
        if [ -n "$profiles_file" ]; then
            echo "Error: Profile '$name' not found in $profiles_file." >&2
        else
            echo "Error: Both name and email are required to set a profile." >&2
        fi
        echo "Usage:" >&2
        echo "  \$0 git-profile [name] [email]   (Set profile directly)" >&2
        echo "  \$0 git-profile [profile-key]   (Set from profiles config file)" >&2
        exit 1
    fi

    echo "=========================================================="
    echo "          Current Git User Configuration"
    echo "=========================================================="
    local local_name=$(git config --local user.name 2>/dev/null || echo "<not set>")
    local local_email=$(git config --local user.email 2>/dev/null || echo "<not set>")
    local global_name=$(git config --global user.name 2>/dev/null || echo "<not set>")
    local global_email=$(git config --global user.email 2>/dev/null || echo "<not set>")

    echo "Local Profile (This Repository):"
    echo "  user.name:  $local_name"
    echo "  user.email: $local_email"
    echo ""
    echo "Global Profile (Default):"
    echo "  user.name:  $global_name"
    echo "  user.email: $global_email"
    echo ""

    if [ -f "$profiles_file" ]; then
        echo "Available Profiles (from $profiles_file):"
        local profiles
        profiles=$(grep -E "^[a-zA-Z0-9_\-]+\.name=" "$profiles_file" | cut -d'.' -f1 | sort -u)
        for p in $profiles; do
            local p_n=$(grep "^${p}\.name=" "$profiles_file" | cut -d'=' -f2-)
            local p_e=$(grep "^${p}\.email=" "$profiles_file" | cut -d'=' -f2-)
            echo "  - \$p: \"$p_n\" <$p_e>"
        done
    fi
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
    sync-api)
        cmd_sync_api
        ;;
    log-usage)
        cmd_log_usage "$@"
        ;;
    create-adr)
        cmd_create_adr "$@"
        ;;
    release)
        cmd_release "$@"
        ;;
    create-skill)
        cmd_create_skill "$@"
        ;;
    list-skills)
        cmd_list_skills
        ;;
    create-rule)
        cmd_create_rule "$@"
        ;;
    list-rules)
        cmd_list_rules
        ;;
    git-profile)
        cmd_git_profile "$@"
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

# Write helper.ps1 wrapper script
write_template_safe ".agents/scripts/helper.ps1" << 'EOF'
# Antigravity Agent Workspace Helper Wrapper for Windows PowerShell
# Forwards arguments to helper.sh running inside Git Bash

$gitBash = "C:\Program Files\Git\bin\bash.exe"
if (-not (Test-Path $gitBash)) {
    $gitBash = (Get-Command bash.exe -ErrorAction SilentlyContinue).Source
}

if (-not $gitBash) {
    Write-Error "Git Bash is required to run Antigravity helper scripts on Windows. Please install Git for Windows (https://git-scm.com/)."
    exit 1
}

# Resolve target helper.sh script path relative to this script
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$helperSh = Join-Path $scriptPath "helper.sh"

# Format target path for Bash environment (ensure Unix style slashes)
$helperShUnix = $helperSh.Replace('\', '/')

# Execute helper.sh inside Git Bash, forwarding all arguments exactly
if ($args) {
    & $gitBash $helperShUnix @args
} else {
    & $gitBash $helperShUnix
}
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

# 9. Check Token Budget Guard
echo "Check 9: Token Budget Guard"
BUDGET_FILE=".agents/token_budget.json"
if [ -f "$BUDGET_FILE" ] && command -v jq >/dev/null 2>&1; then
    MAX_BUDGET=$(jq -r '.max_token_budget' "$BUDGET_FILE")
    CURRENT_USAGE=$(jq -r '.current_token_usage' "$BUDGET_FILE")
    THRESHOLD=$(jq -r '.alert_threshold_percent' "$BUDGET_FILE")
    
    if [ "$MAX_BUDGET" -gt 0 ]; then
        PERCENT=$(( CURRENT_USAGE * 100 / MAX_BUDGET ))
        echo "  Current token usage: $CURRENT_USAGE / $MAX_BUDGET ($PERCENT%)"
        if [ "$CURRENT_USAGE" -ge "$MAX_BUDGET" ]; then
            echo "  [FAIL] Token budget exceeded! Current: $CURRENT_USAGE, Limit: $MAX_BUDGET."
            echo "         Please save your task checkpoint in workflows/ and handover the task."
            FAILED=1
        elif [ "$PERCENT" -ge "$THRESHOLD" ]; then
            echo "  [WARNING] Token usage is at $PERCENT% of budget. Consider saving and handing over."
        else
            echo "  [PASS] Token usage is within safe budget limits."
        fi
    fi
fi

# 10. Check ADR Compliance Check
echo "Check 10: ADR Compliance Check"
ADR_ERRORS=0
if [ -f ".agents/adr.md" ]; then
    if [ -d ".agents/adrs" ]; then
        for adr_file in .agents/adrs/*.md; do
            if [ -f "$adr_file" ]; then
                base_name=$(basename "$adr_file")
                # Verify registration in adr.md
                if ! grep -q "$base_name" ".agents/adr.md"; then
                    echo "  [FAIL] Architectural Decision Record file '$base_name' is NOT registered in '.agents/adr.md'!"
                    ADR_ERRORS=$((ADR_ERRORS + 1))
                fi
                # Check for placeholders
                if grep -i -q -E "TODO|FIXME|\[placeholder\]" "$adr_file"; then
                    echo "  [FAIL] ADR file '$base_name' contains placeholder text (TODO/FIXME/placeholder)!"
                    ADR_ERRORS=$((ADR_ERRORS + 1))
                fi
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

echo "=========================================================="
if [ "$FAILED" -eq 0 ]; then
    echo "Workspace Status: VALIDATED"
    exit 0
else
    echo "Workspace Status: DEGRADED (Check issues detailed above)"
    exit 1
fi
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
echo "Architectural Blueprint written to: .agents/rules/project_rules.md"
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

