import os
import sys
import subprocess
import utils
import re

def run(args):
    memory_file = utils.get_memory_file()
    if not os.path.exists(memory_file):
        print(f"Error: Memory file {memory_file} not found.", file=sys.stderr)
        sys.exit(1)
        
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], 
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except:
        branch = "detached"
        
    try:
        commit = subprocess.check_output(
            ["git", "log", "-n", 1, "--format=%h"], 
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except:
        commit = "none"
        
    with open(memory_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    content = re.sub(r"- \*\*Active Branch\*\*: .*", f"- **Active Branch**: {branch}", content)
    content = re.sub(r"- \*\*Last Commit Reference\*\*: .*", f"- **Last Commit Reference**: {commit}", content)
    
    with open(memory_file, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Synchronized: Branch={branch}, Commit={commit} in {memory_file}")
