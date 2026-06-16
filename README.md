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
  ├── bootstrap.ps1               <-- Windows Bootstrapper entrypoint (automatically deletes itself)
  ├── AGENTS.md                   <-- Static: Global Agent Protocol (cached)
  ├── README.md                   <-- Static: Developer handbook
  ├── .github/                    <-- GitHub configurations
  │     └── workflows/
  │           └── antigravity.yml <-- CI workspace validator workflow
  └── .agents/                    <-- Workspace operational directory (generated)
        ├── bootstrap.sh          <-- Local backup of the bootstrapper script
        ├── schema.md             <-- Semi-Static: Database & API specs index
        ├── adr.md                <-- Static: Architectural Design Records (cached)
        ├── memory.md             <-- Dynamic: Active task state (<100 lines)
        ├── rules/                <-- Static: Workspace rules including tech stack and architecture
        │     └── project_rules.md <-- Static: Tech Stack, coding rules, & gates (cached)
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
        │     ├── helper.ps1      <-- PowerShell command wrapper for Windows compatibility
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
- **Automated CI Validation**: Runs validation checks automatically on GitHub pushes and pull requests via the `.github/workflows/antigravity.yml` workflow template.

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

##### **Bootstrapper CLI Options & Flags**

Both `bootstrap.sh` and `bootstrap.ps1` accept command-line arguments to customize their run behavior:

| Linux/macOS Flag | Windows PowerShell Option | Description |
|---|---|---|
| `-f`, `--force` | `-Force` | **Force Overwrite**: Forces the script to overwrite existing files, templates, hooks, and configurations in `.agents/`. (Default: `false`, preserves user changes). |
| `-u`, `--update` | `-Update` | **Update Only**: Performs an update of the core scripts in `.agents/scripts/` to the latest version, without overwriting custom workspace configurations, rules, or the active memory ledger. |
| *N/A* | `-Version <version>` | **Target Version**: (PowerShell wrapper only) Downloads and executes a specific version/branch of the bootstrapper (defaults to `main`). |

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

The script will autodetect your programming language, linter, tests, and database migrations, and write the project settings to `.agents/rules/project_rules.md` automatically!

> [!TIP]
> Just like in Scenario A, you can pass optional CLI flags to the bootstrapper (e.g. `-u` / `-Update` to perform update-only of core scripts, or `-f` / `-Force` to overwrite existing configuration templates).

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

## 4. Operational Scripts Guide (`helper.sh` / `helper.ps1`)

Once bootstrapped, operations are managed through `./.agents/scripts/helper.sh` (or `./.agents/scripts/helper.ps1` for native PowerShell support on Windows) or standard Git commands.

### 💡 Simplified Developer Cheat Sheet (Daily Essentials)

If you are a developer, you only need to know these **5 essential commands** for daily work. All other complex options and background tasks are handled automatically:

1. **Start a Project**:
   ```bash
   ./.agents/scripts/helper.sh init
   ```
   *Launches a friendly questionnaire to set up your project folder structure and stack settings!*

2. **Check Workspace Health**:
   ```bash
   ./.agents/scripts/helper.sh doctor
   ```
   *Diagnoses if something is wrong. Checks permissions, Git hooks, and module locks.*

3. **Lock a Module (Before Editing)**:
   ```bash
   ./.agents/scripts/helper.sh lock <module-name>
   ```
   *Tells agents and other developers: "I am currently editing this directory, please do not touch it!"*

4. **Unlock a Module (When Done)**:
   ```bash
   ./.agents/scripts/helper.sh unlock <module-name>
   ```
   *Releases the lock. (Note: Making a commit via the tool automatically releases all active locks for you).*

5. **Commit Your Code Safely**:
   ```bash
   ./.agents/scripts/helper.sh commit
   ```
   *Launches an interactive wizard to write your commit message. It runs verification tests and switches profiles automatically to keep your workspace safe!*

---

Here is a quick reference table of all commands:

