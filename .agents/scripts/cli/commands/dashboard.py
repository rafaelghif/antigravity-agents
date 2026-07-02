import sys
import os
import re
import json
import webbrowser
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

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

def get_dashboard_data():
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
    compliance = {
        "Critical Files": validate.audit_critical_files(),
        "Secrets & Ignored Files": validate.audit_secrets_and_ignored_files(),
        "Link Integrity": validate.audit_link_integrity(),
        "Git Branch Alignment": validate.audit_git_branch_alignment(),
        "Workspace Sync": validate.audit_workspace_sync(),
        "Task Board Schema": validate.audit_task_board_schema(),
        "Static Code Linting": validate.audit_static_linting(),
        "Local Unit Tests": validate.audit_unit_tests(),
        "Module Lock Compliance": validate.audit_module_locks(),
        "Commit Message Compliance": validate.audit_commit_messages()
    }

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

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Antigravity AAC V2 Local Dashboard</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-color: #0b0f19;
      --card-bg: #151d30;
      --card-border: #24324f;
      --text-main: #f1f5f9;
      --text-muted: #94a3b8;
      --accent-primary: #6366f1; /* Indigo */
      --accent-success: #10b981; /* Emerald */
      --accent-warning: #f59e0b; /* Amber */
      --accent-error: #ef4444; /* Rose */
      --gradient-brand: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
    }

    body {
      background-color: var(--bg-color);
      color: var(--text-main);
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      margin: 0;
      padding: 0;
      line-height: 1.5;
    }

    /* Header styling with brand gradient */
    header {
      background: var(--gradient-brand);
      padding: 2rem 2rem 2.5rem 2rem;
      border-bottom: 1px solid var(--card-border);
      position: relative;
    }

    .header-content {
      max-width: 1200px;
      margin: 0 auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .logo-area h1 {
      font-family: 'Outfit', sans-serif;
      font-size: 2.2rem;
      font-weight: 800;
      margin: 0;
      letter-spacing: -0.025em;
      text-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .logo-area p {
      margin: 0.25rem 0 0 0;
      color: rgba(255, 255, 255, 0.8);
      font-size: 0.95rem;
    }

    .badge {
      background: rgba(255, 255, 255, 0.2);
      backdrop-filter: blur(4px);
      padding: 0.35rem 0.8rem;
      border-radius: 20px;
      font-family: 'Fira Code', monospace;
      font-size: 0.85rem;
      font-weight: 600;
      border: 1px solid rgba(255, 255, 255, 0.25);
    }

    /* Container */
    .dashboard-container {
      max-width: 1200px;
      margin: -1.5rem auto 3rem auto;
      padding: 0 1.5rem;
    }

    /* Navigation Tabs */
    .tabs-bar {
      display: flex;
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 0.35rem;
      margin-bottom: 2rem;
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }

    .tab-btn {
      flex: 1;
      background: transparent;
      border: none;
      color: var(--text-muted);
      padding: 0.85rem 1rem;
      border-radius: 8px;
      font-size: 0.95rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      font-family: 'Outfit', sans-serif;
      text-align: center;
    }

    .tab-btn:hover {
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.05);
    }

    .tab-btn.active {
      color: #ffffff;
      background: var(--accent-primary);
      box-shadow: 0 4px 10px rgba(99, 102, 241, 0.3);
    }

    /* Layout structure */
    .tab-content {
      display: none;
    }

    .tab-content.active {
      display: block;
    }

    /* Grid Layouts */
    .overview-grid {
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 1.5rem;
    }

    @media (max-width: 900px) {
      .overview-grid {
        grid-template-columns: 1fr;
      }
    }

    /* Card Styling */
    .card {
      background-color: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 1.5rem;
      margin-bottom: 1.5rem;
      box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.4);
      transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .card:hover {
      border-color: #3b507a;
      transform: translateY(-2px);
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.25rem;
      border-bottom: 1px solid var(--card-border);
      padding-bottom: 0.75rem;
    }

    .card-header h2 {
      font-family: 'Outfit', sans-serif;
      font-size: 1.3rem;
      margin: 0;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .card-header .header-meta {
      font-size: 0.85rem;
      color: var(--text-muted);
    }

    /* Compliance check items */
    .compliance-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.75rem 1rem;
      background: rgba(255, 255, 255, 0.02);
      margin-bottom: 0.6rem;
      border-radius: 8px;
      border: 1px solid rgba(255, 255, 255, 0.03);
    }

    .compliance-item .name {
      font-size: 0.95rem;
      font-weight: 500;
    }

    .status-badge {
      padding: 0.25rem 0.65rem;
      border-radius: 12px;
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .status-badge.pass {
      background: rgba(16, 185, 129, 0.15);
      color: var(--accent-success);
      border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .status-badge.fail {
      background: rgba(239, 68, 68, 0.15);
      color: var(--accent-error);
      border: 1px solid rgba(239, 68, 68, 0.3);
    }

    /* Task Checklist */
    .task-item {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.65rem 0.5rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }

    .task-item:last-child {
      border-bottom: none;
    }

    .task-checkbox {
      width: 18px;
      height: 18px;
      accent-color: var(--accent-primary);
    }

    .task-label {
      font-size: 0.95rem;
    }

    .task-label.checked {
      color: var(--text-muted);
      text-decoration: line-through;
    }

    /* Lock List */
    .lock-item {
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--card-border);
      border-radius: 10px;
      padding: 1rem;
      margin-bottom: 0.75rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .lock-details {
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }

    .lock-module {
      font-family: 'Fira Code', monospace;
      font-size: 0.95rem;
      font-weight: 600;
      color: #cbd5e1;
    }

    .lock-branch {
      font-size: 0.8rem;
      color: var(--text-muted);
    }

    .lock-time {
      font-size: 0.8rem;
      color: var(--text-muted);
    }

    /* Git status */
    .git-file {
      font-family: 'Fira Code', monospace;
      font-size: 0.85rem;
      padding: 0.4rem 0.6rem;
      background: rgba(255,255,255,0.03);
      border-radius: 6px;
      margin-bottom: 0.4rem;
      border-left: 3px solid var(--accent-warning);
    }

    .git-file.staged {
      border-left-color: var(--accent-success);
    }

    /* Memory lessons & rules */
    .rule-item {
      padding: 0.75rem 1rem;
      background: rgba(255,255,255,0.02);
      border-radius: 8px;
      border-left: 3px solid var(--accent-primary);
      margin-bottom: 0.75rem;
      font-size: 0.9rem;
      line-height: 1.4;
    }

    /* Utility classes */
    .btn-action {
      background: var(--accent-primary);
      color: #ffffff;
      border: none;
      padding: 0.6rem 1.2rem;
      border-radius: 8px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      font-family: 'Outfit', sans-serif;
    }

    .btn-action:hover {
      box-shadow: 0 0 12px rgba(99, 102, 241, 0.5);
      transform: translateY(-1px);
    }

    .text-center {
      text-align: center;
    }

    .text-muted {
      color: var(--text-muted);
    }

    .flex-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .badge-info {
      background: rgba(99, 102, 241, 0.15);
      color: #818cf8;
      border: 1px solid rgba(99, 102, 241, 0.3);
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      font-size: 0.75rem;
      font-weight: 600;
    }
  </style>
</head>
<body>

  <header>
    <div class="header-content">
      <div class="logo-area">
        <h1>AAC V2 Dashboard</h1>
        <p>Operational Workspace Control & Compliance</p>
      </div>
      <div>
        <span class="badge" id="version-badge">v2.106.0</span>
      </div>
    </div>
  </header>

  <div class="dashboard-container">
    <div class="tabs-bar">
      <button class="tab-btn active" onclick="switchTab('overview')">Overview & Active Issue</button>
      <button class="tab-btn" onclick="switchTab('locks')">Module Locks</button>
      <button class="tab-btn" onclick="switchTab('memory')">Self-Learning Memory</button>
      <button class="tab-btn" onclick="switchTab('changelog')">SemVer & Releases</button>
    </div>

    <!-- TAB 1: OVERVIEW -->
    <div id="overview-tab" class="tab-content active">
      <div class="overview-grid">
        <!-- Active Issue Card -->
        <div>
          <div class="card">
            <div class="card-header">
              <h2>🎫 Active Issue</h2>
              <span class="badge-info" id="active-issue-branch">Loading...</span>
            </div>
            <div id="active-issue-content">
              <h3 id="active-issue-title" style="margin-top: 0;">Loading...</h3>
              <p class="text-muted" style="font-size: 0.9rem;">Status: <span id="active-issue-status" class="status-badge pass">open</span></p>
              
              <h4 style="margin-bottom: 0.5rem;">Issue Checklist:</h4>
              <div id="active-issue-checklist">
                <!-- dynamically loaded -->
              </div>
            </div>
          </div>

          <div class="card">
            <div class="card-header">
              <h2>📂 Git status changes</h2>
            </div>
            <div id="git-status-content">
              <!-- dynamically loaded -->
            </div>
          </div>
        </div>

        <!-- Compliance Checklist Card -->
        <div>
          <div class="card">
            <div class="card-header">
              <h2>✅ Compliance Audits</h2>
              <span class="header-meta" id="compliance-timestamp">Just now</span>
            </div>
            <div id="compliance-list">
              <!-- dynamically loaded -->
            </div>
            <div style="margin-top: 1.25rem;" class="text-center">
              <button class="btn-action" onclick="loadData()">Refresh Audit Status</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 2: LOCKS -->
    <div id="locks-tab" class="tab-content">
      <div class="card">
        <div class="card-header">
          <h2>🔒 Active Module Locks</h2>
        </div>
        <p class="text-muted" style="margin-top: 0; margin-bottom: 1.5rem;">Locks prevent parallel AI agents from making conflicting edits to files.</p>
        <div id="locks-list">
          <!-- dynamically loaded -->
        </div>
      </div>
    </div>

    <!-- TAB 3: SELF-LEARNING -->
    <div id="memory-tab" class="tab-content">
      <div class="card">
        <div class="card-header">
          <h2>🧠 Synthesized Rules (Self-Learning Memory)</h2>
        </div>
        <p class="text-muted" style="margin-top: 0; margin-bottom: 1.5rem;">These rules are automatically generated when bugs are fixed locally to prevent agent regression.</p>
        <div id="rules-list">
          <!-- dynamically loaded -->
        </div>
      </div>
      <div class="card">
        <div class="card-header">
          <h2>📝 Lessons Learned Feed</h2>
        </div>
        <div id="lessons-list">
          <!-- dynamically loaded -->
        </div>
      </div>
    </div>

    <!-- TAB 4: SEMVER & RELEASES -->
    <div id="changelog-tab" class="tab-content">
      <div class="card">
        <div class="card-header">
          <h2>📝 SemVer Release History</h2>
        </div>
        <p class="text-muted" style="margin-top: 0; margin-bottom: 1.5rem;">Recent SemVer bumps and automated release tags.</p>
        <div id="changelog-list">
          <!-- dynamically loaded -->
        </div>
      </div>
    </div>
  </div>

  <script>
    function switchTab(tabId) {
      document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

      event.target.classList.add('active');
      document.getElementById(tabId + '-tab').classList.add('active');
    }

    async function loadData() {
      try {
        const res = await fetch('/api/status');
        const data = await res.json();
        
        // Update version badge
        document.getElementById('version-badge').textContent = 'v' + data.version;

        // Render Compliance Checks
        const complianceList = document.getElementById('compliance-list');
        complianceList.innerHTML = '';
        for (const [name, passed] of Object.entries(data.compliance)) {
          const item = document.createElement('div');
          item.className = 'compliance-item';
          item.innerHTML = `
            <span class="name">${name}</span>
            <span class="status-badge ${passed ? 'pass' : 'fail'}">${passed ? 'PASS' : 'FAIL'}</span>
          `;
          complianceList.appendChild(item);
        }
        document.getElementById('compliance-timestamp').textContent = 'Updated: ' + data.timestamp;

        // Render Active Issue
        const issue = data.active_issue;
        document.getElementById('active-issue-title').textContent = issue.id !== 'None' ? issue.id + ': ' + issue.title : issue.title;
        document.getElementById('active-issue-branch').textContent = issue.branch;
        
        const statusBadge = document.getElementById('active-issue-status');
        statusBadge.textContent = issue.status;
        statusBadge.className = 'status-badge ' + (issue.status === 'open' ? 'pass' : 'fail');

        const checklist = document.getElementById('active-issue-checklist');
        checklist.innerHTML = '';
        if (issue.tasks && issue.tasks.length > 0) {
          issue.tasks.forEach(task => {
            const checked = task.toLowerCase().includes('[x]');
            const cleanLabel = task.replace(/^-\s+\[\s*[xX\s]\s*\]\s*/, '');
            const item = document.createElement('div');
            item.className = 'task-item';
            item.innerHTML = `
              <input type="checkbox" class="task-checkbox" ${checked ? 'checked' : ''} disabled>
              <span class="task-label ${checked ? 'checked' : ''}">${cleanLabel}</span>
            `;
            checklist.appendChild(item);
          });
        } else {
          checklist.innerHTML = '<p class="text-muted">No checklist tasks defined in the active issue file.</p>';
        }

        // Render Git Status
        const gitContent = document.getElementById('git-status-content');
        gitContent.innerHTML = '';
        if (data.git_status && data.git_status.length > 0) {
          data.git_status.forEach(file => {
            const isStaged = file.startsWith('M') || file.startsWith('A') || file.startsWith('D');
            const item = document.createElement('div');
            item.className = 'git-file ' + (isStaged ? 'staged' : '');
            item.textContent = file;
            gitContent.appendChild(item);
          });
        } else {
          gitContent.innerHTML = '<p class="text-muted">Workspace is clean. No uncommitted modifications.</p>';
        }

        // Render Module Locks
        const locksList = document.getElementById('locks-list');
        locksList.innerHTML = '';
        if (data.locks && data.locks.length > 0) {
          data.locks.forEach(lock => {
            const item = document.createElement('div');
            item.className = 'lock-item';
            item.innerHTML = `
              <div class="lock-details">
                <span class="lock-module">${lock.module}</span>
                <span class="lock-branch">Branch: <b>${lock.branch}</b></span>
              </div>
              <div class="text-muted lock-time">Locked: ${lock.timestamp}</div>
            `;
            locksList.appendChild(item);
          });
        } else {
          locksList.innerHTML = '<p class="text-muted">No active module locks found. Run <code>./helper.sh lock &lt;module&gt;</code> to lock.</p>';
        }

        // Render Synthesized Rules
        const rulesList = document.getElementById('rules-list');
        rulesList.innerHTML = '';
        if (data.rules && data.rules.length > 0) {
          data.rules.forEach(rule => {
            const item = document.createElement('div');
            item.className = 'rule-item';
            item.textContent = rule;
            rulesList.appendChild(item);
          });
        } else {
          rulesList.innerHTML = '<p class="text-muted">No synthesized rules recorded yet.</p>';
        }

        // Render Lessons Learned
        const lessonsList = document.getElementById('lessons-list');
        lessonsList.innerHTML = '';
        if (data.lessons && data.lessons.length > 0) {
          data.lessons.forEach(lesson => {
            const item = document.createElement('div');
            item.className = 'rule-item';
            item.style.borderLeftColor = 'var(--accent-warning)';
            item.textContent = lesson;
            lessonsList.appendChild(item);
          });
        } else {
          lessonsList.innerHTML = '<p class="text-muted">No lessons learned recorded yet.</p>';
        }

        // Render Changelog
        const changelogList = document.getElementById('changelog-list');
        changelogList.innerHTML = '';
        if (data.changelog && data.changelog.length > 0) {
          data.changelog.forEach(release => {
            const item = document.createElement('div');
            item.className = 'lock-item';
            item.innerHTML = `
              <span class="lock-module">Release v${release.version}</span>
              <span class="lock-time">${release.date}</span>
            `;
            changelogList.appendChild(item);
          });
        } else {
          changelogList.innerHTML = '<p class="text-muted">No changelog entries found.</p>';
        }

      } catch (err) {
        console.error('Failed to load status:', err);
      }
    }

    // Initial load
    loadData();
  </script>
</body>
</html>
"""

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            try:
                data = get_dashboard_data()
                self.wfile.write(json.dumps(data).encode('utf-8'))
            except Exception as e:
                err_response = {"error": str(e)}
                self.wfile.write(json.dumps(err_response).encode('utf-8'))
        elif self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    # Override log_message to prevent terminal cluttering
    def log_message(self, format, *args):
        pass

def run(args):
    port = 8000
    server = None
    # Auto port binding to avoid port conflicts
    while port < 8020:
        try:
            server = HTTPServer(('127.0.0.1', port), DashboardHandler)
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
