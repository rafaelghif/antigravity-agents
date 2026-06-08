# Global Agent Protocol (GAP)

This document dictates the absolute boundaries, operational procedures, memory constraints, and quality gates for all AI agent operations in this workspace. Compliance is mandatory for every agent execution.

---

## 1. Bootstrapping & Cognitive Alignment
- **Autonomous Bootstrapping**: At the beginning of any session or task context, the agent MUST read:
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
- **verbatim Reference**: When documenting compile, lint, or test failures, paste the exact stack traces and logs verbatim instead of describing them in general terms.

---

## 3. AI Prompt Caching & Token Optimization
To maximize prompt execution speed, leverage model-side context caching, and avoid token exhaustion, agents must strictly follow these caching protocols:
- **Cache-Friendly Memory Split**: Decouple static files (`AGENTS.md`, `project_rules.md`, `adr.md`) from dynamic ones. Static files must remain stable to hit 100% prompt cache.
- **Active Memory Cap**: Keep [.agents/memory.md](file://./.agents/memory.md) under 100 lines at all times. Once a milestone is achieved, immediately archive the checklist to [.agents/archive/](file://./.agents/archive/).
- **Targeted File Reads**: NEVER read entire source files when looking for small details. Always use precise `StartLine` and `EndLine` parameters in file-viewing tools to preserve prefix cache hits.
- **Persistent Terminal Shells**: Reuse active terminal sessions by passing `RunPersistent: true` and specifying `RequestedTerminalID`. This avoids spawning new bash subshells, which bloats terminal history logs.

---

## 4. Multi-Agent & Teamwork Coordination
To operate seamlessly in collaborative environments with other developers and autonomous agents:
- **Isolated Feature Branches**: All development must occur on separate, isolated git feature branches. Directly committing to `main` or `master` is strictly forbidden.
- **Federated Git-Backed Memory**: Memory resides in the repository. Pulling remote updates (`git pull --rebase origin main`) automatically syncs schemas, decision records, and active task progress across the entire team without needing external databases.
- **Active Lockfile Protocol**: To prevent parallel agents/developers from editing the same module:
  - Create a lockfile under `.agents/locks/<module_name>.lock` containing: branch name, active owner (agent or human name), lock timestamp, and file paths.
  - Before editing any file, check `.agents/locks/`. If a lock exists for files you intend to edit, do NOT proceed. Coordinate with the lock owner, wait for release, or notify the user.
  - Delete the lockfile immediately upon committing your changes or closing the branch.
- **Pre-Merge Compaction Protocol**: To prevent merge conflicts on `memory.md` during integration:
  - Before merging a branch into `main`/`master`, the agent/developer MUST archive their active task checklist from `memory.md` into a new file: `.agents/archive/sprint_<branch_name>.md`.
  - Reset the active checklists and sprint metrics in `memory.md` back to an idle/blank state, referencing the new archive file.
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
2. **Lock**: Create `.agents/locks/<module>.lock` and set the target task to `[/]` in `memory.md`.
3. **Edit**: Modify a single file or write a test (under TDD guidelines).
4. **Compile & Test**: Run local validation commands. If tests fail, go back to step 3.
5. **Commit**: Stage and commit using conventional commit format: `type(scope): description`.
6. **Sync Memory**: Update [.agents/memory.md](file://./.agents/memory.md) task checklist to `[x]` and update `schema.md` (if database columns or API routes changed).
7. **Unlock**: Delete the lock file.

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
1. **Trigger Reconnaissance**: Immediately execute the `codebase-recon` skill to discover the project's language, framework, folder structure, config files, and relational database migrations/schemas.
2. **Populate Project Blueprint**:
   - Write the discovered technical stack, directories boundary gate, and validation commands (build, test, lint) directly into [.agents/project_rules.md](file://./.agents/project_rules.md).
3. **Populate Database Schema Map**:
   - Map all relational database models, tables, columns, and API routes found, and organize them into specialized domain-driven schemas under [.agents/schemas/](file://./.agents/schemas/).
   - Update the high-level index map inside [.agents/schema.md](file://./.agents/schema.md) to link to these domain schemas.
4. **Initialize Active Memory**:
   - Populate [.agents/memory.md](file://./.agents/memory.md) with the detected system topology, active branch, and initial task list.
5. **Autoprovision Commit**: Commit these initialized configuration files using git: `chore(agent): autodetect project stack and initialize memory blueprints`.
Once the blueprints are populated, the agent must strictly follow the detected project rules for all code mutations.
