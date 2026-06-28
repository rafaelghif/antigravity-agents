import sys
import os
import re
import json
import subprocess
import shutil
import http.server
import socketserver
import webbrowser
from typing import List

# Setup sys.path to import commands easily
commands_dir = os.path.dirname(os.path.abspath(__file__))
if commands_dir not in sys.path:
    sys.path.insert(0, commands_dir)

import profile as profile_cmd
import doctor as doctor_cmd

PORT = 8520

def parse_board_md() -> dict:
    board_path = ".agents/tasks/board.md"
    sections = {"todo": [], "doing": [], "done": []}
    if not os.path.exists(board_path):
        return sections
        
    with open(board_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    current_section = None
    for line in content.splitlines():
        line_stripped = line.strip()
        if line_stripped == "## Todo":
            current_section = "todo"
        elif line_stripped == "## Doing":
            current_section = "doing"
        elif line_stripped == "## Done":
            current_section = "done"
        elif line_stripped.startswith("- ["):
            is_completed = line_stripped.startswith("- [x]")
            title = ""
            branch = ""
            issue_id = ""
            
            id_match = re.search(r"<!--\s*id:\s*([^\s-]+-\d+|[^\s>]+)\s*-->", line_stripped)
            if id_match:
                issue_id = id_match.group(1)
                
            branch_match = re.search(r"\(([^)]+)\)", line_stripped)
            if branch_match:
                branch = branch_match.group(1)
                
            raw_title = line_stripped[5:].strip()
            if branch_match:
                raw_title = raw_title.split("(" + branch)[0].strip()
            elif id_match:
                raw_title = raw_title.split("<!--")[0].strip()
                
            title = raw_title
            
            task_item = {
                "id": issue_id or title,
                "title": title,
                "branch": branch,
                "completed": is_completed,
                "raw_line": line
            }
            if current_section:
                sections[current_section].append(task_item)
    return sections

def update_board_task_status(task_id: str, new_status: str) -> bool:
    board_path = ".agents/tasks/board.md"
    if not os.path.exists(board_path):
        return False
        
    with open(board_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    lines = content.splitlines()
    target_task_line = None
    
    # Locate task line
    for line in lines:
        if f"id: {task_id}" in line or (task_id in line and line.strip().startswith("- [")):
            target_task_line = line
            break
            
    if not target_task_line:
        return False
        
    # Rebuild line with correct completion box
    cleaned_line = target_task_line.strip()
    if new_status == "done":
        if cleaned_line.startswith("- [ ]"):
            cleaned_line = "- [x]" + cleaned_line[5:]
    else:
        if cleaned_line.startswith("- [x]"):
            cleaned_line = "- [ ]" + cleaned_line[5:]
            
    # Remove old line from lines
    updated_lines = [l for l in lines if l != target_task_line]
    
    # Insert under new section
    section_headers = {
        "todo": "## Todo",
        "doing": "## Doing",
        "done": "## Done"
    }
    target_header = section_headers.get(new_status)
    
    final_lines = []
    inserted = False
    for line in updated_lines:
        final_lines.append(line)
        if line.strip() == target_header and not inserted:
            final_lines.append(f"  {cleaned_line}")
            inserted = True
            
    with open(board_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(final_lines) + "\n")
    return True

class AACWebHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(HTML_UI.encode('utf-8'))
        elif self.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            # Get current git branch
            branch = "main"
            res_branch = subprocess.run(['git', 'branch', '--show-current'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res_branch.returncode == 0:
                branch = res_branch.stdout.strip()
                
            # Get active profile
            active_profile = "None"
            profiles_file = ".agents/git_profiles.json"
            if os.path.exists(profiles_file):
                try:
                    with open(profiles_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        active = next((p for p in data.get("profiles", []) if p.get("active")), None)
                        if active:
                            active_profile = active.get("name")
                except Exception:
                    pass
                    
            status_data = {
                "branch": branch,
                "profile": active_profile,
                "version": "2.73.0"
            }
            self.wfile.write(json.dumps(status_data).encode('utf-8'))
        elif self.path == "/api/board":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            data = parse_board_md()
            self.wfile.write(json.dumps(data).encode('utf-8'))
        elif self.path == "/api/profiles":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            profiles_file = ".agents/git_profiles.json"
            if os.path.exists(profiles_file):
                with open(profiles_file, 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode('utf-8'))
            else:
                self.wfile.write(json.dumps({"profiles": []}).encode('utf-8'))
        elif self.path == "/api/diagnostics":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            results = []
            results.append({"name": "Python Environment", "status": "PASS" if doctor_cmd.check_python() else "FAIL"})
            results.append({"name": "Git CLI Installation", "status": "PASS" if doctor_cmd.check_git() else "FAIL"})
            results.append({"name": "Git Workspace Tree", "status": "PASS" if doctor_cmd.check_worktree() else "FAIL"})
            results.append({"name": "Git Identity Setup", "status": "PASS" if doctor_cmd.check_identity() else "FAIL"})
            results.append({"name": "Developer Profiles Setup", "status": "PASS" if doctor_cmd.check_profiles() else "FAIL"})
            results.append({"name": "Network Connectivity", "status": "PASS" if doctor_cmd.check_network() else "WARN"})
            
            self.wfile.write(json.dumps(results).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        if self.path == "/api/board/move":
            try:
                params = json.loads(post_data)
                task_id = params.get("id")
                new_status = params.get("status")
                
                success = update_board_task_status(task_id, new_status)
                self.send_response(200 if success else 400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": success}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode('utf-8'))
                
        elif self.path == "/api/profiles/switch":
            try:
                params = json.loads(post_data)
                profile_name = params.get("name")
                
                # Switch active profile
                profile_cmd.handle_switch([profile_name])
                
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode('utf-8'))
                
        elif self.path == "/api/profiles/add":
            try:
                params = json.loads(post_data)
                name = params.get("name")
                email = params.get("email")
                signing_key = params.get("signing_key")
                ssh_key_path = params.get("ssh_key_path")
                git_token = params.get("git_token")
                
                # Save new profile to JSON
                profiles_file = ".agents/git_profiles.json"
                data = {"profiles": []}
                if os.path.exists(profiles_file):
                    with open(profiles_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                new_profile = {
                    "name": name,
                    "email": email,
                    "active": False
                }
                if signing_key: new_profile["signing_key"] = signing_key
                if ssh_key_path: new_profile["ssh_key_path"] = ssh_key_path
                if git_token: new_profile["git_token"] = git_token
                
                data["profiles"].append(new_profile)
                with open(profiles_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                    
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run(args: List[str]) -> None:
    print("="*60)
    print("      Antigravity Agent Core (AAC) V2 Web Dashboard")
    print("="*60)
    
    server_address = ('127.0.0.1', PORT)
    try:
        handler = AACWebHandler
        with socketserver.TCPServer(server_address, handler) as httpd:
            print(f"[OK] AAC Web UI running at: http://127.0.0.1:{PORT}/")
            print("Press Ctrl+C to stop the dashboard server.")
            
            # Automatically launch browser
            webbrowser.open(f"http://127.0.0.1:{PORT}/")
            
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Dashboard server stopped successfully.")
    except Exception as e:
        print(f"[FAIL] Error launching dashboard server: {e}")
        sys.exit(1)

# Embed visual HTML/CSS/JS frontend
HTML_UI = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Antigravity Agent Core Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0b0f17;
            --card-bg: rgba(22, 28, 45, 0.45);
            --card-border: rgba(255, 255, 255, 0.05);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent: #3b82f6;
            --accent-glow: rgba(59, 130, 246, 0.25);
            --success: #10b981;
            --success-glow: rgba(16, 185, 129, 0.2);
            --error: #f43f5e;
            --warning: #f59e0b;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Plus Jakarta Sans', 'Outfit', sans-serif;
            background-color: var(--bg-color);
            background-image: 
                radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.12) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(16, 185, 129, 0.08) 0px, transparent 50%);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
        }

        header {
            background: rgba(11, 15, 23, 0.7);
            border-bottom: 1px solid var(--card-border);
            padding: 1.25rem 2.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            backdrop-filter: blur(20px);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .logo-container {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .logo-icon {
            font-size: 1.85rem;
            background: linear-gradient(135deg, #60a5fa, #3b82f6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: float 4s ease-in-out infinite;
        }

        @keyframes float {
            0%, 100% { transform: translateY(0) rotate(0deg); }
            50% { transform: translateY(-4px) rotate(5deg); }
        }

        .logo-text {
            font-size: 1.35rem;
            font-weight: 700;
            letter-spacing: -0.5px;
            background: linear-gradient(90deg, #f8fafc, #cbd5e1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .tabs {
            display: flex;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--card-border);
            padding: 0.35rem;
            border-radius: 30px;
            gap: 0.25rem;
        }

        .tab-btn {
            background: none;
            border: none;
            color: var(--text-secondary);
            font-size: 0.9rem;
            font-weight: 600;
            padding: 0.5rem 1.25rem;
            cursor: pointer;
            border-radius: 20px;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .tab-btn.active {
            color: var(--text-primary);
            background-color: var(--accent);
            box-shadow: 0 4px 12px var(--accent-glow);
        }

        .tab-btn:hover:not(.active) {
            color: var(--text-primary);
            background-color: rgba(255, 255, 255, 0.05);
        }

        /* Status Widget */
        .status-widget {
            display: flex;
            gap: 1.5rem;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--card-border);
            padding: 0.5rem 1.25rem;
            border-radius: 12px;
            font-size: 0.85rem;
        }

        .status-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: var(--success);
            box-shadow: 0 0 8px var(--success-glow);
        }

        main {
            flex: 1;
            padding: 2.5rem;
            max-width: 1400px;
            width: 100%;
            margin: 0 auto;
        }

        .content-tab {
            display: none;
            animation: slideUp 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .content-tab.active {
            display: block;
        }

        @keyframes slideUp {
            from { opacity: 0; transform: translateY(12px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Task Board Column Design */
        .board-container {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 2rem;
            min-height: 600px;
        }

        .board-col {
            background-color: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
            backdrop-filter: blur(16px);
        }

        .col-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 1rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }

        .col-title {
            font-size: 1.1rem;
            font-weight: 700;
            letter-spacing: -0.2px;
        }

        .col-count {
            background-color: rgba(255, 255, 255, 0.06);
            font-size: 0.8rem;
            font-weight: 600;
            padding: 0.25rem 0.65rem;
            border-radius: 20px;
            color: var(--text-secondary);
            border: 1px solid var(--card-border);
        }

        .task-list {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            overflow-y: auto;
        }

        /* Task Cards */
        .task-card {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.7) 100%);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 12px;
            padding: 1.25rem;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }

        .task-card:hover {
            border-color: rgba(59, 130, 246, 0.35);
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
        }

        .task-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.8rem;
        }

        .task-branch {
            background-color: rgba(59, 130, 246, 0.12);
            color: #93c5fd;
            padding: 0.2rem 0.5rem;
            border-radius: 6px;
            font-family: monospace;
            font-weight: 600;
            border: 1px solid rgba(59, 130, 246, 0.2);
        }

        .task-actions {
            display: flex;
            gap: 0.5rem;
            margin-top: 0.5rem;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            padding-top: 0.75rem;
        }

        .action-btn {
            border: none;
            color: white;
            padding: 0.5rem 0.75rem;
            font-size: 0.8rem;
            font-weight: 700;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.35rem;
        }

        .primary-btn {
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            box-shadow: 0 4px 10px rgba(29, 78, 216, 0.3);
        }

        .primary-btn:hover {
            filter: brightness(1.1);
            box-shadow: 0 4px 15px rgba(29, 78, 216, 0.5);
        }

        .secondary-btn {
            background: rgba(255, 255, 255, 0.05);
            color: var(--text-secondary);
            border: 1px solid var(--card-border);
        }

        .secondary-btn:hover {
            background: rgba(255, 255, 255, 0.1);
            color: var(--text-primary);
        }

        .success-btn {
            background: linear-gradient(135deg, #10b981, #047857);
            box-shadow: 0 4px 10px rgba(4, 120, 87, 0.3);
        }

        .success-btn:hover {
            filter: brightness(1.1);
            box-shadow: 0 4px 15px rgba(4, 120, 87, 0.5);
        }

        .warning-btn {
            background: linear-gradient(135deg, #f59e0b, #d97706);
            box-shadow: 0 4px 10px rgba(217, 119, 6, 0.3);
        }

        .warning-btn:hover {
            filter: brightness(1.1);
            box-shadow: 0 4px 15px rgba(217, 119, 6, 0.5);
        }

        /* Profile Styles */
        .profiles-container {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 2.5rem;
        }

        .profile-list {
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
        }

        .profile-card {
            background-color: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 1.75rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.25s ease;
            backdrop-filter: blur(16px);
        }

        .profile-card.active {
            border-color: var(--success);
            box-shadow: 0 0 25px var(--success-glow);
            background: linear-gradient(135deg, rgba(22, 28, 45, 0.6) 0%, rgba(16, 185, 129, 0.04) 100%);
        }

        .profile-info {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .profile-name {
            font-size: 1.25rem;
            font-weight: 700;
            letter-spacing: -0.2px;
        }

        .profile-email {
            font-size: 0.95rem;
            color: var(--text-secondary);
        }

        .profile-keys {
            display: flex;
            gap: 0.5rem;
            margin-top: 0.5rem;
            font-size: 0.75rem;
        }

        .key-badge {
            background: rgba(255, 255, 255, 0.05);
            padding: 0.25rem 0.55rem;
            border-radius: 6px;
            color: var(--text-secondary);
            border: 1px solid var(--card-border);
        }

        .switch-btn {
            background-color: var(--accent);
            color: white;
            border: none;
            padding: 0.6rem 1.25rem;
            border-radius: 10px;
            font-weight: 700;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .switch-btn:hover {
            box-shadow: 0 0 15px var(--accent-glow);
            filter: brightness(1.1);
        }

        .switch-btn.active-btn {
            background-color: transparent;
            border: 1.5px solid var(--success);
            color: var(--success);
            cursor: default;
        }

        .add-profile-form {
            background-color: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 1.75rem;
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
            backdrop-filter: blur(16px);
        }

        .form-title {
            font-size: 1.2rem;
            font-weight: 700;
            letter-spacing: -0.2px;
            margin-bottom: 0.25rem;
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .form-group label {
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-secondary);
        }

        .form-group input {
            background-color: rgba(15, 19, 26, 0.6);
            border: 1px solid var(--card-border);
            color: var(--text-primary);
            padding: 0.75rem 1rem;
            border-radius: 10px;
            font-family: inherit;
            outline: none;
            transition: all 0.2s ease;
        }

        .form-group input:focus {
            border-color: var(--accent);
            box-shadow: 0 0 8px var(--accent-glow);
        }

        .submit-btn {
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
            border: none;
            padding: 0.75rem;
            border-radius: 10px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s ease;
            margin-top: 0.5rem;
            box-shadow: 0 4px 10px var(--success-glow);
        }

        .submit-btn:hover {
            filter: brightness(1.1);
        }

        /* Doctor Styles */
        .doctor-container {
            background-color: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 2rem;
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
            backdrop-filter: blur(16px);
        }

        .doctor-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            padding-bottom: 1.25rem;
        }

        .doctor-header h2 {
            font-size: 1.35rem;
            font-weight: 700;
        }

        .run-doctor-btn {
            background: linear-gradient(135deg, #3b82f6, #2563eb);
            color: white;
            border: none;
            padding: 0.65rem 1.25rem;
            border-radius: 10px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 4px 12px var(--accent-glow);
        }

        .run-doctor-btn:hover {
            filter: brightness(1.1);
        }

        .diagnostic-list {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .diagnostic-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 1.5rem;
            background: rgba(15, 19, 26, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.03);
            border-radius: 12px;
            transition: all 0.2s ease;
        }

        .diagnostic-row:hover {
            border-color: rgba(255, 255, 255, 0.08);
            background: rgba(15, 19, 26, 0.7);
        }

        .diagnostic-name {
            font-weight: 600;
            font-size: 0.95rem;
        }

        .status-badge {
            font-size: 0.8rem;
            font-weight: 700;
            padding: 0.3rem 0.85rem;
            border-radius: 20px;
            letter-spacing: 0.5px;
        }

        .status-badge.PASS {
            background-color: var(--success-glow);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.2);
        }

        .status-badge.FAIL {
            background-color: rgba(244, 63, 94, 0.12);
            color: #fb7185;
            border: 1px solid rgba(244, 63, 94, 0.2);
        }

        .status-badge.WARN {
            background-color: rgba(245, 158, 11, 0.12);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.2);
        }
    </style>
</head>
<body>
    <header>
        <div class="logo-container">
            <span class="logo-icon">▲</span>
            <span class="logo-text">AAC WORKSPACE</span>
        </div>
        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('board')">Tasks Board</button>
            <button class="tab-btn" onclick="switchTab('profiles')">Credentials</button>
            <button class="tab-btn" onclick="switchTab('doctor')">Diagnostics</button>
        </div>
        <div class="status-widget">
            <div class="status-item">
                <span class="status-dot"></span>
                <span>Branch: <strong id="header-branch" style="color: #60a5fa; font-family: monospace;">main</strong></span>
            </div>
            <div class="status-item" style="border-left: 1px solid rgba(255,255,255,0.08); padding-left: 1rem;">
                <span>Profile: <strong id="header-profile" style="color: #34d399;">None</strong></span>
            </div>
        </div>
    </header>

    <main>
        <!-- Task Board Tab -->
        <section id="tab-board" class="content-tab active">
            <div class="board-container">
                <div class="board-col">
                    <div class="col-header">
                        <span class="col-title">Todo</span>
                        <span class="col-count" id="count-todo">0</span>
                    </div>
                    <div class="task-list" id="list-todo"></div>
                </div>
                <div class="board-col">
                    <div class="col-header">
                        <span class="col-title">Doing</span>
                        <span class="col-count" id="count-doing">0</span>
                    </div>
                    <div class="task-list" id="list-doing"></div>
                </div>
                <div class="board-col">
                    <div class="col-header">
                        <span class="col-title">Done</span>
                        <span class="col-count" id="count-done">0</span>
                    </div>
                    <div class="task-list" id="list-done"></div>
                </div>
            </div>
        </section>

        <!-- Profiles Tab -->
        <section id="tab-profiles" class="content-tab">
            <div class="profiles-container">
                <div class="profile-list" id="profile-cards-container"></div>
                <div class="add-profile-form">
                    <h3 class="form-title">Create Developer Profile</h3>
                    <p style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Register local GPG/SSH profiles to prevent Git email mismatches.</p>
                    <div class="form-group">
                        <label for="prof-name">Profile Name</label>
                        <input type="text" id="prof-name" placeholder="e.g. personal-work">
                    </div>
                    <div class="form-group">
                        <label for="prof-email">Git Config Email</label>
                        <input type="email" id="prof-email" placeholder="e.g. dev@test.com">
                    </div>
                    <div class="form-group">
                        <label for="prof-signing">Signing GPG Key (optional)</label>
                        <input type="text" id="prof-signing" placeholder="e.g. 4A1D5B">
                    </div>
                    <div class="form-group">
                        <label for="prof-ssh">SSH Key Path (optional)</label>
                        <input type="text" id="prof-ssh" placeholder="e.g. ~/.ssh/id_rsa">
                    </div>
                    <div class="form-group">
                        <label for="prof-token">GitHub Token PAT (optional)</label>
                        <input type="password" id="prof-token" placeholder="ghp_...">
                    </div>
                    <button class="submit-btn" onclick="addProfile()">Register Profile</button>
                </div>
            </div>
        </section>

        <!-- Doctor Tab -->
        <section id="tab-doctor" class="content-tab">
            <div class="doctor-container">
                <div class="doctor-header">
                    <h2>Diagnostics Doctor Checks</h2>
                    <button class="run-doctor-btn" onclick="runDiagnostics()">Run Audits</button>
                </div>
                <div class="diagnostic-list" id="diagnostic-results">
                    <p style="color: var(--text-secondary);">Click "Run Audits" to perform diagnostic sweeps.</p>
                </div>
            </div>
        </section>
    </main>

    <script>
        function switchTab(tabName) {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.content-tab').forEach(tab => tab.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById('tab-' + tabName).classList.add('active');
            
            if (tabName === 'board') fetchBoard();
            if (tabName === 'profiles') fetchProfiles();
        }

        // Fetch System Status (Header bar info)
        async function fetchSystemStatus() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                document.getElementById('header-branch').innerText = data.branch;
                document.getElementById('header-profile').innerText = data.profile;
            } catch (e) {
                console.error("Failed to load status info", e);
            }
        }

        // Board Fetching & Movement
        async function fetchBoard() {
            const res = await fetch('/api/board');
            const data = await res.json();
            
            document.getElementById('count-todo').innerText = data.todo.length;
            document.getElementById('count-doing').innerText = data.doing.length;
            document.getElementById('count-done').innerText = data.done.length;
            
            renderColumn('todo', data.todo);
            renderColumn('doing', data.doing);
            renderColumn('done', data.done);
            fetchSystemStatus();
        }

        function renderColumn(colId, tasks) {
            const container = document.getElementById('list-' + colId);
            container.innerHTML = '';
            
            tasks.forEach(t => {
                const card = document.createElement('div');
                card.className = 'task-card';
                
                let branchHtml = t.branch ? `<span class="task-branch">⌥ ${t.branch}</span>` : '';
                
                let actionsHtml = '';
                if (colId === 'todo') {
                    actionsHtml = `<button class="action-btn primary-btn" onclick="moveTask('${t.id}', 'doing')">🚀 Start Task</button>`;
                } else if (colId === 'doing') {
                    actionsHtml = `
                        <button class="action-btn secondary-btn" onclick="moveTask('${t.id}', 'todo')">↩ Move back</button>
                        <button class="action-btn success-btn" onclick="moveTask('${t.id}', 'done')">✓ Complete</button>
                    `;
                } else if (colId === 'done') {
                    actionsHtml = `<button class="action-btn warning-btn" onclick="moveTask('${t.id}', 'doing')">↺ Reopen Task</button>`;
                }
                
                card.innerHTML = `
                    <div style="font-weight: 600; font-size: 0.95rem; line-height: 1.4; color: #f8fafc;">${t.title}</div>
                    <div class="task-meta">
                        <span style="font-size: 0.75rem; color: #94a3b8;">ID: ${t.id}</span>
                        ${branchHtml}
                    </div>
                    <div class="task-actions">${actionsHtml}</div>
                `;
                container.appendChild(card);
            });
        }

        async function moveTask(taskId, targetStatus) {
            await fetch('/api/board/move', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: taskId, status: targetStatus })
            });
            fetchBoard();
        }

        // Profiles Management
        async function fetchProfiles() {
            const res = await fetch('/api/profiles');
            const data = await res.json();
            const container = document.getElementById('profile-cards-container');
            container.innerHTML = '';
            
            data.profiles.forEach(p => {
                const card = document.createElement('div');
                card.className = 'profile-card' + (p.active ? ' active' : '');
                
                let keysHtml = '';
                if (p.signing_key) keysHtml += `<span class="key-badge">🔑 GPG: ${p.signing_key}</span>`;
                if (p.ssh_key_path) keysHtml += `<span class="key-badge">⚙ SSH: ${p.ssh_key_path.split('/').pop()}</span>`;
                if (p.git_token) keysHtml += `<span class="key-badge">PAT Verified</span>`;
                
                let btnHtml = p.active 
                    ? `<button class="switch-btn active-btn">Active</button>` 
                    : `<button class="switch-btn" onclick="switchProfile('${p.name}')">Switch Profile</button>`;
                
                card.innerHTML = `
                    <div class="profile-info">
                        <span class="profile-name">${p.name}</span>
                        <span class="profile-email">${p.email}</span>
                        <div class="profile-keys">${keysHtml}</div>
                    </div>
                    <div>${btnHtml}</div>
                `;
                container.appendChild(card);
            });
            fetchSystemStatus();
        }

        async function switchProfile(name) {
            await fetch('/api/profiles/switch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name })
            });
            fetchProfiles();
        }

        async function addProfile() {
            const name = document.getElementById('prof-name').value;
            const email = document.getElementById('prof-email').value;
            const signing_key = document.getElementById('prof-signing').value;
            const ssh_key_path = document.getElementById('prof-ssh').value;
            const git_token = document.getElementById('prof-token').value;
            
            if (!name || !email) {
                alert('Profile Name and Email are required.');
                return;
            }
            
            await fetch('/api/profiles/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, signing_key, ssh_key_path, git_token })
            });
            
            // Reset form
            document.getElementById('prof-name').value = '';
            document.getElementById('prof-email').value = '';
            document.getElementById('prof-signing').value = '';
            document.getElementById('prof-ssh').value = '';
            document.getElementById('prof-token').value = '';
            
            fetchProfiles();
        }

        // Diagnostics Doctor
        async function runDiagnostics() {
            const container = document.getElementById('diagnostic-results');
            container.innerHTML = '<p style="color: var(--text-secondary);">Auditing workspace security and locks...</p>';
            
            const res = await fetch('/api/diagnostics');
            const data = await res.json();
            
            container.innerHTML = '';
            data.forEach(d => {
                const row = document.createElement('div');
                row.className = 'diagnostic-row';
                row.innerHTML = `
                    <span class="diagnostic-name">${d.name}</span>
                    <span class="status-badge ${d.status}">${d.status}</span>
                `;
                container.appendChild(row);
            });
        }

        // Initial Load
        fetchBoard();
    </script>
</body>
</html>
"""
