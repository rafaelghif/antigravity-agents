#!/usr/bin/env python3
import time
import subprocess
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INBOX_FILE = str(ROOT / ".agents" / "inbox" / "state.json")
MEETING_NOTES = str(ROOT / "tasks" / "meeting_notes.md")
CRON_INTERVAL = 300 # 5 minutes

def load_blackboard():
    if not os.path.exists(INBOX_FILE):
        return None
    try:
        with open(INBOX_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        sys.stderr.write(f"Blackboard read error: {e}\n")
        return None

def save_blackboard(data):
    # Safe atomic write similar to inbox_manager
    import tempfile
    dirname = os.path.dirname(INBOX_FILE)
    os.makedirs(dirname, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(dir=dirname, text=True)
    with os.fdopen(fd, 'w') as f:
        json.dump(data, f, indent=2)
    os.replace(temp_path, INBOX_FILE)

def run_scrum_master(prompt):
    """Invokes the Scrum Master natively via agy to perform real cognitive tasks."""
    print(f"[MEETING] Invoking Scrum Master: {prompt}")
    cmd_prefix = ["agy"]
    try:
        subprocess.run(["agy", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except Exception:
        cmd_prefix = [sys.executable, "-m", "antigravity_cli"]
        
    cmd_args = cmd_prefix + ["--agent", "scrum-master", "--print", prompt]
    try:
        subprocess.run(cmd_args, cwd=str(ROOT), check=True)
    except Exception as e:
        sys.stderr.write(f"[MEETING ERROR] Failed to invoke Scrum Master: {e}\n")

def handle_preventive_action(data):
    """Detects if agents are debating too much and warns them before they get blocked."""
    turns = data.get('debate_turn_count', 0)
    if 7 <= turns < 10:
        print("[PREVENTIVE ACTION] High debate count detected. Warning agents.")
        subprocess.run([sys.executable, str(ROOT / 'scripts' / 'inbox_manager.py'), 'send', 'scrum-master', 'all', 
                        'PREVENTIVE WARNING: You are nearing the debate limit. Reach a consensus or escalate immediately.'],
                       cwd=str(ROOT))

def handle_corrective_action(data):
    """Unblocks the room and forces the Scrum Master to intervene."""
    if data.get('status') == 'blocked':
        print("[CORRECTIVE ACTION] Room is blocked. Resetting state and forcing Scrum Master intervention.")
        data['status'] = 'active'
        data['debate_turn_count'] = 0
        save_blackboard(data)
        
        # Force Scrum Master to resolve the conflict
        run_scrum_master("The agents have reached the debate limit and the room was blocked. Review the inbox and make a final executive decision to unblock them.")

def run_standup_meeting():
    """Compiles a meeting digest."""
    print("[STANDUP MEETING] Orchestrating team standup...")
    run_scrum_master(f"Read the last 10 messages from {INBOX_FILE}. Compile a structured Markdown meeting digest into {MEETING_NOTES} summarizing progress, blockers, and next action items. Do not hallucinate.")

def coordinator_loop():
    print('Starting L9 Enterprise Meeting Coordinator...')
    cycles = 0
    while True:
        data = load_blackboard()
        if data:
            handle_preventive_action(data)
            handle_corrective_action(data)
            
            # Every 3rd cycle (e.g., 15 mins), run a formal standup meeting
            if cycles > 0 and cycles % 3 == 0:
                run_standup_meeting()
                
        time.sleep(CRON_INTERVAL)
        cycles += 1

def run_single_cycle():
    print("[MEETING COORDINATOR] Executing single-cycle sync...")
    data = load_blackboard()
    if data:
        handle_preventive_action(data)
        handle_corrective_action(data)
    subprocess.run([sys.executable, str(ROOT / 'scripts' / 'inbox_manager.py'), 'report'], cwd=str(ROOT))

if __name__ == '__main__':
    if "--once" in sys.argv:
        run_single_cycle()
    else:
        coordinator_loop()
