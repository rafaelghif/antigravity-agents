import sys
import os
import re
import json
import webbrowser
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import threading
import io
import contextlib
import mimetypes
mimetypes.init()
from urllib.parse import urlparse, parse_qs
from socketserver import ThreadingMixIn
import importlib.util

# Thread-safe compliance status cache
LATEST_DATA = {}
data_lock = threading.Lock()
initial_data_loaded = threading.Event()
audit_in_progress = False
audit_thread_lock = threading.Lock()

DEFAULT_COMPLIANCE = {
    "Critical Files": True,
    "Secrets & Ignored Files": True,
    "Link Integrity": True,
    "Git Branch Alignment": True,
    "Workspace Sync": True,
    "Task Board Schema": True,
    "Static Code Linting": True,
    "Local Unit Tests": True,
    "Module Lock Compliance": True,
    "Commit Message Compliance": True
}

# Resolve parent scripts directory
scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

import validate

# Dynamically import custom profile command module avoiding name collision with standard lib profile
cmd_dir = os.path.dirname(__file__)
spec = importlib.util.spec_from_file_location("profile_cmd", os.path.join(cmd_dir, "profile.py"))
profile_cmd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(profile_cmd)

# Dynamically import custom lock command module
spec_lock = importlib.util.spec_from_file_location("lock_cmd", os.path.join(cmd_dir, "lock.py"))
lock_cmd = importlib.util.module_from_spec(spec_lock)
spec_lock.loader.exec_module(lock_cmd)

# Dynamically import custom learn command module
spec_learn = importlib.util.spec_from_file_location("learn_cmd", os.path.join(cmd_dir, "learn.py"))
learn_cmd = importlib.util.module_from_spec(spec_learn)
spec_learn.loader.exec_module(learn_cmd)

# Dynamically import custom token command module
spec_token = importlib.util.spec_from_file_location("token_cmd", os.path.join(cmd_dir, "token.py"))
token_cmd = importlib.util.module_from_spec(spec_token)
spec_token.loader.exec_module(token_cmd)

def get_issue_frontmatter(path):
    fm = {}
    if not os.path.exists(path):
        return fm
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        lines = content.splitlines()
        if len(lines) > 0 and lines[0].strip() == '---':
            fm_lines = []
            for line in lines[1:]:
                if line.strip() == '---':
                    break
                fm_lines.append(line)
            for line in fm_lines:
                if ':' in line:
                    k, v = line.split(':', 1)
                    fm[k.strip().lower()] = v.strip().strip('"').strip("'")
    except Exception:
        pass
    return fm

def run_silent_validation():
    compliance = {}
    f_dummy = io.StringIO()
    with contextlib.redirect_stdout(f_dummy), contextlib.redirect_stderr(f_dummy):
        try:
            compliance["Critical Files"] = validate.audit_critical_files()
        except Exception:
            compliance["Critical Files"] = False
            
        try:
            compliance["Secrets & Ignored Files"] = validate.audit_secrets_and_ignored_files()
        except Exception:
            compliance["Secrets & Ignored Files"] = False
            
        try:
            compliance["Link Integrity"] = validate.audit_link_integrity()
        except Exception:
            compliance["Link Integrity"] = False
            
        try:
            compliance["Git Branch Alignment"] = validate.audit_git_branch_alignment()
        except Exception:
            compliance["Git Branch Alignment"] = False
            
        try:
            compliance["Workspace Sync"] = validate.audit_workspace_sync()
        except Exception:
            compliance["Workspace Sync"] = False
            
        try:
            compliance["Task Board Schema"] = validate.audit_task_board_schema()
        except Exception:
            compliance["Task Board Schema"] = False
            
        try:
            compliance["Static Code Linting"] = validate.audit_static_linting()
        except Exception:
            compliance["Static Code Linting"] = False
            
        try:
            compliance["Local Unit Tests"] = validate.audit_unit_tests()
        except Exception:
            compliance["Local Unit Tests"] = False
            
        try:
            compliance["Module Lock Compliance"] = validate.audit_module_locks()
        except Exception:
            compliance["Module Lock Compliance"] = False
            
        try:
            compliance["Commit Message Compliance"] = validate.audit_commit_messages()
        except Exception:
            compliance["Commit Message Compliance"] = False
            
    return compliance

