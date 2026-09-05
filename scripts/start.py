#!/usr/bin/env python3
import subprocess
import sys
import os
import time
import platform

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def stop_process(proc: subprocess.Popen, log_file: object) -> None:
    print("Stopping meeting coordinator...")
    try:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=2)
    except Exception as exc:
        sys.stderr.write(f"Process termination notice: {exc}\n")
    finally:
        if hasattr(log_file, "close"):
            try:
                log_file.close()
            except Exception as e:
                sys.stderr.write(f"Log close notice: {e}\n")

def start_loop(mode: str = "auto") -> int:
    print(f"[L9 SYSTEM] Starting Enterprise Agentic Loop ({mode.upper()})...")
    
    # 1. Start the meeting coordinator in the background
    coordinator_cmd = [sys.executable, str(ROOT / "scripts" / "meeting_coordinator.py")]
    
    # Ensure .agents/inbox directory exists
    inbox_dir = ROOT / ".agents" / "inbox"
    inbox_dir.mkdir(parents=True, exist_ok=True)
    log_file = open(inbox_dir / "coordinator.log", "a", encoding="utf-8")
    
    print("Starting background meeting coordinator...")
    sub_env = os.environ.copy()
    sub_env["PYTHONIOENCODING"] = "utf-8"
    sub_env["PYTHONUTF8"] = "1"
    # On Windows, we use CREATE_NEW_PROCESS_GROUP to detach if necessary
    if platform.system() == "Windows":
        create_flags = getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0x00000200)
        coordinator_proc = subprocess.Popen(coordinator_cmd, stdout=log_file, stderr=subprocess.STDOUT, cwd=str(ROOT), creationflags=create_flags, env=sub_env)
    else:
        coordinator_proc = subprocess.Popen(coordinator_cmd, stdout=log_file, stderr=subprocess.STDOUT, cwd=str(ROOT), start_new_session=True, env=sub_env)
        
    print(f"Meeting coordinator started (PID: {coordinator_proc.pid}).")
    time.sleep(1) # Give it a second to initialize

    # 2. Run the task loop manager in the foreground
    if mode == "hermes":
        print("Starting Hermes DAG Orchestrator...")
        loop_cmd = [sys.executable, str(ROOT / "scripts" / "hermes_manager.py"), "--run"]
    else:
        print("Starting autonomous task loop...")
        loop_cmd = [sys.executable, str(ROOT / "scripts" / "autonomous_loop.py")]
    
    exit_code = 0
    try:
        result = subprocess.run(loop_cmd, cwd=str(ROOT), env=sub_env)
        exit_code = result.returncode
    except KeyboardInterrupt:
        print("\n[L9 SYSTEM] Loop interrupted.")
        exit_code = 0
    except Exception as e:
        print(f"Error executing loop: {e}")
        exit_code = 1
    finally:
        stop_process(coordinator_proc, log_file)
        
    return exit_code

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="L9 Enterprise Autonomous Daemon Runner")
    parser.add_argument("--hermes", action="store_true", help="Run Enterprise Hermes DAG Orchestrator")
    parser.add_argument("--status", action="store_true", help="Display Hermes task graph status and exit")
    args = parser.parse_args()

    if args.status:
        sub_env = os.environ.copy()
        sub_env["PYTHONIOENCODING"] = "utf-8"
        sub_env["PYTHONUTF8"] = "1"
        res = subprocess.run([sys.executable, str(ROOT / "scripts" / "hermes_manager.py"), "--status"], cwd=str(ROOT), env=sub_env)
        sys.exit(res.returncode)

    mode = "hermes" if args.hermes else "auto"
    sys.exit(start_loop(mode=mode))