| Command | Usage | Description |
|---|---|---|
| `init` | `init [name] [stack] [arch] [db_orm] [env_vars]` | Launches the setup questionnaire to scaffold directories, configurations, and file templates. |
| `recon` | `recon` | Runs the autonomous codebase scanner to map stacks, directories, databases, and routes. |
| `validate` | `validate` | Audits the project for secrets, memory cap limits, and domain decoupling. |
| `doctor` | `doctor` | Checks workspace health, script permissions, Git hook installation, and active locks. |
| `commit` | `commit [--no-test] [type] [scope] [desc] [files...]` | Runs validations, tests, automates Git profile rotation, and makes a Conventional Commit. |
| `sync-git` | `sync-git` | *(Automated)* Synchronizes active branch and last commit hash in `memory.md`. |
| `lock` | `lock <module>` | Locks a specific module to prevent parallel edits. |
| `unlock` | `unlock <module>` | *(Automated)* Releases the lock on a module. |
| `archive` | `archive` | Archives completed checklists to prevent merge conflicts. |
| `migrate` | `migrate` | Safely upgrades older agent setups to the current standard. |
| `build` | `build` | Monorepo-aware command to compile code in modified subfolders. |
| `lint` | `lint` | Monorepo-aware command to lint code in modified subfolders. |
| `test` | `test` | Monorepo-aware command to test code in modified subfolders. |
| `sync-api` | `sync-api` | Extracts OpenAPI schema and generates frontend TypeScript fetch API client. |
| `create-skill` | `create-skill <name> [description]` | Scaffolds a new specialized skill directory (lowercase kebab-case). |
| `list-skills` | `list-skills` | Audits all registered skills in `.agents/skills/` for compliance and lists them. |
| `create-rule` | `create-rule <name> <activation> [param]` | Scaffolds a new workspace rule file under `.agents/rules/`. |
| `list-rules` | `list-rules` | Audits all registered workspace rules in `.agents/rules/` for compliance. |
| `log-usage` | `log-usage <count>` | Records token consumption counts inside `.agents/token_budget.json`. |
| `release` | `release <major/minor/patch>` | Auto-increments version and scaffolds release notes in `CHANGELOG.md`. |
| `create-adr` | `create-adr <title> [status]` | Scaffolds a new Architectural Decision Record under `.agents/adrs/`. |
| `git-profile` | `git-profile [key/name/rotate] [email]` | Switches or displays Git config profiles and automates local SSH key rotation. |
| `api-profile` | `api-profile [key/rotate]` | Switches or displays API provider key profiles and automates local environment rotation. |


### 4.1 API Contract Synchronization (`sync-api`)

The `sync-api` command extracts the OpenAPI schema (`openapi.json`) from the backend application and synchronizes it with the frontend to generate a zero-dependency, fully-typed TypeScript fetch API client wrapper (`api-client.ts`).

- **FastAPI/Python Backend**: Automatically boots a minimal context to dump `app.openapi()` directly into `openapi.json`.
- **Go Gin Backend**: Runs `swag init` on the main server entry point to build and copy the schema.
- **Frontend Client Compilation**: Reads `openapi.json` and parses components, schemas, path parameters, query parameters, request bodies, and responses. Outputs interfaces and client classes at the appropriate frontend location (e.g., `src/lib/api-client.ts`).
- **Zero-Dependency**: The generated client is clean TypeScript that uses vanilla `fetch` and does not require third-party libraries.

### 4.2 Skill Scaffolding & Auditing (`create-skill` / `list-skills`)

To dynamically extend the agent's capabilities inside this workspace, you (or the agent) can create and audit specialized skills:

- **Create Skill**: Run `./.agents/scripts/helper.sh create-skill <name> [description]`. This scaffolds a new directory at `.agents/skills/<name>/` containing a standard, parameterizable `SKILL.md` template and a structured Python script wrapper inside `scripts/main.py`.
- **List & Audit Skills**: Run `./.agents/scripts/helper.sh list-skills`. This scans all registered skill directories and audits them for compliance:
  1. `SKILL.md` exists and starts with a valid YAML frontmatter header containing `name` and `description`.
  2. File body and script source code contain no unresolved placeholder markers (e.g. `TODO`, `FIXME`, or `[placeholder]`).
  3. All referenced scripts listed in the YAML header exist and have executable permissions (`chmod +x`).

