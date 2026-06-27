import os
import urllib.request
import json
import urllib.error

# Detect GITHUB_TOKEN or GIT_PAT from environment
def get_pat():
    return os.getenv("GITHUB_TOKEN") or os.getenv("GIT_PAT")

def get_repo_info():
    # Attempt to parse repository owner and name from git remote URL
    import subprocess
    try:
        res = subprocess.run(['git', 'remote', 'get-url', 'origin'], stdout=subprocess.PIPE, text=True)
        url = res.stdout.strip()
        # Parse git@github.com:owner/repo.git or https://github.com/owner/repo.git
        if "github.com" in url:
            part = url.split("github.com")[-1].strip(":/")
            if part.endswith(".git"):
                part = part[:-4]
            return part # e.g. "owner/repo"
    except Exception:
        pass
    return None

def create_github_issue(title, body=""):
    pat = get_pat()
    repo = get_repo_info()
    if not pat or not repo:
        return None
        
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        "Authorization": f"token {pat}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Antigravity-Agent-Core"
    }
    data = json.dumps({"title": title, "body": body}).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as res:
            res_data = json.loads(res.read().decode('utf-8'))
            return res_data.get("html_url"), res_data.get("number")
    except urllib.error.HTTPError as e:
        print(f"GitHub API Error: {e.code} - {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Failed to create GitHub issue: {e}")
    return None

def close_github_issue(issue_number):
    pat = get_pat()
    repo = get_repo_info()
    if not pat or not repo or not issue_number:
        return False
        
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}"
    headers = {
        "Authorization": f"token {pat}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Antigravity-Agent-Core"
    }
    data = json.dumps({"state": "closed"}).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers, method="PATCH")
    try:
        with urllib.request.urlopen(req) as res:
            return res.status == 200
    except Exception as e:
        print(f"Failed to close GitHub issue #{issue_number}: {e}")
    return False
