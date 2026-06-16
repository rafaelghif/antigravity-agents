# Operational Scripts Guide (`helper.sh`)

Once bootstrapped, operations are managed through `./.agents/scripts/helper.sh` (or `./.agents/scripts/helper.ps1` for native PowerShell support on Windows).

> [!NOTE]
> **Modular Python CLI Engine**: Starting from version `1.8.0`, AAC uses a modular Python CLI engine situated under `.agents/scripts/cli/`. The `helper.sh` and `helper.ps1` scripts serve as thin wrappers forwarding execution. This architecture isolates individual subcommands into separate modules, which drastically reduces token overhead for developer agents.

---

## 1. Quick Reference Cheat Sheet (Daily Essentials)

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

## 2. Command Quick Reference Table

| Command | Usage | Description |
|---|---|---|
| `init` | `init [name] [stack] [arch] [db_orm] [env_vars]` | Launches the setup questionnaire to scaffold directories, configurations, and file templates. |
| `recon` | `recon` | Runs the autonomous codebase scanner to map stacks, directories, databases, and routes. |
| `validate` | `validate` | Audits the project for secrets, memory cap limits, and domain decoupling. |
| `push` | `push [-f/--force] [-n/--no-validate]` | Runs workspace validation and pushes the current branch to origin using rotated SSH profile keys. |
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
| `adr-wizard` | `adr-wizard [args...]` | Interactive guided Architectural Decision Record (ADR) wizard. |
| `git-profile` | `git-profile [key/name/rotate] [email]` | Switches or displays Git config profiles and automates local SSH key rotation. |
| `api-profile` | `api-profile [key/rotate]` | Switches or displays API provider key profiles and automates local environment rotation. |
| `guide` | `guide` | Prints an interactive step-by-step developer onboarding tutorial to the terminal. |
| `clean` | `clean` | Purges workspace locks, archives, and resets memory/configs. |
| `menu` | `menu` | Launches the interactive developer dashboard menu (TUI). (Runs automatically when calling helper.sh without arguments in a TTY). |

---

## 3. Core Commands Detailed Reference

### 3.1 API Contract Synchronization (`sync-api`)
The `sync-api` command extracts the OpenAPI schema (`openapi.json`) from the backend application and synchronizes it with the frontend to generate a zero-dependency, fully-typed TypeScript fetch API client wrapper (`api-client.ts`).
- **FastAPI/Python Backend**: Automatically boots a minimal context to dump `app.openapi()` directly into `openapi.json`.
- **Go Gin Backend**: Runs `swag init` on the main server entry point to build and copy the schema.
- **Frontend Client Compilation**: Reads `openapi.json` and parses components, schemas, path parameters, query parameters, request bodies, and responses. Outputs interfaces and client classes at the appropriate frontend location (e.g., `src/lib/api-client.ts`).
- **Zero-Dependency**: The generated client is clean TypeScript that uses vanilla `fetch` and does not require third-party libraries.

### 3.2 Skill Scaffolding & Auditing (`create-skill` / `list-skills`)
To dynamically extend the agent's capabilities inside this workspace, you (or the agent) can create and audit specialized skills:
- **Create Skill**: Run `./.agents/scripts/helper.sh create-skill <name> [description]`. This scaffolds a new directory at `.agents/skills/<name>/` containing a standard, parameterizable `SKILL.md` template and a structured Python script wrapper inside `scripts/main.py`.
- **List & Audit Skills**: Run `./.agents/scripts/helper.sh list-skills`. This scans all registered skill directories and audits them for compliance:
  1. `SKILL.md` exists and starts with a valid YAML frontmatter header containing `name` and `description`.
  2. File body and script source code contain no unresolved placeholder markers (e.g. `TODO`, `FIXME`, or `[placeholder]`).
  3. All referenced scripts listed in the YAML header exist and have executable permissions (`chmod +x`).

### 3.3 Workspace Rules Scaffolding & Auditing (`create-rule` / `list-rules`)
Workspace rules define how coding standards are applied dynamically. The rules reside in the `.agents/rules/` directory (with backward compatibility/automatic migration for `.agent/rules/`):
- **Create Rule**: Run `./.agents/scripts/helper.sh create-rule <name> <activation> [param]`. Scaffolds a new markdown rule file under `.agents/rules/<name>.md`.
  * Activation modes: `manual`, `always-on`, `glob` (requires glob pattern param), and `model-decision` (requires NL description param).