### 4.3 Workspace Rules Scaffolding & Auditing (`create-rule` / `list-rules`)

Workspace rules define how coding standards are applied dynamically. The rules reside in the `.agents/rules/` directory (with backward compatibility/automatic migration for `.agent/rules/`):

- **Create Rule**: Run `./.agents/scripts/helper.sh create-rule <name> <activation> [param]`. Scaffolds a new markdown rule file under `.agents/rules/<name>.md`.
  * Activation modes: `manual`, `always-on`, `glob` (requires glob pattern param), and `model-decision` (requires NL description param).
- **List & Audit Rules**: Run `./.agents/scripts/helper.sh list-rules`. Audits all registered rule files for compliance:
  1. Valid `.md` file name extension.
  2. Valid YAML frontmatter containing `name` and `activation`.
  3. Correct configuration of activation-dependent parameter (e.g. `pattern` for Glob, `description` for Model Decision).
  4. Absence of unresolved placeholders (e.g. `TODO`, `FIXME`, `[placeholder]`) in the rule body.

### 4.4 Git Profile Management (`git-profile`)

The `git-profile` command allows developers to switch between multiple Git accounts (names, emails, and SSH keys) locally inside the repository. This is useful for developers who work on multiple projects using different accounts (e.g. work vs personal) or want to simulate contributions from multiple users.

#### A. How it Works
Git keeps configurations locally inside the `.git/config` folder of your project.
- **Git Identity**: The tool configures `user.name` and `user.email` locally so they apply *only* to this repository.
- **SSH Authentication (Private Key)**: If you specify an `ssh_key` path, the tool sets `core.sshCommand = "ssh -i <path> -o IdentitiesOnly=yes"`. This instructs Git to use that specific private key when talking to GitHub (pushing/pulling) for *only* this repository. This prevents SSH key clashes without messing up your global SSH config files!

#### B. Quick Start Guide

##### Step 1: Create your profiles file
1. Copy the example file to `.agents/git_profiles` (which is already configured in `.gitignore` to keep your private details safe):
   ```bash
   cp .agents/git_profiles.example .agents/git_profiles
   ```
2. Open `.agents/git_profiles` and fill in your git accounts. You can configure user identity and private keys:
   ```ini
   # Profile 1: Work Account
   work.name=Alice (Work)
   work.email=alice@company.com
   work.ssh_key=~/.ssh/id_rsa_work

   # Profile 2: Personal Account
   personal.name=Alice (Personal)
   personal.email=alice@gmail.com
   personal.ssh_key=~/.ssh/id_rsa_personal
   ```

##### Step 2: Switch accounts
- **Manual Switch**:
  To switch the active profile of the current repository to your work account, run:
  ```bash
  ./.agents/scripts/helper.sh git-profile work
  ```
  *(This instantly configures Git to commit as Alice and push/pull using `id_rsa_work`)*

- **Check Current Status**:
  To see which identity and SSH key are currently active in this repository vs your global default settings, run:
  ```bash
  ./.agents/scripts/helper.sh git-profile
  ```

- **Manual Profile Rotation**:
  To manually trigger profile rotation to the next configured identity in your `.agents/git_profiles` based on the last commit email (without making a commit), run:
  ```bash
  ./.agents/scripts/helper.sh git-profile rotate
  # Or
  ./.agents/scripts/helper.sh git-profile --rotate
  ```

- **Automated Round-Robin Commit Rotation**:
  If multiple profiles are configured in `.agents/git_profiles`, running:
  ```bash
  ./.agents/scripts/helper.sh commit
  ```
  will **automatically rotate** the commit author and SSH key (round-robin) based on the author of the last commit. For example, if your last commit was done using `personal`, the next commit will automatically switch to `work`, simulating multiple developers collaborating.

#### C. How to Create and Register SSH Keys (Tutorial)
If you have multiple GitHub accounts, you must generate a separate SSH key for each account. This works across Linux, macOS, and Windows:

##### Step 1: Generate a new SSH key
Open your terminal or command-line client and run the generator command:

