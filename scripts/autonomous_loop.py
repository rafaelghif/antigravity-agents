#!/usr/bin/env python3
import time
import subprocess
import os

print("🚀 Starting Fully Automated Agentic Looping System")
print("Scanning for tasks...")
time.sleep(1)

tasks = [f for f in os.listdir('tasks') if f.endswith('.yaml')] if os.path.exists('tasks') else []
if not tasks:
    print("No pending tasks found. System idle.")
    exit(0)

for task in tasks:
    print(f"Assigning task {task} to Scrum Master for orchestration...")
    # Trigger the agent CLI or API (mocked for now, as CLI integration is handled by user executing /goal or /boost)
    print("-> Triggering Meeting Protocol via inbox_manager...")
    subprocess.run(["python3", "scripts/inbox_manager.py", "send", "system", "scrum-master", f"Execute {task}"])
    time.sleep(2)
    print(f"Task {task} orchestrated successfully.")

print("All tasks completed. Loop finished.")
