import os
import re
import sys
import tempfile
import builtins
import threading
from concurrent.futures import ThreadPoolExecutor

print_lock = threading.Lock()
_original_print = builtins.print

def locked_print(*args, **kwargs):
    with print_lock:
        _original_print(*args, **kwargs)

builtins.print = locked_print

class SandboxManager:
    """
    Manages an isolated Python virtualenv sandbox environment for safe command execution.
    By using --system-site-packages, we inherit installed packages instantly without pip delay.
    """
    def __init__(self, enabled: bool = True):
        if os.environ.get("AAC_DISABLE_SANDBOX", "0").lower() in ("1", "true"):
            enabled = False
        self.enabled = enabled
        self.temp_dir = None
        self.venv_dir = None
        self.old_cwd = None
        self.old_path = None
        
    def __enter__(self):
        if not self.enabled:
            return self
            
        try:
            self.temp_dir = tempfile.mkdtemp(prefix="aac_sandbox_")
            self.venv_dir = os.path.join(self.temp_dir, "venv")
            
            import venv
            # Create venv with system site packages to avoid reinstalling dependencies
            venv.create(self.venv_dir, system_site_packages=True, with_pip=False)
            
            self.old_cwd = os.getcwd()
            
            # Copy codebase files to sandbox directory (exclude massive dependency folders)
            for item in os.listdir(self.old_cwd):
                if item in ('.git', '.lock', 'venv', 'node_modules', '.venv', 'build', 'dist', 'tmp'):
                    continue
                src = os.path.join(self.old_cwd, item)
                dst = os.path.join(self.temp_dir, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst, symlinks=True, ignore=shutil.ignore_patterns('.git', '.lock'))
                else:
                    shutil.copy2(src, dst)
                    
            # If Git variables exist, convert them to absolute paths BEFORE changing directory
            for env_var in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY"):
                if env_var in os.environ:
                    os.environ[env_var] = os.path.abspath(os.environ[env_var])

            os.chdir(self.temp_dir)
            
            # Setup Git repository references so git commands resolve cleanly inside the sandbox
            # By pointing GIT_WORK_TREE to old_cwd, git operations refer to the host filesystem index,
            # avoiding stat cache mismatches or modification flags on sandbox file copies.
            if "GIT_DIR" not in os.environ:
                os.environ["GIT_DIR"] = os.path.abspath(os.path.join(self.old_cwd, ".git"))
            if "GIT_WORK_TREE" not in os.environ:
                os.environ["GIT_WORK_TREE"] = self.old_cwd
            
            self.old_path = os.environ.get("PATH", "")
            venv_bin = os.path.join(self.venv_dir, "bin")
            os.environ["PATH"] = venv_bin + os.pathsep + self.old_path
            os.environ["VIRTUAL_ENV"] = self.venv_dir
            
        except Exception as e:
            # Avoid thread-lock re-entrancy warnings in fail scenarios
            _original_print(f"\033[93m[WARN] Failed to initialize sandbox environment: {e}. Falling back to host execution.\033[0m")
            self.enabled = False
            
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.enabled:
            return
            
        try:
            if self.old_cwd:
                os.chdir(self.old_cwd)
            if self.old_path is not None:
                os.environ["PATH"] = self.old_path
            if "VIRTUAL_ENV" in os.environ:
                del os.environ["VIRTUAL_ENV"]
            if "GIT_DIR" in os.environ:
                del os.environ["GIT_DIR"]
            if "GIT_WORK_TREE" in os.environ:
                del os.environ["GIT_WORK_TREE"]
                
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            pass

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

_base_branch_cache = None

