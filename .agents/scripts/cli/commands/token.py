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

    # 4. Check global google_accounts.json for active account
    try:
        acc_file = os.path.expanduser("~/.gemini/google_accounts.json")
        if os.path.exists(acc_file):
            with open(acc_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                active = data.get("active")
                if active:
                    return active.strip()
    except Exception:
        pass

    # 5. Scan global Antigravity CLI log files
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

def recalculate_used_from_log(budget: dict) -> dict:
    """Recalculate daily_used and monthly_used from token_usage.log dynamically."""
    from datetime import datetime, timezone
    import re
    
    now = datetime.now(timezone.utc)
    today_utc = now.date()
    this_month_utc = (now.year, now.month)
    
    daily_sum = 0
    monthly_sum = 0
    
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
                    
                    if ts.date() == today_utc:
                        daily_sum += total
                    if ts.year == this_month_utc[0] and ts.month == this_month_utc[1]:
                        monthly_sum += total
        except Exception:
            pass
            
    budget["daily_used"] = daily_sum
    budget["monthly_used"] = monthly_sum
    return budget

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
        return recalculate_used_from_log(default_budget)
    try:
        with open(BUDGET_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Guarantee structure
            for key in default_budget:
                if key not in data:
                    data[key] = default_budget[key]
            if "accounts" not in data:
                data["accounts"] = {}
                
            # Self-heal corrupted daily/monthly limits
            if data.get("daily_limit", 0) < 500000:
                data["daily_limit"] = 500000
            if data.get("monthly_limit", 0) < 5000000:
                data["monthly_limit"] = 5000000
                
            return recalculate_used_from_log(data)
    except Exception:
        return recalculate_used_from_log(default_budget)

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

def get_transcript_tokens_fallback() -> tuple:
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
        return 15000, 1000

    transcript_path = os.path.expanduser(f"~/.gemini/antigravity-cli/brain/{conversation_id}/.system_generated/logs/transcript.jsonl")
    if not os.path.exists(transcript_path):
        return 15000, 1000

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
            return 15000, 1000

        # Find the last MODEL response step and preceding steps in the current turn
        last_model_idx = -1
        for idx in range(len(steps) - 1, -1, -1):
            if steps[idx].get("source") == "MODEL":
                last_model_idx = idx
                break

        if last_model_idx == -1:
            return 15000, 1000

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
        return 15000, 1000

def auto_detect_tokens() -> tuple:
    """
    Attempt to auto-detect prompt and completion tokens using agy -p "/usage" and local budget differences.
    Falls back to transcript-based estimation if needed.
    """
    # 1. Prevent recursion and check if running under unit tests
    if os.environ.get("INTERNAL_SYNC") == "true":
        return get_transcript_tokens_fallback()

    is_testing = "unittest" in sys.modules or "pytest" in sys.modules
    if is_testing and os.environ.get("FORCE_PLATFORM_DETECT") != "true":
        return get_transcript_tokens_fallback()

    # 2. Run agy -p "/usage" to get actual platform token usage
    env = os.environ.copy()
    env["INTERNAL_SYNC"] = "true"
    try:
        res = subprocess.run(
            ["agy", "-p", "/usage"],
            capture_output=True,
            text=True,
            timeout=40,
            env=env
        )
        if res.returncode == 0:
            parsed = parse_usage_output(res.stdout)
            if parsed:
                # Find current task ID
                task_id = get_current_task_id()
                
                # Fetch platform task usage
                platform_tasks = parsed.get("tasks", {})
                platform_task_info = platform_tasks.get(task_id)
                
                # If not found for current task, maybe under 'unknown'
                if not platform_task_info and "unknown" in platform_tasks:
                    platform_task_info = platform_tasks["unknown"]
                
                if platform_task_info:
                    platform_prompt = platform_task_info.get("prompt_tokens", 0)
                    platform_completion = platform_task_info.get("completion_tokens", 0)
                    
                    # Compare with local logged task usage
                    budget = load_budget()
                    local_tasks = budget.get("tasks", {})
                    local_task_info = local_tasks.get(task_id, {})
                    
                    local_prompt = local_task_info.get("prompt_tokens", 0)
                    local_completion = local_task_info.get("completion_tokens", 0)
                    
                    prompt_diff = platform_prompt - local_prompt
                    completion_diff = platform_completion - local_completion
                    
                    if prompt_diff > 0 or completion_diff > 0:
                        return max(0, prompt_diff), max(0, completion_diff)
                
                # Alternate detection: check difference in daily_used
                platform_daily = parsed.get("daily_used", 0)
                budget = load_budget()
                local_daily = budget.get("daily_used", 0)
                
                daily_diff = platform_daily - local_daily
                if daily_diff > 0:
                    # Estimate prompt/completion split (90% / 10%)
                    prompt_est = int(daily_diff * 0.9)
                    comp_est = int(daily_diff * 0.1)
                    return max(1, prompt_est), max(1, comp_est)
    except Exception:
        pass

    # 3. Fallback to transcript estimation
    return get_transcript_tokens_fallback()

def normalize_time_string(raw_time: str) -> str:
    """Normalize human readable time strings to Xd Yh Zm format."""
    raw_time = raw_time.replace(',', '').lower()
    raw_time = re.sub(r'\bdays?\b', 'd', raw_time)
    raw_time = re.sub(r'\bhours?\b', 'h', raw_time)
    raw_time = re.sub(r'\bminutes?\b', 'm', raw_time)
    raw_time = re.sub(r'(\d+)\s*([dhm])', r'\1\2', raw_time)
    raw_time = re.sub(r'\s+', ' ', raw_time).strip()
    return raw_time

def parse_usage_output(output: str, budget: dict = None) -> dict:
    """Parse output of agy -p '/usage' to extract limits and remaining reset times."""
    stats = {}
    lines = output.split('\n')

    # 0. Check for new block-percentage format
    has_blocks = any("██" in line or "░░" in line for line in lines)
    if has_blocks:
        # Detect active account
        for line in lines:
            m_acc = re.search(r'Account\s*:\s*([a-zA-Z0-9_.@+-:]+)', line, re.IGNORECASE)
            if m_acc:
                stats["active_account"] = m_acc.group(1).strip()

        current_group = None
        for i, line in enumerate(lines):
            line_strip = line.strip()
            if "GEMINI MODELS" in line_strip:
                current_group = "gemini"
            elif "CLAUDE AND GPT MODELS" in line_strip:
                current_group = "claude"
                
            if current_group == "gemini":
                if "Weekly Limit" in line_strip:
                    for offset in (1, 2, 3):
                        if i + offset < len(lines):
                            next_line = lines[i + offset].strip()
                            m_pct = re.search(r'(\d+(?:\.\d+)?)%', next_line)
                            if m_pct and "weekly_remaining_pct" not in stats:
                                stats["weekly_remaining_pct"] = float(m_pct.group(1))
                                stats["weekly_pct"] = 100.0 - stats["weekly_remaining_pct"]
                            m_ref = re.search(r'Refreshes in\s*(.+)', next_line, re.IGNORECASE)
                            if m_ref and "weekly_remaining" not in stats:
                                stats["weekly_remaining"] = normalize_time_string(m_ref.group(1))
                elif "Five Hour Limit" in line_strip or "5-Hour Limit" in line_strip:
                    for offset in (1, 2, 3):
                        if i + offset < len(lines):
                            next_line = lines[i + offset].strip()
                            m_pct = re.search(r'(\d+(?:\.\d+)?)%', next_line)
                            if m_pct and "five_hour_remaining_pct" not in stats:
                                stats["five_hour_remaining_pct"] = float(m_pct.group(1))
                                stats["five_hour_pct"] = 100.0 - stats["five_hour_remaining_pct"]
                            m_ref = re.search(r'Refreshes in\s*(.+)', next_line, re.IGNORECASE)
                            if m_ref and "five_hour_remaining" not in stats:
                                stats["five_hour_remaining"] = normalize_time_string(m_ref.group(1))
                                
        if budget is None:
            budget = load_budget()
        if "weekly_pct" in stats:
            stats["weekly_limit"] = budget.get("weekly_limit", 2500000)
            stats["weekly_used"] = int(stats["weekly_pct"] / 100.0 * stats["weekly_limit"])
        if "five_hour_pct" in stats:
            stats["five_hour_limit"] = budget.get("five_hour_limit", 200000)
            stats["five_hour_used"] = int(stats["five_hour_pct"] / 100.0 * stats["five_hour_limit"])
            
        if "active_account" in stats and "weekly_used" in stats:
            stats["accounts"] = {
                stats["active_account"]: {
                    "daily_used": stats.get("five_hour_used", 0),
                    "monthly_used": stats.get("weekly_used", 0),
                    "total_used": stats.get("weekly_used", 0)
                }
            }
        return stats

    # 1. First attempt: parse using direct colon format (Console Text output)
    for line in lines:
        line_strip = line.strip()
        if not line_strip:
            continue
            
        m_daily_limit = re.search(r'Daily\s+Limit\s*:\s*([\d,]+)', line_strip, re.IGNORECASE)
        if m_daily_limit:
            stats["daily_limit"] = int(m_daily_limit.group(1).replace(',', ''))
        m_daily_used = re.search(r'Daily\s+Used\s*:\s*([\d,]+)', line_strip, re.IGNORECASE)
        if m_daily_used:
            stats["daily_used"] = int(m_daily_used.group(1).replace(',', ''))
            
        m_monthly_limit = re.search(r'Monthly\s+Limit\s*:\s*([\d,]+)', line_strip, re.IGNORECASE)
        if m_monthly_limit:
            stats["monthly_limit"] = int(m_monthly_limit.group(1).replace(',', ''))
        m_monthly_used = re.search(r'Monthly\s+Used\s*:\s*([\d,]+)', line_strip, re.IGNORECASE)
        if m_monthly_used:
            stats["monthly_used"] = int(m_monthly_used.group(1).replace(',', ''))

        m_5h_limit = re.search(r'5-Hour\s+(?:Rolling\s+)?Limit\s*:\s*([\d,]+)', line_strip, re.IGNORECASE)
        if m_5h_limit:
            stats["five_hour_limit"] = int(m_5h_limit.group(1).replace(',', ''))
        m_5h_used = re.search(r'5-Hour\s+(?:Rolling\s+)?Used\s*:\s*([\d,]+)', line_strip, re.IGNORECASE)
        if m_5h_used:
            stats["five_hour_used"] = int(m_5h_used.group(1).replace(',', ''))
        m_5h_reset = re.search(r'5-Hour\s+Reset\s+In\s*:\s*(.+)', line_strip, re.IGNORECASE)
        if m_5h_reset:
            stats["five_hour_remaining"] = normalize_time_string(m_5h_reset.group(1))

        m_weekly_limit = re.search(r'Weekly\s+(?:Rolling\s+)?Limit\s*:\s*([\d,]+)', line_strip, re.IGNORECASE)
        if m_weekly_limit:
            stats["weekly_limit"] = int(m_weekly_limit.group(1).replace(',', ''))
        m_weekly_used = re.search(r'Weekly\s+(?:Rolling\s+)?Used\s*:\s*([\d,]+)', line_strip, re.IGNORECASE)
        if m_weekly_used:
            stats["weekly_used"] = int(m_weekly_used.group(1).replace(',', ''))
        m_weekly_reset = re.search(r'Weekly\s+Reset\s+In\s*:\s*(.+)', line_strip, re.IGNORECASE)
        if m_weekly_reset:
            stats["weekly_remaining"] = normalize_time_string(m_weekly_reset.group(1))

    # 2. Fall back to list/table matching if daily_limit or monthly_limit was not found
    if "daily_limit" not in stats or "monthly_limit" not in stats:
        for line in lines:
            if "Daily" in line and "Limit" not in line and "Used" not in line:
                clean_line = re.sub(r'Daily\s*(?:Quota)?', '', line, flags=re.IGNORECASE)
                nums = [int(s.replace(',', '')) for s in re.findall(r'\b\d{1,3}(?:,\d{3})+\b|\b\d+\b', clean_line)]
                if len(nums) >= 2:
                    if "Quota" in line or "/" in line: # Bullet list
                        stats["daily_used"] = nums[0]
                        stats["daily_limit"] = nums[1]
                    else: # Table
                        stats["daily_limit"] = nums[0]
                        stats["daily_used"] = nums[1]
                        
            if "Monthly" in line and "Limit" not in line and "Used" not in line:
                clean_line = re.sub(r'Monthly\s*(?:Quota)?', '', line, flags=re.IGNORECASE)
                nums = [int(s.replace(',', '')) for s in re.findall(r'\b\d{1,3}(?:,\d{3})+\b|\b\d+\b', clean_line)]
                if len(nums) >= 2:
                    if "Quota" in line or "/" in line:
                        stats["monthly_used"] = nums[0]
                        stats["monthly_limit"] = nums[1]
                    else:
                        stats["monthly_limit"] = nums[0]
                        stats["monthly_used"] = nums[1]

        # Parse 5-Hour rolling in list/table fallback
        if "five_hour_limit" not in stats:
            five_hour_block_lines = []
            for i, line in enumerate(lines):
                if "5-Hour" in line:
                    five_hour_block_lines.append(line)
                    for offset in (1, 2):
                        if i + offset < len(lines):
                            next_line = lines[i + offset]
                            if any(k in next_line for k in ("Weekly", "Daily", "Monthly", "Account Breakdown", "Task Breakdown", "---", "===")):
                                break
                            five_hour_block_lines.append(next_line)
                    break
            
            if five_hour_block_lines:
                five_hour_text = "\n".join(five_hour_block_lines)
                
                # Check for slash format: used / limit (e.g. 142,000 / 200,000)
                m_slash = re.search(r'([\d,`\s]+)\s*/\s*([\d,`\s]+)', five_hour_text)
                if m_slash:
                    stats["five_hour_used"] = int(m_slash.group(1).replace('`','').replace(',','').strip())
                    stats["five_hour_limit"] = int(m_slash.group(2).replace('`','').replace(',','').strip())
                else:
                    # Look for Limit and Used separately using keywords
                    m_limit = re.search(r'Limit\b[^\d]*([\d,]+)', five_hour_text, re.IGNORECASE)
                    m_used = re.search(r'Used\b[^\d]*([\d,]+)', five_hour_text, re.IGNORECASE)
                    if m_limit:
                        stats["five_hour_limit"] = int(m_limit.group(1).replace(',', ''))
                    if m_used:
                        stats["five_hour_used"] = int(m_used.group(1).replace(',', ''))
                        
                pct_match = re.search(r'(\d+(?:\.\d+)?)%', five_hour_text)
                if pct_match:
                    stats["five_hour_pct"] = float(pct_match.group(1))
                    
                rem_match = re.search(r'(?:Resets?\s+in|Reset\s+In|Refreshes?\s+in)[^\d]*([a-zA-Z0-9\s,]+)', five_hour_text, re.IGNORECASE)
                if rem_match:
                    stats["five_hour_remaining"] = normalize_time_string(rem_match.group(1).strip())

        # Parse Weekly rolling in list/table fallback
        if "weekly_limit" not in stats:
            weekly_block_lines = []
            for i, line in enumerate(lines):
                if "Weekly" in line:
                    weekly_block_lines.append(line)
                    for offset in (1, 2):
                        if i + offset < len(lines):
                            next_line = lines[i + offset]
                            if any(k in next_line for k in ("5-Hour", "Daily", "Monthly", "Account Breakdown", "Task Breakdown", "---", "===")):
                                break
                            weekly_block_lines.append(next_line)
                    break
            
            if weekly_block_lines:
                weekly_text = "\n".join(weekly_block_lines)
                
                # Check for slash format: used / limit
                m_slash = re.search(r'([\d,`\s]+)\s*/\s*([\d,`\s]+)', weekly_text)
                if m_slash:
                    stats["weekly_used"] = int(m_slash.group(1).replace('`','').replace(',','').strip())
                    stats["weekly_limit"] = int(m_slash.group(2).replace('`','').replace(',','').strip())
                else:
                    # Look for Limit and Used separately using keywords
                    m_limit = re.search(r'Limit\b[^\d]*([\d,]+)', weekly_text, re.IGNORECASE)
                    m_used = re.search(r'Used\b[^\d]*([\d,]+)', weekly_text, re.IGNORECASE)
                    if m_limit:
                        stats["weekly_limit"] = int(m_limit.group(1).replace(',', ''))
                    if m_used:
                        stats["weekly_used"] = int(m_used.group(1).replace(',', ''))
                        
                pct_match = re.search(r'(\d+(?:\.\d+)?)%', weekly_text)
                if pct_match:
                    stats["weekly_pct"] = float(pct_match.group(1))
                    
                rem_match = re.search(r'(?:Resets?\s+in|Reset\s+In|Refreshes?\s+in)[^\d]*([a-zA-Z0-9\s,]+)', weekly_text, re.IGNORECASE)
                if rem_match:
                    stats["weekly_remaining"] = normalize_time_string(rem_match.group(1).strip())

    # Compute percentage overrides if limit and used are present
    if "five_hour_limit" in stats and "five_hour_used" in stats and "five_hour_pct" not in stats:
        stats["five_hour_pct"] = (stats["five_hour_used"] / stats["five_hour_limit"] * 100) if stats["five_hour_limit"] > 0 else 0
    if "weekly_limit" in stats and "weekly_used" in stats and "weekly_pct" not in stats:
        stats["weekly_pct"] = (stats["weekly_used"] / stats["weekly_limit"] * 100) if stats["weekly_limit"] > 0 else 0

    # Parse Account Breakdown
    accounts = {}
    in_account_breakdown = False
    for line in lines:
        line_lower = line.lower()
        if "account breakdown:" in line_lower:
            in_account_breakdown = True
            continue
        if in_account_breakdown:
            if line.startswith("---") or line.startswith("===") or "task breakdown:" in line_lower:
                in_account_breakdown = False
            else:
                m = re.match(r'\s*-\s*([a-zA-Z0-9_.@+-:]+)\s*:\s*daily\s*([\d,]+)\s*\|\s*monthly\s*([\d,]+)\s*\|\s*total\s*([\d,]+)', line)
                if m:
                    acc_name = m.group(1).strip()
                    daily = int(m.group(2).replace(',', ''))
                    monthly = int(m.group(3).replace(',', ''))
                    total = int(m.group(4).replace(',', ''))
                    accounts[acc_name] = {
                        "daily_used": daily,
                        "monthly_used": monthly,
                        "total_used": total
                    }
                else:
                    # Try table format: | Account | Daily | Monthly | Total |
                    m_table = re.match(r'\s*\|\s*(?:\*\*)?([a-zA-Z0-9_.@+-:]+)(?:\*\*)?\s*\|\s*([\d,]+)[^|]*\|\s*([\d,]+)[^|]*\|\s*([\d,]+)[^|]*\|', line)
                    if m_table:
                        acc_name = m_table.group(1).strip()
                        if acc_name.lower() not in ("account", "metric", "limit", "task"):
                            daily = int(m_table.group(2).replace(',', ''))
                            monthly = int(m_table.group(3).replace(',', ''))
                            total = int(m_table.group(4).replace(',', ''))
                            accounts[acc_name] = {
                                "daily_used": daily,
                                "monthly_used": monthly,
                                "total_used": total
                            }
    if accounts:
        stats["accounts"] = accounts

    # Parse Task Breakdown
    tasks = {}
    in_task_breakdown = False
    for line in lines:
        line_lower = line.lower()
        if "task breakdown:" in line_lower:
            in_task_breakdown = True
            continue
        if in_task_breakdown:
            if line.startswith("---") or line.startswith("===") or "account breakdown:" in line_lower:
                in_task_breakdown = False
            else:
                m = re.match(r'\s*-\s*([a-zA-Z0-9_-]+)\s*:\s*([\d,]+)\s*total\s*\(([\d,]+)\s*prompt\s*/\s*([\d,]+)\s*completion\)', line)
                if m:
                    task_id = m.group(1).strip()
                    total = int(m.group(2).replace(',', ''))
                    prompt = int(m.group(3).replace(',', ''))
                    completion = int(m.group(4).replace(',', ''))
                    tasks[task_id] = {
                        "prompt_tokens": prompt,
                        "completion_tokens": completion,
                        "total_tokens": total,
                        "updated_at": datetime.utcnow().isoformat() + "Z"
                    }
                else:
                    # Try table format: | Task | Total | Prompt | Completion |
                    m_table = re.match(r'\s*\|\s*(?:\*\*)?([a-zA-Z0-9_-]+)(?:\*\*)?\s*\|\s*([\d,]+)[^|]*\|\s*([\d,]+)[^|]*\|\s*([\d,]+)[^|]*\|', line)
                    if m_table:
                        task_id = m_table.group(1).strip()
                        if task_id.lower() not in ("task", "metric", "limit"):
                            total = int(m_table.group(2).replace(',', ''))
                            prompt = int(m_table.group(3).replace(',', ''))
                            completion = int(m_table.group(4).replace(',', ''))
                            tasks[task_id] = {
                                "prompt_tokens": prompt,
                                "completion_tokens": completion,
                                "total_tokens": total,
                                "updated_at": datetime.utcnow().isoformat() + "Z"
                            }
    if tasks:
        stats["tasks"] = tasks

    return stats

def scan_conversations_for_usage() -> str:
    """
    Scan global Antigravity conversation databases for the most recent /usage slash command output.
    Returns the raw string output if found, or None.
    """
    import os
    import sqlite3
    
    db_dir = os.path.expanduser("~/.gemini/antigravity-cli/conversations")
    if not os.path.exists(db_dir):
        return None
        
    try:
        db_files = [
            os.path.join(db_dir, f)
            for f in os.listdir(db_dir)
            if f.endswith(".db")
        ]
        if not db_files:
            return None
            
        # Sort by modification time (newest first)
        db_files.sort(key=os.path.getmtime, reverse=True)
        
        # Scan the 10 most recently modified databases
        for db_path in db_files[:10]:
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                # Check if steps table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='steps'")
                if not cursor.fetchone():
                    conn.close()
                    continue
                    
                # Query steps payload newest first
                cursor.execute("SELECT step_payload FROM steps ORDER BY idx DESC")
                for (payload,) in cursor.fetchall():
                    if not payload:
                        continue
                    try:
                        text = payload.decode('utf-8', errors='ignore')
                        # Check for distinctive markers of the platform /usage output
                        if "Weekly Limit" in text and "GEMINI MODELS" in text:
                            conn.close()
                            return text
                    except Exception:
                        pass
                conn.close()
            except Exception:
                pass
    except Exception:
        pass
    return None

def sync_from_platform_usage() -> dict:
    """Sync token_budget.json by scanning conversation databases or running agy -p '/usage' as fallback."""
    import subprocess
    import os
    
    # 1. Try scanning conversation DBs first for the real platform usage output
    db_usage = scan_conversations_for_usage()
    parsed = None
    if db_usage:
        parsed = parse_usage_output(db_usage)
        if parsed:
            parsed["synced_from_db"] = True
            
    # 2. If not found in DBs, run agy -p '/usage' as a fallback
    if not parsed:
        env = os.environ.copy()
        env["INTERNAL_SYNC"] = "true"
        try:
            res = subprocess.run(
                ["agy", "-p", "/usage"],
                capture_output=True,
                text=True,
                timeout=40,
                env=env
            )
            if res.returncode == 0:
                parsed = parse_usage_output(res.stdout)
        except Exception:
            pass
            
    if parsed:
        budget = load_budget()
        # Update core limits and used
        if "daily_limit" in parsed: budget["daily_limit"] = parsed["daily_limit"]
        if "daily_used" in parsed: budget["daily_used"] = parsed["daily_used"]
        if "monthly_limit" in parsed: budget["monthly_limit"] = parsed["monthly_limit"]
        if "monthly_used" in parsed: budget["monthly_used"] = parsed["monthly_used"]
        
        # Rolling window overrides
        if "weekly_pct" in parsed: budget["weekly_pct_override"] = parsed["weekly_pct"]
        if "weekly_remaining" in parsed: budget["weekly_remaining_override"] = parsed["weekly_remaining"]
        if "five_hour_pct" in parsed: budget["five_hour_pct_override"] = parsed["five_hour_pct"]
        if "five_hour_remaining" in parsed: budget["five_hour_remaining_override"] = parsed["five_hour_remaining"]

        # Dynamically calculate and learn limits from local logs and platform percentages
        log_stats = get_rolling_window_stats()
        local_weekly = log_stats.get("weekly_used", 0)
        local_five_hour = log_stats.get("five_hour_used", 0)
        
        if "weekly_pct" in parsed and parsed["weekly_pct"] > 0:
            calculated_weekly_limit = int(local_weekly / (parsed["weekly_pct"] / 100.0))
            if calculated_weekly_limit > 0:
                budget["weekly_limit"] = calculated_weekly_limit
                
        if "five_hour_pct" in parsed and parsed["five_hour_pct"] > 0:
            calculated_five_hour_limit = int(local_five_hour / (parsed["five_hour_pct"] / 100.0))
            if calculated_five_hour_limit > 0:
                budget["five_hour_limit"] = calculated_five_hour_limit
        
        # Update accounts and tasks breakdowns
        if "accounts" in parsed:
            if "accounts" not in budget:
                budget["accounts"] = {}
            for acc, acc_info in parsed["accounts"].items():
                budget["accounts"][acc] = acc_info
        if "tasks" in parsed:
            if "tasks" not in budget:
                budget["tasks"] = {}
            for t_id, t_info in parsed["tasks"].items():
                budget["tasks"][t_id] = t_info
        
        save_budget(budget)
        return parsed
        
    return {}

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
    
    # Run automatic sync from platform usage if not already running internally
    if os.environ.get("INTERNAL_SYNC") != "true":
        sync_from_platform_usage()
        # Reload budget after sync to get updated limit/used check
        budget = load_budget()

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
