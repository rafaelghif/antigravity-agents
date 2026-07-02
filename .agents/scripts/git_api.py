import os
import urllib.request
import json
import urllib.error
import subprocess
import sys
import re
from typing import Optional, Tuple

# Detect GITHUB_TOKEN or GIT_PAT from environment
def get_pat(silent: bool = False) -> Optional[str]:
    pat = os.getenv("GITHUB_TOKEN") or os.getenv("GIT_PAT")
    if not pat:
        profiles_file = ".agents/git_profiles.json"
        if os.path.exists(profiles_file):
            try:
                with open(profiles_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                profiles = data.get("profiles", [])
                active = next((p for p in profiles if p.get("active")), None)
                if active:
                    pat = active.get("git_token")
            except Exception:
                pass
    if not pat and not silent:
        print("[WARN] GitHub token (GITHUB_TOKEN or GIT_PAT) is not set in the environment.", file=sys.stderr)
    return pat

def get_repo_info() -> Optional[str]:
    # Attempt to parse repository owner and name from git remote URL
    try:
        res = subprocess.run(['git', 'remote', 'get-url', 'origin'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            print("[WARN] Git remote 'origin' is not configured.", file=sys.stderr)
            return None
        url = res.stdout.strip()
        # Parse git@github.com:owner/repo.git or https://github.com/owner/repo.git
        match = re.search(r'github\.com[:/]([^/]+/[^/\.]+)(\.git)?', url)
        if match:
            return match.group(1)
        print(f"[WARN] Could not parse repository info from URL: '{url}'", file=sys.stderr)
    except Exception as e:
        print(f"[WARN] Failed to get Git remote details: {e}", file=sys.stderr)
    return None

def create_github_issue(title: str, body: str = "") -> Optional[Tuple[str, int]]:
    pat = get_pat()
    repo = get_repo_info()
    if not pat or not repo:
        print("[WARN] Bypassing remote GitHub issue creation due to missing configuration.", file=sys.stderr)
        return None
        
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        "Authorization": f"Bearer {pat}",
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
        if e.code in (401, 403):
            print("[WARN] GitHub API unauthorized (401/403). Could not create remote issue.", file=sys.stderr)
        else:
            try:
                err_detail = e.read().decode('utf-8')
                print(f"[FAIL] GitHub API HTTP Error: {e.code} - {err_detail}", file=sys.stderr)
            except Exception:
                print(f"[FAIL] GitHub API HTTP Error: {e.code}", file=sys.stderr)
    except urllib.error.URLError:
        print("[WARN] Network offline. Could not create remote GitHub issue.", file=sys.stderr)
    except Exception as e:
        print(f"[FAIL] Failed to create GitHub issue: {e}", file=sys.stderr)
    return None

def close_github_issue(issue_number: int) -> bool:
    pat = get_pat()
    repo = get_repo_info()
    if not pat or not repo or not issue_number:
        print("[WARN] Bypassing remote GitHub issue closure due to missing configuration.", file=sys.stderr)
        return False
        
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}"
    headers = {
        "Authorization": f"Bearer {pat}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Antigravity-Agent-Core"
    }
    data = json.dumps({"state": "closed"}).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers, method="PATCH")
    try:
        with urllib.request.urlopen(req) as res:
            return res.status == 200
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            print(f"[WARN] GitHub API unauthorized (401/403). Could not close remote issue #{issue_number}.", file=sys.stderr)
        else:
            print(f"[FAIL] GitHub API HTTP Error: {e.code} on closing issue #{issue_number}", file=sys.stderr)
    except urllib.error.URLError:
        print(f"[WARN] Network offline. Could not close remote GitHub issue #{issue_number}.", file=sys.stderr)
    except Exception as e:
        print(f"[FAIL] Failed to close GitHub issue #{issue_number}: {e}", file=sys.stderr)
    return False

def fetch_github_issues(force: bool = False) -> Optional[list]:
    pat = get_pat(silent=True)
    repo = get_repo_info()
    if not pat or not repo:
        return None
        
    cache_file = ".agents/sync_cache.json"
    import time
    
    if not force and os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            last_sync = cache_data.get("last_sync_time", 0.0)
            if time.time() - last_sync < 300.0:
                return cache_data.get("cached_issues")
        except Exception:
            pass
        
    url = f"https://api.github.com/repos/{repo}/issues?state=all&per_page=100"
    headers = {
        "Authorization": f"Bearer {pat}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Antigravity-Agent-Core"
    }
    
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=3.0) as res:
            data = json.loads(res.read().decode('utf-8'))
            try:
                os.makedirs(os.path.dirname(cache_file), exist_ok=True)
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump({"last_sync_time": time.time(), "cached_issues": data}, f)
            except Exception:
                pass
            return data
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            print("[WARN] GitHub API unauthorized (401/403). Operating in offline mode.", file=sys.stderr)
        else:
            print(f"[WARN] Failed to fetch remote GitHub issues: HTTP Error {e.code}", file=sys.stderr)
    except urllib.error.URLError:
        print("[WARN] Network offline. Operating in offline mode.", file=sys.stderr)
    except Exception as e:
        print(f"[WARN] Failed to fetch remote GitHub issues: {e}", file=sys.stderr)
    return None

def post_commit_status(sha: str, state: str, target_url: str = "", description: str = "", context: str = "AAC Validation Guard") -> bool:
    """Post a validation status back to GitHub commit."""
    pat = get_pat(silent=True)
    repo = get_repo_info()
    if not pat or not repo or not sha:
        return False
        
    url = f"https://api.github.com/repos/{repo}/statuses/{sha}"
    headers = {
        "Authorization": f"Bearer {pat}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Antigravity-Agent-Core"
    }
    payload = {
        "state": state, # pending, success, error, failure
        "target_url": target_url,
        "description": description,
        "context": context
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as res:
            return res.status == 201
    except Exception as e:
        print(f"[FAIL] Failed to post commit status: {e}", file=sys.stderr)
    return False

def create_github_release(tag_name: str, name: str, body: str, draft: bool = True) -> Optional[str]:
    """Create a draft or published release on GitHub."""
    pat = get_pat()
    repo = get_repo_info()
    if not pat or not repo:
        print("[WARN] Bypassing remote GitHub release creation due to missing configuration.", file=sys.stderr)
        return None
        
    url = f"https://api.github.com/repos/{repo}/releases"
    headers = {
        "Authorization": f"Bearer {pat}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Antigravity-Agent-Core"
    }
    payload = {
        "tag_name": tag_name,
        "name": name,
        "body": body,
        "draft": draft
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as res:
            res_data = json.loads(res.read().decode('utf-8'))
            return res_data.get("html_url")
    except Exception as e:
        print(f"[FAIL] Failed to create GitHub release: {e}", file=sys.stderr)
    return None
