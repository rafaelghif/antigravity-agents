import os
import sys
import subprocess
import shutil
import json
import utils

def run(args):
    print("==========================================================")
    print("  Starting Antigravity Agent Workspace Clean-up...        ")
    print("==========================================================")

    # 1. Clear locks directory (except cli.lock)
    locks_dir = os.path.join(utils.get_agents_dir(), "locks")
    if os.path.exists(locks_dir):
        print("Cleaning locks...")
        for item in os.listdir(locks_dir):
            if item == "cli.lock":
                continue
            item_path = os.path.join(locks_dir, item)
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
                print(f"  Removed lock: {item}")
            except Exception as e:
                print(f"  Warning: Failed to remove lock {item}: {e}", file=sys.stderr)

    # 2. Clear archives directory
    archive_dir = os.path.join(utils.get_agents_dir(), "archive")
    if os.path.exists(archive_dir):
        print("Cleaning sprint archives...")
        for item in os.listdir(archive_dir):
            item_path = os.path.join(archive_dir, item)
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
                print(f"  Removed archive: {item}")
            except Exception as e:
                print(f"  Warning: Failed to remove archive {item}: {e}", file=sys.stderr)

    # 3. Clear workflows (except task_workspace_cleanup_command.md)
    workflows_dir = os.path.join(utils.get_agents_dir(), "workflows")
    if os.path.exists(workflows_dir):
        print("Cleaning task workflows...")
        for item in os.listdir(workflows_dir):
            if item == "task_workspace_cleanup_command.md":
                continue
            item_path = os.path.join(workflows_dir, item)
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
                print(f"  Removed workflow: {item}")
            except Exception as e:
                print(f"  Warning: Failed to remove workflow {item}: {e}", file=sys.stderr)

    # 4. Reset token budget json
    budget_file = os.path.join(utils.get_agents_dir(), "token_budget.json")
    print("Resetting token budget...")
    default_budget = {
        "max_token_budget": 500000,
        "current_token_usage": 0,
        "alert_threshold_percent": 90,
        "profiles": {}
    }
    try:
        with open(budget_file, "w") as f:
            json.dump(default_budget, f, indent=2)
        print("  [SUCCESS] Token budget reset to default limits.")
    except Exception as e:
        print(f"  Error: Failed to reset token budget: {e}", file=sys.stderr)

    # 5. Reset API profile name and active keys
    profile_name_file = os.path.join(utils.get_agents_dir(), "active_api_profile_name")
    active_keys_sh = os.path.join(utils.get_agents_dir(), "active_api_keys")
    active_keys_ps1 = os.path.join(utils.get_agents_dir(), "active_api_keys.ps1")

    print("Resetting active API key configurations...")
    try:
        with open(profile_name_file, "w") as f:
            f.write("default\n")
            
        with open(active_keys_sh, "w") as f:
            f.write("# Active API Keys configuration\n")
            f.write("export GEMINI_API_KEY=\"\"\n")
            f.write("export OPENAI_API_KEY=\"\"\n")
            f.write("export ANTHROPIC_API_KEY=\"\"\n")
            
        with open(active_keys_ps1, "w") as f:
            f.write("# Active API Keys configuration for Windows PowerShell\n")
            f.write("$env:GEMINI_API_KEY=\"\"\n")
            f.write("$env:OPENAI_API_KEY=\"\"\n")
            f.write("$env:ANTHROPIC_API_KEY=\"\"\n")
        print("  [SUCCESS] API profile configurations and keys reset to clean templates.")
    except Exception as e:
        print(f"  Error: Failed to reset active API keys: {e}", file=sys.stderr)

    # 6. Reset memory.md to clean template
    memory_file = utils.get_memory_file()
    print("Resetting active memory ledger...")
    
    # Resolve branch and commit
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], 
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except:
        branch = "main"
        
    try:
        commit = subprocess.check_output(
            ["git", "log", "-n", "1", "--format=%h"], 
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except:
        commit = "none"

    clean_memory_content = f"""# Agent Core Memory

> **Memory Schema Version**: 5.0.0  
> **Target System**: Antigravity Agent Core
> **Active Guidelines**: Read [AGENTS.md](file://../AGENTS.md) and [.agents/rules/project_rules.md](file://./rules/project_rules.md) for execution details. Keep this file under 100 lines at all times.

---

## 1. Git State & Infrastructure Runtime
- **Active Branch**: {branch}
- **Last Commit Reference**: {commit}
- **Active Pull Request Target**: `main`
- **Infrastructure Health Status**:
  - Database: `HEALTHY`
  - Cache/Broker: `HEALTHY`
  - Primary API Server: `HEALTHY`

---

## 2. Active Epic & Sub-Tasks Execution Matrix
- **Primary Epic**: Initial Setup
- **Current Task Target**: Configure workspace rules and verify stack
- **State Flag**: `COMPLETED`

### Sprint Tasks Checklist
- [x] Configure workspace rules and verify stack
- [x] Run health check doctor

---

## 3. Relayed Context & Handover Notes
- **Last Active Agent**: None
- **Last Action Completed**: Initialized clean Antigravity Agent Core workspace.
- **Next Planned Action**: None. Ready for new features or tasks.
- **Blockers / Runtime Notes**: None.

---

## 4. Reference Links Index
- **Core Guidelines**: [AGENTS.md](file://../AGENTS.md)
- **Project Specific Rules**: [project_rules.md](file://./rules/project_rules.md)
- **Database Schema**: [schema.md](file://./schema.md)
- **Design Decisions**: [adr.md](file://./adr.md)
- **Sprint Archives**: [archive/](file://./archive/)
"""
    try:
        with open(memory_file, "w") as f:
            f.write(clean_memory_content)
        print("  [SUCCESS] memory.md reset to default clean template.")
    except Exception as e:
        print(f"  Error: Failed to reset memory.md: {e}", file=sys.stderr)

    print("==========================================================")
    print("  Workspace clean-up completed successfully!             ")
    print("==========================================================")
