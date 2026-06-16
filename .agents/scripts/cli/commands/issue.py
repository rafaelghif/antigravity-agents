import os
import sys
import re
from datetime import datetime
import utils

# ANSI color codes
C_GREEN = '\033[92m'
C_YELLOW = '\033[93m'
C_RED = '\033[91m'
C_GRAY = '\033[90m'
C_BOLD = '\033[1m'
C_CYAN = '\033[96m'
C_END = '\033[0m'

def color(text, ansi_code):
    if sys.stdout.isatty():
        return f"{ansi_code}{text}{C_END}"
    return text

def get_issues_dir():
    issues_dir = os.path.join(utils.get_agents_dir(), "issues")
    if not os.path.exists(issues_dir):
        os.makedirs(issues_dir)
    return issues_dir

def parse_frontmatter(file_path):
    metadata = {}
    description = ""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        m = re.match(r'^---\n(.*?)\n---\n*(.*)', content, re.DOTALL)
        if m:
            yaml_block = m.group(1)
            description = m.group(2).strip()
            
            for line in yaml_block.splitlines():
                if ':' in line:
                    k, v = line.split(':', 1)
                    metadata[k.strip()] = v.strip().strip('"\'')
        else:
            description = content.strip()
    except Exception as e:
        print(f"Error parsing issue file {file_path}: {e}", file=sys.stderr)
        
    return metadata, description

def show_help():
    print("==========================================================")
    print("  Antigravity Local Issue Tracker CLI")
    print("==========================================================")
    print("Usage: helper.sh issue <command> [arguments...]")
    print("")
    print("Subcommands:")
    print("  list                       List all issues (open and closed)")
    print("  create \"<title>\" [\"<desc>\"] Create a new local issue")
    print("  view <id>                  View details of a specific issue")
    print("  close <id>                 Close an open issue")
    print("==========================================================")

def list_issues():
    issues_dir = get_issues_dir()
    files = sorted([f for f in os.listdir(issues_dir) if re.match(r'^issue_[0-9]+\.md$', f)])
    
    if not files:
        print(color("\nNo issues found in workspace.", C_GRAY))
        return
        
    print(color("\n--- Workspace Local Issues ---", C_BOLD + C_CYAN))
    print(f"{'ID':<6} | {'Status':<8} | {'Title':<35} | {'Assignee':<10}")
    print("-" * 65)
    
    for f in files:
        file_path = os.path.join(issues_dir, f)
        meta, _ = parse_frontmatter(file_path)
        
        issue_id = meta.get("id", f.split('_')[1].split('.')[0])
        title = meta.get("title", "No Title")
        status = meta.get("status", "open").lower()
        assignee = meta.get("assignee", "None")
        
        if len(title) > 33:
            title = title[:30] + "..."
            
        status_str = f"[{status.upper()}]"
        if status == "open":
            status_colored = color(status_str, C_GREEN + C_BOLD)
        else:
            status_colored = color(status_str, C_GRAY)
            
        print(f"#{int(issue_id):<5} | {status_colored:<17} | {title:<35} | {assignee:<10}")
    print("")

def create_issue(title, description="No description provided."):
    if not title:
        print(color("Error: Issue title is required.", C_RED), file=sys.stderr)
        sys.exit(1)
        
    issues_dir = get_issues_dir()
    files = [f for f in os.listdir(issues_dir) if re.match(r'^issue_[0-9]+\.md$', f)]
    
    next_id = 1
    if files:
        ids = []
        for f in files:
            m = re.search(r'issue_([0-9]+)\.md', f)
            if m:
                ids.append(int(m.group(1)))
        if ids:
            next_id = max(ids) + 1
            
    filename = f"issue_{next_id:03d}.md"
    file_path = os.path.join(issues_dir, filename)
    created_at = datetime.now().strftime("%Y-%m-%d")
    
    content = f"""---
id: {next_id}
title: "{title}"
status: open
assignee: Agent
created_at: {created_at}
closed_at: null
---

# Description
{description}
"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(color(f"\n[SUCCESS] Created Issue #{next_id}: \"{title}\"", C_GREEN + C_BOLD))
        print(f"Saved to: .agents/issues/{filename}\n")
    except Exception as e:
        print(color(f"Error: Failed to save issue file: {e}", C_RED), file=sys.stderr)
        sys.exit(1)

def close_issue(issue_id_str):
    try:
        issue_id = int(issue_id_str)
    except ValueError:
        print(color(f"Error: Invalid issue ID '{issue_id_str}'", C_RED), file=sys.stderr)
        sys.exit(1)
        
    issues_dir = get_issues_dir()
    filename = f"issue_{issue_id:03d}.md"
    file_path = os.path.join(issues_dir, filename)
    
    if not os.path.exists(file_path):
        print(color(f"Error: Issue #{issue_id} not found.", C_RED), file=sys.stderr)
        sys.exit(1)
        
    meta, desc = parse_frontmatter(file_path)
    if meta.get("status") == "closed":
        print(color(f"Issue #{issue_id} is already closed.", C_YELLOW))
        return
        
    closed_at = datetime.now().strftime("%Y-%m-%d")
    
    content = f"""---
