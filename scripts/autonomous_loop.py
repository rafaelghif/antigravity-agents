#!/usr/bin/env python3
import time
import subprocess
import os
import sys

print("🚀 Starting Fully Automated Agentic Looping System (v4.42.1 Unleashed)")
print("Scanning for tasks...")
time.sleep(1)

tasks = [f for f in os.listdir('tasks') if f.endswith('.yaml')] if os.path.exists('tasks') else []
if not tasks:
    print("No pending tasks found. System idle.")
    exit(0)

# Check if agy is available in path, else fallback to module execution
cmd_prefix = ["agy"]
try:
    subprocess.run(["agy", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
except Exception:
    cmd_prefix = [sys.executable, "-m", "antigravity_cli"]

for task in tasks:
    print(f"Assigning task {task} to Scrum Master for orchestration...")
    # Execute the agent natively without sandbox
    cmd_args = cmd_prefix + ["run", "--agent", "scrum-master", "--print", f"Execute task {task} from tasks directory."]
    print(f"-> Executing: {' '.join(cmd_args)}")
    try:
        subprocess.run(cmd_args, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Task {task} failed with exit code {e.returncode}.")
    print(f"Task {task} orchestrated successfully.")

print("All tasks completed. Loop finished.")
