#!/usr/bin/env python3
import os
import subprocess
import json
import sys

def run_cmd(cmd_args):
    result = subprocess.run(cmd_args, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def main():
    pr_num = os.environ.get("PR_NUMBER")
    if not pr_num:
        print("No PR_NUMBER provided. Skipping auto-review.")
        sys.exit(0)
    
    print(f"🤖 Hermes Reviewer triggered for PR #{pr_num}")
    
    # Run our strict L9 verification gates
    retcode, stdout, stderr = run_cmd([sys.executable, "scripts/verify.py", "--execute", "--terse"])
    
    if retcode == 0:
        print("✅ Code is L9 Perfect. Approving PR.")
        body = "### 🤖 Hermes Manager Auto-Review\n\n**Verdict:** `APPROVED` ✅\n\nCode has passed all static AST analysis, complexity checks, and semantic evaluation gates. Ready for production."
        event = "APPROVE"
    else:
        print("❌ Flaws detected. Requesting changes.")
        body = f"### 🤖 Hermes Manager Auto-Review\n\n**Verdict:** `REQUEST CHANGES` ❌\n\nCode violates L9 Enterprise standards. Please fix the following issues:\n\n```text\n{stdout}\n{stderr}\n```"
        event = "REQUEST_CHANGES"
    
    # Payload for GitHub API
    payload = {
        "body": body,
        "event": event
    }
    
    with open("review_payload.json", "w") as f:
        json.dump(payload, f)
    
    # Submit Review
    repo = os.environ.get("GITHUB_REPOSITORY", "rafaelghif/antigravity-agents")
    api_cmd = ["gh", "api", "-X", "POST", f"repos/{repo}/pulls/{pr_num}/reviews", "--input", "review_payload.json"]
    
    res, out, err = run_cmd(api_cmd)
    if res != 0:
        print(f"Failed to submit review: {err}")
    else:
        print("Review submitted successfully.")
        
    # Auto-merge if approved
    if event == "APPROVE":
        print("Attempting to auto-merge the PR and clean up branch...")
        # Use gh pr merge to squash and auto-delete branch to prevent PR/branch spam
        merge_cmd = ["gh", "pr", "merge", pr_num, "--repo", repo, "--squash", "--delete-branch", "--admin"]
        m_res, m_out, m_err = run_cmd(merge_cmd)
        if m_res == 0:
            print("PR successfully merged and branch deleted!")
        else:
            print(f"Failed to merge PR: {m_err}")
            
if __name__ == "__main__":
    main()
