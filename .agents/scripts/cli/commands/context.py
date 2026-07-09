import sys
import os
import re
import json
import subprocess
from typing import List, Dict, Any

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def print_err(msg: str) -> None:
    print(f"{RED}[FAIL] {msg}{RESET}")

def print_ok(msg: str) -> None:
    print(f"{GREEN}[OK] {msg}{RESET}")

def get_current_branch() -> str:
    res = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=subprocess.PIPE, text=True)
    return res.stdout.strip() if res.returncode == 0 else ""

def get_issue_id(branch: str) -> str:
    match = re.search(r'(issue|task|chore)-[0-9]+', branch, re.IGNORECASE)
    return match.group(0).lower() if match else ""

def parse_yaml_frontmatter(content: str) -> Dict[str, str]:
    meta = {}
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        for line in match.group(1).split('\n'):
            if ':' in line:
                k, v = line.split(':', 1)
                meta[k.strip().lower()] = v.strip().strip('"').strip("'")
    return meta

def get_issue_details(issue_id: str) -> Dict[str, Any]:
    file_id = issue_id.replace('-', '_')
    # 1. Search in active issues first
    issue_file = f".agents/issues/{file_id}.md"
    if not os.path.exists(issue_file):
        # 2. Fallback to archive issues
        issue_file = f".agents/archive/issues/{file_id}.md"

    details = {
        "title": "Unknown Title",
        "tasks": [],
        "description": "No description found."
    }
    if os.path.exists(issue_file):
        with open(issue_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        meta = parse_yaml_frontmatter(content)
        details["title"] = meta.get("title", "Unknown Title")
        
        tasks = []
        for line in content.split('\n'):
            if line.strip().startswith('- ['):
                tasks.append(line.strip())
        details["tasks"] = tasks
    return details

def get_locked_modules(branch: str) -> List[str]:
    locks_file = ".agents/state/locks.json"
    if not os.path.exists(locks_file):
        return []
    try:
        with open(locks_file, 'r', encoding='utf-8') as f:
            locks = json.load(f)
        ret = []
        for module, info in locks.items():
            if isinstance(info, dict):
                if info.get("branch") == branch:
                    ret.append(module)
            elif isinstance(info, str):
                if info == branch:
                    ret.append(module)
        return ret
    except Exception:
        return []

def get_git_changes() -> List[str]:
    res = subprocess.run(['git', 'status', '--porcelain'], stdout=subprocess.PIPE, text=True)
    if res.returncode == 0 and res.stdout.strip():
        return [line.strip() for line in res.stdout.strip().split('\n')]
    return []

def archive_completed_tasks_and_plans() -> None:
    """Scan the task board, find issues in the Done column, and move their
    corresponding markdown files from .agents/issues/ and .agents/plans/ to .agents/archive/."""
    board_file = ".agents/tasks/board.md"
    if not os.path.exists(board_file):
        return
        
    done_issues = set()
    try:
        with open(board_file, 'r', encoding='utf-8') as f:
            board_content = f.read()
        # Extract Done section
        done_match = re.search(r'## Done\n([\s\S]*?)(?:##|$)', board_content)
        if done_match:
            # Find all issue ids: <!-- id: issue-xxx -->
            for match in re.finditer(r'<!-- id:\s*(issue-[a-zA-Z0-9_-]+)\s*-->', done_match.group(1)):
                done_issues.add(match.group(1).lower())
    except Exception as e:
        print_err(f"Failed to read task board for archiving: {e}")
        return

    if not done_issues:
        return

    # Create archive directories
    archive_issues_dir = ".agents/archive/issues"
    archive_plans_dir = ".agents/archive/plans"
    os.makedirs(archive_issues_dir, exist_ok=True)
    os.makedirs(archive_plans_dir, exist_ok=True)

    archived_count = 0
    # Process issues
    issues_dir = ".agents/issues"
    if os.path.exists(issues_dir):
        for f_name in os.listdir(issues_dir):
            if not f_name.endswith(".md"):
                continue
            normalized_name = f_name.lower().replace('_', '-')
            for issue_id in done_issues:
                file_id = issue_id.replace('-', '-')
                if file_id in normalized_name:
                    src_path = os.path.join(issues_dir, f_name)
                    dest_path = os.path.join(archive_issues_dir, f_name)
                    try:
                        os.rename(src_path, dest_path)
                        archived_count += 1
                    except Exception as e:
                        print_err(f"Failed to archive issue file '{f_name}': {e}")

    # Process plans
    plans_dir = ".agents/plans"
    if os.path.exists(plans_dir):
        for f_name in os.listdir(plans_dir):
            if not f_name.endswith(".md"):
                continue
            normalized_name = f_name.lower().replace('_', '-')
            for issue_id in done_issues:
                if issue_id in normalized_name:
                    src_path = os.path.join(plans_dir, f_name)
                    dest_path = os.path.join(archive_plans_dir, f_name)
                    try:
                        os.rename(src_path, dest_path)
                        archived_count += 1
                    except Exception as e:
                        print_err(f"Failed to archive plan file '{f_name}': {e}")
                        
    if archived_count > 0:
        print_ok(f"Successfully archived {archived_count} completed task/plan files to '.agents/archive/'.")

def optimize_context() -> None:
    # First, archive completed tasks and plans to keep LLM context clean
    archive_completed_tasks_and_plans()

    branch = get_current_branch()
    if not branch or branch in ('main', 'master'):
        print_err("Cannot optimize context on base branch main/master. Checkout a feature branch first.")
        sys.exit(1)
        
    issue_id = get_issue_id(branch)
    if not issue_id:
        print_err(f"Branch '{branch}' does not contain a valid issue ID pattern (e.g. feat/issue-123).")
        sys.exit(1)
        
    details = get_issue_details(issue_id)
    locks = get_locked_modules(branch)
    changes = get_git_changes()
    
    locked_str = "\n".join(f"- `{l}`" for l in locks) if locks else "- *No modules locked. Run './helper.sh lock <module>' to lock.*"
    changes_str = "\n".join(f"- `{c}`" for c in changes) if changes else "- *No uncommitted changes.*"
    tasks_str = "\n".join(t for t in details["tasks"]) if details["tasks"] else "- *No tasks defined.*"
    
    # Read synthesized rules from .agents/rules.md
    synthesized_rules_str = "- *No synthesized rules found.*"
    rules_file = ".agents/rules.md"
    if os.path.exists(rules_file):
        try:
            with open(rules_file, 'r', encoding='utf-8') as rf:
                rules_content = rf.read()
            match = re.search(r'## 5\. Synthesized Rules \(Self-Learning Memory\)[\s\S]*$', rules_content)
            if match:
                # Get the content of this section, stripping empty lines
                section_content = match.group(0).replace('## 5. Synthesized Rules (Self-Learning Memory)', '').strip()
                if section_content:
                    synthesized_rules_str = section_content
        except Exception:
            pass
            
    context_content = f"""# 🎯 Active Workspace Context Manifest

> [!IMPORTANT]
> This manifest defines the strict task scope and active workspace files for the current session.
> You must strictly follow all non-negotiable rules in [AGENTS.md](file://{os.path.abspath("AGENTS.md")}) and rules in [.agents/rules.md](file://{os.path.abspath(".agents/rules.md")}).

## 🎫 Active Issue: {issue_id.upper()}
- **Title**: {details["title"]}
- **Branch**: `{branch}`

## 🔒 Locked Modules & Files to Edit
{locked_str}

## 📂 Git Status Changes
{changes_str}

## 📋 Active Task Checklist
{tasks_str}

## 🧠 Synthesized Rules (Self-Learning Memory)
{synthesized_rules_str}

## ⚠️ Scope Boundaries
- **Strict Scope**: Only edit the files listed under "Locked Modules & Files to Edit" or files relevant to the active issue.
- **NEVER** edit files outside this scope unless explicitly requested by the USER.
"""
    
    context_file = ".agents/state/active_context.md"
    try:
        os.makedirs(os.path.dirname(context_file), exist_ok=True)
        with open(context_file, 'w', encoding='utf-8') as f:
            f.write(context_content)
        print_ok(f"Context manifest successfully optimized and written to '{context_file}'.")
    except Exception as e:
        print_err(f"Failed to write context manifest: {e}")
        sys.exit(1)

def run(args: List[str]) -> None:
    if not args or args[0].lower() != "optimize":
        print("Usage: helper.py context optimize")
        sys.exit(1)
        
    optimize_context()
    sys.exit(0)
