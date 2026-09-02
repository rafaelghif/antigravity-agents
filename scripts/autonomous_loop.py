#!/usr/bin/env python3
import time
import subprocess
import os
import shutil
import sys

print("🚀 Starting Fully Automated Agentic Looping System (L9 Expert Mode)")

agy_path = shutil.which("agy") or os.path.expanduser("~/.local/bin/agy")
if not os.path.exists(agy_path):
    print("ERROR: Antigravity CLI ('agy') not found. Agentic loop requires 'agy' binary.")
    sys.exit(1)

tasks_dir = "tasks"
if not os.path.exists(tasks_dir):
    print("No pending tasks found (tasks/ directory missing). System idle.")
    sys.exit(0)

tasks = sorted([f for f in os.listdir(tasks_dir) if f.endswith('.yaml')])
if not tasks:
    print("No pending tasks found. System idle.")
    sys.exit(0)

for task in tasks:
    task_path = os.path.join(tasks_dir, task)
    print(f"[{time.strftime('%H:%M:%S')}] Assigning task {task} to Scrum Master...")
    
    # Actually trigger the Antigravity CLI to spawn the agent
    cmd = [
        agy_path, 
        "--agent", "scrum-master", 
        "--print", f"Load task instructions from {task_path} and coordinate with expert agents via inbox_manager to complete the task."
    ]
    
    try:
        # Run the agent synchronously so we wait for the task to finish before moving to the next
        result = subprocess.run(cmd, capture_output=False)
        if result.returncode == 0:
            print(f"[{time.strftime('%H:%M:%S')}] Task {task} completed successfully.")
            # Move task to done or delete
            done_dir = os.path.join(tasks_dir, "done")
            os.makedirs(done_dir, exist_ok=True)
            shutil.move(task_path, os.path.join(done_dir, task))
        else:
            print(f"[{time.strftime('%H:%M:%S')}] ERROR: Task {task} failed with exit code {result.returncode}.")
            sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\nLoop interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Execution error: {e}")
        sys.exit(1)

print("✅ All tasks completed. Fully Agentic Loop finished.")
