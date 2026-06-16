import os
import sys
import subprocess
import shutil
import utils

def get_git_info():
    """Resolve active branch and local config email."""
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], 
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except:
        branch = "unknown"
        
    try:
        email = subprocess.check_output(
            ["git", "config", "user.email"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except:
        email = "not set"
        
    return branch, email

def get_active_api_profile():
    """Resolve active API profile name."""
    profile_file = os.path.join(utils.get_agents_dir(), 'active_api_profile_name')
    if os.path.exists(profile_file):
        try:
            with open(profile_file, 'r') as f:
                return f.read().strip()
        except:
            pass
    return "default"

def get_active_locks():
    """Scan and return active lock names."""
    locks_dir = os.path.join(utils.get_agents_dir(), 'locks')
    locks = []
    if os.path.exists(locks_dir):
        for item in os.listdir(locks_dir):
            if item.endswith('.lock'):
                locks.append(item[:-5].replace('_', '/'))
    return sorted(locks)

def run_subcommand(cmd_name, args_list=None):
    """Dynamically import and run a subcommand, trapping SystemExit."""
    if args_list is None:
        args_list = []
    
    cmd_map = {
        "lock": "lock",
        "unlock": "lock",
        "validate": "validate",
        "doctor": "doctor",
        "migrate": "migrate",
        "push": "push",
        "clean": "clean",
        "git-profile": "git_profile",
        "api-profile": "api_profile",
        "log-usage": "log_usage",
        "archive": "archive",
        "recon": "recon",
        "list-skills": "skills",
        "create-skill": "skills",
        "list-rules": "rules",
        "create-rule": "rules",
        "init": "init",
        "commit": "commit",
        "sync-git": "sync_git",
        "build": "build",
        "lint": "lint",
        "test": "test",
        "sync-api": "sync_api",
        "create-adr": "create_adr",
        "adr-wizard": "adr_wizard",
        "release": "release",
        "autocomplete": "autocomplete",
        "guide": "guide"
    }
    
    module_name = cmd_map.get(cmd_name)
    if not module_name:
        print(f"Error: Unknown subcommand mapping for '{cmd_name}'", file=sys.stderr)
        return False
        
    try:
        # Import the command module dynamically
        # Ensure 'commands' is in path (should be since helper.py does it)
        cmd_module = __import__(f"commands.{module_name}", fromlist=[module_name])
        # Execute the run function
        cmd_module.run([cmd_name] + args_list)
        return True
    except SystemExit as e:
        if e.code != 0:
            print(f"\n[INFO] Command '{cmd_name}' finished with exit code {e.code}")
            return False
        return True
    except Exception as e:
        print(f"\n[ERROR] Failed to execute '{cmd_name}': {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False

def show_git_profile_menu():
    """Interactive selector for git profiles."""
    profiles_file = ""
    agents_profiles = os.path.join(utils.get_agents_dir(), 'git_profiles')
    home_profiles = os.path.expanduser('~/.git_profiles')
    
    if os.path.exists(agents_profiles):
        profiles_file = agents_profiles
    elif os.path.exists(home_profiles):
        profiles_file = home_profiles
        
    config = {}
    if os.path.exists(profiles_file):
        with open(profiles_file, 'r') as f:
            for line in f:
                if line.strip() and not line.strip().startswith('#') and '=' in line:
                    parts = line.strip().split('=', 1)
                    config[parts[0].strip()] = parts[1].strip()
                    
    keys = sorted(list(set(k.split('.')[0] for k in config.keys() if k.endswith('.name'))))
    
    print("\n--- Git Profile Options ---")
    for i, k in enumerate(keys):
        p_n = config[f"{k}.name"]
        p_e = config.get(f"{k}.email", "")
        print(f"  [{i+1}] Switch to Profile '{k}': \"{p_n}\" <{p_e}>")
    
    offset = len(keys)
    print(f"  [{offset+1}] Rotate Profile (round-robin)")
    print(f"  [{offset+2}] Configure manual user.name and user.email")
    print("  [0] Cancel")
    
    try:
        val = input("\nSelect choice: ").strip()
        if not val or val == "0":
            return
            
        choice = int(val)
        if 1 <= choice <= len(keys):
            selected_profile = keys[choice - 1]
            run_subcommand("git-profile", [selected_profile])
        elif choice == offset + 1:
            run_subcommand("git-profile", ["rotate"])
        elif choice == offset + 2:
            name = input("Enter git user.name: ").strip()
            email = input("Enter git user.email: ").strip()
            if name and email:
                run_subcommand("git-profile", [name, email])
            else:
                print("Error: name and email cannot be empty.")
    except ValueError:
        print("Invalid choice.")
    except KeyboardInterrupt:
        print("\nCancelled.")

def show_api_profile_menu():
    """Interactive selector for API key profiles."""
    api_keys_file = ""
    agents_keys = os.path.join(utils.get_agents_dir(), 'api_keys')
    home_keys = os.path.expanduser('~/.antigravity_api_keys')
    if os.path.exists(agents_keys):
        api_keys_file = agents_keys
    elif os.path.exists(home_keys):
        api_keys_file = home_keys
        
    config = {}
    if os.path.exists(api_keys_file):
        with open(api_keys_file, 'r') as f:
            for line in f:
                if line.strip() and not line.strip().startswith('#') and '=' in line:
                    parts = line.strip().split('=', 1)
                    config[parts[0].strip()] = parts[1].strip()
                    
    profiles_list = sorted(list(set(k.split('.')[0] for k in config.keys() if '.' in k)))
    
    print("\n--- API Keys Profile Options ---")
    for i, p in enumerate(profiles_list):
        keys = [k.split('.', 1)[1] for k in config.keys() if k.startswith(f"{p}.")]
        print(f"  [{i+1}] Switch to Profile '{p}' ({' '.join(keys)})")
        
    offset = len(profiles_list)
    print(f"  [{offset+1}] Rotate Active API Profile")
    print("  [0] Cancel")
    
    try:
        val = input("\nSelect choice: ").strip()
        if not val or val == "0":
            return
            
        choice = int(val)
        if 1 <= choice <= len(profiles_list):
            selected_profile = profiles_list[choice - 1]
            run_subcommand("api-profile", [selected_profile])
        elif choice == offset + 1:
            run_subcommand("api-profile", ["rotate"])
    except ValueError:
        print("Invalid choice.")
    except KeyboardInterrupt:
        print("\nCancelled.")

def run(args):
    """Main interactive menu loop."""
    while True:
        branch, email = get_git_info()
        api_profile = get_active_api_profile()
        locks = get_active_locks()
        
        print("\n==========================================================")
        print("   🚀 Antigravity Agent Core - Interactive Dashboard 🚀   ")
        print("==========================================================")
        print(f"  Branch:  {branch:<15} |  API Profile: {api_profile}")
        print(f"  Email:   {email:<15} |  Active Locks: {', '.join(locks) if locks else 'None'}")
        print("==========================================================")
        
        print("\n  --- Daily Development ---")
        print("  [1] Lock a module for editing (lock)")
        print("  [2] Unlock a module (unlock)")
        print("  [3] Commit changes safely (commit)")
        print("  [4] Securely push branch to remote (push)")
        
        print("\n  --- Diagnostics & Audits ---")
        print("  [5] Run Health Diagnostics (doctor)")
        print("  [6] Validate compliance checks (validate)")
        
        print("\n  --- Configurations & Profiles ---")
        print("  [7] Switch/Rotate Git config profile (git-profile)")
        print("  [8] Switch/Rotate API key profile (api-profile)")
        print("  [9] Interactive guided ADR Wizard (adr-wizard)")
        
        print("\n  --- Workspace Utilities ---")
        print("  [10] View step-by-step Onboarding Tutorial (guide)")
        print("  [11] Purge Workspace / Clean up (clean)")
        print("  [12] Archive completed checklists (archive)")
        print("  [13] Codebase Stack Discovery (recon)")
        
        print("\n  [0] Exit Menu")
        print("==========================================================")
        
        try:
            choice = input("Select choice [0-13]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break
            
        if choice == "0":
            print("Goodbye!")
            break
        elif choice == "1":
            module = input("Enter module name to lock (e.g. core, auth, apps/backend) or [0] to cancel: ").strip()
            if module and module != "0":
                run_subcommand("lock", [module])
        elif choice == "2":
            active_locks = get_active_locks()
            if not active_locks:
                print("\n[INFO] No active locks found to unlock.")
                input("\nPress Enter to continue...")
                continue
                
            print("\n--- Active Module Locks ---")
            for i, lock in enumerate(active_locks):
                print(f"  [{i+1}] Unlock '{lock}'")
            print("  [0] Cancel")
            
            try:
                sel = input("\nSelect lock to release: ").strip()
                if sel and sel != "0":
                    idx = int(sel) - 1
                    if 0 <= idx < len(active_locks):
                        run_subcommand("unlock", [active_locks[idx]])
            except ValueError:
                print("Invalid choice.")
        elif choice == "3":
            run_subcommand("commit")
        elif choice == "4":
            print("\n--- Push Options ---")
            print("  [1] Secure push (runs validation, rotates SSH key) [Recommended]")
            print("  [2] Force push securely (--force)")
            print("  [3] Skip validation checks (--no-validate)")
            print("  [0] Cancel")
            push_sel = input("\nSelect push action: ").strip()
            if push_sel == "1":
                run_subcommand("push")
            elif push_sel == "2":
                run_subcommand("push", ["--force"])
            elif push_sel == "3":
                run_subcommand("push", ["--no-validate"])
        elif choice == "5":
            run_subcommand("doctor")
            input("\nPress Enter to return to menu...")
        elif choice == "6":
            run_subcommand("validate")
            input("\nPress Enter to return to menu...")
        elif choice == "7":
            show_git_profile_menu()
        elif choice == "8":
            show_api_profile_menu()
        elif choice == "9":
            run_subcommand("adr-wizard")
        elif choice == "10":
            run_subcommand("guide")
            input("\nPress Enter to return to menu...")
        elif choice == "11":
            print("\n⚠️  WARNING: Workspace Clean-up")
            print("This will delete active lock files, sprint archives, and reset")
            print("token budgets and active API configuration keys.")
            confirm = input("Are you sure you want to clean the workspace? (y/N): ").strip().lower()
            if confirm in ("y", "yes"):
                run_subcommand("clean")
                input("\nPress Enter to return to menu...")
        elif choice == "12":
            run_subcommand("archive")
            input("\nPress Enter to return to menu...")
        elif choice == "13":
            run_subcommand("recon")
            input("\nPress Enter to return to menu...")
        else:
            print("Invalid selection. Please enter a number from 0 to 13.")
            
        # Add a small separator line between loop cycles
        print("\n" + "-" * 58)
