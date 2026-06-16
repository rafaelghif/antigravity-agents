import os
import sys
import subprocess
import utils

def run(args):
    validate_sh = os.path.join(utils.get_agents_dir(), 'scripts', 'validate.sh')
    if not os.path.exists(validate_sh):
        print(f"Error: validate.sh not found at {validate_sh}", file=sys.stderr)
        sys.exit(1)
        
    proc = utils.run_shell_script(validate_sh)
    sys.exit(proc.returncode)
