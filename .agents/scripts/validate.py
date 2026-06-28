import os
import re
import sys

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
                
                if active_profile:
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
                        print_err(f"SSH private key file not found for profile '{matching_profile.get('name')}': '{ssh_key_abs}'")
                        failed = True
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
                
    issue_dir = ".agents/issues"
    file_exists = False
    matched_path = None
    if os.path.exists(issue_dir):
        normalized_id = issue_id.replace('-', '_')
        for f_name in os.listdir(issue_dir):
            if normalized_id in f_name.lower().replace('-', '_') or issue_id in f_name.lower():
                file_exists = True
                matched_path = os.path.join(issue_dir, f_name)
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
            
    return True

# ==========================================================
# 5. Synchronization Check
# ==========================================================
def audit_workspace_sync() -> bool:
    print("\n[5/9] Auditing Workspace Sync Alignment...")
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

# ==========================================================
# 7. Static Code Linting / Compile Check
# ==========================================================
def audit_static_linting() -> bool:
    print("\n[7/9] Auditing Static Syntax Compilation...")
    failed = False
    scripts_dir = ".agents/scripts"
    antigravity_patterns = parse_antigravity_ignore()
    
    if os.path.exists(scripts_dir):
        for root, dirs, files in os.walk(scripts_dir):
            dirs[:] = [d for d in dirs if not is_ignored_by_antigravity(os.path.join(root, d), antigravity_patterns)]
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    if is_ignored_by_antigravity(file_path, antigravity_patterns):
                        continue
                    try:
                        py_compile.compile(file_path, doraise=True)
                    except py_compile.PyCompileError as e:
                        print_err(f"Python syntax compilation failed for '{file_path}':\n{e}")
                        failed = True
                        continue
                        
                    if shutil.which("flake8"):
                        res = subprocess.run(['flake8', file_path], stdout=subprocess.PIPE, text=True)
                        if res.returncode != 0:
                            print_err(f"flake8 style violations found in '{file_path}':\n{res.stdout}")
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
                    
                print(f"Running test suite for sub-project '{name}' in '{path}': {cmd_str}")
                import shlex
                cmd_args = shlex.split(cmd_str)
                
                use_shell = False
                if not shutil.which(cmd_args[0]) and os.name != 'nt':
                    use_shell = True
                
                test_res = subprocess.run(
                    cmd_str if use_shell else cmd_args,
                    cwd=resolved_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    shell=use_shell
                )
                if test_res.returncode != 0:
                    print_err(f"Sub-project '{name}' tests failed!\nStdout:\n{test_res.stdout}\nStderr:\n{test_res.stderr}")
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

    staged_files = []
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
    for path in staged_files:
        if path.endswith(('.md', '.json', '.txt', '.sh', '.ps1', '.gitignore', '.antigravityignore', '.example', '.template')):
            continue
        if "tests/" in path or "plans/" in path or "memory/" in path or "docs/" in path:
            continue
            
        base = os.path.basename(path)
        mod_name = os.path.splitext(base)[0]
        
        if mod_name in locks:
            if locks[mod_name] != branch:
                print_err(f"Module '{mod_name}' (file '{path}') is locked by branch '{locks[mod_name]}', but you are committing from '{branch}'!")
                failed = True
            else:
                print_ok(f"Module '{mod_name}' (file '{path}') is correctly locked by this branch.")
        else:
            print_err(f"Module '{mod_name}' (file '{path}') is staged for commit, but no lock is acquired! "
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
            
            modified = False
            for mod, holder in list(locks.items()):
                if holder != "unknown":
                    res = subprocess.run(
                        ['git', 'show-ref', f'refs/heads/{holder}'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    if res.returncode != 0:
                        del locks[mod]
                        modified = True
            if modified:
                with open(locks_file, 'w', encoding='utf-8') as f:
                    json.dump(locks, f, indent=2)
                print_ok("Auto-pruned stale module locks in 'locks.json'.")
        except Exception:
            pass

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
    
    # Auto sync remote issues
    try:
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "cli")))
        import commands.issue as issue_cmd
        issue_cmd.sync_issues()
    except Exception:
        pass
    
    # Run the 9 audits sequentially
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
