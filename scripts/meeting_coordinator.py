#!/usr/bin/env python3
import time
import subprocess
import json
import os
import sys

INBOX_FILE = '.agents/inbox/state.json'
CRON_INTERVAL = 300 # 5 minutes

def load_blackboard():
    if not os.path.exists(INBOX_FILE):
        return None
    try:
        with open(INBOX_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        sys.stderr.write(f"Blackboard read error: {e}\n")
        return None

def ping_agents(agents):
    for agent in agents:
        if agent != 'scrum-master':
            cmd = ['python3', 'scripts/inbox_manager.py', 'send', 'scrum-master', agent, 'Status report requested. Respond immediately.']
            try:
                subprocess.run(cmd, check=True)
            except Exception as e:
                sys.stderr.write(f"Ping error for {agent}: {e}\n")

def handle_coordination_cycle(data):
    if not data:
        return
    agents = data.get('active_agents', [])
    status = data.get('status', 'active')
    
    if status == 'blocked':
        print('Detected blocked agents in blackboard. Resolving dependencies...')
        cmd = ['python3', 'scripts/inbox_manager.py', 'send', 'scrum-master', 'all', 'Unblocking agents. Resetting debate count.']
        try:
            subprocess.run(cmd, check=True)
        except Exception as e:
            sys.stderr.write(f"Unblock error: {e}\n")
    else:
        print('Pinging agents for status...')
        ping_agents(agents)

def coordinator_loop():
    print('Starting Automated Meeting Coordinator...')
    while True:
        data = load_blackboard()
        handle_coordination_cycle(data)
        time.sleep(CRON_INTERVAL)

if __name__ == '__main__':
    coordinator_loop()
