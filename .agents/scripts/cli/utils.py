import os
import sys
import json
import time

def find_workspace_root():
    """
    Finds the directory containing the '.agents' folder, starting from the current directory
    and walking up. Defaults to the current directory if not found.
    """
    curr = os.path.abspath(os.getcwd())
    while True:
        if os.path.isdir(os.path.join(curr, '.agents')):
            return curr
        parent = os.path.dirname(curr)
        if parent == curr:
            break
        curr = parent
    return os.path.abspath(os.getcwd())

def get_agents_dir():
    return os.path.join(find_workspace_root(), '.agents')

def get_sh_executable():
    """
    Locates the 'sh' executable on Windows systems by checking PATH,
    auto-discovering via Git exec-path, and checking common paths.
    Returns 'sh' as a fallback or for non-Windows platforms.
    """
    import shutil
    import subprocess
    
    if os.name != 'nt':
        return 'sh'
        
    # 1. Check if 'sh' is already in PATH
    sh_path = shutil.which('sh')
    if sh_path:
        return sh_path
        
    # 2. Query Git exec-path to locate the Git root directory
    try:
        git_exec = subprocess.check_output(
            ["git", "--exec-path"], 
            stderr=subprocess.DEVNULL, 
            text=True
        ).strip()
        if git_exec:
            # git_exec is usually: C:\Program Files\Git\mingw64\libexec\git-core
            # We want to walk up to C:\Program Files\Git\
            git_exec_norm = os.path.normpath(git_exec)
            git_root = git_exec_norm
            for _ in range(3):
                git_root = os.path.dirname(git_root)
            
            # Check common subdirectories under Git root
            candidates = [
                os.path.join(git_root, 'bin', 'sh.exe'),
                os.path.join(git_root, 'usr', 'bin', 'sh.exe'),
            ]
            for candidate in candidates:
                if os.path.exists(candidate):
                    return candidate
    except Exception:
        pass
        
    # 3. Check hardcoded common installation paths on Windows
    common_paths = [
        r"C:\Program Files\Git\bin\sh.exe",
        r"C:\Program Files\Git\usr\bin\sh.exe",
        r"C:\Program Files (x86)\Git\bin\sh.exe",
        r"C:\Program Files (x86)\Git\usr\bin\sh.exe",
    ]
    for path in common_paths:
        if os.path.exists(path):
            return path
            
    # 4. Fallback
    return 'sh'

def run_shell_script(script_path, args=None):
    import subprocess
    if args is None:
        args = []
    if os.name == 'nt':
        sh_exe = get_sh_executable()
        return subprocess.run([sh_exe, script_path] + args)
    else:
        return subprocess.run([script_path] + args)

def get_memory_file():
    return os.path.join(get_agents_dir(), 'memory.md')

def print_title(title):
    print("==========================================================")
    print(f"  {title}")
    print("==========================================================")

def load_budget():
    budget_file = os.path.join(get_agents_dir(), 'token_budget.json')
    budget = {
        "max_token_budget": 500000,
        "current_token_usage": 0,
        "alert_threshold_percent": 90,
        "profiles": {}
    }
    if os.path.exists(budget_file):
        try:
            with open(budget_file, 'r') as f:
                budget = json.load(f)
        except:
            pass
            
    # Process automatic budget resets if configured
    reset_interval = budget.get("reset_interval")
    if reset_interval and reset_interval != "none":
        # Determine interval duration in seconds
        interval_seconds = None
        if reset_interval == "hourly":
            interval_seconds = 3600
        elif reset_interval == "daily":
            interval_seconds = 86400
        elif reset_interval == "weekly":
            interval_seconds = 604800
        elif reset_interval == "monthly":
            interval_seconds = 2592000
        else:
            try:
                interval_seconds = int(reset_interval)
            except ValueError:
                pass
                
        if interval_seconds is not None:
            current_time = int(time.time())
            last_reset = budget.get("last_reset_timestamp")
            
            # If last reset is not set, initialize it to the current time
            if last_reset is None:
                budget["last_reset_timestamp"] = current_time
                save_budget(budget)
            else:
                try:
                    last_reset = int(last_reset)
                except ValueError:
                    last_reset = current_time
                    budget["last_reset_timestamp"] = current_time
                    save_budget(budget)
                    
                if current_time - last_reset >= interval_seconds:
                    print(f"\n[INFO] Token budget reset interval ('{reset_interval}') has expired.")
                    print("Resetting all current token usage counts to 0.")
                    budget["current_token_usage"] = 0
                    if "profiles" in budget:
                        for profile in budget["profiles"].values():
                            if isinstance(profile, dict):
                                profile["current_token_usage"] = 0
                    budget["last_reset_timestamp"] = current_time
                    save_budget(budget)
                    
    return budget

def save_budget(budget):
    budget_file = os.path.join(get_agents_dir(), 'token_budget.json')
    with open(budget_file, 'w') as f:
        json.dump(budget, f, indent=2)

def log_token_usage(tokens):
    """
    Log token usage for both the active profile and globally.
    """
    budget = load_budget()
    
    # Update global usage
    budget["current_token_usage"] = budget.get("current_token_usage", 0) + tokens
    
    # Read active profile
    profile_file = os.path.join(get_agents_dir(), 'active_api_profile_name')
    active_profile = "default"
    if os.path.exists(profile_file):
        with open(profile_file, 'r') as f:
            active_profile = f.read().strip()
            
    # Update profile usage
    profiles = budget.get("profiles", {})
    if active_profile not in profiles:
        profiles[active_profile] = {
            "current_token_usage": 0,
            "max_token_budget": 500000
        }
    profiles[active_profile]["current_token_usage"] = profiles[active_profile].get("current_token_usage", 0) + tokens
    
    budget["profiles"] = profiles
    save_budget(budget)
    
    # Calculate warning thresholds
    global_usage = budget["current_token_usage"]
    global_limit = budget["max_token_budget"]
    pct = (global_usage / global_limit) * 100
    alert_threshold = budget.get("alert_threshold_percent", 90)
    
    print(f"Logged {tokens} tokens to profile '{active_profile}'.")
    print(f"  Active Profile Usage: {profiles[active_profile]['current_token_usage']} / {profiles[active_profile]['max_token_budget']}")
    print(f"  Global Usage: {global_usage} / {global_limit} ({pct:.1f}%)")
    
    if pct >= alert_threshold:
        print(f"\n[WARNING] Token usage has reached {pct:.1f}% of budget! Threshold is {alert_threshold}%.")
        print("Please wrap up your task, stage and commit completed tasks, and hand over.")
