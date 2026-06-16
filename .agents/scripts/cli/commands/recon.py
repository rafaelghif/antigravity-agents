import os
import sys
import subprocess
import utils

def run(args):
    recon_sh = os.path.join(utils.get_agents_dir(), 'scripts', 'recon.sh')
    if not os.path.exists(recon_sh):
        print(f"Error: recon.sh not found at {recon_sh}", file=sys.stderr)
        sys.exit(1)
        
    proc = subprocess.run([recon_sh] + args[1:])
    sys.exit(proc.returncode)
