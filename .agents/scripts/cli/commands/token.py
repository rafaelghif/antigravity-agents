import sys
import os
import json
import re
import subprocess
from datetime import datetime
from typing import List

BUDGET_FILE = ".agents/token_budget.json"
LOG_FILE = ".agents/logs/token_usage.log"

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def print_err(msg: str) -> None:
    print(f"{RED}[FAIL] {msg}{RESET}")

def print_warn(msg: str) -> None:
    print(f"{YELLOW}[WARN] {msg}{RESET}")

def print_ok(msg: str) -> None:
    print(f"{GREEN}[OK] {msg}{RESET}")

def get_active_profile_name() -> str:
    """Detect active profile name from git_profiles.json."""
    profiles_file = ".agents/git_profiles.json"
    if os.path.exists(profiles_file):
        try:
            with open(profiles_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                profiles = data.get("profiles", [])
                for p in profiles:
                    if p.get("active"):
                        return p.get("name", "default")
        except Exception:
            pass
    return "default"

def load_budget() -> dict:
    default_budget = {
        "monthly_limit": 5000000,
        "monthly_used": 0,
        "daily_limit": 500000,
        "daily_used": 0,
        "last_reset": datetime.utcnow().isoformat() + "Z",
        "accounts": {},
        "tasks": {}
    }
    if not os.path.exists(BUDGET_FILE):
        return default_budget
    try:
        with open(BUDGET_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Guarantee structure
            for key in default_budget:
                if key not in data:
                    data[key] = default_budget[key]
            if "accounts" not in data:
                data["accounts"] = {}
            return data
    except Exception:
        return default_budget

def save_budget(data: dict) -> None:
    os.makedirs(os.path.dirname(BUDGET_FILE), exist_ok=True)
    try:
        with open(BUDGET_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print_err(f"Failed to save token budget: {e}")

def check_date_resets(budget: dict) -> dict:
    """Check if day or month has changed relative to last_reset, and reset budget values if so."""
    try:
        last_reset_str = budget.get("last_reset", "")
        # Standardize Z to UTC offset for fromisoformat in older Python
        if last_reset_str.endswith("Z"):
            last_reset_str = last_reset_str[:-1] + "+00:00"
        last_reset_dt = datetime.fromisoformat(last_reset_str)
    except Exception:
        last_reset_dt = datetime.utcnow()

    now_dt = datetime.utcnow()
    
    # 1. Monthly Reset
    if now_dt.year != last_reset_dt.year or now_dt.month != last_reset_dt.month:
        budget["monthly_used"] = 0
        budget["daily_used"] = 0
        if "accounts" in budget:
            for acc in budget["accounts"].values():
                acc["daily_used"] = 0
                acc["monthly_used"] = 0
        budget["last_reset"] = now_dt.isoformat() + "Z"
        print_ok("New month detected. Reset monthly and daily token usage counters.")
    # 2. Daily Reset
    elif now_dt.date() != last_reset_dt.date():
        budget["daily_used"] = 0
        if "accounts" in budget:
            for acc in budget["accounts"].values():
                acc["daily_used"] = 0
        budget["last_reset"] = now_dt.isoformat() + "Z"
        print_ok("New day detected. Reset daily token usage counter.")

    return budget

def get_current_task_id() -> str:
    """Attempt to extract task ID from active git branch name."""
    try:
        res = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if res.returncode == 0:
            branch = res.stdout.strip()
            match = re.search(r'(task-\d+|issue-\d+)', branch.lower())
            if match:
                return match.group(1)
    except Exception:
        pass
    return "unknown"

def append_to_log(task_id: str, prompt: int, completion: int) -> None:
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    total = prompt + completion
    log_line = f"[{timestamp}] Task: {task_id} | Prompt: {prompt} | Completion: {completion} | Total: {total}\n"
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line)
    except Exception as e:
        print_warn(f"Could not write to token log file: {e}")

def run_log(args: List[str]) -> None:
    if len(args) < 2:
        print("Usage: helper.py token log <prompt_tokens> <completion_tokens> [--task <task_id>]")
        sys.exit(1)

    try:
        prompt = int(args[0])
        completion = int(args[1])
        if prompt < 0 or completion < 0:
            raise ValueError()
    except ValueError:
        print_err("Prompt and completion tokens must be non-negative integers.")
        sys.exit(1)

    task_id = None
    if "--task" in args:
        try:
            idx = args.index("--task")
            if idx + 1 < len(args):
                task_id = args[idx + 1]
        except Exception:
            pass

    if not task_id:
        task_id = get_current_task_id()

    budget = load_budget()
    budget = check_date_resets(budget)

    total = prompt + completion

    # Update daily and monthly
    budget["daily_used"] += total
    budget["monthly_used"] += total

    # Update per-account
    account_name = get_active_profile_name()
    if "accounts" not in budget:
        budget["accounts"] = {}
    if account_name not in budget["accounts"]:
        budget["accounts"][account_name] = {
            "daily_used": 0,
            "monthly_used": 0,
            "total_used": 0
        }
    budget["accounts"][account_name]["daily_used"] += total
    budget["accounts"][account_name]["monthly_used"] += total
    budget["accounts"][account_name]["total_used"] += total

    # Update task-specific
    if "tasks" not in budget:
        budget["tasks"] = {}

    if task_id not in budget["tasks"]:
        budget["tasks"][task_id] = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "updated_at": ""
        }

    budget["tasks"][task_id]["prompt_tokens"] += prompt
    budget["tasks"][task_id]["completion_tokens"] += completion
    budget["tasks"][task_id]["total_tokens"] += total
    budget["tasks"][task_id]["updated_at"] = datetime.utcnow().isoformat() + "Z"

    save_budget(budget)
    append_to_log(task_id, prompt, completion)

    print_ok(f"Logged {total} tokens for task '{task_id}' (account: '{account_name}').")
    
    # Enforce strict warning alerts on budget limit breach
    if budget["daily_used"] > budget["daily_limit"]:
        print_warn(f"Daily token budget limit exceeded! Used: {budget['daily_used']}/{budget['daily_limit']}")
    if budget["monthly_used"] > budget["monthly_limit"]:
        print_warn(f"Monthly token budget limit exceeded! Used: {budget['monthly_used']}/{budget['monthly_limit']}")

def run_status(args: List[str]) -> None:
    budget = load_budget()
    budget = check_date_resets(budget)

    daily_used = budget.get("daily_used", 0)
    daily_limit = budget.get("daily_limit", 500000)
    daily_pct = (daily_used / daily_limit * 100) if daily_limit > 0 else 0

    monthly_used = budget.get("monthly_used", 0)
    monthly_limit = budget.get("monthly_limit", 5000000)
    monthly_pct = (monthly_used / monthly_limit * 100) if monthly_limit > 0 else 0

    print("="*60)
    print("                Antigravity Token Budget Status")
    print("="*60)
    print(f"Daily Limit   : {daily_limit:,} tokens")
    print(f"Daily Used    : {daily_used:,} tokens ({daily_pct:.2f}% utilized)")
    print(f"Monthly Limit : {monthly_limit:,} tokens")
    print(f"Monthly Used  : {monthly_used:,} tokens ({monthly_pct:.2f}% utilized)")
    print(f"Last Reset    : {budget.get('last_reset', 'N/A')}")
    print("-"*60)
    print("Account Breakdown:")
    accounts = budget.get("accounts", {})
    if not accounts:
        print("  No accounts logged yet.")
    else:
        for acc_name, acc_info in sorted(accounts.items()):
            print(f"  - {acc_name:<15}: daily {acc_info.get('daily_used', 0):,} | monthly {acc_info.get('monthly_used', 0):,} | total {acc_info.get('total_used', 0):,}")
    print("-"*60)
    print("Task Breakdown:")
    
    tasks = budget.get("tasks", {})
    if not tasks:
        print("  No tasks logged yet.")
    else:
        for t_id, info in sorted(tasks.items()):
            print(f"  - {t_id:<15}: {info.get('total_tokens', 0):,} total ({info.get('prompt_tokens', 0):,} prompt / {info.get('completion_tokens', 0):,} completion)")
    print("="*60)

def run_reset(args: List[str]) -> None:
    budget = load_budget()
    
    if "--all" in args or not args:
        budget["daily_used"] = 0
        budget["monthly_used"] = 0
        budget["tasks"] = {}
        budget["accounts"] = {}
        budget["last_reset"] = datetime.utcnow().isoformat() + "Z"
        print_ok("Reset all token budget usage counters, task breakdown, and account statistics.")
    elif "--daily" in args:
        budget["daily_used"] = 0
        if "accounts" in budget:
            for acc in budget["accounts"].values():
                acc["daily_used"] = 0
        budget["last_reset"] = datetime.utcnow().isoformat() + "Z"
        print_ok("Reset daily token budget usage counter.")
    elif "--monthly" in args:
        budget["monthly_used"] = 0
        if "accounts" in budget:
            for acc in budget["accounts"].values():
                acc["daily_used"] = 0
                acc["monthly_used"] = 0
        budget["last_reset"] = datetime.utcnow().isoformat() + "Z"
        print_ok("Reset monthly token budget usage counter.")
    else:
        print("Usage: helper.py token reset [--daily | --monthly | --all]")
        sys.exit(1)
        
    save_budget(budget)

def run(args: List[str]) -> None:
    if not args:
        print("Usage: helper.py token <log | status | reset> [args...]")
        sys.exit(1)

    subcommand = args[0].lower()
    if subcommand == "log":
        run_log(args[1:])
    elif subcommand == "status":
        run_status(args[1:])
    elif subcommand == "reset":
        run_reset(args[1:])
    else:
        print_err(f"Unknown token budget subcommand: '{subcommand}'. Supported subcommands: log, status, reset.")
        sys.exit(1)
