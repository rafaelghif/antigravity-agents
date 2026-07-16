import os
import sys
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any

# ANSI Colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

class LogLevel:
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"

class StructuredLogger:
    def __init__(self, name: str = "AAC"):
        self.name = name
        self.json_format = os.environ.get("AAC_LOG_JSON") == "1"
        self.color_enabled = (
            not os.environ.get("NO_COLOR") 
            and sys.stdout.isatty() 
            and os.environ.get("ANTIGRAVITY_NONINTERACTIVE") != "1"
        )

    def _format_message(self, level: str, msg: str, extra: Optional[Dict[str, Any]] = None) -> str:
        if self.json_format:
            log_data = {
                "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                "level": level,
                "logger": self.name,
                "message": msg
            }
            if extra:
                log_data.update(extra)
            return json.dumps(log_data)
        
        # Color definitions
        color_map = {
            LogLevel.DEBUG: BLUE,
            LogLevel.INFO: "",
            LogLevel.WARN: YELLOW,
            LogLevel.ERROR: RED,
            LogLevel.SUCCESS: GREEN
        }
        
        prefix_map = {
            LogLevel.DEBUG: "[DEBUG]",
            LogLevel.INFO: "[INFO]",
            LogLevel.WARN: "[WARN]",
            LogLevel.ERROR: "[FAIL]",
            LogLevel.SUCCESS: "[OK]"
        }
        
        color = color_map.get(level, "") if self.color_enabled else ""
        reset = RESET if self.color_enabled and color else ""
        prefix = prefix_map.get(level, f"[{level}]")
        
        base_log = f"{color}{prefix} {msg}{reset}"
        if extra:
            extra_str = " | " + " ".join(f"{k}={v}" for k, v in extra.items())
            base_log += f"{color}{extra_str}{reset}"
        return base_log

    def log(self, level: str, msg: str, extra: Optional[Dict[str, Any]] = None) -> None:
        formatted = self._format_message(level, msg, extra)
        if level in (LogLevel.ERROR, LogLevel.WARN):
            print(formatted, file=sys.stderr, flush=True)
        else:
            print(formatted, flush=True)

    def debug(self, msg: str, extra: Optional[Dict[str, Any]] = None) -> None:
        if os.environ.get("AAC_DEBUG") == "1" or os.environ.get("DEBUG") == "1":
            self.log(LogLevel.DEBUG, msg, extra)

    def info(self, msg: str, extra: Optional[Dict[str, Any]] = None) -> None:
        self.log(LogLevel.INFO, msg, extra)

    def warn(self, msg: str, extra: Optional[Dict[str, Any]] = None) -> None:
        self.log(LogLevel.WARN, msg, extra)

    def error(self, msg: str, extra: Optional[Dict[str, Any]] = None) -> None:
        self.log(LogLevel.ERROR, msg, extra)

    def success(self, msg: str, extra: Optional[Dict[str, Any]] = None) -> None:
        self.log(LogLevel.SUCCESS, msg, extra)

# Default global logger
logger = StructuredLogger("AAC")