- **List & Audit Rules**: Run `./.agents/scripts/helper.sh list-rules`. Audits all registered rule files for compliance:
  1. Valid `.md` file name extension.
  2. Valid YAML frontmatter containing `name` and `activation`.
  3. Correct configuration of activation-dependent parameter (e.g. `pattern` for Glob, `description` for Model Decision).
  4. Absence of unresolved placeholders (e.g. `TODO`, `FIXME`, `[placeholder]`) in the rule body.

### 3.4 Git Profile Management (`git-profile`)
The `git-profile` command allows developers to switch between multiple Git accounts (names, emails, and SSH keys) locally inside the repository.
- **Git Identity**: The tool configures `user.name` and `user.email` locally so they apply *only* to this repository.
- **SSH Authentication (Private Key)**: If you specify an `ssh_key` path, the tool sets `core.sshCommand = "ssh -i <path> -o IdentitiesOnly=yes"`. This instructs Git to use that specific private key when talking to GitHub (pushing/pulling) for *only* this repository.

#### A. Quick Start Guide
1. Copy the example file to `.agents/git_profiles` (which is already configured in `.gitignore` to keep your private details safe):
   ```bash
   cp .agents/git_profiles.example .agents/git_profiles
   ```
2. Open `.agents/git_profiles` and fill in your git accounts.
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
3. Switch accounts:
   - **Manual Switch**: `../../helper.sh git-profile work`
   - **Check Current Status**: `../../helper.sh git-profile`
   - **Manual Profile Rotation**: `../../helper.sh git-profile rotate`
   - **Automated Round-Robin Commit Rotation**: If multiple profiles are configured in `.agents/git_profiles`, running `./.agents/scripts/helper.sh commit` will **automatically rotate** the commit author and SSH key (round-robin) based on the author of the last commit.

#### B. Generate SSH Keys
* **On Linux, macOS, or Windows Git Bash**:
  ```bash
  ssh-keygen -t ed25519 -C "your_email@domain.com" -f ~/.ssh/id_rsa_name
  ```
* **On Windows Command Prompt (CMD)**:
  ```cmd
  ssh-keygen -t ed25519 -C "your_email@domain.com" -f %USERPROFILE%\.ssh\id_rsa_name
  ```

---

## 4. Detailed CLI Command Arguments Reference

### 4.1 Project Scaffolding Wizard (`init`)
- **Signature**: `./.agents/scripts/helper.sh init [name] [stack] [architecture] [db_orm] [env_vars]`
- **Parameters**:
  - `[name]`: Name of the project (e.g., `MyService`).
  - `[stack]`: Target language/stack (choices: `Next.js`, `Go Gin`, `FastAPI`, `Node/TypeScript`, `Go`, `Python`, `Monorepo`, `Multi-Project`, `Laravel`).
  - `[architecture]`: Architecture pattern (e.g., `clean`, `hexagonal`, `mvc`).
  - `[db_orm]`: Relational DB or ORM framework (e.g., `PostgreSQL`, `MongoDB`, `Prisma`, `None`).
  - `[env_vars]`: Space-separated configuration environment variables (e.g., `"PORT DATABASE_URL"`).
- **Behavior**: If any arguments are missing, the command falls back to an interactive setup menu automatically.

