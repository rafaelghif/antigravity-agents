import sys
import os
import subprocess

try:
    from . import validation
except ImportError:
    import validation

try:
    from .services import lock_service
except ImportError:
    try:
        import services.lock_service as lock_service
    except ImportError:
        from cli.commands.services import lock_service

LOCK_FILE = lock_service.LOCK_FILE

def get_issue_id_from_branch(branch_name: str) -> str:
    return lock_service.get_issue_id_from_branch(branch_name)

def normalize_branch_name(branch: str) -> str:
    return lock_service.normalize_branch_name(branch)

def load_locks() -> dict:
    return lock_service.load_locks()

def save_locks(locks: dict) -> None:
    lock_service.save_locks(locks)

def prune_stale_locks(locks: dict) -> dict:
    return lock_service.prune_stale_locks(locks)

def get_existing_branches() -> list:
    return lock_service.get_existing_branches()

def read_locks() -> dict:
    return lock_service.read_locks()

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

    if args and args[0] in ("--clear-all", "--clear"):
        save_locks({})
        if os.path.exists(LOCK_FILE):
            try:
                os.remove(LOCK_FILE)
            except Exception:
                pass
        print("Successfully cleared all local module locks.")
        return

    if args and args[0] in ("--prune", "-p"):
        pruned = prune_stale_locks(locks)
        save_locks(pruned)
        print("Successfully pruned stale module locks.")
        return

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
            if not validation.validate_safe_path(mod_name):
                print(f"Error: Invalid module or path name '{mod_name}'.")
                sys.exit(1)

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
        if not validation.validate_safe_path(mod_name):
            print(f"Error: Invalid module or path name '{mod_name}'.")
            sys.exit(1)

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
