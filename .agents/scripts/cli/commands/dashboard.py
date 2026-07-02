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
from urllib.parse import urlparse, parse_qs
from socketserver import ThreadingMixIn

# Thread-safe compliance status cache
LATEST_DATA = {}
data_lock = threading.Lock()
initial_data_loaded = threading.Event()

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
    locks_path = ".agents/locks.json"
    if os.path.exists(locks_path):
        try:
            with open(locks_path, 'r', encoding='utf-8') as f:
                lock_data = json.load(f)
            for module, info in lock_data.items():
                locks.append({
                    "module": module,
                    "branch": info.get("branch", "unknown"),
                    "timestamp": info.get("timestamp", "unknown")
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
    compliance = {}
    if force:
        compliance = run_silent_validation()
        with data_lock:
            LATEST_DATA["compliance"] = compliance
    else:
        with data_lock:
            compliance = LATEST_DATA.get("compliance", DEFAULT_COMPLIANCE)

    return {
        "version": version,
        "locks": locks,
        "active_issue": active_issue,
        "git_status": git_status,
        "lessons": lessons,
        "rules": rules,
        "changelog": changelog_releases[:5], # top 5 releases
        "compliance": compliance,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            try:
                query = parse_qs(parsed_url.query)
                force = query.get('force', ['false'])[0].lower() == 'true'
                data = get_dashboard_data(force=force)
                self.wfile.write(json.dumps(data).encode('utf-8'))
            except Exception as e:
                err_response = {"error": str(e)}
                self.wfile.write(json.dumps(err_response).encode('utf-8'))
        elif parsed_url.path in ('/', '/index.html'):
            self.serve_static_file('index.html', 'text/html')
        elif parsed_url.path == '/style.css':
            self.serve_static_file('style.css', 'text/css')
        elif parsed_url.path == '/app.js':
            self.serve_static_file('app.js', 'application/javascript')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def do_POST(self):
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
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def serve_static_file(self, filename, content_type):
        workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
        filepath = os.path.join(workspace_root, ".agents", "dashboard", filename)
        if os.path.exists(filepath):
            self.send_response(200)
            self.send_header('Content-Type', f'{content_type}; charset=utf-8')
            self.end_headers()
            try:
                with open(filepath, 'rb') as f:
                    self.wfile.write(f.read())
            except Exception as e:
                self.wfile.write(f"Error reading file: {e}".encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"File Not Found")

    # Override log_message to prevent terminal cluttering
    def log_message(self, format, *args):
        pass

def initial_audit_worker():
    global LATEST_DATA
    compliance = run_silent_validation()
    with data_lock:
        LATEST_DATA["compliance"] = compliance
    initial_data_loaded.set()

def run(args):
    # Spawn background thread to populate initial compliance cache asynchronously
    t = threading.Thread(target=initial_audit_worker, daemon=True)
    t.start()

    port = 8000
    server = None
    # Auto port binding to avoid port conflicts
    while port < 8020:
        try:
            server = ThreadingHTTPServer(('127.0.0.1', port), DashboardHandler)
            break
        except OSError:
            port += 1
            
    if not server:
        print("\033[91mError: Could not bind HTTPServer to any local port between 8000-8020.\033[0m")
        sys.exit(1)
        
    url = f"http://127.0.0.1:{port}/"
    print(f"\033[92m==========================================================\033[0m")
    print(f"\033[92m🚀 AAC V2 Local Dashboard Server started at: {url}\033[0m")
    print(f"\033[92m==========================================================\033[0m")
    print("\033[93mPress Ctrl+C to terminate dashboard server.\033[0m\n")
    
    # Auto-open browser tab
    try:
        webbrowser.open_new_tab(url)
    except Exception:
        pass
        
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\033[93mDashboard server stopped. Exiting.\033[0m")
        sys.exit(0)
