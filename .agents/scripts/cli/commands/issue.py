import sys
import os
import re

# Inject parent directory containing git_api
scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)
import subprocess
from datetime import datetime

ISSUE_DIR = ".agents/issues"

def parse_issue_frontmatter(content):
    """Parse YAML-like frontmatter between --- boundaries."""
    lines = content.splitlines()
    fm = {}
    if len(lines) > 0 and lines[0].strip() == '---':
        fm_lines = []
        for line in lines[1:]:
            if line.strip() == '---':
                break
            fm_lines.append(line)
        for line in fm_lines:
            if ':' in line:
                k, v = line.split(':', 1)
                k = k.strip()
                v = v.strip()
                # Strip surrounding quotes
                if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                    v = v[1:-1]
                fm[k] = v
    return fm

def get_issue_tasks(content):
    """
    Extract checklist tasks under specific sections (Tasks, Subtasks, Criteria).
    Returns (all_tasks, unchecked_tasks) as lists of task lines.
    """
    lines = content.splitlines()
    all_tasks = []
    unchecked = []
    in_relevant_section = False
    
    for line in lines:
        striped = line.strip()
        if striped.startswith('##'):
            # Check if this is a tasks or acceptance criteria section
            lower_header = striped.lower()
            if 'task' in lower_header or 'subtask' in lower_header or 'criteria' in lower_header:
                in_relevant_section = True
            else:
                in_relevant_section = False
        elif in_relevant_section:
            if striped.startswith(('-', '*')) and '[' in striped and ']' in striped:
                match = re.match(r'^[-*]\s*\[\s*([xX\s/])\s*\]\s+(.*)', striped)
                if match:
                    all_tasks.append(striped)
                    if match.group(1).strip() == '':
                        unchecked.append(striped)
    return all_tasks, unchecked

def update_board_completed(issue_id):
    board_path = ".agents/tasks/board.md"
    if not os.path.exists(board_path):
        return
    try:
        with open(board_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.splitlines()
        target_line = None
        new_lines = []
        
        pattern = rf"<!-- id:\s*{re.escape(issue_id)}\s*-->"
        for line in lines:
            if re.search(pattern, line):
                target_line = line
            else:
                new_lines.append(line)
                
        if target_line:
            # Change unchecked or doing to checked
            target_line = re.sub(r'\[\s*\]', '[x]', target_line)
            target_line = re.sub(r'\[\s*[xX]\s*\]', '[x]', target_line)
            target_line = re.sub(r'\[\s*/\s*\]', '[x]', target_line)
            
            # Find ## Done line
            done_idx = -1
            for idx, line in enumerate(new_lines):
                if line.strip() == "## Done":
                    done_idx = idx
                    break
            
            if done_idx != -1:
                new_lines.insert(done_idx + 1, target_line)
            else:
                new_lines.append(target_line)
                
            with open(board_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(new_lines) + "\n")
            print(f"[OK] Moved task '{issue_id}' to Done in task board.")
    except Exception as e:
        print(f"Warning: Could not update task board: {e}")

def sync_issues():
    """Fetch remote issues and synchronize status/existence with local markdown files."""
    try:
        import git_api
        remote_issues = git_api.fetch_github_issues()
        if not remote_issues:
            print("[INFO] Operating in local offline mode using local issue cache.")
            return
            
        print("[INFO] Synchronizing local issues with GitHub remote...")
        if not os.path.exists(ISSUE_DIR):
            os.makedirs(ISSUE_DIR, exist_ok=True)
            
        # Parse all local issues to build a map of {github_number: file_path}
        local_issues = {}
        for f_name in os.listdir(ISSUE_DIR):
            if not f_name.endswith(".md") or "example" in f_name:
                continue
            path = os.path.join(ISSUE_DIR, f_name)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                fm = parse_issue_frontmatter(content)
                if "github_number" in fm:
                    local_issues[int(fm["github_number"])] = path
            except Exception:
                pass
                
        for issue in remote_issues:
            # Skip pull requests
            if "pull_request" in issue:
                continue
                
            number = issue.get("number")
            title = issue.get("title", "")
            state = issue.get("state", "open")
            html_url = issue.get("html_url", "")
            body = issue.get("body", "") or ""
            
            if number in local_issues:
                # Update status if mismatched
                path = local_issues[number]
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    fm = parse_issue_frontmatter(content)
                    current_status = fm.get("status")
                    if current_status and current_status != state:
                        content = re.sub(r'status:\s*' + re.escape(current_status), f'status: {state}', content)
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"[OK] Updated local issue #{number} status to '{state}'.")
                except Exception:
                    pass
            else:
                # Create a new local issue file
                issue_id = f"issue-{number}"
                file_path = os.path.join(ISSUE_DIR, f"issue_{number}.md")
                current_date = datetime.now().strftime("%Y-%m-%d")
                
                template = f"""---
id: {issue_id}
title: "{title}"
status: {state}
assignee: agent-antigravity
created_at: {current_date}
github_url: "{html_url}"
github_number: {number}
---

# Issue Details

## Problem Statement
{body}

## Tasks
- [ ] Implement remote synchronization fixes

## Acceptance Criteria
- [ ] Verification complete
"""
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(template)
                    print(f"[OK] Pulled new remote issue #{number} as local file '{file_path}'.")
                except Exception:
                    pass
    except Exception as e:
        print(f"[WARN] Issue synchronization failed: {e}", file=sys.stderr)

