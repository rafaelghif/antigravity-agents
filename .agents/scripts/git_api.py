import os
import urllib.request
import json
import urllib.error
import subprocess
import sys
import re
from typing import Optional, Tuple

def get_active_profile() -> Optional[dict]:
    profiles_file = ".agents/git_profiles.json"
    if os.path.exists(profiles_file):
        try:
            with open(profiles_file, 'r', encoding='utf-8') as f:
                lines = [line for line in f if not line.strip().startswith("#")]
                data = json.loads("".join(lines))
            profiles = data.get("profiles", [])
            return next((p for p in profiles if p.get("active")), None)
        except Exception:
            pass
    return None

def get_service_info() -> Tuple[str, str, str, str, str]:
    # 1. Get git remote origin URL
    remote_url = ""
    try:
        res = subprocess.run(['git', 'remote', 'get-url', 'origin'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0:
            remote_url = res.stdout.strip()
    except Exception:
        pass

    # 2. Get active profile details
    profile_token = None
    gitea_token = None
    gitea_host = None
    
    profile = get_active_profile()
    if profile:
        profile_token = profile.get("git_pat") or profile.get("git_token")
        gitea_token = profile.get("gitea_token")
        gitea_host = profile.get("gitea_host")

    # Determine service type
    is_gitea = False
    if gitea_host or os.getenv("GITEA_HOST") or (remote_url and "github.com" not in remote_url):
        is_gitea = True

    if is_gitea:
        service = "gitea"
        host = os.getenv("GITEA_HOST") or gitea_host or "http://localhost:3000"
        host = host.rstrip("/")
        
        # Determine token
        token = os.getenv("GITEA_ACCESS_TOKEN") or gitea_token or ""
        if token.startswith("env:"):
            token = os.getenv(token[4:]) or ""
    else:
        service = "github"
        host = "https://api.github.com"
        
        token = os.getenv("GITHUB_TOKEN") or os.getenv("GIT_PAT") or profile_token or ""
        if token.startswith("env:"):
            token = os.getenv(token[4:]) or ""

    # Parse owner and repo name from remote origin URL
    owner, repo_name = "", ""
    if remote_url:
        url = remote_url
        if url.endswith(".git"):
            url = url[:-4]
        # Match SSH format: git@domain.com:owner/repo
        if ":" in url and not url.startswith("http"):
            parts = url.split(":", 1)
            path = parts[1]
            owner_repo = path.split("/", 1)
            if len(owner_repo) == 2:
                owner, repo_name = owner_repo[0], owner_repo[1]
        else:
            # Match HTTP format: https://domain.com/owner/repo or http://domain.com/owner/repo
            match = re.search(r'https?://[^/]+/([^/]+)/([^/]+)', url)
            if match:
                owner, repo_name = match.group(1), match.group(2)
                
    return service, host, token, owner, repo_name

def get_pat(silent: bool = False) -> Optional[str]:
    service, _, token, _, _ = get_service_info()
    if not token and not silent:
        print(f"[WARN] Access token for {service.upper()} is not configured.", file=sys.stderr)
    return token if token else None

def get_repo_info() -> Optional[str]:
    _, _, _, owner, repo = get_service_info()
    if owner and repo:
        return f"{owner}/{repo}"
    return None

def create_github_issue(title: str, body: str = "") -> Optional[Tuple[str, int]]:
    service, host, token, owner, repo = get_service_info()
    if not token or not owner or not repo:
        print(f"[WARN] Bypassing remote {service.upper()} issue creation due to missing configuration.", file=sys.stderr)
        return None
        
    if service == "github":
        url = f"{host}/repos/{owner}/{repo}/issues"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Antigravity-Agent-Core"
        }
    else: # gitea
        url = f"{host}/api/v1/repos/{owner}/{repo}/issues"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/json",
            "User-Agent": "Antigravity-Agent-Core"
        }
        
    data = json.dumps({"title": title, "body": body}).encode('utf-8')
    headers["Content-Type"] = "application/json"
    
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10.0) as res:
            res_data = json.loads(res.read().decode('utf-8'))
            return res_data.get("html_url"), res_data.get("number")
    except urllib.error.HTTPError as e:
        sys.stderr.write(f"[WARN] {service.upper()} API error code: {e.code}\n")
    except Exception as e:
        sys.stderr.write(f"[FAIL] Failed to create remote issue on {service.upper()}: {e}\n")
    return None

