#!/usr/bin/env python3
import os
import time
import yaml
import subprocess
import glob

TASKS_DIR = 'tasks'
INTENT_FILE = 'intent.yaml'

def get_file_mtimes():
    mtimes = {}
    if os.path.exists(INTENT_FILE):
        mtimes[INTENT_FILE] = os.path.getmtime(INTENT_FILE)
    for task_file in glob.glob(os.path.join(TASKS_DIR, '*.yaml')):
        mtimes[task_file] = os.path.getmtime(task_file)
    return mtimes

def load_tasks():
    tasks = {}
    for task_file in glob.glob(os.path.join(TASKS_DIR, '*.yaml')):
        if os.path.getsize(task_file) == 0:
            continue
        with open(task_file, 'r') as f:
            try:
                task_data = yaml.safe_load(f)
                if task_data and 'id' in task_data:
                    tasks[task_data['id']] = {
                        'file': task_file,
                        'data': task_data,
                        'status': task_data.get('status', 'TODO')
                    }
            except Exception as e:
                print(f'Error parsing {task_file}: {e}')
    return tasks

active_processes = {}

def spawn_agent(task_id, task_file):
    print(f'Spawning agent for task: {task_id}')
    cmd = ['python3', 'scripts/inbox_manager.py', 'send', 'scrum-master', f'agent-{task_id}', f'Assigning task {task_id}']
    proc = subprocess.Popen(cmd)
    active_processes[task_id] = proc

def check_processes():
    completed = []
    for tid, proc in active_processes.items():
        if proc.poll() is not None:
            completed.append(tid)
    for tid in completed:
        print(f'Agent process for {tid} completed with code {active_processes[tid].returncode}')
        del active_processes[tid]

def daemon_loop():
    print('Starting Autonomous Loop Daemon...')
    last_mtimes = {}
    while True:
        current_mtimes = get_file_mtimes()
        if current_mtimes != last_mtimes:
            print('Detected file changes.')
            last_mtimes = current_mtimes
            
            tasks = load_tasks()
            
            for tid, tinfo in tasks.items():
                status = tinfo['status']
                if status in ('TODO', 'IN_PROGRESS'):
                    if tid not in active_processes:
                        spawn_agent(tid, tinfo['file'])
                        
            if all(t['status'] == 'DONE' for t in tasks.values()) and len(tasks) > 0:
                print('All tasks are DONE. Idling...')
        
        check_processes()
        time.sleep(2)

if __name__ == '__main__':
    daemon_loop()
