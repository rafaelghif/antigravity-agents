import sys
import os
import re
import subprocess
from datetime import datetime

# Inject parent directory containing git_api
scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)


try:
    from . import validation
except ImportError:
    import validation

try:
    from .services import issue_service
except ImportError:
    try:
        import services.issue_service as issue_service
    except ImportError:
        from cli.commands.services import issue_service

ISSUE_DIR = issue_service.ISSUE_DIR

def parse_issue_frontmatter(content):
    return issue_service.parse_issue_frontmatter(content)

def get_issue_tasks(content):
    return issue_service.get_issue_tasks(content)

def update_board_completed(issue_id):
    issue_service.update_board_completed(issue_id)

def sync_board_with_issues():
    issue_service.sync_board_with_issues()

def sync_issues():
    issue_service.sync_issues()

def push_offline_issues():
    issue_service.push_offline_issues()

def get_issue_path(issue_id):
    return issue_service.get_issue_path(issue_id)

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
        if not validation.validate_safe_identifier(issue_id):
            print(f"Error: Invalid issue ID '{issue_id}'.")
            sys.exit(1)
            
        if not os.path.exists(ISSUE_DIR):
            os.makedirs(ISSUE_DIR)
            
        file_path = get_issue_path(issue_id)
        if os.path.exists(file_path):
            print(f"Error: Issue file '{file_path}' already exists.")
            sys.exit(1)
            
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
- [ ] Task 1 <!-- id: task-1 -->

## Acceptance Criteria
- [ ] Criteria 1

## Rule & Schema Compliance Audit
- Target files to edit:
  - [ ] None <!-- id: audit-target-files -->
