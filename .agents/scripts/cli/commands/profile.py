import sys
import os
import json
import re
import subprocess
import shutil
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

def find_ssh_keygen() -> str:
    """Attempt to locate ssh-keygen on Windows if not in PATH."""
    binary = shutil.which("ssh-keygen")
    if binary:
        return binary
        
    if os.name == 'nt':
        common_paths = [
            r"C:\Program Files\Git\usr\bin\ssh-keygen.exe",
            r"C:\Program Files (x86)\Git\usr\bin\ssh-keygen.exe",
            os.path.expandvars(r"%USERPROFILE%\AppData\Local\Programs\Git\usr\bin\ssh-keygen.exe")
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path
    return "ssh-keygen"

def generate_ssh_key(name: str, email: str) -> str:
    """Generate a secure Ed25519 SSH key pair for the profile."""
    ssh_dir = os.path.abspath(os.environ.get("AAC_SSH_DIR") or os.path.expanduser("~/.ssh"))
    try:
        os.makedirs(ssh_dir, mode=0o700, exist_ok=True)
    except Exception as e:
        print_warn(f"Failed to create SSH directory '{ssh_dir}': {e}. Trying current workspace directory.")
        ssh_dir = os.path.abspath(".agents")
        
    key_path = os.path.join(ssh_dir, f"id_ed25519_{name}")
    
    if os.path.exists(key_path):
        print_warn(f"SSH private key file already exists at '{key_path}'. Registering the existing key.")
        return key_path
        
    keygen_bin = find_ssh_keygen()
    print(f"Generating secure Ed25519 SSH key pair at '{key_path}'...")
    passphrase = ""
    if sys.stdin.isatty() and "unittest" not in sys.modules:
        try:
            import getpass
            print("Note: You can secure your SSH key with a passphrase (press Enter for passphraseless):")
            p1 = getpass.getpass("Enter passphrase: ")
            if p1:
                p2 = getpass.getpass("Enter same passphrase again: ")
                if p1 == p2:
                    passphrase = p1
                else:
                    print_warn("Passphrases do not match! Defaulting to passphraseless key for automation.")
        except Exception:
            pass
    else:
        print_warn("Non-interactive terminal detected. Defaulting to passphraseless SSH key generation.")

    try:
        res = subprocess.run(
            [keygen_bin, '-t', 'ed25519', '-C', email, '-f', key_path, '-N', passphrase],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if res.returncode != 0:
            print_err(f"Failed to generate SSH key: {res.stderr.strip()}")
            sys.exit(1)
            
        print_ok("SSH key pair generated successfully.")
        
        pub_path = f"{key_path}.pub"
        if os.path.exists(pub_path):
            with open(pub_path, 'r', encoding='utf-8') as f:
                pub_key = f.read().strip()
            print("\n" + "="*60)
            print(f"{GREEN}ACTION REQUIRED:{RESET} Add this SSH public key to your GitHub account:")
            print("-"*60)
            print(pub_key)
            print("="*60 + "\n")
            
        return key_path
    except Exception as e:
        print_err(f"Error executing ssh-keygen: {e}")
        sys.exit(1)

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

def heal_credential_helper_path() -> None:
    """Automatically detect and fix absolute path mismatches in git credential.helper config."""
    try:
        git_check = subprocess.run(
            ['git', 'rev-parse', '--is-inside-work-tree'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if git_check.returncode != 0:
            return
            
        res = subprocess.run(
            ['git', 'config', '--local', 'credential.helper'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if res.returncode != 0 or not res.stdout.strip():
            return
            
        current_helper = res.stdout.strip()
        if "profile credential-helper" not in current_helper:
            return
            
        current_helper_py = os.path.abspath(os.path.join(os.path.dirname(__file__), "../helper.py"))
        current_python_exe = sys.executable
        
        expected_helper = f'!"{current_python_exe}" "{current_helper_py}" profile credential-helper'
        if current_helper != expected_helper:
            print("Self-Healing: Git credential.helper path drift detected. Updating path configuration.")
            subprocess.run(['git', 'config', '--local', 'credential.helper', expected_helper], check=True)
    except Exception:
        pass

def load_profiles() -> Dict[str, Any]:
    """Load git profiles from file, ignoring comments starting with '#'."""
    heal_credential_helper_path()
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

def extract_gpg_key_id(key_block: str) -> str:
    """Extract Key ID/fingerprint from GPG armored key block using gpg --show-keys."""
    try:
        # Try colons first
        res = subprocess.run(
            ['gpg', '--show-keys', '--with-colons'],
            input=key_block,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                parts = line.split(':')
                if len(parts) > 4 and parts[0] == 'pub':
                    return parts[4] # Standard key ID field in colon format
                if len(parts) > 9 and parts[0] == 'fpr':
                    return parts[9] # Fingerprint field
                    
        # Fallback to standard show-keys
        res2 = subprocess.run(
            ['gpg', '--show-keys'],
            input=key_block,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if res2.returncode == 0:
            lines = res2.stdout.splitlines()
            for i, line in enumerate(lines):
                if "pub " in line or "sec " in line:
                    if i + 1 < len(lines):
                        return lines[i+1].strip()
    except Exception:
        pass
    return None

def validate_safe_path(path: str) -> bool:
    """Validate that the path does not contain shell command injection characters."""
    # Permitted characters: alphanumeric, dots, hyphens, underscores, slashes, backslashes, colons, tildes, and spaces.
    pattern = r"^[a-zA-Z0-9_\-\.\/\~\:\s\\]+$"
    return bool(re.match(pattern, path))

def apply_git_config(profile: Dict[str, Any], force_no_gpg: bool = False) -> None:
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
    signing_key = None if force_no_gpg else profile.get("signing_key")
    
    # Dynamic GPG private key block loading
    if not force_no_gpg:
        gpg_key_block = None
        if "gpg_private_key" in profile:
            gpg_key_block = profile["gpg_private_key"]
        elif "gpg_private_key_env" in profile:
            env_var = profile["gpg_private_key_env"]
            gpg_key_block = os.environ.get(env_var)
        elif "gpg_private_key_file" in profile:
            key_file = os.path.expanduser(profile["gpg_private_key_file"])
            if os.path.exists(key_file):
                try:
                    with open(key_file, 'r', encoding='utf-8') as f:
                        gpg_key_block = f.read()
                except Exception:
                    pass

        if gpg_key_block:
            print("Importing dynamic GPG private key...")
            try:
                res_import = subprocess.run(
                    ['gpg', '--import', '--batch', '--yes'],
                    input=gpg_key_block,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                if res_import.returncode == 0:
                    print_ok("Successfully imported GPG private key dynamically.")
                    # Try to extract the Key ID to configure user.signingkey if not already explicitly set
                    if not signing_key:
                        extracted_id = extract_gpg_key_id(gpg_key_block)
                        if extracted_id:
                            signing_key = extracted_id
                            print_ok(f"Automatically resolved GPG signing key ID: {signing_key}")
                else:
                    print_warn(f"Failed to import GPG private key: {res_import.stderr.strip()}")
            except Exception as e:
                print_warn(f"Error importing GPG key: {e}")
    
    try:
        if email:
            subprocess.run(['git', 'config', '--local', 'user.email', email], check=True)
        if name:
            subprocess.run(['git', 'config', '--local', 'user.name', name], check=True)
            
        if signing_key and not signing_key.endswith("..."):
            subprocess.run(['git', 'config', '--local', 'user.signingkey', signing_key], check=True)
            subprocess.run(['git', 'config', '--local', 'commit.gpgsign', 'true'], check=True)
            if signing_key.startswith("ssh-") or "ssh" in signing_key:
                subprocess.run(['git', 'config', '--local', 'gpg.format', 'ssh'], check=True)
            else:
                subprocess.run(['git', 'config', '--local', 'gpg.format', 'openpgp'], check=True)
        else:
            subprocess.run(['git', 'config', '--local', '--unset', 'commit.gpgsign'], stderr=subprocess.DEVNULL)
            subprocess.run(['git', 'config', '--local', '--unset', 'user.signingkey'], stderr=subprocess.DEVNULL)
            subprocess.run(['git', 'config', '--local', '--unset', 'gpg.format'], stderr=subprocess.DEVNULL)
            
        ssh_key = profile.get("ssh_key_path")
        if ssh_key:
            if not validate_safe_path(ssh_key):
                print_err(f"Security Alert: SSH key path contains dangerous shell characters: {ssh_key}")
                sys.exit(1)
            ssh_key_abs = os.path.abspath(os.path.expanduser(ssh_key))
            if not validate_safe_path(ssh_key_abs):
                print_err(f"Security Alert: Absolute SSH key path contains dangerous shell characters: {ssh_key_abs}")
                sys.exit(1)
            subprocess.run(['git', 'config', '--local', 'core.sshCommand', f'ssh -i "{ssh_key_abs}" -o IdentitiesOnly=yes'], check=True)
        else:
            subprocess.run(['git', 'config', '--local', '--unset', 'core.sshCommand'], stderr=subprocess.DEVNULL)
            
        profile_env_suffix = name.upper().replace("-", "_").replace(".", "_")
        profile_env_var = f"AAC_GITHUB_TOKEN_{profile_env_suffix}"
        has_env_token = os.getenv(profile_env_var) is not None
        
        git_pat = profile.get("git_pat") or profile.get("git_token")
        is_dummy = git_pat and (git_pat.startswith("ghp_corporateToken") or git_pat.startswith("ghp_personalToken"))
        
        if (git_pat and not is_dummy) or has_env_token:
            helper_py = os.path.abspath(os.path.join(os.path.dirname(__file__), "../helper.py"))
            python_exe = sys.executable
            subprocess.run(['git', 'config', '--local', 'credential.helper', f'!"{python_exe}" "{helper_py}" profile credential-helper'], check=True)
        else:
            subprocess.run(['git', 'config', '--local', '--unset', 'credential.helper'], stderr=subprocess.DEVNULL)
            
        print_ok(f"Applied Git Profile to local config: '{name}' <{email}>")
    except subprocess.CalledProcessError as e:
        print_err(f"Failed to apply local Git configuration: {e}")

def handle_switch(args: List[str]) -> None:
    """Switch active profile by name and apply settings to Git config."""
    force_no_gpg = False
    if "--force-no-gpg" in args:
        force_no_gpg = True
        args.remove("--force-no-gpg")
        
    data = load_profiles()
    profiles = data.get("profiles", [])
    
    if not args:
        if not profiles:
            print_err("No profiles found to switch. Please add a profile first: './helper.sh profile add'")
            sys.exit(1)
            
        cli_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if cli_dir not in sys.path:
            sys.path.insert(0, cli_dir)
        from interactive import interactive_select
        
        options = []
        default_idx = 0
        for idx, p in enumerate(profiles):
            desc = p.get("email")
            if p.get("active"):
                desc += " (active)"
                default_idx = idx
            options.append({"name": p.get("name"), "desc": desc})
            
        selection = interactive_select(options, title="Select a profile to switch to:", default_idx=default_idx)
        if not selection:
            print(f"{YELLOW}[WARN] Switch aborted.{RESET}")
            sys.exit(0)
        target_name = selection.get("name")
    else:
        target_name = args[0]
        
    target_profile = None
    for p in profiles:
        if p.get("name") == target_name:
            target_profile = p
            break
            
    if not target_profile:
        print_err(f"Profile '{target_name}' not found.")
        sys.exit(1)
        
    ssh_key = target_profile.get("ssh_key_path")
    if ssh_key:
        ssh_key_abs = os.path.abspath(os.path.expanduser(ssh_key))
        if not os.path.exists(ssh_key_abs):
            print_warn(f"SSH private key file not found at '{ssh_key_abs}'.")
            is_interactive = sys.stdin.isatty() and os.getenv("ANTIGRAVITY_AGENT") != "1" and os.getenv("ANTIGRAVITY_NONINTERACTIVE") != "1"
            if is_interactive:
                gen_choice = input("Would you like us to generate a new secure SSH key pair for this profile? (Y/n) [y]: ").strip().lower() or "y"
                if gen_choice == "y":
                    generated_path = generate_ssh_key(target_name, target_profile.get("email"))
                    target_profile["ssh_key_path"] = generated_path
                    save_profiles(data)
            else:
                print_warn("Commitment verification might fail if this key is required.")
        else:
            print_ok(f"SSH private key verified at '{ssh_key_abs}'.")

    signing_key = target_profile.get("signing_key")
    if signing_key and not signing_key.endswith("...") and not force_no_gpg and not (signing_key.startswith("ssh-") or "ssh" in signing_key):
        print(f"Validating GPG signing key '{signing_key}'...")
        try:
            gpg_check = subprocess.run(
                ['gpg', '--list-secret-keys', '--keyid-format', 'LONG', signing_key],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if gpg_check.returncode != 0:
                print_warn(f"GPG signing key '{signing_key}' is not found or is invalid on this machine.")
                is_interactive = sys.stdin.isatty() and os.getenv("ANTIGRAVITY_AGENT") != "1" and os.getenv("ANTIGRAVITY_NONINTERACTIVE") != "1" and 'unittest' not in sys.modules and 'pytest' not in sys.modules and os.getenv("CI") != "true"
                if is_interactive:
                    disable_choice = input("Disable local Git commit signing for this session to prevent commit failures? (Y/n) [y]: ").strip().lower() or "y"
                    if disable_choice == "y":
                        force_no_gpg = True
                else:
                    print_warn("Commit signing might fail if this key is required.")
            else:
                print_ok("GPG signing key is valid.")
        except FileNotFoundError:
            print_warn("GnuPG ('gpg') tool is not installed on this machine. Cannot verify GPG signing key validity.")
            print_warn("Proceeding with profile switch anyway.")
            
    for p in profiles:
        if p.get("name") == target_name:
            p["active"] = True
        else:
            p["active"] = False
            
    save_profiles(data)
    print_ok(f"Switched active profile to '{target_name}'.")
    
    # Locate the active profile and apply it
    for p in profiles:
        if p.get("active"):
            apply_git_config(p, force_no_gpg)
            break

def validate_name(name: str) -> bool:
    """Validate name is alphanumeric, hyphens, or underscores."""
    return bool(re.match(r'^[a-zA-Z0-9_\-]+$', name))

def validate_email(email: str) -> bool:
    """Validate basic email format."""
    return bool(re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email))

def run_interactive_wizard() -> Dict[str, Any]:
    """Guide the developer through registering a new profile step-by-step."""
    print("\n" + "="*60)
    print(f"{GREEN}   Antigravity Profile Registration Wizard   {RESET}")
    print("="*60)
    print("Configure a new Git profile step-by-step.\n")
    
    try:
        # 1. Profile Name
        while True:
            name = input("1. Enter Profile Name (alphanumeric, hyphens, underscores): ").strip()
            if not name:
                print("   Profile name cannot be empty.")
                continue
            if not validate_name(name):
                print("   Invalid name format. Only alphanumeric, hyphens, and underscores are allowed.")
                continue
            # Check uniqueness
            data = load_profiles()
            profiles = data.get("profiles", [])
            if any(p.get("name") == name for p in profiles):
                print(f"   Profile '{name}' already exists. Please choose a different name.")
                continue
            break
            
        # 2. Email
        while True:
            email = input("2. Enter Git Email: ").strip()
            if not email:
                print("   Email cannot be empty.")
                continue
            if not validate_email(email):
                print("   Invalid email format. Please try again.")
                continue
            break
            
        # 3. Signing Type
        signing_key = None
        ssh_key_path = None
        
        print("\n3. Choose Commit Signing Option:")
        print("   [1] None (default)")
        print("   [2] SSH Key (Automatic generation or existing file)")
        print("   [3] GPG Key (Existing keyring Key ID)")
        choice = input("Enter choice (1-3) [1]: ").strip() or "1"
        
        if choice == "2":
            gen_choice = input("   Would you like us to generate a new secure SSH key pair? (Y/n) [y]: ").strip().lower() or "y"
            if gen_choice == "y":
                ssh_key_path = generate_ssh_key(name, email)
                # Read the public key to use as the signing key
                pub_key_path = f"{ssh_key_path}.pub"
                if os.path.exists(pub_key_path):
                    try:
                        with open(pub_key_path, 'r', encoding='utf-8') as f:
                            signing_key = f.read().strip()
                    except Exception:
                        pass
            else:
                while True:
                    path_input = input("   Enter path to your private SSH key: ").strip()
                    if not path_input:
                        print("   SSH key path cannot be empty.")
                        continue
                    ssh_key_path = os.path.expanduser(path_input)
                    if not os.path.exists(ssh_key_path):
                        print(f"   Warning: file '{ssh_key_path}' does not exist yet. We will register it anyway.")
                    # Check if public key exists to set signing_key
                    pub_key_path = f"{ssh_key_path}.pub"
                    if os.path.exists(pub_key_path):
                        try:
                            with open(pub_key_path, 'r', encoding='utf-8') as f:
                                signing_key = f.read().strip()
                        except Exception:
                            pass
                    break
        elif choice == "3":
            while True:
                gpg_input = input("   Enter GPG Key ID (e.g. 4A1D5B or 16-char hex): ").strip()
                if not gpg_input:
                    print("   GPG Key ID cannot be empty.")
                    continue
                signing_key = gpg_input
                break
                
        # 4. GitHub PAT
        print("\n4. Authentication Token:")
        print("   (Tip: To avoid plain-text storage, press Enter to skip and instead set the environment")
        print(f"   variable 'AAC_GITHUB_TOKEN_{name.upper().replace('-', '_').replace('.', '_')}' inside your shell)")
        git_pat = input("   Enter GitHub Personal Access Token (PAT) [press Enter to skip]: ").strip()
        if not git_pat:
            git_pat = None
            
        # 5. Switch Immediately
        switch_choice = input("\n5. Switch to this new profile immediately? (Y/n) [y]: ").strip().lower() or "y"
        switch_after = (switch_choice == "y")
        
        return {
            "name": name,
            "email": email,
            "signing_key": signing_key,
            "ssh_key_path": ssh_key_path,
            "git_pat": git_pat,
            "switch_after": switch_after
        }
        
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}[WARN] Profile registration wizard aborted.{RESET}")
        sys.exit(0)

def handle_add(args: List[str]) -> None:
    """Add a new profile to JSON configuration."""
    if len(args) == 0:
        wizard_data = run_interactive_wizard()
        name = wizard_data["name"]
        email = wizard_data["email"]
        signing_key = wizard_data["signing_key"]
        ssh_key_path = wizard_data["ssh_key_path"]
        git_pat = wizard_data["git_pat"]
        switch_after = wizard_data["switch_after"]
        generate_ssh = False
    else:
        if len(args) < 2:
            print_err("Usage: helper.py profile add <name> <email> [signing_key] [--ssh-key <path>] [--git-pat <pat>] [--generate-ssh] [--switch|-s]")
            sys.exit(1)
            
        name = args[0]
        email = args[1]
        
        signing_key = None
        ssh_key_path = None
        git_pat = None
        generate_ssh = False
        switch_after = False
        
        i = 2
        while i < len(args):
            arg = args[i]
            if arg in ('--switch', '-s'):
                switch_after = True
                i += 1
            elif arg == '--ssh-key':
                if i + 1 < len(args):
                    ssh_key_path = args[i+1]
                    i += 2
                else:
                    print_err("Error: --ssh-key requires a path argument.")
                    sys.exit(1)
            elif arg in ('--git-pat', '--git-token'):
                if i + 1 < len(args):
                    git_pat = args[i+1]
                    i += 2
                else:
                    print_err(f"Error: {arg} requires a PAT argument.")
                    sys.exit(1)
            elif arg == '--generate-ssh':
                generate_ssh = True
                i += 1
            elif not arg.startswith('-'):
                signing_key = arg
                i += 1
            else:
                i += 1
            
    if not validate_name(name):
        print_err(f"Invalid profile name '{name}'. Only alphanumeric, hyphens, and underscores allowed.")
        sys.exit(1)
        
    if not validate_email(email):
        print_err(f"Invalid email format: '{email}'.")
        sys.exit(1)
        
    if ssh_key_path and generate_ssh:
        print_err("Error: --ssh-key and --generate-ssh options are mutually exclusive.")
        sys.exit(1)
        
    if ssh_key_path:
        if not validate_safe_path(ssh_key_path):
            print_err(f"Invalid SSH key path '{ssh_key_path}'. Dangerous characters are not allowed.")
            sys.exit(1)
        
    data = load_profiles()
    profiles = data.get("profiles", [])
    
    for p in profiles:
        if p.get("name") == name:
            print_err(f"Profile '{name}' already exists.")
            sys.exit(1)
            
    if generate_ssh:
        ssh_key_path = generate_ssh_key(name, email)
            
    new_profile = {
        "name": name,
        "email": email,
        "active": False
    }
    if signing_key:
        new_profile["signing_key"] = signing_key
    if ssh_key_path:
        new_profile["ssh_key_path"] = ssh_key_path
    if git_pat:
        new_profile["git_pat"] = git_pat
        
    profiles.append(new_profile)
    data["profiles"] = profiles
    save_profiles(data)
    print_ok(f"Profile '{name}' successfully added.")
    
    if switch_after:
        handle_switch([name])

def handle_credential_helper(args: List[str]) -> None:
    """Implement Git Credential Helper protocol to dynamically rotate HTTPS tokens."""
    if not args:
        sys.exit(0)
        
    action = args[0].lower()
    if action == "get":
        query = {}
        for line in sys.stdin:
            line = line.strip()
            if not line:
                break
            if "=" in line:
                k, v = line.split("=", 1)
                query[k] = v
                
        data = load_profiles()
        profiles = data.get("profiles", [])
        active_profile = next((p for p in profiles if p.get("active")), None)
        
        if active_profile:
            profile_env_suffix = active_profile.get("name", "").upper().replace("-", "_").replace(".", "_")
            profile_env_var = f"AAC_GITHUB_TOKEN_{profile_env_suffix}"
            env_token = os.getenv(profile_env_var)
            
            token = env_token or active_profile.get("git_pat") or active_profile.get("git_token")
            if token and token.startswith("env:"):
                token = os.getenv(token[4:])
                
            if not token:
                token = os.getenv("GITHUB_TOKEN") or os.getenv("GIT_PAT")
                
            if token and not token.startswith("ghp_corporateToken") and not token.startswith("ghp_personalToken"):
                username = active_profile.get("email") or active_profile.get("name") or "git"
                print(f"username={username}")
                print(f"password={token}")
                print()
                sys.exit(0)
                
    elif action in ("store", "erase"):
        for _ in sys.stdin:
            pass
        sys.exit(0)
        
    sys.exit(0)

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
    elif subcmd == "credential-helper":
        handle_credential_helper(args[1:])
    else:
        print_err(f"Unknown subcommand '{subcmd}'. Available: list, switch, add")
        sys.exit(1)
