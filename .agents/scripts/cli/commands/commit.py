import os
import sys
import subprocess
import re
import utils

def run(args):
    no_test_flag = False
    stage_files = []
    commit_type = ""
    scope = ""
    desc = ""
    
    # Parse arguments
    idx = 1
    while idx < len(args):
        arg = args[idx]
        if arg in ("--no-test", "--no-verify"):
            no_test_flag = True
            idx += 1
        elif arg == "commit":
            idx += 1
        elif not commit_type:
            commit_type = arg
            idx += 1
        elif not scope:
            scope = arg
            idx += 1
        elif not desc:
            desc = arg
            idx += 1
        else:
            stage_files.append(arg)
            idx += 1
            
    # Interactive inputs
    if not commit_type:
        print("Choose commit type:")
        print("  [1] feat:     A new feature")
        print("  [2] fix:      A bug fix")
        print("  [3] refactor: A code change that neither fixes a bug nor adds a feature")
        print("  [4] chore:    Changes to the build process or auxiliary tools and libraries")
        print("  [5] docs:     Documentation only changes")
        print("  [6] test:     Adding missing tests or correcting existing tests")
        print("  [7] perf:     A code change that improves performance")
        try:
            type_choice = input("Select number or type string (default: feat): ").strip()
        except KeyboardInterrupt:
            print("\nCancelled.")
            sys.exit(1)
            
        mapping = {
            "1": "feat", "2": "fix", "3": "refactor", "4": "chore",
            "5": "docs", "6": "test", "7": "perf", "": "feat"
        }
        commit_type = mapping.get(type_choice, type_choice)
        
    if not scope:
        try:
            scope = input("Enter commit scope (e.g. core, auth, db, shared) (default: core): ").strip()
        except KeyboardInterrupt:
            print("\nCancelled.")
            sys.exit(1)
        if not scope:
            scope = "core"
            
    if not desc:
        try:
            desc = input("Enter brief description of change: ").strip()
        except KeyboardInterrupt:
            print("\nCancelled.")
            sys.exit(1)
        if not desc:
            print("Error: Description cannot be empty.", file=sys.stderr)
            sys.exit(1)
            
    # Workspace Validation
    print("Running workspace validation checks...")
    validate_sh = os.path.join(utils.get_agents_dir(), "scripts", "validate.sh")
    if os.path.exists(validate_sh):
        proc = utils.run_shell_script(validate_sh)
        if proc.returncode != 0:
            print("Error: Workspace validation failed. Aborting commit.", file=sys.stderr)
            sys.exit(1)
            
    # Linter and Test commands from project_rules.md
    linter_cmd = ""
    test_runner = ""
    rules_file = os.path.join(utils.get_agents_dir(), "rules", "project_rules.md")
    if os.path.exists(rules_file):
        try:
            with open(rules_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if "Linter command" in line:
                        m = re.search(r"`([^`]+)`", line)
                        if m: linter_cmd = m.group(1)
                    elif "Test runner command" in line:
                        m = re.search(r"`([^`]+)`", line)
                        if m: test_runner = m.group(1)
        except Exception as e:
            print(f"Warning: Failed to read project rules for lint/test commands: {e}", file=sys.stderr)
            
    if os.name == 'nt':
        python3_works = False
        try:
            if subprocess.run("python3 --version", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
                python3_works = True
        except:
            pass
        if not python3_works:
            if linter_cmd.startswith("python3 "):
                linter_cmd = linter_cmd.replace("python3 ", "python ", 1)
            elif linter_cmd == "python3":
                linter_cmd = "python"
            if test_runner.startswith("python3 "):
                test_runner = test_runner.replace("python3 ", "python ", 1)
            elif test_runner == "python3":
                test_runner = "python"
                
    if not no_test_flag:
        if linter_cmd and linter_cmd != "echo 'No linter found'":
            print(f"Running linter command: {linter_cmd}...")
            proc = subprocess.run(linter_cmd, shell=True)
            if proc.returncode != 0:
                print("Error: Linter check failed. Aborting commit.", file=sys.stderr)
                sys.exit(1)
            print("  [PASS] Linter check passed successfully.")
            
        if test_runner and test_runner != "echo 'No test suite found'":
            print(f"Running test suite: {test_runner}...")
            proc = subprocess.run(test_runner, shell=True)
            if proc.returncode != 0:
                print("Error: Test runner suite failed. Aborting commit.", file=sys.stderr)
                sys.exit(1)
            print("  [PASS] All tests passed successfully.")
    else:
        print("Linter and Test checks bypassed via --no-test / --no-verify.")
        
    # File Staging
    if stage_files:
        print(f"Staging specified files: {' '.join(stage_files)}...")
        subprocess.run(["git", "add"] + stage_files)
    else:
        print("Staging all modified and untracked files...")
        status = subprocess.check_output(["git", "status", "--porcelain"]).decode()
        # filter out lock files
        has_changes = False
        for line in status.splitlines():
            if not line.strip().endswith(".lock") or ".agents/locks/" not in line:
                has_changes = True
                break
        if has_changes:
            subprocess.run(["git", "add", "-A", "--", ":!.agents/locks/*"])
            
    # Auto-rotate profiles
    profiles_file = ""
    local_pf = os.path.join(utils.get_agents_dir(), "git_profiles")
    home_pf = os.path.expanduser("~/.git_profiles")
    if os.path.exists(local_pf):
        profiles_file = local_pf
    elif os.path.exists(home_pf):
        profiles_file = home_pf
        
    if profiles_file:
        profiles = {}
        try:
            with open(profiles_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line_strip = line.strip()
                    m = re.match(r"^([a-zA-Z0-9_\-]+)\.(name|email|ssh_key)\s*=\s*(.+)$", line_strip)
                    if m:
                        prof_key = m.group(1)
                        field = m.group(2)
                        val = m.group(3).strip('\'"')
                        profiles.setdefault(prof_key, {})[field] = val
        except Exception as e:
            print(f"Warning: Failed to parse Git profiles: {e}", file=sys.stderr)
            
        profile_keys = sorted(list(profiles.keys()))
        if profile_keys:
            try:
                last_email = subprocess.check_output(
                    ["git", "log", "-n", 1, "--format=%ae"], 
                    stderr=subprocess.DEVNULL
                ).decode().strip()
            except:
                last_email = ""
                
            selected_idx = 0
            for i, pk in enumerate(profile_keys):
                if profiles[pk].get("email") == last_email:
                    selected_idx = (i + 1) % len(profile_keys)
                    break
                    
            selected_profile = profile_keys[selected_idx]
            p_name = profiles[selected_profile].get("name")
            p_email = profiles[selected_profile].get("email")
            p_ssh = profiles[selected_profile].get("ssh_key", "")
            
            if not p_name or not p_email:
                print(f"Error: Profile '{selected_profile}' is misconfigured in {profiles_file}.", file=sys.stderr)
                sys.exit(1)
                
            print(f"Auto-selecting Git profile: '{selected_profile}' (\"{p_name}\" <{p_email}>) for round-robin commit rotation.")
            subprocess.run(["git", "config", "--local", "user.name", p_name])
            subprocess.run(["git", "config", "--local", "user.email", p_email])
            
            if p_ssh:
                p_ssh_expanded = os.path.expanduser(p_ssh)
                if os.path.exists(p_ssh_expanded):
                    print(f"Auto-selecting SSH key: '{p_ssh}' for profile '{selected_profile}'.")
                    subprocess.run(["git", "config", "--local", "core.sshCommand", f"ssh -i \"{p_ssh_expanded}\" -o IdentitiesOnly=yes"])
                else:
                    print(f"Warning: SSH key file at '{p_ssh}' specified for profile '{selected_profile}' does not exist. Bypassing SSH setup.", file=sys.stderr)
                    subprocess.run(["git", "config", "--local", "--unset", "core.sshCommand"])
            else:
                subprocess.run(["git", "config", "--local", "--unset", "core.sshCommand"])
        else:
            print(f"Error: Git profiles file found at {profiles_file} but no valid profiles were parsed.", file=sys.stderr)
            sys.exit(1)
    else:
        # Fallbacks
        try:
            active_name = subprocess.check_output(["git", "config", "user.name"]).decode().strip()
        except:
            active_name = ""
        try:
            active_email = subprocess.check_output(["git", "config", "user.email"]).decode().strip()
        except:
            active_email = ""
            
        if not active_name or not active_email:
            print("Warning: No Git profiles config found (.agents/git_profiles) and no default Git identity (user.name/user.email) is configured.", file=sys.stderr)
            print("  [FALLBACK] Configuring temporary local-only identity: \"Local Developer\" <local-dev@localhost>", file=sys.stderr)
            subprocess.run(["git", "config", "--local", "user.name", "Local Developer"])
            subprocess.run(["git", "config", "--local", "user.email", "local-dev@localhost"])
            subprocess.run(["git", "config", "--local", "--unset", "core.sshCommand"])
        else:
            if re.match(r"^[a-zA-Z0-9_\.-]+@(company\.com|gmail\.com|example\.com)$", active_email) and re.match(r"^(Developer|Test|Alice|Bob).*", active_name):
                print("Warning: Active Git configuration appears to be using a template or placeholder:", file=sys.stderr)
                print(f"  Name:  {active_name}", file=sys.stderr)
                print(f"  Email: {active_email}", file=sys.stderr)
                print("  Please update your credentials or set up '.agents/git_profiles' for enterprise-grade compliance.", file=sys.stderr)
            print(f"[INFO] Auto-rotation bypassed (no profiles config). Using active Git identity: \"{active_name}\" <{active_email}>")

    # Conventional Commit
    commit_msg = f"{commit_type}({scope}): {desc}"
    print(f"Executing conventional commit: '{commit_msg}'...")
    env = os.environ.copy()
    env["AAC_COMMIT_RUNNING"] = "1"
    proc = subprocess.run(["git", "commit", "-m", commit_msg], env=env)
    if proc.returncode == 0:
        print("Commit successful.")
        
        # Check for issue auto-closing in commit message
        closed_issues = re.findall(r"\b(?:fixes|closes|resolves)\s+#([0-9]+)\b", desc, re.IGNORECASE)
        if closed_issues:
            try:
                import importlib
                issue_mod = importlib.import_module("commands.issue")
                staged_any = False
                for issue_id_str in closed_issues:
                    print(f"Commit message matches auto-close pattern for issue #{issue_id_str}. Auto-closing issue...")
                    try:
                        issue_mod.close_issue(issue_id_str)
                        issues_dir = issue_mod.get_issues_dir()
                        filename = f"issue_{int(issue_id_str):03d}.md"
                        file_path = os.path.join(issues_dir, filename)
                        if os.path.exists(file_path):
                            subprocess.run(["git", "add", file_path])
                            staged_any = True
                    except SystemExit:
                        print(f"Warning: Could not auto-close issue #{issue_id_str} (does not exist or invalid ID).", file=sys.stderr)
                
                if staged_any:
                    print("Amending commit to include auto-closed issue files...")
                    subprocess.run(["git", "commit", "--amend", "--no-edit", "--no-verify"], env=env)
                    print("Commit amended successfully.")
            except Exception as e:
                print(f"Warning: Failed to auto-close issues: {e}", file=sys.stderr)
    else:
        print("Error: Git commit failed.", file=sys.stderr)
        sys.exit(1)
