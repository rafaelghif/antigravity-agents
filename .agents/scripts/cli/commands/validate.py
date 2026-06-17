import os
import sys
import re
import subprocess
import json
import utils

# ANSI color codes
C_GREEN = '\033[92m'
C_YELLOW = '\033[93m'
C_RED = '\033[91m'
C_BLUE = '\033[94m'
C_CYAN = '\033[96m'
C_BOLD = '\033[1m'
C_END = '\033[0m'

def color(text, ansi_code):
    if sys.stdout.isatty():
        return f"{ansi_code}{text}{C_END}"
    return text

def get_files_to_scan():
    exclude_dirs = {'.git', '.agents', 'node_modules', 'dist', 'build', 'venv', 'env', 'target', 'vendor', 'out', '__pycache__'}
    exclude_exts = {'.pyc', '.md', '.json', '.lock', '.png', '.jpg', '.gif'}
    files_to_scan = []
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
        for f in files:
            ext = os.path.splitext(f)[1]
            if ext in exclude_exts or f == 'bootstrap.sh':
                continue
            files_to_scan.append(os.path.join(root, f))
    return files_to_scan

def run(args):
    utils.print_title("Starting Antigravity Agent Workspace Validation...")
    
    failed = False
    
    # 1. Check Active Memory Size
    memory_file = utils.get_memory_file()
    print(f"Check 1: Memory File Line Count")
    if os.path.exists(memory_file):
        try:
            with open(memory_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            line_count = len(lines)
            print(f"  Memory file: {line_count} lines")
            if line_count > 100:
                print(f"  {color('[WARNING]', C_YELLOW + C_BOLD)} Memory file '{memory_file}' exceeds the 100-line limit ({line_count} lines)!")
                print("            Please run 'python .agents/scripts/cli/helper.py archive' to compact your memory.")
            else:
                print("  [PASS] Memory file size is within recommended limits.")
        except Exception as e:
            print(f"  {color('[FAIL]', C_RED + C_BOLD)} Failed to read memory file: {e}")
            failed = True
    else:
        print(f"  {color('[FAIL]', C_RED + C_BOLD)} Memory file '{memory_file}' does not exist!")
        failed = True
        
    # 2. Check Active Lockfiles
    print("Check 2: Active Module Locks")
    locks_dir = os.path.join(utils.get_agents_dir(), "locks")
    if os.path.exists(locks_dir) and os.path.isdir(locks_dir):
        lock_files = [f for f in os.listdir(locks_dir) if f.endswith('.lock')]
        if lock_files:
            print("  Found active locks:")
            for lf in lock_files:
                mod = os.path.splitext(lf)[0]
                print(f"  - Module '{mod}':")
                try:
                    with open(os.path.join(locks_dir, lf), 'r', encoding='utf-8') as f:
                        for line in f:
                            print(f"    {line.strip()}")
                except Exception:
                    pass
        else:
            print("  [PASS] No active locks found.")
    else:
        print("  [PASS] No active locks found.")
        
    # 3. Secret and Credential Scanning
    failed = check_hardcoded_credentials(failed)
    
    # 4. Check for Raw Environment Variable Reads
    check_raw_env()
    
    # 5. Check Git Upstream Synchronization
    failed = check_git_upstream(failed)
    
    # 6. Check Schema Index Registration Compliance
    failed = check_schema_registration(failed)
    
    # 7. Check Gitignore & Antigravityignore Configuration Compliance
    failed = check_gitignore_compliance(failed)
    
    # 8. Check Memory State Flag Enforcement
    failed = check_memory_state_flag(failed)
    
    # 9. Check Token Budget Guard
    failed = check_token_budget(failed)
    
    # 10. Check ADR Compliance Check
    failed = check_adr_compliance(failed)
    
    # 11. Check Git Configuration & Profile Compliance
    failed = check_git_profile_compliance(failed)
    
    # 12. Check API Configuration & Profile Compliance
    failed = check_api_profile_compliance(failed)
    
    # 13. Check CHANGELOG.md Format (Keep a Changelog Compliance)
    failed = check_changelog(failed)
    
    # 14. Check for TODO/FIXME Annotations in Staged Code
    failed = check_staged_todo(failed)
    
    # 15. Check for Staged Transient Files & Config Leak Guard
    failed = check_staged_transient(failed)
    
    # 16. Local Workspace Issues Schema Validation
    failed = check_local_issues(failed)
    
    # 17. Base Branch Modification Check
    failed = check_base_branch_modification(failed)
    
    # 18. Staged/Modified Files Module Locking Check
    failed = check_module_locking(failed)
    
    # 19. Issue Branch and Memory Alignment Check
    failed = check_issue_alignment(failed)
    
    print("==========================================================")
    if not failed:
        print(color("Workspace Status: VALIDATED", C_GREEN + C_BOLD))
        sys.exit(0)
    else:
        print(color("Workspace Status: DEGRADED (Check issues detailed above)", C_RED + C_BOLD))
        sys.exit(1)

def check_hardcoded_credentials(failed_flag):
    print("Check 3: Hardcoded Credentials Scan (excluding .agents/ and .git/)")
    secret_found = False
    
    files_to_scan = get_files_to_scan()
    patterns = ["apikey", "api_key", "secret", "password", "passwd", "private_key", "jwt_secret"]
    
    regexes = [re.compile(rf"{pat}\s*=\s*['\"][a-zA-Z0-9_\-\.]{{8,}}['\"]", re.IGNORECASE) for pat in patterns]
    
    for path in files_to_scan:
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                for idx, line in enumerate(f, 1):
                    for r, pat in zip(regexes, patterns):
                        if r.search(line):
                            print(f"  [FAIL] Potential hardcoded credential found for pattern '{pat}':")
                            print(f"    {path}:{idx}: {line.strip()}")
                            secret_found = True
                    if "BEGIN PRIVATE KEY" in line:
                        print(f"  [FAIL] Hardcoded Private Key Block found:")
                        print(f"    {path}:{idx}: {line.strip()}")
                        secret_found = True
        except Exception:
            pass
            
    if secret_found:
        return True
    print("  [PASS] No hardcoded credentials detected in scan scope.")
    return failed_flag

def check_raw_env():
    print("Check 4: Raw Environment Access Scan (domain-purity verification)")
    raw_env_found = False
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in {'.git', '.agents', 'venv', 'env', 'node_modules', 'dist', 'vendor', 'out', 'target'}]
        for f in files:
            path = os.path.join(root, f)
            path_lower = path.lower()
            if "config" in path_lower or "test" in path_lower:
                continue
                
            ext = os.path.splitext(f)[1]
            if ext in ('.js', '.ts', '.tsx'):
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as file_obj:
                        for idx, line in enumerate(file_obj, 1):
                            if re.search(r'process\.env\.[A-Za-z0-9_]', line):
                                print(f"  [WARNING] Raw 'process.env' access found outside configuration modules:")
                                print(f"    {path}:{idx}: {line.strip()}")
                                raw_env_found = True
                except Exception:
                    pass
            elif ext == '.go':
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as file_obj:
                        for idx, line in enumerate(file_obj, 1):
                            if 'os.Getenv' in line:
                                print(f"  [WARNING] Raw 'os.Getenv' access found outside configuration modules:")
                                print(f"    {path}:{idx}: {line.strip()}")
                                raw_env_found = True
                except Exception:
                    pass
            elif ext == '.py':
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as file_obj:
                        for idx, line in enumerate(file_obj, 1):
                            if re.search(r'os\.(environ|getenv|environ\.get)\b', line):
                                print(f"  [WARNING] Raw 'os.environ/os.getenv' access found outside configuration modules:")
                                print(f"    {path}:{idx}: {line.strip()}")
                                raw_env_found = True
                except Exception:
                    pass
                    
    if not raw_env_found:
        print("  [PASS] Domain isolation looks healthy (no scattered raw env reads).")

