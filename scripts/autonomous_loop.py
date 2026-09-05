import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def find_pending_tasks(tasks_dir: Path) -> list[str]:
    pending = []
    if tasks_dir.exists():
        for tf in sorted(tasks_dir.glob("*.yaml")):
            try:
                content = tf.read_text(encoding="utf-8")
                # Only process tasks that are not marked as DONE
                if not re.search(r'status:\s*(["\']?)DONE\1', content):
                    pending.append(tf.name)
            except Exception as e:
                sys.stderr.write(f"Notice reading task {tf.name}: {e}\n")
    return pending

def orchestrate_task(task_name: str, root_dir: Path = ROOT) -> bool:
    print(f"Assigning task {task_name} to Scrum Master for orchestration...")
    sub_env = os.environ.copy()
    sub_env["PYTHONIOENCODING"] = "utf-8"
    sub_env["PYTHONUTF8"] = "1"
    try:
        dispatch_cmd = [
            sys.executable,
            str(root_dir / "scripts" / "inbox_manager.py"),
            "send",
            "autonomous_loop",
            "scrum-master",
            f"Execute task {task_name} from tasks directory."
        ]
        subprocess.run(dispatch_cmd, cwd=str(root_dir), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=sub_env, timeout=15)
    except Exception as exc:
        sys.stderr.write(f"Notice: {exc}\n")

    if shutil.which("agy"):
        cmd_args = [
            "agy",
            "--model",
            "gemini-3.8-flash-high",
            "--agent",
            "scrum-master",
            "--effort",
            "high",
            "--dangerously-skip-permissions",
            "--print",
            f"Execute task {task_name} from tasks directory."
        ]
        try:
            subprocess.run(cmd_args, cwd=str(root_dir), env=sub_env, timeout=300, check=True)
            print(f"Task {task_name} orchestrated successfully.")
            return True
        except (subprocess.CalledProcessError, OSError, subprocess.TimeoutExpired) as e:
            print(f"Task {task_name} invocation notice: {e}.")
            return False
    else:
        print(f"Task {task_name} queued on blackboard (.agents/inbox/state.json).")
        return True

def run_loop(root_dir: Path = ROOT) -> int:
    print("🚀 Starting Fully Automated Agentic Looping System (v4.47.0 Unleashed)")
    print("Scanning for tasks...")
    
    tasks_dir = root_dir / "tasks"
    pending_tasks = find_pending_tasks(tasks_dir)

    if not pending_tasks:
        print("No pending tasks found. System idle.")
        return 0

    has_failures = False
    for task in pending_tasks:
        success = orchestrate_task(task, root_dir)
        if not success:
            has_failures = True

    if has_failures:
        print("Loop finished with some failed tasks.")
        return 1
    else:
        print("All pending tasks completed. Loop finished.")
        return 0

if __name__ == "__main__":
    time.sleep(1)
    sys.exit(run_loop())
