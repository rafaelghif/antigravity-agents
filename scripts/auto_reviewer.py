#!/usr/bin/env python3
"""
L9 Automated Code & PR Reviewer:
Evaluates code diffs, runs static AST verification gates,
and generates structured Markdown review verdicts locally or submits to GitHub PRs via gh CLI.
"""
import os
import sys
import json
import tempfile
import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def run_cmd(cmd_args: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(cmd_args, capture_output=True, text=True, timeout=300, cwd=ROOT)
    return result.returncode, result.stdout, result.stderr

def format_review(retcode: int, stdout: str, stderr: str, diff_summary: str = "") -> tuple[str, str]:
    if retcode == 0:
        body = (
            "### 🤖 L9 Autonomous Quality Review\n\n"
            "**Verdict:** `APPROVED` ✅\n\n"
            "Code has passed all 9 technical gates (AST Complexity, Anti-Sham Testing, DRY Clone Detection, Git Hygiene, WCAG 2.2 AA).\n"
        )
        if diff_summary:
            body += f"\n```text\n{diff_summary}\n```\n"
        event = "APPROVE"
    else:
        err_text = (stderr.strip() or stdout.strip())
        body = (
            "### 🤖 L9 Autonomous Quality Review\n\n"
            "**Verdict:** `REQUEST CHANGES` ❌\n\n"
            "Code violates L9 Enterprise Quality Standards. The following issues were detected:\n\n"
            f"```text\n{err_text}\n```\n"
        )
        event = "REQUEST_CHANGES"
    return body, event

def submit_github_review(pr_num: str, repo: str, body: str, event: str) -> bool:
    payload = {"body": body, "event": event}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tf:
        json.dump(payload, tf)
        tmp_name = tf.name

    try:
        api_cmd = ["gh", "api", "-X", "POST", f"repos/{repo}/pulls/{pr_num}/reviews", "--input", tmp_name]
        res, out, err = run_cmd(api_cmd)
        if res != 0:
            sys.stderr.write(f"Failed to submit GitHub review: {err.strip()}\n")
            return False
        print(f"✅ Review successfully submitted to PR #{pr_num} ({event}).")
        return True
    finally:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)

def get_git_diff_summary() -> str:
    res, out, _ = run_cmd(["git", "diff", "--stat"])
    return out.strip() if res == 0 else ""

def main() -> None:
    parser = argparse.ArgumentParser(description="L9 Automated Code & PR Reviewer")
    parser.add_argument("--pr", type=str, default=os.environ.get("PR_NUMBER", ""), help="GitHub PR number to review")
    parser.add_argument("--repo", type=str, default=os.environ.get("GITHUB_REPOSITORY", ""), help="Target GitHub repository (e.g. owner/repo)")
    parser.add_argument("--submit", action="store_true", help="Submit review via gh CLI (requires gh authentication)")
    parser.add_argument("--terse", action="store_true", help="Output terse review summary")
    args = parser.parse_args()

    print("=" * 60)
    print("🔍 Running L9 Autonomous Verification Gates...")
    print("=" * 60)
    retcode, stdout, stderr = run_cmd([sys.executable, "scripts/verify.py", "--execute", "--terse"])
    
    diff_summary = get_git_diff_summary()
    body, event = format_review(retcode, stdout, stderr, diff_summary)

    print("\n" + body)

    if args.pr:
        if args.submit:
            repo = args.repo or "rafaelghif/antigravity-agents"
            submit_github_review(args.pr, repo, body, event)
        else:
            print("💡 Tip: Add --submit to automatically post this review to GitHub via gh CLI.")

    sys.exit(retcode)

if __name__ == "__main__":
    main()
