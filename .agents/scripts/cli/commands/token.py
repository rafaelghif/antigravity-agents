import sys
import os
import json
import re
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from typing import List

try:
    from . import validation
except ImportError:
    import validation

try:
    from .services import token_service
except ImportError:
    try:
        import services.token_service as token_service
    except ImportError:
        from cli.commands.services import token_service

BUDGET_FILE = token_service.BUDGET_FILE
LOG_FILE = token_service.LOG_FILE
GLOBAL_GEMINI_DIR = token_service.GLOBAL_GEMINI_DIR

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

def load_budget() -> dict:
    return token_service.load_budget()

def save_budget(budget: dict) -> None:
    token_service.save_budget(budget)

def check_date_resets(budget: dict) -> dict:
    return token_service.check_date_resets(budget)

def get_current_task_id() -> str:
    return token_service.get_current_task_id()

def append_to_log(task_id: str, prompt: int, completion: int) -> None:
    token_service.append_to_log(task_id, prompt, completion)

def auto_detect_tokens() -> tuple:
    return token_service.auto_detect_tokens()

def parse_usage_output(output: str, budget: dict = None) -> dict:
    return token_service.parse_usage_output(output, budget)

def scan_conversations_for_usage() -> str:
    return token_service.scan_conversations_for_usage()

def sync_from_platform_usage() -> dict:
    return token_service.sync_from_platform_usage()

def trigger_background_sync() -> None:
    token_service.trigger_background_sync()

def get_rolling_stats() -> dict:
    return token_service.get_rolling_stats()

def get_rolling_window_stats() -> dict:
    return token_service.get_rolling_window_stats()

def get_reset_intervals_remaining() -> dict:
    return token_service.get_reset_intervals_remaining()

def get_active_api_account() -> str:
    return token_service.get_active_api_account()

def run_log(args: List[str]) -> None:
    task_id = None
    if "--task" in args:
        try:
            idx = args.index("--task")
            if idx + 1 < len(args):
                task_id = args[idx + 1]
                args = args[:idx] + args[idx + 2:]
        except Exception:
            pass

    prompt = 0
    completion = 0

    if len(args) >= 2:
        try:
            prompt = int(args[0])
            completion = int(args[1])
            if prompt < 0 or completion < 0:
                raise ValueError()
        except ValueError:
            print_err("Prompt and completion tokens must be non-negative integers.")
            sys.exit(1)
    else:
        prompt, completion = auto_detect_tokens()
        if prompt == 0 and completion == 0:
            print_err("No tokens specified and could not auto-detect token usage from transcript.")
            sys.exit(1)

    if not task_id:
        task_id = get_current_task_id()

    if task_id and not validation.validate_safe_identifier(task_id):
        print_err(f"Error: Invalid task ID '{task_id}'.")
        sys.exit(1)

    budget = load_budget()
    budget = check_date_resets(budget)

    total = prompt + completion

    budget["daily_used"] += total
    budget["monthly_used"] += total

    account_name = get_active_api_account()
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
    
    if os.environ.get("INTERNAL_SYNC") != "true":
        trigger_background_sync()

    if budget["daily_used"] > budget["daily_limit"]:
        print_warn(f"Daily token budget limit exceeded! Used: {budget['daily_used']}/{budget['daily_limit']}")
    if budget["monthly_used"] > budget["monthly_limit"]:
        print_warn(f"Monthly token budget limit exceeded! Used: {budget['monthly_used']}/{budget['monthly_limit']}")

def run_sync(args: List[str]) -> None:
    if not args or "--auto" in args:
        print("Synchronizing actual platform token quotas from agy /usage...")
        parsed = sync_from_platform_usage()
        if parsed:
            print_ok("Successfully synchronized actual platform token quotas with local budget.")
        else:
            print_err("Failed to synchronize token quotas from agy.")
        return

    budget = load_budget()
    i = 0
    while i < len(args):
        arg = args[i].lower()
        if arg == "--weekly":
            if i + 1 < len(args):
                budget["weekly_pct_override"] = float(args[i+1])
                i += 1
        elif arg == "--weekly-rem":
            if i + 1 < len(args):
                budget["weekly_remaining_override"] = args[i+1]
                i += 1
        elif arg == "--five-hour":
            if i + 1 < len(args):
                budget["five_hour_pct_override"] = float(args[i+1])
                i += 1
        elif arg == "--five-hour-rem":
            if i + 1 < len(args):
                budget["five_hour_remaining_override"] = args[i+1]
                i += 1
        i += 1
    save_budget(budget)
    print_ok("Successfully synchronized actual platform token quotas with local budget.")

