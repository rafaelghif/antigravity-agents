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
- **Isolated Feature Branches**: All development must occur on separate, isolated git feature branches. Directly committing to `main` or `master` is strictly forbidden.
- **Federated Git-Backed Memory**: Memory resides in the repository. Pulling remote updates (`git pull --rebase origin main`) automatically syncs schemas, decision records, and active task progress across the entire team without needing external databases.
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
1. **Sync**: Rebase the branch to sync with remote updates (`git pull --rebase origin main`).
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
