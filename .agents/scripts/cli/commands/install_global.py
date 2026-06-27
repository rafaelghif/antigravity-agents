import sys
import os
import stat
from typing import List

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def print_err(msg: str) -> None:
    print(f"{RED}[FAIL] {msg}{RESET}")

def print_ok(msg: str) -> None:
    print(f"{GREEN}[OK] {msg}{RESET}")

def print_warn(msg: str) -> None:
    print(f"{YELLOW}[WARN] {msg}{RESET}")

def run(args: List[str]) -> None:
    print("="*60)
    print("   Antigravity Agent Core (AAC) Global CLI Installer")
    print("="*60)
    
    bin_dir = os.path.abspath(os.path.expanduser("~/.local/bin"))
    os.makedirs(bin_dir, exist_ok=True)
    
    is_windows = os.name == 'nt'
    
    if is_windows:
        launcher_path = os.path.join(bin_dir, "aac.ps1")
        content = """# Antigravity Agent Core Global Launcher Wrapper
$GitRoot = git rev-parse --show-toplevel 2>$null
if (-not $GitRoot) {
    Write-Error "[FAIL] Not inside a Git repository workspace."
    exit 1
}

$HelperScript = Join-Path $GitRoot "helper.ps1"
if (-not (Test-Path $HelperScript)) {
    Write-Error "[FAIL] Antigravity Agent Core is not initialized in this workspace (helper.ps1 not found at $GitRoot)."
    exit 1
}

& $HelperScript @args
"""
    else:
        launcher_path = os.path.join(bin_dir, "aac")
        content = """#!/usr/bin/env bash
# Antigravity Agent Core Global Launcher Wrapper
GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -z "$GIT_ROOT" ]; then
    echo "[FAIL] Not inside a Git repository workspace."
    exit 1
fi

if [ ! -f "$GIT_ROOT/helper.sh" ]; then
    echo "[FAIL] Antigravity Agent Core is not initialized in this workspace (helper.sh not found at $GIT_ROOT)."
    exit 1
fi

exec "$GIT_ROOT/helper.sh" "$@"
"""
        
    try:
        with open(launcher_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        if not is_windows:
            st = os.stat(launcher_path)
            os.chmod(launcher_path, st.st_mode | stat.S_IEXEC)
            
        print_ok(f"Global wrapper installed successfully at '{launcher_path}'.")
        
        path_env = os.environ.get("PATH", "")
        normal_paths = [os.path.normpath(p.strip()) for p in path_env.split(os.pathsep)]
        if os.path.normpath(bin_dir) not in normal_paths:
            print("\n" + "="*60)
            print(f"{YELLOW}ACTION REQUIRED: Add the local bin directory to your PATH{RESET}")
            print("-"*60)
            if is_windows:
                print(f"Run this in PowerShell to add to user PATH permanently:")
                print(f"[Environment]::SetEnvironmentVariable('Path', [Environment]::GetEnvironmentVariable('Path', 'User') + ';{bin_dir}', 'User')")
            else:
                print(f"Add this line to your shell profile (.bashrc or .zshrc):")
                print(f"export PATH=\"\\$HOME/.local/bin:\\$PATH\"")
            print("="*60 + "\n")
        else:
            print_ok("Verified: target directory is already in your PATH environment variable.")
            print("You can now run 'aac <command>' globally from any project directory!")
            
    except Exception as e:
        print_err(f"Failed to install global launcher wrapper: {e}")
        sys.exit(1)
        
    print("="*60)
    sys.exit(0)
