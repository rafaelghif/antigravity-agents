# Antigravity Agent Core (AAC) V2 🚀

A project-agnostic, enterprise-grade developer protocol and operational workspace layout designed to standardize AI coding assistants (like Gemini, Claude, Cursor, Aider, and GPT-4) across **any** tech stack.

AAC V2 optimizes prompt caching, prevents secrets leakage, enforces architectural insulation, and dynamically auto-adapts to your project's programming languages and tools.

---

## 🌟 Supported Stacks (Stack-Agnostic)

AAC V2's auto-reconnaissance engine dynamically scans your repository and configures rules, schemas, and build/test environments for:
- **Node.js**: JavaScript, TypeScript, Next.js, React, Vue, NestJS, Express
- **PHP**: Core PHP, Laravel, WordPress
- **Python**: Python 3 standard, Pytest, Poetry, Pipenv
- **Go**: Golang modules and tooling
- **Rust**: Cargo suites
- **Java & Kotlin**: Maven and Gradle configurations
- **CSS / Styling**: Tailwind CSS, SCSS, Vanilla CSS
- **Containerization**: Docker, Docker Compose

---

## 🚀 Getting Started (3-Step Setup)

To bootstrap your AI assistant in **any new or existing repository**:

### 1. Run the Installer
Run the bootstrap installer script inside your project's root folder:

**Linux / macOS (Bash):**
```bash
curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; Invoke-WebRequest -Uri "https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/install.ps1" -OutFile "install.ps1"; .\install.ps1
```

### 2. Auto-Detect Your Stack
The installer automatically triggers the reconnaissance script (`.agents/scripts/recon.py`), which:
- Scans your project structure recursively.
- Replaces the placeholders in `AGENTS.md` with your detected languages and tools.
- Automatically writes test/build rules in `.agents/rules.md`.

### 3. Start Coding with the Agent
When prompting your agent, refer to the master instruction guidelines:
> "Read AGENTS.md and align with our workspace layout, rules, and memory ledger."

---

## 🛠️ AAC V2 CLI Commands Reference

AAC V2 provides a unified command dispatcher wrapper `./helper.sh` (Linux/macOS) and `./helper.ps1` (Windows) to manage all developer workflows.

| Command | Usage | Description |
|---|---|---|
| **`bootstrap`** | `./helper.sh bootstrap` | Scaffolds directories, detects stack, writes `AGENTS.md`, and guides Git profile setup. |
| **`validate`** | `./helper.sh validate` | Runs local validation guard check (8 core audits: critical files, secrets/ignored files, links, task board, git alignment, syntax, unit tests). |
| **`issue`** | `./helper.sh issue <subcommand>` | Local issue tracker. Supports `list`, `add <title>`, `view <id>`, and `close <id>`. |
| **`lock`** | `./helper.sh lock <module>` | Local locks for collaborative coding. Run with `--release <module>` to unlock. |
| **`profile`** | `./helper.sh profile <subcommand>` | Credentials manager. Supports `add <name> <email>`, `switch <name>`, `list`, and `apply`. |
| **`changelog`** | `./helper.sh changelog` | Auto-changelog generator. Parses conventional commits and bumps SemVer version. |
| **`sync`** | `./helper.sh sync` | Synchronizes custom skills index in `AGENTS.md` and ADR registries in `architecture.md`. |
| **`learn`** | `./helper.sh learn "Lesson..."` | Records developer/agent lessons, post-mortems, and solutions directly to `lessons-learned.md`. |
| **`doctor`** | `./helper.sh doctor` | Diagnostics doctor that verifies host environment health, identity setups, and network checks. |
| **`upgrade`** | `./helper.sh upgrade` | Auto-upgrades agent core scripts and templates from the official repository. |
| **`completion`** | `./helper.sh completion <bash/zsh>` | Generates terminal tab-completion configurations. |
| **`install-global`**| `./helper.sh install-global` | Installs the global wrapper launcher command `aac` into the user PATH. |

---

## 🌐 Global Wrapper Installation (`aac`)

To run Antigravity Agent Core commands globally from any subdirectory inside your project workspace (instead of writing `./helper.sh` or relative paths), install the global launcher alias:

1. **Install launcher wrapper**:
   ```bash
   ./helper.sh install-global
   ```
2. **Path Setup**:
   * **Linux/macOS**: If `~/.local/bin` is not in your environment PATH, add this line to your shell configuration (`~/.bashrc` or `~/.zshrc`):
     ```bash
     export PATH="$HOME/.local/bin:$PATH"
     ```
   * **Windows**: If not present, run this in PowerShell:
     ```powershell
     [Environment]::SetEnvironmentVariable('Path', [Environment]::GetEnvironmentVariable('Path', 'User') + ';$HOME\.local\bin', 'User')
     ```
3. **Usage**:
   Once registered, run any command globally:
   ```bash
   aac validate
   aac profile list
   ```

---

## ⌨️ Shell Tab-Completion Integration

Speed up command invocation with tab completion for Bash and Zsh:

### For Bash:
1. Append the completion script output to your `~/.bashrc`:
   ```bash
   aac completion bash >> ~/.bashrc
   ```
