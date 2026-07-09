import sys
import os
import subprocess
import socket
import json
from typing import List

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def print_err(msg: str) -> None:
    print(f"{RED}[FAIL] {msg}{RESET}")

def print_warn(msg: str) -> None:
    print(f"{YELLOW}[WARN] {msg}{RESET}")

def print_ok(msg: str) -> None:
    print(f"{GREEN}[OK] {msg}{RESET}")

def check_python() -> bool:
    print("Checking Python environment...")
    v = sys.version_info
    if v.major < 3 or (v.major == 3 and v.minor < 8):
        print_err(f"Python version {sys.version} is older than recommended 3.8.")
        return False
    print_ok(f"Python {v.major}.{v.minor}.{v.micro} verified.")
    return True

def check_git() -> bool:
    print("Checking Git CLI installation...")
    try:
        res = subprocess.run(['git', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0:
            print_ok(f"Git CLI detected: {res.stdout.strip()}")
            return True
        else:
            print_err("Git version check returned non-zero code.")
            return False
    except FileNotFoundError:
        print_err("Git binary 'git' not found in system PATH.")
        return False

def check_worktree() -> bool:
    print("Checking Git workspace root...")
    try:
        res = subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0 and res.stdout.strip() == "true":
            print_ok("Workspace is inside a valid Git work tree.")
            return True
        else:
            print_err("Not inside a Git repository work tree.")
            return False
    except Exception as e:
        print_err(f"Git workspace check failed: {e}")
        return False

def check_identity() -> bool:
    print("Checking Git identity configuration...")
    success = True
    try:
        res_email = subprocess.run(['git', 'config', 'user.email'], stdout=subprocess.PIPE, text=True)
        email = res_email.stdout.strip()
        res_name = subprocess.run(['git', 'config', 'user.name'], stdout=subprocess.PIPE, text=True)
        name = res_name.stdout.strip()
        
        if not email:
            print_warn("Git email ('user.email') is not configured.")
            success = False
        else:
            print_ok(f"Git Config Email: '{email}'")
            
        if not name:
            print_warn("Git name ('user.name') is not configured.")
            success = False
        else:
            print_ok(f"Git Config Name: '{name}'")
    except Exception as e:
        print_err(f"Failed to query Git identity: {e}")
        return False
    return success

def check_profiles() -> bool:
    print("Checking developer profiles config...")
    profiles_file = ".agents/git_profiles.json"
    if not os.path.exists(profiles_file):
        print_warn(f"Developer profiles config '{profiles_file}' is missing.")
        return False
        
    try:
        with open(profiles_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        profiles = data.get("profiles", [])
        if not profiles:
            print_warn("No profiles registered in git_profiles.json.")
            return False
            
        print_ok(f"Found {len(profiles)} registered developer profiles.")
        active = next((p for p in profiles if p.get("active")), None)
        if active:
            print_ok(f"Active profile: '{active.get('name')}' <{active.get('email')}>")
            
            # 1. Check SSH Key
            ssh_key = active.get("ssh_key_path")
            if ssh_key:
                ssh_key_abs = os.path.abspath(os.path.expanduser(ssh_key))
                if os.path.exists(ssh_key_abs):
                    print_ok(f"SSH private key file verified: '{ssh_key_abs}'")
                else:
                    print_warn(f"SSH private key file not found: '{ssh_key_abs}'. "
                               f"Commit signatures using SSH key might fail if this key is required.")
                    
            # 2. Check GPG Key
            signing_key = active.get("signing_key")
            if signing_key and not signing_key.startswith("ssh-"):
                import shutil
                print(f"Verifying GPG signing key '{signing_key}' in local keyring...")
                if shutil.which("gpg"):
                    try:
                        gpg_check = subprocess.run(
                            ['gpg', '--list-secret-keys', '--keyid-format', 'LONG', signing_key],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                        )
                        if gpg_check.returncode == 0:
                            print_ok("GPG signing key verified in local keyring.")
                        else:
                            print_warn(f"GPG key '{signing_key}' not found in local keyring! Commit signing will fail if required.")
                    except Exception as e:
                        print_warn(f"Failed to execute gpg check: {e}")
                else:
                    print_warn("GnuPG ('gpg') tool is not installed, but GPG commit signing key is configured.")
        else:
            print_warn("No active profile set in git_profiles.json.")
            
        return True
    except Exception as e:
        print_err(f"Error parsing git_profiles.json: {e}")
        return False

def check_network() -> bool:
    print("Checking network connectivity to remote repo domain (github.com)...")
    try:
        socket.setdefaulttimeout(2.0)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("github.com", 443))
        s.close()
        print_ok("Network connection to github.com verified.")
        return True
    except Exception as e:
        print_warn(f"Domain github.com is unreachable (offline mode active): {e}")
        return False

def get_existing_branches() -> set:
    """Retrieve all local Git branch names in a single Git call."""
    try:
        res = subprocess.run(
            ['git', 'show-ref', '--heads'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if res.returncode != 0:
            return set()
        branches = set()
        for line in res.stdout.splitlines():
            parts = line.strip().split()
            if len(parts) == 2:
                ref = parts[1]
                if ref.startswith("refs/heads/"):
                    branches.add(ref[11:])
        return branches
    except Exception:
        return set()

def perform_repairs() -> None:
    print("Running auto-recovery repairs...")
    
    # 1. Restore missing or corrupted JSON configs
    configs = {
        ".agents/state/locks.json": {},
        ".agents/state/token_budget.json": {
            "monthly_limit": 5000000,
            "monthly_used": 0,
            "daily_limit": 500000,
            "daily_used": 0,
            "last_reset": "1970-01-01T00:00:00Z",
            "tasks": {}
        },
        ".agents/projects.json": []
    }
    
    for path, default_val in configs.items():
        needs_restore = False
        if not os.path.exists(path):
            print_warn(f"Config '{path}' is missing.")
            needs_restore = True
        else:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    json.load(f)
            except Exception:
                print_warn(f"Config '{path}' is corrupted/invalid JSON.")
                needs_restore = True
                
        if needs_restore:
            try:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(default_val, f, indent=2)
                print_ok(f"Restored default configuration for '{path}'.")
            except Exception as e:
                print_err(f"Failed to restore '{path}': {e}")

    # 2. Fix missing profiles config from example
    profiles_file = ".agents/git_profiles.json"
    profiles_example = ".agents/git_profiles.example"
    if not os.path.exists(profiles_file) and os.path.exists(profiles_example):
        try:
            import shutil
            shutil.copy(profiles_example, profiles_file)
            print_ok(f"Recovered '{profiles_file}' from example template.")
        except Exception as e:
            print_err(f"Failed to recover profiles config: {e}")

    # 3. Clean up stale locks
    locks_file = ".agents/state/locks.json"
    if os.path.exists(locks_file):
        try:
            with open(locks_file, 'r', encoding='utf-8') as f:
                locks = json.load(f)
            existing_branches = get_existing_branches()
            stale_keys = []
            for key, branch in list(locks.items()):
                if branch not in existing_branches and branch != "unknown":
                    stale_keys.append(key)
            
            if stale_keys:
                for key in stale_keys:
                    del locks[key]
                with open(locks_file, 'w', encoding='utf-8') as f:
                    json.dump(locks, f, indent=2)
                print_ok(f"Pruned stale locks for deleted branches: {', '.join(stale_keys)}")
        except Exception as e:
            print_err(f"Failed to prune stale locks: {e}")

    # 4. Repair/Install Git Hooks
    try:
        res = subprocess.run(['git', 'rev-parse', '--git-dir'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0:
            git_dir = res.stdout.strip()
            hooks_dir = os.path.join(git_dir, "hooks")
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
                    with open(path, 'w', encoding='utf-8') as hf:
                        hf.write(content.replace("\r\n", "\n"))
                    try:
                        os.chmod(path, 0o755)
                    except Exception:
                        pass
                print_ok("Reinstalled/repaired all Git hooks.")
    except Exception as e:
        print_err(f"Failed to repair Git hooks: {e}")

def run(args: List[str]) -> None:
    repair_mode = "--repair" in args
    
    print("="*60)
    print("      Antigravity Agent Core (AAC) V3 Diagnostics Doctor")
    print("="*60)
    
    if repair_mode:
        perform_repairs()
        print("="*60)
        
    passed = True
    passed &= check_python()
    print("-"*60)
    passed &= check_git()
    print("-"*60)
    passed &= check_worktree()
    print("-"*60)
    passed &= check_identity()
    print("-"*60)
    passed &= check_profiles()
    print("-"*60)
    check_network()
    print("="*60)
    
    if not passed:
        if not repair_mode:
            print_warn("Diagnostics detected warnings or failures. Run with --repair to auto-fix.")
            sys.exit(1)
        else:
            print_warn("Repairs completed, but some diagnostic warnings persist.")
            sys.exit(0)
    else:
        print_ok("All diagnostic audits PASSED! Local workspace is healthy.")
        print("="*60)
        sys.exit(0)
