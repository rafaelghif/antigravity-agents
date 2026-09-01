#!/usr/bin/env python3
"""
Hermes Orchestrator - Deep Iterative Loop Engine
"""
import os
import time
import yaml
import json
import subprocess
import glob

TASKS_DIR = 'tasks'

def load_tasks():
    tasks = []
    if not os.path.exists(TASKS_DIR):
        return tasks
    for f in sorted(glob.glob(os.path.join(TASKS_DIR, '*.yaml'))):
        with open(f, 'r') as file:
            try:
                data = yaml.safe_load(file)
                if data and data.get('status') == 'TODO':
                    tasks.append((f, data))
            except Exception:
                pass
    return tasks

def update_task_status(task_file, status):
    with open(task_file, 'r') as f:
        content = f.read()
    content = content.replace('status: "TODO"', f'status: "{status}"')
    content = content.replace('status: "IN_PROGRESS"', f'status: "{status}"')
    with open(task_file, 'w') as f:
        f.write(content)

def run_agent(agent_name, prompt):
    print(f"\n[Hermes] 🤖 Spawning {agent_name}...")
    cmd = ['agy', '--agent', agent_name, '--dangerously-skip-permissions', '-p', prompt]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def hermes_loop():
    print("🚀 Starting Hermes Orchestrator...")
    while True:
        tasks = load_tasks()
        if not tasks:
            print("💤 No pending tasks. Hermes is idling...")
            time.sleep(5)
            continue
            
        for task_file, task_data in tasks:
            task_id = task_data.get('id', 'unknown')
            title = task_data.get('title', 'Untitled')
            desc = task_data.get('description', '')
            
            print(f"\n📦 [Hermes] Processing Task: {title} ({task_id})")
            update_task_status(task_file, 'IN_PROGRESS')
            
            iteration = 1
            max_iterations = 3
            approved = False
            feedback = "Initial implementation."
            
            # Determine implementer
            implementer = "staff-backend"
            if "frontend" in desc.lower() or "ui" in title.lower():
                implementer = "frontend-architect"
            elif "database" in desc.lower() or "schema" in title.lower():
                implementer = "database-sre"
                
            while iteration <= max_iterations and not approved:
                print(f"\n🔄 [Hermes] Iteration {iteration}/{max_iterations}")
                
                # 1. IMPLEMENTATION PHASE
                print(f"   -> [Implementer] Assigning to {implementer}...")
                impl_prompt = f"TASK: {title}\nDESC: {desc}\nCONTEXT: {feedback}\n\nPlease implement the code to satisfy this task. Do not ask for permission, just write the files. Ensure tests pass."
                run_agent(implementer, impl_prompt)
                
                # 2. REVIEW PHASE
                print(f"   -> [Reviewer] Assigning to qa-automation-lead...")
                rev_prompt = f"TASK: {title}\nDESC: {desc}\n\nThe implementer has finished. Review the codebase and git diff. Output ONLY a valid JSON object in this exact format: {{\"status\": \"APPROVED\", \"feedback\": \"Looks good\"}} OR {{\"status\": \"REJECTED\", \"feedback\": \"Missing error handling in foo.py\"}}. DO NOT output any markdown blocks or other text."
                
                rev_output = run_agent("qa-automation-lead", rev_prompt)
                
                # Parse reviewer JSON
                try:
                    json_str = rev_output
                    if "{" in json_str and "}" in json_str:
                        json_str = json_str[json_str.find("{"):json_str.rfind("}")+1]
                        
                    rev_result = json.loads(json_str)
                    status = rev_result.get('status', 'REJECTED')
                    feedback = rev_result.get('feedback', 'No feedback provided.')
                    
                    if status == 'APPROVED':
                        print(f"   ✅ [Reviewer] APPROVED: {feedback}")
                        approved = True
                    else:
                        print(f"   ❌ [Reviewer] REJECTED: {feedback}")
                        iteration += 1
                        
                except json.JSONDecodeError:
                    print("   ⚠️ [Hermes] Failed to parse Reviewer JSON. Forcing iteration...")
                    feedback = f"Your previous output was not reviewed properly because the reviewer broke. The raw review was: {rev_output}. Please ensure the code works."
                    iteration += 1
                    
            if approved:
                print(f"🎉 [Hermes] Task {task_id} perfected after {iteration} iterations!")
                update_task_status(task_file, 'DONE')
            else:
                print(f"💀 [Hermes] Task {task_id} failed to reach perfection after {max_iterations} iterations. Marking BLOCKED.")
                update_task_status(task_file, 'BLOCKED')
                
if __name__ == '__main__':
    hermes_loop()
