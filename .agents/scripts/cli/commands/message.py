import sys
import os
import json
import subprocess
import uuid
import re
from datetime import datetime, timezone

MESSAGES_DIR = ".agents/messages"

def get_sender_identity() -> str:
    # 1. Try to read active profile from git_profiles.json
    profiles_file = ".agents/git_profiles.json"
    if os.path.exists(profiles_file):
        try:
            with open(profiles_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                profiles = data.get("profiles", [])
                for p in profiles:
                    if p.get("active"):
                        return p.get("name")
        except Exception:
            pass
            
    # 2. Fallback: Git config user.name or user.email
    try:
        name = subprocess.run(['git', 'config', 'user.name'], stdout=subprocess.PIPE, text=True).stdout.strip()
        if name:
            return name
    except Exception:
        pass
    return "unknown-agent"

def run(args):
    if len(args) == 0:
        print("Usage: ./helper.sh message <send|list|status> [args...]")
        sys.exit(1)
        
    action = args[0].lower()
    
    if action == "send":
        if len(args) < 4:
            print("Usage: ./helper.sh message send <recipient> <action> <payload_json_or_text>")
            sys.exit(1)
            
        recipient = args[1]
        msg_action = args[2]
        payload_raw = args[3]
        
        # Parse payload as JSON if possible, otherwise store as string
        try:
            payload = json.loads(payload_raw)
        except Exception:
            payload = {"text": payload_raw}
            
        # Get active task ID if possible
        task_id = "unknown"
        try:
            res = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=subprocess.PIPE, text=True)
            branch = res.stdout.strip()
            m = re.search(r'(issue-\d+|task-\d+)', branch.lower())
            if m:
                task_id = m.group(1)
        except Exception:
            pass
            
        sender = get_sender_identity()
        msg_id = f"msg_{uuid.uuid4().hex[:10]}"
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        
        # Build message envelope
        msg = {
            "message_id": msg_id,
            "conversation_id": os.environ.get("CONVERSATION_ID", str(uuid.uuid4())),
            "timestamp": timestamp,
            "sender": sender,
            "recipient": recipient,
            "status": "pending",
            "payload": {
                "task_id": task_id,
                "action": msg_action,
                **payload
            }
        }
        
        if not os.path.exists(MESSAGES_DIR):
            os.makedirs(MESSAGES_DIR)
            
        msg_file = os.path.join(MESSAGES_DIR, f"{msg_id}.json")
        with open(msg_file, 'w', encoding='utf-8') as f:
            json.dump(msg, f, indent=2)
            
        print(f"Successfully sent message {msg_id} to {recipient}.")
        print(json.dumps(msg, indent=2))
        
    elif action == "list":
        if not os.path.exists(MESSAGES_DIR):
            print("No messages found (mailbox is empty).")
            return
            
        files = [f for f in os.listdir(MESSAGES_DIR) if f.endswith(".json")]
        if not files:
            print("No messages found (mailbox is empty).")
            return
            
        messages = []
        for f in files:
            try:
                with open(os.path.join(MESSAGES_DIR, f), 'r', encoding='utf-8') as mf:
                    messages.append(json.load(mf))
            except Exception:
                pass
                
        # Sort by timestamp
        messages.sort(key=lambda m: m.get("timestamp", ""))
        
        print(f"{'Message ID':<15} | {'Sender':<15} | {'Recipient':<15} | {'Status':<10} | {'Timestamp':<20} | {'Action':<15}")
        print("-" * 105)
        for m in messages:
            msg_id = m.get("message_id", "")
            sender = m.get("sender", "")
            recipient = m.get("recipient", "")
            status = m.get("status", "")
            timestamp = m.get("timestamp", "")
            payload = m.get("payload", {})
            action_type = payload.get("action", "")
            
            # Format status colors
            status_colored = status
            if status == "pending":
                status_colored = f"\033[93m{status}\033[0m"
            elif status == "completed":
                status_colored = f"\033[92m{status}\033[0m"
            elif status == "failed":
                status_colored = f"\033[91m{status}\033[0m"
                
            print(f"{msg_id:<15} | {sender:<15} | {recipient:<15} | {status_colored:<19} | {timestamp:<20} | {action_type:<15}")
            
    elif action == "status":
        if len(args) < 3:
            print("Usage: ./helper.sh message status <msg_id> <status> [reply_info_raw_or_json]")
            sys.exit(1)
            
        msg_id = args[1]
        new_status = args[2].lower()
        reply_raw = args[3] if len(args) >= 4 else None
        
        msg_file = os.path.join(MESSAGES_DIR, f"{msg_id}.json")
        if not os.path.exists(msg_file):
            print(f"Error: Message with ID '{msg_id}' not found.")
            sys.exit(1)
            
        try:
            with open(msg_file, 'r', encoding='utf-8') as f:
                msg = json.load(f)
        except Exception as e:
            print(f"Error reading message file: {e}")
            sys.exit(1)
            
        msg["status"] = new_status
        msg["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        
        if reply_raw:
            try:
                reply_payload = json.loads(reply_raw)
            except Exception:
                reply_payload = {"text": reply_raw}
            msg["reply"] = reply_payload
            
        try:
            with open(msg_file, 'w', encoding='utf-8') as f:
                json.dump(msg, f, indent=2)
            print(f"Successfully updated message {msg_id} status to '{new_status}'.")
        except Exception as e:
            print(f"Error writing message file: {e}")
            sys.exit(1)
            
    else:
        print(f"Error: Unknown action '{action}'. Available: send, list, status")
        sys.exit(1)
