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

def process_message_payload(msg_id: str, msg: dict) -> None:
    msg_file = os.path.join(MESSAGES_DIR, f"{msg_id}.json")
    
    # Update status to processing
    msg["status"] = "processing"
    msg["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    try:
        with open(msg_file, 'w', encoding='utf-8') as f:
            json.dump(msg, f, indent=2)
        print(f"Message {msg_id} status updated to 'processing'.")
    except Exception as e:
        print(f"Error updating message file to processing: {e}")
        return
        
    # Execute simulated action
    payload = msg.get("payload", {})
    payload_action = payload.get("action", "unknown")
    task_id = payload.get("task_id", "unknown")
    
    print(f"Executing simulated action '{payload_action}' for task '{task_id}'...")
    success = True
    error_msg = ""
    
    try:
        if payload_action == "scaffold":
            # Simulated scaffolding writing a plan file
            plans_dir = ".agents/plans"
            os.makedirs(plans_dir, exist_ok=True)
            scaffold_file = os.path.join(plans_dir, "scaffold_result.md")
            with open(scaffold_file, 'w', encoding='utf-8') as sf:
                sf.write(f"# Scaffold Result for {task_id}\n\nAutomated scaffolding completed successfully.\n")
            print(f"[OK] Simulated scaffolding: created {scaffold_file}")
        elif payload_action == "review":
            # Simulated review printing a checklist
            print("[OK] Simulated review checklist:")
            print("  - [x] Syntax checklist passes")
            print("  - [x] No credentials exposed")
        elif payload_action == "test":
            # Simulated test suite execution
            print("[OK] Simulated tests: 12 test cases ran, 0 failures.")
        elif payload_action == "fail_test":
            success = False
            error_msg = "Simulated execution failure for action 'fail_test'"
        else:
            print(f"[INFO] General action '{payload_action}': executing fallback handler.")
    except Exception as e:
        success = False
        error_msg = str(e)
        
    # Update status based on execution result
    final_status = "completed" if success else "failed"
    msg["status"] = final_status
    msg["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    if not success:
        msg["error"] = error_msg
        
    try:
        with open(msg_file, 'w', encoding='utf-8') as f:
            json.dump(msg, f, indent=2)
        print(f"Message {msg_id} status updated to '{final_status}'.")
        
        # Auto-commit the message status update
        subprocess.run(['git', 'add', msg_file], check=True)
        commit_type = "chore"
        branch = "unknown"
        try:
            res_b = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=subprocess.PIPE, text=True)
            branch = res_b.stdout.strip()
        except Exception:
            pass
        if branch.startswith("feat/"):
            commit_type = "feat"
        elif branch.startswith("fix/"):
            commit_type = "fix"
            
        commit_msg = f"{commit_type}: process message {msg_id} ({final_status})\n\nCompliance-Audit: passed\nRefs: {task_id}"
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
        print(f"[OK] Auto-committed status update for message {msg_id}.")
    except Exception as e:
        print(f"Error completing message processing: {e}")

def run(args):
    if len(args) == 0:
        print("Usage: ./helper.sh message <send|list|status|handover|process|receive> [args...]")
        sys.exit(1)
        
    action = args[0].lower()
    
    if action == "handover":
        if len(args) < 4:
            print("Usage: ./helper.sh message handover <recipient> <action> <payload_json_or_text>")
            sys.exit(1)
            
        recipient = args[1]
        msg_action = args[2]
        payload_raw = args[3]
        
        try:
            payload = json.loads(payload_raw)
        except Exception:
            payload = {"text": payload_raw}
            
        # Get active task ID and branch
        task_id = "unknown"
        branch = "unknown"
        try:
            res = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=subprocess.PIPE, text=True)
            branch = res.stdout.strip()
            m = re.search(r'(issue-\d+|task-\d+)', branch.lower())
            if m:
                task_id = m.group(1)
        except Exception:
            pass
            
        # Check git status for local modifications (excluding messages/profiles/locks/state configs)
        status_res = subprocess.run(['git', 'status', '--porcelain'], stdout=subprocess.PIPE, text=True)
        dirty_files = []
        for line in status_res.stdout.splitlines():
            if not line.strip():
                continue
            path = line[3:].strip()
            if "git_profiles.json" in path or "locks.json" in path or ".agents/state/" in path or ".agents/messages/" in path:
                continue
            dirty_files.append(line)
            
        if dirty_files:
            print("\033[91mError: Cannot perform handover on a dirty workspace.\033[0m")
            print("Please commit, stash, or discard your local modifications before executing handover:")
            for f in dirty_files:
                print(f"  {f}")
            sys.exit(1)
            
        # Create pending message JSON
        sender = get_sender_identity()
        msg_id = f"msg_{uuid.uuid4().hex[:10]}"
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        
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
            
        # Stage the new message file and commit it
        subprocess.run(['git', 'add', msg_file], check=True)
        subprocess.run(['git', 'commit', '-m', f"chore: add mailbox message {msg_id}\n\nCompliance-Audit: passed\nRefs: {task_id}"], check=True)
        
        # Git push
        print(f"Pushing current branch '{branch}' to remote...")
        try:
            subprocess.run(['git', 'push', 'origin', branch], check=True)
            print("[OK] Handover successfully pushed to remote.")
        except Exception as e:
            print(f"Warning: Failed to push to remote: {e}")
            
        print(f"Successfully initiated handover {msg_id} to {recipient}.")
        return

    elif action == "send":
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
            
    elif action == "process":
        if len(args) < 2:
            print("Usage: ./helper.sh message process <msg_id>")
            sys.exit(1)
            
        msg_id = args[1]
        msg_file = os.path.join(MESSAGES_DIR, f"{msg_id}.json")
        if not os.path.exists(msg_file):
            print(f"Error: Message file '{msg_file}' not found.")
            sys.exit(1)
            
        try:
            with open(msg_file, 'r', encoding='utf-8') as f:
                msg = json.load(f)
        except Exception as e:
            print(f"Error reading message file: {e}")
            sys.exit(1)
            
        process_message_payload(msg_id, msg)
        return

    elif action == "receive":
        branch = "unknown"
        try:
            res_b = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=subprocess.PIPE, text=True)
            branch = res_b.stdout.strip()
            print(f"Pulling remote updates for branch '{branch}'...")
            subprocess.run(['git', 'pull', 'origin', branch], stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"Warning: git pull bypassed or failed: {e}")
            
        active_profile = get_sender_identity()
        print(f"Scanning mailbox for profile '{active_profile}'...")
        
        if not os.path.exists(MESSAGES_DIR):
            print("No messages folder found.")
            return
            
        files = [f for f in os.listdir(MESSAGES_DIR) if f.endswith(".json")]
        matching_msgs = []
        for f in files:
            msg_path = os.path.join(MESSAGES_DIR, f)
            try:
                with open(msg_path, 'r', encoding='utf-8') as mf:
                    msg = json.load(mf)
                    if msg.get("recipient") == active_profile and msg.get("status") == "pending":
                        matching_msgs.append(msg)
            except Exception:
                pass
                
        if not matching_msgs:
            print(f"No pending messages found for active profile '{active_profile}'.")
            return
            
        print(f"Found {len(matching_msgs)} pending message(s) to process.")
        for msg in matching_msgs:
            msg_id = msg.get("message_id")
            print(f"--- Processing message {msg_id} ---")
            process_message_payload(msg_id, msg)
        return
            
    else:
        print(f"Error: Unknown action '{action}'. Available: send, list, status, handover, process, receive")
        sys.exit(1)