def run_status(args: List[str]) -> None:
    budget = load_budget()
    
    last_sync_str = budget.get("last_sync")
    should_sync = True
    if last_sync_str:
        try:
            if last_sync_str.endswith("Z"):
                last_sync_str = last_sync_str[:-1] + "+00:00"
            last_sync = datetime.fromisoformat(last_sync_str)
            age = (datetime.now(timezone.utc) - last_sync.replace(tzinfo=timezone.utc)).total_seconds()
            if age <= 120:
                should_sync = False
        except Exception:
            pass
            
    if should_sync:
        db_usage = scan_conversations_for_usage()
        if db_usage:
            parsed = parse_usage_output(db_usage)
            if parsed:
                if "daily_limit" in parsed: budget["daily_limit"] = parsed["daily_limit"]
                if "daily_used" in parsed: budget["daily_used"] = parsed["daily_used"]
                if "monthly_limit" in parsed: budget["monthly_limit"] = parsed["monthly_limit"]
                if "monthly_used" in parsed: budget["monthly_used"] = parsed["monthly_used"]
                if "weekly_pct" in parsed: budget["weekly_pct_override"] = parsed["weekly_pct"]
                if "weekly_remaining" in parsed: budget["weekly_remaining_override"] = parsed["weekly_remaining"]
                if "weekly_used" in parsed: budget["weekly_used_override"] = parsed["weekly_used"]
                if "five_hour_pct" in parsed: budget["five_hour_pct_override"] = parsed["five_hour_pct"]
                if "five_hour_remaining" in parsed: budget["five_hour_remaining_override"] = parsed["five_hour_remaining"]
                if "five_hour_used" in parsed: budget["five_hour_used_override"] = parsed["five_hour_used"]
                if "weekly_limit" in parsed: budget["weekly_limit"] = parsed["weekly_limit"]
                if "five_hour_limit" in parsed: budget["five_hour_limit"] = parsed["five_hour_limit"]
                budget["last_sync"] = datetime.utcnow().isoformat() + "Z"
                save_budget(budget)
        else:
            trigger_background_sync()

    budget = check_date_resets(budget)

    daily_used = budget.get("daily_used", 0)
    daily_limit = budget.get("daily_limit", 500000)
    daily_pct = (daily_used / daily_limit * 100) if daily_limit > 0 else 0
    daily_rem = max(0, daily_limit - daily_used)

    monthly_used = budget.get("monthly_used", 0)
    monthly_limit = budget.get("monthly_limit", 5000000)
    monthly_pct = (monthly_used / monthly_limit * 100) if monthly_limit > 0 else 0
    monthly_rem = max(0, monthly_limit - monthly_used)

    print("="*60)
    print("                Antigravity Token Budget Status")
    print("="*60)
    print(f"Daily Limit       : {daily_limit:,} tokens")
    print(f"Daily Used        : {daily_used:,} tokens ({daily_pct:.2f}% utilized)")
    print(f"Daily Remaining   : {daily_rem:,} tokens")
    print(f"Monthly Limit     : {monthly_limit:,} tokens")
    print(f"Monthly Used      : {monthly_used:,} tokens ({monthly_pct:.2f}% utilized)")
    print(f"Monthly Remaining : {monthly_rem:,} tokens")
    print(f"Last Reset        : {budget.get('last_reset', 'N/A')}")
    
    r_stats = get_rolling_stats()
    five_hour_limit = r_stats['five_hour_limit']
    five_hour_used = r_stats['five_hour_used']
    five_hour_rem = max(0, five_hour_limit - five_hour_used)
    
    weekly_limit = r_stats['weekly_limit']
    weekly_used = r_stats['weekly_used']
    weekly_rem = max(0, weekly_limit - weekly_used)

    print("-"*60)
    print("Rolling Quotas & Resets:")
    print(f"  - 5-Hour Rolling Limit     : {five_hour_limit:,} tokens")
    print(f"  - 5-Hour Rolling Used      : {five_hour_used:,} tokens ({r_stats['five_hour_pct']:.2f}% utilized)")
    print(f"  - 5-Hour Rolling Remaining : {five_hour_rem:,} tokens")
    print(f"  - 5-Hour Reset In          : {r_stats['five_hour_remaining']}")
    print(f"  - Weekly Rolling Limit     : {weekly_limit:,} tokens")
    print(f"  - Weekly Rolling Used      : {weekly_used:,} tokens ({r_stats['weekly_pct']:.2f}% utilized)")
    print(f"  - Weekly Rolling Remaining : {weekly_rem:,} tokens")
    print(f"  - Weekly Reset In          : {r_stats['weekly_remaining']}")
    
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
        run_status([])
        return

    subcommand = args[0].lower()
    if subcommand == "log":
        run_log(args[1:])
    elif subcommand == "status":
        run_status(args[1:])
    elif subcommand == "sync":
        run_sync(args[1:])
    elif subcommand == "reset":
        run_reset(args[1:])
    else:
        print_err(f"Unknown token budget subcommand: '{subcommand}'. Supported subcommands: log, status, sync, reset.")
        sys.exit(1)
