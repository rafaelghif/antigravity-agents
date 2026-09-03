#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime, timezone
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
            msg = f"[{datetime.now(timezone.utc).isoformat()}] TELEMETRY: {t.strip()}"
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
        print("[GOD MODE] Debate threshold reached (10 turns). Auto-resolving and resetting debate count to keep flow unblocked.")
        data["debate_turn_count"] = 0
        data["status"] = "active"
        
    data["messages"].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
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

def generate_report():
    data = load_inbox()
    notes_file = ROOT / "tasks" / "meeting_notes.md"
    notes_file.parent.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    active_agents = ", ".join(data.get("active_agents", [])) or "None"
    status = data.get("status", "active")
    debate_turns = data.get("debate_turn_count", 0)
    messages = data.get("messages", [])
    
    lines = [
        f"# 📋 Team Standup & Execution Report ({timestamp})",
        "",
        f"- **Room Status:** `{status.upper()}`",
        f"- **Active Agents:** `{active_agents}`",
        f"- **Debate Turn Count:** `{debate_turns}/10`",
        "",
        "## 💬 Recent Communications",
    ]
    
    if not messages:
        lines.append("*(No messages logged yet)*")
    else:
        for msg in messages[-10:]:
            ts = msg.get("timestamp", "")
            sender = msg.get("sender", "unknown")
            recipient = msg.get("recipient", "all")
            content = msg.get("content", "").strip()
            lines.append(f"- **[{sender} ➔ {recipient}]** `{ts}`: {content}")
            
    lines.extend([
        "",
        "## 🛡️ Governance & Consensus",
        f"- Consensus Reached: `{'YES' if status == 'consensus_reached' else 'IN_PROGRESS'}`",
        f"- Blocked State: `{'YES - Corrective Action Required' if status == 'blocked' else 'NO'}`",
        "",
        "---",
        "*Auto-generated by AAC L9 Enterprise Blackboard Engine.*"
    ])
    
    report_content = "\n".join(lines) + "\n"
    notes_file.write_text(report_content, encoding="utf-8")
    print(f"✅ Standup report generated at {notes_file.relative_to(ROOT)}")
    return report_content

def reset_inbox():
    data = load_inbox()
    data["debate_turn_count"] = 0
    data["status"] = "active"
    save_inbox(data)
    print("✅ Inbox debate turn count reset and room unblocked.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: inbox_manager.py [init|view|report|reset|send <sender> <recipient> <message>|<role>]")
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == "init":
        init_inbox()
    elif cmd == "view":
        view_recent()
    elif cmd == "report":
        generate_report()
    elif cmd == "reset":
        reset_inbox()
    elif cmd == "send" and len(sys.argv) >= 5:
        add_message(sys.argv[2], sys.argv[3], sys.argv[4])
    elif not cmd.startswith("-"):
        handle_workflow_step(cmd)
    else:
        print("Invalid command.")
        sys.exit(1)
