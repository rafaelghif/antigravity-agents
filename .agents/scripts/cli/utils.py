import os
import sys
import json
import time

def find_workspace_root():
    """
    Finds the directory containing the '.agents' folder, starting from the current directory
    and walking up. Defaults to the current directory if not found.
    """
    curr = os.path.abspath(os.getcwd())
    while True:
        if os.path.isdir(os.path.join(curr, '.agents')):
            return curr
        parent = os.path.dirname(curr)
        if parent == curr:
            break
        curr = parent
    return os.path.abspath(os.getcwd())

def get_agents_dir():
    return os.path.join(find_workspace_root(), '.agents')

def get_memory_file():
    return os.path.join(get_agents_dir(), 'memory.md')

def print_title(title):
    print("==========================================================")
    print(f"  {title}")
    print("==========================================================")

def load_budget():
    budget_file = os.path.join(get_agents_dir(), 'token_budget.json')
    if os.path.exists(budget_file):
        try:
            with open(budget_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        "max_token_budget": 500000,
        "current_token_usage": 0,
        "alert_threshold_percent": 90,
        "profiles": {}
    }

def save_budget(budget):
    budget_file = os.path.join(get_agents_dir(), 'token_budget.json')
    with open(budget_file, 'w') as f:
        json.dump(budget, f, indent=2)

def log_token_usage(tokens):
    """
    Log token usage for both the active profile and globally.
    """
    budget = load_budget()
    
    # Update global usage
    budget["current_token_usage"] = budget.get("current_token_usage", 0) + tokens
    
    # Read active profile
    profile_file = os.path.join(get_agents_dir(), 'active_api_profile_name')
    active_profile = "default"
    if os.path.exists(profile_file):
        with open(profile_file, 'r') as f:
            active_profile = f.read().strip()
            
    # Update profile usage
    profiles = budget.get("profiles", {})
    if active_profile not in profiles:
        profiles[active_profile] = {
            "current_token_usage": 0,
            "max_token_budget": 500000
        }
    profiles[active_profile]["current_token_usage"] = profiles[active_profile].get("current_token_usage", 0) + tokens
    
    budget["profiles"] = profiles
    save_budget(budget)
    
    # Calculate warning thresholds
    global_usage = budget["current_token_usage"]
    global_limit = budget["max_token_budget"]
    pct = (global_usage / global_limit) * 100
    alert_threshold = budget.get("alert_threshold_percent", 90)
    
    print(f"Logged {tokens} tokens to profile '{active_profile}'.")
    print(f"  Active Profile Usage: {profiles[active_profile]['current_token_usage']} / {profiles[active_profile]['max_token_budget']}")
    print(f"  Global Usage: {global_usage} / {global_limit} ({pct:.1f}%)")
    
    if pct >= alert_threshold:
        print(f"\n[WARNING] Token usage has reached {pct:.1f}% of budget! Threshold is {alert_threshold}%.")
        print("Please wrap up your task, stage and commit completed tasks, and hand over.")