2. Source your shell configuration:
   ```bash
   source ~/.bashrc
   ```

### For Zsh:
1. Create a completion directory in your user home:
   ```zsh
   mkdir -p ~/.zsh/completion
   ```
2. Redirect the completion script to a file prefixed with `_`:
   ```zsh
   aac completion zsh > ~/.zsh/completion/_aac
   ```
3. Add the completion path to your `~/.zshrc` before calling `compinit`:
   ```zsh
   fpath=(~/.zsh/completion $fpath)
   autoload -U compinit || compinit
   ```
4. Restart your terminal or source your profile:
   ```zsh
   source ~/.zshrc
   ```

---

## 🔒 Developer Profile & Identity Rotation

To prevent committing code under mismatched Git author emails (e.g. leaking personal emails in corporate repositories), AAC V2 implements active profile matching:

1. **Configuring Profiles**: Register developer profiles in `.agents/git_profiles.json` (created automatically from `.agents/git_profiles.example`):
   ```bash
   ./helper.sh profile add corp-work developer@company.com
   ```
2. **Switching Identities**: Switch between accounts dynamically:
   ```bash
   ./helper.sh profile switch corp-work
   ```
3. **Email Validation Gate**: The validation guard (`./helper.sh validate`) automatically compares `git config user.email` with the active profile. If they do not match, validation fails and blocks the pre-commit hook.

---

## 🔑 Collaborative Module Locking

To prevent developers or autonomous agents from modifying the same files concurrently, AAC V2 uses a lightweight, local-only module locking workflow:

- **Locking a Module**: Lock a script or subdirectory before editing:
  ```bash
  ./helper.sh lock validate
  ```
  This creates a lock entry in `.agents/locks.json` mapped to your active branch.
- **Acquiring Conflicts**: If another developer tries to lock the same module, the CLI blocks the action and prints the active branch owner.
- **Stale Lock Auto-Release**: The lock script and validation guard dynamically verify local git refs. If a lock's holder branch is merged or deleted locally, the lock is automatically pruned and released.

---

## 🔄 Safe Automated Upgrades

Upgrading an older version of Antigravity Agent Core is fully automated and risk-free:
- When the installer (`install.sh` or `bootstrap.ps1`) runs in a folder that already contains `.agents`, it automatically generates a timestamped archive:
  - Moving `.agents/` to `.agents_backup_YYYYMMDD_HHMMSS/`
  - Copying `AGENTS.md` to `AGENTS.md.backup_YYYYMMDD_HHMMSS`
- A clean, template-initialized V2 folder is written, ensuring no obsolete or stale files remain, while keeping all previous configurations safely archived.

---

## 🔀 Monorepo & Multi-Project Synchronization

For projects with separate backend and frontend services (e.g., `app/backend` and `app/frontend`), AAC V2 provides seamless multi-project orchestration:

1. **Configuring Sub-Projects**: Add your sub-projects mapping inside `.agents/projects.json`:
   ```json
   {
     "projects": [
       {
         "name": "backend",
         "path": "app/backend",
         "stack": "python",
         "test_command": "pytest"
       },
       {
         "name": "frontend",
         "path": "app/frontend",
         "stack": "node",
         "test_command": "npm run test"
       }
     ]
   }
   ```
2. **Automated Cross-Testing**: The local validation command `./helper.sh validate` scans the registered sub-projects and executes their respective test suites automatically.
3. **API Contract Alignment**: The `contract-synchronization` skill playbooks ensure TypeScript types, frontend API routes, and client bindings are auto-generated from the backend specification (e.g. OpenAPI/Swagger YAML) and never modified manually, preventing interface mismatches.

---

## 📂 The V2 Directory Blueprint

After running the bootstrap, your project will have the following layout:
- `AGENTS.md` (root): Master rules and directory maps loaded by the agent on every prompt.
- `.agents/rules.md`: Automatically generated build, test, and style configurations.
- `.agents/schema.md`: Holds definitions for config schemas and data formats.
- `.agents/projects.json`: Defines paths and test commands for sub-projects in a monorepo setup.
- `.agents/tasks/board.md`: Active markdown task board for tracking progress.
- `.agents/memory/`:
  - `architecture.md`: High-level system architecture summary.
  - `decisions/`: Repository containing Architectural Decision Records (ADRs).
  - `glossary.md`: Key terms definitions.
  - `tech-debt.md` & `lessons-learned.md`: Logs for long-term project quality.
- `.agents/skills/`: Executable playbooks (e.g. `code-review/`, `debugging/`, `coding-standards/`, `contract-synchronization/`).
- `.agents/workflows/`: Automation macros for shell slash commands.

---

## ⚠️ Disclaimer (No Warranty)

> [!WARNING]
> **No Warranty**: Antigravity Agent Core (AAC) is provided **"as-is"** without any warranty of any kind, express or implied. The developers and contributors make no representations or warranties regarding the security, accuracy, reliability, or correctness of code modifications, credential management, or task executions performed by the agent.
> 
> Using this agent involves executing code, managing local keys, and modifying repository content. You assume all risks associated with its use, including but not limited to potential data loss, local environment misconfigurations, or API rate-limiting issues.
