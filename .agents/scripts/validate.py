import os
import re
import sys

# Reconfigure stdout/stderr to support UTF-8 on Windows cp932/etc. terminals
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


# Inject current directory containing git_api into sys.path
scripts_dir = os.path.dirname(os.path.abspath(__file__))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)
import subprocess
import shutil
import json
import py_compile
from typing import List, Dict, Any, Optional

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

def get_current_branch() -> Optional[str]:
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception:
        return None

def parse_antigravity_ignore() -> List[re.Pattern]:
    """Parse .antigravityignore and compile glob patterns to regex patterns."""
    patterns = []
    ignore_file = ".antigravityignore"
    if os.path.exists(ignore_file):
        try:
            with open(ignore_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    pattern = line
                    if pattern.endswith('/'):
                        pattern = pattern[:-1]
                    escaped = re.escape(pattern).replace(r'\*', '.*')
                    regex_str = f"(^|/){escaped}(/|$)"
                    patterns.append(re.compile(regex_str))
        except Exception as e:
            print_warn(f"Failed to parse .antigravityignore: {e}")
    return patterns

def is_ignored_by_antigravity(path: str, patterns: List[re.Pattern]) -> bool:
    """Check if the given path matches any pattern in .antigravityignore."""
    normalized_path = path.replace('\\', '/')
    for pat in patterns:
        if pat.search(normalized_path):
            return True
    return False

def is_git_ignored(path: str) -> bool:
    """Check if the given path is ignored by Git configuration rules."""
    try:
        res = subprocess.run(
            ['git', 'check-ignore', '-q', path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return res.returncode == 0
    except Exception:
        return False

def validate_json_schema(file_path: str, schema_type: str) -> bool:
    """Validate JSON configuration files against lightweight local schemas."""
    if not os.path.exists(file_path):
        return True # File doesn't exist yet, which is fine for optional configs
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as jde:
        print_err(f"JSON Syntax Error in '{file_path}': {jde}")
        return False
    except Exception as e:
        print_err(f"Failed to read '{file_path}': {e}")
        return False

    if schema_type == "projects":
        if not isinstance(data, dict) or "projects" not in data:
            print_err(f"Schema violation in '{file_path}': root must be a dict containing a 'projects' list.")
            return False
        projects = data["projects"]
        if not isinstance(projects, list):
            print_err(f"Schema violation in '{file_path}': 'projects' key must be a list.")
            return False
        for idx, project in enumerate(projects):
            if not isinstance(project, dict):
                print_err(f"Schema violation in '{file_path}': project at index {idx} must be a dictionary.")
                return False
            for req_key in ("name", "path"):
                if req_key not in project or not isinstance(project[req_key], str) or not project[req_key].strip():
                    print_err(f"Schema violation in '{file_path}' (project index {idx}): key '{req_key}' is required and must be a non-empty string.")
                    return False
            for opt_key in ("stack", "test_command", "lint_command"):
                if opt_key in project and not isinstance(project[opt_key], str):
                    print_err(f"Schema violation in '{file_path}' (project index {idx}): key '{opt_key}' must be a string if defined.")
                    return False

    elif schema_type == "locks":
        if not isinstance(data, dict):
            print_err(f"Schema violation in '{file_path}': locks registry must be a JSON dictionary of module names to branch names.")
            return False
        for mod, branch in data.items():
            if not isinstance(mod, str) or not isinstance(branch, str):
                print_err(f"Schema violation in '{file_path}': lock entry '{mod}' and holder '{branch}' must be strings.")
                return False

    elif schema_type == "git_profiles":
        if not isinstance(data, dict) or "profiles" not in data:
            print_err(f"Schema violation in '{file_path}': root must contain a 'profiles' list.")
            return False
        profiles = data["profiles"]
        if not isinstance(profiles, list):
            print_err(f"Schema violation in '{file_path}': 'profiles' must be a list.")
            return False
        for idx, profile in enumerate(profiles):
            if not isinstance(profile, dict):
                print_err(f"Schema violation in '{file_path}': profile at index {idx} must be a dictionary.")
                return False
            for req_key in ("name", "email"):
                if req_key not in profile or not isinstance(profile[req_key], str) or not profile[req_key].strip():
                    print_err(f"Schema violation in '{file_path}' (profile index {idx}): key '{req_key}' is required and must be a non-empty string.")
                    return False
            if "signing_key" in profile and not isinstance(profile["signing_key"], str):
                print_err(f"Schema violation in '{file_path}' (profile index {idx}): key 'signing_key' must be a string.")
                return False
            if "active" in profile and not isinstance(profile["active"], bool):
                print_err(f"Schema violation in '{file_path}' (profile index {idx}): key 'active' must be a boolean.")
                return False

    return True

# ==========================================================
# 1. Critical Files Audit
# ==========================================================
def audit_critical_files() -> bool:
    print("\n[1/9] Auditing Critical Files...")
    critical_files = [
        "AGENTS.md",
        ".agents/rules.md",
        ".agents/tasks/board.md",
        ".agents/memory/architecture.md"
    ]
    failed = False
    for f in critical_files:
        if not os.path.exists(f):
            print_err(f"Critical file '{f}' is missing from workspace!")
            failed = True
        else:
            print_ok(f"Found '{f}'")
            
    # Run JSON schema audits on optional config files
    if not validate_json_schema(".agents/projects.json", "projects"):
        failed = True
    if not validate_json_schema(".agents/locks.json", "locks"):
        failed = True
    if not validate_json_schema(".agents/git_profiles.json", "git_profiles"):
        failed = True
            
    # Verify and self-heal local Git hooks
    hooks_dir = ".git/hooks"
    if os.path.exists(hooks_dir):
        hooks = {
            "pre-commit": r"""#!/usr/bin/env bash
if command -v python3 &>/dev/null && python3 --version &>/dev/null; then
  python3 .agents/scripts/validate.py
elif command -v python &>/dev/null && python --version &>/dev/null; then
  python .agents/scripts/validate.py
else
  echo "Warning: Python not found. Skipping commit validation check."
fi
""",
            "commit-msg": r"""#!/usr/bin/env bash
COMMIT_MSG_FILE="$1"
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")
CONVENTIONAL_REGEX="^(feat|fix|chore|refactor|docs|test|style|perf|ci)(\([a-z0-9_-]+\))?: .+"

if [[ ! "$COMMIT_MSG" =~ $CONVENTIONAL_REGEX ]]; then
  echo "=========================================================="
  echo "[FAIL] Non-compliant commit message format!"
  echo "=========================================================="
  echo "Commit messages must follow Conventional Commits standard:"
  echo "  Format: <type>(<scope>): <subject>"
  echo "  Example: feat(auth): add login endpoint"
  echo "=========================================================="
  exit 1
fi

ID_REGEX="(task-|issue-|chore-)[a-zA-Z0-9_-]+"
if [[ ! "$COMMIT_MSG" =~ $ID_REGEX ]]; then
  echo "=========================================================="
  echo "[FAIL] Missing Task/Issue ID reference!"
  echo "=========================================================="
  echo "Commit messages must include an active task or issue ID reference."
  echo "  Example body: Task ID: issue-123"
  echo "=========================================================="
  exit 1
fi
""",
            "prepare-commit-msg": r"""#!/usr/bin/env bash
COMMIT_MSG_FILE="$1"
COMMIT_SOURCE="${2:-}"

if command -v python3 &>/dev/null && python3 --version &>/dev/null; then
  python3 .agents/scripts/prepare_commit_msg.py "$COMMIT_MSG_FILE" "$COMMIT_SOURCE"
elif command -v python &>/dev/null && python --version &>/dev/null; then
  python .agents/scripts/prepare_commit_msg.py "$COMMIT_MSG_FILE" "$COMMIT_SOURCE"
fi
"""
        }
        
        for name, content in hooks.items():
            path = os.path.join(hooks_dir, name)
            needs_write = False
            if not os.path.exists(path):
                print_warn(f"Git hook '{name}' is missing.")
                needs_write = True
            else:
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        curr = f.read()
                    if curr.strip().replace("\r\n", "\n") != content.strip().replace("\r\n", "\n"):
                        print_warn(f"Git hook '{name}' content is modified or outdated.")
                        needs_write = True
                except Exception:
                    needs_write = True
            
            if needs_write:
                print(f"Auto-repairing Git hook '{name}'...")
                try:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(content.replace("\r\n", "\n"))
                    if os.name != 'nt':
                        os.chmod(path, 0o755)
                    print_ok(f"Git hook '{name}' repaired successfully.")
                except Exception as e:
                    print_err(f"Failed to auto-repair Git hook '{name}': {e}")
                    failed = True
            else:
                print_ok(f"Git hook '{name}' is active and compliant.")
                
    return not failed

# ==========================================================
# 2. Secret, Staged, and Ignored File Audit
# ==========================================================
def audit_secrets_and_ignored_files() -> bool:
    print("\n[2/9] Auditing for Staged Secrets, Private, and Ignored Files...")
    failed = False
    
    staged_files = []
    is_git = True
    try:
        res = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        staged_files = [line.strip() for line in res.stdout.splitlines() if line.strip()]
    except Exception:
        is_git = False
        # Fallback file scanner excluding common build/dependency files
        antigravity_patterns = parse_antigravity_ignore()
        exclude_dirs = {'.git', 'node_modules', 'venv', 'env', '__pycache__', 'vendor', 'dist', 'build', 'out', '.next'}
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if d not in exclude_dirs
                       and not is_ignored_by_antigravity(os.path.join(root, d), antigravity_patterns)
                       and not is_git_ignored(os.path.join(root, d))]
            for file in files:
                file_path = os.path.join(root, file)
                if not is_ignored_by_antigravity(file_path, antigravity_patterns) and not is_git_ignored(file_path):
                    staged_files.append(file_path)

    # A. Check for ignored files staged in git
    antigravity_patterns = parse_antigravity_ignore()
    for path in staged_files:
        if is_git_ignored(path):
            print_err(f"Ignored file (by .gitignore) is staged for commit: '{path}'!")
            failed = True
        elif is_ignored_by_antigravity(path, antigravity_patterns):
            print_err(f"Ignored file (by .antigravityignore) is staged for commit: '{path}'!")
            failed = True

    # B. Check for forbidden private files
    forbidden_patterns = [
        r"git_profiles\.json$",
        r"locks\.json$",
        r"\.env.*$"
    ]
    for path in staged_files:
        for pattern in forbidden_patterns:
            if re.search(pattern, path):
                print_err(f"Forbidden private file staged for commit: '{path}'!")
                failed = True

    # C. Audit file contents for hardcoded credentials / secrets
    secret_patterns = [
        r"(?i)api_key\s*=\s*['\"][a-zA-Z0-9_\-]{16,}['\"]",
        r"(?i)password\s*=\s*['\"][a-zA-Z0-9_\-]{8,}['\"]",
        r"(?i)private_key\s*=\s*['\"].*['\"]",
        r"-----BEGIN [A-Z ]+ PRIVATE KEY-----"
    ]
    for path in staged_files:
        if not os.path.exists(path) or os.path.isdir(path):
            continue
        if "validate.py" in path:
            continue
        if path.endswith(('.png', '.jpg', '.jpeg', '.ico', '.pdf', '.zip', '.tar.gz')):
            continue
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                for idx, line in enumerate(content.splitlines(), 1):
                    for pattern in secret_patterns:
                        if re.search(pattern, line):
                            print_err(f"Potential secret exposed in file '{path}' at line {idx}: {line.strip()}")
                            failed = True
        except Exception:
            pass
            
    # C2. Scan filesystem for untracked/unignored private or sensitive files
    for root, dirs, files in os.walk('.'):
        exclude_dirs = {'.git', 'node_modules', 'venv', 'env', '__pycache__', 'vendor', 'dist', 'build', 'out', '.next'}
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.startswith('.env') or file == 'git_profiles.json':
                path = os.path.normpath(os.path.join(root, file))
                # Skip if it is correctly ignored by git or antigravity
                if not (is_git_ignored(path) or is_ignored_by_antigravity(path, antigravity_patterns)):
                    print_err(f"Private file '{path}' exists but is NOT ignored in .gitignore or .antigravityignore!")
                    print_err("  Please add it to .gitignore or .antigravityignore immediately to prevent accidental exposure.")
                    failed = True
            
    # D. Check if Git config email matches active profile in git_profiles.json
    profiles_path = ".agents/git_profiles.json"
    if os.path.exists(profiles_path):
        try:
            with open(profiles_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            profiles = data.get("profiles", [])
            
            # Get current git config email and name
            res_email = subprocess.run(
                ['git', 'config', 'user.email'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            res_name = subprocess.run(
                ['git', 'config', 'user.name'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            current_email = res_email.stdout.strip()
            current_name = res_name.stdout.strip()

            # Auto-repair empty Git identity locally
            if not current_email or not current_name:
                print_warn("Git identity (name/email) is not configured locally or globally.")
                active_profile = next((p for p in profiles if p.get("active")), None)
                if not active_profile and profiles:
                    active_profile = profiles[0]
                
                placeholders = {"developer@company.com", "dev.personal@gmail.com"}
                if active_profile and active_profile.get("email") not in placeholders:
                    fallback_email = active_profile.get("email", "developer@antigravity.local")
                    fallback_name = active_profile.get("name", "AAC Developer")
                else:
                    fallback_email = "developer@antigravity.local"
                    fallback_name = "AAC Developer"
                    
                print(f"Auto-repairing Git identity locally using fallback: '{fallback_name}' <{fallback_email}>...")
                subprocess.run(['git', 'config', '--local', 'user.email', fallback_email])
                subprocess.run(['git', 'config', '--local', 'user.name', fallback_name])
                current_email = fallback_email
                current_name = fallback_name
            
            # Find profile matching current git config email
            matching_profile = next((p for p in profiles if p.get("email") == current_email), None)
            
            if matching_profile:
                # If it matches a registered profile but is not active, auto-sync it!
                if not matching_profile.get("active"):
                    for p in profiles:
                        p["active"] = (p.get("email") == current_email)
                    with open(profiles_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2)
                    print_ok(f"Auto-switched active profile in git_profiles.json to '{matching_profile.get('name')}' to match Git config.")
                    matching_profile = next((p for p in profiles if p.get("email") == current_email), None)
                else:
                    print_ok(f"Git Config Email matches active profile '{matching_profile.get('name')}' ({current_email}).")
                
                # Verify SSH key path if present
                ssh_key = matching_profile.get("ssh_key_path") if matching_profile else None
                if ssh_key:
                    ssh_key_abs = os.path.abspath(os.path.expanduser(ssh_key))
                    if not os.path.exists(ssh_key_abs):
                        print_warn(f"SSH private key file not found for profile '{matching_profile.get('name')}': '{ssh_key_abs}'. Commit verification might fail if this key is required.")
                    else:
                        print_ok(f"SSH private key path verified for profile '{matching_profile.get('name')}'.")
                
                # Audit and auto-repair GPG/SSH signing configuration
                res_gpgsign = subprocess.run(
                    ['git', 'config', '--local', 'commit.gpgsign'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                res_signingkey = subprocess.run(
                    ['git', 'config', '--local', 'user.signingkey'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                gpgsign_enabled = res_gpgsign.stdout.strip().lower() == "true"
                local_signingkey = res_signingkey.stdout.strip()
                
                if gpgsign_enabled and local_signingkey:
                    # SSH Key
                    if local_signingkey.startswith("ssh-") or "ssh" in local_signingkey:
                        ssh_key_path = matching_profile.get("ssh_key_path")
                        if ssh_key_path:
                            ssh_key_abs = os.path.abspath(os.path.expanduser(ssh_key_path))
                            if not os.path.exists(ssh_key_abs):
                                print_warn(f"Commit signing is enabled with SSH key, but SSH key file is missing at: '{ssh_key_abs}'.")
                                print("Auto-repairing: Disabling local Git commit signing to prevent commit failures...")
                                subprocess.run(['git', 'config', '--local', 'commit.gpgsign', 'false'])
                                subprocess.run(['git', 'config', '--local', '--unset', 'user.signingkey'])
                                subprocess.run(['git', 'config', '--local', '--unset', 'gpg.format'])
                    # GPG Key
                    else:
                        try:
                            gpg_check = subprocess.run(
                                ['gpg', '--list-secret-keys', '--keyid-format', 'LONG', local_signingkey],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True
                            )
                            if gpg_check.returncode != 0:
                                print_warn(f"Commit signing is enabled with GPG key '{local_signingkey}', but key is missing from local keyring.")
                                print("Auto-repairing: Disabling local Git commit signing to prevent commit failures...")
                                subprocess.run(['git', 'config', '--local', 'commit.gpgsign', 'false'])
                                subprocess.run(['git', 'config', '--local', '--unset', 'user.signingkey'])
                                subprocess.run(['git', 'config', '--local', '--unset', 'gpg.format'])
                            else:
                                print_ok("GPG signing key verified in local keyring.")
                        except FileNotFoundError:
                            print_warn("GnuPG ('gpg') tool is not installed, but GPG signing is enabled.")
                            print("Auto-repairing: Disabling local Git commit signing to prevent commit failures...")
                            subprocess.run(['git', 'config', '--local', 'commit.gpgsign', 'false'])
                            subprocess.run(['git', 'config', '--local', '--unset', 'user.signingkey'])
                            subprocess.run(['git', 'config', '--local', '--unset', 'gpg.format'])
            else:
                # Check if there are any user defined profiles (non-placeholder)
                placeholders = {"developer@company.com", "dev.personal@gmail.com"}
                user_defined = any(p.get("email") not in placeholders for p in profiles if p.get("email"))
                
                if not user_defined:
                    print_ok(f"Using local Git Config Email '{current_email}' (profiles are unconfigured).")
                else:
                    # No registered profile matches current git email -> block!
                    active_profile = next((p for p in profiles if p.get("active")), None)
                    print_err(
                        f"Mismatched Git Email Identity! The email '{current_email}' is not registered in git_profiles.json.\n"
                        f"  Please register the profile first: './helper.sh profile add <name> {current_email}'\n"
                        f"  Or switch to an active profile: './helper.sh profile switch <profile_name>'"
                    )
                    failed = True
        except Exception as e:
            print_warn(f"Failed to audit Git config profile email: {e}")

    if not failed:
        print_ok("No credentials, staged private files, mismatched profiles, or secrets detected.")
    return not failed

# ==========================================================
# 3. Link Integrity Audit
# ==========================================================
def audit_link_integrity() -> bool:
    print("\n[3/9] Auditing File Links inside Memory Registers...")
    link_files = [".agents/memory/architecture.md", ".agents/schema.md"]
    failed = False
    
    for f in link_files:
        if not os.path.exists(f):
            continue
        try:
            with open(f, 'r', encoding='utf-8') as file:
                content = file.read()
                links = re.findall(r'file://([^\s\)]+)', content)
                for link in links:
                    if link.startswith('///'):
                        clean_path = '/' + link[3:]
                    elif link.startswith('//.'):
                        clean_path = link[2:]
                    else:
                        clean_path = link
                    
                    base_path = clean_path.split('#')[0]
                    from urllib.parse import unquote
                    base_path = unquote(base_path)
                    
                    # On Windows, absolute file links might look like /C:/path
                    # We strip the leading slash if followed by a drive letter (e.g., /C:)
                    if len(clean_path) >= 3 and clean_path[0] == '/' and clean_path[2] == ':' and clean_path[1].isalpha():
                        clean_path = clean_path[1:]
                        base_path = base_path[1:]
                    
                    is_absolute = clean_path.startswith('/') or (len(clean_path) >= 2 and clean_path[1] == ':' and clean_path[0].isalpha())
                    if is_absolute:
                        resolved_path = base_path
                    else:
                        resolved_path = os.path.join(os.path.dirname(f), base_path)
                    
                    if resolved_path and not os.path.exists(resolved_path):
                        print_err(f"Broken link in '{f}': linked file '{resolved_path}' does not exist.")
                        failed = True
        except Exception as e:
            print_warn(f"Failed to scan links in '{f}': {e}")
            
    if not failed:
        print_ok("All file-link path integrity checks passed.")
    return not failed

# ==========================================================
# 4. Git Branch & Issue Alignment Audit
# ==========================================================
def audit_git_branch_alignment() -> bool:
    print("\n[4/9] Auditing Git Branch to Local Issue Alignment...")
    branch = get_current_branch()
    if not branch:
        print_warn("Not inside a git repository or git command failed.")
        return True
        
    if branch in ('main', 'master', 'HEAD'):
        # Check if there are staged changes or modified files (excluding untracked git_profiles/locks configs)
        try:
            status_res = subprocess.run(
                ['git', 'status', '--porcelain'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            dirty = False
            for line in status_res.stdout.splitlines():
                if not line.strip():
                    continue
                status = line[:2]
                path = line[3:].strip()
                # Ignore private untracked/ignored configs
                if "git_profiles.json" in path or "locks.json" in path:
                    continue
                if status[0] in ('M', 'A', 'D', 'R', 'C') or status[1] in ('M', 'D'):
                    dirty = True
                    break
            if dirty:
                print_err(f"Direct edits or commits on base branch '{branch}' are prohibited! "
                          f"Please checkout a feature branch (e.g., './helper.sh issue checkout issue-028') before editing.")
                return False
        except Exception as e:
            print_warn(f"Failed to check git status on base branch: {e}")
            
        print_ok(f"On base branch '{branch}' (clean, no active modifications).")
        return True
        
    match = re.search(r'(task-\d+|issue-\d+)', branch.lower())
    if not match:
        print_err(f"Branch name '{branch}' does not contain an issue ID pattern (e.g., 'feat/issue-012' or 'fix/task-001')!")
        return False
        
    issue_id = match.group(1)
    task_board_path = ".agents/tasks/board.md"
    in_board = False
    if os.path.exists(task_board_path):
        with open(task_board_path, 'r', encoding='utf-8') as tb:
            if issue_id in tb.read():
                in_board = True
                
    search_dirs = [".agents/issues", ".agents/archive/issues"]
    file_exists = False
    matched_path = None
    normalized_id = issue_id.replace('-', '_')
    for issue_dir in search_dirs:
        if os.path.exists(issue_dir):
            for f_name in os.listdir(issue_dir):
                if normalized_id in f_name.lower().replace('-', '_') or issue_id in f_name.lower():
                    file_exists = True
                    matched_path = os.path.join(issue_dir, f_name)
                    break
            if file_exists:
                break
                
    if not (file_exists or in_board):
        print_err(f"Branch '{branch}' references issue '{issue_id}', but it is not registered in '{task_board_path}' and no matching issue file exists in '{issue_dir}'!")
        return False
        
    print_ok(f"Branch '{branch}' successfully aligned with registered issue '{issue_id}'.")
    
    if file_exists and matched_path:
        try:
            with open(matched_path, 'r', encoding='utf-8') as f:
                issue_content = f.read()
            # Dynamically import issue command to use its helper
            sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "cli")))
            import commands.issue as issue_cmd
            all_tasks, unchecked = issue_cmd.get_issue_tasks(issue_content)
            
            if unchecked:
                if "--skip-subtasks" in sys.argv or os.getenv("SKIP_SUBTASK_AUDIT") == "true":
                    print_warn(f"Active issue '{issue_id}' has {len(unchecked)} unresolved subtasks (bypassed).")
                else:
                    print_err(f"Active issue '{issue_id}' has {len(unchecked)} unresolved subtasks:")
                    for task in unchecked:
                        print_err(f"  {task.strip()}")
                    return False
            else:
                print_ok(f"All subtasks in issue '{issue_id}' have been resolved.")
        except Exception as e:
            print_warn(f"Failed to parse subtasks in '{matched_path}': {e}")
    # Branch Type Enforcer: verify branch prefix alignment with commit types
    base_branch = 'main'
    try:
        res = subprocess.run(
            ['git', 'show-ref', '--verify', 'refs/heads/master'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if res.returncode == 0:
            base_branch = 'master'
    except Exception:
        pass

    try:
        res = subprocess.run(
            ['git', 'log', f'{base_branch}..HEAD', '--format=%s'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        commits = [c.strip() for c in res.stdout.splitlines() if c.strip()]
    except Exception:
        commits = []

    if commits:
        branch_lower = branch.lower()
        if branch_lower.startswith('feat/'):
            # Only enforce at least one feat commit if the working tree is clean (final validation)
            is_clean = True
            try:
                res_status = subprocess.run(
                    ['git', 'status', '--porcelain'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True
                )
                for line in res_status.stdout.splitlines():
                    if line.strip() and not ("git_profiles.json" in line or "locks.json" in line):
                        is_clean = False
                        break
            except Exception:
                pass
            
            if is_clean:
                has_feat = any(c.lower().startswith('feat:') or c.lower().startswith('feat(') or 'feat!:' in c.lower() for c in commits)
                if not has_feat:
                    print_err(f"Branch prefix is 'feat/', but no 'feat:' commits were found in this branch's history!")
                    print_err("  Feature branches must introduce new features before they can be closed/merged.")
                    return False
        elif branch_lower.startswith('fix/'):
            # Fix branch must never contain a feature commit
            has_feat = any(c.lower().startswith('feat:') or c.lower().startswith('feat(') or 'feat!:' in c.lower() for c in commits)
            if has_feat:
                print_err(f"Branch prefix is 'fix/', but a 'feat:' commit was found in history: '{commits[0]}'")
                print_err("  Fix branches must not introduce new features. Please rename the branch to 'feat/' or change the commit type.")
                return False
        elif branch_lower.startswith('chore/'):
            # Chore branch must never contain a feature or fix commit
            has_feat_or_fix = any(
                c.lower().startswith('feat:') or c.lower().startswith('feat(') or 'feat!:' in c.lower() or
                c.lower().startswith('fix:') or c.lower().startswith('fix(') or 'fix!:' in c.lower()
                for c in commits
            )
            if has_feat_or_fix:
                print_err(f"Branch prefix is 'chore/', but a 'feat:' or 'fix:' commit was found in history: '{commits[0]}'")
                print_err("  Chore branches must only contain chores. Please rename the branch or use appropriate commit types.")
                return False

    return True

# ==========================================================
# 5. Synchronization Check
# ==========================================================
def audit_workspace_sync() -> bool:
    print("\n[5/9] Auditing Workspace Sync Alignment...")
    
    try:
        import sync
        print("Automatically synchronizing skills, ADRs, and rules...")
        sync.sync_skills_to_agents_md()
        sync.sync_adrs_to_architecture_md()
        sync.sync_lessons_to_rules()
    except Exception as e:
        print_warn(f"Auto-synchronization failed: {e}")

    skills_dir = ".agents/skills"
    agents_file = "AGENTS.md"
    failed = False
    if os.path.exists(skills_dir) and os.path.exists(agents_file):
        with open(agents_file, 'r', encoding='utf-8') as af:
            af_content = af.read()
        for skill_name in os.listdir(skills_dir):
            skill_path = os.path.join(skills_dir, skill_name, "SKILL.md")
            if os.path.exists(skill_path):
                if f".agents/skills/{skill_name}/SKILL.md" not in af_content:
                    print_err(f"Skill '{skill_name}' is not registered in '{agents_file}' context map!")
                    failed = True
                    
    if not failed:
        print_ok("Workspace AGENTS.md is in perfect sync with local skills.")
    return not failed

# ==========================================================
# 6. Task Board Schema Compliance Check
# ==========================================================
def audit_task_board_schema() -> bool:
    print("\n[6/9] Auditing Task Board Schema Compliance...")
    task_board = ".agents/tasks/board.md"
    failed = False
    if os.path.exists(task_board):
        try:
            with open(task_board, 'r', encoding='utf-8') as f:
                content = f.read()
            required_sections = ["## Todo", "## Doing", "## Done"]
            for sec in required_sections:
                if sec not in content:
                    print_err(f"Task board '{task_board}' is missing section '{sec}'!")
                    failed = True
            
            task_lines = re.findall(r'([-*]\s*\[[xX /]\].*)', content)
            for line in task_lines:
                if "<!-- id:" not in line:
                    print_warn(f"Task line missing ID tracking comment: '{line.strip()}'")
        except Exception as e:
            print_warn(f"Failed to scan task board schema: {e}")
            
    if not failed:
        print_ok("Task board schema is compliant.")
    return not failed
def get_modified_files() -> List[str]:
    """Retrieve list of modified files in the repository across staged/unstaged changes and diff comparison to base branch."""
    files = []
    
    # 1. Local staged changes
    res_staged = subprocess.run(['git', 'diff', '--cached', '--name-only'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res_staged.returncode == 0:
        files.extend(line.strip() for line in res_staged.stdout.splitlines() if line.strip())
        
    # 2. Local unstaged changes
    res_unstaged = subprocess.run(['git', 'diff', '--name-only'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res_unstaged.returncode == 0:
        files.extend(line.strip() for line in res_unstaged.stdout.splitlines() if line.strip())
        
    # 3. Fallback comparison to base branch if diff is empty (e.g. committed changes on feature branch)
    if not files:
        base_branch = "main"
        res_master = subprocess.run(['git', 'show-ref', 'refs/heads/master'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res_master.returncode == 0:
            base_branch = "master"
            
        res_diff = subprocess.run(['git', 'diff', f'{base_branch}...HEAD', '--name-only'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res_diff.returncode == 0:
            files.extend(line.strip() for line in res_diff.stdout.splitlines() if line.strip())
            
    return list(set(files))

# ==========================================================
# 7. Static Code Linting / Compile Check
# ==========================================================
def run_project_lint_command(project_name: str, project_path: str, lint_command: str) -> bool:
    """Run a custom lint command for a sub-project."""
    print(f"Running custom lint command for sub-project '{project_name}'...")
    import shlex
    cmd_args = shlex.split(lint_command)
    use_shell = False
    if not shutil.which(cmd_args[0]) and os.name != 'nt':
        use_shell = True
        
    resolved_path = os.path.abspath(project_path)
    res = subprocess.run(
        lint_command if use_shell else cmd_args,
        cwd=resolved_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if res.returncode != 0:
        print_err(f"Custom lint command for '{project_name}' failed!\nStdout:\n{res.stdout}\nStderr:\n{res.stderr}")
        return False
    print_ok(f"Custom lint check for '{project_name}' passed.")
    return True

def auto_format_file(file_path: str) -> None:
    """Run auto-formatters (black, prettier, php-cs-fixer) on the file if available."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".py":
        if shutil.which("black"):
            subprocess.run(['black', file_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif shutil.which("yapf"):
            subprocess.run(['yapf', '-i', file_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
    elif ext == ".php":
        if shutil.which("php-cs-fixer"):
            subprocess.run(['php-cs-fixer', 'fix', file_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif shutil.which("phpcbf"):
            subprocess.run(['phpcbf', file_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
    elif ext in (".js", ".jsx", ".ts", ".tsx"):
        prettier_bin = None
        curr_dir = os.path.dirname(os.path.abspath(file_path))
        while curr_dir and curr_dir != os.path.dirname(curr_dir):
            bin_path = os.path.join(curr_dir, "node_modules", ".bin", "prettier")
            if os.path.exists(bin_path):
                prettier_bin = bin_path
                break
            curr_dir = os.path.dirname(curr_dir)
            
        if not prettier_bin:
            prettier_bin = shutil.which("prettier")
            
        if prettier_bin:
            subprocess.run([prettier_bin, '--write', file_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif shutil.which("npx"):
            subprocess.run(['npx', '--no-install', 'prettier', '--write', file_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def auto_lint_file(file_path: str) -> bool:
    """Run default syntax and lint checks based on file extension."""
    auto_format_file(file_path)
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".py":
        try:
            py_compile.compile(file_path, doraise=True)
            if shutil.which("flake8"):
                res = subprocess.run(['flake8', file_path], stdout=subprocess.PIPE, text=True)
                if res.returncode != 0:
                    print_err(f"flake8 violations in '{file_path}':\n{res.stdout}")
                    return False
            return True
        except py_compile.PyCompileError as e:
            print_err(f"Python syntax compilation failed for '{file_path}':\n{e}")
            return False
            
    elif ext == ".php":
        if shutil.which("php"):
            res = subprocess.run(['php', '-l', file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode != 0:
                print_err(f"PHP syntax check failed for '{file_path}':\n{res.stderr or res.stdout}")
                return False
            return True
        return True
        
    elif ext in (".js", ".jsx", ".ts", ".tsx"):
        eslint_bin = None
        curr_dir = os.path.dirname(os.path.abspath(file_path))
        while curr_dir and curr_dir != os.path.dirname(curr_dir):
            bin_path = os.path.join(curr_dir, "node_modules", ".bin", "eslint")
            if os.path.exists(bin_path):
                eslint_bin = bin_path
                break
            curr_dir = os.path.dirname(curr_dir)
            
        if not eslint_bin:
            eslint_bin = shutil.which("eslint")
            
        if eslint_bin:
            res = subprocess.run([eslint_bin, file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode != 0:
                print_err(f"ESLint violations in '{file_path}':\n{res.stdout or res.stderr}")
                return False
        elif shutil.which("npx"):
            res = subprocess.run(['npx', '--no-install', 'eslint', file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode != 0 and "eslint" in (res.stderr or res.stdout).lower():
                print_err(f"ESLint violations in '{file_path}':\n{res.stdout or res.stderr}")
                return False
        return True
        
    return True

def audit_static_linting() -> bool:
    print("\n[7/9] Auditing Static Syntax Compilation...")
    failed = False
    antigravity_patterns = parse_antigravity_ignore()
    modified_files = get_modified_files()
    
    projects = []
    projects_file = ".agents/projects.json"
    if os.path.exists(projects_file):
        try:
            with open(projects_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            projects = data.get("projects", [])
        except Exception:
            pass

    target_files = []
    custom_lint_projects = {}
    
    lockfiles = {
        "requirements.txt", "pipfile", "poetry.lock", "pyproject.toml",
        "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb",
        "composer.json", "composer.lock",
        "go.mod", "go.sum",
        "cargo.toml", "cargo.lock"
    }
    is_lockfile_modified = any(os.path.basename(f).lower() in lockfiles for f in modified_files) if modified_files else False
    
    if modified_files and not is_lockfile_modified:
        for f in modified_files:
            if is_ignored_by_antigravity(f, antigravity_patterns) or not os.path.exists(f):
                continue
                
            matched_project = None
            abs_f = os.path.abspath(f)
            for p in projects:
                p_path = p.get("path")
                if p_path:
                    abs_p_path = os.path.abspath(p_path)
                    if abs_f.startswith(abs_p_path + os.sep) or abs_f == abs_p_path:
                        matched_project = p
                        break
                        
            if matched_project:
                lint_cmd = matched_project.get("lint_command")
                if lint_cmd:
                    custom_lint_projects[matched_project["name"]] = (matched_project["path"], lint_cmd)
                else:
                    target_files.append(f)
            else:
                if f.endswith(".py") and f.startswith(".agents/scripts/"):
                    target_files.append(f)
                    
        if target_files or custom_lint_projects:
            print(f"Incremental validation active. Auditing {len(target_files)} file(s) and {len(custom_lint_projects)} project(s).")
        else:
            print("Incremental validation active. No files requiring lint checks modified. Skipping static check.")
            return True
    else:
        print("No active git modifications detected. Performing baseline audit...")
        scripts_dir = ".agents/scripts"
        if os.path.exists(scripts_dir):
            for root, dirs, files in os.walk(scripts_dir):
                dirs[:] = [d for d in dirs if not is_ignored_by_antigravity(os.path.join(root, d), antigravity_patterns)]
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        if not is_ignored_by_antigravity(file_path, antigravity_patterns):
                            target_files.append(file_path)
                            
        for p in projects:
            lint_cmd = p.get("lint_command")
            if lint_cmd:
                custom_lint_projects[p["name"]] = (p["path"], lint_cmd)

    for name, (path, cmd) in custom_lint_projects.items():
        if not run_project_lint_command(name, path, cmd):
            failed = True
            
    for file_path in target_files:
        if not auto_lint_file(file_path):
            failed = True
            
    if not failed:
        print_ok("Static syntax compilation and style audits passed.")
    return not failed

# ==========================================================
# 8. Local Unit Tests Execution
# ==========================================================
def audit_unit_tests() -> bool:
    print("\n[8/9] Executing Local Unit Tests...")
    if os.getenv("BYPASS_TESTS") == "true":
        print_warn("Bypass flag 'BYPASS_TESTS=true' detected. Skipping unit test execution.")
        return True
        
    modified_files = get_modified_files()
    if modified_files:
        lockfiles = {
            "requirements.txt", "pipfile", "poetry.lock", "pyproject.toml",
            "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb",
            "composer.json", "composer.lock",
            "go.mod", "go.sum",
            "cargo.toml", "cargo.lock"
        }
        # Check if any modified file impacts python execution, test configuration, or dependencies
        affects_tests = False
        for f in modified_files:
            filename = os.path.basename(f).lower()
            if f.endswith(".py") or f.startswith(".agents/tests/") or f == ".agents/projects.json" or f == ".agents/rules.md" or filename in lockfiles:
                affects_tests = True
                break
        
        if not affects_tests:
            print_ok("Incremental validation active. No code or test files modified. Skipping unit tests.")
            return True
            
    failed = False
    
    # 1. Run agent system tests
    test_cmd = None
    if os.path.exists(".agents/tests"):
        if shutil.which("pytest"):
            test_cmd = ["pytest", ".agents/tests"]
        else:
            test_cmd = [sys.executable, "-m", "unittest", "discover", "-s", ".agents/tests"]
            
    if test_cmd:
        print(f"Running agent test suite: {' '.join(test_cmd)}")
        test_res = subprocess.run(test_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if test_res.returncode != 0:
            print_err(f"Agent unit tests failed!\nStdout:\n{test_res.stdout}\nStderr:\n{test_res.stderr}")
            failed = True
        else:
            print_ok("Agent unit tests passed successfully.")
            
    # 2. Run sub-project tests listed in .agents/projects.json
    projects_file = ".agents/projects.json"
    if os.path.exists(projects_file):
        try:
            with open(projects_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            projects = data.get("projects", [])
            tasks = []
            for project in projects:
                name = project.get("name")
                path = project.get("path")
                cmd_str = project.get("test_command")
                if not name or not path or not cmd_str:
                    continue
                
                resolved_path = os.path.abspath(path)
                if not os.path.exists(resolved_path):
                    print_err(f"Sub-project '{name}' path '{path}' does not exist!")
                    failed = True
                    continue
                tasks.append((name, resolved_path, cmd_str))

            if tasks:
                print(f"Executing test suites for {len(tasks)} sub-projects in parallel...")
                from concurrent.futures import ThreadPoolExecutor
                
                def run_single_project_test(task):
                    name, resolved_path, cmd_str = task
                    import shlex
                    cmd_args = shlex.split(cmd_str)
                    use_shell = False
                    if not shutil.which(cmd_args[0]) and os.name != 'nt':
                        use_shell = True
                    try:
                        # Avoid implicit shell execution to prevent command injection.
                        # Explicitly delegate to /bin/sh if shell context is required.
                        if use_shell:
                            run_args = ['/bin/sh', '-c', cmd_str]
                        else:
                            run_args = cmd_args
                        res = subprocess.run(
                            run_args,
                            cwd=resolved_path,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )
                        return (name, res.returncode, res.stdout, res.stderr)
                    except Exception as e:
                        return (name, -1, "", f"Failed to start test execution: {e}")

                with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
                    results = list(executor.map(run_single_project_test, tasks))

                for name, returncode, stdout, stderr in results:
                    if returncode != 0:
                        print_err(f"Sub-project '{name}' tests failed!\nStdout:\n{stdout}\nStderr:\n{stderr}")
                        failed = True
                    else:
                        print_ok(f"Sub-project '{name}' tests passed successfully.")
        except Exception as e:
            print_warn(f"Failed to read or execute sub-project tests: {e}")
            failed = True

    return not failed

# ==========================================================
# 9. Module Lock Compliance Audit
# ==========================================================
def audit_module_locks() -> bool:
    print("\n[9/9] Auditing Module Lock Compliance...")
    branch = get_current_branch()
    if not branch:
        print_warn("Not inside a git repository or git command failed.")
        return True
        
    if branch in ('main', 'master', 'HEAD'):
        print_ok(f"On base branch '{branch}' (skipping lock compliance check).")
        return True

    modified_files = set()
    try:
        res = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        for line in res.stdout.splitlines():
            if line.strip():
                modified_files.add(line.strip())
                
        res_unstaged = subprocess.run(
            ['git', 'diff', '--name-only'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        for line in res_unstaged.stdout.splitlines():
            if line.strip():
                modified_files.add(line.strip())
    except Exception:
        pass

    locks_file = ".agents/locks.json"
    locks = {}
    if os.path.exists(locks_file):
        try:
            with open(locks_file, 'r', encoding='utf-8') as f:
                locks = json.load(f)
        except Exception:
            pass

    failed = False
    for path in sorted(modified_files):
        if path.endswith(('.md', '.json', '.txt', '.sh', '.ps1', '.gitignore', '.antigravityignore', '.example', '.template')):
            continue
        if "tests/" in path or "plans/" in path or "memory/" in path or "docs/" in path:
            continue
            
        base = os.path.basename(path)
        mod_name = os.path.splitext(base)[0]
        
        if mod_name in locks:
            if locks[mod_name] != branch:
                print_err(f"Module '{mod_name}' (file '{path}') is locked by branch '{locks[mod_name]}', but you are editing from '{branch}'!")
                failed = True
            else:
                print_ok(f"Module '{mod_name}' (file '{path}') is correctly locked by this branch.")
        else:
            print_err(f"Module '{mod_name}' (file '{path}') is modified, but no lock is acquired! "
                      f"Please run './helper.sh lock {mod_name}' first.")
            failed = True

    if not failed:
        print_ok("Lock compliance check passed.")
    return not failed

def prune_stale_locks() -> None:
    locks_file = ".agents/locks.json"
    if os.path.exists(locks_file):
        try:
            with open(locks_file, 'r', encoding='utf-8') as f:
                locks = json.load(f)
            
            holders = {holder for holder in locks.values() if holder != "unknown"}
            if not holders:
                return
                
            res = subprocess.run(
                ['git', 'show-ref', '--heads'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            existing_branches = set()
            if res.returncode == 0:
                for line in res.stdout.splitlines():
                    parts = line.strip().split()
                    if len(parts) == 2:
                        ref = parts[1]
                        if ref.startswith('refs/heads/'):
                            existing_branches.add(ref[11:])
            else:
                # If git show-ref --heads fails (e.g. empty repo or error), skip pruning to prevent data loss
                return
                
            modified = False
            for mod, holder in list(locks.items()):
                if holder != "unknown" and holder not in existing_branches:
                    del locks[mod]
                    modified = True
            if modified:
                with open(locks_file, 'w', encoding='utf-8') as f:
                    json.dump(locks, f, indent=2)
                print_ok("Auto-pruned stale module locks in 'locks.json'.")
        except Exception:
            pass


# ==========================================================
# 10. Commit Message Compliance Audit
# ==========================================================
def audit_commit_messages() -> bool:
    print("\n[10/10] Auditing Commit Message Compliance...")
    branch = get_current_branch()
    if not branch or branch in ('main', 'master', 'HEAD'):
        print_ok(f"On base branch '{branch}' (skipping commit message compliance check).")
        return True

    # Detect base branch
    base_branch = 'main'
    try:
        res = subprocess.run(
            ['git', 'show-ref', '--verify', 'refs/heads/master'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if res.returncode == 0:
            base_branch = 'master'
    except Exception:
        pass

    try:
        res = subprocess.run(
            ['git', 'log', f'{base_branch}..HEAD', '--format=%B%x00'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
    except Exception as e:
        print_warn(f"Failed to fetch git log: {e}")
        return True

    commits = [c.strip() for c in res.stdout.split('\x00') if c.strip()]
    if not commits:
        print_ok("No new commits on this branch yet.")
        return True

    import re
    # Conventional commit regex pattern (subject line)
    conv_pattern = re.compile(r'^(feat|fix|chore|refactor|docs|test|style|ci|perf|build|revert)(\(.*\))?!?: .+$', re.IGNORECASE)
    # Refs pattern (anywhere in commit message)
    refs_pattern = re.compile(r'Refs:\s*(issue|task)-\d+', re.IGNORECASE)

    failed = False
    for commit in commits:
        lines = commit.splitlines()
        if not lines:
            continue
        subject = lines[0].strip()
        
        # Skip merge commits
        if subject.startswith("Merge branch") or subject.startswith("Merge pull request") or subject.startswith("Merge "):
            continue

        # Check conventional commit prefix
        if not conv_pattern.match(subject):
            print_err(f"Commit subject does not follow Conventional Commits: '{subject}'")
            print_err("  Expected format: 'feat: description', 'fix: description', etc.")
            failed = True
            continue

        # Check Refs trailer line
        if not refs_pattern.search(commit):
            print_err(f"Commit message is missing 'Refs: <issue-id>' trailer: '{subject}'")
            print_err("  Example: 'Refs: issue-106'")
            failed = True

    if failed:
        return False
        
    print_ok("All commit messages are compliant with Conventional Commits and reference task IDs.")
    return True

# ==========================================================
# Main Execution Entry Point
# ==========================================================
def get_commit_sha() -> str:
    try:
        res = subprocess.run(['git', 'rev-parse', 'HEAD'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return ""

def run_validations() -> None:
    failed = False
    
    print("==========================================================")
    print("   Running AAC V2 Local Validation Guard...              ")
    print("==========================================================")
    
    is_ci = os.getenv("CI") == "true" or os.getenv("GITHUB_ACTIONS") == "true"
    sha = get_commit_sha() if is_ci else ""
    
    if is_ci and sha:
        try:
            import git_api
            git_api.post_commit_status(sha, "pending", description="Running AAC V2 Validation Guard...")
        except Exception:
            pass

    # Auto prune stale locks
    prune_stale_locks()
    

    # Run the 10 audits sequentially
    results = {}
    results["Critical Files"] = audit_critical_files()
    results["Secrets & Ignored Files"] = audit_secrets_and_ignored_files()
    results["Link Integrity"] = audit_link_integrity()
    results["Git Branch Alignment"] = audit_git_branch_alignment()
    results["Workspace Sync"] = audit_workspace_sync()
    results["Task Board Schema"] = audit_task_board_schema()
    results["Static Code Linting"] = audit_static_linting()
    results["Local Unit Tests"] = audit_unit_tests()
    results["Module Lock Compliance"] = audit_module_locks()
    results["Commit Message Compliance"] = audit_commit_messages()
    
    # Print the Colored Audit Summary Table
    print("\n==========================================================")
    print("   AAC V2 Local Validation Summary Checklist              ")
    print("----------------------------------------------------------")
    for key, passed in results.items():
        status_text = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
        print(f"  - {key:<35}: [{status_text}]")
    print("==========================================================")
    
    for passed in results.values():
        if not passed:
            failed = True
            
    if failed:
        print(f"{RED}   Validation FAILED! Please fix the errors above. {RESET}")
        print("==========================================================")
        if is_ci and sha:
            try:
                import git_api
                git_api.post_commit_status(sha, "failure", description="AAC V2 Validation Guard failed.")
            except Exception:
                pass
        sys.exit(1)
    else:
        print(f"{GREEN}   Validation PASSED! Workspace is compliant.      {RESET}")
        print("==========================================================")
        if is_ci and sha:
            try:
                import git_api
                git_api.post_commit_status(sha, "success", description="AAC V2 Validation Guard passed successfully!")
            except Exception:
                pass
        sys.exit(0)

if __name__ == '__main__':
    run_validations()