id: {issue_id}
title: "{meta.get('title', 'No Title')}"
status: closed
assignee: {meta.get('assignee', 'Agent')}
created_at: {meta.get('created_at', closed_at)}
closed_at: {closed_at}
---

# Description
{desc}
"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(color(f"\n[SUCCESS] Closed Issue #{issue_id}: \"{meta.get('title')}\"", C_GREEN + C_BOLD))
    except Exception as e:
        print(color(f"Error: Failed to close issue: {e}", C_RED), file=sys.stderr)
        sys.exit(1)

def view_issue(issue_id_str):
    try:
        issue_id = int(issue_id_str)
    except ValueError:
        print(color(f"Error: Invalid issue ID '{issue_id_str}'", C_RED), file=sys.stderr)
        sys.exit(1)
        
    issues_dir = get_issues_dir()
    filename = f"issue_{issue_id:03d}.md"
    file_path = os.path.join(issues_dir, filename)
    
    if not os.path.exists(file_path):
        print(color(f"Error: Issue #{issue_id} not found.", C_RED), file=sys.stderr)
        sys.exit(1)
        
    meta, desc = parse_frontmatter(file_path)
    
    status = meta.get("status", "open").lower()
    if status == "open":
        status_colored = color("OPEN", C_GREEN + C_BOLD)
    else:
        status_colored = color("CLOSED", C_GRAY)
        
    print("\n" + color("="*58, C_CYAN))
    print(f"{color('ISSUE #' + str(issue_id), C_BOLD + C_CYAN)}: {color(meta.get('title', 'No Title'), C_BOLD)}")
    print(color("="*58, C_CYAN))
    print(f"  Status:     {status_colored}")
    print(f"  Assignee:   {meta.get('assignee', 'None')}")
    print(f"  Created At: {meta.get('created_at', 'N/A')}")
    if status == "closed":
        print(f"  Closed At:  {meta.get('closed_at', 'N/A')}")
    print(color("-"*58, C_CYAN))
    print(f"\n{desc}\n")
    print(color("="*58, C_CYAN) + "\n")

def run(args):
    if len(args) < 2:
        show_help()
        sys.exit(0)
        
    subcmd = args[1].lower()
    
    if subcmd == "list":
        list_issues()
    elif subcmd == "create":
        if len(args) < 3:
            print(color("Error: Title is required. Usage: helper.sh issue create \"<title>\" [\"<desc>\"]", C_RED), file=sys.stderr)
            sys.exit(1)
        title = args[2]
        desc = args[3] if len(args) > 3 else "No description provided."
        create_issue(title, desc)
    elif subcmd == "close":
        if len(args) < 3:
            print(color("Error: Issue ID is required. Usage: helper.sh issue close <id>", C_RED), file=sys.stderr)
            sys.exit(1)
        close_issue(args[2])
    elif subcmd == "view":
        if len(args) < 3:
            print(color("Error: Issue ID is required. Usage: helper.sh issue view <id>", C_RED), file=sys.stderr)
            sys.exit(1)
        view_issue(args[2])
    elif subcmd in ("-h", "--help", "help"):
        show_help()
    else:
        print(color(f"Error: Unknown issue subcommand '{subcmd}'", C_RED), file=sys.stderr)
        show_help()
        sys.exit(1)