def get_base_branch() -> str:
    """Retrieve the base branch name, caching the result to avoid redundant Git calls."""
    global _base_branch_cache
    if _base_branch_cache is None:
        _base_branch_cache = 'main'
        try:
            res = subprocess.run(
                ['git', 'show-ref', 'refs/heads/master'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if res.returncode == 0:
                _base_branch_cache = 'master'
        except Exception:
            pass
    return _base_branch_cache

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
            
    # Parse version from AGENTS.md
    agents_version = None
    if os.path.exists("AGENTS.md"):
        try:
            with open("AGENTS.md", "r", encoding="utf-8") as f_ref:
                m = re.search(r"-\s+\*\*Version:\*\*\s*([0-9\.]+)", f_ref.read())
                if m:
                    agents_version = m.group(1)
        except Exception:
            pass

    # Validate version matching in shell/powershell bootstrap files if they exist in root
    if agents_version:
        env_files = ["bootstrap.sh", "bootstrap.ps1"]
        for env_file in env_files:
            if os.path.exists(env_file):
                try:
                    with open(env_file, "r", encoding="utf-8") as f_ref:
                        content = f_ref.read()
                    if agents_version not in content:
                        print_err(f"Version mismatch: '{env_file}' version does not match version '{agents_version}' in AGENTS.md!")
                        failed = True
                    else:
                        print_ok(f"Verified version sync in '{env_file}' (matches '{agents_version}').")
                except Exception as e:
                    print_warn(f"Failed to read '{env_file}' for version check: {e}")

    # Run JSON schema audits on optional config files
    if not validate_json_schema(".agents/projects.json", "projects"):
        failed = True
    if not validate_json_schema(".agents/state/locks.json", "locks"):
        failed = True
    if not validate_json_schema(".agents/git_profiles.json", "git_profiles"):
        failed = True
            
    # Verify and self-heal local Git hooks
    git_dir = os.environ.get("GIT_DIR")
    if git_dir and os.path.exists(git_dir):
        hooks_dir = os.path.join(git_dir, "hooks")
    else:
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

if [[ "$COMMIT_MSG" =~ ^Merge[[:space:]] || "$COMMIT_MSG" =~ ^chore\(git\):[[:space:]]merge[[:space:]]branch || "$COMMIT_MSG" =~ ^chore\(release\): ]]; then
  exit 0
fi

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

COMPLIANCE_REGEX="Compliance-Audit:[[:space:]]*passed"
if [[ ! "$COMMIT_MSG" =~ $COMPLIANCE_REGEX ]]; then
  echo "=========================================================="
  echo "[FAIL] Missing Compliance-Audit: passed reference!"
  echo "=========================================================="
  echo "Commit messages must include 'Compliance-Audit: passed' to verify compliance."
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
            ['git', 'diff', '--cached', '--name-status'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        for line in res.stdout.splitlines():
            if line.strip():
                parts = line.strip().split(None, 1)
                if len(parts) == 2:
                    status, path = parts
                    if status.strip() != 'D':
                        staged_files.append(path.strip())
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
    link_files = ["AGENTS.md", ".agents/rules.md", ".agents/schema.md", ".agents/memory/architecture.md"]
    
    # Dynamically scan issues and memory folders
    for folder in (".agents/issues", ".agents/memory"):
        if os.path.exists(folder):
            for f in os.listdir(folder):
                if f.endswith(".md"):
                    link_files.append(os.path.join(folder, f))
                    
    failed = False
    
    for f in link_files:
        if not os.path.exists(f):
            continue
        try:
            with open(f, 'r', encoding='utf-8') as file:
                content = file.read()
                
                # 1. Match file:// links
                file_links = re.findall(r'file://([^\s\)]+)', content)
                # 2. Match standard relative/local markdown links [text](path)
                # Ignore remote URLs (containing ':') and section anchors starting with '#'
                md_links = re.findall(r'\[[^\]]*\]\(([^:\s\)]+)\)', content)
                
                all_links = []
                for link in file_links:
                    all_links.append((link, True))
                for link in md_links:
                    if not link.startswith('#') and not link.startswith('mailto:'):
                        all_links.append((link, False))
                
                for link, is_proto in all_links:
                    if is_proto:
                        if link.startswith('///'):
                            clean_path = '/' + link[3:]
                        elif link.startswith('//.'):
                            clean_path = link[2:]
                        else:
                            clean_path = link
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
                    elif resolved_path and os.path.exists(resolved_path):
                        # Verify anchor line range if specified (e.g. #L10-L20)
                        anchor = clean_path.split('#')[1] if '#' in clean_path else None
                        if anchor and anchor.startswith('L'):
                            line_part = anchor[1:]
                            try:
                                if '-' in line_part:
                                    parts = line_part.split('-')
                                    start_line = int(parts[0].lstrip('L'))
                                    end_line = int(parts[1].lstrip('L'))
                                else:
                                    start_line = end_line = int(line_part)
                                
                                with open(resolved_path, 'r', encoding='utf-8', errors='ignore') as ref_file:
                                    lines_count = sum(1 for _ in ref_file)
                                if end_line > lines_count:
                                    print_err(f"Broken anchor range in '{f}': linked path '{resolved_path}#{anchor}' points to line {end_line}, but file only has {lines_count} lines.")
                                    failed = True
                            except ValueError:
                                pass
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
                if "git_profiles.json" in path or "locks.json" in path or ".agents/state/" in path or ".agents/issues/" in path:
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
            
            # Contributor identity alignment check
            fm = issue_cmd.parse_issue_frontmatter(issue_content)
            assignee = fm.get("assignee")
            if assignee:
                profiles_file = ".agents/git_profiles.json"
                if os.path.exists(profiles_file):
                    try:
                        with open(profiles_file, 'r', encoding='utf-8') as pf:
                            lines = [line for line in pf if not line.strip().startswith("#")]
                            data = json.loads("".join(lines))
                            profiles = data.get("profiles", [])
                            matching_profile = next((p for p in profiles if p.get("name") == assignee), None)
                            if matching_profile:
                                expected_email = matching_profile.get("email")
                                res_email = subprocess.run(['git', 'config', 'user.email'], stdout=subprocess.PIPE, text=True)
                                current_email = res_email.stdout.strip()
                                if current_email != expected_email:
                                    print_err(f"Branch contributor identity mismatch! Issue is assigned to '{assignee}' "
                                              f"with email '{expected_email}', but current Git Config email is '{current_email}'.")
                                    print_err(f"Please switch to profile '{assignee}' using: './helper.sh profile switch {assignee}'")
                                    return False
                                else:
                                    print_ok(f"Branch contributor identity aligns with assignee '{assignee}' ({expected_email}).")
                            else:
                                print_warn(f"Issue assignee '{assignee}' is not registered in git_profiles.json.")
                    except Exception as e:
                        print_warn(f"Failed to verify contributor identity alignment: {e}")

            all_tasks, unchecked = issue_cmd.get_issue_tasks(issue_content)
            required_unchecked = [t for t in unchecked if not any(opt in t.lower() for opt in ('(optional)', '[optional]'))]
            
            if required_unchecked:
                if os.environ.get("AAC_ENFORCE_SUBTASKS") != "true" and "--enforce-subtasks" not in sys.argv:
                    print_warn(f"Active issue '{issue_id}' has {len(required_unchecked)} unresolved required subtasks (warning: intermediate commit).")
                elif "--skip-subtasks" in sys.argv or os.getenv("SKIP_SUBTASK_AUDIT") == "true":
                    print_warn(f"Active issue '{issue_id}' has {len(required_unchecked)} unresolved required subtasks (bypassed).")
                elif sys.stdin.isatty() and os.getenv("ANTIGRAVITY_AGENT") != "1" and os.getenv("ANTIGRAVITY_NONINTERACTIVE") != "1" and os.getenv("CI") != "true" and os.environ.get("IN_AUDIT_TEST") != "true" and 'unittest' not in sys.modules and 'pytest' not in sys.modules:
                    print_warn(f"Active issue '{issue_id}' has {len(required_unchecked)} unresolved required subtasks:")
                    for task in required_unchecked:
                        print_warn(f"  {task.strip()}")
                    try:
                        print(f"{YELLOW}Active issue has unresolved required subtasks. Continue anyway? (y/N): {RESET}", end="", flush=True)
                        ans = sys.stdin.readline().strip().lower()
                        if ans in ('y', 'yes'):
                            print_warn("Unresolved required subtask check bypassed by user choice.")
                        else:
                            return False
                    except Exception:
                        return False
                else:
                    print_err(f"Active issue '{issue_id}' has {len(required_unchecked)} unresolved required subtasks:")
                    for task in required_unchecked:
                        print_err(f"  {task.strip()}")
                    return False
            else:
                if unchecked:
                    print_ok(f"All required subtasks in issue '{issue_id}' resolved. (Skipped {len(unchecked)} optional tasks).")
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
                    if line.strip() and not ("git_profiles.json" in line or "locks.json" in line or ".agents/state/" in line or ".agents/issues/" in line):
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
def audit_issue_files_schema() -> bool:
    failed = False
    issues_dir = ".agents/issues"
    if not os.path.exists(issues_dir):
        return True
        
    for f_name in os.listdir(issues_dir):
        if not f_name.endswith(".md"):
            continue
        path = os.path.join(issues_dir, f_name)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 1. Check YAML frontmatter existence
            if not content.startswith("---"):
                print_err(f"Issue file '{f_name}' is missing frontmatter start marker '---'!")
                failed = True
                continue
                
            parts = content.split("---", 2)
            if len(parts) < 3:
                print_err(f"Issue file '{f_name}' has malformed frontmatter block (unclosed '---')!")
                failed = True
                continue
                
            frontmatter = parts[1]
            # Validate required metadata fields
            required_fields = ["id:", "title:", "status:", "assignee:", "created_at:"]
            for field in required_fields:
                if field not in frontmatter.lower():
                    print_err(f"Issue file '{f_name}' frontmatter is missing required metadata field '{field[:-1]}'!")
                    failed = True
                    
            body = parts[2]
            # 2. Check required sections
            required_sections = ["## Tasks", "## Acceptance Criteria", "## Rule & Schema Compliance Audit"]
            for sec in required_sections:
                if sec not in body:
                    print_err(f"Issue file '{f_name}' is missing required body section '{sec}'!")
                    failed = True
                    
            # 3. Check that all tasks have tracking IDs
            tasks_match = re.search(r'## Tasks\s*\n(.*?)(?=\n## Acceptance Criteria|$)', body, re.DOTALL)
            if tasks_match:
                tasks_body = tasks_match.group(1)
                sub_task_lines = re.findall(r'([-*]\s*\[[xX /]\].*)', tasks_body)
                for tl in sub_task_lines:
                    if "<!-- id:" not in tl:
                        print_warn(f"Issue file '{f_name}' task line is missing tracking ID: '{tl.strip()}'")
                            
        except Exception as e:
            print_warn(f"Failed to scan issue file schema for '{f_name}': {e}")
            
    return not failed

def audit_task_board_schema() -> bool:
    print("\n[6/9] Auditing Task Board Schema Compliance...")
    task_board = ".agents/tasks/board.md"
    failed = False
    
    # Run issue files schema validation
    if not audit_issue_files_schema():
        failed = True
        
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
        base_branch = get_base_branch()
            
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
    """Run auto-formatters (black, prettier, php-cs-fixer, gofmt, rustfmt, clang-format, rubocop) on the file if available."""
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
            
    elif ext == ".go":
        if shutil.which("gofmt"):
            subprocess.run(['gofmt', '-w', file_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    elif ext == ".rs":
        if shutil.which("rustfmt"):
            subprocess.run(['rustfmt', file_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    elif ext == ".rb":
        if shutil.which("rubocop"):
            subprocess.run(['rubocop', '-A', file_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    elif ext in (".c", ".cpp", ".h", ".hpp"):
        if shutil.which("clang-format"):
            subprocess.run(['clang-format', '-i', file_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    elif ext in (".js", ".jsx", ".ts", ".tsx", ".html", ".css", ".scss", ".json", ".yaml", ".yml"):
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
            if shutil.which("mypy"):
                res_mypy = subprocess.run(['mypy', '--ignore-missing-imports', file_path], stdout=subprocess.PIPE, text=True)
                if res_mypy.returncode != 0:
                    print_err(f"mypy type-checking violations in '{file_path}':\n{res_mypy.stdout}")
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
        
    elif ext == ".go":
        if shutil.which("golangci-lint"):
            res = subprocess.run(['golangci-lint', 'run', file_path], stdout=subprocess.PIPE, text=True)
            if res.returncode != 0:
                print_err(f"golangci-lint violations in '{file_path}':\n{res.stdout}")
                return False
        elif shutil.which("go"):
            res = subprocess.run(['go', 'vet', file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode != 0:
                print_err(f"go vet violations in '{file_path}':\n{res.stderr or res.stdout}")
                return False
        return True

    elif ext == ".rs":
        if shutil.which("rustc"):
            res = subprocess.run(['rustc', '-Z', 'no-codegen', file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode != 0:
                print_err(f"rustc compilation syntax check failed for '{file_path}':\n{res.stderr or res.stdout}")
                return False
        return True

    elif ext == ".rb":
        if shutil.which("rubocop"):
            res = subprocess.run(['rubocop', file_path], stdout=subprocess.PIPE, text=True)
            if res.returncode != 0:
                print_err(f"rubocop violations in '{file_path}':\n{res.stdout}")
                return False
        elif shutil.which("ruby"):
            res = subprocess.run(['ruby', '-c', file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode != 0:
                print_err(f"Ruby syntax check failed for '{file_path}':\n{res.stderr or res.stdout}")
                return False
        return True

    elif ext in (".sh", ".bash"):
        if shutil.which("shellcheck"):
            res = subprocess.run(['shellcheck', file_path], stdout=subprocess.PIPE, text=True)
            if res.returncode != 0:
                print_err(f"shellcheck violations in '{file_path}':\n{res.stdout}")
                return False
        return True

    elif ext in (".yaml", ".yml"):
        if shutil.which("yamllint"):
            res = subprocess.run(['yamllint', file_path], stdout=subprocess.PIPE, text=True)
            if res.returncode != 0:
                print_err(f"yamllint violations in '{file_path}':\n{res.stdout}")
                return False
        return True

    elif ext == ".json":
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            return True
        except Exception as e:
            print_err(f"JSON syntax check failed for '{file_path}':\n{e}")
            return False

    elif ext == ".java":
        if shutil.which("javac"):
            import tempfile
            res = subprocess.run(['javac', '-d', tempfile.gettempdir(), file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode != 0:
                print_err(f"Java compilation errors in '{file_path}':\n{res.stderr or res.stdout}")
                return False
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

        if ext in (".ts", ".tsx"):
            tsc_bin = None
            curr_dir = os.path.dirname(os.path.abspath(file_path))
            while curr_dir and curr_dir != os.path.dirname(curr_dir):
                bin_path = os.path.join(curr_dir, "node_modules", ".bin", "tsc")
                if os.path.exists(bin_path):
                    tsc_bin = bin_path
                    break
                curr_dir = os.path.dirname(curr_dir)
            if not tsc_bin:
                tsc_bin = shutil.which("tsc")
            if tsc_bin:
                res_tsc = subprocess.run([tsc_bin, '--noEmit', '--skipLibCheck', file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if res_tsc.returncode != 0:
                    print_err(f"TypeScript compilation errors in '{file_path}':\n{res_tsc.stdout or res_tsc.stderr}")
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
        env = dict(os.environ)
        env["IN_AUDIT_TEST"] = "true"
        try:
            test_res = subprocess.run(test_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env, timeout=15)
            if test_res.returncode != 0:
                print_err(f"Agent unit tests failed!\nStdout:\n{test_res.stdout}\nStderr:\n{test_res.stderr}")
                failed = True
            else:
                print_ok("Agent unit tests passed successfully.")
        except subprocess.TimeoutExpired:
            print_err("Agent unit tests execution timed out after 15 seconds! Halted to prevent process hang.")
            failed = True
            
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

                max_workers = min(len(tasks), os.cpu_count() or 4)
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
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
    if os.environ.get("SKIP_LOCK_AUDIT") == "true" or os.environ.get("AAC_BYPASS_LOCKS") == "1":
        print_warn("Module Lock Compliance check bypassed by user request.")
        return True

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

    locks = {}
    try:
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'cli')))
        from commands.lock import load_locks
        locks = load_locks()
    except Exception as e:
        pass

    failed = False
    for path in sorted(modified_files):
        if path.endswith(('.md', '.json', '.txt', '.sh', '.ps1', '.gitignore', '.antigravityignore', '.example', '.template')):
            continue
        if "tests/" in path or "plans/" in path or "memory/" in path or "docs/" in path:
            continue
            
        rel_path = os.path.splitext(path)[0]
        lock_key = rel_path
        
        # Support backward compatibility for common modules locked by short basename
        if lock_key not in locks and os.path.basename(rel_path) in locks:
            lock_key = os.path.basename(rel_path)
            
        if lock_key in locks:
            if locks[lock_key] != branch:
                print_err(f"Module '{lock_key}' (file '{path}') is locked by branch '{locks[lock_key]}', but you are editing from '{branch}'!")
                failed = True
            else:
                print_ok(f"Module '{lock_key}' (file '{path}') is correctly locked by this branch.")
        else:
            print_err(f"Module '{lock_key}' (file '{path}') is modified, but no lock is acquired! "
                      f"Please run './helper.sh lock {lock_key}' first.")
            failed = True

    if not failed:
        print_ok("Lock compliance check passed.")
    return not failed

def prune_stale_locks() -> None:
    # No-op under Git-Native branch-bound locking
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
    base_branch = get_base_branch()

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
    # Compliance Audit pattern (anywhere in commit message)
    compliance_pattern = re.compile(r'Compliance-Audit:\s*passed', re.IGNORECASE)

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

        # Forbid generic/placeholder subjects that only mention issue IDs or generic words
        parts = subject.split(':', 1)
        description = parts[1].strip() if len(parts) > 1 else ""
        generic_patterns = [
            r'^(?:fix|chore|feat|refactor|test|docs)?\s*(?:issue|task)-?\d+$',
            r'^close\s*(?:issue|task)-?\d+$',
            r'^fix\s+bugs?$',
            r'^updates?$',
            r'^fixes?$'
        ]
        is_generic = False
        for gp in generic_patterns:
            if re.match(gp, description, re.IGNORECASE):
                is_generic = True
                break
        if is_generic:
            print_err(f"Commit subject is too generic: '{subject}'")
            print_err("  Please provide a descriptive subject summarizing what was changed (e.g. 'fix(security): resolve command injection').")
            failed = True
            continue

        # Check Refs trailer line
        if not refs_pattern.search(commit):
            print_err(f"Commit message is missing 'Refs: <issue-id>' trailer: '{subject}'")
            print_err("  Example: 'Refs: issue-106'")
            failed = True

        # Check Compliance-Audit trailer line
        is_exempt = subject.startswith("chore(release):") or subject.startswith("chore(git):") or subject.startswith("Merge ")
        if not is_exempt and not compliance_pattern.search(commit):
            print_err(f"Commit message is missing 'Compliance-Audit: passed' trailer: '{subject}'")
            print_err("  Please perform the Rule & Schema Compliance Audit and add 'Compliance-Audit: passed' to verify compliance.")
            failed = True

    if failed:
        return False
        
    print_ok("All commit messages are compliant with Conventional Commits and reference task IDs.")
    return True

# ==========================================================
# 11. Codebase Rule & Guidelines Compliance Audit
# ==========================================================
def audit_codebase_rules_compliance() -> bool:
    print("\n[11/11] Auditing Codebase Rule & Guidelines Compliance...")
    failed = False
    
    # Precise regex to match open calls with write modes on locks.json or token_budget.json
    raw_write_pattern = re.compile(r'open\s*\(\s*[^)]*(?:locks\.json|token_budget\.json|LOCK_FILE|BUDGET_FILE)[^)]*,\s*[\'"](?:w|a|r\+)')
    
    # 1. Scan for inline file creation templates in scripts (*.sh, *.ps1)
    try:
        res = subprocess.run(['git', 'ls-files'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0:
            tracked_files = [f.strip() for f in res.stdout.splitlines() if f.strip()]
            for filepath in tracked_files:
                if filepath.endswith(('.sh', '.ps1')):
                    if not os.path.exists(filepath):
                        continue
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    # Check for inline file output content using redirection or here-docs
                    if "cat << 'EOF'" in content or "cat <<EOF" in content:
                        print_err(f"Script file '{filepath}' violates 'no duplicate/inline templates' rule by writing files inline!")
                        failed = True
                        
                elif filepath.endswith('.py') and "validate.py" not in filepath and "test_" not in filepath:
                    if not os.path.exists(filepath):
                        continue
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    # Look for raw writes to locks.json or token_budget.json
                    if raw_write_pattern.search(content):
                        # Verify if tempfile is imported or used in the same file to confirm atomic usage
                        if "NamedTemporaryFile" not in content:
                            print_err(f"Python script '{filepath}' violates 'atomic file writing' guidelines by using raw open write mode on critical JSON files!")
                            failed = True
    except Exception as e:
        print_warn(f"Failed to scan codebase rule compliance: {e}")

    # 2. Check Clean Architecture imports in domain/ modules
    try:
        import ast
        import sys
        std_libs = getattr(sys, "stdlib_module_names", set())
        if not std_libs:
            std_libs = {"typing", "datetime", "uuid", "abc", "dataclasses", "enum", "math", "json", "collections", "sys", "os"}
            
        src_dir = "src"
        if os.path.exists(src_dir):
            for root, dirs, files in os.walk(src_dir):
                if "domain" in root.lower().split(os.sep):
                    for file in files:
                        if file.endswith(".py"):
                            filepath = os.path.join(root, file)
                            with open(filepath, 'r', encoding='utf-8') as f:
                                tree = ast.parse(f.read(), filename=filepath)
                            for node in ast.walk(tree):
                                if isinstance(node, ast.Import):
                                    for alias in node.names:
                                        name = alias.name.split('.')[0]
                                        if name not in std_libs:
                                            print_err(f"Domain entity '{filepath}' violates schema.md: imports external/non-domain module '{alias.name}'!")
                                            failed = True
                                elif isinstance(node, ast.ImportFrom):
                                    if node.level > 0:
                                        continue
                                    if node.module:
                                        name = node.module.split('.')[0]
                                        if name not in std_libs and name != "domain":
                                            print_err(f"Domain entity '{filepath}' violates schema.md: imports external/non-domain module '{node.module}'!")
                                            failed = True
    except Exception as e:
        print_warn(f"Failed to scan clean architecture dependencies: {e}")
        
    if not failed:
        print_ok("Codebase rule compliance check passed.")
    return not failed

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

def make_skill_audit(name: str, hook_path: str):
    def run_skill_hook() -> bool:
        try:
            res = subprocess.run(
                [sys.executable, hook_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if res.returncode == 0:
                return True
            else:
                print_err(f"Skill '{name}' validation hook failed (exit code {res.returncode}):")
                if res.stdout.strip():
                    print(res.stdout)
                if res.stderr.strip():
                    print(res.stderr, file=sys.stderr)
                return False
        except Exception as e:
            print_err(f"Skill '{name}' validation hook execution crashed: {e}")
            return False
    return run_skill_hook

def run_validations() -> None:
    # Check for bypass flags (human fast-track mode)
    if "--bypass" in sys.argv or os.environ.get("AAC_BYPASS_COMPLIANCE", "0").lower() in ("1", "true"):
        print("==========================================================")
        print("   Running AAC V2 Local Validation Guard...              ")
        print("==========================================================")
        print(f"{YELLOW}[BYPASS] Human Fast-Track/Bypass enabled. Bypassing validations...{RESET}")
        print("==========================================================")
        sys.exit(0)

    failed = False
    
    # Self-heal active context manifest if missing on a feature branch
    context_file = ".agents/state/active_context.md"
    if not os.path.exists(context_file):
        branch = get_current_branch()
        if branch and branch not in ('main', 'master', 'HEAD'):
            match = re.search(r'(task-\d+|issue-\d+)', branch.lower())
            if match:
                print("Active context manifest '.agents/state/active_context.md' is missing. Regenerating...")
                try:
                    cli_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "cli"))
                    if cli_dir not in sys.path:
                        sys.path.insert(0, cli_dir)
                    import commands.context as context_cmd
                    context_cmd.optimize_context()
                except Exception as e:
                    print(f"Warning: Failed to auto-generate context manifest: {e}")
    
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
    

    # Run all audits in parallel wrapped inside SandboxManager
    results = {}
    with SandboxManager(enabled=True) as sandbox:
        audits = {
            "Critical Files": audit_critical_files,
            "Secrets & Ignored Files": audit_secrets_and_ignored_files,
            "Link Integrity": audit_link_integrity,
            "Git Branch Alignment": audit_git_branch_alignment,
            "Workspace Sync": audit_workspace_sync,
            "Task Board Schema": audit_task_board_schema,
            "Static Code Linting": audit_static_linting,
            "Local Unit Tests": audit_unit_tests,
            "Module Lock Compliance": audit_module_locks,
            "Commit Message Compliance": audit_commit_messages,
            "Codebase Rule Compliance": audit_codebase_rules_compliance,
        }
        
        # Load and execute active skill validation hooks from registry.json
        registry_file = ".agents/skills/registry.json"
        if os.path.exists(registry_file):
            try:
                with open(registry_file, 'r', encoding='utf-8') as f:
                    registry = json.load(f)
                skills = registry.get("skills", {})
                for skill_name, skill_info in skills.items():
                    if skill_info.get("has_validation_hook") and skill_info.get("validation_hook_path"):
                        hook_path = skill_info["validation_hook_path"]
                        audits[f"Skill: {skill_name}"] = make_skill_audit(skill_name, hook_path)
            except Exception as e:
                print_warn(f"Failed to load skill validation hooks from registry: {e}")
        
        with ThreadPoolExecutor() as executor:
            future_to_key = {executor.submit(func): key for key, func in audits.items()}
            for future in future_to_key:
                key = future_to_key[future]
                try:
                    results[key] = future.result()
                except Exception as e:
                    _original_print(f"{RED}[ERROR] Audit '{key}' crashed: {e}{RESET}")
                    results[key] = False
    
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
        print(f"{YELLOW}   [TIP] If you are a human developer and need to bypass this check, run: {RESET}")
        print(f"{YELLOW}         AAC_BYPASS_COMPLIANCE=1 git commit ... or use --no-verify {RESET}")
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
