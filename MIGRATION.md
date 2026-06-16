# Antigravity Agent Migration Guide (Version 1.7.4)

This guide provides instructions for upgrading existing workspaces configured with older versions of the Antigravity Agent setup to the new **World-Class Enterprise Grade (V1.7.4)** setup.

Version 1.7.4 introduces native multi-platform API key auto-rotation (Bash and Windows PowerShell), per-profile token budgets, compile linter checks, and automated cross-platform rotation test suites.

---

## 1. Automated Migration (Recommended)

The easiest way to upgrade your workspace is using the new built-in `migrate` command in the agent helper.

**For Unix/Linux environments (Bash):**
```bash
./.agents/scripts/helper.sh migrate
```

**For Windows environments (PowerShell):**
```powershell
.\.agents\scripts\helper.ps1 migrate
```

### What the Automated Migrator Does:
1. **Backs up User Files**: Automatically copies existing [.agents/rules/project_rules.md](file://./.agents/rules/project_rules.md) and [.agents/memory.md](file://./.agents/memory.md) to `.backup` files to ensure no custom configurations are lost.
2. **Updates Directory Structure**: Prepares directories for schemas, locks, workflows, skills, and test suites.
3. **Installs/Chains Git Hooks**: Copies and configures Git hooks (`pre-commit`, `post-commit`, `commit-msg`) in your local `.git/hooks/` directory, chaining them with any pre-existing custom hooks.
4. **Upgrades Memory Ledger**: Updates [.agents/memory.md](file://./.agents/memory.md) to the V5.0.0 layout.
5. **Configures Gitignore**: Ensures Git ignores credential configuration files and active environment states (e.g. `.agents/api_keys`, `.agents/active_api_keys`, `.agents/active_api_keys.ps1`, `.agents/active_api_profile_name`) while keeping core protocol configurations tracked.
6. **Reconstructs Blueprints**: Runs the codebase stack auto-recon to generate the new project rules.

---

## 2. Manual Migration Steps

If you prefer to migrate step-by-step or run on an environment where automated scripts are restricted, follow these steps:

### Step 2.1: Update Directory Structure
Create the required subdirectories inside `.agents/`:
```bash
mkdir -p .agents/skills .agents/workflows .agents/archive .agents/locks .agents/schemas .agents/scripts .agents/hooks tests
```

### Step 2.2: Configure Gitignore Tracking
Open your root [.gitignore](file://./.gitignore) file and ensure the following rules are set to block credential leaks:
```gitignore
# DO NOT ignore agent rules and memory
!.agents/
!AGENTS.md

# Ignore agent transient locks
.agents/locks/

# Ignore local agent API key configuration and active state files
.agents/api_keys
.agents/active_api_keys
.agents/active_api_keys.ps1
.agents/active_api_profile_name

# Ignore python compile caches
__pycache__/
*.pyc
```

### Step 2.3: API key setup
Copy the API keys configuration example to `.agents/api_keys` and enter your credential configurations:
```bash
cp .agents/api_keys.example .agents/api_keys
```

### Step 2.4: Install Git Hooks
Copy hook scripts from `.agents/hooks/` to `.git/hooks/` and make them executable:
```bash
cp .agents/hooks/pre-commit .git/hooks/pre-commit
cp .agents/hooks/post-commit .git/hooks/post-commit
cp .agents/hooks/commit-msg .git/hooks/commit-msg
chmod +x .git/hooks/*
```

---

## 3. Post-Migration Verification

After completing the migration, verify that the workspace is healthy by running the doctor utility:

```bash
./.agents/scripts/helper.sh doctor
```

Execute the validation checkgate suite to ensure conventional commits, API configuration security, and token budget compliance:

```bash
./.agents/scripts/helper.sh validate
```

If both commands report `PASS` or `VALIDATED`, your workspace is successfully upgraded!

> [!TIP]
> To run commands with automated API key rotation in Windows PowerShell, use the new native wrapper script:
> ```powershell
> .\.agents\scripts\api-rotate-wrapper.ps1 [command_to_run] [args...]
> ```
