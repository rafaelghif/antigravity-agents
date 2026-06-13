# Antigravity Agent Core (AAC) 🚀

<p align="center">
  <a href="https://github.com/rafaelghif/antigravity-agents/blob/main/LICENSE"><img src="https://img.shields.io/github/license/rafaelghif/antigravity-agents?style=flat-square&color=blue" alt="License"></a>
  <a href="https://github.com/rafaelghif/antigravity-agents/pulls"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square" alt="PRs Welcome"></a>
  <a href="https://github.com/rafaelghif/antigravity-agents/stargazers"><img src="https://img.shields.io/github/stars/rafaelghif/antigravity-agents?style=flat-square&color=yellow" alt="Stars"></a>
  <a href="https://github.com/rafaelghif/antigravity-agents/network/members"><img src="https://img.shields.io/github/forks/rafaelghif/antigravity-agents?style=flat-square&color=lightgrey" alt="Forks"></a>
</p>

**Antigravity Agent Core** is a project-agnostic operational workspace layout and developer protocol designed specifically for AI software engineering agents (such as Gemini, Claude, GPT-4, Cursor, Aider, and local LLMs). 

It enforces developer discipline, enables zero-hallucination execution, optimizes token efficiency (reducing API cost and latency by up to 80% through model-side prompt caching), and secures the codebase against hardcoded credentials and boundary leaks.

---

## 🌟 Open Source & Free Forever

This project is **100% Free, Open Source, and Openly Licensed** under the MIT License:
- **Free to Use**: Deploy it in your personal, commercial, or enterprise repositories without any cost.
- **Free to Fork**: Customize the skills, scripts, and rules to match your team's specific developer workflows.
- **Free to Contribute**: Pull requests, issues, and ideas are highly welcome! Help us build the ultimate workspace for AI agents.

---

## ⚠️ Disclaimer & No Warranty (Read Before Use)

> [!CAUTION]
> **ALL USAGE IS ENTIRELY AT YOUR OWN RISK. THIS FRAMEWORK IS PROVIDED "AS IS" WITHOUT ANY WARRANTY OF ANY KIND.**
>
> By using Antigravity Agent Core, you acknowledge and agree to the following:
>
> - **Financial Responsibility (API & Token Costs)**: AI agent operations are highly recursive and can consume a significant volume of LLM tokens (input, output, and caching). You are **solely responsible** for all charges billed by your AI providers (OpenAI, Anthropic, Google, etc.). Keep track of your spending limits and usage alerts.
> - **Operational & Code Risk**: Autonomous agents can modify files, execute terminal scripts, alter directories, and rewrite Git branches. Always execute agent tasks in a safe development workspace with version control active.
> - **No Liability**: In no event shall the author (Muhammad Rafael Ghifari) or contributors be liable for any direct, indirect, incidental, or consequential damages (including, but not limited to, lost data, system crashes, file corruption, or database downtime) arising out of the use or inability to use this software.
> - **Responsible Review**: You are responsible for inspecting all agent-generated code, commit logs, and validation results before merging them into production environments.

---

## 🚀 30-Second Quick Start

Get any local repository agent-ready in a single command. The bootstrapper automatically configures the environment blueprints, installs Git hooks, and sets up active memory and schemas.

### 💻 1. Installation

Open your terminal in your project root folder and execute the appropriate command for your operating system:

#### **Linux & macOS (Bash/Zsh)**
Run this one-liner to download and install:
```bash
curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/bootstrap.sh | bash
```

