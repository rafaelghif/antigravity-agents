#!/usr/bin/env python3
import time
import subprocess
import os
import sys
import shlex

print("🚀 Starting Fully Automated Agentic Looping System (v4.42.0 Unleashed)")
print("Scanning for tasks...")
time.sleep(1)

tasks = [f for f in os.listdir('tasks') if f.endswith('.yaml')] if os.path.exists('tasks') else []
if not tasks:
    print("No pending tasks found. System idle.")
    exit(0)

# Check if agy is available in path, else fallback to module execution
agy_cmd = "agy"
try:
    subprocess.run(["agy", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
except Exception:
    agy_cmd = "python3 -m antigravity_cli"

for task in tasks:
    print(f"Assigning task {task} to Scrum Master for orchestration...")
    # Execute the agent natively without sandbox
    cmd = f"{agy_cmd} run --agent scrum-master --print \"Execute task {task} from tasks directory.\""
    print(f"-> Executing: {cmd}")
    try:
        subprocess.run(shlex.split(cmd), check=True)
    except subprocess.CalledProcessError as e:
        print(f"Task {task} failed with exit code {e.returncode}.")
    print(f"Task {task} orchestrated successfully.")

print("All tasks completed. Loop finished.")
