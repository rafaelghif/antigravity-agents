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

## ⚠️ Disclaimer & No Warranty

> [!WARNING]
> **Use at your own risk.** This workspace protocol and template framework is provided "as is", without warranty of any kind, express or implied.
> - **API/Token Costs**: AI agent operations can consume large amounts of tokens depending on the size of the codebase. The user is solely responsible for monitoring their own API keys, usage, and billing costs.
> - **No Liability**: The author (Muhammad Rafael Ghifari) shall not be held liable for any direct or indirect damages, loss of database records, broken branches, system crashes, or security boundary issues resulting from the use of this project.
> - **Responsible Use**: Please review agent suggestions and output commits carefully before pushing them to shared production repositories. Use wisely and responsibly!

---

## 🚀 30-Second Quick Start

Get any repository agent-ready in a single step:

### Step 1: Bootstrap the Repository
Navigate to your project root and execute the bootstrapper:

**For Linux/macOS:**
```bash
# Option A: From a locally cloned antigravity-agents repo
/path/to/antigravity-agents/bootstrap.sh

# Option B: Download and run via curl
curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/bootstrap.sh | bash
```

**For Windows (PowerShell):**
```powershell
# Option A: From a locally cloned antigravity-agents repo
powershell -ExecutionPolicy Bypass -File \path\to\antigravity-agents\bootstrap.ps1

# Option B: Download and run via powershell one-liner
Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/bootstrap.ps1'))
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
- **Strict Bootstrapping sequence**: At startup, the agent MUST read `AGENTS.md` ➔ `project_rules.md` ➔ `schema.md` ➔ `memory.md` in order. No other tools or files may be touched prior to this.
- **Git-Backed Memory Sync**: All schemas, ADRs, dynamic workflows, and memory files under `.agents/` (except `.agents/locks/`) MUST be committed to Git. The agent will run verification checks on startup to ensure your local clone is not behind upstream (`origin`).
- **No Agent Git Push/Pull**: The agent is **forbidden** from running remote operations like `git pull`, `git push`, or changing branches. The user must fetch/pull updates before starting work.
- **Discussion Traceability**: All `/grill-me` or design discussion outcomes are immediately saved to `.agents/workflows/task_<task_name>.md`. When feature branches are merged, running `helper.sh archive` moves these files to `.agents/archive/sprint_<branch>/` to keep active workspace clean.
- **Real-Time Schema & Dependency Sync**: Database model or API changes must immediately update `.agents/schemas/` and the main `.agents/schema.md` index before coding starts. Library dependencies must update `project_rules.md` and package manager configs (`package.json`, etc.) immediately.
- **Token Optimization (.antigravityignore)**: Agents strictly adhere to `.antigravityignore` patterns, preventing costly crawls through dependencies, logs, binaries, or build directories.
- **Hardcoded Secret Scan**: The agent cannot commit code if passwords, keys, or API tokens are detected in the workspace (scanned via `validate.sh`).

---

## 📅 Version History & Changelog

All protocol modifications, script updates, and rule changes are documented in the [Agent Core Changelog](file://./.agents/CHANGELOG.md). Refer to it for tracing changes to the workspace setup.


## 👤 Created By & Contact

This project is created and maintained with 💙 by:

- **Author**: Muhammad Rafael Ghifari
- **Business Email**: [business.rafaelghifari@gmail.com](mailto:business.rafaelghifari@gmail.com)
- **LinkedIn**: [rafaelghifari](https://www.linkedin.com/in/rafaelghifari/)
- **GitHub**: [rafaelghif](https://github.com/rafaelghif)

Feel free to open an issue or submit a pull request on the [GitHub Repository](https://github.com/rafaelghif/antigravity-agents). We welcome all ideas and feedback to make AI coding agent workflows better for everyone!
