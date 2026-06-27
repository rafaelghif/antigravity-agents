import sys
import os
import re
import subprocess
from datetime import datetime

ISSUE_DIR = ".agents/issues"

def get_issue_path(issue_id):
    normalized = issue_id.lower().replace('-', '_')
    if not os.path.exists(ISSUE_DIR):
        os.makedirs(ISSUE_DIR)
    for f in os.listdir(ISSUE_DIR):
        if normalized in f.lower().replace('-', '_') or issue_id.lower() in f.lower():
            return os.path.join(ISSUE_DIR, f)
    # Extract only digits/chars for standard suffix
    suffix = normalized.split('_')[-1]
    return os.path.join(ISSUE_DIR, f"issue_{suffix}.md")

def run(args):
    if len(args) == 0:
        print("Usage: helper.py issue <create|list|checkout|close> [args...]")
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
            
        current_date = datetime.now().strftime("%Y-%m-%d")
        template = f"""---
id: {issue_id}
title: "{title}"
status: open
assignee: agent-antigravity
created_at: {current_date}
---

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
            
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        content = re.sub(r'status:\s*open', 'status: closed', content)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully closed issue '{issue_id}' (updated file status).")
        
    else:
        print(f"Error: Unknown action '{action}'. Available: create, list, checkout, close")
        sys.exit(1)
