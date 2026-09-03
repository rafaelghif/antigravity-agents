#!/usr/bin/env python3
import time
import subprocess
import os
import sys

print("🚀 Starting Fully Automated Agentic Looping System (v4.43.0 Unleashed)")
print("Scanning for tasks...")
time.sleep(1)

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
tasks_dir = ROOT / "tasks"
pending_tasks = []
if tasks_dir.exists():
    for tf in sorted(tasks_dir.glob("*.yaml")):
        try:
            content = tf.read_text(encoding="utf-8")
            # Only process tasks that are not marked as DONE
            if not re.search(r'status:\s*(["\']?)DONE\1', content):
                pending_tasks.append(tf.name)
        except Exception as e:
            sys.stderr.write(f"Notice reading task {tf.name}: {e}\n")

if not pending_tasks:
    print("No pending tasks found. System idle.")
    sys.exit(0)

# Check if agy is available in path, else fallback to module execution
cmd_prefix = ["agy"]
try:
    subprocess.run(["agy", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
except Exception:
    cmd_prefix = [sys.executable, "-m", "antigravity_cli"]

has_failures = False
for task in pending_tasks:
    print(f"Assigning task {task} to Scrum Master for orchestration...")
    # Execute the agent natively without invalid 'run' subcommand
    cmd_args = cmd_prefix + ["--agent", "scrum-master", "--print", f"Execute task {task} from tasks directory."]
    print(f"-> Executing: {' '.join(cmd_args)}")
    try:
        subprocess.run(cmd_args, check=True)
        print(f"Task {task} orchestrated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Task {task} failed with exit code {e.returncode}.")
        has_failures = True

if has_failures:
    print("Loop finished with some failed tasks.")
    sys.exit(1)
else:
    print("All pending tasks completed. Loop finished.")
