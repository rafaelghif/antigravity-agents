#!/usr/bin/env python3
import time
import subprocess
import json
import os

INBOX_FILE = '.agents/inbox/state.json'
CRON_INTERVAL = 300 # 5 minutes

def load_blackboard():
    if not os.path.exists(INBOX_FILE):
        return None
    with open(INBOX_FILE, 'r') as f:
        return json.load(f)

def coordinator_loop():
    print('Starting Automated Meeting Coordinator...')
    while True:
        data = load_blackboard()
        if data:
            agents = data.get('active_agents', [])
            status = data.get('status', 'active')
            
            if status == 'blocked':
                print('Detected blocked agents in blackboard. Resolving dependencies...')
                cmd = ['python3', 'scripts/inbox_manager.py', 'send', 'scrum-master', 'all', 'Unblocking agents. Resetting debate count.']
                subprocess.run(cmd)
                
            else:
                print('Pinging agents for status...')
                for agent in agents:
                    if agent != 'scrum-master':
                        cmd = ['python3', 'scripts/inbox_manager.py', 'send', 'scrum-master', agent, 'Status report requested. Respond immediately.']
                        subprocess.run(cmd)
        
        time.sleep(CRON_INTERVAL)

if __name__ == '__main__':
    coordinator_loop()
