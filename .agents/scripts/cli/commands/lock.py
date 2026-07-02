import sys
import os
import json
import subprocess

LOCK_FILE = ".agents/locks.json"

def get_existing_branches() -> set:
    """Retrieve all local Git branch names in a single Git call."""
    try:
        res = subprocess.run(
            ['git', 'show-ref', '--heads'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if res.returncode != 0:
            return set()
        branches = set()
        for line in res.stdout.splitlines():
            parts = line.strip().split()
            if len(parts) == 2:
                ref = parts[1]
                if ref.startswith("refs/heads/"):
                    branches.add(ref[11:])
        return branches
    except Exception:
        return set()

def prune_stale_locks(locks: dict) -> dict:
    """Filter out locks whose holder branches no longer exist locally."""
    if not locks:
        return locks
        
    existing_branches = get_existing_branches()
    # Fallback to keep locks if Git query fails or returns empty branch list
    if not existing_branches:
        return locks
        
    stale_mods = []
    for mod, holder in list(locks.items()):
        if holder == "unknown":
            continue
        if holder not in existing_branches:
            stale_mods.append(mod)
            del locks[mod]
            
    if stale_mods:
        print(f"[INFO] Auto-released stale locks for module(s): {', '.join(stale_mods)} (associated branch no longer exists).")
    return locks

def load_locks() -> dict:
    locks = {}
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, 'r', encoding='utf-8') as f:
                locks = json.load(f)
        except Exception:
            locks = {}
            
    if locks:
        orig_len = len(locks)
        locks = prune_stale_locks(locks)
        if len(locks) != orig_len:
            save_locks(locks)
            
    return locks

def save_locks(locks: dict) -> None:
    try:
        with open(LOCK_FILE, 'w', encoding='utf-8') as f:
            json.dump(locks, f, indent=2)
    except Exception as e:
        print(f"Error saving locks: {e}")

def run(args: list) -> None:
    cli_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if cli_dir not in sys.path:
        sys.path.insert(0, cli_dir)
    from interactive import interactive_select

    is_release = False
    if args and (args[0] == "--release" or args[0] == "-r"):
        is_release = True
        args = args[1:]

    locks = load_locks()

    if is_release:
        if len(args) < 1:
            if not locks:
                print("No active module locks found to release.")
                return
            
            options = [{"name": mod, "desc": f"Locked by branch '{holder}'"} for mod, holder in locks.items()]
            sel = interactive_select(options, title="Select a module lock to release:")
            if not sel:
                print("\033[93m[WARN] Release lock cancelled.\033[0m")
                return
            mod_name = sel["name"]
        else:
            mod_name = args[0]

        if mod_name in locks:
            del locks[mod_name]
            save_locks(locks)
            print(f"Successfully released lock on module '{mod_name}'.")
        else:
            print(f"Module '{mod_name}' is not currently locked.")
        return

    if len(args) == 0:
        if not locks:
            print("No active module locks found.")
        else:
            print("Active module locks:")
            for mod, holder in locks.items():
                print(f"  - {mod}: Locked by branch '{holder}'")
        
        action_opts = [
            {"name": "Acquire module lock", "value": "acquire"},
            {"name": "Release module lock", "value": "release"},
            {"name": "Cancel", "value": "cancel"}
        ]
        sel_action = interactive_select(action_opts, title="Choose an action:")
        if not sel_action or sel_action["value"] == "cancel":
            return
            
        if sel_action["value"] == "release":
            if not locks:
                print("No active module locks found to release.")
                return
            options = [{"name": mod, "desc": f"Locked by branch '{holder}'"} for mod, holder in locks.items()]
            sel = interactive_select(options, title="Select a module lock to release:")
            if not sel:
                return
            mod_name = sel["name"]
            del locks[mod_name]
            save_locks(locks)
            print(f"Successfully released lock on module '{mod_name}'.")
            return
            
        elif sel_action["value"] == "acquire":
            common_modules = [
                "bootstrap", "changelog", "commit", "completion", "context", "doctor",
                "helper", "install_global", "issue", "learn", "lock", "profile", "skill",
                "sync", "upgrade", "validate", "git_api", "recon"
            ]
            options = [{"name": mod, "desc": f"Currently locked by '{locks[mod]}'" if mod in locks else "Available to lock"} for mod in common_modules]
            sel = interactive_select(options, title="Select a module to lock:")
            if not sel:
                return
            mod_name = sel["name"]
    else:
        mod_name = args[0]

    branch = "unknown"
    try:
        res = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=subprocess.PIPE, text=True)
        branch = res.stdout.strip()
    except Exception:
        pass

    if mod_name in locks:
        if locks[mod_name] == branch:
            print(f"Module '{mod_name}' is already locked by you (branch '{branch}').")
        else:
            print(f"Error: Module '{mod_name}' is already locked by branch '{locks[mod_name]}'!")
            sys.exit(1)
    else:
        locks[mod_name] = branch
        save_locks(locks)
        print(f"Successfully acquired lock on module '{mod_name}' for branch '{branch}'.")
