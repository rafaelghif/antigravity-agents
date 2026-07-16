import os
import sys
import json
import re
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from typing import List

BUDGET_FILE = ".agents/state/token_budget.json"
LOG_FILE = ".agents/state/logs/token_usage.log"

GLOBAL_GEMINI_DIR = os.environ.get("AAC_HOME") or os.path.expanduser("~/.gemini")

def get_active_api_account() -> str:
    for var in ("ACTIVE_API_PROFILE", "API_ACCOUNT", "GEMINI_API_PROFILE"):
        val = os.environ.get(var)
        if val:
            return val.strip()

    profile_file = ".agents/active_api_profile_name"
    if os.path.exists(profile_file):
        try:
            with open(profile_file, 'r', encoding='utf-8') as f:
                val = f.read().strip()
                if val:
                    return val
        except Exception:
            pass

    import hashlib
    for key_var, prefix in (
        ("GEMINI_API_KEY", "gemini"),
        ("OPENAI_API_KEY", "openai"),
        ("ANTHROPIC_API_KEY", "anthropic")
    ):
        key_val = os.environ.get(key_var)
        if key_val:
            key_val = key_val.strip()
            key_hash = hashlib.sha256(key_val.encode('utf-8')).hexdigest()
            return f"{prefix}:sha256-{key_hash[:8]}"

    try:
        acc_file = os.path.join(GLOBAL_GEMINI_DIR, "google_accounts.json")
        if os.path.exists(acc_file):
            with open(acc_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                active = data.get("active")
                if active:
                    return active.strip()
    except Exception:
        pass

    try:
        log_dir = os.path.join(GLOBAL_GEMINI_DIR, "antigravity-cli/log")
        if os.path.exists(log_dir):
            log_files = [
                os.path.join(log_dir, f)
                for f in os.listdir(log_dir)
                if f.startswith("cli-") and f.endswith(".log")
            ]
            if log_files:
                log_files.sort(key=os.path.getmtime, reverse=True)
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

def recalculate_used_from_log(budget: dict) -> dict:
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
            for line in reversed(lines):
                line = line.strip()
                if not line:
                    continue
                m = re.match(r'\[(.*?)\] Task:.*?\|.*\|.*\| Total:\s*(\d+)', line)
                if m:
                    ts_str = m.group(1)
                    ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S UTC").replace(tzinfo=timezone.utc)
                    total = int(m.group(2))
                    
                    if ts.year < this_month_utc[0] or (ts.year == this_month_utc[0] and ts.month < this_month_utc[1]):
                        break
                        
                    if ts.date() == today_utc:
                        daily_sum += total
                    if ts.year == this_month_utc[0] and ts.month == this_month_utc[1]:
                        monthly_sum += total
        except Exception:
            pass
            
    budget["daily_used"] = daily_sum
    budget["monthly_used"] = monthly_sum
    return budget

def _save_budget_nolock(data: dict) -> None:
    os.makedirs(os.path.dirname(BUDGET_FILE), exist_ok=True)
    try:
        dir_name = os.path.dirname(BUDGET_FILE) or "."
        with tempfile.NamedTemporaryFile('w', dir=dir_name, delete=False, encoding='utf-8') as tf:
            json.dump(data, tf, indent=2)
            temp_name = tf.name
        os.replace(temp_name, BUDGET_FILE)
    except Exception:
        pass

def save_budget(data: dict) -> None:
    try:
        from helper import FileLockMutex
    except ImportError:
        cli_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if cli_dir not in sys.path:
            sys.path.insert(0, cli_dir)
        from helper import FileLockMutex

    try:
        with FileLockMutex(BUDGET_FILE):
            _save_budget_nolock(data)
    except Exception:
        _save_budget_nolock(data)

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
    
    try:
        from helper import FileLockMutex
    except ImportError:
        cli_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if cli_dir not in sys.path:
            sys.path.insert(0, cli_dir)
        from helper import FileLockMutex

    try:
        with FileLockMutex(BUDGET_FILE):
            if not os.path.exists(BUDGET_FILE):
                return recalculate_used_from_log(default_budget)
            try:
                with open(BUDGET_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key in default_budget:
                        if key not in data:
                            data[key] = default_budget[key]
                    if "accounts" not in data:
                        data["accounts"] = {}
                    if data.get("daily_limit", 0) < 500000:
                        data["daily_limit"] = 500000
                    if data.get("monthly_limit", 0) < 5000000:
                        data["monthly_limit"] = 5000000
                        
                    try:
                        from core.entities import TokenBudget, ValidationError
                    except ImportError:
                        try:
                            from ....core.entities import TokenBudget, ValidationError
                        except ImportError:
                            sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
                            from core.entities import TokenBudget, ValidationError

                    try:
                        global_budget = TokenBudget.from_dict("global", data)
                        global_budget.validate()
                        
                        for acc, acc_data in data.get("accounts", {}).items():
                            acc_budget = TokenBudget.from_dict(acc, acc_data)
                            acc_budget.validate()
                    except ValidationError as ve:
                        print(f"Warning: Token budget validation failed: {ve}")

                    return recalculate_used_from_log(data)
            except Exception:
                return recalculate_used_from_log(default_budget)
    except Exception:
        if not os.path.exists(BUDGET_FILE):
            return recalculate_used_from_log(default_budget)
        try:
            with open(BUDGET_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return recalculate_used_from_log(data)
        except Exception:
            return recalculate_used_from_log(default_budget)

def check_date_resets(budget: dict) -> dict:
    try:
        last_reset_str = budget.get("last_reset", "")
        if last_reset_str.endswith("Z"):
            last_reset_str = last_reset_str[:-1] + "+00:00"
        last_reset_dt = datetime.fromisoformat(last_reset_str)
    except Exception:
        last_reset_dt = datetime.utcnow()

    now_dt = datetime.utcnow()
    
    if now_dt.year != last_reset_dt.year or now_dt.month != last_reset_dt.month:
        budget["monthly_used"] = 0
        budget["daily_used"] = 0
        if "accounts" in budget:
            for acc in budget["accounts"].values():
                acc["daily_used"] = 0
                acc["monthly_used"] = 0
        budget["last_reset"] = now_dt.isoformat() + "Z"
    elif now_dt.date() != last_reset_dt.date():
        budget["daily_used"] = 0
        if "accounts" in budget:
            for acc in budget["accounts"].values():
                acc["daily_used"] = 0
        budget["last_reset"] = now_dt.isoformat() + "Z"

    return budget

def get_current_task_id() -> str:
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
    except Exception:
        pass

def get_transcript_tokens_fallback() -> tuple:
    conversation_id = os.environ.get("ANTIGRAVITY_CONVERSATION_ID")
    if not conversation_id:
        brain_dir = os.path.join(GLOBAL_GEMINI_DIR, "antigravity-cli/brain")
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

    transcript_path = os.path.join(GLOBAL_GEMINI_DIR, "antigravity-cli/brain", conversation_id, ".system_generated/logs/transcript.jsonl")
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
            prompt_tokens = 15000

        return prompt_tokens, completion_tokens
    except Exception:
        return 15000, 1000

def auto_detect_tokens() -> tuple:
    if os.environ.get("INTERNAL_SYNC") == "true":
        return get_transcript_tokens_fallback()

    is_testing = "unittest" in sys.modules or "pytest" in sys.modules
    if is_testing and os.environ.get("FORCE_PLATFORM_DETECT") != "true":
        return get_transcript_tokens_fallback()

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
                task_id = get_current_task_id()
                platform_tasks = parsed.get("tasks", {})
                platform_task_info = platform_tasks.get(task_id)
                
                if not platform_task_info and "unknown" in platform_tasks:
                    platform_task_info = platform_tasks["unknown"]
                
                if platform_task_info:
                    platform_prompt = platform_task_info.get("prompt_tokens", 0)
                    platform_completion = platform_task_info.get("completion_tokens", 0)
                    
                    budget = load_budget()
                    local_tasks = budget.get("tasks", {})
                    local_task_info = local_tasks.get(task_id, {})
                    
                    local_prompt = local_task_info.get("prompt_tokens", 0)
                    local_completion = local_task_info.get("completion_tokens", 0)
                    
                    prompt_diff = platform_prompt - local_prompt
                    completion_diff = platform_completion - local_completion
                    
                    if prompt_diff > 0 or completion_diff > 0:
                        return max(0, prompt_diff), max(0, completion_diff)
                
                platform_daily = parsed.get("daily_used", 0)
                budget = load_budget()
                local_daily = budget.get("daily_used", 0)
                
                daily_diff = platform_daily - local_daily
                if daily_diff > 0:
                    prompt_est = int(daily_diff * 0.9)
                    comp_est = int(daily_diff * 0.1)
                    return max(1, prompt_est), max(1, comp_est)
    except Exception:
        pass

    return get_transcript_tokens_fallback()

def normalize_time_string(raw_time: str) -> str:
    raw_time = raw_time.replace(',', '').lower()
    raw_time = re.sub(r'\bdays?\b', 'd', raw_time)
    raw_time = re.sub(r'\bhours?\b', 'h', raw_time)
    raw_time = re.sub(r'\bminutes?\b', 'm', raw_time)
    raw_time = re.sub(r'(\d+)\s*([dhm])', r'\1\2', raw_time)
    raw_time = re.sub(r'\s+', ' ', raw_time).strip()
    return raw_time

def parse_usage_output(output: str, budget: dict = None) -> dict:
    stats = {}
    stripped = output.strip()
    if stripped.startswith("```json"):
        stripped = stripped[7:].rstrip("`").strip()
    elif stripped.startswith("```"):
        stripped = stripped[3:].rstrip("`").strip()
        
    if stripped.startswith("{") and stripped.endswith("}"):
        try:
            json_data = json.loads(stripped)
            for k in ("daily_limit", "daily_used", "monthly_limit", "monthly_used", 
                      "five_hour_limit", "five_hour_used", "five_hour_remaining", 
                      "weekly_limit", "weekly_used", "weekly_remaining", "active_account",
                      "accounts", "tasks", "weekly_pct", "five_hour_pct"):
                if k in json_data:
                    stats[k] = json_data[k]
            if "weekly_pct" in stats and "weekly_remaining_pct" not in stats:
                stats["weekly_remaining_pct"] = 100.0 - stats["weekly_pct"]
            if "five_hour_pct" in stats and "five_hour_remaining_pct" not in stats:
                stats["five_hour_remaining_pct"] = 100.0 - stats["five_hour_pct"]
            if stats:
                stats["is_json_format"] = True
                return stats
        except Exception:
            pass

    lines = output.split('\n')
    has_blocks = any("██" in line or "░░" in line for line in lines)
    if has_blocks:
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
        stats["is_block_format"] = True
        return stats

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

    if "daily_limit" not in stats or "monthly_limit" not in stats:
        in_breakdown = False
        for line in lines:
            line_lower = line.lower()
            if "account breakdown:" in line_lower or "task breakdown:" in line_lower or "breakdown" in line_lower:
                in_breakdown = True
            if in_breakdown:
                continue
            if "Daily" in line and "Limit" not in line and "Used" not in line:
                clean_line = re.sub(r'Daily\s*(?:Quota)?', '', line, flags=re.IGNORECASE)
                nums = [int(s.replace(',', '')) for s in re.findall(r'\b\d{1,3}(?:,\d{3})+\b|\b\d+\b', clean_line)]
                if len(nums) >= 2:
                    if "Quota" in line or "/" in line:
                        stats["daily_used"] = nums[0]
                        stats["daily_limit"] = nums[1]
                    else:
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

        if "five_hour_limit" not in stats:
            for line in lines:
                if "|" in line and "5-Hour" in line:
                    parts = [p.strip() for p in line.split('|') if p.strip()]
                    if len(parts) >= 4:
                        try:
                            limit_str = re.sub(r'[^\d]', '', parts[1])
                            used_str = re.sub(r'[^\d]', '', parts[2])
                            if limit_str and used_str:
                                stats["five_hour_limit"] = int(limit_str)
                                stats["five_hour_used"] = int(used_str)
                            for part in parts[3:]:
                                if "%" in part:
                                    pct_str = re.sub(r'[^\d.]', '', part)
                                    if pct_str:
                                        stats["five_hour_pct"] = float(pct_str)
                                        break
                        except Exception:
                            pass
                    break

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
                    m_slash = re.search(r'([\d,`\s]+)\s*/\s*([\d,`\s]+)', five_hour_text)
                    if m_slash:
                        stats["five_hour_used"] = int(m_slash.group(1).replace('`','').replace(',','').strip())
                        stats["five_hour_limit"] = int(m_slash.group(2).replace('`','').replace(',','').strip())
                    else:
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

        if "weekly_limit" not in stats:
            for line in lines:
                if "|" in line and "Weekly" in line:
                    parts = [p.strip() for p in line.split('|') if p.strip()]
                    if len(parts) >= 4:
                        try:
                            limit_str = re.sub(r'[^\d]', '', parts[1])
                            used_str = re.sub(r'[^\d]', '', parts[2])
                            if limit_str and used_str:
                                stats["weekly_limit"] = int(limit_str)
                                stats["weekly_used"] = int(used_str)
                            for part in parts[3:]:
                                if "%" in part:
                                    pct_str = re.sub(r'[^\d.]', '', part)
                                    if pct_str:
                                        stats["weekly_pct"] = float(pct_str)
                                        break
                        except Exception:
                            pass
                    break

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
                    m_slash = re.search(r'([\d,`\s]+)\s*/\s*([\d,`\s]+)', weekly_text)
                    if m_slash:
                        stats["weekly_used"] = int(m_slash.group(1).replace('`','').replace(',','').strip())
                        stats["weekly_limit"] = int(m_slash.group(2).replace('`','').replace(',','').strip())
                    else:
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

    if "five_hour_limit" in stats and "five_hour_used" in stats and "five_hour_pct" not in stats:
        stats["five_hour_pct"] = (stats["five_hour_used"] / stats["five_hour_limit"] * 100) if stats["five_hour_limit"] > 0 else 0
    if "weekly_limit" in stats and "weekly_used" in stats and "weekly_pct" not in stats:
        stats["weekly_pct"] = (stats["weekly_used"] / stats["weekly_limit"] * 100) if stats["weekly_limit"] > 0 else 0

    accounts = {}
    in_account_breakdown = False
    for line in lines:
        line_lower = line.lower()
        if "account breakdown" in line_lower:
            in_account_breakdown = True
            continue
        if in_account_breakdown:
            if line.startswith("---") or line.startswith("===") or "task breakdown:" in line_lower:
                in_account_breakdown = False
            else:
                m = re.match(r'\s*[-*]\s*(?:\*\*)?([a-zA-Z0-9_.@+-:]+)(?:\*\*)?\s*:\s*(?:daily\s*)?([\d,]+)\s*(?:\(Daily\)|\(daily\)|daily)?\s*\|\s*(?:monthly\s*)?([\d,]+)\s*(?:\(Monthly\)|\(monthly\)|monthly)?\s*\|\s*(?:total\s*)?([\d,]+)(?:\(Total\)|\(total\)|total)?', line, re.IGNORECASE)
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

    tasks = {}
    in_task_breakdown = False
    for line in lines:
        line_lower = line.lower()
        if "task breakdown" in line_lower:
            in_task_breakdown = True
            continue
        if in_task_breakdown:
            if line.startswith("---") or line.startswith("===") or "account breakdown:" in line_lower:
                in_task_breakdown = False
            else:
                m = re.match(r'\s*[-*]\s*(?:\*\*)?([a-zA-Z0-9_-]+)(?:\*\*)?\s*:\s*([\d,]+)\s*total\s*\(([\d,]+)\s*prompt\s*/\s*([\d,]+)\s*completion\)', line, re.IGNORECASE)
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
    brain_dir = os.path.join(GLOBAL_GEMINI_DIR, "antigravity-cli/brain")
    if os.path.exists(brain_dir):
        try:
            conversation_ids = [
                d for d in os.listdir(brain_dir)
                if os.path.isdir(os.path.join(brain_dir, d)) and not d.startswith(".")
            ]
            if conversation_ids:
                conversation_ids.sort(
                    key=lambda x: os.path.getmtime(os.path.join(brain_dir, x)),
                    reverse=True
                )
                for cid in conversation_ids[:5]:
                    dir_path = os.path.join(brain_dir, cid)
                    if (datetime.now().timestamp() - os.path.getmtime(dir_path)) > 300:
                        continue
                        
                    transcript_path = os.path.join(dir_path, ".system_generated/logs/transcript.jsonl")
                    if os.path.exists(transcript_path):
                        try:
                            with open(transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
                                lines = f.readlines()
                            for line in reversed(lines):
                                line = line.strip()
                                if not line:
                                    continue
                                try:
                                    step = json.loads(line)
                                    content = step.get("content", "") or ""
                                    text = str(content)
                                    if "Weekly Limit" in text and "GEMINI MODELS" in text:
                                        created_at_str = step.get("created_at")
                                        if created_at_str:
                                            created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                                            age = (datetime.now(timezone.utc) - created_at).total_seconds()
                                            if age <= 300:
                                                return text
                                        else:
                                            return text
                                except Exception:
                                    pass
                        except Exception:
                            pass
        except Exception:
            pass

    db_dir = os.path.join(GLOBAL_GEMINI_DIR, "antigravity-cli/conversations")
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
            
        db_files.sort(key=os.path.getmtime, reverse=True)
        
        for db_path in db_files[:10]:
            if (datetime.now().timestamp() - os.path.getmtime(db_path)) > 300:
                continue
                
            try:
                import sqlite3
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='steps'")
                if not cursor.fetchone():
                    conn.close()
                    continue
                    
                cursor.execute("SELECT step_payload FROM steps ORDER BY idx DESC")
                for (payload,) in cursor.fetchall():
                    if not payload:
                        continue
                    try:
                        text = payload.decode('utf-8', errors='ignore')
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
    db_usage = scan_conversations_for_usage()
    parsed = None
    if db_usage:
        parsed = parse_usage_output(db_usage)
        if parsed:
            parsed["synced_from_db"] = True
            
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

        budget["last_sync"] = datetime.utcnow().isoformat() + "Z"

        if "weekly_limit" in parsed and not parsed.get("is_block_format"):
            budget["weekly_limit"] = parsed["weekly_limit"]
        else:
            log_stats = get_rolling_window_stats()
            local_weekly = log_stats.get("weekly_used", 0)
            if "weekly_pct" in parsed and parsed["weekly_pct"] > 0:
                calculated_weekly_limit = int(local_weekly / (parsed["weekly_pct"] / 100.0))
                if calculated_weekly_limit > 0:
                    budget["weekly_limit"] = calculated_weekly_limit

        if "five_hour_limit" in parsed and not parsed.get("is_block_format"):
            budget["five_hour_limit"] = parsed["five_hour_limit"]
        else:
            log_stats = get_rolling_window_stats()
            local_five_hour = log_stats.get("five_hour_used", 0)
            if "five_hour_pct" in parsed and parsed["five_hour_pct"] > 0:
                calculated_five_hour_limit = int(local_five_hour / (parsed["five_hour_pct"] / 100.0))
                if calculated_five_hour_limit > 0:
                    budget["five_hour_limit"] = calculated_five_hour_limit
        
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

def trigger_background_sync() -> None:
    try:
        # Determine paths relative to this file
        helper_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../helper.py"))
        cmd_args = [sys.executable, helper_path, "token", "sync", "--auto"]
        if os.name == 'nt':
            DETACHED_PROCESS = 0x00000008
            subprocess.Popen(
                cmd_args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=DETACHED_PROCESS
            )
        else:
            subprocess.Popen(
                cmd_args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
    except Exception:
        pass

def get_reset_intervals_remaining() -> dict:
    now = datetime.now(timezone.utc)
    
    current_hour = now.hour
    next_hour = ((current_hour // 5) + 1) * 5
    if next_hour >= 24:
        next_dt = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        next_dt = now.replace(hour=next_hour, minute=0, second=0, microsecond=0)
    five_hour_remaining = next_dt - now
    
    next_day_dt = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    daily_remaining = next_day_dt - now
    
    days_to_sunday = 6 - now.weekday()
    next_sunday_dt = (now + timedelta(days=days_to_sunday if days_to_sunday > 0 else 7)).replace(hour=0, minute=0, second=0, microsecond=0)
    if now.weekday() == 6:
        next_sunday_dt = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    weekly_remaining = next_sunday_dt - now
    
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
    now = datetime.now(timezone.utc)
    
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
    
    if budget.get("weekly_used_override") is not None:
        stats["weekly_used"] = budget["weekly_used_override"]
    elif budget.get("weekly_pct_override") is not None:
        stats["weekly_used"] = int(budget["weekly_pct_override"] / 100 * stats["weekly_limit"])
        
    if budget.get("weekly_pct_override") is not None:
        stats["weekly_pct"] = budget["weekly_pct_override"]
        
    if budget.get("weekly_remaining_override") is not None:
        stats["weekly_remaining"] = budget["weekly_remaining_override"]
        
    if budget.get("five_hour_used_override") is not None:
        stats["five_hour_used"] = budget["five_hour_used_override"]
    elif budget.get("five_hour_pct_override") is not None:
        stats["five_hour_used"] = int(budget["five_hour_pct_override"] / 100 * stats["five_hour_limit"])
        
    if budget.get("five_hour_pct_override") is not None:
        stats["five_hour_pct"] = budget["five_hour_pct_override"]
        
    if budget.get("five_hour_remaining_override") is not None:
        stats["five_hour_remaining"] = budget["five_hour_remaining_override"]
        
    return stats
