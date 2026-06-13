#!/usr/bin/env bash

# Antigravity Agent Workspace Bootstrapper
# This script initializes a clean, decoupled agent memory and protocol setup in any project repository.

set -euo pipefail

# Initialize Git if not present (ensures doctor and hooks pass seamlessly)
if [ ! -d .git ]; then
    echo "Git repository not detected. Initializing Git repository..."
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
cat << 'EOF' > AGENTS.md
# Global Agent Protocol (GAP)

This document dictates the absolute boundaries, operational procedures, memory constraints, and quality gates for all AI agent operations in this workspace. Compliance is mandatory for every agent execution.

---

## 1. Bootstrapping & Cognitive Alignment
- **Autonomous Bootstrapping**: At the beginning of any session or task context, the agent MUST read the core files. To maximize prompt prefix cache hits, the agent or the loading interface MUST retrieve these files in the exact sequence from *Most Static* to *Most Dynamic*:
  1. The Global Agent Protocol (this file: [AGENTS.md](file://./AGENTS.md)).
  2. The Project-Specific Rules, if available (e.g. [.agents/project_rules.md](file://./.agents/project_rules.md)).
  3. The Schema Reference database, if available (e.g. [.agents/schema.md](file://./.agents/schema.md)).
  4. The Active Memory Ledger ([.agents/memory.md](file://./.agents/memory.md)).
- **Autonomy Principle**: The agent must rely on these documents and the codebase layout rather than asking the user repetitive or basic design questions. If a design pattern is missing or a user's instruction is ambiguous, default to standard industry best practices or ask a direct, clear multiple-choice question.

---

## 2. Zero-Hallucination & Import Verification Gates
- **Fact-Checking over Guessing**: Never assume a file exists, a package is installed, or a function signature is correct.
- **Symbol Verification Gate**: Before writing an import statement or invoking a function, the agent MUST run `view_file` or `grep_search` to verify:
  1. The path exists.
  2. The exact spelling of the exported symbol/module.
- **Batch Verification and Line Capping**: To prevent token bloat during verification, the agent MUST use precise `StartLine` and `EndLine` parameters in `view_file` to read only the imports/definitions needed, or run batch `grep_search` operations instead of parsing entire source files.
- **verbatim Reference**: When documenting compile, lint, or test failures, paste the exact stack traces and logs verbatim instead of describing them in general terms.

---

## 3. AI Prompt Caching & Token Optimization
To maximize prompt execution speed, leverage model-side context caching, and avoid token exhaustion, agents must strictly follow these caching protocols:
- **Cache-Friendly Memory Split**: Decouple static files (`AGENTS.md`, `project_rules.md`, `adr.md`) from dynamic ones. Static files must remain stable to hit 100% prompt cache.
- **Active Memory Cap**: Keep [.agents/memory.md](file://./.agents/memory.md) under 100 lines at all times. Once a milestone is achieved, immediately archive the checklist to [.agents/archive/](file://./.agents/archive/).
- **Hierarchical Task Trees (Memory Scaling)**: For large projects or complex tasks, the agent MUST NOT store granular, detailed checklists in `memory.md`. Instead, create task-specific workflow files under `.agents/workflows/task_<name>.md`. Track only high-level epic milestones in the core `memory.md`, and lazy-load the workflow files as needed.
- **Targeted File Reads**: NEVER read entire source files when looking for small details. Always use precise `StartLine` and `EndLine` parameters in file-viewing tools to preserve prefix cache hits.
- **Persistent Terminal Shells**: Reuse active terminal sessions by passing `RunPersistent: true` and specifying `RequestedTerminalID`. This avoids spawning new bash subshells, which bloats terminal history logs.

---

## 4. Multi-Agent & Teamwork Coordination
To operate seamlessly in collaborative environments with other developers and autonomous agents:
- **Isolated Feature Branches**: The agent must operate exclusively on the feature branch created by the user. Creating, switching, pushing, or pulling branches is forbidden for the agent; these tasks are strictly handled by the user.
- **Federated Git-Backed Memory**: Memory resides in the repository. The user synchronizes schemas, decision records, and active task progress across the team by running git pull/push.
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

## 5. Stateful Task Checklist
The active checklist inside [.agents/memory.md](file://./.agents/memory.md) must strictly follow this lifecycle:
- `[ ]` **Unstarted**: Proposed task.
- `[/]` **In Progress**: Active task. **CRITICAL**: Only ONE task can be marked `[/]` at a time. The agent must focus 100% on this task.
- `[x]` **Completed**: Done, verified, and committed.

---

## 6. The Atomic Commit Loop (Strict Discipline)
Every code mutation must execute in an atomic, sequential loop:
1. **Sync**: Verify that the workspace is on the correct branch and that there are no uncommitted changes (other than locks or memory files).
2. **Lock**: Run `.agents/scripts/helper.sh lock <module>` and set the target task to `[/]` in `memory.md`.
3. **Edit**: Modify a single file or write a test (under TDD guidelines).
4. **Compile & Test**: Run local validation commands. If tests fail, go back to step 3.
5. **Workspace Validation**: Run `./.agents/scripts/helper.sh validate` to verify memory limits, lack of hardcoded secrets, and environment boundary conformance.
6. **Commit**: Stage and commit using conventional commit format: `type(scope): description`. Note: The installed Git `post-commit` hook will automatically execute `.agents/scripts/helper.sh sync-git` to keep `memory.md` updated.
7. **Sync Memory**: Update [.agents/memory.md](file://./.agents/memory.md) task checklist to `[x]` and update `schema.md` (if database columns or API routes changed).
8. **Unlock**: Run `.agents/scripts/helper.sh unlock <module>`.

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
- **Index Reference**: The main [.agents/schema.md](file://./.agents/schema.md) file acts strictly as a high-level index mapping domain-specific database and API layouts.
- **Domain Segmentation**: Schemas and contracts must be grouped by function under [.agents/schemas/](file://./.agents/schemas/) (e.g., `admin_and_auth.md`, `assets_and_taxonomy.md`).
- **Targeted Reading**: When modifying a resource, the agent MUST ONLY load the relevant domain schema file. Loading the entire database schema map for localized edits is strictly forbidden.
- **Incremental Growth**: These domain-specific schemas grow incrementally when new modules are registered under the schema index map.

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
cat << 'EOF' > .agents/memory.md
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

## 3. Reference Links Index
- **Core Guidelines**: [AGENTS.md](file://../AGENTS.md)
- **Project Specific Rules**: [project_rules.md](file://./project_rules.md)
- **Database Schema**: [schema.md](file://./schema.md)
- **Design Decisions**: [adr.md](file://./adr.md)
- **Sprint Archives**: [archive/](file://./archive/)
EOF

# 4. Write .agents/project_rules.md template
cat << 'EOF' > .agents/project_rules.md
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
cat << 'EOF' > .agents/schema.md
# Technical Schema & Reference Database (SRD) - Index Map

This file serves as the high-level index for the project's technical schemas, database specifications, and API contracts.

---

## 1. Domain Schemas Index
- [Default Module](file://./schemas/default_module.md) -> Reference: [default_module.md](file://./schemas/default_module.md)
EOF

# 6. Write default_module.md template
cat << 'EOF' > .agents/schemas/default_module.md
# Schema: Default Module

Description of tables and APIs in this domain.

---

## 1. Relational Database Tables
- `example_table` (id, name)
EOF

# 7. Write .agents/adr.md template
cat << 'EOF' > .agents/adr.md
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
cat << 'EOF' > .agents/skills/codebase-recon/SKILL.md
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
cat << 'EOF' > .agents/skills/git-ops/SKILL.md
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
cat << 'EOF' > .agents/skills/test-driven-patch/SKILL.md
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
cat << 'EOF' > .agents/skills/infra-provisioner/SKILL.md
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
cat << 'EOF' > .agents/skills/security-ci-audit/SKILL.md
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
cat << 'EOF' > .agents/skills/code-review/SKILL.md
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
cat << 'EOF' > .agents/skills/impact-analysis/SKILL.md
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
cat << 'EOF' > .agents/scripts/helper.sh
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
    local lockfile="$LOCKS_DIR/$module.lock"
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
    local lockfile="$LOCKS_DIR/$module.lock"
    if [ ! -f "$lockfile" ]; then
        echo "Warning: Module '$module' is not locked." >&2
        exit 0
    fi
    rm -f "$lockfile"
    echo "Released lock for module '$module'"
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
    sed -n '/### Sprint Tasks Checklist/,/---/p' "$MEMORY_FILE" | grep -v '---' > "$archive_file"

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
        read -p "Enter Language/Framework (e.g. Node/TypeScript, Go, Python) (default: Node/TypeScript): " tech_stack
        if [ -z "$tech_stack" ]; then tech_stack="Node/TypeScript"; fi
    fi

    if [ -z "$arch_pattern" ]; then
        read -p "Enter Architectural Pattern (e.g. Clean, MVC, Hexagonal) (default: MVC): " arch_pattern
        if [ -z "$arch_pattern" ]; then arch_pattern="MVC"; fi
    fi

    if [ -z "$db_orm" ]; then
        read -p "Enter Database/ORM (e.g. Prisma, PostgreSQL, None) (default: None): " db_orm
        if [ -z "$db_orm" ]; then db_orm="None"; fi
    fi

    if [ -z "$env_vars" ]; then
        read -p "Enter config variables (comma-separated, e.g. PORT,DATABASE_URL) (default: None): " env_vars
        if [ -z "$env_vars" ]; then env_vars=""; fi
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

    # Install Git post-commit Hook template
    if [ -f .agents/hooks/post-commit ]; then
        mkdir -p .git/hooks
        cp .agents/hooks/post-commit .git/hooks/post-commit
        chmod +x .git/hooks/post-commit
        echo "Git post-commit hook installed."
    fi

    # Scaffolding folders if requested
    if [ "$scaffold" = "y" ] || [ "$scaffold" = "yes" ]; then
        echo "Scaffolding directory structure..."
        mkdir -p src tests config
        
        # Node/TypeScript Template
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
        
        # Go Template
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

        # Python Template
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
        .agents/scripts/recon.sh
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
    
    # Check post-commit hook
    if [ -f .git/hooks/post-commit ] && [ -x .git/hooks/post-commit ]; then
        echo "  [PASS] post-commit Git hook is installed and executable."
    else
        echo "  [WARNING] Git post-commit hook is missing or not executable."
        echo "            To install: cp .agents/hooks/post-commit .git/hooks/post-commit && chmod +x .git/hooks/post-commit"
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
            linter_cmd=$(grep "Linter command" .agents/project_rules.md | grep -o "\`.*\`" | tr -d "\`" || echo "")
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
            test_runner=$(grep "Test runner command" .agents/project_rules.md | grep -o "\`.*\`" | tr -d "\`" || echo "")
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
cat << 'EOF' > .agents/scripts/recon.sh
#!/usr/bin/env bash
# Antigravity Agent Core - Autonomous Reconnaissance Script
# Scans the target workspace to automatically configure the agent environment blueprints.

set -euo pipefail

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

echo "Detected Stack: $TECH_STACK"
echo "Detected Build: $BUILD_CMD"
echo "Detected Test:  $TEST_CMD"
echo "Detected Lint:  $LINT_CMD"

# 2. Directory Structure Mapping
NL=$'\n'
DIRS=""
for d in src lib app apps controllers views handlers models services repositories routes tests test config pkg cmd; do
    if [ -d "$d" ]; then
        DIRS="${DIRS}${NL}  - \`$d/\` -> Project workspace component"
    fi
done

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
cat << PAB_EOF > "$PROJECT_RULES_FILE"
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
PAB_EOF

# 6. Database schema domain mapping (Auto-discover domain tables or modules)
mkdir -p "$SCHEMAS_DIR"

# Write a basic schema.md index file
cat << SRD_EOF > "$SCHEMA_INDEX_FILE"
# Technical Schema & Reference Database (SRD) - Index Map

This file serves as the high-level index for the project's technical schemas, database specifications, and API contracts.

---

## 1. Domain Schemas Index
- [Default Module](file://./schemas/default_module.md) -> Reference: [default_module.md](file://./schemas/default_module.md)
SRD_EOF

# Check for custom schema files
if [ "$DB_STACK" = "Prisma ORM (schema: prisma/schema.prisma)" ]; then
    # Create prisma schema domain layout
    cat << PRISMA_EOF > "$SCHEMAS_DIR/database_schema.md"
# Schema: Database Models (Prisma)

Automatically discovered Prisma model entities:

---

## 1. Relational Database Tables / Models
$(grep -E "^model " prisma/schema.prisma | cut -d' ' -f2 | sed 's/^/- /' || true)
PRISMA_EOF

    cat << SRD_EOF >> "$SCHEMA_INDEX_FILE"
- [Database Schema (Prisma)](file://./schemas/database_schema.md) -> Reference: [database_schema.md](file://./schemas/database_schema.md)
SRD_EOF
fi

echo "=========================================================="
echo "Reconnaissance Complete! Blueprints updated successfully."
echo "=========================================================="
EOF

# 11. Write validate.sh script
cat << 'EOF' > .agents/scripts/validate.sh
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
git fetch origin >/dev/null 2>&1 || true

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
cat << 'EOF' > .agents/hooks/pre-commit
#!/usr/bin/env bash
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
    linter_cmd=$(grep "Linter command" .agents/project_rules.md | grep -o "\`.*\`" | tr -d "\`" || echo "")
    if [ -n "$linter_cmd" ] && [ "$linter_cmd" != "echo 'No linter found'" ]; then
        echo "Running linter: $linter_cmd..."
        if ! eval "$linter_cmd"; then
            echo "Error: Linter check failed! Aborting commit." >&2
            exit 1
        fi
        echo "  [PASS] Linter check passed."
    fi

    test_runner=$(grep "Test runner command" .agents/project_rules.md | grep -o "\`.*\`" | tr -d "\`" || echo "")
    if [ -n "$test_runner" ] && [ "$test_runner" != "echo 'No test suite found'" ]; then
        echo "Running test suite: $test_runner..."
        if ! eval "$test_runner"; then
            echo "Error: Tests failed! Aborting commit." >&2
            exit 1
        fi
        echo "  [PASS] All tests passed."
    fi
fi
EOF

cat << 'EOF' > .agents/hooks/post-commit
#!/usr/bin/env bash
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
EOF

if [ -f .agents/bootstrap.sh ]; then chmod +x .agents/bootstrap.sh; fi
if [ -f .agents/scripts/helper.sh ]; then chmod +x .agents/scripts/helper.sh; fi
if [ -f .agents/scripts/recon.sh ]; then chmod +x .agents/scripts/recon.sh; fi
if [ -f .agents/scripts/validate.sh ]; then chmod +x .agents/scripts/validate.sh; fi
if [ -f .agents/hooks/pre-commit ]; then chmod +x .agents/hooks/pre-commit; fi
if [ -f .agents/hooks/post-commit ]; then chmod +x .agents/hooks/post-commit; fi

if [ -d .git ]; then
    mkdir -p .git/hooks
    cp .agents/hooks/pre-commit .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit
    cp .agents/hooks/post-commit .git/hooks/post-commit
    chmod +x .git/hooks/post-commit
    echo "Git pre-commit and post-commit hooks installed."
fi


# Run auto-recon immediately to initialize configuration blueprints
echo "Running autonomous reconnaissance to initialize workspace..."
if [ -f .agents/scripts/recon.sh ]; then
    .agents/scripts/recon.sh
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
.agents/scripts/helper.sh doctor
echo "=========================================================="

# Save a copy of the bootstrapper inside .agents/ for future updates/resets
if [ -f bootstrap.sh ]; then
    cp bootstrap.sh .agents/bootstrap.sh
    chmod +x .agents/bootstrap.sh
fi

# Self-cleanup if bootstrap.sh is executed from the project root
if [ -f bootstrap.sh ]; then
    echo "Cleaning up root bootstrapper script..."
    rm -f bootstrap.sh
fi

