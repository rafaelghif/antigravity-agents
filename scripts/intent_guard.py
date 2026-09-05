#!/usr/bin/env python3
"""
L9 Intent & Task Lifecycle Guard.
Enforces that intent.yaml is kept updated and tasks are properly managed when completed.
Dependency-free (uses pure Python regex).
"""
import sys
import re
from pathlib import Path

try:
    from scripts import platform_guard  # noqa: F401
except ImportError:
    import platform_guard  # noqa: F401

try:
    from scripts.intent_compiler import compile_intent
except ImportError:
    from intent_compiler import compile_intent

def check_intent(root: Path = None) -> bool:
    if root is None:
        root = Path(__file__).resolve().parents[1]
    intent_file = root / "intent.yaml"
    tasks_dir = root / "tasks"

    if not intent_file.is_file():
        intent_file.write_text(
            f'name: "{root.name}"\n'
            f'status: "DONE"\n'
            f'description: "Workspace intent managed by AAC for {root.name}."\n'
            f'objectives:\n'
            f'  - "Maintain high-quality, production-ready codebase."\n',
            encoding="utf-8"
        )
        print(f"💡 Initialized default intent.yaml for consumer project ({root.name}).")

    # 1. Strict schema validation & JSON compilation via intent_compiler
    if not compile_intent(str(intent_file)):
        print("=> FATAL: intent.yaml failed strict schema compilation!")
        return False

    with open(intent_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Search for status line
    status_match = re.search(r'^status:\s*(["\']?)(IN_PROGRESS|DONE)\1', content, re.MULTILINE)
    if not status_match:
        print("=> FATAL: intent.yaml must contain 'status: IN_PROGRESS' or 'status: DONE'.")
        print("This prevents stale intents. Update the status manually or ask the agent to do it.")
        return False
    
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
                        return False
                except Exception as e:
                    print(f"=> FATAL: Failed to read task {tf.name}: {e}")
                    return False
        print("✅ Intent is DONE and all tasks are completed. Ready for final release.")
        return True
    
    elif status == "IN_PROGRESS":
        if not tasks_dir.is_dir() or not list(tasks_dir.glob("*.yaml")):
            print("=> FATAL: intent.yaml is IN_PROGRESS, but tasks/ directory is empty!")
            print("You must split the architecture into micro-tasks (e.g. tasks/01_auth.yaml).")
            return False
        print("✅ Intent is IN_PROGRESS. Pending tasks detected. Keep working.")
        return True

    return False

def main():
    success = check_intent()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
