#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime

INBOX_DIR = ".agents/inbox"
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

def save_inbox(data):
    with open(INBOX_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def extract_telemetry(content):
    import re
    from datetime import datetime
    
    telemetry = re.findall(r'<telemetry>(.*?)</telemetry>', content, re.DOTALL)
    
    # GitOps Audit Logging
    audit_file = ".agents/inbox/audit.log"
    with open(audit_file, "a") as f:
        for t in telemetry:
            msg = f"[{datetime.utcnow().isoformat() + 'Z'}] TELEMETRY: {t.strip()}"
            print(f"[LIVE TELEMETRY] {t.strip()}")
            f.write(msg + "
")
            
    return re.sub(r'<telemetry>.*?</telemetry>', '', content, flags=re.DOTALL)


def add_message(sender, recipient, content):
    data = load_inbox()
    content_clean = extract_telemetry(content)

    
    # Check debate limits if this is a back-and-forth between implementer and reviewer
    if sender in ["implementer", "reviewer"] and recipient in ["implementer", "reviewer"]:
        data["debate_turn_count"] += 1
    
    if data["debate_turn_count"] >= 3:
        data["status"] = "blocked"
        print("ERROR: Debate limit reached (3 turns). Room is blocked. Escalating to @user or @planner.")
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
    return True

def view_recent():
    data = load_inbox()
    print(f"Room Status: {data['status']} | Debate Turns: {data['debate_turn_count']}")
    print("--- Recent Messages ---")
    for msg in data["messages"][-5:]:
        print(f"[{msg['timestamp']}] {msg['sender']} -> {msg['recipient']}: {msg['content']}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: inbox_manager.py [init|view|send <sender> <recipient> <message>]")
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == "init":
        init_inbox()
    elif cmd == "view":
        view_recent()
    elif cmd == "send" and len(sys.argv) >= 5:
        add_message(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print("Invalid command.")
        sys.exit(1)