- Active module locks:
  - [ ] None <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [ ] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [ ] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [ ] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(template)
        print(f"Successfully created issue file '{file_path}'.")
        
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
        if not validation.validate_safe_identifier(issue_id):
            print(f"Error: Invalid issue ID '{issue_id}'.")
            sys.exit(1)
        if not os.path.exists(path):
            print(f"Error: Issue file not found for '{issue_id}'. Please run 'create' first.")
            sys.exit(1)

        active_profile_name = None
        profiles_file = ".agents/git_profiles.json"
        if os.path.exists(profiles_file):
            try:
                import json
                with open(profiles_file, 'r', encoding='utf-8') as f:
                    lines = [line for line in f if not line.strip().startswith("#")]
                    data = json.loads("".join(lines))
                    profiles = data.get("profiles", [])
                    active_profile = next((p for p in profiles if p.get("active")), None)
                    if active_profile:
                        active_profile_name = active_profile.get("name")
            except Exception:
                pass

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            fm = parse_issue_frontmatter(content)
        except Exception as e:
            print(f"Error: Failed to read/parse issue file: {e}")
            sys.exit(1)

        if active_profile_name:
            try:
                curr_assignee = fm.get("assignee")
                if curr_assignee != active_profile_name:
                    lines = content.splitlines()
                    boundary_indices = [idx for idx, line in enumerate(lines) if line.strip() == '---']
                    if len(boundary_indices) >= 2:
                        insert_idx = boundary_indices[1]
                        
                        assignee_line_idx = -1
                        for idx in range(boundary_indices[0] + 1, boundary_indices[1]):
                            if lines[idx].strip().startswith("assignee:"):
                                assignee_line_idx = idx
                                break
                        
                        if assignee_line_idx != -1:
                            lines[assignee_line_idx] = f"assignee: {active_profile_name}"
                        else:
                            lines.insert(insert_idx, f"assignee: {active_profile_name}")
                            
                        new_content = "\n".join(lines) + "\n"
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"\033[92m[OK]\033[0m Assigned issue '{issue_id}' to active profile '{active_profile_name}' in frontmatter.")
            except Exception as e:
                print(f"Warning: Failed to update issue assignee: {e}")
            
        title = fm.get("title", "")
        if title:
            title_slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
            slug = f"{issue_id.lower().replace('_', '-')}-{title_slug}"
        else:
            slug = issue_id.lower().replace('_', '-')
            
        # Trim very long branch names
        if len(slug) > 50:
            slug = slug[:50].rstrip('-')
            
        branch_name = f"feat/{slug}"
        if not validation.validate_safe_branch(branch_name):
            print(f"Error: Invalid branch name '{branch_name}'.")
            sys.exit(1)
        print(f"Checking out Git branch '{branch_name}'...")
        
        res_ref = subprocess.run(['git', 'show-ref', f'refs/heads/{branch_name}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res_ref.returncode == 0:
            subprocess.run(['git', 'checkout', branch_name])
        else:
            subprocess.run(['git', '-c', 'advice.detachedHead=false', 'checkout', '-b', branch_name])
            
        try:
            import commands.context as context_cmd
            context_cmd.optimize_context()
        except Exception as e:
            print(f"Warning: Failed to optimize context after checkout: {e}")
        
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
        if not validation.validate_safe_identifier(issue_id):
            print(f"Error: Invalid issue ID '{issue_id}'.")
            sys.exit(1)
        if not os.path.exists(path):
            print(f"Error: Issue file not found for '{issue_id}'.")
            sys.exit(1)

        res_curr = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=subprocess.PIPE, text=True)
        current_branch = res_curr.stdout.strip()
        
        found_branch = None
        try:
            res_branches = subprocess.run(
                ['git', 'branch', '--format=%(refname:short)'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if res_branches.returncode == 0:
                normalized_id = issue_id.lower().replace('_', '-')
                for b in res_branches.stdout.splitlines():
                    b = b.strip()
                    if not b:
                        continue
                    b_match = re.search(r'(task[-_]?\d+|issue[-_]?\d+|(?:\b|_|/)\d+(?:\b|_|$))', b.lower())
                    if b_match:
                        b_id = b_match.group(1).lower().replace('_', '-')
                        if b_id.isdigit():
                            b_id = f"issue-{b_id}"
                        if b_id == normalized_id:
                            found_branch = b
                            break
                        if normalized_id.isdigit() and b_id == f"issue-{normalized_id}":
                            found_branch = b
                            break
        except Exception:
            pass

        if not found_branch:
            slug = issue_id.lower().replace('_', '-')
            possible_branches = [f"feat/{slug}", f"fix/{slug}"]
            for b in possible_branches:
                res_ref = subprocess.run(['git', 'show-ref', f'refs/heads/{b}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if res_ref.returncode == 0:
                    found_branch = b
                    break

        if found_branch and current_branch != found_branch:
            print(f"Error: You are currently on branch '{current_branch}', but this issue is associated with branch '{found_branch}'.")
            print(f"Please checkout the feature branch first: git checkout {found_branch}")
            sys.exit(1)

        try:
            status_res = subprocess.run(
                ['git', 'status', '--porcelain'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            dirty_files = []
            for line in status_res.stdout.splitlines():
                if not line.strip():
                    continue
                status = line[:2]
                status_path = line[3:].strip()
                if "git_profiles.json" in status_path or "locks.json" in status_path or "upgrade_state.json" in status_path or "token_budget.json" in status_path or "active_context.md" in status_path or ".agents/state/" in status_path or ".agents/issues/" in status_path:
                    continue
                if status[0] in ('M', 'A', 'D', 'R', 'C') or status[1] in ('M', 'D'):
                    dirty_files.append(status_path)
            if dirty_files:
                print(f"Error: Uncommitted changes detected in the following files:")
                for df in dirty_files:
                    print(f"  - {df}")
                print("Please commit or stash your changes before closing the issue.")
                sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to run git status check: {e}")

        print("Triggering pre-close validation guard...")
        val_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../validate.py'))
        if os.path.exists(val_path):
            env = os.environ.copy()
            env["AAC_ENFORCE_SUBTASKS"] = "true"
            val_res = subprocess.run([sys.executable, val_path], env=env)
            if val_res.returncode != 0:
                print("Error: Validation guard failed. Issue close aborted.")
                sys.exit(1)

        print("Triggering Auto-Lessons Extractor...")
        try:
            try:
                from . import learn
            except ImportError:
                import learn
            
            base_branch = "main"
            res_master = subprocess.run(['git', 'show-ref', 'refs/heads/master'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res_master.returncode == 0:
                base_branch = "master"
                
            learn.suggest_and_record_lessons(base_branch)
        except Exception as e:
            print(f"Warning: Auto-Lessons Extractor failed: {e}")

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

        update_board_completed(issue_id)

        print("Running auto-changelog and SemVer version bump...")
        helper_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../helper.py'))
        changelog_res = subprocess.run([sys.executable, helper_path, 'changelog'])
        if changelog_res.returncode != 0:
            print("Warning: Changelog generator failed or was skipped.")

        print("Running workspace sync to compile new lessons into rules...")
        sync_res = subprocess.run([sys.executable, helper_path, 'sync'])
        if sync_res.returncode != 0:
            print("Warning: Workspace synchronization failed.")

        locks_file = ".agents/state/locks.json"
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
                ".agents/memory/lessons-learned.yaml",
                ".agents/memory/lessons-archive.yaml"
            ]
            
            # Dynamically add target files from template_map.md
            template_map_path = ".agents/docs/template_map.md"
            if os.path.exists(template_map_path):
                try:
                    with open(template_map_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip().startswith('|') and '`' in line:
                                parts = [p.strip() for p in line.split('|')]
                                if len(parts) >= 3:
                                    target_val = parts[2].replace('`', '')
                                    if target_val not in files_to_stage:
                                        files_to_stage.append(target_val)
                except Exception:
                    pass
                    
            for f_to_stage in files_to_stage:
                if os.path.exists(f_to_stage):
                    subprocess.run(['git', 'add', f_to_stage])

            issue_title = ""
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        issue_content = f.read()
                    fm = parse_issue_frontmatter(issue_content)
                    issue_title = fm.get("title", "")
                except Exception:
                    pass

            formatted_issue_id = issue_id if issue_id.startswith(('issue-', 'task-', 'chore-')) else f"issue-{issue_id}"
            if issue_title:
                commit_msg = f"chore(release): close {formatted_issue_id} - {issue_title}"
            else:
                commit_msg = f"chore(release): close {formatted_issue_id}"

            print(f"Committing final changes to branch '{found_branch}'...")
            subprocess.run([
                sys.executable,
                helper_path,
                'commit',
                '-m', commit_msg,
                '-m', f"Closes {formatted_issue_id}\n\nRefs: {formatted_issue_id}",
                '-m', "Compliance-Audit: passed",
                '--no-verify'
            ])

            base_branch = "main"
            res_master = subprocess.run(['git', 'show-ref', 'refs/heads/master'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res_master.returncode == 0:
                base_branch = "master"

            try:
                try:
                    from services import token_service
                except ImportError:
                    from commands.services import token_service
                budget = token_service.load_budget()
                daily_used = budget.get("daily_used", 0)
                daily_limit = budget.get("daily_limit", 5000000)
                monthly_used = budget.get("monthly_used", 0)
                monthly_limit = budget.get("monthly_limit", 100000000)
                
                daily_near_limit = daily_used >= (daily_limit * 0.9)
                monthly_near_limit = monthly_used >= (monthly_limit * 0.9)
                
                if daily_near_limit or monthly_near_limit:
                    print("\n==========================================================")
                    print("[WARN] Token budget limit is near or exceeded!")
                    print(f"  Daily: {daily_used}/{daily_limit} ({daily_used/daily_limit:.1%})")
                    print(f"  Monthly: {monthly_used}/{monthly_limit} ({monthly_used/monthly_limit:.1%})")
                    print("==========================================================")
                    print("Bypassing automatic Git merge and branch deletion to prevent budget overruns.")
                    print(f"You can merge and delete the branch '{found_branch}' manually:")
                    print(f"  git checkout {base_branch}")
                    print(f"  git merge {found_branch} --no-ff -m \"chore(git): merge branch {found_branch}\" -m \"{issue_id}\"")
                    print(f"  git branch -d {found_branch}")
                    print("==========================================================\n")
                    sys.exit(0)
            except Exception as e:
                print(f"Warning: Could not check token budget safety: {e}")

            print(f"Switching to base branch '{base_branch}'...")
            subprocess.run(['git', 'checkout', base_branch], check=True)

            print(f"Merging branch '{found_branch}' into '{base_branch}' with --no-ff...")
            merge_msg = f"chore(git): merge branch {found_branch}"
            merge_res = subprocess.run(['git', 'merge', found_branch, '--no-ff', '-m', merge_msg, '-m', issue_id])
            if merge_res.returncode != 0:
                print("Error: Git merge failed with conflict! Automatically aborting merge and returning to feature branch...")
                subprocess.run(['git', 'merge', '--abort'])
                subprocess.run(['git', 'checkout', found_branch])
                sys.exit(1)

            print(f"Deleting branch '{found_branch}'...")
            subprocess.run(['git', 'branch', '-d', found_branch])

            print(f"[OK] Issue '{issue_id}' fully resolved and merged to '{base_branch}' successfully.")
        
    elif action == "sync":
        push_offline_issues()
        sync_issues()
        
    else:
        print(f"Error: Unknown action '{action}'. Available: create, list, checkout, close, sync")
        sys.exit(1)