def push_offline_issues():
    """Find local issues without a github_number and push them to GitHub remote."""
    if not os.path.exists(ISSUE_DIR):
        return
        
    import git_api
    pat = git_api.get_pat()
    repo = git_api.get_repo_info()
    if not pat or not repo:
        return
        
    print("[INFO] Auditing local issues for offline creations...")
    for f_name in os.listdir(ISSUE_DIR):
        if not f_name.endswith(".md") or "example" in f_name:
            continue
        path = os.path.join(ISSUE_DIR, f_name)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            fm = parse_issue_frontmatter(content)
            github_number = fm.get("github_number")
            github_url = fm.get("github_url")
            issue_id = fm.get("id")
            title = fm.get("title")
            
            # If it doesn't have a remote number and has a valid ID/title
            if not github_number and issue_id and title:
                print(f"[INFO] Pushing local issue '{issue_id}' to GitHub remote...")
                res = git_api.create_github_issue(title, f"Local tracking ID: {issue_id}")
                if res:
                    url, number = res
                    # Update local issue file frontmatter by inserting right before the second ---
                    lines = content.splitlines()
                    boundary_indices = [idx for idx, line in enumerate(lines) if line.strip() == '---']
                    if len(boundary_indices) >= 2:
                        insert_idx = boundary_indices[1]
                        lines.insert(insert_idx, f"github_url: \"{url}\"")
                        lines.insert(insert_idx + 1, f"github_number: {number}")
                        new_content = "\n".join(lines) + "\n"
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"[OK] Successfully linked local issue '{issue_id}' to remote GitHub issue #{number}.")
        except Exception as e:
            print(f"[WARN] Failed to push local issue '{f_name}': {e}", file=sys.stderr)

def get_issue_path(issue_id):
    normalized = issue_id.lower().replace('-', '_')
    if not os.path.exists(ISSUE_DIR):
        os.makedirs(ISSUE_DIR, exist_ok=True)
    # 1. Search in active issues dir first
    for f in os.listdir(ISSUE_DIR):
        if normalized in f.lower().replace('-', '_') or issue_id.lower() in f.lower():
            return os.path.join(ISSUE_DIR, f)
    # 2. Search in archive issues dir as fallback
    archive_dir = ".agents/archive/issues"
    if os.path.exists(archive_dir):
        for f in os.listdir(archive_dir):
            if normalized in f.lower().replace('-', '_') or issue_id.lower() in f.lower():
                return os.path.join(archive_dir, f)
    # 3. Fallback path if not found anywhere
    suffix = normalized.split('_')[-1]
    return os.path.join(ISSUE_DIR, f"issue_{suffix}.md")

