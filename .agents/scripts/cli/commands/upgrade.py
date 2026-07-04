import sys
import os
import subprocess
import time
import json
from typing import List

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

SOURCE_REPO = "https://github.com/rafaelghif/antigravity-agents.git"

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
            ".agents/skills/",
            ".agents/rules.md",
            "AGENTS.md",
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

def check_and_run_auto_upgrade() -> None:
    # 1. Check if disabled via environment variable or during audit test validation
    if os.environ.get("AAC_DISABLE_AUTO_UPDATE") == "true" or os.environ.get("IN_AUDIT_TEST") == "true":
        return

    # 2. Check rate limiting (once every 30 minutes / 1800 seconds)
    state_file = ".agents/upgrade_state.json"
    now = time.time()
    try:
        if os.path.exists(state_file):
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            last_check = state.get("last_check_timestamp", 0)
            if now - last_check < 1800:
                return
    except Exception:
        pass

    # 3. Check inside Git worktree
    git_check = subprocess.run(
        ['git', 'rev-parse', '--is-inside-work-tree'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if git_check.returncode != 0:
        return

    # 4. Check active branch (only main/master base branches)
    res_branch = subprocess.run(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if res_branch.returncode != 0:
        return
    active_branch = res_branch.stdout.strip()
    if active_branch not in ('main', 'master'):
        return

    # 5. Check if local working tree is clean for core paths
    paths_to_update = [
        ".agents/scripts/",
        ".agents/templates/",
        ".agents/skills/",
        ".agents/rules.md",
        "AGENTS.md",
        "helper.sh",
        "helper.ps1"
    ]
    res_status = subprocess.run(
        ['git', 'status', '--porcelain', '--'] + paths_to_update,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if res_status.returncode != 0 or res_status.stdout.strip():
        return

    # 6. Determine remote URL from origin, falling back to SOURCE_REPO
    remote_url = SOURCE_REPO
    res_remote = subprocess.run(
        ['git', 'remote', 'get-url', 'origin'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if res_remote.returncode == 0 and res_remote.stdout.strip():
        remote_url = res_remote.stdout.strip()

    # 7. Fetch remote tracking branch
    res_fetch = subprocess.run(
        ['git', 'fetch', '--quiet', '--depth', '1', remote_url, active_branch],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if res_fetch.returncode != 0:
        return

    # 8. Check if remote is ahead of local (fast-forwardable)
    res_ancestor = subprocess.run(
        ['git', 'merge-base', '--is-ancestor', 'HEAD', 'FETCH_HEAD'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if res_ancestor.returncode != 0:
        return

    # 9. Check if there are diffs in core paths
    res_diff = subprocess.run(
        ['git', 'diff', '--quiet', 'HEAD', 'FETCH_HEAD', '--'] + paths_to_update,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    upgrade_available = (res_diff.returncode != 0)
    
    # Save check state and flag
    try:
        os.makedirs(".agents", exist_ok=True)
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump({"last_check_timestamp": now, "upgrade_available": upgrade_available}, f, indent=2)
    except Exception:
        pass
