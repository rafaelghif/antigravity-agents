import sys
import os
import time
import subprocess
import json

def run(args):
    """
    Executes a periodic diagnostic heartbeat check on the agent's work environment.
    """
    print("==========================================================")
    print("   Antigravity Workspace Heartbeat Diagnostic Check       ")
    print("==========================================================")
    
    pulse_passed = True

    # 1. Soul & Identity Alignment Check
    soul_file = ".agents/soul.md"
    if os.path.exists(soul_file):
        print("[OK] Agent soul profile exists and is integrated.")
    else:
        print("[WARN] Agent soul profile (soul.md) is missing from .agents root.")
        pulse_passed = False

    # 2. Lock Compliance Check
    locks_dir = ".lock"
    active_locks = []
    if os.path.exists(locks_dir):
        for f in os.listdir(locks_dir):
            if f.endswith(".lock"):
                active_locks.append(f[:-5])
    if active_locks:
        print(f"[INFO] Active workspace module locks: {', '.join(active_locks)}")
    else:
        print("[OK] No active module locks currently held.")

    # 3. Git Hooks Compliance Check
    hooks = ['pre-commit', 'commit-msg', 'prepare-commit-msg']
    hooks_healthy = True
    for hook in hooks:
        hook_path = os.path.join(".git/hooks", hook)
        if not os.path.exists(hook_path):
            hooks_healthy = False
            break
    if hooks_healthy:
        print("[OK] Git hook triggers are active and operational.")
    else:
        print("[WARN] Git hook triggers are missing or incomplete. Run './helper.sh validate' to repair.")
        pulse_passed = False

    # 4. Token Budget Audit
    usage_file = ".agents/logs/token_usage.jsonl"
    budget_exhausted = False
    if os.path.exists(usage_file):
        # Read last 5 entries to estimate recent usage
        total_tokens = 0
        try:
            with open(usage_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            for line in lines[-5:]:
                data = json.loads(line)
                total_tokens += data.get("prompt_tokens", 0) + data.get("completion_tokens", 0)
            print(f"[OK] Token audit: Last 5 turns consumed {total_tokens} tokens total.")
        except Exception:
            pass
    else:
        print("[INFO] Token usage audit: No local logs created yet.")

    # 5. Git Working Status Check
    try:
        status_out = subprocess.check_output(
            ["git", "status", "--porcelain"],
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()
        if status_out:
            modified_count = len(status_out.split('\n'))
            print(f"[WARN] Working directory is dirty: {modified_count} unstaged/untracked modifications.")
        else:
            print("[OK] Working repository directory is clean.")
    except Exception:
        print("[WARN] Could not retrieve repository working status.")
        pulse_passed = False

    print("==========================================================")
    if pulse_passed:
        print("   Heartbeat: Healthy [PULSE NORMAL]                      ")
    else:
        print("   Heartbeat: Warning [PULSE IRREGULAR]                   ")
    print("==========================================================")
    
    if not pulse_passed:
        sys.exit(1)
