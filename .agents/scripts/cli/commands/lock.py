import sys
import os
import json
import subprocess
import re

try:
    from . import validation
except ImportError:
    import validation

LOCK_FILE = ".agents/state/locks.json"

try:
    import portalocker
except ImportError:
    try:
        from . import portalocker
    except ImportError:
        import portalocker

def get_issue_id_from_branch(branch_name: str) -> str:
    m = re.search(r'(issue|task)[-_]?\d+', branch_name, re.IGNORECASE)
    if m:
        return m.group(0).lower().replace('_', '-')
    return ""

def normalize_branch_name(branch: str) -> str:
    b = branch
    if b.startswith("refs/heads/"):
        b = b[11:]
    elif b.startswith("refs/remotes/"):
        b = b[13:]
    if b.startswith("origin/"):
        b = b[7:]
    return b

def parse_locks_from_content(content: str) -> list:
    locks = []
    lines = content.splitlines()
    in_locks_section = False
    for line in lines:
        stripped = line.strip()
        if "Active module locks:" in line:
            in_locks_section = True
            continue
        if in_locks_section:
            if line.startswith('- ') or line.startswith('* ') or line.startswith('#'):
                in_locks_section = False
                continue
            m = re.match(r'^[-*]\s*(?:\[[ xX]\]\s*)?([^\s<]+)', stripped)
            if m:
                val = m.group(1).strip()
                if val and val.lower() != "none":
                    locks.append(val)
    return locks

def load_issue_content_from_branch(branch: str, issue_id: str) -> str:
    path = f".agents/issues/{issue_id.replace('-', '_')}.md"
    try:
        res = subprocess.run(
            ['git', 'show', f"{branch}:{path}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if res.returncode == 0:
            return res.stdout
    except Exception:
        pass
    return ""

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
    if not existing_branches:
        return locks
    return {mod: holder for mod, holder in locks.items() if holder == "unknown" or holder in existing_branches}

def read_locks() -> dict:
    if not os.path.exists(LOCK_FILE):
        return {}
    try:
        with portalocker.Lock(LOCK_FILE, 'r', flags=portalocker.LOCK_SH, timeout=5.0) as f:
            content = f.read()
            if not content.strip():
                return {}
            return json.loads(content)
    except Exception:
        return {}

def load_locks() -> dict:
    locks = read_locks()
    if locks:
        # Prune stale locks immediately
        pruned = prune_stale_locks(locks)
        if pruned != locks:
            save_locks(pruned)
        return pruned

    locks = {}
    
    # Get all branches (local and remote)
    branches = []
    try:
        res = subprocess.run(
            ['git', 'branch', '-a', '--format=%(refname:short)'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                b = line.strip()
                if not b:
                    continue
                if "HEAD" in b:
                    continue
                if b in ("main", "master", "origin/main", "origin/master"):
                    continue
                branches.append(b)
    except Exception:
        pass

    # Get current branch
    current_branch = "unknown"
    try:
        res = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=subprocess.PIPE, text=True)
        current_branch = res.stdout.strip()
    except Exception:
        pass

    # Try importing parse_issue_frontmatter from issue command, fallback to simple parsing
    try:
        from .issue import parse_issue_frontmatter
    except Exception:
        def parse_issue_frontmatter(content):
            lines = content.splitlines()
            fm = {}
            if len(lines) > 0 and lines[0].strip() == '---':
                fm_lines = []
                for line in lines[1:]:
                    if line.strip() == '---':
                        break
                    fm_lines.append(line)
                for line in fm_lines:
                    if ':' in line:
                        k, v = line.split(':', 1)
                        fm[k.strip()] = v.strip().strip('"').strip("'")
            return fm

    for raw_branch in branches:
        branch = normalize_branch_name(raw_branch)
        issue_id = get_issue_id_from_branch(branch)
        if not issue_id:
            continue

        content = ""
        # Prefer local workspace file for the current branch to capture uncommitted changes
        if branch == current_branch:
            local_path = os.path.join(".agents/issues", f"{issue_id.replace('-', '_')}.md")
            if os.path.exists(local_path):
                try:
                    with open(local_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except Exception:
                    pass

        # Fallback to git show for the branch
        if not content:
            content = load_issue_content_from_branch(raw_branch, issue_id)

        if content:
            try:
                fm = parse_issue_frontmatter(content)
                status = fm.get("status", "open").lower()
                if status in ("closed", "done"):
                    continue
            except Exception:
                pass

            mod_locks = parse_locks_from_content(content)
            for mod in mod_locks:
                if mod not in locks or "origin/" in raw_branch:
                    locks[mod] = branch

    if locks:
        save_locks(locks)
    return locks

def save_locks(locks: dict) -> None:
    # Write locks to LOCK_FILE under exclusive lock
    try:
        with portalocker.Lock(LOCK_FILE, 'w', flags=portalocker.LOCK_EX, timeout=5.0) as f:
            json.dump(locks, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to write lock file: {e}")

    branch = "unknown"
    try:
        res = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=subprocess.PIPE, text=True)
        branch = res.stdout.strip()
    except Exception:
        pass
        
    if branch == "unknown":
        return
        
    issue_id = get_issue_id_from_branch(branch)
    if not issue_id:
        return
        
    issue_path = os.path.join(".agents/issues", f"{issue_id.replace('-', '_')}.md")
    if not os.path.exists(issue_path):
        return

    # Filter locks to get the ones owned by the current branch
    my_locks = []
    for mod, holder in locks.items():
        if holder == branch:
            my_locks.append(mod)

    try:
        with open(issue_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return

    lines = content.splitlines()
    in_locks_section = False
    locks_start_idx = -1
    locks_end_idx = -1

    for idx, line in enumerate(lines):
        if "Active module locks:" in line:
            in_locks_section = True
            locks_start_idx = idx
            continue
        if in_locks_section:
            if line.startswith('- ') or line.startswith('* ') or line.startswith('#'):
                in_locks_section = False
                locks_end_idx = idx
                break

    if in_locks_section and locks_end_idx == -1:
        locks_end_idx = len(lines)

    # Prepare new locks section
    new_locks_lines = []
    if not my_locks:
        new_locks_lines.append("  - [ ] None <!-- id: audit-module-locks -->")
    else:
        for mod in my_locks:
            safe_id = mod.split('/')[-1].replace('.', '_').replace('-', '_')
            new_locks_lines.append(f"  - [ ] {mod} <!-- id: lock-{safe_id} -->")

    if locks_start_idx != -1:
        updated_lines = lines[:locks_start_idx + 1] + new_locks_lines + lines[locks_end_idx:]
        new_content = '\n'.join(updated_lines) + '\n'
        try:
            with open(issue_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
        except Exception as e:
            print(f"Error updating issue locks: {e}")

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

