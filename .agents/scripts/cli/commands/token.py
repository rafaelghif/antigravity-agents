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

def get_active_api_account() -> str:
    """
    Detect the active API account or logged-in account name.
    1. Check env vars: ACTIVE_API_PROFILE, API_ACCOUNT, GEMINI_API_PROFILE.
    2. Check local file: .agents/active_api_profile_name.
    3. Check env vars for actual keys: GEMINI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY.
       If found, mask and use as account name (e.g. 'gemini:AIza...8b9c').
    4. Scan global Antigravity CLI logs in ~/.gemini/antigravity-cli/log/ for active email.
    5. Fallback to 'default'.
    """
    # 1. Check environment variables
    for var in ("ACTIVE_API_PROFILE", "API_ACCOUNT", "GEMINI_API_PROFILE"):
        val = os.environ.get(var)
        if val:
            return val.strip()

    # 2. Check local active profile file
    profile_file = ".agents/active_api_profile_name"
    if os.path.exists(profile_file):
        try:
            with open(profile_file, 'r', encoding='utf-8') as f:
                val = f.read().strip()
                if val:
                    return val
        except Exception:
            pass

    # 3. Check environment variables for API keys
    import hashlib
    for key_var, prefix in (
        ("GEMINI_API_KEY", "gemini"),
        ("OPENAI_API_KEY", "openai"),
        ("ANTHROPIC_API_KEY", "anthropic")
    ):
        key_val = os.environ.get(key_var)
        if key_val:
            key_val = key_val.strip()
            # Compute a cryptographically secure hash of the key
            key_hash = hashlib.sha256(key_val.encode('utf-8')).hexdigest()
            # Expose only the provider and a short 8-char slice of the hash
            return f"{prefix}:sha256-{key_hash[:8]}"

    # 4. Scan global Antigravity CLI log files
    try:
        log_dir = os.path.expanduser("~/.gemini/antigravity-cli/log")
        if os.path.exists(log_dir):
            log_files = [
                os.path.join(log_dir, f)
                for f in os.listdir(log_dir)
                if f.startswith("cli-") and f.endswith(".log")
            ]
            if log_files:
                # Sort by modification time (newest first)
                log_files.sort(key=os.path.getmtime, reverse=True)
                # Matches "OAuth: authenticated successfully as <email>" or "applyAuthResult: email=<email>"
                email_pattern = re.compile(
                    r"(?:OAuth: authenticated successfully as |applyAuthResult: email=)([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
                )
                for log_file in log_files[:5]:
                    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                        for line in reversed(lines):
                            m = email_pattern.search(line)
                            if m:
                                return m.group(1).strip()
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

