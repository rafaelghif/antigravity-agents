import sys
import os
import subprocess
from typing import List

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

SOURCE_REPO = "https://github.com/rafaelghifari/antigravity-agents.git"

def print_err(msg: str) -> None:
    print(f"{RED}[FAIL] {msg}{RESET}")

def print_warn(msg: str) -> None:
    print(f"{YELLOW}[WARN] {msg}{RESET}")

def print_ok(msg: str) -> None:
    print(f"{GREEN}[OK] {msg}{RESET}")

def run(args: List[str]) -> None:
    print("="*60)
    print("      Antigravity Agent Core (AAC) V2 Auto-Upgrader")
    print("="*60)
    
    git_check = subprocess.run(
        ['git', 'rev-parse', '--is-inside-work-tree'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if git_check.returncode != 0:
        print_err("Not inside a Git repository. Cannot perform upgrade.")
        sys.exit(1)
        
    print(f"Fetching latest updates from official source repository: {SOURCE_REPO}...")
    try:
        res_fetch = subprocess.run(
            ['git', 'fetch', '--depth', '1', SOURCE_REPO, 'main'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if res_fetch.returncode != 0:
            res_fetch = subprocess.run(
                ['git', 'fetch', '--depth', '1', SOURCE_REPO, 'master'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
        if res_fetch.returncode != 0:
            print_err(f"Failed to fetch updates from source repository: {res_fetch.stderr.strip()}")
            sys.exit(1)
            
        print_ok("Successfully fetched latest remote release.")
        print("Checking out core files...")
        
        paths_to_update = [
            ".agents/scripts/",
            ".agents/templates/",
            "helper.sh",
            "helper.ps1"
        ]
        
        res_checkout = subprocess.run(
            ['git', 'checkout', 'FETCH_HEAD', '--'] + paths_to_update,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if res_checkout.returncode != 0:
            print_err(f"Failed to restore core files from FETCH_HEAD: {res_checkout.stderr.strip()}")
            sys.exit(1)
            
        if os.name != 'nt' and os.path.exists("helper.sh"):
            os.chmod("helper.sh", 0o755)
            
        print_ok("Antigravity Agent Core has been upgraded successfully!")
        print("Local configuration and profile settings were preserved.")
        print("="*60)
        sys.exit(0)
    except Exception as e:
        print_err(f"Error performing upgrade: {e}")
        sys.exit(1)
