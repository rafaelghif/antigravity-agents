import sys
import os
import json

LOCK_FILE = ".agents/locks.json"

def load_locks():
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_locks(locks):
    try:
        with open(LOCK_FILE, 'w', encoding='utf-8') as f:
            json.dump(locks, f, indent=2)
    except Exception as e:
        print(f"Error saving locks: {e}")

def run(args):
    if len(args) == 0:
        locks = load_locks()
        if not locks:
            print("No active module locks found.")
        else:
            print("Active module locks:")
            for mod, holder in locks.items():
                print(f"  - {mod}: Locked by branch '{holder}'")
        return

    if args[0] == "--release" or args[0] == "-r":
        if len(args) < 2:
            print("Usage: helper.py lock --release <module-name>")
            sys.exit(1)
        mod_name = args[1]
        locks = load_locks()
        if mod_name in locks:
            del locks[mod_name]
            save_locks(locks)
            print(f"Successfully released lock on module '{mod_name}'.")
        else:
            print(f"Module '{mod_name}' is not currently locked.")
        return

    mod_name = args[0]
    # Determine holder branch
    import subprocess
    branch = "unknown"
    try:
        res = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=subprocess.PIPE, text=True)
        branch = res.stdout.strip()
    except Exception:
        pass

    locks = load_locks()
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
