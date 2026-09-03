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

def run_agent(agent_name: str, prompt: str):
    """Invokes an agent natively via agy to perform real cognitive tasks."""
    print(f"[MEETING] Invoking {agent_name}: {prompt}")
    cmd_prefix = ["agy"]
    try:
        subprocess.run(["agy", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except Exception:
        cmd_prefix = [sys.executable, "-m", "antigravity_cli"]
        
    cmd_args = cmd_prefix + ["--agent", agent_name, "--dangerously-skip-permissions", "--print", prompt]
    try:
        subprocess.run(cmd_args, cwd=str(ROOT), check=True)
    except Exception as e:
        sys.stderr.write(f"[MEETING ERROR] Failed to invoke {agent_name}: {e}\n")

def run_scrum_master(prompt: str):
    run_agent("scrum-master", prompt)

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
    """Compiles a meeting digest with active task and sprint inspection."""
    print("[STANDUP MEETING] Orchestrating team standup...")
    tasks_dir = ROOT / "tasks"
    pending = 0
    done = 0
    if tasks_dir.is_dir():
        for tf in tasks_dir.glob("*.yaml"):
            try:
                content = tf.read_text(encoding="utf-8")
                if "status: DONE" in content or 'status: "DONE"' in content:
                    done += 1
                else:
                    pending += 1
            except Exception as exc:
                sys.stderr.write(f"Notice reading task file: {exc}\n")

    msg = f"STANDUP SYNC: Active sprint sync conducted. Tasks: {done} completed, {pending} pending. Governance status: ACTIVE. Evidence_Source: tasks/ Falsifiability_Criteria: Check tasks/*.yaml"
    subprocess.run([sys.executable, str(ROOT / 'scripts' / 'inbox_manager.py'), 'send', 'scrum-master', '@all', msg], cwd=str(ROOT))
    subprocess.run([sys.executable, str(ROOT / 'scripts' / 'inbox_manager.py'), 'report'], cwd=str(ROOT))

def run_planning_meeting(topic: str):
    """Orchestrates a sprint planning meeting between Product Manager and Scrum Master."""
    print(f"[MEETING] Orchestrating Sprint Planning on: '{topic}'...")
    msg = f"PLANNING MEETING: Sprint planning initiated for '{topic}'. Product Manager analyzing requirements. Evidence_Source: intent.yaml Falsifiability_Criteria: Check tasks/"
    subprocess.run([sys.executable, str(ROOT / 'scripts' / 'inbox_manager.py'), 'send', 'scrum-master', 'product-manager', msg], cwd=str(ROOT))
    prompt = (
        f"SPRINT PLANNING MEETING: Topic: '{topic}'. "
        "Break down this topic into atomic user stories with acceptance criteria in tasks/."
    )
    run_agent("product-manager", prompt)
    subprocess.run([sys.executable, str(ROOT / 'scripts' / 'inbox_manager.py'), 'report'], cwd=str(ROOT))

def run_review_meeting():
    """Orchestrates an Architecture & QA Review Meeting before release."""
    print("[MEETING] Orchestrating Architecture & QA Review Meeting...")
    prompt = "ARCHITECTURE & QA REVIEW: Review recent git changes against the 9 ACI gates. Verify zero regressions."
    run_agent("qa-automation-lead", prompt)
    subprocess.run([sys.executable, str(ROOT / 'scripts' / 'inbox_manager.py'), 'report'], cwd=str(ROOT))

def run_single_cycle():
    print("[MEETING COORDINATOR] Executing single-cycle sync...")
    data = load_blackboard()
    if data:
        handle_preventive_action(data)
        handle_corrective_action(data)
    subprocess.run([sys.executable, str(ROOT / 'scripts' / 'inbox_manager.py'), 'report'], cwd=str(ROOT))

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

if __name__ == '__main__':
    args = sys.argv[1:]
    if "--once" in args or "--sync" in args:
        run_single_cycle()
    elif "--standup" in args:
        run_standup_meeting()
    elif "--planning" in args:
        idx = args.index("--planning")
        topic = args[idx + 1] if idx + 1 < len(args) else "General Sprint"
        run_planning_meeting(topic)
    elif "--review" in args:
        run_review_meeting()
    else:
        coordinator_loop()