* **On Linux, macOS, Windows Git Bash, or Windows PowerShell**:
  ```bash
  # For your personal account
  ssh-keygen -t ed25519 -C "your_personal_email@gmail.com" -f ~/.ssh/id_rsa_personal

  # For your work account
  ssh-keygen -t ed25519 -C "your_work_email@company.com" -f ~/.ssh/id_rsa_work
  ```
* **On Windows Command Prompt (CMD)**:
  ```cmd
  :: For your personal account
  ssh-keygen -t ed25519 -C "your_personal_email@gmail.com" -f %USERPROFILE%\.ssh\id_rsa_personal

  :: For your work account
  ssh-keygen -t ed25519 -C "your_work_email@company.com" -f %USERPROFILE%\.ssh\id_rsa_work
  ```
*(Press Enter when prompted for a passphrase to keep it passwordless, or enter one if desired).*

##### Step 2: Register the Public Key on GitHub
1. Copy the public key content to your clipboard:
   * **Linux / macOS / Git Bash**: `cat ~/.ssh/id_rsa_personal.pub`
   * **Windows PowerShell**: `Get-Content ~/.ssh/id_rsa_personal.pub`
   * **Windows CMD**: `type %USERPROFILE%\.ssh\id_rsa_personal.pub`
2. Log into your GitHub account, navigate to **Settings -> SSH and GPG keys -> New SSH Key**.
3. Paste the copied text and save.
4. Repeat this step for your work account using its corresponding public key.

##### Step 3: Add Private Key Path to `.agents/git_profiles`
Open `.agents/git_profiles` and paste the paths to the **private keys** (without the `.pub` extension):

> [!TIP]
> **Cross-Platform Path Compatibility**:
> - Using tilde paths like `~/.ssh/id_rsa_personal` is recommended as it is fully supported and automatically resolved on Linux, macOS, and Windows.
> - If you prefer using absolute paths on Windows, **always use forward slashes** (e.g. `C:/Users/YourName/.ssh/id_rsa_personal`) to prevent backslash escaping conflicts in Git configuration commands.

```ini
work.ssh_key=~/.ssh/id_rsa_work
personal.ssh_key=~/.ssh/id_rsa_personal
```

#### D. Robustness & Extreme Conditions Handling (Enterprise-Grade)
The system is built to handle extreme edge cases gracefully:
- **Zero Commit History**: On a brand new repository with no commits, the rotation logic safely defaults to the first profile in your `.agents/git_profiles`.
- **Tilde Path Expansion**: Tilde paths (like `~/.ssh/...`) specified in your profile are automatically resolved to the absolute path of your `$HOME` directory before checking for file existence.
- **Spaces in Key Paths**: Key paths containing spaces are automatically quoted inside the `core.sshCommand` configurations to prevent command splitting errors (especially on Windows).
- **Missing SSH Key Files**: If a configured SSH key file is missing on your system, the tool warns you and unsets the local SSH command config (falling back to system default SSH keys) rather than letting connection commands crash.
- **Zero Global/Local Git Identity**: If a developer has no Git identity configured on their machine and no profiles configuration is set, the tool automatically sets up a temporary, local-only identity (`Local Developer <local-dev@localhost>`) so they can still commit locally out-of-the-box.

### 4.5 API Profile Management & Auto-Rotation (`api-profile`)

The `api-profile` command allows developers to define and rotate active API keys (such as `GEMINI_API_KEY`, `OPENAI_API_KEY`, etc.) locally inside the workspace. This is useful for rotating between different accounts, managing token quota limits, or automatically switching keys when encountering rate limits.

#### A. How it Works
API keys are stored in a Git-ignored file (`.agents/api_keys`). When you select a profile (e.g. `work`), the helper script:
1. Extracts all keys defined for that profile.
2. Writes them to `.agents/active_api_keys` (for Bash/Zsh) and `.agents/active_api_keys.ps1` (for PowerShell).
3. The active keys can then be loaded dynamically by runner wrappers before running the agent.

#### B. Quick Start Guide

##### Step 1: Create your API profiles file
1. Copy the example file to `.agents/api_keys` (which is ignored by Git to keep credentials secure):
   ```bash
   cp .agents/api_keys.example .agents/api_keys
   ```
