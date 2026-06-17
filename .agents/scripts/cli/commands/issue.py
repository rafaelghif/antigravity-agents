import os
import sys
import re
from datetime import datetime
import utils
import urllib.request
import urllib.error
import json

# ANSI color codes
C_GREEN = '\033[92m'
C_YELLOW = '\033[93m'
C_RED = '\033[91m'
C_GRAY = '\033[90m'
C_BOLD = '\033[1m'
C_CYAN = '\033[96m'
C_END = '\033[0m'

def get_active_profile_token(provider):
    # 1. Get current git user email
    import subprocess
    try:
        git_email = subprocess.check_output(
            ["git", "config", "user.email"], 
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except:
        return None, None
        
    if not git_email:
        return None, None
        
    # 2. Find profiles file
    profiles_file = ""
    agents_profiles = os.path.join(utils.get_agents_dir(), 'git_profiles')
    home_profiles = os.path.expanduser('~/.git_profiles')
    
    if os.path.exists(agents_profiles):
        profiles_file = agents_profiles
    elif os.path.exists(home_profiles):
        profiles_file = home_profiles
        
    if not profiles_file:
        return None, None
        
    # 3. Parse profiles
    config = {}
    try:
        with open(profiles_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip() and not line.strip().startswith('#') and '=' in line:
                    parts = line.strip().split('=', 1)
                    config[parts[0].strip()] = parts[1].strip()
    except:
        return None, None
        
    # 4. Find profile prefix that matches git_email
    profile_prefix = None
    for k, v in config.items():
        if k.endswith('.email') and v == git_email:
            profile_prefix = k.rsplit('.email', 1)[0]
            break
            
    if not profile_prefix:
        return None, None
        
    # 5. Get token & custom URL based on provider
    token_key = f"{profile_prefix}.{provider}_token"
    url_key = f"{profile_prefix}.{provider}_url"
    return config.get(token_key), config.get(url_key)

def get_provider_and_repo():
    import subprocess
    try:
        remote_url = subprocess.check_output(
            ["git", "remote", "get-url", "origin"], 
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except:
        return None
        
    if not remote_url:
        return None
        
    # GitHub: github.com[:/]([^/]+)/([^/.]+)(?:\.git)?$
    if "github.com" in remote_url:
        m = re.search(r'github\.com[:/]([^/]+)/([^/.]+)(?:\.git)?$', remote_url)
        if m:
            return "github", "https://api.github.com", m.group(1), m.group(2)
            
    # GitLab: gitlab.com[:/]([^/]+)/([^/.]+)(?:\.git)?$ (or custom domain with gitlab in it)
    elif "gitlab" in remote_url:
        domain = "gitlab.com"
        m_domain = re.search(r'(?:https?://|git@)([^:/]+)', remote_url)
        if m_domain:
            domain = m_domain.group(1)
            
        url_prefix = f"https://{domain}"
        if remote_url.startswith("http"):
            m_prefix = re.match(r'(https?://[^/]+)', remote_url)
            if m_prefix:
                url_prefix = m_prefix.group(1)
                
        m = re.search(r'[^:/]+[:/]([^/]+)/([^/.]+)(?:\.git)?$', remote_url)
        if m:
            return "gitlab", url_prefix, m.group(1), m.group(2)
            
    # Default to Gitea/local if it's Gitea or custom local/server git hosting
    else:
        domain = "localhost:3000"
        m_domain = re.search(r'(?:https?://|git@)([^:/]+)(?::\d+)?', remote_url)
        if m_domain:
            domain = m_domain.group(1)
            m_port = re.search(r'(?:https?://|git@)[^:/]+:(\d+)', remote_url)
            if m_port:
                domain = f"{domain}:{m_port.group(1)}"
        
        protocol = "http"
        if remote_url.startswith("https"):
            protocol = "https"
            
        url_prefix = f"{protocol}://{domain}"
        if remote_url.startswith("http"):
            m_prefix = re.match(r'(https?://[^/]+)', remote_url)
            if m_prefix:
                url_prefix = m_prefix.group(1)
                
        m = re.search(r'[^:/]+[:/]([^/]+)/([^/.]+)(?:\.git)?$', remote_url)
        if m:
            return "gitea", url_prefix, m.group(1), m.group(2)
            
    return None

def sync_remote_issue(action, title=None, body=None, remote_issue_number=None):
    # 1. Resolve Git remote repository info
    repo_info = get_provider_and_repo()
    if not repo_info:
        return None
        
    provider, default_url, owner, repo = repo_info

    # 2. Find git_profiles config file
    profiles_file = ""
    agents_profiles = os.path.join(utils.get_agents_dir(), 'git_profiles')
    home_profiles = os.path.expanduser('~/.git_profiles')
    
    if os.path.exists(agents_profiles):
        profiles_file = agents_profiles
    elif os.path.exists(home_profiles):
        profiles_file = home_profiles
        
    config = {}
    if os.path.exists(profiles_file):
        try:
            with open(profiles_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip() and not line.strip().startswith('#') and '=' in line:
                        parts = line.strip().split('=', 1)
                        config[parts[0].strip()] = parts[1].strip()
        except:
            pass
            
    keys = sorted(list(set(k.split('.')[0] for k in config.keys() if k.endswith('.name'))))
    max_tries = len(keys) if keys else 1
    
    for attempt in range(max_tries):
        token, url_override = get_active_profile_token(provider)
        
        res_data = None
        if token:
            base_url = url_override if url_override else default_url
            headers = {
                "User-Agent": "Antigravity-Agent-Helper"
            }
            
            import urllib.parse
            import urllib.request
            import urllib.error
            
            if provider == "github":
                headers["Authorization"] = f"Bearer {token}"
                headers["Accept"] = "application/vnd.github+json"
                headers["X-GitHub-Api-Version"] = "2022-11-28"
                
                if action == "create":
                    url = f"{base_url}/repos/{owner}/{repo}/issues"
                    data = {"title": title, "body": body or ""}
                    method = "POST"
                elif action == "close":
                    if not remote_issue_number:
                        return None
                    url = f"{base_url}/repos/{owner}/{repo}/issues/{remote_issue_number}"
                    data = {"state": "closed"}
                    method = "PATCH"
                else:
                    return None
                    
            elif provider == "gitlab":
                headers["PRIVATE-TOKEN"] = token
                headers["Content-Type"] = "application/json"
                
                project_path = urllib.parse.quote(f"{owner}/{repo}", safe="")
                
                if action == "create":
                    url = f"{base_url}/api/v4/projects/{project_path}/issues"
                    data = {"title": title, "description": body or ""}
                    method = "POST"
                elif action == "close":
                    if not remote_issue_number:
                        return None
                    url = f"{base_url}/api/v4/projects/{project_path}/issues/{remote_issue_number}"
                    data = {"state_event": "close"}
                    method = "PUT"
                else:
                    return None
                    
            elif provider == "gitea":
                headers["Authorization"] = f"token {token}"
                headers["Content-Type"] = "application/json"
                
                if action == "create":
                    url = f"{base_url}/api/v1/repos/{owner}/{repo}/issues"
                    data = {"title": title, "body": body or ""}
                    method = "POST"
                elif action == "close":
                    if not remote_issue_number:
                        return None
                    url = f"{base_url}/api/v1/repos/{owner}/{repo}/issues/{remote_issue_number}"
                    data = {"state": "closed"}
                    method = "PATCH"
                else:
                    return None
            else:
                return None
                
            req_data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
            
            try:
                with urllib.request.urlopen(req) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                    if "number" in res_data:
                        res_data["remote_id"] = res_data["number"]
                    elif "iid" in res_data:
                        res_data["remote_id"] = res_data["iid"]
                    return res_data
            except urllib.error.HTTPError as e:
                print(color(f"\n{provider.upper()} API Error ({e.code}): {e.reason}", C_YELLOW), file=sys.stderr)
                try:
                    err_body = e.read().decode('utf-8')
                    print(color(f"Details: {err_body}", C_GRAY), file=sys.stderr)
                except:
                    pass
            except Exception as e:
                print(color(f"\nWarning: Failed to connect to {provider.upper()} API: {e}", C_YELLOW), file=sys.stderr)
        else:
            print(color(f"\nWarning: Token for remote provider '{provider}' is not configured in the active profile.", C_YELLOW), file=sys.stderr)
            
        # Rotate to the next profile locally if sync failed
        if attempt < max_tries - 1:
            import subprocess
            try:
                git_email = subprocess.check_output(
                    ["git", "config", "user.email"], 
                    stderr=subprocess.DEVNULL
                ).decode().strip()
            except:
                git_email = ""
                
            selected_idx = 0
            for i, k in enumerate(keys):
                p_e = config.get(f"{k}.email", "")
                if p_e == git_email:
                    selected_idx = (i + 1) % len(keys)
                    break
                    
            next_profile = keys[selected_idx]
            p_n = config[f"{next_profile}.name"]
            p_e = config.get(f"{next_profile}.email", "")
            p_s = config.get(f"{next_profile}.ssh_key", "")
            
            print(color(f"\n[INFO] Rotating local Git configuration to profile '{next_profile}' and retrying sync...", C_YELLOW))
            try:
                subprocess.run(["git", "config", "--local", "user.name", p_n], check=True)
                subprocess.run(["git", "config", "--local", "user.email", p_e], check=True)
                if p_s:
                    resolved_ssh = os.path.expanduser(p_s)
                    if os.path.exists(resolved_ssh):
                        subprocess.run(["git", "config", "--local", "core.sshCommand", f"ssh -i \"{p_s}\" -o IdentitiesOnly=yes"], check=True)
                    else:
                        subprocess.run(["git", "config", "--local", "--unset", "core.sshCommand"], stderr=subprocess.DEVNULL)
                else:
                    subprocess.run(["git", "config", "--local", "--unset", "core.sshCommand"], stderr=subprocess.DEVNULL)
            except Exception as rotation_err:
                print(color(f"Warning: Failed to rotate Git profile locally: {rotation_err}", C_YELLOW), file=sys.stderr)
                break
                
    return None


def color(text, ansi_code):
    if sys.stdout.isatty():
        return f"{ansi_code}{text}{C_END}"
    return text

def get_issues_dir():
    issues_dir = os.path.join(utils.get_agents_dir(), "issues")
    if not os.path.exists(issues_dir):
        os.makedirs(issues_dir)
    return issues_dir

def parse_frontmatter(file_path):
    metadata = {}
    description = ""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        m = re.match(r'^---\n(.*?)\n---\n*(.*)', content, re.DOTALL)
        if m:
            yaml_block = m.group(1)
            description = m.group(2).strip()
            
            for line in yaml_block.splitlines():
                if ':' in line:
                    k, v = line.split(':', 1)
                    metadata[k.strip()] = v.strip().strip('"\'')
        else:
            description = content.strip()
    except Exception as e:
        print(f"Error parsing issue file {file_path}: {e}", file=sys.stderr)
        
    return metadata, description

def show_help():
    print("==========================================================")
    print("  Antigravity Local Issue Tracker CLI")
    print("==========================================================")
    print("Usage: helper.sh issue <command> [arguments...]")
    print("")
    print("Subcommands:")
    print("  list                       List all issues (open and closed)")
    print("  create \"<title>\" [\"<desc>\"] Create a new local issue")
    print("  view <id>                  View details of a specific issue")
    print("  close <id>                 Close an open issue")
    print("  checkout <id>              Create/checkout branch for an issue and update memory.md")
    print("  merge <id>                 Validate workspace, commit issue branch, and merge it")
    print("==========================================================")

def list_issues():
    issues_dir = get_issues_dir()
    files = sorted([f for f in os.listdir(issues_dir) if re.match(r'^issue_[0-9]+\.md$', f)])
    
    if not files:
        print(color("\nNo issues found in workspace.", C_GRAY))
        return
        
    print(color("\n--- Workspace Local Issues ---", C_BOLD + C_CYAN))
    print(f"{'ID':<6} | {'Status':<8} | {'Title':<35} | {'Assignee':<10}")
    print("-" * 65)
    
    for f in files:
        file_path = os.path.join(issues_dir, f)
        meta, _ = parse_frontmatter(file_path)
        
        issue_id = meta.get("id", f.split('_')[1].split('.')[0])
        title = meta.get("title", "No Title")
        status = meta.get("status", "open").lower()
        assignee = meta.get("assignee", "None")
        
        if len(title) > 33:
            title = title[:30] + "..."
            
        status_str = f"[{status.upper()}]"
        if status == "open":
            status_colored = color(status_str, C_GREEN + C_BOLD)
        else:
            status_colored = color(status_str, C_GRAY)
            
        print(f"#{int(issue_id):<5} | {status_colored:<17} | {title:<35} | {assignee:<10}")
    print("")

def create_issue(title, description="No description provided."):
    if not title:
        print(color("Error: Issue title is required.", C_RED), file=sys.stderr)
        sys.exit(1)
        
    issues_dir = get_issues_dir()
    files = [f for f in os.listdir(issues_dir) if re.match(r'^issue_[0-9]+\.md$', f)]
    
    next_id = 1
    if files:
        ids = []
        for f in files:
            m = re.search(r'issue_([0-9]+)\.md', f)
            if m:
                ids.append(int(m.group(1)))
        if ids:
            next_id = max(ids) + 1
            
    # Try to sync to Remote Issues
    remote_id = None
    provider = None
    repo_info = get_provider_and_repo()
    if repo_info:
        provider = repo_info[0]
        token, _ = get_active_profile_token(provider)
        if token:
            res = sync_remote_issue("create", title=title, body=description)
            if res and "remote_id" in res:
                remote_id = res["remote_id"]
                print(color(f"  [SUCCESS] Synchronized to {provider.upper()}: Issue #{remote_id} created.", C_GREEN))
            else:
                print(color(f"  [WARNING] {provider.upper()} integration configured but synchronization failed.", C_YELLOW))

    filename = f"issue_{next_id:03d}.md"
    file_path = os.path.join(issues_dir, filename)
    created_at = datetime.now().strftime("%Y-%m-%d")
    
    content = f"""---
id: {next_id}
github_id: {remote_id if (remote_id and provider == 'github') else 'null'}
gitlab_id: {remote_id if (remote_id and provider == 'gitlab') else 'null'}
gitea_id: {remote_id if (remote_id and provider == 'gitea') else 'null'}
remote_id: {remote_id if remote_id else 'null'}
remote_provider: {provider if remote_id else 'null'}
title: "{title}"
status: open
assignee: Agent
created_at: {created_at}
closed_at: null
---

# Description
{description}
"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(color(f"\n[SUCCESS] Created Issue #{next_id}: \"{title}\"", C_GREEN + C_BOLD))
        print(f"Saved to: .agents/issues/{filename}\n")
    except Exception as e:
        print(color(f"Error: Failed to save issue file: {e}", C_RED), file=sys.stderr)
        sys.exit(1)

def close_issue(issue_id_str):
    try:
        issue_id = int(issue_id_str)
    except ValueError:
        print(color(f"Error: Invalid issue ID '{issue_id_str}'", C_RED), file=sys.stderr)
        sys.exit(1)
        
    issues_dir = get_issues_dir()
    filename = f"issue_{issue_id:03d}.md"
    file_path = os.path.join(issues_dir, filename)
    
    if not os.path.exists(file_path):
        print(color(f"Error: Issue #{issue_id} not found.", C_RED), file=sys.stderr)
        sys.exit(1)
        
    meta, desc = parse_frontmatter(file_path)
    if meta.get("status") == "closed":
        print(color(f"Issue #{issue_id} is already closed.", C_YELLOW))
        return
        
    closed_at = datetime.now().strftime("%Y-%m-%d")
    
    # Try to close on remote if remote_id or provider-specific id is set
    github_id_val = meta.get("github_id", "null")
    gitlab_id_val = meta.get("gitlab_id", "null")
    gitea_id_val = meta.get("gitea_id", "null")
    remote_id_val = meta.get("remote_id", "null")
    remote_provider_val = meta.get("remote_provider", "null")
    
    resolved_id = None
    resolved_provider = None
    
    if remote_id_val and remote_id_val != "null" and remote_id_val != "None":
        resolved_id = remote_id_val
        resolved_provider = remote_provider_val
    elif github_id_val and github_id_val != "null" and github_id_val != "None":
        resolved_id = github_id_val
        resolved_provider = "github"
    elif gitlab_id_val and gitlab_id_val != "null" and gitlab_id_val != "None":
        resolved_id = gitlab_id_val
        resolved_provider = "gitlab"
    elif gitea_id_val and gitea_id_val != "null" and gitea_id_val != "None":
        resolved_id = gitea_id_val
        resolved_provider = "gitea"
        
    if resolved_id and resolved_provider:
        try:
            gh_num = int(resolved_id)
            repo_info = get_provider_and_repo()
            if repo_info and repo_info[0] == resolved_provider:
                gh_res = sync_remote_issue("close", remote_issue_number=gh_num)
                if gh_res:
                    print(color(f"  [SUCCESS] Synchronized to {resolved_provider.upper()}: Closed Issue #{gh_num}.", C_GREEN))
            else:
                print(color(f"  [INFO] Bypassing remote sync: Current provider does not match issue's remote provider '{resolved_provider}'.", C_YELLOW))
        except Exception as e:
            print(color(f"  [WARNING] Failed to close issue on {resolved_provider.upper()}: {e}", C_YELLOW))
            
    content = f"""---
id: {issue_id}
github_id: {github_id_val if github_id_val else 'null'}
gitlab_id: {gitlab_id_val if gitlab_id_val else 'null'}
gitea_id: {gitea_id_val if gitea_id_val else 'null'}
remote_id: {remote_id_val if remote_id_val else 'null'}
remote_provider: {remote_provider_val if remote_provider_val else 'null'}
title: "{meta.get('title', 'No Title')}"
status: closed
assignee: {meta.get('assignee', 'Agent')}
created_at: {meta.get('created_at', closed_at)}
closed_at: {closed_at}
---

# Description
{desc}
"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(color(f"\n[SUCCESS] Closed Issue #{issue_id}: \"{meta.get('title')}\"", C_GREEN + C_BOLD))
    except Exception as e:
        print(color(f"Error: Failed to close issue: {e}", C_RED), file=sys.stderr)
        sys.exit(1)

def view_issue(issue_id_str):
    try:
        issue_id = int(issue_id_str)
    except ValueError:
        print(color(f"Error: Invalid issue ID '{issue_id_str}'", C_RED), file=sys.stderr)
        sys.exit(1)
        
    issues_dir = get_issues_dir()
    filename = f"issue_{issue_id:03d}.md"
    file_path = os.path.join(issues_dir, filename)
    
    if not os.path.exists(file_path):
        print(color(f"Error: Issue #{issue_id} not found.", C_RED), file=sys.stderr)
        sys.exit(1)
        
    meta, desc = parse_frontmatter(file_path)
    
    status = meta.get("status", "open").lower()
    if status == "open":
        status_colored = color("OPEN", C_GREEN + C_BOLD)
    else:
        status_colored = color("CLOSED", C_GRAY)
        
    print("\n" + color("="*58, C_CYAN))
    print(f"{color('ISSUE #' + str(issue_id), C_BOLD + C_CYAN)}: {color(meta.get('title', 'No Title'), C_BOLD)}")
    print(color("="*58, C_CYAN))
    print(f"  Status:     {status_colored}")
    print(f"  Assignee:   {meta.get('assignee', 'None')}")
    print(f"  Created At: {meta.get('created_at', 'N/A')}")
    if status == "closed":
        print(f"  Closed At:  {meta.get('closed_at', 'N/A')}")
    print(color("-"*58, C_CYAN))
    print(f"\n{desc}\n")
    print(color("="*58, C_CYAN) + "\n")

def checkout_issue(issue_id_str):
    import subprocess
    try:
        issue_id = int(issue_id_str)
    except ValueError:
        print(color(f"Error: Invalid issue ID '{issue_id_str}'", C_RED), file=sys.stderr)
        sys.exit(1)
        
    issues_dir = get_issues_dir()
    filename = f"issue_{issue_id:03d}.md"
    file_path = os.path.join(issues_dir, filename)
    
    if not os.path.exists(file_path):
        print(color(f"Error: Issue #{issue_id} not found.", C_RED), file=sys.stderr)
        sys.exit(1)
        
    meta, desc = parse_frontmatter(file_path)
    title = meta.get("title", "issue")
    # Slugify title
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    if not slug:
        slug = "task"
    branch_name = f"issue-{issue_id}-{slug}"
    
    # Update issue assignee
    git_user = "Agent"
    try:
        git_user = subprocess.check_output(["git", "config", "user.name"], stderr=subprocess.DEVNULL).decode().strip()
    except:
        pass
    
    meta["assignee"] = git_user
    
    closed_at_str = meta.get("closed_at", "null")
    github_id_val = meta.get("github_id", "null")
    gitlab_id_val = meta.get("gitlab_id", "null")
    gitea_id_val = meta.get("gitea_id", "null")
    remote_id_val = meta.get("remote_id", "null")
    remote_provider_val = meta.get("remote_provider", "null")
    content = f"""---
id: {issue_id}
github_id: {github_id_val if github_id_val else 'null'}
gitlab_id: {gitlab_id_val if gitlab_id_val else 'null'}
gitea_id: {gitea_id_val if gitea_id_val else 'null'}
remote_id: {remote_id_val if remote_id_val else 'null'}
remote_provider: {remote_provider_val if remote_provider_val else 'null'}
title: "{meta.get('title')}"
status: {meta.get('status', 'open')}
assignee: {meta.get('assignee')}
created_at: {meta.get('created_at')}
closed_at: {closed_at_str if closed_at_str else 'null'}
---

# Description
{desc}
"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(color(f"Preparing Git branch '{branch_name}'...", C_CYAN))
    
    # Check if branch exists
    try:
        branches = subprocess.check_output(["git", "branch"]).decode()
    except Exception as e:
        branches = ""
        
    if re.search(fr'\b{re.escape(branch_name)}\b', branches):
        subprocess.run(["git", "checkout", branch_name])
    else:
        subprocess.run(["git", "checkout", "-b", branch_name])
        
    # Update memory.md
    memory_file = utils.get_memory_file()
    if os.path.exists(memory_file):
        try:
            with open(memory_file, 'r', encoding='utf-8') as f:
                mem_content = f.read()
                
            mem_content = re.sub(r'^- \*\*Current Task Target\*\*:.*', f'- **Current Task Target**: Resolve issue #{issue_id}: {title}', mem_content, flags=re.M)
            mem_content = re.sub(r'^- \*\*State Flag\*\*:.*', '- **State Flag**: `IN_PROGRESS`', mem_content, flags=re.M)
            
            checklist_line = f"- [/] Resolve issue #{issue_id}: {title}"
            if f"Resolve issue #{issue_id}:" not in mem_content:
                m = re.search(r'### Sprint Tasks Checklist\n', mem_content)
                if m:
                    idx = m.end()
                    mem_content = mem_content[:idx] + checklist_line + "\n" + mem_content[idx:]
                    
            with open(memory_file, 'w', encoding='utf-8') as f:
                f.write(mem_content)
            print(color(f"[SUCCESS] Updated memory.md with issue #{issue_id} task checklist.", C_GREEN))
        except Exception as e:
            print(color(f"Warning: Failed to update memory.md: {e}", C_YELLOW))
            
    print(color(f"[SUCCESS] Checked out branch '{branch_name}' and initialized task.", C_GREEN + C_BOLD))

def get_conflicted_files():
    import subprocess
    try:
        out = subprocess.check_output(["git", "diff", "--name-only", "--diff-filter=U"]).decode().strip()
        if out:
            return out.splitlines()
    except:
        pass
    return []

def merge_changelog_sections(sec1, sec2):
    import re
    lines1 = sec1.splitlines()
    if not lines1:
        return sec2
    version_line = lines1[0]
    
    def parse_subsections(content):
        parts = content.split('### ')
        subsections = {}
        for part in parts[1:]:
            m = re.match(r'^([A-Za-z]+)\n(.*)', part, re.DOTALL)
            if m:
                sub_type = m.group(1)
                items = [line.strip() for line in m.group(2).splitlines() if line.strip().startswith('-')]
                subsections[sub_type] = items
        return subsections
        
    sub1 = parse_subsections(sec1)
    sub2 = parse_subsections(sec2)
    
    merged_sub = {}
    all_types = list(set(sub1.keys()) | set(sub2.keys()))
    
    type_order = ["Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"]
    all_types.sort(key=lambda t: type_order.index(t) if t in type_order else 99)
    
    result = version_line + "\n"
    for t in all_types:
        items1 = sub1.get(t, [])
        items2 = sub2.get(t, [])
        merged_items = []
        for item in items1 + items2:
            if item not in merged_items:
                merged_items.append(item)
        
        if merged_items:
            result += f"### {t}\n"
            for item in merged_items:
                result += f"{item}\n"
            result += "\n"
            
    return result.strip()

def try_smart_merge_changelog(filepath):
    import subprocess
    import re
    try:
        ours = subprocess.check_output(["git", "show", f":2:{filepath}"]).decode('utf-8')
        theirs = subprocess.check_output(["git", "show", f":3:{filepath}"]).decode('utf-8')
    except:
        return False
        
    def parse_sections(content):
        parts = content.split('## [')
        header = parts[0]
        sections = {}
        for part in parts[1:]:
            m = re.match(r'^([^\]]+)\](.*)', part, re.DOTALL)
            if m:
                version = m.group(1)
                sections[version] = '## [' + part
        return header, sections

    try:
        h_ours, sec_ours = parse_sections(ours)
        h_theirs, sec_theirs = parse_sections(theirs)
        
        merged_content = h_ours
        all_versions = list(set(sec_ours.keys()) | set(sec_theirs.keys()))
        
        def semver_key(v):
            try:
                return [int(x) for x in re.findall(r'\d+', v)]
            except:
                return [0]
                
        all_versions.sort(key=semver_key, reverse=True)
        
        for v in all_versions:
            if v in sec_ours and v not in sec_theirs:
                merged_content += sec_ours[v] + "\n"
            elif v in sec_theirs and v not in sec_ours:
                merged_content += sec_theirs[v] + "\n"
            else:
                if sec_ours[v].strip() == sec_theirs[v].strip():
                    merged_content += sec_ours[v] + "\n"
                else:
                    merged_content += merge_changelog_sections(sec_ours[v], sec_theirs[v]) + "\n"
                    
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(merged_content.strip() + "\n")
        return True
    except Exception as e:
        print(f"Smart changelog merge failed: {e}", file=sys.stderr)
        return False

def try_smart_merge_memory(filepath):
    import subprocess
    import re
    try:
        ours = subprocess.check_output(["git", "show", f":2:{filepath}"]).decode('utf-8')
        theirs = subprocess.check_output(["git", "show", f":3:{filepath}"]).decode('utf-8')
    except:
        return False
        
    try:
        def get_checklist_items(content):
            return [line.strip() for line in content.splitlines() if re.match(r'^-\s+\[[ x/]\]', line.strip())]
            
        items_ours = get_checklist_items(ours)
        items_theirs = get_checklist_items(theirs)
        
        def parse_task(line):
            m = re.match(r'^-\s+\[([ x/])\]\s*(.*)', line)
            if m:
                return m.group(1), m.group(2).strip()
            return None, None
            
        merged_tasks = {}
        ordered_keys = []
        
        for line in items_theirs + items_ours:
            status, desc = parse_task(line)
            if desc:
                if desc not in merged_tasks:
                    merged_tasks[desc] = status
                    ordered_keys.append(desc)
                else:
                    curr_status = merged_tasks[desc]
                    if status == 'x' or (status == '/' and curr_status == ' '):
                        merged_tasks[desc] = status
                        
        new_checklist = ""
        for desc in ordered_keys:
            status = merged_tasks[desc]
            new_checklist += f"- [{status}] {desc}\n"
            
        parts = theirs.split('### Sprint Tasks Checklist\n')
        if len(parts) < 2:
            parts = theirs.split('### Sprint Tasks Checklist\r\n')
            
        if len(parts) >= 2:
            header = parts[0] + "### Sprint Tasks Checklist\n"
            rem = parts[1]
            idx_dash = rem.find('\n---')
            if idx_dash == -1:
                idx_dash = rem.find('\r\n---')
            if idx_dash != -1:
                footer = rem[idx_dash:]
            else:
                footer = "\n---\n"
                
            merged_memory = header + new_checklist + footer
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(merged_memory)
            return True
    except:
        pass
        
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(theirs)
        return True
    except:
        return False

def smart_automerge_file(filepath):
    filename = os.path.basename(filepath)
    if filename == "memory.md":
        return try_smart_merge_memory(filepath)
    elif filename == "CHANGELOG.md":
        return try_smart_merge_changelog(filepath)
    return False

def resolve_merge_conflicts():
    import subprocess
    conflicted_files = get_conflicted_files()
    if not conflicted_files:
        print(color("No conflicted files found.", C_GREEN))
        return
        
    print(color(f"\nFound {len(conflicted_files)} conflicted file(s):", C_BOLD + C_CYAN))
    for f in conflicted_files:
        print(f"  - {f}")
    print("")
    
    for filepath in conflicted_files:
        filename = os.path.basename(filepath)
        print(color("="*58, C_CYAN))
        print(color(f"Resolving conflict in: {filepath}", C_BOLD + C_CYAN))
        print(color("="*58, C_CYAN))
        
        if filename in ("memory.md", "CHANGELOG.md"):
            print(color(f"Attempting smart auto-merge for {filename}...", C_GRAY))
            if smart_automerge_file(filepath):
                print(color(f"[SUCCESS] Smart auto-merge succeeded for {filename}!", C_GREEN))
                subprocess.run(["git", "add", filepath], check=True)
                continue
            else:
                print(color(f"[WARNING] Smart auto-merge failed for {filename}. Falling back to manual selection.", C_YELLOW))
                
        while True:
            print(f"  [{color('1', C_GREEN)}] Use OURS (Keep changes from base branch/main)")
            print(f"  [{color('2', C_GREEN)}] Use THEIRS (Keep changes from feature branch)")
            print(f"  [{color('3', C_GREEN)}] Open in Editor for manual resolution")
            print(f"  [{color('0', C_YELLOW)}] Abort Merge")
            
            try:
                choice = input(color("\nSelect resolution option [0-3]: ", C_BOLD)).strip()
            except (KeyboardInterrupt, EOFError):
                print(color("\nMerge aborted.", C_RED))
                subprocess.run(["git", "merge", "--abort"])
                sys.exit(1)
                
            if choice == "0":
                print(color("\nMerge aborted by user.", C_RED))
                subprocess.run(["git", "merge", "--abort"])
                sys.exit(1)
            elif choice == "1":
                print(color(f"Applying OURS version to {filepath}...", C_GRAY))
                subprocess.run(["git", "checkout", "--ours", filepath], check=True)
                subprocess.run(["git", "add", filepath], check=True)
                break
            elif choice == "2":
                print(color(f"Applying THEIRS version to {filepath}...", C_GRAY))
                subprocess.run(["git", "checkout", "--theirs", filepath], check=True)
                subprocess.run(["git", "add", filepath], check=True)
                break
            elif choice == "3":
                editor = None
                try:
                    editor = subprocess.check_output(["git", "config", "core.editor"]).decode().strip()
                except:
                    pass
                if not editor:
                    editor = os.environ.get("EDITOR")
                if not editor:
                    if sys.platform == "win32":
                        editor = "notepad.exe"
                    else:
                        editor = "nano"
                        
                print(color(f"Opening {filepath} in editor: {editor}...", C_GRAY))
                try:
                    subprocess.run(f'{editor} "{filepath}"', shell=True)
                    input(color("\nPress Enter AFTER you have finished resolving conflicts and saved the file: ", C_BOLD))
                    subprocess.run(["git", "add", filepath], check=True)
                    break
                except Exception as editor_err:
                    print(color(f"Error opening editor: {editor_err}", C_RED), file=sys.stderr)
            else:
                print(color("Invalid choice. Please enter 0, 1, 2, or 3.", C_RED))
                
    print(color("\n[SUCCESS] All conflicts resolved! Completing merge...", C_GREEN + C_BOLD))

def merge_issue(issue_id_str):
    import subprocess
    try:
        issue_id = int(issue_id_str)
    except ValueError:
        print(color(f"Error: Invalid issue ID '{issue_id_str}'", C_RED), file=sys.stderr)
        sys.exit(1)
        
    issues_dir = get_issues_dir()
    filename = f"issue_{issue_id:03d}.md"
    file_path = os.path.join(issues_dir, filename)
    
    if not os.path.exists(file_path):
        print(color(f"Error: Issue #{issue_id} not found.", C_RED), file=sys.stderr)
        sys.exit(1)
        
    meta, desc = parse_frontmatter(file_path)
    title = meta.get("title", "issue")
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    if not slug:
        slug = "task"
    branch_name = f"issue-{issue_id}-{slug}"
    
    # Check current branch
    current_branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip()
    if current_branch != branch_name:
        print(color(f"Error: You are currently on branch '{current_branch}', but merging issue #{issue_id} requires being on issue branch '{branch_name}'.", C_RED), file=sys.stderr)
        sys.exit(1)
        
    # 1. Run validation checks
    validate_sh = os.path.join(utils.get_agents_dir(), "scripts", "validate.sh")
    if os.path.exists(validate_sh):
        print(color("Running workspace validation checks...", C_CYAN))
        memory_file = utils.get_memory_file()
        orig_mem = ""
        if os.path.exists(memory_file):
            with open(memory_file, 'r', encoding='utf-8') as f:
                orig_mem = f.read()
            temp_mem = re.sub(r'^- \*\*State Flag\*\*:.*', '- **State Flag**: `COMPLETED`', orig_mem, flags=re.M)
            temp_mem = temp_mem.replace(f"[/] Resolve issue #{issue_id}:", f"[x] Resolve issue #{issue_id}:")
            with open(memory_file, 'w', encoding='utf-8') as f:
                f.write(temp_mem)
                
        try:
             proc = utils.run_shell_script(validate_sh)
             if proc.returncode != 0:
                 if orig_mem:
                     with open(memory_file, 'w', encoding='utf-8') as f:
                         f.write(orig_mem)
                 print(color("Error: Workspace validation failed. Merge aborted.", C_RED), file=sys.stderr)
                 sys.exit(proc.returncode)
        except Exception as e:
             if orig_mem:
                 with open(memory_file, 'w', encoding='utf-8') as f:
                     f.write(orig_mem)
             raise e
             
        # Compile bootstrap
        try:
             repo_dir = os.path.dirname(os.path.dirname(utils.get_agents_dir()))
             compile_script = os.path.join(repo_dir, "scratch", "compile_bootstrap.py")
             if os.path.exists(compile_script):
                 print(color("Re-compiling bootstrap.sh with completed task...", C_CYAN))
                 subprocess.run([sys.executable, compile_script])
        except Exception as e:
             print(color(f"Warning: Failed to compile bootstrap: {e}", C_YELLOW))
    else:
        print(color("Warning: validate.sh not found. Skipping workspace validation.", C_YELLOW))
         
    # 2. Close the issue locally
    close_issue(issue_id_str)
     
    # 3. Commit issue branch
    print(color(f"Committing changes on branch '{branch_name}'...", C_CYAN))
    commit_cmd = [
         sys.executable,
         os.path.join(utils.get_agents_dir(), "scripts", "cli", "helper.py"),
         "commit",
         "feat",
         "issue",
         f"resolve issue #{issue_id}: {title} closes #{issue_id}"
    ]
    subprocess.run(commit_cmd)
     
    # 4. Merge branch into base branch
    base_branch = "main"
    memory_file = utils.get_memory_file()
    if os.path.exists(memory_file):
         with open(memory_file, 'r', encoding='utf-8') as f:
             for line in f:
                 if "Active Pull Request Target" in line:
                     m = re.search(r'`([^`]+)`', line)
                     if m:
                         base_branch = m.group(1)
                         
    print(color(f"Switching to base branch '{base_branch}' and merging issue branch '{branch_name}'...", C_CYAN))
    subprocess.run(["git", "checkout", base_branch])
    
    env = os.environ.copy()
    env["AAC_COMMIT_RUNNING"] = "1"
    proc_merge = subprocess.run(
        ["git", "merge", branch_name, "--no-ff", "-m", f"merge({base_branch}): branch '{branch_name}' into '{base_branch}'"],
        env=env
    )
    if proc_merge.returncode != 0:
        print(color("\n[WARN] Merge conflict detected! Launching interactive resolution helper...", C_YELLOW))
        resolve_merge_conflicts()
        # Complete the merge commit
        subprocess.run(["git", "commit", "--no-edit"], env=env, check=True)
     
    # 5. Clean up local issue branch
    print(color(f"Deleting local issue branch '{branch_name}'...", C_CYAN))
    subprocess.run(["git", "branch", "-d", branch_name])
     
    # 6. Clean workspace
    clean_cmd = [
         sys.executable,
         os.path.join(utils.get_agents_dir(), "scripts", "cli", "helper.py"),
         "clean"
    ]
    subprocess.run(clean_cmd)
    
    # Restore memory.md reference
    subprocess.run(["git", "checkout", "--", memory_file])
    print(color(f"\n[SUCCESS] Issue #{issue_id} branch merged successfully into '{base_branch}' and cleaned up!\n", C_GREEN + C_BOLD))

def run(args):
    if len(args) < 2:
        show_help()
        sys.exit(0)
        
    subcmd = args[1].lower()
    
    if subcmd == "list":
        list_issues()
    elif subcmd == "create":
        if len(args) < 3:
            print(color("Error: Title is required. Usage: helper.sh issue create \"<title>\" [\"<desc>\"]", C_RED), file=sys.stderr)
            sys.exit(1)
        title = args[2]
        desc = args[3] if len(args) > 3 else "No description provided."
        create_issue(title, desc)
    elif subcmd == "close":
        if len(args) < 3:
            print(color("Error: Issue ID is required. Usage: helper.sh issue close <id>", C_RED), file=sys.stderr)
            sys.exit(1)
        close_issue(args[2])
    elif subcmd == "view":
        if len(args) < 3:
            print(color("Error: Issue ID is required. Usage: helper.sh issue view <id>", C_RED), file=sys.stderr)
            sys.exit(1)
        view_issue(args[2])
    elif subcmd == "checkout":
        if len(args) < 3:
            print(color("Error: Issue ID is required. Usage: helper.sh issue checkout <id>", C_RED), file=sys.stderr)
            sys.exit(1)
        checkout_issue(args[2])
    elif subcmd == "merge":
        if len(args) < 3:
            print(color("Error: Issue ID is required. Usage: helper.sh issue merge <id>", C_RED), file=sys.stderr)
            sys.exit(1)
        merge_issue(args[2])
    elif subcmd in ("-h", "--help", "help"):
        show_help()
    else:
        print(color(f"Error: Unknown issue subcommand '{subcmd}'", C_RED), file=sys.stderr)
        show_help()
        sys.exit(1)
