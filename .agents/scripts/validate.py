import os
import re
import sys
import subprocess
import shutil
from typing import List, Dict, Any

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
    print("\n[1/8] Auditing Critical Files...")
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
    print("\n[2/8] Auditing for Staged Secrets, Private, and Ignored Files...")
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
            
    if not failed:
        print_ok("No credentials, staged private files, or secrets detected.")
    return not failed

# ==========================================================
# 3. Link Integrity Audit
# ==========================================================
def audit_link_integrity() -> bool:
    print("\n[3/8] Auditing File Links inside Memory Registers...")
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
                    
                    if not clean_path.startswith('/'):
                        resolved_path = os.path.join(os.path.dirname(f), base_path)
                    else:
                        resolved_path = base_path
                    
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
    print("\n[4/8] Auditing Git Branch to Local Issue Alignment...")
    branch = get_current_branch()
    if not branch:
        print_warn("Not inside a git repository or git command failed.")
        return True
        
    if branch in ('main', 'master', 'HEAD'):
        print_ok(f"On base branch '{branch}' (skipping issue verification).")
        return True
        
    match = re.search(r'(task-\d+|issue-\d+)', branch.lower())
    if not match:
        print_warn(f"Branch name '{branch}' does not contain an issue ID pattern (e.g. 'issue-12' or 'task-001').")
        return True
        
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
                unchecked = re.findall(r'([-*]\s*\[\s+\]\s+.*)', issue_content)
                if unchecked:
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
    print("\n[5/8] Auditing Workspace Sync Alignment...")
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
    print("\n[6/8] Auditing Task Board Schema Compliance...")
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
    print("\n[7/8] Auditing Static Syntax Compilation...")
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
                    import py_compile
                    try:
                        py_compile.compile(file_path, doraise=True)
                    except py_compile.PyCompileError as e:
                        print_err(f"Python syntax compilation failed for '{file_path}':\n{e}")
                        failed = True
                        continue
                        
                    import shutil
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
    print("\n[8/8] Executing Local Unit Tests...")
    if os.getenv("BYPASS_TESTS") == "true":
        print_warn("Bypass flag 'BYPASS_TESTS=true' detected. Skipping unit test execution.")
        return True
        
    test_cmd = None
    if os.path.exists(".agents/tests"):
        if shutil.which("pytest"):
            test_cmd = ["pytest", ".agents/tests"]
        else:
            test_cmd = [sys.executable, "-m", "unittest", "discover", "-s", ".agents/tests"]
            
    if test_cmd:
        print(f"Running test suite: {' '.join(test_cmd)}")
        test_res = subprocess.run(test_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if test_res.returncode != 0:
            print_err(f"Unit tests failed!\nStdout:\n{test_res.stdout}\nStderr:\n{test_res.stderr}")
            return False
        else:
            print_ok("All unit tests passed successfully.")
            return True
    else:
        print_warn("No test suite directory ('.agents/tests/') or runner (pytest/unittest) found.")
        return True

# ==========================================================
# Main Execution Entry Point
# ==========================================================
def run_validations() -> None:
    failed = False
    
    print("==========================================================")
    print("   Running AAC V2 Local Validation Guard...              ")
    print("==========================================================")
    
    # Run the 8 audits sequentially
    results = {}
    results["Critical Files"] = audit_critical_files()
    results["Secrets & Ignored Files"] = audit_secrets_and_ignored_files()
    results["Link Integrity"] = audit_link_integrity()
    results["Git Branch Alignment"] = audit_git_branch_alignment()
    results["Workspace Sync"] = audit_workspace_sync()
    results["Task Board Schema"] = audit_task_board_schema()
    results["Static Code Linting"] = audit_static_linting()
    results["Local Unit Tests"] = audit_unit_tests()
    
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
        sys.exit(1)
    else:
        print(f"{GREEN}   Validation PASSED! Workspace is compliant.      {RESET}")
        print("==========================================================")
        sys.exit(0)

if __name__ == '__main__':
    run_validations()