def check_git_upstream(failed_flag):
    print("Check 5: Git Upstream Synchronization Check")
    
    try:
        remotes = subprocess.check_output(["git", "remote"], stderr=subprocess.DEVNULL).decode().split()
    except Exception:
        print("  [WARNING] No upstream tracking branch set or Git repository not initialized.")
        return failed_flag
        
    if "origin" in remotes:
        try:
            subprocess.run(
                ["git", "fetch", "origin"],
                timeout=5,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception:
            pass
            
    try:
        local_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
        remote_commit = subprocess.check_output(["git", "rev-parse", "@{u}"], stderr=subprocess.DEVNULL).decode().strip()
        base_commit = subprocess.check_output(["git", "merge-base", "HEAD", "@{u}"], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        print("  [WARNING] No upstream tracking branch set or Git repository not initialized.")
        return failed_flag
        
    if local_commit == remote_commit:
        print("  [PASS] Local branch is up-to-date with upstream.")
    elif local_commit == base_commit:
        print("  [FAIL] Workspace is behind upstream! Run 'git pull' before letting the agent modify files.")
        return True
    elif remote_commit == base_commit:
        print("  [PASS] Local branch is ahead of upstream (unpushed commits).")
    else:
        print("  [FAIL] Workspace has diverged from upstream! Please reconcile branches before modifying files.")
        return True
    return failed_flag

def check_schema_registration(failed_flag):
    print("Check 6: Schema Index Registration Compliance")
    schema_errors = 0
    schema_index = ".agents/schema.md"
    schemas_dir = ".agents/schemas"
    
    if not os.path.exists(schema_index):
        print("  [FAIL] Primary schema index '.agents/schema.md' is missing!")
        return True
        
    try:
        with open(schema_index, 'r', encoding='utf-8') as f:
            schema_content = f.read()
    except Exception:
        schema_content = ""
        
    if os.path.exists(schemas_dir) and os.path.isdir(schemas_dir):
        for f in os.listdir(schemas_dir):
            if f.endswith('.md'):
                if f not in schema_content:
                    print(f"  [FAIL] Domain schema file '{f}' is NOT registered in '.agents/schema.md'!")
                    schema_errors += 1
                    
    if schema_errors > 0:
        return True
    print("  [PASS] All domain schemas are correctly indexed.")
    return failed_flag

def check_gitignore_compliance(failed_flag):
    print("Check 7: Gitignore & Antigravityignore Compliance")
    gitignore_errors = 0
    
    gitignore_path = ".gitignore"
    transients = [
        ".agents/locks/",
        ".agents/api_keys",
        ".agents/active_api_keys",
        ".agents/active_api_keys.ps1",
        ".agents/active_api_profile_name",
        ".agents/cooldowns.json"
    ]
    
    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                gi_content = f.read()
                gi_lines = gi_content.splitlines()
        except Exception:
            gi_content = ""
            gi_lines = []
            
        for line in gi_lines:
            clean = line.strip()
            if re.match(r'^\.agents/?$', clean):
                print("  [FAIL] .gitignore ignores '.agents/' folder globally! Please remove it.")
                gitignore_errors += 1
            if clean == "AGENTS.md":
                print("  [FAIL] .gitignore ignores 'AGENTS.md'! Please remove it.")
                gitignore_errors += 1
                
        healed = False
        with open(gitignore_path, 'a', encoding='utf-8') as f:
            for t in transients:
                ignored = False
                for line in gi_lines:
                    clean = line.strip()
                    if clean == t or clean == t.rstrip('/'):
                        ignored = True
                        break
                if not ignored:
                    print(f"  [WARNING] .gitignore does not ignore transient: '{t}'. Auto-healing...")
                    f.write(f"\n{t}\n")
                    healed = True
        if healed:
            print("  [PASS] .gitignore auto-healed successfully.")
    else:
        print("  [WARNING] No .gitignore file found in project root.")
        
    ag_path = ".antigravityignore"
    if os.path.exists(ag_path):
        try:
            with open(ag_path, 'r', encoding='utf-8') as f:
                ag_content = f.read()
                ag_lines = ag_content.splitlines()
        except Exception:
            ag_content = ""
            ag_lines = []
            
        healed = False
        with open(ag_path, 'a', encoding='utf-8') as f:
            for t in transients:
                ignored = False
                for line in ag_lines:
                    clean = line.strip()
                    if clean == t or clean == t.rstrip('/'):
                        ignored = True
                        break
                if not ignored:
                    print(f"  [WARNING] .antigravityignore does not ignore transient: '{t}'. Auto-healing...")
                    f.write(f"\n{t}\n")
                    healed = True
        if healed:
            print("  [PASS] .antigravityignore auto-healed successfully.")
            
    if gitignore_errors > 0:
        return True
    print("  [PASS] Gitignore & Antigravityignore configurations are validated.")
    return failed_flag

def check_memory_state_flag(failed_flag):
    print("Check 8: Memory State Flag Enforcement")
    state_errors = 0
    try:
        current_branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        current_branch = "detached"
        
    if current_branch in ("main", "master"):
        memory_file = utils.get_memory_file()
        if os.path.exists(memory_file):
            try:
                with open(memory_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                if "- **State Flag**:" in content or "- State Flag:" in content:
                    m = re.search(r'-\s*\*\*State Flag\*\*:\s*`?COMPLETED`?', content, re.IGNORECASE)
                    if not m:
                        print(f"  [FAIL] Commit rejected on branch '{current_branch}' because State Flag is not 'COMPLETED'!")
                        print("         Please complete your tasks and update memory.md State Flag to 'COMPLETED' first.")
                        state_errors += 1
            except Exception:
                pass
        else:
            print("  [FAIL] Memory file does not exist!")
            state_errors += 1
    else:
        print(f"  [PASS] Memory state flag checks bypassed on local feature branch '{current_branch}'.")
        
    if state_errors > 0:
        return True
    if current_branch in ("main", "master"):
        print("  [PASS] Memory state flag is 'COMPLETED' for production commit.")
    return failed_flag

def check_token_budget(failed_flag):
    print("Check 9: Token Budget Guard")
    budget_file = ".agents/token_budget.json"
    if not os.path.exists(budget_file):
        print("  [PASS] No active token budget file or jq tool found. Bypassing check.")
        return failed_flag
        
    try:
        budget = utils.load_budget()
    except Exception:
        print("  [PASS] No active token budget file or jq tool found. Bypassing check.")
        return failed_flag
        
    active_profile = ""
    profile_path = ".agents/active_api_profile_name"
    if os.path.exists(profile_path):
        try:
            with open(profile_path, 'r') as f:
                active_profile = f.read().strip()
        except:
            pass
            
    profiles = budget.get("profiles", {})
    has_profile = active_profile and active_profile in profiles
    
    if has_profile:
        prof_data = profiles[active_profile]
        max_budget = prof_data.get("max_token_budget", 0)
        current_usage = prof_data.get("current_token_usage", 0)
        print(f"  Checking budget for active API profile: '{active_profile}'")
    else:
        max_budget = budget.get("max_token_budget", 0)
        current_usage = budget.get("current_token_usage", 0)
        print("  Checking global token budget")
        
    threshold = budget.get("alert_threshold_percent", 90)
    
    if max_budget > 0:
        percent = int(current_usage * 100 / max_budget)
        print(f"  Current token usage: {current_usage} / {max_budget} ({percent}%)")
        if current_usage >= max_budget:
            print(f"  [FAIL] Token budget exceeded! Current: {current_usage}, Limit: {max_budget}.")
            print("         Please save your task checkpoint in workflows/ and handover the task.")
            return True
        elif percent >= 95:
            print(f"  [FAIL] Token usage has reached critical threshold ({percent}% >= 95%)! All operations blocked.")
            print("         Please request a budget increase or manually reset the usage log.")
            return True
        elif percent >= threshold:
            print(f"  [WARNING] Token usage is at {percent}% of budget. Consider saving and handing over.")
        else:
            print("  [PASS] Token usage is within safe budget limits.")
    else:
        print("  [PASS] Token usage is within safe budget limits.")
        
    return failed_flag

def check_adr_compliance(failed_flag):
    print("Check 10: ADR Compliance Check")
    adr_errors = 0
    adr_index = ".agents/adr.md"
    adrs_dir = ".agents/adrs"
    
    if not os.path.exists(adr_index):
        print("  [FAIL] Primary ADR index '.agents/adr.md' is missing!")
        return True
        
    adr_content = ""
    try:
        with open(adr_index, 'r', encoding='utf-8') as f:
            adr_content = f.read()
    except Exception:
        adr_content = ""
        
    if os.path.exists(adrs_dir) and os.path.isdir(adrs_dir):
        max_num = 0
        adr_files = []
        for f in os.listdir(adrs_dir):
            if f.endswith('.md'):
                adr_files.append(f)
                
        for base_name in adr_files:
            adr_file_path = os.path.join(adrs_dir, base_name)
            
            if base_name not in adr_content:
                print(f"  [FAIL] Architectural Decision Record file '{base_name}' is NOT registered in '.agents/adr.md'!")
                adr_errors += 1
                
            try:
                with open(adr_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                content = ""
                
            placeholders = ["TODO", "FIXME", "[placeholder]", "Describe the problem", "Describe the decision", "Describe the result"]
            if any(p in content for p in placeholders):
                print(f"  [FAIL] ADR file '{base_name}' contains placeholder text (TODO/FIXME/placeholder/template default)!")
                adr_errors += 1
                
            if "## Context" not in content or "## Decision" not in content or "## Consequences" not in content:
                print(f"  [FAIL] ADR file '{base_name}' is missing required sections (Context, Decision, Consequences)!")
                adr_errors += 1
                
            m = re.match(r'^([0-9]{3})-', base_name)
            if m:
                num = int(m.group(1))
                if num > max_num:
                    max_num = num
                    
        if max_num > 0:
            for i in range(1, max_num + 1):
                padded_num = f"{i:03d}"
                found = False
                for f in adr_files:
                    if f.startswith(f"{padded_num}-"):
                        found = True
                        break
                if not found:
                    print(f"  [FAIL] Missing ADR in sequence: ADR-{padded_num} is not found!")
                    adr_errors += 1
                    
        links = re.findall(r'file://\./adrs/([^)]+\.md)', adr_content)
        for link in links:
            link_path = os.path.join(adrs_dir, link)
            if not os.path.exists(link_path):
                print(f"  [FAIL] ADR index references non-existent file '.agents/adrs/{link}'!")
                adr_errors += 1
    else:
        print("  [FAIL] ADR directory is missing!")
        adr_errors += 1
                
    if adr_errors == 0:
        print("  [PASS] All Architectural Decision Records are correctly indexed and complete.")
    else:
        return True
    return failed_flag

def check_git_profile_compliance(failed_flag):
    print("Check 11: Git Configuration & Profile Compliance")
    git_errors = 0
    profiles_file = ".agents/git_profiles"
    
    placeholders = {"work@company.com", "personal@gmail.com", "side@project.com"}
    
    if os.path.exists(profiles_file):
        try:
            with open(profiles_file, 'r', encoding='utf-8') as f:
                for line in f:
                    clean = line.strip()
                    if not clean or clean.startswith('#'):
                        continue
                    if '=' in clean:
                        k, v = clean.split('=', 1)
                        k = k.strip()
                        v = v.strip()
                        
                        m = re.match(r'^([a-zA-Z0-9_\-]+)\.(name|email|ssh_key)$', k)
                        if m:
                            key = m.group(1)
                            prop = m.group(2)
                            
                            if prop == "email" and v in placeholders:
                                print(f"  [WARNING] Profile '{key}' uses a default template email: '{v}'.")
                            elif prop == "ssh_key" and v:
                                resolved_key = os.path.expanduser(v)
                                if not os.path.exists(resolved_key):
                                    print(f"  [WARNING] Profile '{key}' specifies an SSH key file that does not exist: '{v}'.")
        except Exception:
            pass
            
    try:
        local_email = subprocess.check_output(["git", "config", "--local", "user.email"], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        local_email = ""
        
    if local_email in placeholders:
        print(f"  [WARNING] Local Git config user.email uses a placeholder email: '{local_email}'.")
        
    if git_errors > 0:
        return True
    print("  [PASS] Git configurations and profiles are validated.")
    return failed_flag

def check_api_profile_compliance(failed_flag):
    print("Check 12: API Configuration & Profile Compliance")
    api_errors = 0
    api_keys_file = ".agents/api_keys"
    
    if os.path.exists(api_keys_file):
        try:
            with open(api_keys_file, 'r', encoding='utf-8') as f:
                for line in f:
                    clean = line.strip()
                    if not clean or clean.startswith('#'):
                        continue
                    if '=' in clean:
                        k, v = clean.split('=', 1)
                        k = k.strip()
                        v = v.strip()
                        
                        m = re.match(r'^([a-zA-Z0-9_\-]+)\.([A-Z0-9_]+)$', k)
                        if m:
                            key = m.group(1)
                            prop = m.group(2)
                            if v == "your_api_key_here" or v.endswith('_key_here'):
                                print(f"  [WARNING] API Profile '{key}' uses a placeholder value for '{prop}': '{v}'.")
                        else:
                            print(f"  [FAIL] Invalid syntax in {api_keys_file}: '{clean}'. Must be in format: profile.VARIABLE_NAME=value")
                            api_errors += 1
        except Exception:
            pass
            
    gitignore_path = ".gitignore"
    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                gi_content = f.read()
        except Exception:
            gi_content = ""
            
        for pattern in (".agents/api_keys", ".agents/active_api_keys", ".agents/active_api_keys.ps1", ".agents/active_api_profile_name"):
            if pattern not in gi_content:
                print(f"  [FAIL] .gitignore compliance: '{pattern}' is not ignored. Please add it to your .gitignore to protect credentials.")
                api_errors += 1
                
    if api_errors > 0:
        return True
    print("  [PASS] API configurations and profiles are validated and secure.")
    return failed_flag

def check_changelog(failed_flag):
    print("Check 13: Keep a Changelog Compliance")
    changelog_errors = 0
    changelog_path = "CHANGELOG.md"
    
    if os.path.exists(changelog_path):
        try:
            with open(changelog_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                f.seek(0)
                content = f.read()
        except Exception:
            first_line = ""
            content = ""
            
        if not first_line.startswith("# Changelog"):
            print("  [FAIL] CHANGELOG.md must start with '# Changelog' header.")
            changelog_errors += 1
            
        for line in content.splitlines():
            if line.startswith("## "):
                m = re.match(r'^## \[(Unreleased|\d+\.\d+\.\d+)\]( - \d{4}-\d{2}-\d{2})?$', line)
                if not m:
                    print(f"  [FAIL] CHANGELOG.md contains invalid version header: '{line}'")
                    changelog_errors += 1
    else:
        print("  [WARNING] No CHANGELOG.md file found in project root.")
        
    if changelog_errors > 0:
        return True
    print("  [PASS] CHANGELOG.md matches Keep a Changelog compliance.")
    return failed_flag

def check_staged_todo(failed_flag):
    print("Check 14: Staged Code Quality (TODO/FIXME Guard)")
    todo_errors = 0
    
    try:
        subprocess.check_call(["git", "rev-parse", "--is-inside-work-tree"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        print("  [PASS] Staged changes contain no TODO or FIXME annotations.")
        return failed_flag
        
    try:
        staged_files = subprocess.check_output(["git", "diff", "--cached", "--name-only"]).decode().splitlines()
    except Exception:
        staged_files = []
        
    for f in staged_files:
        if f.endswith('.md') or f == 'bootstrap.sh' or f.startswith('.agents/'):
            continue
            
        if os.path.exists(f):
            try:
                diff_output = subprocess.check_output(["git", "diff", "--cached", "--", f]).decode(errors='ignore')
                for line in diff_output.splitlines():
                    if line.startswith('+') and not line.startswith('++'):
                        if re.search(r'\b(TODO|FIXME)\b', line, re.IGNORECASE):
                            print(f"  [FAIL] Quality Guard: Staged file '{f}' contains TODO or FIXME annotations:")
                            print(f"         {line}")
                            todo_errors += 1
            except Exception:
                pass
                
    if todo_errors > 0:
        return True
    print("  [PASS] Staged changes contain no TODO or FIXME annotations.")
    return failed_flag

def check_staged_transient(failed_flag):
    print("Check 15: Staged Transient Files & Leak Guard")
    leak_errors = 0
    
    try:
        subprocess.check_call(["git", "rev-parse", "--is-inside-work-tree"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        staged_files = subprocess.check_output(["git", "diff", "--cached", "--name-only"]).decode().splitlines()
    except Exception:
        staged_files = []
        
    for f in staged_files:
        if f.endswith('.lock') or 'active_api_keys' in f or f.endswith('cooldowns.json'):
            print(f"  [FAIL] Leak Guard: Transient file '{f}' is staged for commit! Please unstage it.")
            leak_errors += 1
            
    if leak_errors > 0:
        return True
    print("  [PASS] No transient files or credentials are staged.")
    return failed_flag

def check_local_issues(failed_flag):
    print("Check 16: Local Workspace Issues Validation")
    issue_errors = 0
    issues_dir = ".agents/issues"
    
    if os.path.exists(issues_dir) and os.path.isdir(issues_dir):
        for f in os.listdir(issues_dir):
            if f.startswith('issue_') and f.endswith('.md'):
                path = os.path.join(issues_dir, f)
                
                try:
                    with open(path, 'r', encoding='utf-8') as file_obj:
                        lines = file_obj.readlines()
                except Exception:
                    lines = []
                    
                if not lines:
                    print(f"  [FAIL] Issue file '{f}' is empty!")
                    issue_errors += 1
                    continue
                    
                if lines[0].strip() != "---":
                    print(f"  [FAIL] Issue file '{f}' does not start with YAML frontmatter delimiter '---'!")
                    issue_errors += 1
                    continue
                    
                closing_idx = -1
                for idx, line in enumerate(lines[1:], 1):
                    if line.strip() == "---":
                        closing_idx = idx
                        break
                        
                if closing_idx == -1:
                    print(f"  [FAIL] Issue file '{f}' is missing closing YAML frontmatter delimiter '---'!")
                    issue_errors += 1
                    continue
                    
                frontmatter_lines = lines[1:closing_idx]
                frontmatter = {}
                for line in frontmatter_lines:
                    if ':' in line:
                        k, v = line.split(':', 1)
                        frontmatter[k.strip()] = v.strip().strip('"\'')
                        
                required_keys = ["id", "title", "status", "created_at", "closed_at"]
                for key in required_keys:
                    if key not in frontmatter:
                        print(f"  [FAIL] Issue file '{f}' is missing required frontmatter field '{key}:'!")
                        issue_errors += 1
                        
                status_val = frontmatter.get("status", "").lower()
                if status_val not in ("open", "closed"):
                    print(f"  [FAIL] Issue file '{f}' has invalid status value '{status_val}' (must be 'open' or 'closed')!")
                    issue_errors += 1
                    
    if issue_errors > 0:
        return True
    print("  [PASS] All local issue files are validated and compliant.")
    return failed_flag

def check_base_branch_modification(failed_flag):
    print("Check 17: Base Branch Modification Check")
    # Check if a merge is in progress (bypasses branch/lock checks)
    is_merging = False
    try:
        git_dir = subprocess.check_output(["git", "rev-parse", "--git-dir"], stderr=subprocess.DEVNULL).decode().strip()
        if os.path.exists(os.path.join(git_dir, "MERGE_HEAD")):
            is_merging = True
    except Exception:
        pass
        
    if is_merging:
        print("  [PASS] Merge commit in progress. Bypassing check.")
        return failed_flag

    try:
        current_branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        current_branch = "detached"
        
    if current_branch in ("main", "master"):
        # Check for modified or untracked code files (excluding .agents/, .git/, and metadata files)
        try:
            status_output = subprocess.check_output(["git", "status", "--porcelain"], stderr=subprocess.DEVNULL).decode()
        except Exception:
            status_output = ""
            
        unauthorized_files = []
        for line in status_output.splitlines():
            if not line.strip():
                continue
            # Format is XY filepath or XY "filepath"
            filepath = line[3:].strip().strip('"\'')
            
            # Exclude metadata / config / lock files
            if filepath.startswith('.agents/') or filepath.startswith('.git/'):
                continue
            ext = os.path.splitext(filepath)[1]
            if ext in ('.md', '.json', '.txt', '.yml', '.yaml', '.lock') or filepath in ('.gitignore', '.antigravityignore'):
                continue
                
            unauthorized_files.append(filepath)
            
        if unauthorized_files:
            print(f"  {color('[FAIL]', C_RED + C_BOLD)} Unauthorized code modifications found directly on base branch '{current_branch}':")
            for uf in unauthorized_files:
                print(f"    - {uf}")
            print("         Please run './.agents/scripts/helper.sh issue checkout <id>' to work in an isolated feature branch.")
            return True
            
    print("  [PASS] Base branch check passed (no direct modifications on main/master).")
    return failed_flag

def check_module_locking(failed_flag):
    print("Check 18: Staged/Modified Files Module Locking Check")
    # Check if a merge is in progress (bypasses branch/lock checks)
    is_merging = False
    try:
        git_dir = subprocess.check_output(["git", "rev-parse", "--git-dir"], stderr=subprocess.DEVNULL).decode().strip()
        if os.path.exists(os.path.join(git_dir, "MERGE_HEAD")):
            is_merging = True
    except Exception:
        pass
        
    if is_merging:
        print("  [PASS] Merge commit in progress. Bypassing check.")
        return failed_flag

    try:
        status_output = subprocess.check_output(["git", "status", "--porcelain"], stderr=subprocess.DEVNULL).decode()
    except Exception:
        status_output = ""
        
    modified_files = []
    for line in status_output.splitlines():
        if not line.strip():
            continue
        filepath = line[3:].strip().strip('"\'')
        
        # Normalize and filter
        filepath = filepath.replace('\\', '/')
        if filepath.startswith('.agents/') or filepath.startswith('.git/'):
            continue
        ext = os.path.splitext(filepath)[1]
        if ext in ('.md', '.json', '.txt', '.yml', '.yaml', '.lock') or filepath in ('.gitignore', '.antigravityignore'):
            continue
            
        modified_files.append(filepath)
        
    if not modified_files:
        print("  [PASS] No modified files require locking.")
        return failed_flag
        
    # Get active locks
    locks_dir = os.path.join(utils.get_agents_dir(), "locks")
    active_locks = set()
    if os.path.exists(locks_dir) and os.path.isdir(locks_dir):
        for f in os.listdir(locks_dir):
            if f.endswith('.lock'):
                active_locks.add(os.path.splitext(f)[0])
                
    unlock_errors = 0
    for f in modified_files:
        # Map file to module lock name
        if '/' not in f:
            req_lock = 'root'
        else:
            req_lock = f.split('/')[0]
            
        if req_lock not in active_locks:
            print(f"  {color('[FAIL]', C_RED + C_BOLD)} File '{f}' is modified but module '{req_lock}' is not locked!")
            print(f"         Please acquire a lock first: './.agents/scripts/helper.sh lock {req_lock}'")
            unlock_errors += 1
            
    if unlock_errors > 0:
        return True
        
    print("  [PASS] All modified files are properly locked.")
    return failed_flag

def check_issue_alignment(failed_flag):
    print("Check 19: Issue Branch and Memory Alignment Check")
    try:
        current_branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        current_branch = "detached"
        
    # Check if branch name matches issue-<id>-<slug>
    m = re.match(r'^issue-(\d+)-(.+)$', current_branch)
    if not m:
        print("  [PASS] Not on an issue feature branch. Skipping alignment check.")
        return failed_flag
        
    issue_id = int(m.group(1))
    issues_dir = os.path.join(utils.get_agents_dir(), "issues")
    filename = f"issue_{issue_id:03d}.md"
    file_path = os.path.join(issues_dir, filename)
    
    if not os.path.exists(file_path):
        print(f"  {color('[FAIL]', C_RED + C_BOLD)} Branch '{current_branch}' references non-existent issue #{issue_id}!")
        return True
        
    # Parse title from issue
    title = ""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('title:'):
                    title = line.split(':', 1)[1].strip().strip('"\'')
                    break
    except Exception:
        pass
        
    memory_file = utils.get_memory_file()
    if not os.path.exists(memory_file):
        print(f"  {color('[FAIL]', C_RED + C_BOLD)} Memory file 'memory.md' is missing!")
        return True
        
    try:
        with open(memory_file, 'r', encoding='utf-8') as f:
            mem_content = f.read()
    except Exception:
        mem_content = ""
        
    alignment_errors = 0
    
    # Verify State Flag is IN_PROGRESS or COMPLETED
    if not re.search(r'-\s*\*\*State Flag\*\*:\s*`?(IN_PROGRESS|COMPLETED)`?', mem_content, re.IGNORECASE):
        print(f"  {color('[FAIL]', C_RED + C_BOLD)} memory.md State Flag must be 'IN_PROGRESS' or 'COMPLETED' on issue branch!")
        alignment_errors += 1
        
    # Verify Current Task Target contains the issue title or ID
    expected_target_pat = f"issue #{issue_id}"
    if expected_target_pat not in mem_content.lower() and (title.lower() not in mem_content.lower() if title else True):
        print(f"  {color('[FAIL]', C_RED + C_BOLD)} memory.md Current Task Target is not aligned with issue #{issue_id}!")
        alignment_errors += 1
        
    # Verify issue task checklist is present
    if f"issue #{issue_id}:" not in mem_content.lower():
        print(f"  {color('[FAIL]', C_RED + C_BOLD)} memory.md checklist is missing a task for issue #{issue_id}!")
        alignment_errors += 1
        
    if alignment_errors > 0:
        return True
        
    print(f"  [PASS] Branch '{current_branch}' is fully aligned with memory.md.")
    return failed_flag