def auto_detect_tokens() -> tuple:
    """
    Attempt to auto-detect prompt and completion tokens from the conversation transcript.
    Returns: (prompt_tokens, completion_tokens)
    """
    conversation_id = os.environ.get("ANTIGRAVITY_CONVERSATION_ID")
    if not conversation_id:
        brain_dir = os.path.expanduser("~/.gemini/antigravity-cli/brain")
        if os.path.exists(brain_dir):
            try:
                dirs = [d for d in os.listdir(brain_dir) if os.path.isdir(os.path.join(brain_dir, d)) and not d.startswith(".")]
                if dirs:
                    dirs.sort(key=lambda x: os.path.getmtime(os.path.join(brain_dir, x)), reverse=True)
                    conversation_id = dirs[0]
            except Exception:
                pass
                
    if not conversation_id:
        return 0, 0

    transcript_path = os.path.expanduser(f"~/.gemini/antigravity-cli/brain/{conversation_id}/.system_generated/logs/transcript.jsonl")
    if not os.path.exists(transcript_path):
        return 0, 0

    try:
        with open(transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        steps = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                steps.append(json.loads(line))
            except Exception:
                pass

        if not steps:
            return 0, 0

        # Find the last MODEL response step and preceding steps in the current turn
        last_model_idx = -1
        for idx in range(len(steps) - 1, -1, -1):
            if steps[idx].get("source") == "MODEL":
                last_model_idx = idx
                break

        if last_model_idx == -1:
            return 0, 0

        model_step = steps[last_model_idx]
        completion_content = model_step.get("content", "") or ""
        tool_calls = model_step.get("tool_calls", [])
        if tool_calls:
            completion_content += json.dumps(tool_calls)

        completion_tokens = max(1, int(len(completion_content) / 3.8))

        start_turn_idx = 0
        for idx in range(last_model_idx - 1, -1, -1):
            if steps[idx].get("source") == "MODEL":
                start_turn_idx = idx + 1
                break

        prompt_content = ""
        for idx in range(start_turn_idx, last_model_idx):
            step = steps[idx]
            prompt_content += (step.get("content", "") or "")
            if "tool_calls" in step:
                prompt_content += json.dumps(step.get("tool_calls", []))

        prompt_tokens = max(1, int(len(prompt_content) / 3.8))
        if prompt_tokens < 100:
            prompt_tokens = 15000  # standard system + rules baseline fallback

        return prompt_tokens, completion_tokens
    except Exception:
        return 0, 0

def run_log(args: List[str]) -> None:
    task_id = None
    if "--task" in args:
        try:
            idx = args.index("--task")
            if idx + 1 < len(args):
                task_id = args[idx + 1]
                # Remove --task and its value from args to simplify parsing
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

    budget = load_budget()
    budget = check_date_resets(budget)

    total = prompt + completion

    # Update daily and monthly
    budget["daily_used"] += total
    budget["monthly_used"] += total

    # Update per-account
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

def get_reset_intervals_remaining() -> dict:
    """
    Calculate the time remaining (hours and minutes) until the next resets.
    - 5-Hour Reset (intervals: 00:00, 05:00, 10:00, 15:00, 20:00 UTC)
    - Daily Reset (midnight UTC)
    - Weekly Reset (Sunday midnight UTC)
    - Monthly Reset (1st of next month midnight UTC)
    """
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    
    # 1. 5-Hour Reset remaining
    current_hour = now.hour
    next_hour = ((current_hour // 5) + 1) * 5
    if next_hour >= 24:
        next_dt = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        next_dt = now.replace(hour=next_hour, minute=0, second=0, microsecond=0)
    five_hour_remaining = next_dt - now
    
    # 2. Daily Reset remaining
    next_day_dt = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    daily_remaining = next_day_dt - now
    
    # 3. Weekly Reset remaining (until Sunday midnight UTC)
    days_to_sunday = 6 - now.weekday()
    next_sunday_dt = (now + timedelta(days=days_to_sunday if days_to_sunday > 0 else 7)).replace(hour=0, minute=0, second=0, microsecond=0)
    if now.weekday() == 6:
        next_sunday_dt = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    weekly_remaining = next_sunday_dt - now
    
    # 4. Monthly Reset remaining
    if now.month == 12:
        next_month_dt = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        next_month_dt = datetime(now.year, now.month + 1, 1, tzinfo=timezone.utc)
    monthly_remaining = next_month_dt - now
    
    def format_td(td: timedelta) -> str:
        total_seconds = int(td.total_seconds())
        days = td.days
        hours = (total_seconds // 3600) % 24
        minutes = (total_seconds % 3600) // 60
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        return f"{hours}h {minutes}m"
        
    return {
        "five_hour": format_td(five_hour_remaining),
        "daily": format_td(daily_remaining),
        "weekly": format_td(weekly_remaining),
        "monthly": format_td(monthly_remaining)
    }

def get_rolling_window_stats() -> dict:
    """
    Calculate rolling window token usage and remaining reset times from log.
    - 5-Hour rolling window
    - 7-Day (weekly) rolling window
    """
    from datetime import datetime, timedelta, timezone
    import re
    now = datetime.now(timezone.utc)
    
    five_hour_limit = 200000
    weekly_limit = 2500000
    
    budget = load_budget()
    five_hour_limit = budget.get("five_hour_limit", 200000)
    weekly_limit = budget.get("weekly_limit", 2500000)
    
    five_hour_used = 0
    weekly_used = 0
    
    five_hour_oldest = None
    weekly_oldest = None
    
    log_path = ".agents/logs/token_usage.log"
    if os.path.exists(log_path):
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                m = re.match(r'\[(.*?)\] Task:.*?\|.*\|.*\| Total:\s*(\d+)', line)
                if m:
                    ts_str = m.group(1)
                    ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S UTC").replace(tzinfo=timezone.utc)
                    total = int(m.group(2))
                    
                    if now - ts <= timedelta(hours=5):
                        five_hour_used += total
                        if not five_hour_oldest or ts < five_hour_oldest:
                            five_hour_oldest = ts
                            
                    if now - ts <= timedelta(days=7):
                        weekly_used += total
                        if not weekly_oldest or ts < weekly_oldest:
                            weekly_oldest = ts
        except Exception:
            pass
            
    if five_hour_oldest:
        five_hour_rem = (five_hour_oldest + timedelta(hours=5)) - now
        if five_hour_rem.total_seconds() < 0:
            five_hour_rem_str = "0h 0m"
        else:
            total_secs = int(five_hour_rem.total_seconds())
            five_hour_rem_str = f"{total_secs // 3600}h {(total_secs % 3600) // 60}m"
    else:
        five_hour_rem_str = "0h 0m"
        
    if weekly_oldest:
        weekly_rem = (weekly_oldest + timedelta(days=7)) - now
        if weekly_rem.total_seconds() < 0:
            weekly_rem_str = "0h 0m"
        else:
            total_secs = int(weekly_rem.total_seconds())
            days = weekly_rem.days
            hours = (total_secs // 3600) % 24
            mins = (total_secs % 3600) // 60
            if days > 0:
                weekly_rem_str = f"{days}d {hours}h {mins}m"
            else:
                weekly_rem_str = f"{hours}h {mins}m"
    else:
        weekly_rem_str = "0h 0m"
        
    return {
        "five_hour_used": five_hour_used,
        "five_hour_limit": five_hour_limit,
        "five_hour_pct": (five_hour_used / five_hour_limit * 100) if five_hour_limit > 0 else 0,
        "five_hour_remaining": five_hour_rem_str,
        "weekly_used": weekly_used,
        "weekly_limit": weekly_limit,
        "weekly_pct": (weekly_used / weekly_limit * 100) if weekly_limit > 0 else 0,
        "weekly_remaining": weekly_rem_str
    }

def get_rolling_stats() -> dict:
    stats = get_rolling_window_stats()
    resets = get_reset_intervals_remaining()
    stats["daily_remaining"] = resets["daily"]
    stats["monthly_remaining"] = resets["monthly"]
    
    budget = load_budget()
    if budget.get("weekly_pct_override") is not None:
        stats["weekly_pct"] = budget["weekly_pct_override"]
        stats["weekly_used"] = int(stats["weekly_pct"] / 100 * stats["weekly_limit"])
    if budget.get("weekly_remaining_override") is not None:
        stats["weekly_remaining"] = budget["weekly_remaining_override"]
        
    if budget.get("five_hour_pct_override") is not None:
        stats["five_hour_pct"] = budget["five_hour_pct_override"]
        stats["five_hour_used"] = int(stats["five_hour_pct"] / 100 * stats["five_hour_limit"])
    if budget.get("five_hour_remaining_override") is not None:
        stats["five_hour_remaining"] = budget["five_hour_remaining_override"]
        
    return stats

def run_sync(args: List[str]) -> None:
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
    
    r_stats = get_rolling_stats()
    print("-"*60)
    print("Rolling Quotas & Resets:")
    print(f"  - 5-Hour Rolling Limit : {r_stats['five_hour_limit']:,} tokens")
    print(f"  - 5-Hour Rolling Used  : {r_stats['five_hour_used']:,} tokens ({r_stats['five_hour_pct']:.2f}% utilized)")
    print(f"  - 5-Hour Reset In      : {r_stats['five_hour_remaining']}")
    print(f"  - Weekly Rolling Limit : {r_stats['weekly_limit']:,} tokens")
    print(f"  - Weekly Rolling Used  : {r_stats['weekly_used']:,} tokens ({r_stats['weekly_pct']:.2f}% utilized)")
    print(f"  - Weekly Reset In      : {r_stats['weekly_remaining']}")
    
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
        print("Usage: helper.py token <log | status | sync | reset> [args...]")
        sys.exit(1)

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