2. Open `.agents/api_keys` and fill in your API tokens:
   ```ini
   # Profile: personal
   personal.GEMINI_API_KEY=AIzaSyA_personal_key
   personal.OPENAI_API_KEY=sk-proj-personal_key

   # Profile: work
   work.GEMINI_API_KEY=AIzaSyB_work_key
   work.OPENAI_API_KEY=sk-proj-work_key
   ```

##### Step 2: Switch accounts
- **Manual Switch**:
  To switch the active API keys to your work profile, run:
  ```bash
  ./.agents/scripts/helper.sh api-profile work
  ```
- **Check Current Status**:
  To view the active API profile name and masked key values, run:
  ```bash
  ./.agents/scripts/helper.sh api-profile
  ```
- **Manual API Profile Rotation**:
  To rotate the active API credentials to the next available profile, run:
  ```bash
  ./.agents/scripts/helper.sh api-profile rotate
  # Or
  ./.agents/scripts/helper.sh api-profile --rotate
  ```

#### C. Automated Runtime Rotation (Wrapper Scripts)
To automatically rotate API keys when encountering rate-limiting (HTTP status code `429`, exit code `129`, or resource exhaustion), use the provided execution wrapper scripts:

**For Unix/Linux environments (Bash):**
```bash
./.agents/scripts/api-rotate-wrapper.sh [command_to_run] [args...]
```
**Example:**
```bash
./.agents/scripts/api-rotate-wrapper.sh npx antigravity-cli task-run
```

**For Windows environments (PowerShell):**
```powershell
.\.agents\scripts\api-rotate-wrapper.ps1 [command_to_run] [args...]
```
**Example:**
```powershell
.\.agents\scripts\api-rotate-wrapper.ps1 npx antigravity-cli task-run
```
If the command fails due to a rate limit, the wrapper script will automatically rotate to the next configured API key profile, reload the active keys, and retry the execution.

In PowerShell, you can also automatically import/load the selected active API profile's keys into your current terminal session by dot-sourcing `helper.ps1`:
```powershell
. .\.agents\scripts\helper.ps1 api-profile work
```

#### D. Specialized Python Rotator Skill (`api-rotator`)
For developers writing custom Python agent scripts, the framework provides a native skill at `.agents/skills/api-rotator/scripts/main.py`. This script implements the hybrid rotation design pattern:
1. **Proactive Quota Checks**: Before making any LLM call, it checks the local `.agents/token_budget.json` profile usage. If the active profile's token usage exceeds its quota, it automatically rotates early.
2. **Reactive Rate-Limit Retries**: It intercepts `google-generativeai` and `openai` exception objects for HTTP 429/ResourceExhausted errors, rotates key profiles via `api-profile rotate`, and transparently retries.
3. **Usage Logging**: Upon success, it automatically logs token counts to the active profile under `profiles` inside `token_budget.json`.

**Usage Example (with rate limit simulation for testing):**
```bash
python3 .agents/skills/api-rotator/scripts/main.py --prompt "Explain quantum computing" --simulate-limit 1
```

#### E. Per-Profile Quota & Token Budget Tracking
The token budget configuration at `.agents/token_budget.json` supports granular profile limits:
- `helper.sh log-usage <count>` logs token counts to the active API profile (automatically detected from `.agents/active_api_profile_name`).
- `helper.sh log-usage <count> [profile-name]` logs to a specific profile manually.
- `validate.sh` Check 9 automatically validates the active profile's quota usage, preventing budget overrun.

### 4.6 Detailed Helper Command Reference

For users and agents, the helper script supports explicit parameters and flags to run operations in non-interactive, automated, or specific modes:

#### 1. Project Scaffolding Wizard (`init`)
- **Signature**: `./.agents/scripts/helper.sh init [name] [stack] [architecture] [db_orm] [env_vars]`
- **Parameters**:
  - `[name]`: Name of the project (e.g., `MyService`).
  - `[stack]`: Target language/stack (choices: `Next.js`, `Go Gin`, `FastAPI`, `Node/TypeScript`, `Go`, `Python`, `Monorepo`, `Multi-Project`, `Laravel`).
  - `[architecture]`: Architecture pattern (e.g., `clean`, `hexagonal`, `mvc`).
  - `[db_orm]`: Relational DB or ORM framework (e.g., `PostgreSQL`, `MongoDB`, `Prisma`, `None`).
  - `[env_vars]`: Space-separated configuration environment variables (e.g., `"PORT DATABASE_URL"`).
