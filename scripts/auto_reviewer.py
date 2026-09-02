#!/usr/bin/env python3
import os
import subprocess
import json
import sys

def run_cmd(cmd_args):
    result = subprocess.run(cmd_args, capture_output=True, text=True, timeout=300)
    return result.returncode, result.stdout, result.stderr

def format_github_review(retcode, stdout, stderr):
    if retcode == 0:
        print("✅ Code is L9 Perfect. Approving PR.")
        body = "### 🤖 Hermes Manager Auto-Review\n\n**Verdict:** `APPROVED` ✅\n\nCode has passed all static AST analysis, complexity checks, and semantic evaluation gates. Ready for production."
        event = "APPROVE"
    else:
        print("❌ Flaws detected. Requesting changes.")
        body = f"### 🤖 Hermes Manager Auto-Review\n\n**Verdict:** `REQUEST CHANGES` ❌\n\nCode violates L9 Enterprise standards. Please fix the following issues:\n\n```text\n{stdout}\n{stderr}\n```"
        event = "REQUEST_CHANGES"
    return body, event

def submit_review(pr_num, body, event):
    payload = {
        "body": body,
        "event": event
    }
    
    with open("review_payload.json", "w") as f:
        json.dump(payload, f)
    
    repo = os.environ.get("GITHUB_REPOSITORY", "rafaelghif/antigravity-agents")
    api_cmd = ["gh", "api", "-X", "POST", f"repos/{repo}/pulls/{pr_num}/reviews", "--input", "review_payload.json"]
    
    res, out, err = run_cmd(api_cmd)
    if res != 0:
        print(f"Failed to submit review: {err}")
    else:
        print("Review submitted successfully.")
    return res, repo

def auto_merge_pr(pr_num, repo):
    print("Attempting to auto-merge the PR and clean up branch...")
    merge_cmd = ["gh", "pr", "merge", pr_num, "--repo", repo, "--squash", "--delete-branch", "--admin"]
    m_res, m_out, m_err = run_cmd(merge_cmd)
    if m_res == 0:
        print("PR successfully merged and branch deleted!")
    else:
        print(f"Failed to merge PR: {m_err}")

def main():
    pr_num = os.environ.get("PR_NUMBER")
    if not pr_num:
        print("No PR_NUMBER provided. Skipping auto-review.")
        sys.exit(0)
    
    print(f"🤖 Hermes Reviewer triggered for PR #{pr_num}")
    
    # Run our strict L9 verification gates
    retcode, stdout, stderr = run_cmd([sys.executable, "scripts/verify.py", "--execute", "--terse"])
    
    body, event = format_github_review(retcode, stdout, stderr)
    res, repo = submit_review(pr_num, body, event)
        
    # Auto-merge if approved
    if event == "APPROVE" and res == 0:
        auto_merge_pr(pr_num, repo)
            
if __name__ == "__main__":
    main()
