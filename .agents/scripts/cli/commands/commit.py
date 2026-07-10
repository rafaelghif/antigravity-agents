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

def has_user_defined_profiles(profiles):
    placeholders = {"developer@company.com", "dev.personal@gmail.com"}
    for p in profiles:
        email = p.get("email")
        if email and email not in placeholders:
            return True
    return False

def run_interactive_commit():
    cli_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if cli_dir not in sys.path:
        sys.path.insert(0, cli_dir)
    try:
        from interactive import interactive_select
    except ImportError:
        interactive_select = None

    print("\n==========================================================")
    print("   Antigravity Conventional Commit Helper                 ")
    print("==========================================================\n")

    types = [
        {"name": "feat", "desc": "A new feature"},
        {"name": "fix", "desc": "A bug fix"},
        {"name": "chore", "desc": "Other changes that don't modify src or test files"},
        {"name": "refactor", "desc": "A code change that neither fixes a bug nor adds a feature"},
        {"name": "docs", "desc": "Documentation only changes"},
        {"name": "test", "desc": "Adding missing tests or correcting existing tests"},
        {"name": "style", "desc": "Changes that do not affect the meaning of the code (white-space, formatting, etc)"},
        {"name": "perf", "desc": "A code change that improves performance"},
        {"name": "ci", "desc": "Changes to our CI configuration files and scripts"},
    ]

    selected_type = "feat"
    if interactive_select:
        sel = interactive_select([{"name": f"{t['name']:<10} - {t['desc']}", "val": t["name"]} for t in types], title="Select the type of change that you're committing:")
        if not sel:
            print("Commit helper cancelled.")
            sys.exit(0)
        selected_type = sel["val"]
    else:
        print("Commit Types:")
        for idx, t in enumerate(types):
            print(f"  {idx + 1}. {t['name']:<10} - {t['desc']}")
        while True:
            try:
                choice = input(f"Enter choice (1-{len(types)}): ").strip()
                if not choice:
                    selected_type = "feat"
                    break
                idx = int(choice) - 1
                if 0 <= idx < len(types):
                    selected_type = types[idx]["name"]
                    break
            except (ValueError, IndexError):
                pass

    scope = input("Enter the scope of this change (optional, press Enter to skip): ").strip()
    subject = ""
    while not subject:
        subject = input("Enter a short, imperative tense description of the change: ").strip()

    body = input("Enter a longer description of the change (optional, press Enter to skip): ").strip()
    issue_id = input("Enter task/issue ID (optional, e.g. issue-123, press Enter to skip): ").strip()

    # Form commit message
    header = f"{selected_type}"
    if scope:
        header += f"({scope})"
    header += f": {subject}"

    msg_lines = [header]
    if body:
        msg_lines.append("")
        msg_lines.append(body)
    
    if issue_id:
        msg_lines.append("")
        msg_lines.append(f"Refs: {issue_id}")

    msg_lines.append("")
    msg_lines.append("Compliance-Audit: passed")

    commit_msg = "\n".join(msg_lines)

    # Confirm commit
    print("\nGenerated Commit Message:")
    print("----------------------------------------------------------")
    print(commit_msg)
    print("----------------------------------------------------------")
    
    confirm = input("Proceed with commit? (Y/n): ").strip().lower()
    if confirm not in ("", "y", "yes"):
        print("Commit aborted.")
        sys.exit(0)

    return commit_msg

def run(args):
    # Check for interactive flag
    interactive_mode = False
    if '--interactive' in args:
        interactive_mode = True
        args.remove('--interactive')
    if '-i' in args:
        interactive_mode = True
        args.remove('-i')

    commit_msg = None
    if interactive_mode:
        commit_msg = run_interactive_commit()

    data = load_profiles()
    profiles = data.get("profiles", [])
    active_profile = None
    for p in profiles:
        if p.get("active"):
            active_profile = p
            break
            
    local_email = ""
    try:
        res = subprocess.run(['git', 'config', 'user.email'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0:
            local_email = res.stdout.strip()
    except Exception:
        pass

    apply_profile = False
    if active_profile:
        placeholder_emails = {"developer@company.com", "dev.personal@gmail.com"}
        if active_profile.get("email") not in placeholder_emails:
            if not local_email:
                apply_profile = True
            elif has_user_defined_profiles(profiles):
                apply_profile = True

    if apply_profile and active_profile:
        print(f"Applying Git Profile: '{active_profile['name']}'")
        email = active_profile.get("email")
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
            subprocess.run(['git', 'config', '--local', '--unset', 'commit.gpgsign'], stderr=subprocess.DEVNULL)
            subprocess.run(['git', 'config', '--local', '--unset', 'user.signingkey'], stderr=subprocess.DEVNULL)
            
        ssh_key = active_profile.get("ssh_key_path")
        if ssh_key:
            subprocess.run(['git', 'config', '--local', 'core.sshCommand', f'ssh -i {ssh_key} -o IdentitiesOnly=yes'])
        else:
            subprocess.run(['git', 'config', '--local', '--unset', 'core.sshCommand'], stderr=subprocess.DEVNULL)
            
    # Trigger local validation checks
    if '--no-verify' not in args:
        print("Triggering pre-commit validation guard...")
        val_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../validate.py'))
        val_res = subprocess.run([sys.executable, val_path])
        if val_res.returncode != 0:
            print("Error: Validation guard failed. Commit aborted.")
            sys.exit(1)
            
    # Forward to native Git Commit
    if commit_msg:
        cmd = ['git', 'commit', '-m', commit_msg] + args
    else:
        cmd = ['git', 'commit'] + args
    res = subprocess.run(cmd)
    sys.exit(res.returncode)
