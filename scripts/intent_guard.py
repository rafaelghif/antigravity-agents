#!/usr/bin/env python3
"""
L9 Intent & Task Lifecycle Guard.
Enforces that intent.yaml is kept updated and tasks are properly managed when completed.
Dependency-free (uses pure Python regex).
"""
import sys
import re
from pathlib import Path

def main():
    root = Path(__file__).resolve().parents[1]
    intent_file = root / "intent.yaml"
    tasks_dir = root / "tasks"

    if not intent_file.is_file():
        print("=> FATAL: intent.yaml is missing! [INTENT_ARCHITECTURE] violated.")
        sys.exit(1)

    with open(intent_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Search for status line
    status_match = re.search(r'^status:\s*(["\']?)(IN_PROGRESS|DONE)\1', content, re.MULTILINE)
    if not status_match:
        print("=> FATAL: intent.yaml must contain 'status: IN_PROGRESS' or 'status: DONE'.")
        print("This prevents stale intents. Update the status manually or ask the agent to do it.")
        sys.exit(1)
    
    status = status_match.group(2)

    if status == "DONE":
        # When intent is marked DONE, ensure all task files in tasks/ have status: DONE
        if tasks_dir.is_dir():
            task_files = list(tasks_dir.glob("*.yaml"))
            for tf in task_files:
                try:
                    t_content = tf.read_text(encoding="utf-8")
                    if not re.search(r'status:\s*(["\']?)DONE\1', t_content):
                        print(f"=> FATAL: intent.yaml is marked DONE, but task '{tf.name}' is not marked as DONE!")
                        sys.exit(1)
                except Exception as e:
                    print(f"=> FATAL: Failed to read task {tf.name}: {e}")
                    sys.exit(1)
        print("✅ Intent is DONE and all tasks are completed. Ready for final release.")
    
    elif status == "IN_PROGRESS":
        if not tasks_dir.is_dir() or not list(tasks_dir.glob("*.yaml")):
            print("=> FATAL: intent.yaml is IN_PROGRESS, but tasks/ directory is empty!")
            print("You must split the architecture into micro-tasks (e.g. tasks/01_auth.yaml).")
            sys.exit(1)
        print("✅ Intent is IN_PROGRESS. Pending tasks detected. Keep working.")

if __name__ == "__main__":
    main()