def close_github_issue(issue_number: int) -> bool:
    service, host, token, owner, repo = get_service_info()
    if not token or not owner or not repo or not issue_number:
        print(f"[WARN] Bypassing remote {service.upper()} issue closure due to missing configuration.", file=sys.stderr)
        return False
        
    if service == "github":
        url = f"{host}/repos/{owner}/{repo}/issues/{issue_number}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Antigravity-Agent-Core"
        }
    else: # gitea
        url = f"{host}/api/v1/repos/{owner}/{repo}/issues/{issue_number}"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/json",
            "User-Agent": "Antigravity-Agent-Core"
        }
        
    data = json.dumps({"state": "closed"}).encode('utf-8')
    headers["Content-Type"] = "application/json"
    
    req = urllib.request.Request(url, data=data, headers=headers, method="PATCH")
    try:
        with urllib.request.urlopen(req, timeout=10.0) as res:
            return res.status in (200, 201)
    except Exception as e:
        sys.stderr.write(f"[FAIL] Failed to close remote issue #{issue_number} on {service.upper()}: {e}\n")
    return False

def fetch_github_issues(force: bool = False) -> Optional[list]:
    service, host, token, owner, repo = get_service_info()
    if not token or not owner or not repo:
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
            
    if service == "github":
        url = f"{host}/repos/{owner}/{repo}/issues?state=all&per_page=100"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Antigravity-Agent-Core"
        }
    else: # gitea
        url = f"{host}/api/v1/repos/{owner}/{repo}/issues?state=all&limit=100"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/json",
            "User-Agent": "Antigravity-Agent-Core"
        }
        
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=5.0) as res:
            data = json.loads(res.read().decode('utf-8'))
            try:
                os.makedirs(os.path.dirname(cache_file), exist_ok=True)
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump({"last_sync_time": time.time(), "cached_issues": data}, f)
            except Exception:
                pass
            return data
    except Exception as e:
        sys.stderr.write(f"[WARN] Failed to fetch remote issues from {service.upper()}: {e}\n")
    return None

def post_commit_status(sha: str, state: str, target_url: str = "", description: str = "", context: str = "AAC Validation Guard") -> bool:
    service, host, token, owner, repo = get_service_info()
    if not token or not owner or not repo or not sha:
        return False
        
    if service == "github":
        url = f"{host}/repos/{owner}/{repo}/statuses/{sha}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Antigravity-Agent-Core"
        }
    else: # gitea
        url = f"{host}/api/v1/repos/{owner}/{repo}/statuses/{sha}"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/json",
            "User-Agent": "Antigravity-Agent-Core"
        }
        
    payload = {
        "state": state, # pending, success, error, failure
        "target_url": target_url,
        "description": description,
        "context": context
    }
    data = json.dumps(payload).encode('utf-8')
    headers["Content-Type"] = "application/json"
    
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10.0) as res:
            return res.status in (200, 201)
    except Exception as e:
        sys.stderr.write(f"[FAIL] Failed to post status to {service.upper()}: {e}\n")
    return False

def create_github_release(tag_name: str, name: str, body: str, draft: bool = True) -> Optional[str]:
    service, host, token, owner, repo = get_service_info()
    if not token or not owner or not repo:
        print(f"[WARN] Bypassing remote {service.upper()} release creation due to missing configuration.", file=sys.stderr)
        return None
        
    if service == "github":
        url = f"{host}/repos/{owner}/{repo}/releases"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Antigravity-Agent-Core"
        }
    else: # gitea
        url = f"{host}/api/v1/repos/{owner}/{repo}/releases"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/json",
            "User-Agent": "Antigravity-Agent-Core"
        }
        
    payload = {
        "tag_name": tag_name,
        "name": name,
        "body": body,
        "draft": draft
    }
    data = json.dumps(payload).encode('utf-8')
    headers["Content-Type"] = "application/json"
    
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10.0) as res:
            res_data = json.loads(res.read().decode('utf-8'))
            return res_data.get("html_url")
    except Exception as e:
        sys.stderr.write(f"[FAIL] Failed to create release on {service.upper()}: {e}\n")
    return None
