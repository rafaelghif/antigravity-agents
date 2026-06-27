import os
import re
import sys

# Terminal Colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def print_err(msg):
    print(f"{RED}[FAIL] {msg}{RESET}", file=sys.stderr)

def print_warn(msg):
    print(f"{YELLOW}[WARN] {msg}{RESET}")

def print_ok(msg):
    print(f"{GREEN}[OK] {msg}{RESET}")

def run_validations():
    failed = False
    
    print("==========================================================")
    print("   Running AAC V2 Local Validation Guard...              ")
    print("==========================================================")
    
    # 1. Critical Files Audit
    critical_files = [
        "AGENTS.md",
        ".agents/rules.md",
        ".agents/tasks/board.md",
        ".agents/memory/architecture.md"
    ]
    
    print("\n[1/8] Auditing Critical Files...")
    for f in critical_files:
        if not os.path.exists(f):
            print_err(f"Critical file '{f}' is missing from workspace!")
            failed = True
        else:
            print_ok(f"Found '{f}'")
            
    # 2. Secret Exposure Audit
    print("\n[2/8] Auditing for Staged Secrets & Credentials...")
    # Scan files in current directory, excluding .git, node_modules, vendor, etc.
    secret_patterns = [
        r"(?i)api_key\s*=\s*['\"][a-zA-Z0-9_\-]{16,}['\"]",
        r"(?i)password\s*=\s*['\"][a-zA-Z0-9_\-]{8,}['\"]",
        r"(?i)private_key\s*=\s*['\"].*['\"]",
        r"-----BEGIN [A-Z ]+ PRIVATE KEY-----"
    ]
    
    exclude_dirs = {'.git', 'node_modules', 'venv', 'env', '__pycache__', 'vendor'}
    found_secrets = False
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            # Skip binary files or common non-code files
            if file.endswith(('.png', '.jpg', '.ico', '.pdf', '.zip', '.tar.gz')):
                continue
            path = os.path.join(root, file)
            # Avoid self-scanning validation script or Git logs
            if "validate.py" in path:
                continue
                
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for idx, line in enumerate(content.splitlines(), 1):
                        for pattern in secret_patterns:
                            if re.search(pattern, line):
                                print_err(f"Potential secret exposed in '{path}' at line {idx}: {line.strip()}")
                                found_secrets = True
                                failed = True
            except Exception:
                pass
                
    if not found_secrets:
        print_ok("No credentials or secrets detected.")
        
    # 3. Link Integrity Audit
    print("\n[3/8] Auditing File Links inside Memory Registers...")
    link_files = [".agents/memory/architecture.md", ".agents/schema.md"]
    found_broken_links = False
    
    for f in link_files:
        if not os.path.exists(f):
            continue
        try:
            with open(f, 'r', encoding='utf-8') as file:
                content = file.read()
                # Find markdown file scheme links like file:///absolute/path/to/file or file://./relative/path
                links = re.findall(r'file://([^\s\)]+)', content)
                for link in links:
                    # Parse absolute vs relative file paths
                    if link.startswith('///'):
                        clean_path = '/' + link[3:]
                    elif link.startswith('//.'):
                        clean_path = link[2:]
                    else:
                        clean_path = link
                    
                    # Split anchors (#L120-L130)
                    base_path = clean_path.split('#')[0]
                    # Unquote URL encoding (%20 etc)
                    from urllib.parse import unquote
                    base_path = unquote(base_path)
                    
                    # Resolve relative path from the scanned file's directory
                    if not clean_path.startswith('/'):
                        resolved_path = os.path.join(os.path.dirname(f), base_path)
                    else:
                        resolved_path = base_path
                    
                    if resolved_path and not os.path.exists(resolved_path):
                        print_err(f"Broken link in '{f}': linked file '{resolved_path}' does not exist.")
                        found_broken_links = True
                        failed = True
        except Exception as e:
            print_warn(f"Failed to scan links in '{f}': {e}")
            
    if not found_broken_links:
        print_ok("All file-link path integrity checks passed.")
        
    # 4. Git Branch & Issue Alignment Audit
    print("\n[4/8] Auditing Git Branch to Local Issue Alignment...")
    branch = get_current_branch()
    if branch:
        if branch in ('main', 'master', 'HEAD'):
            print_ok(f"On base branch '{branch}' (skipping issue verification).")
        else:
            # Detect pattern like issue-001 or task-001
            match = re.search(r'(task-\d+|issue-\d+)', branch.lower())
            if not match:
                print_warn(f"Branch name '{branch}' does not contain an issue ID pattern (e.g. 'issue-12' or 'task-001').")
            else:
                issue_id = match.group(1)
                task_board_path = ".agents/tasks/board.md"
                in_board = False
                if os.path.exists(task_board_path):
                    with open(task_board_path, 'r', encoding='utf-8') as tb:
                        tb_content = tb.read()
                        if issue_id in tb_content:
                            in_board = True
                            
                # Check for issue file: issue_001.md or task-001.md
                issue_dir = ".agents/issues"
                file_exists = False
                if os.path.exists(issue_dir):
                    normalized_id = issue_id.replace('-', '_')
                    for f_name in os.listdir(issue_dir):
                        if normalized_id in f_name.lower().replace('-', '_') or issue_id in f_name.lower():
                            file_exists = True
                            break
                            
                if not (file_exists or in_board):
                    print_err(f"Branch '{branch}' references issue '{issue_id}', but it is not registered in '{task_board_path}' and no matching issue file exists in '{issue_dir}'!")
                    failed = True
                else:
                    print_ok(f"Branch '{branch}' successfully aligned with registered issue '{issue_id}'.")
                    
                    # Audit active issue checkboxes/subtasks
                    if file_exists:
                        matched_path = None
                        normalized_id = issue_id.replace('-', '_')
                        for f_name in os.listdir(issue_dir):
                            if normalized_id in f_name.lower().replace('-', '_') or issue_id in f_name.lower():
                                matched_path = os.path.join(issue_dir, f_name)
                                break
                        if matched_path:
                            try:
                                with open(matched_path, 'r', encoding='utf-8') as f:
                                    issue_content = f.read()
                                    unchecked = re.findall(r'([-*]\s*\[\s+\]\s+.*)', issue_content)
                                    if unchecked:
                                        print_err(f"Active issue '{issue_id}' has {len(unchecked)} unresolved subtasks:")
                                        for task in unchecked:
                                            print_err(f"  {task.strip()}")
                                        failed = True
                                    else:
                                        print_ok(f"All subtasks in issue '{issue_id}' have been resolved.")
                            except Exception as e:
                                print_warn(f"Failed to parse subtasks in '{matched_path}': {e}")
    else:
        print_warn("Not inside a git repository or git command failed.")
        
    # 5. Synchronization Check
    print("\n[5/8] Auditing Workspace Sync Alignment...")
    skills_dir = ".agents/skills"
    agents_file = "AGENTS.md"
    sync_failed = False
    if os.path.exists(skills_dir) and os.path.exists(agents_file):
        with open(agents_file, 'r', encoding='utf-8') as af:
            af_content = af.read()
        for skill_name in os.listdir(skills_dir):
            skill_path = os.path.join(skills_dir, skill_name, "SKILL.md")
            if os.path.exists(skill_path):
                if f".agents/skills/{skill_name}/SKILL.md" not in af_content:
                    print_err(f"Skill '{skill_name}' is not registered in '{agents_file}' context map!")
                    sync_failed = True
                    failed = True
                    
    if not sync_failed:
        print_ok("Workspace AGENTS.md is in perfect sync with local skills.")
        
    # 6. Task Board Schema Compliance Check
    print("\n[6/8] Auditing Task Board Schema Compliance...")
    task_board = ".agents/tasks/board.md"
    board_failed = False
    if os.path.exists(task_board):
        try:
            with open(task_board, 'r', encoding='utf-8') as f:
                content = f.read()
            required_sections = ["## Todo", "## Doing", "## Done"]
            for sec in required_sections:
                if sec not in content:
                    print_err(f"Task board '{task_board}' is missing section '{sec}'!")
                    board_failed = True
                    failed = True
            # Verify markdown task checkboxes have dynamic tracking IDs
            task_lines = re.findall(r'([-*]\s*\[[xX /]\].*)', content)
            for line in task_lines:
                if "<!-- id:" not in line:
                    print_warn(f"Task line missing ID tracking comment: '{line.strip()}'")
        except Exception as e:
            print_warn(f"Failed to scan task board schema: {e}")
    if not board_failed:
        print_ok("Task board schema is compliant.")
        
    # 7. Static Code Linting / Compile Check
    print("\n[7/8] Auditing Static Syntax Compilation...")
    lint_failed = False
    scripts_dir = ".agents/scripts"
    if os.path.exists(scripts_dir):
        for root, _, files in os.walk(scripts_dir):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    import py_compile
                    try:
                        py_compile.compile(file_path, doraise=True)
                    except py_compile.PyCompileError as e:
                        print_err(f"Python syntax compilation failed for '{file_path}':\n{e}")
                        lint_failed = True
                        failed = True
                        continue
                        
                    # Optional style check via flake8
                    import shutil
                    if shutil.which("flake8"):
                        import subprocess
                        res = subprocess.run(['flake8', file_path], stdout=subprocess.PIPE, text=True)
                        if res.returncode != 0:
                            print_err(f"flake8 style violations found in '{file_path}':\n{res.stdout}")
                            lint_failed = True
                            failed = True
    if not lint_failed:
        print_ok("Static syntax compilation and style audits passed.")
        
    # 8. Executing Local Unit Tests
    print("\n[8/8] Executing Local Unit Tests...")
    if os.getenv("BYPASS_TESTS") == "true":
        print_warn("Bypass flag 'BYPASS_TESTS=true' detected. Skipping unit test execution.")
    else:
        import shutil
        import subprocess
        test_cmd = None
        # Default python/pytest testing
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
                failed = True
            else:
                print_ok("All unit tests passed successfully.")
        else:
            print_warn("No test suite directory ('.agents/tests/') or runner (pytest/unittest) found.")
            
    print("\n==========================================================")
    if failed:
        print(f"{RED}   Validation FAILED! Please fix the errors above. {RESET}")
        print("==========================================================")
        sys.exit(1)
    else:
        print(f"{GREEN}   Validation PASSED! Workspace is compliant.      {RESET}")
        print("==========================================================")
        sys.exit(0)

def get_current_branch():
    import subprocess
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

if __name__ == '__main__':
    run_validations()
