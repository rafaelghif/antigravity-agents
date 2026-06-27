import sys
import os
import json
import subprocess

PROFILES_FILE = ".agents/git_profiles.json"
PROFILES_EXAMPLE = ".agents/git_profiles.example"

def load_profiles():
    target = PROFILES_FILE if os.path.exists(PROFILES_FILE) else PROFILES_EXAMPLE
    if os.path.exists(target):
        try:
            with open(target, 'r', encoding='utf-8') as f:
                lines = [line for line in f if not line.strip().startswith("#")]
                return json.loads("".join(lines))
        except Exception as e:
            print(f"Warning: Failed to load git profiles from '{target}': {e}")
    return {}

def run(args):
    data = load_profiles()
    profiles = data.get("profiles", [])
    active_profile = None
    for p in profiles:
        if p.get("active"):
            active_profile = p
            break
            
    if active_profile:
        print(f"Applying Git Profile: '{active_profile['name']}'")
        email = active_profile.get("email")
        # Extract default username from name field or email
        name = active_profile.get("name", "Developer")
        if email:
            subprocess.run(['git', 'config', '--local', 'user.email', email])
        if name:
            subprocess.run(['git', 'config', '--local', 'user.name', name])
        signing_key = active_profile.get("signing_key")
        if signing_key and not signing_key.endswith("..."):
            subprocess.run(['git', 'config', '--local', 'user.signingkey', signing_key])
            subprocess.run(['git', 'config', '--local', 'commit.gpgsign', 'true'])
        else:
            # Disable gpg signing if using placeholder/no key to prevent commit blocks
            subprocess.run(['git', 'config', '--local', '--unset', 'commit.gpgsign'], stderr=subprocess.DEVNULL)
            subprocess.run(['git', 'config', '--local', '--unset', 'user.signingkey'], stderr=subprocess.DEVNULL)
            
    # Trigger local validation checks
    if '--no-verify' not in args:
        print("Triggering pre-commit validation guard...")
        val_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../validate.py'))
        val_res = subprocess.run([sys.executable, val_path])
        if val_res.returncode != 0:
            print("Error: Validation guard failed. Commit aborted.")
            sys.exit(1)
            
    # Forward to native Git Commit
    cmd = ['git', 'commit'] + args
    res = subprocess.run(cmd)
    sys.exit(res.returncode)
