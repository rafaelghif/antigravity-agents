import os
import sys
import subprocess
import utils

def run(args):
    """
    Delegate command to the adr-wizard skill main script.
    """
    # Find workspace root
    workspace_root = utils.find_workspace_root()
    script_path = os.path.join(
        workspace_root, ".agents", "skills", "adr-wizard", "scripts", "main.py"
    )
    
    if not os.path.exists(script_path):
        print(f"Error: adr-wizard skill main script not found at {script_path}", file=sys.stderr)
        sys.exit(1)
        
    # Forward all CLI arguments passed after 'adr-wizard'
    cmd = [sys.executable, script_path] + args[1:]
    
    # Execute and connect standard streams to allow interactive console prompts
    proc = subprocess.run(cmd, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
    sys.exit(proc.returncode)
