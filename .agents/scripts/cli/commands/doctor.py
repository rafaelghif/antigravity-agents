import os
import sys
import subprocess
import utils

# ANSI color codes
C_GREEN = '\033[92m'
C_YELLOW = '\033[93m'
C_RED = '\033[91m'
C_BOLD = '\033[1m'
C_END = '\033[0m'

def color(text, ansi_code):
    if sys.stdout.isatty():
        return f"{ansi_code}{text}{C_END}"
    return text

def run(args):
    utils.print_title("Antigravity Workspace Doctor Diagnostics")
    
    errors = 0
    
    # Check Git Repository
    if os.path.isdir('.git'):
        print(f"  {color('[PASS]', C_GREEN + C_BOLD)} Git repository initialized.")
    else:
        print(f"  {color('[FAIL]', C_RED + C_BOLD)} Git repository not initialized!")
        errors += 1
        
    def check_hook(hook_name):
        import filecmp
        import shutil
        agents_dir = utils.get_agents_dir()
        src = os.path.join(agents_dir, 'hooks', hook_name)
        dest = os.path.join('.git', 'hooks', hook_name)
        
        if not os.path.exists(src):
            return
            
        out_of_sync = False
        if not os.path.exists(dest):
            out_of_sync = True
        elif not os.access(dest, os.X_OK):
            out_of_sync = True
        else:
            try:
                if not filecmp.cmp(src, dest, shallow=False):
                    out_of_sync = True
            except:
                out_of_sync = True
                
        if out_of_sync:
            print(f"  {color('[WARNING]', C_YELLOW + C_BOLD)} Git {hook_name} hook is missing, out-of-sync, or not executable. Auto-healing...")
            try:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy(src, dest)
                os.chmod(dest, 0o755)
                print(f"            [PASS] Git {hook_name} hook auto-healed successfully.")
            except Exception as e:
                print(f"            Failed to copy hook: {e}", file=sys.stderr)
        else:
            print(f"  {color('[PASS]', C_GREEN + C_BOLD)} {hook_name} Git hook is installed, up-to-date, and executable.")
            
    check_hook("pre-commit")
    check_hook("post-commit")
    check_hook("commit-msg")
    
    def check_script(script_name):
        nonlocal errors
        script_path = os.path.join(utils.get_agents_dir(), 'scripts', script_name)
        if os.path.exists(script_path):
            if os.access(script_path, os.X_OK):
                print(f"  {color('[PASS]', C_GREEN + C_BOLD)} {script_name} is executable.")
            else:
                print(f"  {color('[WARNING]', C_YELLOW + C_BOLD)} {script_name} is not executable. Auto-correcting...")
                try:
                    os.chmod(script_path, 0o755)
                except Exception as e:
                    print(f"            Failed to set executable permission: {e}", file=sys.stderr)
        else:
            print(f"  {color('[FAIL]', C_RED + C_BOLD)} {script_name} is missing!")
            errors += 1
            
    check_script("helper.sh")
    check_script("recon.sh")
    check_script("validate.sh")
    
    validate_sh = os.path.join(utils.get_agents_dir(), 'scripts', 'validate.sh')
    if os.path.exists(validate_sh):
        print("----------------------------------------------------------")
        proc = utils.run_shell_script(validate_sh)
        if proc.returncode != 0:
            errors += 1
            
    print("==========================================================")
    if errors == 0:
        print(color("Doctor diagnostics: ALL SYSTEMS HEALTHY", C_GREEN + C_BOLD))
        sys.exit(0)
    else:
        print(color(f"Doctor diagnostics: FOUND {errors} ERROR(S) / WARNING(S)", C_YELLOW + C_BOLD))
        sys.exit(1)
