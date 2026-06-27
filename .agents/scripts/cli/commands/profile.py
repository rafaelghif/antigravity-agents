import sys
import os
import json
import re
import subprocess
from typing import List, Dict, Any

PROFILES_FILE = ".agents/git_profiles.json"
PROFILES_EXAMPLE = ".agents/git_profiles.example"

# Terminal Colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def print_err(msg: str) -> None:
    print(f"{RED}[FAIL] {msg}{RESET}", file=sys.stderr)

def print_warn(msg: str) -> None:
    print(f"{YELLOW}[WARN] {msg}{RESET}")

def print_ok(msg: str) -> None:
    print(f"{GREEN}[OK] {msg}{RESET}")

def ensure_profiles_file() -> None:
    """Ensure that the git profiles json file exists in the workspace."""
    if os.path.exists(PROFILES_FILE):
        return
    if os.path.exists(PROFILES_EXAMPLE):
        try:
            import shutil
            shutil.copy(PROFILES_EXAMPLE, PROFILES_FILE)
            print_ok(f"Initialized '{PROFILES_FILE}' from example configuration.")
        except Exception as e:
            print_err(f"Failed to initialize git profiles JSON: {e}")
            sys.exit(1)
    else:
        # Create empty fallback structure
        try:
            with open(PROFILES_FILE, 'w', encoding='utf-8') as f:
                json.dump({"profiles": []}, f, indent=2)
        except Exception as e:
            print_err(f"Failed to create empty git profiles JSON: {e}")
            sys.exit(1)

def load_profiles() -> Dict[str, Any]:
    """Load git profiles from file, ignoring comments starting with '#'."""
    ensure_profiles_file()
    try:
        with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
            lines = [line for line in f if not line.strip().startswith("#")]
            return json.loads("".join(lines))
    except Exception as e:
        print_err(f"Failed to load git profiles: {e}")
        sys.exit(1)

def save_profiles(data: Dict[str, Any]) -> None:
    """Save profiles dict back to JSON file."""
    try:
        with open(PROFILES_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print_err(f"Failed to save git profiles: {e}")
        sys.exit(1)

def handle_list(args: List[str]) -> None:
    """List all registered profiles, highlighting the active one."""
    data = load_profiles()
    profiles = data.get("profiles", [])
    if not profiles:
        print("No profiles registered.")
        return
        
    print("Registered Git Profiles:")
    for p in profiles:
        name = p.get("name", "Unknown")
        email = p.get("email", "unknown@domain.com")
        active = p.get("active", False)
        
        if active:
            print(f"  {GREEN}* {name} ({email}) [active]{RESET}")
        else:
            print(f"    {name} ({email})")

def apply_git_config(profile: Dict[str, Any]) -> None:
    """Immediately configure the local Git repository settings."""
    # Check if we are inside a Git repository
    git_check = subprocess.run(
        ['git', 'rev-parse', '--is-inside-work-tree'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if git_check.returncode != 0:
        print_warn("Not inside a Git repository. Profile updated in JSON but local Git config not applied.")
        return
        
    email = profile.get("email")
    name = profile.get("name")
    signing_key = profile.get("signing_key")
    
    try:
        if email:
            subprocess.run(['git', 'config', '--local', 'user.email', email], check=True)
        if name:
            subprocess.run(['git', 'config', '--local', 'user.name', name], check=True)
            
        if signing_key and not signing_key.endswith("..."):
            subprocess.run(['git', 'config', '--local', 'user.signingkey', signing_key], check=True)
            subprocess.run(['git', 'config', '--local', 'commit.gpgsign', 'true'], check=True)
        else:
            subprocess.run(['git', 'config', '--local', '--unset', 'commit.gpgsign'], stderr=subprocess.DEVNULL)
            subprocess.run(['git', 'config', '--local', '--unset', 'user.signingkey'], stderr=subprocess.DEVNULL)
            
        ssh_key = profile.get("ssh_key_path")
        if ssh_key:
            subprocess.run(['git', 'config', '--local', 'core.sshCommand', f'ssh -i {ssh_key} -o IdentitiesOnly=yes'], check=True)
        else:
            subprocess.run(['git', 'config', '--local', '--unset', 'core.sshCommand'], stderr=subprocess.DEVNULL)
            
        print_ok(f"Applied Git Profile to local config: '{name}' <{email}>")
    except subprocess.CalledProcessError as e:
        print_err(f"Failed to apply local Git configuration: {e}")

def handle_switch(args: List[str]) -> None:
    """Switch active profile by name and apply settings to Git config."""
    if not args:
        print_err("Usage: helper.py profile switch <name>")
        sys.exit(1)
        
    target_name = args[0]
    data = load_profiles()
    profiles = data.get("profiles", [])
    
    found = False
    for p in profiles:
        if p.get("name") == target_name:
            p["active"] = True
            found = True
        else:
            p["active"] = False
            
    if not found:
        print_err(f"Profile '{target_name}' not found.")
        sys.exit(1)
        
    save_profiles(data)
    print_ok(f"Switched active profile to '{target_name}'.")
    
    # Locate the active profile and apply it
    for p in profiles:
        if p.get("active"):
            apply_git_config(p)
            break

def validate_name(name: str) -> bool:
    """Validate name is alphanumeric, hyphens, or underscores."""
    return bool(re.match(r'^[a-zA-Z0-9_\-]+$', name))

def validate_email(email: str) -> bool:
    """Validate basic email format."""
    return bool(re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email))

def handle_add(args: List[str]) -> None:
    """Add a new profile to JSON configuration."""
    if len(args) < 2:
        print_err("Usage: helper.py profile add <name> <email> [signing_key] [--switch|-s]")
        sys.exit(1)
        
    name = args[0]
    email = args[1]
    
    signing_key = None
    switch_after = False
    
    remaining_args = args[2:]
    for arg in remaining_args:
        if arg in ('--switch', '-s'):
            switch_after = True
        elif not arg.startswith('-'):
            signing_key = arg
            
    if not validate_name(name):
        print_err(f"Invalid profile name '{name}'. Only alphanumeric, hyphens, and underscores allowed.")
        sys.exit(1)
        
    if not validate_email(email):
        print_err(f"Invalid email format: '{email}'.")
        sys.exit(1)
        
    data = load_profiles()
    profiles = data.get("profiles", [])
    
    for p in profiles:
        if p.get("name") == name:
            print_err(f"Profile '{name}' already exists.")
            sys.exit(1)
            
    new_profile = {
        "name": name,
        "email": email,
        "active": False
    }
    if signing_key:
        new_profile["signing_key"] = signing_key
        
    profiles.append(new_profile)
    data["profiles"] = profiles
    save_profiles(data)
    print_ok(f"Profile '{name}' successfully added.")
    
    if switch_after:
        handle_switch([name])

def run(args: List[str]) -> None:
    """Main CLI dispatch entry point for profile command."""
    if not args:
        print("Usage: helper.py profile <list|switch|add> [args...]")
        sys.exit(1)
        
    subcmd = args[0].lower()
    if subcmd == "list":
        handle_list(args[1:])
    elif subcmd == "switch":
        handle_switch(args[1:])
    elif subcmd == "add":
        handle_add(args[1:])
    else:
        print_err(f"Unknown subcommand '{subcmd}'. Available: list, switch, add")
        sys.exit(1)
