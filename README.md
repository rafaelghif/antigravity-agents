# Antigravity Agent Core (AAC) - 1% World-Class Developer Agent Workspace

AAC is an elite, project-agnostic operational configuration and workspace blueprint for AI software engineering agents (such as Gemini, Claude, and GPT-4). It enforces extreme developer discipline, enables zero-hallucination execution, maximizes token efficiency (prompt caching), and supports safe, conflict-free teamwork collaboration.

---

## 1. Directory Structure Blueprint

When initialized in a project, the directory layout is structured as follows:

```
[Project Root]
  ├── AGENTS.md                   <-- Static: Global Agent Protocol (cached)
  ├── README.md                   <-- Static: Developer handbook
  └── .agents/
        ├── bootstrap.sh          <-- Static: Executable bootstrapper script
        ├── project_rules.md      <-- Static: Tech Stack, coding rules, & gates (cached)
        ├── schema.md             <-- Semi-Static: Database & API specs index
        ├── adr.md                <-- Static: Architectural Design Records (cached)
        ├── memory.md             <-- Dynamic: Active task state (<100 lines)
        ├── schemas/              <-- Semi-Static: Domain-driven schema files (lazy-loaded)
        │     └── default_module.md
        ├── skills/               <-- Static: Generalized parameterizable agent skills
        │     ├── codebase-recon/
        │     ├── git-ops/
        │     ├── test-driven-patch/
        │     ├── infra-provisioner/
        │     ├── security-ci-audit/
        │     └── code-review/
        ├── locks/                <-- Dynamic: Module locks preventing parallel edits
        ├── workflows/            <-- Project-specific implementation plans
        └── archive/              <-- Historical: Completed sprint/checklists archives
```

---

## 2. Core Features & Capabilities

### 2.1. Autonomous Adaptation Protocol (AAP)
No manual configuration is needed when starting a new project. On the first turn, if the workspace blueprints (`project_rules.md` and `schema.md`) are empty templates:
1. The agent triggers the [codebase-recon](file://./.agents/skills/codebase-recon/SKILL.md) skill.
2. It autodetects the programming language, framework boundaries, config files, and DB migration schemas.
3. It autonomously writes findings into [project_rules.md](file://./.agents/project_rules.md) and creates domain-scoped documents inside `schemas/`.
4. It commits this initialization: `chore(agent): autodetect project stack and initialize memory blueprints`.

### 2.2. Federated Git-Backed Team Memory
* **Zero External DBs**: Memory travels *inside* the repository. Teammates pull/push memory files (`schema.md`, `project_rules.md`, archives) via Git standard rebase/merges.
* **Module Lockfiles**: To prevent parallel agents/developers from editing the same modules, agents register lockfiles in `.agents/locks/` before editing files and delete them upon commit.
* **Pre-Merge Compaction**: To prevent merge conflicts on `memory.md`, checklists are archived to `archive/sprint_<branch_name>.md` and cleared in `memory.md` pre-merge.

### 2.3. Caching & Token Optimization
* **Static vs. Dynamic Decoupling**: Large files (`AGENTS.md`, `project_rules.md`, `adr.md`) remain static to hit model-side prompt cache 100% of the time.
* **Dynamic Memory Cap**: The active [memory.md](file://./.agents/memory.md) is strictly capped at 100 lines. Older sprint data is moved to `archive/`.
* **Domain Schemas Split**: Large database schemas are split into individual domain files under `schemas/`. The agent only reads the specific file relevant to the active task, saving thousands of tokens per message.

### 2.4. Zero-Hallucination & Testing Rigor
* **Symbol Verification Gate**: The agent must run `view_file` or `grep_search` to verify imports or function signatures before writing them.
* **Stateful Checklist**: Tasks follow a strict notation: `[ ]` (Unstarted), `[/]` (In Progress), `[x]` (Completed). **Only one** task can be marked `[/]` at a time.
* **Atomic Commit Loop**: Edit -> Test -> Commit -> Sync Memory -> Unlock. Changes are committed instantly as soon as tests pass, facilitating fast recovery.

---

## 3. How to Install on a New Project

To bootstrap any target repository:

### Method A: Single Command (Via Bootstrap Script)
1. Copy the [.agents/bootstrap.sh](file://./.agents/bootstrap.sh) script to the root of your target project.
2. Make it executable and run it:
   ```bash
   chmod +x .agents/bootstrap.sh && ./.agents/bootstrap.sh
   ```
3. Commit the initialized setup:
   ```bash
   git add AGENTS.md .agents/ && git commit -m "chore(infra): initialize antigravity agent core"
   ```

### Method B: Manual Copying
Simply copy the `AGENTS.md` and `.agents/` folder directly to the root of your target project repository and commit them.

---

## 4. How to Run & Operate the Agent

1. **Alignment Turn**: Once installed, open a session with the agent. The agent will run the Autonomous Adaptation Protocol (AAP) to map your codebase configurations, databases, and routes.
2. **Setup Sprint Target**: Edit [.agents/memory.md](file://./.agents/memory.md) to add your target checklist under `### Sprint Tasks Checklist`.
3. **Execution**: The agent will run the Atomic Commit Loop, editing code, running test commands specified in `project_rules.md`, committing files individually, and checking off tasks.
4. **Peer Review**: When a feature branch is ready, the agent generates a PR summary handbook under `.agents/workflows/pr_review_<branch_name>.md` and runs the Pre-Merge Compaction to clean up the default memory.
