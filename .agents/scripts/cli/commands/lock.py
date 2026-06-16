import os
import sys
import subprocess
from datetime import datetime
import utils

def run(args):
    command = args[0]
    
    if len(args) < 2:
        print(f"Error: Please specify a module name to {command}.", file=sys.stderr)
        sys.exit(1)
        
    module = args[1]
    # Replace slashes with underscores for nested monorepo paths
    lock_name = module.replace('/', '_')
    locks_dir = os.path.join(utils.get_agents_dir(), 'locks')
    os.makedirs(locks_dir, exist_ok=True)
    lockfile = os.path.join(locks_dir, f"{lock_name}.lock")
    
    if command == "lock":
        if os.path.exists(lockfile):
            print(f"Error: Module '{module}' is already locked!", file=sys.stderr)
            with open(lockfile, 'r') as f:
                print(f.read(), file=sys.stderr)
            sys.exit(1)
            
        # Get git branch
        try:
            branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], 
                stderr=subprocess.DEVNULL
            ).decode().strip()
        except:
            branch = "detached"
            
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        with open(lockfile, 'w') as f:
            f.write(f"Branch: {branch}\n")
            f.write(f"Owner: Agent\n")
            f.write(f"Timestamp: {timestamp}\n")
            
        print(f"Acquired lock for module '{module}' at {lockfile}")
        
    elif command == "unlock":
        if os.path.exists(lockfile):
            os.remove(lockfile)
            print(f"Released lock for module '{module}'")
        else:
            print(f"Warning: No active lock found for module '{module}'")
