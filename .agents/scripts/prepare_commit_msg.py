#!/usr/bin/env python3
import sys
import os
import re
import subprocess

def get_branch_name():
    try:
        res = subprocess.run(
            ['git', 'symbolic-ref', '--short', 'HEAD'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return res.stdout.strip()
    except Exception:
        try:
            res = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            return res.stdout.strip()
        except Exception:
            return ""

def main():
    if len(sys.argv) < 2:
        return
        
    commit_msg_filepath = sys.argv[1]
    commit_source = sys.argv[2] if len(sys.argv) > 2 else ""
    
    # Skip for merge or squash commits as they have their own templates
    if commit_source in ("merge", "squash"):
        return
        
    branch = get_branch_name()
    if not branch:
        return
        
    # Search for (task-|issue-|chore-)[a-zA-Z0-9_-]+ in branch name
    m = re.search(r'((?:task|issue|chore)-[a-zA-Z0-9_-]+)', branch, re.IGNORECASE)
    if not m:
        return
        
    issue_id = m.group(1)
    
    if not os.path.exists(commit_msg_filepath):
        return
        
    with open(commit_msg_filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Skip if the issue ID is already mentioned in the commit message
    if re.search(re.escape(issue_id), content, re.IGNORECASE):
        return
        
    lines = content.splitlines()
    
    # Find insert point before git comments
    insert_idx = len(lines)
    for idx, line in enumerate(lines):
        if line.strip().startswith('#'):
            insert_idx = idx
            break
            
    trailer = f"Refs: {issue_id}"
    
    insert_lines = []
    if insert_idx > 0 and lines[insert_idx - 1].strip():
        insert_lines.append("")
    insert_lines.append(trailer)
    if insert_idx < len(lines):
        insert_lines.append("")
        
    for item in reversed(insert_lines):
        lines.insert(insert_idx, item)
        
    new_content = "\n".join(lines)
    if not new_content.endswith('\n') and content.endswith('\n'):
         new_content += '\n'
         
    with open(commit_msg_filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

if __name__ == '__main__':
    main()