def get_dashboard_data(force=False):
    # 1. Version Info
    version = "2.106.0"
    agents_path = "AGENTS.md"
    if os.path.exists(agents_path):
        try:
            with open(agents_path, 'r', encoding='utf-8') as f:
                content = f.read()
            m = re.search(r'-\s+\*\*Version:\*\*.*?([\d.]+)', content, re.IGNORECASE)
            if m:
                version = m.group(1).strip()
        except Exception:
            pass

    # 2. Module Locks
    locks = []
    try:
        lock_data = lock_cmd.load_locks()
        for module, info in lock_data.items():
            if isinstance(info, dict):
                b_name = info.get("branch", "unknown")
                ts = info.get("timestamp", "unknown")
            else:
                b_name = str(info)
                ts = "unknown"
            locks.append({
                "module": module,
                "branch": b_name,
                "timestamp": ts
            })
    except Exception:
        pass

    # 3. Active Issue Details
    active_branch = ""
    try:
        res = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0:
            active_branch = res.stdout.strip()
    except Exception:
        pass

    active_issue = {"id": "None", "title": "No Active Issue Checked Out", "status": "closed", "tasks": [], "branch": active_branch}
    issue_match = re.search(r'(issue|task|chore)-[0-9]+', active_branch, re.IGNORECASE)
    if issue_match:
        issue_id = issue_match.group(0).lower()
        file_id = issue_id.replace('-', '_')
        issue_path = f".agents/issues/{file_id}.md"
        if not os.path.exists(issue_path):
            issue_path = f".agents/archive/issues/{file_id}.md"
        
        if os.path.exists(issue_path):
            fm = get_issue_frontmatter(issue_path)
            active_issue["id"] = fm.get("id", issue_id).upper()
            active_issue["title"] = fm.get("title", "Unknown Title")
            active_issue["status"] = fm.get("status", "open")
            
            # Extract tasks list
            try:
                with open(issue_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                tasks = []
                for line in content.splitlines():
                    if line.strip().startswith('- ['):
                        tasks.append(line.strip())
                active_issue["tasks"] = tasks
            except Exception:
                pass

    # 4. Git Status Changes
    git_status = []
    try:
        res = subprocess.run(['git', 'status', '--porcelain'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0 and res.stdout.strip():
            for line in res.stdout.splitlines():
                git_status.append(line.strip())
    except Exception:
        pass

    # 5. Lessons Learned
    lessons = []
    lessons_path = ".agents/memory/lessons-learned.md"
    if os.path.exists(lessons_path):
        try:
            with open(lessons_path, 'r', encoding='utf-8') as f:
                content = f.read()
            in_lessons = False
            for line in content.splitlines():
                if line.strip().startswith('## Lessons Learned'):
                    in_lessons = True
                    continue
                elif line.strip().startswith('##') and in_lessons:
                    break
                if in_lessons and line.strip().startswith('- '):
                    # Clean markdown formatting from bullet point
                    bullet = line.strip()[2:]
                    lessons.append(bullet)
        except Exception:
            pass

    # 6. Synthesized Rules
    rules = []
    rules_path = ".agents/rules.md"
    if os.path.exists(rules_path):
        try:
            with open(rules_path, 'r', encoding='utf-8') as f:
                content = f.read()
            m = re.search(r'## 5\. Synthesized Rules \(Self-Learning Memory\)[\s\S]*$', content)
            if m:
                for line in m.group(0).splitlines():
                    if line.strip().startswith('- '):
                        rules.append(line.strip()[2:])
        except Exception:
            pass

    # 7. Recent Changelog Releases
    changelog_releases = []
    changelog_path = "CHANGELOG.md"
    if os.path.exists(changelog_path):
        try:
            with open(changelog_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Extract header versions e.g. ## [2.103.0] - 2026-07-02
            for match in re.finditer(r'^##\s+\[([\d.]+)\]\s+-\s+(\d{4}-\d{2}-\d{2})', content, re.MULTILINE):
                changelog_releases.append({
                    "version": match.group(1),
                    "date": match.group(2)
                })
        except Exception:
            pass

    # 8. Real-time Live Compliance Check
    global audit_in_progress
    if force:
        with audit_thread_lock:
            if not audit_in_progress:
                audit_in_progress = True
                def run_async_audit():
                    global audit_in_progress
                    try:
                        new_compliance = run_silent_validation()
                        with data_lock:
                            LATEST_DATA["compliance"] = new_compliance
                    finally:
                        with audit_thread_lock:
                            audit_in_progress = False
                
                t = threading.Thread(target=run_async_audit, daemon=True)
                t.start()

    with data_lock:
        compliance = LATEST_DATA.get("compliance", DEFAULT_COMPLIANCE)

    with audit_thread_lock:
        is_auditing = audit_in_progress

    # 9. Token Budget Data
    token_budget = {}
    budget_path = ".agents/state/token_budget.json"
    if os.path.exists(budget_path):
        try:
            with open(budget_path, 'r', encoding='utf-8') as f:
                token_budget = json.load(f)
            # Add reset intervals remaining
            try:
                token_budget["resets"] = token_cmd.get_reset_intervals_remaining()
            except Exception:
                pass
        except Exception:
            pass

    # Parse log entries for trend chart
    token_trend = []
    log_path = ".agents/logs/token_usage.log"
    if os.path.exists(log_path):
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            for line in lines[-15:]:  # return last 15 entries
                line = line.strip()
                if not line:
                    continue
                # Format: [2026-07-04 01:05:54 UTC] Task: issue-164 | Prompt: 15000 | Completion: 3000 | Total: 18000
                m = re.search(
                    r'\[(.*?)\] Task:\s*(\S+)\s*\|\s*Prompt:\s*(\d+)\s*\|\s*Completion:\s*(\d+)\s*\|\s*Total:\s*(\d+)',
                    line
                )
                if m:
                    token_trend.append({
                        "timestamp": m.group(1),
                        "task": m.group(2),
                        "prompt": int(m.group(3)),
                        "completion": int(m.group(4)),
                        "total": int(m.group(5))
                    })
        except Exception:
            pass

    return {
        "version": version,
        "locks": locks,
        "active_issue": active_issue,
        "git_status": git_status,
        "lessons": lessons,
        "rules": rules,
        "changelog": changelog_releases[:5], # top 5 releases
        "compliance": compliance,
        "token_budget": token_budget,
        "token_trend": token_trend,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "auditing": is_auditing
    }


def toggle_issue_task(task_index, completed):
    active_branch = ""
    try:
        res = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0:
            active_branch = res.stdout.strip()
    except Exception:
        pass

    issue_match = re.search(r'(issue|task|chore)-[0-9]+', active_branch, re.IGNORECASE)
    if not issue_match:
        return False

    issue_id = issue_match.group(0).lower()
    file_id = issue_id.replace('-', '_')
    issue_path = f".agents/issues/{file_id}.md"
    if not os.path.exists(issue_path):
        issue_path = f".agents/archive/issues/{file_id}.md"

    if not os.path.exists(issue_path):
        return False

    try:
        with open(issue_path, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()

        task_counter = 0
        updated = False
        for i, line in enumerate(lines):
            if line.strip().startswith('- ['):
                if task_counter == task_index:
                    checked_str = '[x]' if completed else '[ ]'
                    new_line = re.sub(r'-\s+\[\s*[xX\s]?\s*\]', f'- {checked_str}', line)
                    lines[i] = new_line
                    updated = True
                    break
                task_counter += 1

        if updated:
            with open(issue_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(lines) + "\n")
            
            # Sync the task board
            try:
                cmd_dir = os.path.dirname(__file__)
                if cmd_dir not in sys.path:
                    sys.path.insert(0, cmd_dir)
                import issue as issue_cmd
                issue_cmd.sync_board_with_issues()
            except Exception:
                pass
            return True
    except Exception:
        pass
    return False

def switch_active_profile(name):
    try:
        data = profile_cmd.load_profiles()
        profiles = data.get("profiles", [])
        target = None
        for p in profiles:
            if p.get("name") == name:
                p["active"] = True
                target = p
            else:
                p["active"] = False
        if not target:
            return False, f"Profile '{name}' not found"
        profile_cmd.save_profiles(data)
        
        # Auto-generate key if requested key file is not present
        ssh_key = target.get("ssh_key_path")
        if ssh_key:
            ssh_key_abs = os.path.abspath(os.path.expanduser(ssh_key))
            if not os.path.exists(ssh_key_abs):
                try:
                    profile_cmd.generate_ssh_key(name, target.get("email"))
                except Exception:
                    pass
                    
        profile_cmd.apply_git_config(target)
        return True, "Success"
    except Exception as e:
        return False, str(e)

def add_new_profile(profile_data):
    try:
        name = profile_data.get("name")
        email = profile_data.get("email")
        if not name or not profile_cmd.validate_name(name):
            return False, "Invalid profile name. Only alphanumeric, hyphens, and underscores allowed."
        if not email or not profile_cmd.validate_email(email):
            return False, "Invalid email format."
            
        data = profile_cmd.load_profiles()
        profiles = data.get("profiles", [])
        if any(p.get("name") == name for p in profiles):
            return False, f"Profile '{name}' already exists"
            
        ssh_key_path = profile_data.get("ssh_key_path")
        generate_ssh = profile_data.get("generate_ssh", False)
        signing_key = profile_data.get("signing_key")
        
        if generate_ssh:
            try:
                ssh_key_path = profile_cmd.generate_ssh_key(name, email)
                pub_key_path = f"{ssh_key_path}.pub"
                if os.path.exists(pub_key_path):
                    with open(pub_key_path, 'r', encoding='utf-8') as f:
                        signing_key = f.read().strip()
            except Exception as e:
                return False, f"Failed to generate SSH key: {e}"
                
        new_profile = {
            "name": name,
            "email": email,
            "active": False
        }
        if signing_key:
            new_profile["signing_key"] = signing_key
        if ssh_key_path:
            new_profile["ssh_key_path"] = ssh_key_path
        if profile_data.get("git_token"):
            new_profile["git_token"] = profile_data["git_token"]
            
        profiles.append(new_profile)
        data["profiles"] = profiles
        profile_cmd.save_profiles(data)
        
        if profile_data.get("switch_after", False):
            switch_active_profile(name)
            
        return True, "Profile added successfully"
    except Exception as e:
        return False, str(e)

def get_ssh_public_key(profile_name=None):
    try:
        data = profile_cmd.load_profiles()
        profiles = data.get("profiles", [])
        
        target = None
        if profile_name:
            target = next((p for p in profiles if p.get("name") == profile_name), None)
        else:
            target = next((p for p in profiles if p.get("active")), None)
            
        if not target:
            return None, "Profile not found"
            
        ssh_key = target.get("ssh_key_path")
        if not ssh_key:
            return None, "No SSH key path registered for this profile"
            
        pub_key_path = f"{os.path.abspath(os.path.expanduser(ssh_key))}.pub"
        if not os.path.exists(pub_key_path):
            return None, f"Public key file not found at '{pub_key_path}'"
            
        with open(pub_key_path, 'r', encoding='utf-8') as f:
            pub_content = f.read().strip()
        return pub_content, None
    except Exception as e:
        return None, str(e)

def acquire_module_lock(module):
    try:
        branch = "unknown"
        try:
            res = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=subprocess.PIPE, text=True)
            branch = res.stdout.strip()
        except Exception:
            pass

        locks = lock_cmd.load_locks()
        if module in locks:
            if locks[module] == branch:
                return True, f"Module '{module}' is already locked by you (branch '{branch}')."
            else:
                return False, f"Error: Module '{module}' is already locked by branch '{locks[module]}'!"
        else:
            locks[module] = branch
            lock_cmd.save_locks(locks)
            return True, f"Successfully acquired lock on module '{module}' for branch '{branch}'."
    except Exception as e:
        return False, str(e)

def release_module_lock(module):
    try:
        locks = lock_cmd.load_locks()
        if module in locks:
            del locks[module]
            lock_cmd.save_locks(locks)
            return True, f"Successfully released lock on module '{module}'."
        else:
            return False, f"Module '{module}' is not currently locked."
    except Exception as e:
        return False, str(e)

def record_learned_lesson(lesson, category):
    try:
        if not lesson:
            return False, "Lesson description cannot be empty."
        learn_cmd.record_lesson(lesson, category)
        # Auto-sync workspace to rebuild rules.md!
        run_sync_workspace()
        return True, "Lesson recorded and rules synchronized successfully."
    except Exception as e:
        return False, str(e)

def run_sync_workspace():
    try:
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../sync.py'))
        if not os.path.exists(script_path):
            return False, f"Sync script not found at '{script_path}'"
        spec = importlib.util.spec_from_file_location("sync_module", script_path)
        sync_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sync_module)
        sync_module.sync_skills_to_agents_md()
        sync_module.sync_adrs_to_architecture_md()
        sync_module.sync_lessons_to_rules()
        return True, "Workspace synchronized successfully."
    except Exception as e:
        return False, str(e)

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

class DashboardHandler(BaseHTTPRequestHandler):
    def is_client_allowed(self) -> bool:
        if os.environ.get("AAC_DASHBOARD_ALLOW_EXTERNAL") == "true":
            return True
        
        # Verify client address IP
        client_ip = self.client_address[0]
        if client_ip not in ('127.0.0.1', '::1', 'localhost'):
            return False
            
        # Verify Origin header to prevent CSRF
        origin = self.headers.get('Origin')
        if origin:
            parsed_origin = urlparse(origin)
            if parsed_origin.hostname not in ('localhost', '127.0.0.1', '::1', None):
                return False
                
        # Verify Referer header to prevent CSRF
        referer = self.headers.get('Referer')
        if referer:
            parsed_referer = urlparse(referer)
            if parsed_referer.hostname not in ('localhost', '127.0.0.1', '::1', None):
                return False
                
        return True

    def reject_request(self):
        self.send_response(403)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b"Forbidden: External connections are not allowed.")

    def do_GET(self):
        if not self.is_client_allowed():
            self.reject_request()
            return
        parsed_url = urlparse(self.path)
        if parsed_url.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.end_headers()
            try:
                query = parse_qs(parsed_url.query)
                force = query.get('force', ['false'])[0].lower() == 'true'
                data = get_dashboard_data(force=force)
                self.wfile.write(json.dumps(data).encode('utf-8'))
            except Exception as e:
                err_response = {"error": str(e)}
                self.wfile.write(json.dumps(err_response).encode('utf-8'))
        elif parsed_url.path == '/api/profiles':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.end_headers()
            try:
                data = profile_cmd.load_profiles()
                self.wfile.write(json.dumps(data).encode('utf-8'))
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        elif parsed_url.path == '/api/ssh/public-key':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.end_headers()
            try:
                query = parse_qs(parsed_url.query)
                profile_name = query.get('profile', [None])[0]
                pub_key, err = get_ssh_public_key(profile_name)
                if err:
                    self.wfile.write(json.dumps({"error": err}).encode('utf-8'))
                else:
                    self.wfile.write(json.dumps({"public_key": pub_key}).encode('utf-8'))
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.serve_static_file(parsed_url.path)

    def do_POST(self):
        if not self.is_client_allowed():
            self.reject_request()
            return
        parsed_url = urlparse(self.path)
        if parsed_url.path == '/api/task/toggle':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                req = json.loads(post_data.decode('utf-8'))
                task_index = int(req.get('taskIndex'))
                completed = bool(req.get('completed'))
                success = toggle_issue_task(task_index, completed)
                
                self.send_response(200 if success else 400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": success}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        elif parsed_url.path == '/api/profiles/switch':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                req = json.loads(post_data.decode('utf-8'))
                profile_name = req.get('name')
                success, msg = switch_active_profile(profile_name)
                self.send_response(200 if success else 400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": success, "message": msg}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        elif parsed_url.path == '/api/profiles/add':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                req = json.loads(post_data.decode('utf-8'))
                success, msg = add_new_profile(req)
                self.send_response(200 if success else 400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": success, "message": msg}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        elif parsed_url.path == '/api/locks/acquire':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                req = json.loads(post_data.decode('utf-8'))
                module_name = req.get('module')
                success, msg = acquire_module_lock(module_name)
                self.send_response(200 if success else 400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": success, "message": msg}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        elif parsed_url.path == '/api/locks/release':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                req = json.loads(post_data.decode('utf-8'))
                module_name = req.get('module')
                success, msg = release_module_lock(module_name)
                self.send_response(200 if success else 400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": success, "message": msg}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        elif parsed_url.path == '/api/learn':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                req = json.loads(post_data.decode('utf-8'))
                lesson = req.get('lesson')
                category = req.get('category')
                success, msg = record_learned_lesson(lesson, category)
                self.send_response(200 if success else 400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": success, "message": msg}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        elif parsed_url.path == '/api/sync':
            try:
                success, msg = run_sync_workspace()
                self.send_response(200 if success else 400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": success, "message": msg}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def serve_static_file(self, path):
        workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
        dashboard_dir = os.path.join(workspace_root, ".agents", "dashboard")
        
        clean_path = path.lstrip('/')
        if not clean_path or clean_path == 'index.html':
            clean_path = 'index.html'
            
        filepath = os.path.abspath(os.path.join(dashboard_dir, clean_path))
        
        # Path Traversal Guard: verify the resolved path starts with dashboard_dir
        base_dir = os.path.abspath(dashboard_dir)
        if not base_dir.endswith(os.path.sep):
            base_dir += os.path.sep
            
        if not filepath.startswith(base_dir) and filepath != os.path.abspath(dashboard_dir):
            self.send_response(403)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(b"Forbidden: Directory Traversal Blocked")
            return
            
        if os.path.exists(filepath) and os.path.isfile(filepath):
            content_type, _ = mimetypes.guess_type(filepath)
            if not content_type:
                content_type = 'application/octet-stream'
                
            self.send_response(200)
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            if content_type.startswith('text/') or content_type in ('application/javascript', 'application/json'):
                self.send_header('Content-Type', f'{content_type}; charset=utf-8')
            else:
                self.send_header('Content-Type', content_type)
            self.end_headers()
            try:
                with open(filepath, 'rb') as f:
                    self.wfile.write(f.read())
            except Exception as e:
                self.wfile.write(f"Error reading file: {e}".encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(b"Not Found")

    # Override log_message to prevent terminal cluttering
    def log_message(self, format, *args):
        pass

def initial_audit_worker():
    global LATEST_DATA, audit_in_progress
    with audit_thread_lock:
        audit_in_progress = True
    try:
        compliance = run_silent_validation()
        with data_lock:
            LATEST_DATA["compliance"] = compliance
    finally:
        with audit_thread_lock:
            audit_in_progress = False
    initial_data_loaded.set()

def run(args):
    # Spawn background thread to populate initial compliance cache asynchronously
    t = threading.Thread(target=initial_audit_worker, daemon=True)
    t.start()

    host = '127.0.0.1'
    port = 8000
    allow_external = False

    # Argument parsing
    i = 0
    while i < len(args):
        arg = args[i].lower()
        if arg == '--host':
            if i + 1 < len(args):
                host = args[i+1]
                i += 1
        elif arg == '--port':
            if i + 1 < len(args):
                try:
                    port = int(args[i+1])
                except ValueError:
                    print(f"\033[91mError: Invalid port number '{args[i+1]}'.\033[0m")
                    sys.exit(1)
                i += 1
        elif arg == '--allow-external':
            allow_external = True
        i += 1

    if os.environ.get("AAC_DASHBOARD_ALLOW_EXTERNAL") == "true":
        allow_external = True

    if host not in ('127.0.0.1', '::1', 'localhost'):
        allow_external = True

    if allow_external:
        os.environ["AAC_DASHBOARD_ALLOW_EXTERNAL"] = "true"

    server = None
    # Auto port binding if port is default, otherwise try the specified port first
    start_port = port
    while port < start_port + 20:
        try:
            server = ThreadingHTTPServer((host, port), DashboardHandler)
            break
        except OSError:
            if start_port != 8000:
                print(f"\033[91mError: Could not bind HTTPServer to {host}:{port}.\033[0m")
                sys.exit(1)
            port += 1
            
    if not server:
        print(f"\033[91mError: Could not bind HTTPServer to any port between {start_port}-{start_port+20}.\033[0m")
        sys.exit(1)
        
    url = f"http://{host}:{port}/"
    if host == '0.0.0.0':
        url = f"http://127.0.0.1:{port}/ (accessible externally at your LAN IP)"

    print(f"\033[92m==========================================================\033[0m")
    print(f"\033[92m🚀 AAC V2 Local Dashboard Server started at: {url}\033[0m")
    if allow_external:
        print(f"\033[93m⚠️  [WARNING] External access is enabled! Make sure your network is secure.\033[0m")
    print(f"\033[92m==========================================================\033[0m")
    print("\033[93mPress Ctrl+C to terminate dashboard server.\033[0m\n")
    
    # Auto-open browser tab if not external-only/headless
    if host in ('127.0.0.1', '::1', 'localhost'):
        try:
            webbrowser.open_new_tab(f"http://127.0.0.1:{port}/")
        except Exception:
            pass
        
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard server...")
        sys.exit(0)
