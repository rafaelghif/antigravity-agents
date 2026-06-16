import os
import sys
import subprocess
import shutil
import utils

# ANSI Color Escape Codes
C_HEADER = '\033[95m'
C_BLUE = '\033[94m'
C_CYAN = '\033[96m'
C_GREEN = '\033[92m'
C_YELLOW = '\033[93m'
C_RED = '\033[91m'
C_GRAY = '\033[90m'
C_BOLD = '\033[1m'
C_END = '\033[0m'

def color(text, ansi_code):
    """Wrap text in ANSI color codes if stdout is a TTY."""
    if sys.stdout.isatty():
        return f"{ansi_code}{text}{C_END}"
    return text

def get_progress_bar(pct, length=15):
    """Generate a visual progress bar string."""
    filled = int(round(length * pct / 100))
    filled = max(0, min(filled, length))
    bar = "█" * filled + "░" * (length - filled)
    
    # Color the progress bar based on percentage
    if pct >= 90:
        return color(bar, C_RED)
    elif pct >= 75:
        return color(bar, C_YELLOW)
    return color(bar, C_GREEN)

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
        print(color(f"Error: Unknown subcommand mapping for '{cmd_name}'", C_RED), file=sys.stderr)
        return False
        
    try:
        # Import the command module dynamically
        cmd_module = __import__(f"commands.{module_name}", fromlist=[module_name])
        # Execute the run function
        cmd_module.run([cmd_name] + args_list)
        return True
    except SystemExit as e:
        if e.code != 0:
            print(color(f"\n[INFO] Command '{cmd_name}' finished with exit code {e.code}", C_YELLOW))
            return False
        return True
    except Exception as e:
        print(color(f"\n[ERROR] Failed to execute '{cmd_name}': {e}", C_RED), file=sys.stderr)
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
    
    print(color("\n--- 👥 Git Identity Profiles ---", C_BOLD + C_CYAN))
    for i, k in enumerate(keys):
        p_n = config[f"{k}.name"]
        p_e = config.get(f"{k}.email", "")
        print(f"  [{color(str(i+1), C_GREEN)}] Switch to {color(k, C_BOLD)}: \"{p_n}\" <{p_e}>")
    
    offset = len(keys)
    print(f"  [{color(str(offset+1), C_GREEN)}] Rotate Profiles (round-robin)")
    print(f"  [{color(str(offset+2), C_GREEN)}] Manually enter new Name & Email")
    print(f"  [{color('0', C_YELLOW)}] Cancel")
    
    try:
        val = input(color("\nSelect choice: ", C_BOLD)).strip()
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
                print(color("Error: name and email cannot be empty.", C_RED))
    except ValueError:
        print(color("Invalid choice.", C_RED))
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
    
    print(color("\n--- 🔑 API Provider Key Profiles ---", C_BOLD + C_CYAN))
    for i, p in enumerate(profiles_list):
        keys = [k.split('.', 1)[1] for k in config.keys() if k.startswith(f"{p}.")]
        print(f"  [{color(str(i+1), C_GREEN)}] Switch to {color(p, C_BOLD)} ({', '.join(keys)})")
        
    offset = len(profiles_list)
    print(f"  [{color(str(offset+1), C_GREEN)}] Rotate Active API Profiles")
    print(f"  [{color('0', C_YELLOW)}] Cancel")
    
    try:
        val = input(color("\nSelect choice: ", C_BOLD)).strip()
        if not val or val == "0":
            return
            
        choice = int(val)
        if 1 <= choice <= len(profiles_list):
            selected_profile = profiles_list[choice - 1]
            run_subcommand("api-profile", [selected_profile])
        elif choice == offset + 1:
            run_subcommand("api-profile", ["rotate"])
    except ValueError:
        print(color("Invalid choice.", C_RED))
    except KeyboardInterrupt:
        print("\nCancelled.")

