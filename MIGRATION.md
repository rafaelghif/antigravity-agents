# Antigravity Agent Migration Guide (Version 1.4.0)

This guide provides instructions for upgrading existing workspaces configured with older versions of the Antigravity Agent setup to the new **World-Class Enterprise Grade (V1.4.0)** setup.

Version 1.4.0 introduces strict Git hook validation, unified workspace health checking (`doctor`), decoupled schema management, and automated branch-based checklist archiving.

---

## 1. Automated Migration (Recommended)

The easiest way to upgrade your workspace is using the new built-in `migrate` command in the agent helper.

Run the following command in Git Bash (Windows) or Terminal (Linux/macOS):

```bash
./.agents/scripts/helper.sh migrate
```

### What the Automated Migrator Does:
1. **Backs up User Files**: Automatically copies existing [.agents/project_rules.md](file://./.agents/project_rules.md) and [.agents/memory.md](file://./.agents/memory.md) to `.backup` files to ensure no custom configurations are lost.
2. **Updates Directory Structure**: Prepares directories for schemas, locks, workflows, and skills.
3. **Installs/Chains Git Hooks**: Copies and configures Git hooks (`pre-commit`, `post-commit`, `commit-msg`) in your local `.git/hooks/` directory, chaining them with any pre-existing custom hooks.
4. **Upgrades Memory Ledger**: Updates [.agents/memory.md](file://./.agents/memory.md) to the V5.0.0 layout.
5. **Configures Gitignore**: Ensures Git tracks system configurations under `.agents/` but ignores transient local lock files (`.agents/locks/`).
6. **Reconstructs Blueprints**: Runs the codebase stack auto-recon to generate the new project rules.

> [!WARNING]
> If you have custom rules configured in [.agents/project_rules.md](file://./.agents/project_rules.md), they will be backed up to `project_rules.md.backup`. Please review the backup and merge any custom rules back into the newly generated file.

---

## 2. Manual Migration Steps

If you prefer to migrate step-by-step or run on an environment where automated scripts are restricted, follow these steps:

### Step 2.1: Update Directory Structure
Create the required subdirectories inside `.agents/`:
```bash
mkdir -p .agents/skills .agents/workflows .agents/archive .agents/locks .agents/schemas .agents/scripts .agents/hooks
```

### Step 2.2: Upgrade the Memory Ledger Layout
Update [.agents/memory.md](file://./.agents/memory.md) to include the **Memory Schema Version** tag and the **Handover Notes** section. The top of the file must read:
```markdown
# Agent Core Memory

> **Memory Schema Version**: 5.0.0  
> **Target System**: Antigravity Agent Core
> **Active Guidelines**: Read [AGENTS.md](file://../AGENTS.md) and [.agents/project_rules.md](file://./project_rules.md) for execution details. Keep this file under 100 lines at all times.
```

Ensure the file contains the following high-level headers:
- `## 1. Git State & Infrastructure Runtime`
- `## 2. Active Epic & Sub-Tasks Execution Matrix`
- `## 3. Relayed Context & Handover Notes`
- `## 4. Reference Links Index`

### Step 2.3: Configure Gitignore Tracking
Open your root [.gitignore](file://./.gitignore) file and ensure the following rules are set:
```gitignore
# DO NOT ignore agent rules and memory
!.agents/
!AGENTS.md

# Ignore local locks and dynamic workflows in progress
.agents/locks/
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

After completing the migration (either automatically or manually), verify that the workspace is healthy by running:

```bash
./.agents/scripts/helper.sh doctor
```

And execute validation checks to ensure zero-hallucination compliance:

```bash
./.agents/scripts/helper.sh validate
```

If both commands report `PASS` or `VALIDATED`, your workspace is successfully upgraded!

> [!TIP]
> From now on, you do not need to run manual verification scripts before committing code. Simply use the standard `git commit` command. The hooks will automatically validate your code, verify conventional commit formats, and release any active locks when your commit succeeds.
