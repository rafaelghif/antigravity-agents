import os
import sys
import subprocess
import shutil
import utils

def run(args):
    memory_file = utils.get_memory_file()
    if not os.path.exists(memory_file):
        print(f"Error: Memory file {memory_file} not found.", file=sys.stderr)
        sys.exit(1)
        
    archive_dir = os.path.join(utils.get_agents_dir(), 'archive')
    os.makedirs(archive_dir, exist_ok=True)
    
    # Get git branch
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], 
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except:
        branch = "detached"
        
    branch_clean = branch.replace('/', '_')
    archive_file = os.path.join(archive_dir, f"sprint_{branch_clean}.md")
    
    print(f"Archiving tasks to {archive_file}...")
    
    # Read memory.md
    with open(memory_file, 'r') as f:
        lines = f.readlines()
        
    checklist_lines = []
    in_checklist = False
    
    # Extract the checklist
    for line in lines:
        if "### Sprint Tasks Checklist" in line:
            in_checklist = True
            checklist_lines.append(line)
            continue
        if in_checklist:
            if line.strip() == "---" or line.startswith("## "):
                in_checklist = False
            else:
                checklist_lines.append(line)
                
    # Save/append the checklist to the archive file
    if checklist_lines:
        mode = 'a' if os.path.exists(archive_file) else 'w'
        with open(archive_file, mode) as f:
            f.write("".join(checklist_lines))
            f.write("\n")
            
    # Relocate workflow and PR files
    branch_archive_dir = os.path.join(archive_dir, f"sprint_{branch_clean}")
    os.makedirs(branch_archive_dir, exist_ok=True)
    
    workflows_dir = os.path.join(utils.get_agents_dir(), 'workflows')
    print(f"Archiving workflow and PR review files to {branch_archive_dir}...")
    
    if os.path.exists(workflows_dir):
        for item in os.listdir(workflows_dir):
            item_path = os.path.join(workflows_dir, item)
            # Match task_* or pr_review_* files
            if os.path.isfile(item_path) and (item.startswith("task_") or item.startswith("pr_review_")):
                shutil.move(item_path, os.path.join(branch_archive_dir, item))
                
    # Reset checklist in memory.md
    new_lines = []
    skip = False
    for line in lines:
        if "### Sprint Tasks Checklist" in line:
            new_lines.append(line)
            new_lines.append("- [ ] Implement core logic\n")
            new_lines.append("- [ ] Write unit tests\n")
            new_lines.append("- [ ] Verify build and tests pass\n")
            skip = True
            continue
        if skip:
            if line.strip() == "---":
                skip = False
                new_lines.append(line)
            continue
        new_lines.append(line)
        
    with open(memory_file, 'w') as f:
        f.writelines(new_lines)
        
    print("Checklist reset successfully.")
