import sys
import os
import shutil
import re
import subprocess
from datetime import datetime
from typing import List, Tuple

def print_err(msg: str) -> None:
    print(f"\033[91m[FAIL] {msg}\033[0m", file=sys.stderr)

def print_warn(msg: str) -> None:
    print(f"\033[93m[WARN] {msg}\033[0m")

def print_ok(msg: str) -> None:
    print(f"\033[92m[OK] {msg}\033[0m")

def should_exclude(rel_path: str) -> bool:
    """Determine if a file path should be excluded from installation copying."""
    normalized_path = rel_path.replace("/", os.sep).replace("\\", os.sep)
    parts = normalized_path.split(os.sep)
    
    # Exclude basic development directories
    if any(p in ("__pycache__", ".git", ".github") for p in parts):
        return True
        
    # Exclude git repository directory
    if ".git" in parts:
        return True
        
    # Exclude src directory to protect existing project code
    if len(parts) > 0 and parts[0] == "src":
        return True
        
    filename = os.path.basename(rel_path)
    
    # Exclude active/private configurations, keys, and databases
    excluded_filenames = {
        "git_profiles.json",
        "projects.json",
        "locks.json",
        "rules.md",
        ".DS_Store",
        "active_context.md",
        "token_budget.json",
        "sync_cache.json",
        "cooldowns.json",
        "upgrade_state.json",
        "schema.md",
        "api_keys",
        "active_api_keys",
        "active_api_keys.ps1",
        "active_api_profile_name",
        "mcp_config.json",
        "config.json",
        "CHANGELOG.md",
        "AGENTS.md",
        ".gitignore",
        ".antigravityignore",
        "Dockerfile",
        "README.md",
        "bootstrap.sh",
        "bootstrap.ps1",
        "install.sh",
        "install.ps1",
        "requirements.txt",
        "pyproject.toml",
        "architecture.md",
        "glossary.md",
        "lessons-archive.md",
        "lessons-learned.md",
        "milestones.md",
        "security-policy.md",
        "tech-debt.md"
    }
    
    if filename in excluded_filenames:
        return True
        
    if filename.endswith(('.pyc', '.pyo')):
        return True
        
    # Exclude active local directories in .agents/
    if len(parts) >= 2 and parts[0] == ".agents":
        sub_dir = parts[1]
        if sub_dir in ("tasks", "issues", "plans", "tests", "archive", "logs", "state"):
            return True
        if sub_dir == "memory":
            # Exclude everything in memory except templates/
            if len(parts) >= 3 and parts[2] not in ("templates",):
                return True
                
    return False

