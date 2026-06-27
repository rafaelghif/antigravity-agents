import sys
import os
import subprocess
import socket
import json
from typing import List

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def print_err(msg: str) -> None:
    print(f"{RED}[FAIL] {msg}{RESET}")

def print_warn(msg: str) -> None:
    print(f"{YELLOW}[WARN] {msg}{RESET}")

def print_ok(msg: str) -> None:
    print(f"{GREEN}[OK] {msg}{RESET}")

def check_python() -> bool:
    print("Checking Python environment...")
    v = sys.version_info
    if v.major < 3 or (v.major == 3 and v.minor < 8):
        print_err(f"Python version {sys.version} is older than recommended 3.8.")
        return False
    print_ok(f"Python {v.major}.{v.minor}.{v.micro} verified.")
    return True

def check_git() -> bool:
    print("Checking Git CLI installation...")
    try:
        res = subprocess.run(['git', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0:
            print_ok(f"Git CLI detected: {res.stdout.strip()}")
            return True
        else:
            print_err("Git version check returned non-zero code.")
            return False
    except FileNotFoundError:
        print_err("Git binary 'git' not found in system PATH.")
        return False

def check_worktree() -> bool:
    print("Checking Git workspace root...")
    try:
        res = subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0 and res.stdout.strip() == "true":
            print_ok("Workspace is inside a valid Git work tree.")
            return True
        else:
            print_err("Not inside a Git repository work tree.")
            return False
    except Exception as e:
        print_err(f"Git workspace check failed: {e}")
        return False

def check_identity() -> bool:
    print("Checking Git identity configuration...")
    success = True
    try:
        res_email = subprocess.run(['git', 'config', 'user.email'], stdout=subprocess.PIPE, text=True)
        email = res_email.stdout.strip()
        res_name = subprocess.run(['git', 'config', 'user.name'], stdout=subprocess.PIPE, text=True)
        name = res_name.stdout.strip()
        
        if not email:
            print_warn("Git email ('user.email') is not configured.")
            success = False
        else:
            print_ok(f"Git Config Email: '{email}'")
            
        if not name:
            print_warn("Git name ('user.name') is not configured.")
            success = False
        else:
            print_ok(f"Git Config Name: '{name}'")
    except Exception as e:
        print_err(f"Failed to query Git identity: {e}")
        return False
    return success

def check_profiles() -> bool:
    print("Checking developer profiles config...")
    profiles_file = ".agents/git_profiles.json"
    if not os.path.exists(profiles_file):
        print_warn(f"Developer profiles config '{profiles_file}' is missing.")
        return False
        
    try:
        with open(profiles_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        profiles = data.get("profiles", [])
        if not profiles:
            print_warn("No profiles registered in git_profiles.json.")
            return False
            
        print_ok(f"Found {len(profiles)} registered developer profiles.")
        active = next((p for p in profiles if p.get("active")), None)
        if active:
            print_ok(f"Active profile: '{active.get('name')}' <{active.get('email')}>")
            ssh_key = active.get("ssh_key_path")
            if ssh_key:
                ssh_key_abs = os.path.abspath(os.path.expanduser(ssh_key))
                if os.path.exists(ssh_key_abs):
                    print_ok(f"SSH private key file verified: '{ssh_key_abs}'")
                else:
                    print_err(f"SSH private key file not found: '{ssh_key_abs}'")
                    return False
        else:
            print_warn("No active profile set in git_profiles.json.")
            
        return True
    except Exception as e:
        print_err(f"Error parsing git_profiles.json: {e}")
        return False

def check_network() -> bool:
    print("Checking network connectivity to remote repo domain (github.com)...")
    try:
        socket.setdefaulttimeout(2.0)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("github.com", 443))
        s.close()
        print_ok("Network connection to github.com verified.")
        return True
    except Exception as e:
        print_warn(f"Domain github.com is unreachable (offline mode active): {e}")
        return False

def handle_fixes() -> None:
    profiles_file = ".agents/git_profiles.json"
    profiles_example = ".agents/git_profiles.example"
    if not os.path.exists(profiles_file) and os.path.exists(profiles_example):
        print("Attempting to auto-fix missing profiles configuration...")
        try:
            import shutil
            shutil.copy(profiles_example, profiles_file)
            print_ok(f"Recovered '{profiles_file}' from example template.")
        except Exception as e:
            print_err(f"Auto-fix failed: {e}")

def run(args: List[str]) -> None:
    print("="*60)
    print("      Antigravity Agent Core (AAC) V2 Diagnostics Doctor")
    print("="*60)
    
    passed = True
    passed &= check_python()
    print("-"*60)
    passed &= check_git()
    print("-"*60)
    passed &= check_worktree()
    print("-"*60)
    passed &= check_identity()
    print("-"*60)
    passed &= check_profiles()
    print("-"*60)
    check_network()
    print("="*60)
    
    if not passed:
        print_warn("Diagnostics detected warnings or failures. Running auto-repairs...")
        handle_fixes()
        print("="*60)
        sys.exit(1)
    else:
        print_ok("All diagnostic audits PASSED! Local workspace is healthy.")
        print("="*60)
        sys.exit(0)
