#!/usr/bin/env python3
import subprocess
import sys
import os
import time
import platform

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def start_loop():
    print("[L9 SYSTEM] Starting Enterprise Agentic Loop (Cross-Platform)...")
    
    # 1. Start the meeting coordinator in the background
    coordinator_cmd = [sys.executable, str(ROOT / "scripts" / "meeting_coordinator.py")]
    
    # Ensure .agents/inbox directory exists
    inbox_dir = ROOT / ".agents" / "inbox"
    inbox_dir.mkdir(parents=True, exist_ok=True)
    log_file = open(inbox_dir / "coordinator.log", "a", encoding="utf-8")
    
    print("Starting background meeting coordinator...")
    # On Windows, we use CREATE_NEW_PROCESS_GROUP to detach if necessary
    if platform.system() == "Windows":
        CREATE_NEW_PROCESS_GROUP = getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0x00000200)
        coordinator_proc = subprocess.Popen(coordinator_cmd, stdout=log_file, stderr=subprocess.STDOUT, cwd=str(ROOT), creationflags=CREATE_NEW_PROCESS_GROUP)
    else:
        coordinator_proc = subprocess.Popen(coordinator_cmd, stdout=log_file, stderr=subprocess.STDOUT, cwd=str(ROOT), start_new_session=True)
        
    print(f"Meeting coordinator started (PID: {coordinator_proc.pid}).")
    time.sleep(1) # Give it a second to initialize

    # 2. Run the autonomous loop manager in the foreground
    print("Starting autonomous task loop...")
    loop_cmd = [sys.executable, str(ROOT / "scripts" / "autonomous_loop.py")]
    
    try:
        result = subprocess.run(loop_cmd, cwd=str(ROOT))
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\n[L9 SYSTEM] Loop interrupted. Stopping meeting coordinator...")
        coordinator_proc.terminate()
        sys.exit(0)
    except Exception as e:
        print(f"Error executing loop: {e}")
        coordinator_proc.terminate()
        sys.exit(1)

if __name__ == "__main__":
    start_loop()