def run(args: List[str]) -> None:
    """Execute the unified python installation process."""
    print("==========================================================")
    print("   Installing Antigravity Agent Core V3...                ")
    print("==========================================================")

    # 1. Determine target directory
    target_dir = args[0] if args else "."
    target_abs = os.path.abspath(target_dir)
    print(f"Target Directory: {target_abs}")

    # 2. Verify target directory path
    try:
        os.makedirs(target_abs, exist_ok=True)
    except Exception as e:
        print_err(f"Failed to create target directory '{target_abs}': {e}")
        sys.exit(1)

    # 3. Resolve source repository root
    cmd_dir = os.path.dirname(os.path.abspath(__file__))
    source_root = os.path.abspath(os.path.join(cmd_dir, "../../../.."))

    # 4. Perform backups if upgrading an existing installation
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target_agents = os.path.join(target_abs, ".agents")
    if os.path.exists(target_agents):
        backup_agents = os.path.join(target_abs, f".agents_backup_{timestamp}")
        print(f"Existing installation found! Archiving to {os.path.basename(backup_agents)}...")
        try:
            shutil.move(target_agents, backup_agents)
        except Exception as e:
            print_err(f"Failed to archive existing .agents directory: {e}")
            sys.exit(1)
            
    target_agents_md = os.path.join(target_abs, "AGENTS.md")
    if os.path.exists(target_agents_md):
        backup_agents_md = os.path.join(target_abs, f"AGENTS.md.backup_{timestamp}")
        print(f"Backing up AGENTS.md to {os.path.basename(backup_agents_md)}...")
        try:
            shutil.copy(target_agents_md, backup_agents_md)
        except Exception as e:
            print_warn(f"Failed to backup AGENTS.md: {e}")

    # 5. Copy files recursively with exclusions
    print("Copying core files recursively...")
    copy_if_missing_filenames = {
        "schema.md",
        "AGENTS.md",
        ".gitignore",
        ".antigravityignore",
        "mcp_config.json",
        "config.json"
    }

    for root, dirs, files in os.walk(source_root):
        for f in files:
            source_file = os.path.join(root, f)
            rel_path = os.path.relpath(source_file, source_root)
            dest_file = os.path.join(target_abs, rel_path)
            
            if should_exclude(rel_path):
                filename = os.path.basename(rel_path)
                if filename in copy_if_missing_filenames and not os.path.exists(dest_file):
                    # Proceed with copying since it is safe and missing in target
                    pass
                else:
                    continue
                
            try:
                os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                shutil.copy2(source_file, dest_file)
            except Exception as e:
                print_warn(f"Failed to copy file '{rel_path}': {e}")


    # 6.5. Restore user configurations and workspace state from backup if upgrading
    if 'backup_agents' in locals() and os.path.exists(backup_agents):
        print("Restoring user configurations and workspace state from backup...")
        for root, dirs, files in os.walk(backup_agents):
            for f in files:
                backup_file = os.path.join(root, f)
                rel_path = os.path.relpath(backup_file, backup_agents)
                target_rel_path = os.path.join(".agents", rel_path)
                
                if should_exclude(target_rel_path):
                    dest_file = os.path.join(target_abs, target_rel_path)
                    try:
                        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                        shutil.copy2(backup_file, dest_file)
                    except Exception as e:
                        print_warn(f"Failed to restore file '{target_rel_path}' from backup: {e}")

    # 7. Initialize Git repo in target if not present
    target_git = os.path.join(target_abs, ".git")
    if not os.path.exists(target_git):
        print("Initializing empty Git repository in target directory...")
        try:
            subprocess.run(['git', '-C', target_abs, 'init'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            print_warn(f"Failed to initialize Git repository: {e}")

    # 8. Set helper.sh executable permission on Unix-like systems
    helper_sh = os.path.join(target_abs, "helper.sh")
    if os.path.exists(helper_sh) and os.name != 'nt':
        try:
            os.chmod(helper_sh, 0o755)
        except Exception:
            pass

    # 9. Invoke the bootstrapper logic inside the target directory context
    print("Transitioning to project setup and bootstrap configuration...")
    os.chdir(target_abs)
    
    # Load and run bootstrap command in target
    target_bootstrap_script = os.path.join(target_abs, ".agents", "scripts", "cli/commands/bootstrap.py")
    if os.path.exists(target_bootstrap_script):
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("bootstrap_cmd", target_bootstrap_script)
            if spec and spec.loader:
                bootstrap_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(bootstrap_module)
                
                # Pass the project name (basename of target dir) and forwarded arguments to bootstrap
                project_name = os.path.basename(target_abs)
                bootstrap_args = [project_name] + args[1:] + ["--no-scaffold"]
                bootstrap_module.run(bootstrap_args)
                print_ok("Bootstrap executed successfully.")
            else:
                print_err("Failed to load bootstrap script module spec.")
        except Exception as e:
            print_err(f"Error during bootstrap execution: {e}")
            sys.exit(1)
    else:
        print_err("Bootstrap script not found in target directories.")
        sys.exit(1)

    # 10. Run final synchronization in target directory
    print("Running final synchronization...")
    try:
        subprocess.run([sys.executable, ".agents/scripts/cli/helper.py", "sync"], check=True)
    except Exception as e:
        print_warn(f"Failed to execute final sync: {e}")

    print("==========================================================")
    print("   AAC V3 Installation Completed Successfully!            ")
    print("   Run './helper.sh validate' in target folder to test.   ")
    print("==========================================================")
