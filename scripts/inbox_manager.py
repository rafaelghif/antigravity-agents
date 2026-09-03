#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INBOX_DIR = str(ROOT / ".agents" / "inbox")
INBOX_FILE = os.path.join(INBOX_DIR, "state.json")

def init_inbox():
    os.makedirs(INBOX_DIR, exist_ok=True)
    if not os.path.exists(INBOX_FILE):
        with open(INBOX_FILE, 'w') as f:
            json.dump({
                "room_id": "default",
                "active_agents": [],
                "debate_turn_count": 0,
                "status": "active",
                "messages": []
            }, f, indent=2)

def load_inbox():
    init_inbox()
    with open(INBOX_FILE, 'r') as f:
        return json.load(f)

import tempfile

def save_inbox(data):
    # Atomic write
    dirname = os.path.dirname(INBOX_FILE)
    fd, temp_path = tempfile.mkstemp(dir=dirname, text=True)
    with os.fdopen(fd, 'w') as f:
        json.dump(data, f, indent=2)
    os.replace(temp_path, INBOX_FILE)


def extract_telemetry(content):
    import re
    from datetime import datetime
    
    telemetry = re.findall(r'<telemetry>(.*?)</telemetry>', content, re.DOTALL)
    
    # GitOps Audit Logging
    audit_file = str(ROOT / ".agents" / "inbox" / "audit.log")
    with open(audit_file, "a") as f:
        for t in telemetry:
            msg = f"[{datetime.utcnow().isoformat() + 'Z'}] TELEMETRY: {t.strip()}"
            print(f"[LIVE TELEMETRY] {t.strip()}")
            f.write(msg + "\n")
            
    return re.sub(r'<telemetry>.*?</telemetry>', '', content, flags=re.DOTALL)



def check_consensus(data):
    if len(data["messages"]) < 3: return False
    recent_msgs = [m["content"].lower() for m in data["messages"][-3:]]
    approvals = sum(1 for m in recent_msgs if "lgtm" in m or "approve" in m or "consensus reached" in m)
    if approvals >= 3:
        if data["status"] != "consensus_reached":
            data["status"] = "consensus_reached"
            print("[MoA] 3/3 Consensus Reached. Production gates unlocked.")
            save_inbox(data)
        return True
    return False

def add_message(sender, recipient, content):
    data = load_inbox()
    content_clean = extract_telemetry(content)


    
    # Check debate limits if this is a back-and-forth between any two agents
    if sender != "scrum-master" and recipient != "scrum-master" and sender != recipient:
        data["debate_turn_count"] += 1
    
    if data["debate_turn_count"] >= 10:
        data["status"] = "blocked"
        print("ERROR: Debate limit reached (10 turns). Room is blocked. Escalating to @user or @planner.")
        save_inbox(data)
        return False
        
    data["messages"].append({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "sender": sender,
        "recipient": recipient,
        "content": content
    })
    
    if sender not in data["active_agents"]:
        data["active_agents"].append(sender)
        
    save_inbox(data)
    print(f"Message from {sender} to {recipient} appended to Inbox.")
    check_consensus(data)
    return True

def view_recent():
    data = load_inbox()
    print(f"Room Status: {data['status']} | Debate Turns: {data['debate_turn_count']}")
    print("--- Recent Messages ---")
    for msg in data["messages"][-5:]:
        print(f"[{msg['timestamp']}] {msg['sender']} -> {msg['recipient']}: {msg['content']}")

def handle_workflow_step(role: str):
    init_inbox()
    print(f"[INBOX] Orchestrating workflow stage for role: {role}")
    add_message(
        sender="dag-orchestrator",
        recipient=role,
        content=f"Workflow step '{role}' activated and staged for execution."
    )
    print(f"✅ Workflow step for '{role}' registered in blackboard.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: inbox_manager.py [init|view|send <sender> <recipient> <message>|<role>]")
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == "init":
        init_inbox()
    elif cmd == "view":
        view_recent()
    elif cmd == "send" and len(sys.argv) >= 5:
        add_message(sys.argv[2], sys.argv[3], sys.argv[4])
    elif not cmd.startswith("-"):
        handle_workflow_step(cmd)
    else:
        print("Invalid command.")
        sys.exit(1)
