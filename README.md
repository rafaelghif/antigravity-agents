# Antigravity Agent Core (AAC) 🚀

> **A project-agnostic operational configuration and workspace blueprint designed for AI software engineering agents (Gemini, Claude, GPT-4). It enforces clean development boundaries, guarantees token-efficiency (prompt caching), and keeps your workspace safe and secure.**
>
> Created by: **Muhammad Rafael Ghifari**  
> Contact Business: [business.rafaelghifari@gmail.com](mailto:business.rafaelghifari@gmail.com)  
> LinkedIn: [rafaelghifari](https://www.linkedin.com/in/rafaelghifari/)  
> GitHub Profile: [rafaelghif](https://github.com/rafaelghif)  
> Project Repository: [antigravity-agents](https://github.com/rafaelghif/antigravity-agents)

---

## 🚀 30-Second Quick Start

Get any repository agent-ready in a single step:

### Step 1: Bootstrap the Repository
Navigate to your project root and execute the bootstrapper:
```bash
# Option A: From a locally cloned antigravity-agents repo
/path/to/antigravity-agents/bootstrap.sh

# Option B: Run directly via curl
curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/bootstrap.sh | bash
```

### Step 2: Scaffold Your Stack (Optional)
If it's an empty project, run the interactive initialization wizard:
```bash
./.agents/scripts/helper.sh init
```

### Step 3: Verify Health & Status
Ensure the workspace is healthy and ready:
```bash
./.agents/scripts/helper.sh doctor
```

---

## 📖 Table of Contents
1. [Directory Structure Blueprint](#1-directory-structure-blueprint)
2. [Core Features & Capabilities](#2-core-features--capabilities)
3. [Step-by-Step Setup Guide](#3-step-by-step-setup-guide)
   - [Scenario A: Starting a Brand New / Empty Project](#scenario-a-starting-a-brand-new--empty-project)
   - [Scenario B: Integrating into an Existing Project](#scenario-b-integrating-into-an-existing-project)
4. [Operational Scripts Guide (`helper.sh`)](#4-operational-scripts-guide-helpersh)
5. [Typical Workflow for the Agent](#5-typical-workflow-for-the-agent)
6. [Core Rules & Architecture Purity](#6-core-rules--architecture-purity)

---

## 1. Directory Structure Blueprint

When initialized in a project, the directory layout is structured as follows:

```
[Project Root]
  ├── bootstrap.sh                <-- Bootstrapper entrypoint (automatically deletes itself)
  ├── AGENTS.md                   <-- Static: Global Agent Protocol (cached)
  ├── README.md                   <-- Static: Developer handbook
  └── .agents/                    <-- Workspace operational directory (generated)
        ├── bootstrap.sh          <-- Local backup of the bootstrapper script
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

## 3. Step-by-Step Setup Guide

No matter if you are an expert developer or have zero coding experience, setting up Antigravity is as easy as running a single command.

### Scenario A: Starting a Brand New / Empty Project

Follow these steps if you are starting a project from a completely empty folder:

#### **Step 1: Open Terminal and Go to Your Folder**
Create a new folder for your project, open your terminal (command prompt), and navigate to it:
```bash
mkdir my-brand-new-project
cd my-brand-new-project
```

#### **Step 2: Run the Bootstrapper**
Run this one-liner command to download and run the bootstrapper:
```bash
curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/bootstrap.sh | bash
```
*(Alternatively, if you cloned the repo locally, run: `/path/to/antigravity-agents/bootstrap.sh`)*

> [!NOTE]
> The script will automatically initialize Git for you and clean itself up from the root when done.

#### **Step 3: Run the Initialization Wizard**
Configure your project details (scaffolding directories and template config files) by running the wizard:
```bash
./.agents/scripts/helper.sh init
```
The wizard will interactively ask you:
1. **Project Name**
2. **Language/Stack** (Node/TypeScript, Go, Python, etc.)
3. **Architecture** (MVC, Clean, Hexagonal)
4. **Database/ORM** (Prisma, PostgreSQL, None)
5. **Environment Variables** (like `PORT`, `DATABASE_URL`)

It will generate the folder structures and config templates instantly. You are now ready to let your AI agent code!

---

### Scenario B: Integrating into an Existing Project

Follow these steps if you already have a codebase and want to add Antigravity:

#### **Step 1: Navigate to Your Project Root**
Open your terminal and go to your existing project folder:
```bash
cd /path/to/your/existing-project
```

#### **Step 2: Run the Bootstrapper**
Execute the script to configure the workspace around your current code:
```bash
curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/bootstrap.sh | bash
```
The script will autodetect your programming language, linter, tests, and database migrations, and write the project settings to `.agents/project_rules.md` automatically!

#### **Step 3: Run Diagnostics & Commit**
Verify that your existing workspace passes the agent safety checks:
```bash
./.agents/scripts/helper.sh doctor
```
If everything is healthy, stage the configurations and make your first validated commit:
```bash
git add AGENTS.md .agents/
./.agents/scripts/helper.sh commit chore core "initialize antigravity agent workspace"
```

---

## 4. Operational Scripts Guide (`helper.sh`)

Once bootstrapped, all operations are managed through `./.agents/scripts/helper.sh`. Here is a quick reference:

| Command | Usage | Description |
|---|---|---|
| `init` | `./.agents/scripts/helper.sh init` | Launches the interactive setup questionnaire to scaffold directories, configurations, and file templates. |
| `recon` | `./.agents/scripts/helper.sh recon` | Runs the autonomous codebase scanner to map stacks, directories, databases, and routes. |
| `validate` | `./.agents/scripts/helper.sh validate` | Audits the project for secrets, memory cap limits, and domain decoupling. |
| `doctor` | `./.agents/scripts/helper.sh doctor` | Checks workspace health, script permissions, Git hook installation, and active locks. |
| `commit` | `./.agents/scripts/helper.sh commit [type] [scope] [desc] [files...]` | Runs workspace validations, checks the project's linter and test suite, and executes a Git conventional commit (supports `--no-verify`/`--no-test` to bypass checks). |
| `sync-git` | `./.agents/scripts/helper.sh sync-git` | Synchronizes the active branch and last commit hash in `memory.md`. |
| `lock` | `./.agents/scripts/helper.sh lock <module>` | Locks a specific module to prevent parallel developers or agents from modifying the same files simultaneously. |
| `unlock` | `./.agents/scripts/helper.sh unlock <module>` | Releases the lock on a module. |
| `archive` | `./.agents/scripts/helper.sh archive` | Archives the completed checklists from `memory.md` to `archive/` pre-merge to prevent merge conflicts. |

---

## 5. Typical Workflow for the Agent

When an AI Agent starts working on a task, it must strictly follow these steps to ensure clean history and zero bugs:

1. **Verify State**: Verify that the workspace is on the correct branch and clean.
2. **Lock Module**: Acquire the module lock to prevent conflicts:
   ```bash
   ./.agents/scripts/helper.sh lock <module_name>
   ```
3. **Implement Feature**: Write code & tests under TDD guidelines.
4. **Automated Verification & Local Commit**: Stage, validate, run tests, and commit cleanly in one step:
   ```bash
   ./.agents/scripts/helper.sh commit feat core "add new feature implementation"
   ```
5. **Unlock Module**: Release the lock:
   ```bash
   ./.agents/scripts/helper.sh unlock <module_name>
   ```
6. **Merge Preparation**: Run `./.agents/scripts/helper.sh archive` to compact checklists before merging to `main`/`master`.

---

## 6. Core Rules & Architecture Purity

Antigravity Workspace enforces these key rules on AI agents:
- **No Remote Git operations**: The agent is **forbidden** from running `git pull`, `git push`, `git fetch`, or `git checkout -b` to prevent conflicts. Branch management and pushing to remote repos is handled exclusively by **you** (the user).
- **Hardcoded Secret Scan**: The agent cannot commit if there are passwords, private keys, or API tokens exposed in the codebase (scanned via `validate.sh`).
- **Context Preservation**: Keeps the task checklists small and modular (`memory.md` capped at 100 lines) to achieve 100% prompt cache hits, making agent invocations 80% faster and cheaper.
