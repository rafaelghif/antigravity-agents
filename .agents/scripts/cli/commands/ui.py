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
        # Silence server logs to stdout
        pass

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(HTML_UI.encode('utf-8'))
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
            
            # Simple run diagnostics and return list
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
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0f131a;
            --card-bg: rgba(22, 28, 38, 0.7);
            --border-color: rgba(255, 255, 255, 0.08);
            --text-primary: #f3f4f6;
            --text-secondary: #9ca3af;
            --accent: #2563eb;
            --accent-glow: rgba(37, 99, 235, 0.15);
            --success: #10b981;
            --success-glow: rgba(16, 185, 129, 0.15);
            --error: #ef4444;
            --warning: #f59e0b;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
        }

        header {
            background: linear-gradient(180deg, rgba(15, 19, 26, 0.9) 0%, rgba(15, 19, 26, 0.5) 100%);
            border-bottom: 1px solid var(--border-color);
            padding: 1.5rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            backdrop-filter: blur(10px);
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
            font-size: 1.75rem;
            animation: float 3s ease-in-out infinite;
        }

        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-4px); }
        }

        .logo-text {
            font-size: 1.25rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            background: linear-gradient(90deg, #60a5fa, #3b82f6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .tabs {
            display: flex;
            gap: 1rem;
        }

        .tab-btn {
            background: none;
            border: none;
            color: var(--text-secondary);
            font-size: 0.95rem;
            font-weight: 500;
            padding: 0.5rem 1rem;
            cursor: pointer;
            border-radius: 6px;
            transition: all 0.2s ease;
        }

        .tab-btn.active {
            color: var(--text-primary);
            background-color: rgba(255, 255, 255, 0.05);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
        }

        .tab-btn:hover:not(.active) {
            color: var(--text-primary);
            background-color: rgba(255, 255, 255, 0.02);
        }

        main {
            flex: 1;
            padding: 2rem;
            max-width: 1400px;
            width: 100%;
            margin: 0 auto;
        }

        .content-tab {
            display: none;
            animation: fadeIn 0.3s ease-in-out;
        }

        .content-tab.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(5px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Task Board Styles */
        .board-container {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1.5rem;
            min-height: 500px;
        }

        .board-col {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .col-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid var(--border-color);
        }

        .col-title {
            font-size: 1.05rem;
            font-weight: 600;
            color: var(--text-primary);
        }

        .col-count {
            background-color: rgba(255, 255, 255, 0.05);
            font-size: 0.8rem;
            padding: 0.2rem 0.5rem;
            border-radius: 10px;
            color: var(--text-secondary);
        }

        .task-list {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            overflow-y: auto;
        }

        .task-card {
            background-color: rgba(15, 19, 26, 0.6);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1rem;
            transition: all 0.2s ease;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .task-card:hover {
            border-color: rgba(255, 255, 255, 0.15);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }

        .task-title {
            font-size: 0.95rem;
            font-weight: 500;
            line-height: 1.4;
        }

        .task-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.8rem;
            color: var(--text-secondary);
        }

        .task-branch {
            background-color: rgba(59, 130, 246, 0.1);
            color: #60a5fa;
            padding: 0.15rem 0.4rem;
            border-radius: 4px;
            font-family: monospace;
        }

        .task-actions {
            display: flex;
            gap: 0.5rem;
            margin-top: 0.5rem;
        }

        .action-btn {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            padding: 0.35rem 0.6rem;
            font-size: 0.75rem;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s ease;
            flex: 1;
            text-align: center;
        }

        .action-btn:hover {
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(255, 255, 255, 0.2);
        }

        /* Profile Styles */
        .profiles-container {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 2rem;
        }

        .profile-list {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .profile-card {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.2s ease;
        }

        .profile-card.active {
            border-color: var(--success);
            box-shadow: 0 0 15px var(--success-glow);
        }

        .profile-info {
            display: flex;
            flex-direction: column;
            gap: 0.35rem;
        }

        .profile-name {
            font-size: 1.1rem;
            font-weight: 600;
        }

        .profile-email {
            font-size: 0.9rem;
            color: var(--text-secondary);
        }

        .profile-keys {
            display: flex;
            gap: 0.5rem;
            margin-top: 0.25rem;
            font-size: 0.75rem;
        }

        .key-badge {
            background: rgba(255, 255, 255, 0.05);
            padding: 0.15rem 0.4rem;
            border-radius: 4px;
            color: var(--text-secondary);
        }

        .switch-btn {
            background-color: var(--accent);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .switch-btn:hover {
            box-shadow: 0 0 10px var(--accent-glow);
            filter: brightness(1.1);
        }

        .switch-btn.active-btn {
            background-color: transparent;
            border: 1px solid var(--success);
            color: var(--success);
            cursor: default;
        }

        .add-profile-form {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .form-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 0.35rem;
        }

        .form-group label {
            font-size: 0.85rem;
            color: var(--text-secondary);
        }

        .form-group input, .form-group select {
            background-color: rgba(15, 19, 26, 0.6);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            padding: 0.6rem;
            border-radius: 6px;
            font-family: inherit;
            outline: none;
        }

        .form-group input:focus {
            border-color: var(--accent);
        }

        .submit-btn {
            background-color: var(--success);
            color: white;
            border: none;
            padding: 0.6rem;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            margin-top: 0.5rem;
        }

        .submit-btn:hover {
            filter: brightness(1.1);
        }

        /* Doctor Styles */
        .doctor-container {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .doctor-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 1rem;
        }

        .run-doctor-btn {
            background-color: var(--accent);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .diagnostic-list {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }

        .diagnostic-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem 1rem;
            background: rgba(15, 19, 26, 0.4);
            border: 1px solid var(--border-color);
            border-radius: 6px;
        }

        .status-badge {
            font-size: 0.8rem;
            font-weight: 600;
            padding: 0.2rem 0.6rem;
            border-radius: 10px;
        }

        .status-badge.PASS {
            background-color: var(--success-glow);
            color: var(--success);
        }

        .status-badge.FAIL {
            background-color: rgba(239, 68, 68, 0.15);
            color: var(--error);
        }

        .status-badge.WARN {
            background-color: rgba(245, 158, 11, 0.15);
            color: var(--warning);
        }
    </style>
</head>
<body>
    <header>
        <div class="logo-container">
            <span class="logo-icon">🚀</span>
            <span class="logo-text">AAC V2 Web UI</span>
        </div>
        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('board')">Task Board</button>
            <button class="tab-btn" onclick="switchTab('profiles')">Profiles</button>
            <button class="tab-btn" onclick="switchTab('doctor')">Diagnostics</button>
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
                    <h3 class="form-title">Add Developer Profile</h3>
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

        // Board Fetching & Movement
        async function fetchBoard() {
            const res = await fetch('/api/board');
            const data = await res.json();
            
            document.getElementById('count-todo').innerText = data.todo.length;
            document.getElementById('count-doing').innerText = data.doing.length;
            document.getElementById('count-done').innerText = data.done.length;
            
            renderColumn('todo', data.todo, ['doing']);
            renderColumn('doing', data.doing, ['todo', 'done']);
            renderColumn('done', data.done, ['doing']);
        }

        function renderColumn(colId, tasks, allowedTargets) {
            const container = document.getElementById('list-' + colId);
            container.innerHTML = '';
            
            tasks.forEach(t => {
                const card = document.createElement('div');
                card.className = 'task-card';
                
                let branchHtml = t.branch ? `<span class="task-branch">${t.branch}</span>` : '';
                
                let actionsHtml = '';
                allowedTargets.forEach(target => {
                    let label = target === 'doing' ? 'Start Task' : (target === 'done' ? 'Complete' : 'To Todo');
                    actionsHtml += `<button class="action-btn" onclick="moveTask('${t.id}', '${target}')">${label}</button>`;
                });
                
                card.innerHTML = `
                    <span class="task-title">${t.title}</span>
                    <div class="task-meta">
                        <span>ID: ${t.id}</span>
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
                if (p.signing_key) keysHtml += `<span class="key-badge">GPG: ${p.signing_key}</span>`;
                if (p.ssh_key_path) keysHtml += `<span class="key-badge">SSH: ${p.ssh_key_path.split('/').pop()}</span>`;
                if (p.git_token) keysHtml += `<span class="key-badge">PAT Configured</span>`;
                
                let btnHtml = p.active 
                    ? `<button class="switch-btn active-btn">Active</button>` 
                    : `<button class="switch-btn" onclick="switchProfile('${p.name}')">Switch</button>`;
                
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
            container.innerHTML = '<p style="color: var(--text-secondary);">Auditing local configurations...</p>';
            
            const res = await fetch('/api/diagnostics');
            const data = await res.json();
            
            container.innerHTML = '';
            data.forEach(d => {
                const row = document.createElement('div');
                row.className = 'diagnostic-row';
                row.innerHTML = `
                    <span>${d.name}</span>
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
