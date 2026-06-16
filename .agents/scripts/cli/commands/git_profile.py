import os
import sys
import subprocess
import utils

def run(args):
    # args[0] is 'git-profile'
    if not os.path.isdir('.git'):
        print("Error: Not a Git repository.", file=sys.stderr)
        sys.exit(1)
        
    name = ""
    email = ""
    if len(args) > 1:
        name = args[1]
    if len(args) > 2:
        email = args[2]
        
    profiles_file = ""
    agents_profiles = os.path.join(utils.get_agents_dir(), 'git_profiles')
    home_profiles = os.path.expanduser('~/.git_profiles')
    
    if os.path.exists(agents_profiles):
        profiles_file = agents_profiles
    elif os.path.exists(home_profiles):
        profiles_file = home_profiles
        
    # Read profiles config key-values
    config = {}
    if os.path.exists(profiles_file):
        with open(profiles_file, 'r') as f:
            for line in f:
                if line.strip() and not line.strip().startswith('#') and '=' in line:
                    parts = line.strip().split('=', 1)
                    config[parts[0].strip()] = parts[1].strip()
                    
    is_key_rotate = "rotate.name" in config
    
    if (name == "rotate" or name == "--rotate") and not is_key_rotate:
        if os.path.exists(profiles_file):
            keys = sorted(list(set(k.split('.')[0] for k in config.keys() if k.endswith('.name'))))
            if keys:
                try:
                    last_email = subprocess.check_output(
                        ["git", "log", "-n", "1", "--format=%ae"],
                        stderr=subprocess.DEVNULL
                    ).decode().strip()
                except:
                    last_email = ""
                    
                selected_idx = 0
                for i, k in enumerate(keys):
                    p_e = config.get(f"{k}.email", "")
                    if p_e == last_email:
                        selected_idx = (i + 1) % len(keys)
                        break
                name = keys[selected_idx]
                print(f"Rotating local Git profile to: '{name}'...")
            else:
                print(f"Error: No profiles defined in {profiles_file}.", file=sys.stderr)
                sys.exit(1)
        else:
            print("Error: No Git profiles configuration found to rotate.", file=sys.stderr)
            sys.exit(1)
            
    # Check if name is a profile key
    profile_name_key = f"{name}.name"
    if name and not email and os.path.exists(profiles_file) and profile_name_key in config:
        p_n = config[profile_name_key]
        p_e = config.get(f"{name}.email", "")
        p_s = config.get(f"{name}.ssh_key", "")
        
        print(f"Setting local repository Git configuration to profile '{name}'...")
        subprocess.run(["git", "config", "--local", "user.name", p_n], check=True)
        subprocess.run(["git", "config", "--local", "user.email", p_e], check=True)
        
        if p_s:
            resolved_ssh = os.path.expanduser(p_s)
            if os.path.exists(resolved_ssh):
                subprocess.run(["git", "config", "--local", "core.sshCommand", f"ssh -i \"{p_s}\" -o IdentitiesOnly=yes"], check=True)
            else:
                print(f"  [WARNING] SSH key file at '{p_s}' was not found. Bypassing SSH command setup.", file=sys.stderr)
                subprocess.run(["git", "config", "--local", "--unset", "core.sshCommand"], stderr=subprocess.DEVNULL)
        else:
            subprocess.run(["git", "config", "--local", "--unset", "core.sshCommand"], stderr=subprocess.DEVNULL)
            
        print("  [SUCCESS] Local Git profile updated.")
        name = ""
        email = ""
        
    if name and email:
        print("Setting local repository Git configuration...")
        subprocess.run(["git", "config", "--local", "user.name", name], check=True)
        subprocess.run(["git", "config", "--local", "user.email", email], check=True)
        subprocess.run(["git", "config", "--local", "--unset", "core.sshCommand"], stderr=subprocess.DEVNULL)
        print("  [SUCCESS] Local Git profile updated.")
    elif name or email:
        if os.path.exists(profiles_file):
            print(f"Error: Profile '{name}' not found in {profiles_file}.", file=sys.stderr)
        else:
            print("Error: Both name and email are required to set a profile.", file=sys.stderr)
        sys.exit(1)
        
    # Display configuration
    utils.print_title("Current Git User Configuration")
    
    def get_git_config(scope, key):
        try:
            return subprocess.check_output(["git", "config", f"--{scope}", key], stderr=subprocess.DEVNULL).decode().strip()
        except:
            return "<not set>"
            
    print("Local Profile (This Repository):")
    print(f"  user.name:        {get_git_config('local', 'user.name')}")
    print(f"  user.email:       {get_git_config('local', 'user.email')}")
    print(f"  core.sshCommand:  {get_git_config('local', 'core.sshCommand')}")
    print("")
    print("Global Profile (Default):")
    print(f"  user.name:        {get_git_config('global', 'user.name')}")
    print(f"  user.email:       {get_git_config('global', 'user.email')}")
    print(f"  core.sshCommand:  {get_git_config('global', 'core.sshCommand')}")
    print("")
    
    if os.path.exists(profiles_file):
        print(f"Available Profiles (from {profiles_file}):")
        keys = sorted(list(set(k.split('.')[0] for k in config.keys() if k.endswith('.name'))))
        for k in keys:
            p_n = config[f"{k}.name"]
            p_e = config.get(f"{k}.email", "")
            p_s = config.get(f"{k}.ssh_key", "")
            if p_s:
                print(f"  - {k}: \"{p_n}\" <{p_e}> (ssh_key: {p_s})")
            else:
                print(f"  - {k}: \"{p_n}\" <{p_e}>")
