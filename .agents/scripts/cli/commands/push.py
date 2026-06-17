import os
import sys
import subprocess
import utils

def run(args):
    # Parse options
    force = False
    no_validate = False
    
    if len(args) > 1:
        if '--help' in args[1:] or '-h' in args[1:]:
            print("==========================================================")
            print("  Antigravity Helper CLI - git push wrapper")
            print("==========================================================")
            print("Usage: helper.sh push [options]")
            print("")
            print("Options:")
            print("  -f, --force         Force push to remote origin")
            print("  -n, --no-validate   Skip workspace validation and Git profile warnings")
            print("  -h, --help          Show this help message")
            sys.exit(0)
            
        for arg in args[1:]:
            if arg in ('--force', '-f'):
                force = True
            elif arg in ('--no-validate', '-n'):
                no_validate = True

    # 1. Run Workspace Validation
    if not no_validate:
        validate_sh = os.path.join(utils.get_agents_dir(), 'scripts', 'validate.sh')
        if os.path.exists(validate_sh):
            print("Running workspace validation...")
            proc = utils.run_shell_script(validate_sh)
            if proc.returncode != 0:

                print("Error: Workspace validation failed. Push aborted.", file=sys.stderr)
                sys.exit(proc.returncode)
        else:
            print(f"Warning: validate.sh not found at {validate_sh}. Skipping validation.", file=sys.stderr)

    # 2. Check Git user profile mapping
    agents_profiles = os.path.join(utils.get_agents_dir(), 'git_profiles')
    home_profiles = os.path.expanduser('~/.git_profiles')
    
    profiles_file = ""
    if os.path.exists(agents_profiles):
        profiles_file = agents_profiles
    elif os.path.exists(home_profiles):
        profiles_file = home_profiles
        
    config = {}
    if profiles_file:
        try:
            with open(profiles_file, 'r') as f:
                for line in f:
                    if line.strip() and not line.strip().startswith('#') and '=' in line:
                        parts = line.strip().split('=', 1)
                        config[parts[0].strip()] = parts[1].strip()
        except Exception as e:
            print(f"Warning: Failed to read profiles from {profiles_file}: {e}", file=sys.stderr)

    current_email = ""
    try:
        current_email = subprocess.check_output(
            ["git", "config", "user.email"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception as e:
        pass

    matching_profile = None
    ssh_key_path = None

    if config:
        profile_names = sorted(list(set(k.split('.')[0] for k in config.keys() if k.endswith('.name'))))
        for p_name in profile_names:
            p_email = config.get(f"{p_name}.email", "")
            if current_email and p_email == current_email:
                matching_profile = p_name
                p_ssh = config.get(f"{p_name}.ssh_key", "")
                if p_ssh:
                    resolved_ssh = os.path.expanduser(p_ssh)
                    if os.path.exists(resolved_ssh):
                        ssh_key_path = resolved_ssh
                    else:
                        print(f"[WARNING] SSH key file for profile '{p_name}' at '{p_ssh}' was not found.", file=sys.stderr)
                break

    if not no_validate:
        if not profiles_file:
            print("[WARNING] No Git profiles configuration found. Cannot verify user profile alignment.", file=sys.stderr)
        elif not matching_profile:
            print(f"[WARNING] Current Git user email '{current_email}' does not match any profile in {profiles_file}.", file=sys.stderr)
        else:
            print(f"[INFO] Active Git profile matched: '{matching_profile}'")

    # 3. Detect current branch
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], 
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception as e:
        print(f"Error: Failed to resolve current Git branch: {e}", file=sys.stderr)
        sys.exit(1)

    if not branch or branch == "HEAD":
        print("Error: Cannot push in detached HEAD state.", file=sys.stderr)
        sys.exit(1)

    # 4. Prepare and run git push
    cmd = ["git", "push", "origin", branch]
    if force:
        cmd.append("--force")

    env = os.environ.copy()
    if ssh_key_path:
        env["GIT_SSH_COMMAND"] = f"ssh -i \"{ssh_key_path}\" -o IdentitiesOnly=yes"
        print(f"[INFO] Using SSH key rotation: '{ssh_key_path}'")

    print(f"Running: {' '.join(cmd)}")
    proc = subprocess.run(cmd, env=env)
    sys.exit(proc.returncode)