#### **Windows (PowerShell)**
Run this one-liner to download and install (*requires Git Bash installed*):
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/bootstrap.ps1'))
```

---

### 🛠️ 2. Scaffold Your Stack (Optional)
If you are starting a brand new project, run the scaffolding wizard to initialize folders and configure dependencies (supports Node, TypeScript, Python, Go, PHP, Ruby):
```bash
./.agents/scripts/helper.sh init
```

---

### 🩺 3. Verify Workspace Health
Run the doctor tool to inspect active hooks, locks, script permissions, and security validation checks:
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
7. [Migration Guide (Upgrading from Older Versions)](#7-migration-guide-upgrading-from-older-versions)

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

### 2.4. Native Monorepo Support & Directory-Aware Validation
Antigravity natively supports multi-project repositories (e.g., Turborepo, pnpm workspaces, Yarn workspaces, Go workspaces):
- **Autonomous Discovery**: The recon engine scans the repository and maps out all nested sub-projects under directories like `apps/`, `packages/`, or `services/`.
- **Differential Execution**: Linter and test runners analyze staged git file boundaries, executing commands only on directories that contain modifications, preventing redundant runs and minimizing token consumption.
- **Scaffolding Integration**: The initialization script allows users to scaffold a full Turborepo + pnpm monorepo architecture (Next.js frontend, Go Gin backend API, and shared workspace package) out-of-the-box.

### 2.5. Multi-Agent & Multi-Account Synchronization Protocol
Keeps multiple agents, developers, and distinct user accounts 100% aligned and in sync:
- **Git-Backed Single Source of Truth**: Active task checklists (`memory.md`), project blueprints (`project_rules.md`), design decisions (`adr.md`), and domain schemas (`schema.md`, `schemas/`) are committed and tracked in Git. When a developer or agent pulls modifications (`git pull`), the workspace context aligns instantly.
- **Branch-Aware Upstream Gate**: The validation suite checks if the local repository is behind its remote origin branch. If so, it halts agent execution to prevent code conflicts and split-brain memory states.
- **Sub-Project Module Locks**: Prevents overlapping edits on the same directory by using local locking (`helper.sh lock <path>`). Slash paths are sanitized automatically (e.g., `apps/backend` locks to `apps_backend.lock`).
- **Pre-Merge Checklist Archival**: Clears active memory checklists and archives them to `archive/` upon branch completion to avoid git merge conflicts.

### 2.6. Docker & Local Infrastructure Provisioning
Easily containerize and orchestrate your application components and databases:
- **Dockerfile Generation**: Automatically generates multi-stage, production-ready `Dockerfile` configurations for Next.js, NestJS, Go Gin, FastAPI, and React SPA (served via Nginx).
- **Docker Compose Orchestration**: Configures a unified `docker-compose.yml` to spin up backend services, frontend services, and persistent database volumes.
- **Service Sequencing & Healthchecks**: Automatically structures `depends_on` conditions to ensure application containers wait for database healthchecks (e.g., `pg_isready` for PostgreSQL, `mysqladmin ping` for MySQL, or `redis-cli ping` for Redis) to pass before starting.
- **Port-Clash Prevention**: Intelligently offsets host ports (e.g., mapping host `3001` to frontend `3000`) if backend and frontend containers both default to port `3000`.

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

**For Linux/macOS:**
```bash
# Download and execute
curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/bootstrap.sh | bash

# Or run from local clone
/path/to/antigravity-agents/bootstrap.sh
```

**For Windows (PowerShell):**
```powershell
# Download and execute
Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/bootstrap.ps1'))

# Or run from local clone
powershell -ExecutionPolicy Bypass -File \path\to\antigravity-agents\bootstrap.ps1
```

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

**For Linux/macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/bootstrap.sh | bash
```

