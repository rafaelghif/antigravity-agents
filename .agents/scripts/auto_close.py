#!/usr/bin/env python3
import sys
import os
import re
import subprocess

def close_issue(issue_id):
    """Update board.md and issue_XXX.md to close the issue."""
    board_path = os.path.join(".agents", "tasks", "board.md")
    issue_path = os.path.join(".agents", "issues", f"issue_{issue_id}.md")
    
    # 1. Update board.md
    if os.path.exists(board_path):
        with open(board_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        new_lines = []
        task_line = None
        in_doing = False
        in_todo = False
        
        for line in lines:
            if line.startswith("## Doing"):
                in_doing = True
                in_todo = False
                new_lines.append(line)
                continue
            elif line.startswith("## Todo"):
                in_todo = True
                in_doing = False
                new_lines.append(line)
                continue
            elif line.startswith("## "):
                in_doing = False
                in_todo = False
                new_lines.append(line)
                continue
                
            # If we find the task in Todo or Doing, capture it and don't append it yet
            if (in_doing or in_todo) and line.strip().startswith("- [ ]") and f"id: {issue_id}" in line:
                task_line = line.replace("- [ ]", "- [x]", 1)
                continue
                
            new_lines.append(line)
            
        if task_line:
            # Insert into Done
            final_lines = []
            in_done = False
            inserted = False
            for line in new_lines:
                if line.startswith("## Done"):
                    in_done = True
                    final_lines.append(line)
                    continue
                elif line.startswith("## ") and in_done:
                    if not inserted:
                        final_lines.append(task_line)
                        inserted = True
                    in_done = False
                
                if in_done and not line.strip() and not inserted:
                    final_lines.append(task_line)
                    inserted = True
                    
                final_lines.append(line)
                
            if not inserted:
                # Fallback if Done doesn't have an empty line at the end
                final_lines.append(task_line)
                
            with open(board_path, 'w', encoding='utf-8') as f:
                f.writelines(final_lines)
            subprocess.run(['git', 'add', board_path], check=False)
            
    # 2. Update issue file
    if os.path.exists(issue_path):
        with open(issue_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = re.sub(r'status:\s*(open|in_progress)', 'status: closed', content, flags=re.IGNORECASE)
        if new_content != content:
            with open(issue_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            subprocess.run(['git', 'add', issue_path], check=False)

def main():
    if len(sys.argv) < 2:
        sys.exit(0)
        
    commit_msg_file = sys.argv[1]
    if not os.path.exists(commit_msg_file):
        sys.exit(0)
        
    try:
        with open(commit_msg_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Match "Closes #123" or "Fixes issue-123"
        pattern = r'(?i)(?:closes|fixes|resolves)\s+(?:#|issue-)(\d+)'
        matches = re.finditer(pattern, content)
        
        for m in matches:
            issue_id = m.group(1)
            close_issue(issue_id)
            
    except Exception as e:
        print(f"[WARN] Failed to auto-close local issues: {e}")
        
if __name__ == '__main__':
    main()