def run(args):
    if len(args) == 0:
        print("Usage: helper.py issue <create|list|checkout|close|sync> [args...]")
        sys.exit(1)
        
    action = args[0].lower()
    
    if action == "create":
        cli_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if cli_dir not in sys.path:
            sys.path.insert(0, cli_dir)
        from interactive import prompt_input
        
        issue_id = None
        title = None
        
        if len(args) >= 2:
            issue_id = args[1]
        else:
            files = [f for f in os.listdir(ISSUE_DIR) if f.endswith(".md") and "example" not in f]
            max_num = 0
            for f in files:
                m = re.search(r'issue_(\d+)\.md', f)
                if m:
                    max_num = max(max_num, int(m.group(1)))
            default_id = f"issue-{max_num + 1:03d}"
            issue_id = prompt_input("Enter issue ID", default=default_id)
            if not issue_id:
                print("\033[91mError: Issue ID is required.\033[0m")
                sys.exit(1)
                
        if len(args) >= 3:
            title = args[2]
        else:
            title = prompt_input("Enter issue title/description")
            if not title:
                print("\033[91mError: Issue title is required.\033[0m")
                sys.exit(1)
        if not os.path.exists(ISSUE_DIR):
            os.makedirs(ISSUE_DIR)
            
        file_path = get_issue_path(issue_id)
        if os.path.exists(file_path):
            print(f"Error: Issue file '{file_path}' already exists.")
            sys.exit(1)
            
        # Attempt to create remote GitHub issue
        github_url = ""
        github_number = ""
        try:
            import git_api
            res = git_api.create_github_issue(title, f"Local tracking ID: {issue_id}")
            if res:
                github_url, github_number = res
                print(f"Successfully created remote GitHub issue #{github_number}: {github_url}")
            else:
                print("Warning: Remote GitHub issue creation was bypassed (either token or git remote is missing).")
        except Exception as e:
            print(f"Warning: Could not create remote GitHub issue: {e}")

        current_date = datetime.now().strftime("%Y-%m-%d")
        github_fields = ""
        if github_url:
            github_fields = f"github_url: \"{github_url}\"\ngithub_number: {github_number}\n"

        template = f"""---
id: {issue_id}
title: "{title}"
status: open
assignee: agent-antigravity
created_at: {current_date}
{github_fields}---

# Issue Details

## Problem Statement
{title}

## Tasks
- [ ] Task 1

## Acceptance Criteria
- [ ] Criteria 1
"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(template)
        print(f"Successfully created issue file '{file_path}'.")
        
        # Auto-append to task board board.md
        board_path = ".agents/tasks/board.md"
        if os.path.exists(board_path):
            try:
                with open(board_path, 'r', encoding='utf-8') as f:
                    board_content = f.read()
                
                slug = issue_id.lower().replace('_', '-')
                branch_name = f"feat/{slug}"
                new_task_line = f"- [ ] {title} ({branch_name}) <!-- id: {issue_id} -->"
                
                lines = board_content.splitlines()
                updated_lines = []
                inserted = False
                for line in lines:
                    updated_lines.append(line)
                    if line.strip() == "## Todo" and not inserted:
                        updated_lines.append(new_task_line)
                        inserted = True
                
                with open(board_path, 'w', encoding='utf-8') as f:
                    f.write("\n".join(updated_lines) + "\n")
                print(f"[OK] Automatically added task '{issue_id}' to Todo in task board.")
            except Exception as e:
                print(f"Warning: Could not auto-append issue to task board: {e}")
        
    elif action == "list":
        if not os.path.exists(ISSUE_DIR):
            print("No issues directory found.")
            return
        files = [f for f in os.listdir(ISSUE_DIR) if f.endswith(".md")]
        if not files:
            print("No issues found.")
            return
            
        print("Issues registered:")
        for f_name in sorted(files):
            # Skip templates
            if "example" in f_name:
                continue
            path = os.path.join(ISSUE_DIR, f_name)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                fm = parse_issue_frontmatter(content)
                i_id = fm.get("id", f_name)
                i_title = fm.get("title", "No Title")
                i_status = fm.get("status", "unknown")
                
                # Count tasks
                all_tasks, unchecked = get_issue_tasks(content)
                res_str = f"({len(all_tasks) - len(unchecked)}/{len(all_tasks)} tasks)" if all_tasks else ""
                
                status_color = "\033[92m" if i_status == "open" else "\033[90m"
                reset = "\033[0m"
                print(f"  - {i_id}: {i_title} [{status_color}{i_status}{reset}] {res_str}")
            except Exception as e:
                print(f"  - Error reading {f_name}: {e}")
                
    elif action == "checkout":
        if len(args) < 2:
            files = [f for f in os.listdir(ISSUE_DIR) if f.endswith(".md") and "example" not in f]
            open_issues = []
            for f_name in sorted(files):
                path = os.path.join(ISSUE_DIR, f_name)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    fm = parse_issue_frontmatter(content)
                    i_status = fm.get("status", "unknown")
                    if i_status == "open":
                        open_issues.append({
                            "name": fm.get("id"),
                            "desc": fm.get("title", "No Title")
                        })
                except Exception:
                    pass
            if not open_issues:
                print("Error: No open issues found. Please create one first: './helper.sh issue create <id> \"<title>\"'")
                sys.exit(1)
            
            cli_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if cli_dir not in sys.path:
                sys.path.insert(0, cli_dir)
            from interactive import interactive_select
            
            selection = interactive_select(open_issues, title="Select an issue to check out:")
            if not selection:
                print("\033[93m[WARN] Checkout aborted.\033[0m")
                sys.exit(0)
            issue_id = selection.get("name")
        else:
            issue_id = args[1]
            
        path = get_issue_path(issue_id)
        if not os.path.exists(path):
            print(f"Error: Issue file not found for '{issue_id}'. Please run 'create' first.")
            sys.exit(1)
            
        # Determine branch name
        slug = issue_id.lower().replace('_', '-')
        branch_name = f"feat/{slug}"
        print(f"Checking out Git branch '{branch_name}'...")
        
        # Check if branch exists
        res_ref = subprocess.run(['git', 'show-ref', f'refs/heads/{branch_name}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res_ref.returncode == 0:
            subprocess.run(['git', 'checkout', branch_name])
        else:
            subprocess.run(['git', '-c', 'advice.detachedHead=false', 'checkout', '-b', branch_name])
        
    elif action == "close":
        if len(args) < 2:
            res_curr = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=subprocess.PIPE, text=True)
            current_branch = res_curr.stdout.strip()
            detected_id = None
            if current_branch.startswith("feat/") or current_branch.startswith("fix/"):
                detected_id = current_branch.split("/", 1)[1].replace('_', '-')
                
            files = [f for f in os.listdir(ISSUE_DIR) if f.endswith(".md") and "example" not in f]
            open_issues = []
            detected_issue_info = None
            for f_name in sorted(files):
                path = os.path.join(ISSUE_DIR, f_name)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    fm = parse_issue_frontmatter(content)
                    i_id = fm.get("id")
                    i_title = fm.get("title", "No Title")
                    i_status = fm.get("status", "unknown")
                    if i_status == "open":
                        issue_info = {"name": i_id, "desc": i_title}
                        open_issues.append(issue_info)
                        if detected_id and i_id.lower().replace('_', '-') == detected_id.lower():
                            detected_issue_info = issue_info
                except Exception:
                    pass
                    
            if not open_issues:
                print("Error: No open issues found to close.")
                sys.exit(0)
                
            cli_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if cli_dir not in sys.path:
                sys.path.insert(0, cli_dir)
            from interactive import interactive_select
            
            if detected_issue_info:
                title = f"Close active issue '{detected_issue_info['name']}'?"
                confirm_opts = [
                    {"name": "Yes, close it", "value": detected_issue_info["name"]},
                    {"name": "Select another open issue...", "value": "select_other"},
                    {"name": "Cancel", "value": "cancel"}
                ]
                sel = interactive_select(confirm_opts, title=title)
                if not sel or sel["value"] == "cancel":
                    print("\033[93m[WARN] Close aborted.\033[0m")
                    sys.exit(0)
                elif sel["value"] == "select_other":
                    sel_other = interactive_select(open_issues, title="Select an issue to close:")
                    if not sel_other:
                        print("\033[93m[WARN] Close aborted.\033[0m")
                        sys.exit(0)
                    issue_id = sel_other["name"]
                else:
                    issue_id = sel["value"]
            else:
                sel = interactive_select(open_issues, title="Select an open issue to close:")
                if not sel:
                    print("\033[93m[WARN] Close aborted.\033[0m")
                    sys.exit(0)
                issue_id = sel["name"]
        else:
            issue_id = args[1]
            
        path = get_issue_path(issue_id)
        if not os.path.exists(path):
            print(f"Error: Issue file not found for '{issue_id}'.")
            sys.exit(1)

        # Get current branch
        res_curr = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=subprocess.PIPE, text=True)
        current_branch = res_curr.stdout.strip()
        
        slug = issue_id.lower().replace('_', '-')
        possible_branches = [f"feat/{slug}", f"fix/{slug}"]
        
        found_branch = None
        for b in possible_branches:
            res_ref = subprocess.run(['git', 'show-ref', f'refs/heads/{b}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res_ref.returncode == 0:
                found_branch = b
                break

        if found_branch and current_branch != found_branch:
            print(f"Error: You are currently on branch '{current_branch}', but this issue is associated with branch '{found_branch}'.")
            print(f"Please checkout the feature branch first: git checkout {found_branch}")
            sys.exit(1)

        # 1. Run local validation checks before closing
        print("Triggering pre-close validation guard...")
        val_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../validate.py'))
        if os.path.exists(val_path):
            val_res = subprocess.run([sys.executable, val_path])
            if val_res.returncode != 0:
                print("Error: Validation guard failed. Issue close aborted.")
                sys.exit(1)

        # Trigger Auto-Lessons Extractor
        print("Triggering Auto-Lessons Extractor...")
        try:
            commands_dir = os.path.dirname(__file__)
            if commands_dir not in sys.path:
                sys.path.insert(0, commands_dir)
            import learn
            
            # Detect base branch dynamically
            base_branch = "main"
            res_master = subprocess.run(['git', 'show-ref', 'refs/heads/master'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res_master.returncode == 0:
                base_branch = "master"
                
            learn.suggest_and_record_lessons(base_branch)
        except Exception as e:
            print(f"Warning: Auto-Lessons Extractor failed: {e}")

        # Read issue file
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        fm = parse_issue_frontmatter(content)
        github_number = fm.get("github_number")
        if github_number:
            try:
                github_number = int(github_number)
                import git_api
                print(f"Closing remote GitHub issue #{github_number}...")
                git_api.close_github_issue(github_number)
            except Exception as e:
                print(f"Warning: Could not close remote GitHub issue: {e}")
            
        current_status = fm.get("status", "open")
        content = re.sub(r'status:\s*' + re.escape(current_status), 'status: closed', content)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully closed issue '{issue_id}' (updated file status).")

        # 2. Update task board
        update_board_completed(issue_id)

        # 3. Run SemVer changelog generator
        print("Running auto-changelog and SemVer version bump...")
        helper_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../helper.py'))
        changelog_res = subprocess.run([sys.executable, helper_path, 'changelog'])
        if changelog_res.returncode != 0:
            print("Warning: Changelog generator failed or was skipped.")

        # Run workspace sync to compile new lessons into rules
        print("Running workspace sync to compile new lessons into rules...")
        sync_res = subprocess.run([sys.executable, helper_path, 'sync'])
        if sync_res.returncode != 0:
            print("Warning: Workspace synchronization failed.")

        # Release locks held by this branch before staging final commit
        locks_file = ".agents/locks.json"
        if os.path.exists(locks_file):
            try:
                import json
                with open(locks_file, 'r', encoding='utf-8') as lf:
                    locks = json.load(lf)
                modified_locks = False
                for mod, holder in list(locks.items()):
                    if holder == found_branch:
                        del locks[mod]
                        modified_locks = True
                if modified_locks:
                    with open(locks_file, 'w', encoding='utf-8') as lf:
                        json.dump(locks, lf, indent=2)
                    print("[OK] Released module locks associated with the branch.")
            except Exception:
                pass

        # 4. Stage and commit release/board/issue files on feature branch
        if found_branch:
            print(f"Staging issue, board, and release changes on branch '{found_branch}'...")
            files_to_stage = [
                path,
                ".agents/tasks/board.md",
                "CHANGELOG.md",
                "AGENTS.md",
                "bootstrap.sh",
                "bootstrap.ps1",
                ".agents/scripts/cli/commands/bootstrap.py",
                "README.md",
                ".agents/scripts/cli/commands/issue.py",
                ".agents/memory/lessons-learned.md",
                ".agents/rules.md",
                ".agents/locks.json"
            ]
            for f_to_stage in files_to_stage:
                if os.path.exists(f_to_stage):
                    subprocess.run(['git', 'add', f_to_stage])

            commit_msg = f"chore(release): close {issue_id}, update task board, and bump version"
            print(f"Committing final changes to branch '{found_branch}'...")
            subprocess.run([
                sys.executable,
                helper_path,
                'commit',
                '-m', commit_msg,
                '-m', issue_id,
                '--no-verify'
            ])

            # 5. Merge and cleanup branch
            base_branch = "main"
            res_master = subprocess.run(['git', 'show-ref', 'refs/heads/master'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res_master.returncode == 0:
                base_branch = "master"

            print(f"Switching to base branch '{base_branch}'...")
            subprocess.run(['git', 'checkout', base_branch], check=True)

            print(f"Merging branch '{found_branch}' into '{base_branch}' with --no-ff...")
            merge_msg = f"chore(git): merge branch {found_branch}"
            merge_res = subprocess.run(['git', 'merge', found_branch, '--no-ff', '-m', merge_msg, '-m', issue_id])
            if merge_res.returncode != 0:
                print("Error: Git merge failed with conflict! Please resolve manually.")
                print(f"To abort the merge: git merge --abort && git checkout {found_branch}")
                sys.exit(1)

            print(f"Deleting branch '{found_branch}'...")
            subprocess.run(['git', 'branch', '-d', found_branch])

            # Locks were released and committed on the feature branch prior to base merge.
            print(f"[OK] Issue '{issue_id}' fully resolved and merged to '{base_branch}' successfully.")
        
    elif action == "sync":
        push_offline_issues()
        sync_issues()
        
    else:
        print(f"Error: Unknown action '{action}'. Available: create, list, checkout, close, sync")
        sys.exit(1)
