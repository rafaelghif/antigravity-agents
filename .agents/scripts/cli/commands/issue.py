import sys
import os
import re
import subprocess
from datetime import datetime

ISSUE_DIR = ".agents/issues"

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
            # Change unchecked to checked
            target_line = re.sub(r'\[\s*\]', '[x]', target_line)
            target_line = re.sub(r'\[\s*[xX]\s*\]', '[x]', target_line)
            
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
                m_num = re.search(r'github_number:\s*(\d+)', content)
                if m_num:
                    local_issues[int(m_num.group(1))] = path
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
                    m_status = re.search(r'status:\s*(.*?)\n', content)
                    if m_status:
                        current_status = m_status.group(1).strip()
                        if current_status != state:
                            content = re.sub(r'status:\s*' + current_status, f'status: {state}', content)
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

def get_issue_path(issue_id):
    normalized = issue_id.lower().replace('-', '_')
    if not os.path.exists(ISSUE_DIR):
        os.makedirs(ISSUE_DIR, exist_ok=True)
    for f in os.listdir(ISSUE_DIR):
        if normalized in f.lower().replace('-', '_') or issue_id.lower() in f.lower():
            return os.path.join(ISSUE_DIR, f)
    # Extract only digits/chars for standard suffix
    suffix = normalized.split('_')[-1]
    return os.path.join(ISSUE_DIR, f"issue_{suffix}.md")

def run(args):
    if len(args) == 0:
        print("Usage: helper.py issue <create|list|checkout|close|sync> [args...]")
        sys.exit(1)
        
    action = args[0].lower()
    
    if action == "create":
        if len(args) < 3:
            print("Usage: helper.py issue create <id> \"<title>\"")
            sys.exit(1)
        issue_id = args[1]
        title = args[2]
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
                    m_id = re.search(r'id:\s*(.*?)\n', content)
                    m_title = re.search(r'title:\s*"(.*?)"', content)
                    m_status = re.search(r'status:\s*(.*?)\n', content)
                    
                    i_id = m_id.group(1).strip() if m_id else f_name
                    i_title = m_title.group(1).strip() if m_title else "No Title"
                    i_status = m_status.group(1).strip() if m_status else "unknown"
                    
                    # Count tasks
                    all_tasks = re.findall(r'([-*]\s*\[\s*[xX ]\s*\]\s+.*)', content)
                    unchecked = re.findall(r'([-*]\s*\[\s+\]\s+.*)', content)
                    res_str = f"({len(all_tasks) - len(unchecked)}/{len(all_tasks)} tasks)" if all_tasks else ""
                    
                    status_color = "\033[92m" if i_status == "open" else "\033[90m"
                    reset = "\033[0m"
                    print(f"  - {i_id}: {i_title} [{status_color}{i_status}{reset}] {res_str}")
            except Exception as e:
                print(f"  - Error reading {f_name}: {e}")
                
    elif action == "checkout":
        if len(args) < 2:
            print("Usage: helper.py issue checkout <id>")
            sys.exit(1)
        issue_id = args[1]
        path = get_issue_path(issue_id)
        if not os.path.exists(path):
            print(f"Error: Issue file not found for '{issue_id}'. Please run 'create' first.")
            sys.exit(1)
            
        # Determine branch name
        slug = issue_id.lower().replace('_', '-')
        branch_name = f"feat/{slug}"
        print(f"Creating/checking out Git branch '{branch_name}'...")
        
        # Run git checkout
        subprocess.run(['git', 'checkout', '-b', branch_name], stderr=subprocess.PIPE)
        subprocess.run(['git', 'checkout', branch_name])
        
    elif action == "close":
        if len(args) < 2:
            print("Usage: helper.py issue close <id>")
            sys.exit(1)
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

        # Read issue file
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse github_number to close remote issue
        m_num = re.search(r'github_number:\s*(\d+)', content)
        if m_num:
            github_number = int(m_num.group(1))
            try:
                import git_api
                print(f"Closing remote GitHub issue #{github_number}...")
                git_api.close_github_issue(github_number)
            except Exception as e:
                print(f"Warning: Could not close remote GitHub issue: {e}")
            
        content = re.sub(r'status:\s*open', 'status: closed', content)
        
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
                ".agents/scripts/cli/commands/bootstrap.py"
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

            print(f"Merging branch '{found_branch}' into '{base_branch}'...")
            merge_res = subprocess.run(['git', 'merge', found_branch])
            if merge_res.returncode != 0:
                print("Error: Git merge failed with conflict! Please resolve manually.")
                sys.exit(1)

            print(f"Deleting branch '{found_branch}'...")
            subprocess.run(['git', 'branch', '-d', found_branch])

            # Release lock
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
            print(f"[OK] Issue '{issue_id}' fully resolved and merged to '{base_branch}' successfully.")
        
    elif action == "sync":
        sync_issues()
        
    else:
        print(f"Error: Unknown action '{action}'. Available: create, list, checkout, close, sync")
        sys.exit(1)
