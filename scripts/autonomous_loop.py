#!/usr/bin/env python3
"""
Autonomous Loop Daemon Wrapper.
Monitors filesystem events and triggers the Hermes Orchestrator Engine.
"""
import os
import sys
import time
import glob
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

TASKS_DIR = 'tasks'
INTENT_FILE = 'intent.yaml'

def get_file_mtimes():
    mtimes = {}
    if os.path.exists(INTENT_FILE):
        mtimes[INTENT_FILE] = os.path.getmtime(INTENT_FILE)
    for task_file in glob.glob(os.path.join(TASKS_DIR, '*.yaml')):
        mtimes[task_file] = os.path.getmtime(task_file)
    return mtimes

def run_hermes_cycle():
    try:
        from hermes_manager import HermesEngine
        HermesEngine().run()
    except Exception as e:
        sys.stderr.write(f"Hermes execution notice: {e}\n")

def daemon_loop():
    print('Starting Autonomous Loop Daemon (Hermes Engine Integration)...')
    last_mtimes = {}
    while True:
        current_mtimes = get_file_mtimes()
        if current_mtimes != last_mtimes:
            print('Detected filesystem intent/task updates. Triggering Hermes...')
            last_mtimes = current_mtimes
            run_hermes_cycle()
        time.sleep(3)

if __name__ == '__main__':
    daemon_loop()