- **Behavior**: If any arguments are missing, the command falls back to an interactive setup menu automatically.

#### 2. Conventional Commit Builder (`commit`)
- **Signature**: `./.agents/scripts/helper.sh commit [--no-test|--no-verify] [type] [scope] [description] [files...]`
- **Options & Flags**:
  - `--no-test`, `--no-verify`: Bypasses pre-commit test suites and workspace sanity validation checks.
  - `[type]`: Commit type (choices: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`, `perf`).
  - `[scope]`: Component scope of the modification (e.g., `core`, `auth`, `db`, `shared`).
  - `[description]`: Short conventional commit description.
  - `[files...]`: Optional paths to specific files to stage and commit. If omitted, all modified tracked files are staged.
- **Behavior**: Automatically performs the linter/test checks (unless bypassed), rotates the local Git profile and SSH key to simulate collaborating developers, and commits atomic changes. If parameters are omitted, it defaults to interactive prompts.

#### 3. Module Locking (`lock` / `unlock`)
- **Signature**:
  - Lock: `./.agents/scripts/helper.sh lock <module>`
  - Unlock: `./.agents/scripts/helper.sh unlock <module>`
- **Parameters**:
  - `<module>`: Kebab-case or directory-path name of the module/domain to lock (e.g., `apps/backend`).
- **Behavior**: Acquires a transient lock by creating `.agents/locks/<module_sanitized>.lock`. Checking locks prevents parallel developers or agents from modifying the same files simultaneously.

#### 4. API Schema Sync (`sync-api`)
- **Signature**: `./.agents/scripts/helper.sh sync-api`
- **Behavior**: Programmatically boots or scans the backend API application, dumps the latest OpenAPI schema to `openapi.json`, and compiles a zero-dependency type-safe fetch client wrapper in the frontend.

#### 5. Skill Creation (`create-skill`)
- **Signature**: `./.agents/scripts/helper.sh create-skill <name> [description]`
- **Parameters**:
  - `<name>`: Unique name for the skill. Must be strictly lowercase kebab-case (e.g., `db-optimization`).
  - `[description]`: A brief summary of the skill's purpose.
- **Behavior**: Scaffolds a compliant directory under `.agents/skills/<name>/` including `SKILL.md` template and an executable main script.

#### 6. Custom Workspace Rules (`create-rule`)
- **Signature**: `./.agents/scripts/helper.sh create-rule <name> <activation> [description_or_pattern]`
- **Parameters**:
  - `<name>`: Unique name for the rule. Must be strictly lowercase kebab-case (e.g., `no-raw-queries`).
  - `<activation>`: Rule activation mode. Valid modes are:
    - `manual`: User explicitly calls the rule.
    - `always-on`: Rule is always active for all files.
    - `model-decision`: Evaluated by AI agent decision. Needs a natural language description as the third parameter.
    - `glob`: Applies to files matching a glob pattern. Needs a glob pattern as the third parameter.
  - `[description_or_pattern]`: The activation argument (glob pattern or natural language rule description).
- **Behavior**: Scaffolds a new compliant markdown rule under `.agents/rules/<name>.md`.

#### 7. Architectural Decision Records (`create-adr`)
- **Signature**: `./.agents/scripts/helper.sh create-adr <title> [proposed|accepted|superseded]`
- **Parameters**:
  - `<title>`: Space-separated title of the ADR.
  - `[status]`: Initial status of the decision (defaults to `proposed`).
- **Behavior**: Scaffolds a new ADR file under `.agents/adrs/` with correct headers and status tags.

#### 8. Project Releases (`release`)
- **Signature**: `./.agents/scripts/helper.sh release <major|minor|patch>`
- **Parameters**:
  - `<major|minor|patch>`: Type of semantic version bump.
- **Behavior**: Automatically extracts the current version from `CHANGELOG.md`, calculates the bumped version, scaffolds the new release header, and prepares the version comparison links.

#### 9. Token Usage Tracker (`log-usage`)
- **Signature**: `./.agents/scripts/helper.sh log-usage <token_count>`
- **Parameters**:
  - `<token_count>`: Number of tokens consumed by the AI agent during the execution turn.
- **Behavior**: Accumulates usage inside `.agents/token_budget.json` to prevent exceeding agent token constraints.

#### 10. Local Git Profile Manager (`git-profile`)
- **Signature**: `./.agents/scripts/helper.sh git-profile [profile-key | name] [email]`
- **Usage Patterns**:
  - `./.agents/scripts/helper.sh git-profile`: Displays local/global configurations and lists available profiles.
  - `./.agents/scripts/helper.sh git-profile [profile-key]`: Loads a specific profile identity and sets up the local SSH key command.
  - `./.agents/scripts/helper.sh git-profile [name] [email]`: Configures user identity directly without config files.
  - `./.agents/scripts/helper.sh git-profile rotate` or `--rotate`: Rotates the repository's identity/SSH key config to the next profile based on the last commit email.

#### 11. Local API Profile Manager (`api-profile`)
- **Signature**: `./.agents/scripts/helper.sh api-profile [profile-key]`
- **Usage Patterns**:
  - `./.agents/scripts/helper.sh api-profile`: Displays the active API profile and lists available ones.
  - `./.agents/scripts/helper.sh api-profile [profile-key]`: Loads keys belonging to a specific profile and updates the active environment files.
  - `./.agents/scripts/helper.sh api-profile rotate` or `--rotate`: Rotates active API keys to the next profile in a round-robin cycle.

### 4.7 Windows PowerShell Wrapper (`helper.ps1`)

For developers working natively on Windows without standard Bash shells, a native PowerShell wrapper is available at `.agents/scripts/helper.ps1`.

- **Automatic Location**: The wrapper automatically searches for `bash.exe` (from Git Bash) in standard install directories (e.g., `C:\Program Files\Git\bin\bash.exe`) and in the system `PATH`.
- **Transparent Forwarding**: It forwards all command-line arguments directly to the underlying `helper.sh` script, making all CLI features (like `lock`, `validate`, `create-skill`) fully available in PowerShell.

---

## 5. Typical Workflow for the Agent
 
> [!NOTE]
> **Autonomous Script Execution**: Agents are instructed by the project architectural blueprint ([project_rules.md](file://./.agents/rules/project_rules.md)) to execute these operational commands (locking, validation, API sync, and archiving) automatically without requiring manual user commands.

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
- **Strict Bootstrapping sequence**: At startup, the agent MUST read `AGENTS.md` ➔ `rules/project_rules.md` ➔ `schema.md` ➔ `memory.md` in order. No other tools or files may be touched prior to this.
- **Git-Backed Memory Sync**: All schemas, ADRs, dynamic workflows, and memory files under `.agents/` (except `.agents/locks/`) MUST be committed to Git. The agent will run verification checks on startup to ensure your local clone is not behind upstream (`origin`).
- **No Agent Git Push/Pull**: The agent is **forbidden** from running remote operations like `git pull`, `git push`, or changing branches. The user must fetch/pull updates before starting work.
- **Discussion Traceability**: All `/grill-me` or design discussion outcomes are immediately saved to `.agents/workflows/task_<task_name>.md`. When feature branches are merged, running `helper.sh archive` moves these files to `.agents/archive/sprint_<branch>/` to keep active workspace clean.
- **Real-Time Schema & Dependency Sync**: Database model or API changes must immediately update `.agents/schemas/` and the main `.agents/schema.md` index before coding starts. Library dependencies must update `.agents/rules/project_rules.md` and package manager configs (`package.json`, etc.) immediately.
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
   *This automatically backs up your existing configuration files (`memory.md`, `rules/project_rules.md`, `schema.md`) to `.backup` extensions, updates system hooks and subdirectories, upgrades your active memory schema, and runs auto-recon to align rules.*

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
