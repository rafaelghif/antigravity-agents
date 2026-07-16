import os
import sys
import json
import subprocess
import re

try:
    import portalocker
except ImportError:
    try:
        from .. import portalocker
    except ImportError:
        import portalocker

LOCK_FILE = ".agents/state/locks.json"

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

def load_issue_content_from_branch(branch: str, issue_id: str) -> str:
    try:
        filename = f"{issue_id.replace('-', '_')}.md"
        path_in_repo = f".agents/issues/{filename}"
        res = subprocess.run(
            ['git', 'show', f"{branch}:{path_in_repo}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if res.returncode == 0:
            return res.stdout
    except Exception:
        pass
    return ""

def parse_locks_from_content(content: str) -> list:
    locks = []
    in_locks_section = False
    for line in content.splitlines():
        if "Active module locks:" in line:
            in_locks_section = True
            continue
        if in_locks_section:
            if line.startswith('- ') or line.startswith('* ') or line.startswith('#'):
                in_locks_section = False
                continue
            m = re.search(r'-\s*\[\s*\]\s*([^\s<]+)', line)
            if m:
                val = m.group(1).strip()
                if val.lower() != "none":
                    locks.append(val)
    return locks

def get_existing_branches() -> set:
    existing = set()
    try:
        res = subprocess.run(
            ['git', 'show-ref'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if res.returncode != 0:
            res = subprocess.run(
                ['git', 'branch', '--format=%(refname:short)'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                line = line.strip()
                if not line:
                    continue
                match = re.search(r'refs/heads/(\S+)', line)
                if match:
                    existing.add(match.group(1))
                elif "HEAD" not in line:
                    b = line.lstrip('* ').strip()
                    if b:
                        existing.add(b)
    except Exception:
        pass
    return existing

def prune_stale_locks(locks: dict) -> dict:
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
            data = json.loads(content)
            
            try:
                from core.entities import ModuleLock, ValidationError
            except ImportError:
                try:
                    from ....core.entities import ModuleLock, ValidationError
                except ImportError:
                    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
                    from core.entities import ModuleLock, ValidationError
                    
            valid_locks = {}
            for module, branch in data.items():
                try:
                    lock_entity = ModuleLock(module=module, branch=branch)
                    lock_entity.validate()
                    valid_locks[module] = branch
                except ValidationError as ve:
                    print(f"Warning: Ignored unsafe lock definition: {ve}")
            return valid_locks
    except Exception:
        return {}

def load_locks() -> dict:
    locks = read_locks()
    if locks:
        pruned = prune_stale_locks(locks)
        if pruned != locks:
            save_locks(pruned)
        return pruned

    locks = {}
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
                if not b or "HEAD" in b:
                    continue
                if b in ("main", "master", "origin/main", "origin/master"):
                    continue
                branches.append(b)
    except Exception:
        pass

    current_branch = "unknown"
    try:
        res = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=subprocess.PIPE, text=True)
        current_branch = res.stdout.strip()
    except Exception:
        pass

    try:
        from ..issue import parse_issue_frontmatter
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
        if branch == current_branch:
            local_path = os.path.join(".agents/issues", f"{issue_id.replace('-', '_')}.md")
            if os.path.exists(local_path):
                try:
                    with open(local_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except Exception:
                    pass

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