**For Windows (PowerShell):**
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/bootstrap.ps1'))
```

The script will autodetect your programming language, linter, tests, and database migrations, and write the project settings to `.agents/project_rules.md` automatically!

#### **Step 3: Run Diagnostics & Commit**
Verify that your existing workspace passes the agent safety checks:
```bash
./.agents/scripts/helper.sh doctor
```
If everything is healthy, stage the configurations and make your first validated commit:
```bash
git add AGENTS.md .agents/ .antigravityignore
git commit -m "chore(core): initialize antigravity agent workspace"
```

---

## 4. Operational Scripts Guide (`helper.sh`)

Once bootstrapped, operations are managed through `./.agents/scripts/helper.sh` or standard Git commands. Here is a quick reference:

| Command | Usage | Description |
|---|---|---|
| `init` | `./.agents/scripts/helper.sh init` | Launches the interactive setup questionnaire to scaffold directories, configurations, and file templates. |
| `recon` | `./.agents/scripts/helper.sh recon` | Runs the autonomous codebase scanner to map stacks, directories, databases, and routes. |
| `validate` | `./.agents/scripts/helper.sh validate` | Audits the project for secrets, memory cap limits, and domain decoupling. |
| `doctor` | `./.agents/scripts/helper.sh doctor` | Checks workspace health, script permissions, Git hook installation, and active locks. |
| `sync-git` | `./.agents/scripts/helper.sh sync-git` | *(Automated)* Synchronizes active branch and last commit hash in `memory.md`. |
| `lock` | `./.agents/scripts/helper.sh lock <module>` | Locks a specific module to prevent parallel developers or agents from modifying the same files simultaneously. |
| `unlock` | `./.agents/scripts/helper.sh unlock <module>` | *(Automated)* Releases the lock on a module. |
| `archive` | `./.agents/scripts/helper.sh archive` | Archives completed checklists and moves dynamic workflow files to `archive/` pre-merge to prevent conflicts. |
| `sync-api` | `./.agents/scripts/helper.sh sync-api` | Automatically extracts backend OpenAPI schema and generates a zero-dependency typed TypeScript fetch client in the frontend. |
| `log-usage` | `./.agents/scripts/helper.sh log-usage <count>` | Records token consumption counts inside `.agents/token_budget.json` to prevent budget exhaustion. |

### 4.1 API Contract Synchronization (`sync-api`)

The `sync-api` command extracts the OpenAPI schema (`openapi.json`) from the backend application and synchronizes it with the frontend to generate a zero-dependency, fully-typed TypeScript fetch API client wrapper (`api-client.ts`).

- **FastAPI/Python Backend**: Automatically boots a minimal context to dump `app.openapi()` directly into `openapi.json`.
- **Go Gin Backend**: Runs `swag init` on the main server entry point to build and copy the schema.
- **Frontend Client Compilation**: Reads `openapi.json` and parses components, schemas, path parameters, query parameters, request bodies, and responses. Outputs interfaces and client classes at the appropriate frontend location (e.g., `src/lib/api-client.ts`).
- **Zero-Dependency**: The generated client is clean TypeScript that uses vanilla `fetch` and does not require third-party libraries.

---

## 5. Typical Workflow for the Agent
 
> [!NOTE]
> **Autonomous Script Execution**: Agents are instructed by the project architectural blueprint ([project_rules.md](file://./.agents/project_rules.md)) to execute these operational commands (locking, validation, API sync, and archiving) automatically without requiring manual user commands.

When an AI Agent starts working on a task, it must strictly follow these steps to ensure clean history and zero bugs:
 
1. **Verify State**: Verify that the workspace is on the correct branch and clean.
2. **Lock Module**: Acquire the module lock to prevent conflicts:
   ```bash
   ./.agents/scripts/helper.sh lock <module_name>
   ```
3. **Implement Feature**: Write code & tests under TDD guidelines.
4. **Staging & Commit**: Stage files and execute a standard Git commit:
   ```bash
   git add -A
   git commit -m "feat(core): add new feature implementation"
   ```
   *(The Git `pre-commit` hook automatically runs validations/tests, and the `post-commit` hook automatically syncs memory and releases all active locks).*
5. **Handover Relay (Next Turn)**: Before ending a session or switching agent accounts, the agent writes a brief state summary (under 5 lines) in `.agents/memory.md` under `## 3. Relayed Context & Handover Notes` to guide the incoming agent.
6. **Merge Preparation**: Run `./.agents/scripts/helper.sh archive` to compact checklists before merging to `main`/`master`.