### 4.2 Conventional Commit Builder (`commit`)
- **Signature**: `./.agents/scripts/helper.sh commit [--no-test|--no-verify] [type] [scope] [description] [files...]`
- **Options & Flags**:
  - `--no-test`, `--no-verify`: Bypasses pre-commit test suites and workspace sanity validation checks.
  - `[type]`: Commit type (choices: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`, `perf`).
  - `[scope]`: Component scope of the modification (e.g., `core`, `auth`, `db`, `shared`).
  - `[description]`: Short conventional commit description.
  - `[files...]`: Optional paths to specific files to stage and commit. If omitted, all modified tracked files are staged.
- **Behavior**: Automatically performs the linter/test checks (unless bypassed), rotates the local Git profile and SSH key, and commits atomic changes. If parameters are omitted, it defaults to interactive prompts.

### 4.3 Module Locking (`lock` / `unlock`)
- **Signature**:
  - Lock: `./.agents/scripts/helper.sh lock <module>`
  - Unlock: `./.agents/scripts/helper.sh unlock <module>`
- **Parameters**:
  - `<module>`: Kebab-case or directory-path name of the module/domain to lock (e.g., `apps/backend`).
- **Behavior**: Acquires a transient lock by creating `.agents/locks/<module_sanitized>.lock`.

### 4.4 Skill Creation (`create-skill`)
- **Signature**: `./.agents/scripts/helper.sh create-skill <name> [description]`
- **Parameters**:
  - `<name>`: Unique name for the skill. Must be strictly lowercase kebab-case (e.g., `db-optimization`).
  - `[description]`: A brief summary of the skill's purpose.

### 4.5 Custom Workspace Rules (`create-rule`)
- **Signature**: `./.agents/scripts/helper.sh create-rule <name> <activation> [description_or_pattern]`
- **Parameters**:
  - `<name>`: Unique name for the rule. Must be strictly lowercase kebab-case.
  - `<activation>`: Rule activation mode. Valid modes are: `manual`, `always-on`, `model-decision`, `glob`.
  - `[description_or_pattern]`: The activation argument (glob pattern or natural language rule description).

### 4.6 Architectural Decision Records (`create-adr`)
- **Signature**: `./.agents/scripts/helper.sh create-adr <title> [proposed|accepted|superseded]`

### 4.7 Architectural Decision Record Wizard (`adr-wizard`)
- **Signature**: `./.agents/scripts/helper.sh adr-wizard [args...]`
- **Options**: Supports `--title`, `--status`, `--context`, `--decision`, `--consequences`, `--json <path>`. Fires interactive prompts if run without arguments in a TTY.

### 4.8 Token Usage Tracker (`log-usage`)
- **Signature**: `./.agents/scripts/helper.sh log-usage <token_count>`

### 4.9 Secure Git Push (`push`)
- **Signature**: `./.agents/scripts/helper.sh push [-f|--force] [-n|--no-validate]`
- **Options & Flags**:
  - `-f`, `--force`: Executes a force push (`git push origin <branch> --force`).
  - `-n`, `--no-validate`: Bypasses the workspace validation checks and matches warnings for non-aligned Git profiles.
- **Behavior**: Auto-detects the active local branch name, verifies that the current Git user email matches an identity inside `.agents/git_profiles`, dynamically injects `GIT_SSH_COMMAND="ssh -i <key> -o IdentitiesOnly=yes"` if the profile has a configured SSH key, runs workspace sanity validation checks, and executes `git push`.

### 4.10 Developer Onboarding Tutorial (`guide`)
- **Signature**: `./.agents/scripts/helper.sh guide`
- **Behavior**: Prints a beautifully formatted, easy-to-read developer guide inside the terminal, outlining the daily essentials workflow (locking, editing, and helper commits) and core diagnostics.

### 4.11 Purge Workspace Release (`clean`)
- **Signature**: `./.agents/scripts/helper.sh clean`
- **Behavior**: Prepares the workspace for a clean public release. It deletes all sprint archives under `.agents/archive/`, purges all task workflow files under `.agents/workflows/` (except the active cleanup workflow), clears active lock files under `.agents/locks/` (except the active cleanup lock), resets the token budget to default limits, resets the active API profile, and writes a clean template version of `.agents/memory.md` containing dynamically resolved Git branch and commit information.

### 4.12 Interactive Dashboard Menu (`menu`)
- **Signature**: `./.agents/scripts/helper.sh` (when interactive with no arguments) or `./.agents/scripts/helper.sh menu`
- **Behavior**: Launches a user-friendly, interactive dashboard menu in the console. It groups commands logically (Daily Development, Diagnostics, Profiles, Utilities) and enables quick number/name selection. When releasing locks, it scans active locks in the repository and shows them as a selection list to prevent typos. It also requires explicit confirmation before executing the `clean` subcommand.

---

## 5. Windows PowerShell Wrapper (`helper.ps1`)

For developers working natively on Windows without standard Bash shells, a native PowerShell wrapper is available at `.agents/scripts/helper.ps1`.
- **Automatic Location**: The wrapper automatically searches for `bash.exe` (from Git Bash) in standard install directories (e.g., `C:\Program Files\Git\bin\bash.exe`) and in the system `PATH`.
- **Transparent Forwarding**: It forwards all command-line arguments directly to the underlying `helper.sh` script, making all CLI features (like `lock`, `validate`, `create-skill`) fully available in PowerShell.