def run(args):
    """Main interactive menu loop."""
    while True:
        branch, email = get_git_info()
        api_profile = get_active_api_profile()
        locks = get_active_locks()
        
        # Load token budget statistics
        budget = utils.load_budget()
        global_usage = budget.get("current_token_usage", 0)
        global_limit = budget.get("max_token_budget", 500000)
        pct = (global_usage / global_limit) * 100 if global_limit > 0 else 0
        bar = get_progress_bar(pct, length=12)
        
        # Draw Beautiful Card Header
        print("\n" + color("+" + "="*58 + "+", C_BLUE))
        print(color("|", C_BLUE) + color(f"   🚀  ANTIGRAVITY AGENT WORKSPACE CONTROL PANEL   ", C_BOLD + C_HEADER) + " "*7 + color("|", C_BLUE))
        print(color("+" + "="*58 + "+", C_BLUE))
        
        branch_colored = color(branch, C_GREEN if branch != "unknown" else C_GRAY)
        email_colored = color(email, C_CYAN if email != "not set" else C_GRAY)
        api_profile_colored = color(api_profile, C_GREEN)
        
        if locks:
            locks_colored = color(f"⚠️  Locked: {', '.join(locks)}", C_YELLOW)
        else:
            locks_colored = color("🔓 Open", C_GREEN)
            
        print(f"  Branch:      {branch_colored:<25} |  API Profile:  {api_profile_colored}")
        print(f"  Git Email:   {email_colored:<25} |  Locks:        {locks_colored}")
        print(f"  Token Limit: {global_usage:,} / {global_limit:,} tokens [{bar}] {pct:.1f}%")
        print(color("+" + "-"*58 + "+", C_BLUE))
        
        print(color("\n  --- 🛠️  DAILY DEVELOPMENT ---", C_BOLD + C_BLUE))
        print(f"  [{color('1', C_GREEN)}] 🔒 Lock a folder for editing (prevent parallel edits)")
        print(f"  [{color('2', C_GREEN)}] 🔓 Unlock a folder (make it available again)")
        print(f"  [{color('3', C_GREEN)}] 💾 Save & Commit changes (auto-rotates Git profiles + checks)")
        print(f"  [{color('4', C_GREEN)}] 🚀 Push to Git Repository (runs security checks + pushes)")
        
        print(color("\n  --- 🩺 DIAGNOSTICS & SECURITY ---", C_BOLD + C_BLUE))
        print(f"  [{color('5', C_GREEN)}] 🩺 Run Doctor Health diagnostics (checks hooks & permissions)")
        print(f"  [{color('6', C_GREEN)}] 🛡️  Validate Compliance (scan for secrets, budget & rules)")
        
        print(color("\n  --- ⚙️  CONFIGURATIONS & PROFILES ---", C_BOLD + C_BLUE))
        print(f"  [{color('7', C_GREEN)}] 👤 Switch/Rotate local Git identity profiles")
        print(f"  [{color('8', C_GREEN)}] 🔑 Switch/Rotate API key credentials profiles")
        print(f"  [{color('9', C_GREEN)}] 📝 Run guided ADR Wizard (document architectural decisions)")
        
        print(color("\n  --- 📚 UTILITIES & HELP ---", C_BOLD + C_BLUE))
        print(f"  [{color('10', C_GREEN)}] 📖 View Step-by-Step Onboarding Tutorial")
        print(f"  [{color('11', C_GREEN)}] 🧹 Clean Workspace (prepare repo for a clean public clone)")
        print(f"  [{color('12', C_GREEN)}] 📦 Archive sprint checkpoints (prevents memory merge conflicts)")
        print(f"  [{color('13', C_GREEN)}] 🔍 Scan codebase tech-stack topology")
        
        print(color(f"\n  [{color('0', C_YELLOW)}] Exit Dashboard", C_BOLD))
        print(color("+" + "="*58 + "+", C_BLUE))
        
        try:
            choice = input(color("Select choice [0-13]: ", C_BOLD)).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break
            
        if choice == "0":
            print("Goodbye!")
            break
        elif choice == "1":
            module = input("\nEnter folder/module name to lock (e.g. core, auth, apps/backend) or [0] to cancel: ").strip()
            if module and module != "0":
                run_subcommand("lock", [module])
        elif choice == "2":
            active_locks = get_active_locks()
            if not active_locks:
                print(color("\n[INFO] No active locks found.", C_CYAN))
                input("\nPress Enter to continue...")
                continue
                
            print(color("\n--- Active Module Locks ---", C_BOLD + C_CYAN))
            for i, lock in enumerate(active_locks):
                print(f"  [{color(str(i+1), C_GREEN)}] Unlock '{color(lock, C_BOLD)}'")
            print(f"  [{color('0', C_YELLOW)}] Cancel")
            
            try:
                sel = input(color("\nSelect lock to release: ", C_BOLD)).strip()
                if sel and sel != "0":
                    idx = int(sel) - 1
                    if 0 <= idx < len(active_locks):
                        run_subcommand("unlock", [active_locks[idx]])
            except ValueError:
                print(color("Invalid choice.", C_RED))
        elif choice == "3":
            run_subcommand("commit")
        elif choice == "4":
            print(color("\n--- Secure Push Actions ---", C_BOLD + C_CYAN))
            print(f"  [{color('1', C_GREEN)}] Standard push (runs validation, rotates SSH key) [Recommended]")
            print(f"  [{color('2', C_GREEN)}] Force push (--force)")
            print(f"  [{color('3', C_GREEN)}] Skip validation checks (--no-validate)")
            print(f"  [{color('0', C_YELLOW)}] Cancel")
            push_sel = input(color("\nSelect push action: ", C_BOLD)).strip()
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
            print(color("\n⚠️  WARNING: Workspace Clean-up", C_YELLOW + C_BOLD))
            print("This will delete active lock files, sprint archives, and reset")
            print("token budgets and active API configuration keys.")
            confirm = input(color("Are you sure you want to clean the workspace? (y/N): ", C_BOLD)).strip().lower()
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
            print(color("Invalid selection. Please enter a number from 0 to 13.", C_RED))
            
        print("\n" + color("-" * 60, C_BLUE))