---

## 6. Core Rules & Architecture Purity

Antigravity Workspace enforces these key rules on AI agents:
- **Strict Bootstrapping sequence**: At startup, the agent MUST read `AGENTS.md` ➔ `project_rules.md` ➔ `schema.md` ➔ `memory.md` in order. No other tools or files may be touched prior to this.
- **Git-Backed Memory Sync**: All schemas, ADRs, dynamic workflows, and memory files under `.agents/` (except `.agents/locks/`) MUST be committed to Git. The agent will run verification checks on startup to ensure your local clone is not behind upstream (`origin`).
- **No Agent Git Push/Pull**: The agent is **forbidden** from running remote operations like `git pull`, `git push`, or changing branches. The user must fetch/pull updates before starting work.
- **Discussion Traceability**: All `/grill-me` or design discussion outcomes are immediately saved to `.agents/workflows/task_<task_name>.md`. When feature branches are merged, running `helper.sh archive` moves these files to `.agents/archive/sprint_<branch>/` to keep active workspace clean.
- **Real-Time Schema & Dependency Sync**: Database model or API changes must immediately update `.agents/schemas/` and the main `.agents/schema.md` index before coding starts. Library dependencies must update `project_rules.md` and package manager configs (`package.json`, etc.) immediately.
- **Token Optimization (.antigravityignore)**: Agents strictly adhere to `.antigravityignore` patterns, preventing costly crawls through dependencies, logs, binaries, or build directories.
- **Hardcoded Secret Scan**: The agent cannot commit code if passwords, keys, or API tokens are detected in the workspace (scanned via `validate.sh`).
- **Handover Relayed Context**: Before finishing a turn or switching accounts, the agent writes the current status and next action items in `memory.md` under `## 3. Relayed Context & Handover Notes`, ensuring the next agent picks up immediately without token waste.

## 7. Migration Guide (Upgrading from Older Versions)

For upgrading existing workspaces configured with older versions of the Antigravity Agent to the new version **1.4.0**, a dedicated migration command is available.

### ⚡ Automatic Upgrade (Recommended)

1. First, pull the latest system files and script templates:
   - **Linux/macOS (Bash/Zsh)**:
     ```bash
     curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/bootstrap.sh | bash -s -- --update
     ```
   - **Windows (PowerShell)**:
     ```powershell
     Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/bootstrap.ps1')); powershell -ExecutionPolicy Bypass -File .\bootstrap.ps1 -Update
     ```
2. Run the automated migration command:
   ```bash
   ./.agents/scripts/helper.sh migrate
   ```
   *This automatically backs up your existing configuration files (`memory.md`, `project_rules.md`, `schema.md`) to `.backup` extensions, updates system hooks and subdirectories, upgrades your active memory schema, and runs auto-recon to align rules.*

For full details, precautions, and manual step-by-step migration instructions, refer to the standalone [MIGRATION.md](file://./MIGRATION.md) guide in the project root.

---


## 📅 Version History & Changelog

All protocol modifications, script updates, and rule changes are documented in the [Agent Core Changelog](file://./CHANGELOG.md). Refer to it for tracing changes to the workspace setup.



## 👤 Created By & Contact

This project is created and maintained with 💙 by:

- **Author**: Muhammad Rafael Ghifari
- **Business Email**: [business.rafaelghifari@gmail.com](mailto:business.rafaelghifari@gmail.com)
- **LinkedIn**: [rafaelghifari](https://www.linkedin.com/in/rafaelghifari/)
- **GitHub**: [rafaelghif](https://github.com/rafaelghif)

Feel free to open an issue or submit a pull request on the [GitHub Repository](https://github.com/rafaelghif/antigravity-agents). We welcome all ideas and feedback to make AI coding agent workflows better for everyone!
