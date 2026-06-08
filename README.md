# Antigravity Agent Core (AAC) - Plug-and-Play Developer Agent Workspace

AAC is a project-agnostic operational configuration and workspace blueprint designed for AI software engineering agents (such as Gemini, Claude, and GPT-4). It enforces developer discipline, enables zero-hallucination execution, optimizes token efficiency (prompt caching), and supports safe, conflict-free teamwork collaboration.

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
        ├── scripts/              <-- Workspace management scripts
        │     ├── helper.sh       <-- Main command dispatcher
        │     ├── recon.sh        <-- Auto-reconnaissance scanner
        │     └── validate.sh     <-- Security and standards validator
        └── archive/              <-- Historical: Completed sprint/checklists archives
```

---

## 2. Core Features & Capabilities

### 2.1. Project Initialization & Scaffolding Wizard
If you are starting a project from scratch, running the initialization command launches an interactive prompt wizard that guides you (or the agent) through setting up:
- Project name
- Target language/framework stack (e.g. Node/TypeScript, Go, Python)
- Architectural pattern (e.g. MVC, Clean, Hexagonal)
- Target database / ORM configuration (e.g. Prisma, PostgreSQL, None)
- Required configuration environment variable keys
- Option to automatically scaffold project folders and file templates (e.g. `package.json`, `go.mod`, `main.go`, `main.py`, `.env`)

### 2.2. Autonomous Adaptation Protocol (AAP)
If deployed in an existing codebase, the workspace autodetects the programming language, framework, database migrations, testing commands, and linter configurations. It automatically updates `project_rules.md` and generates relational schema maps inside `schemas/` without manual setup.

### 2.3. Workspace Validator & Security Gate
Ensures strict coding and security practices before code is staged or committed:
- **Secret Scanner**: Detects hardcoded credentials, private keys, passwords, and API keys.
- **Memory Cap Guard**: Keeps `memory.md` under 100 lines for prompt cache hits.
- **Purity Verifier**: Flags raw environment variable reads (e.g., `process.env` or `os.Getenv`) outside config adapters.

---

## 3. How to Install & Bootstrap

To bootstrap any repository (new or existing):

1. Copy the `.agents/bootstrap.sh` script to your project root.
2. Make it executable and run it:
   ```bash
   chmod +x .agents/bootstrap.sh && ./.agents/bootstrap.sh
   ```
3. Commit the initialized setup:
   ```bash
   git add AGENTS.md .agents/ && git commit -m "chore(infra): initialize antigravity agent workspace"
   ```

---

## 4. Operational Scripts Guide (`helper.sh`)

Manage your workspace using the helper command dispatcher:

| Command | Usage | Description |
|---|---|---|
| `init` | `./.agents/scripts/helper.sh init` | Launches the interactive setup questionnaire to scaffold directories, configurations, and file templates. |
| `recon` | `./.agents/scripts/helper.sh recon` | Runs the autonomous codebase scanner to map stacks, directories, databases, and routes. |
| `validate` | `./.agents/scripts/helper.sh validate` | Audits the project for secrets, memory cap limits, and domain decoupling. |
| `doctor` | `./.agents/scripts/helper.sh doctor` | Checks workspace health, script permissions, Git hook installation, and active locks. |
| `sync-git` | `./.agents/scripts/helper.sh sync-git` | Synchronizes the active branch and last commit hash in `memory.md`. |
| `lock` | `./.agents/scripts/helper.sh lock <module>` | Locks a specific module to prevent editing conflicts with other agents. |
| `unlock` | `./.agents/scripts/helper.sh unlock <module>` | Releases a locked module lock file. |
| `archive` | `./.agents/scripts/helper.sh archive` | Archives the completed checklists from `memory.md` to `archive/` pre-merge. |

---

## 5. Typical Workflow for the Agent

1. **Onboarding**: Bootstrapping creates configuration blueprints.
2. **Interactive Setup / Recon**: Run `helper.sh init` (for new projects) or `helper.sh recon` (for existing code) to fill out directories and tech stacks.
3. **Setup Sprint Target**: Set active task items under `memory.md`'s checklists.
4. **Development Loop**:
   - Lock module: `./.agents/scripts/helper.sh lock <module_name>`
   - Write code & tests under TDD guidelines.
   - Compile & Test.
   - Run validation: `./.agents/scripts/helper.sh validate` to pass security gates.
   - Commit changes using Git conventional commits format: `type(scope): description`.
   - Release lock: `./.agents/scripts/helper.sh unlock <module_name>`
5. **Merge Preparation**: Run `./.agents/scripts/helper.sh archive` to compact logs before merging to `main`/`master`.
