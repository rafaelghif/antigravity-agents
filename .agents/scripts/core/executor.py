import os
import sys
import time
import subprocess
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

try:
    from core.logger import logger
except ImportError:
    try:
        from .logger import logger
    except ImportError:
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        from core.logger import logger

@dataclass
class ExecutionResult:
    command: List[str]
    returncode: int
    stdout: str
    stderr: str
    duration: float

    @property
    def success(self) -> bool:
        return self.returncode == 0

class ShellExecutor:
    def __init__(self, sanitize: bool = True):
        self.sanitize = sanitize

    def _sanitize(self, cmd: List[str]) -> None:
        """Scan command arguments for potential command injection vectors."""
        if not self.sanitize:
            return
            
        blacklist = [';', '&&', '||', '|', '`', '$(', '\n', '\r']
        for arg in cmd:
            if any(char in arg for char in blacklist):
                raise ValueError(f"Unsafe shell argument blocked: '{arg}'. Contains blacklisted character.")

    def execute(
        self, 
        cmd: List[str], 
        check: bool = False, 
        capture_output: bool = True, 
        text: bool = True, 
        env: Optional[Dict[str, str]] = None, 
        cwd: Optional[str] = None
    ) -> ExecutionResult:
        """Run a command safely and measure execution duration (telemetry)."""
        self._sanitize(cmd)
        
        cmd_str = " ".join(cmd)
        logger.debug(f"Executing shell command: '{cmd_str}'", extra={"cwd": cwd or "."})
        
        start_time = time.perf_counter()
        try:
            res = subprocess.run(
                cmd,
                stdout=subprocess.PIPE if capture_output else None,
                stderr=subprocess.PIPE if capture_output else None,
                text=text,
                env=env,
                cwd=cwd
            )
            duration = time.perf_counter() - start_time
            
            stdout_str = res.stdout if capture_output and res.stdout else ""
            stderr_str = res.stderr if capture_output and res.stderr else ""
            
            result = ExecutionResult(
                command=cmd,
                returncode=res.returncode,
                stdout=stdout_str,
                stderr=stderr_str,
                duration=duration
            )
            
            if not result.success:
                logger.debug(
                    f"Command failed (exit {result.returncode}): '{cmd_str}' in {duration:.4f}s",
                    extra={"stderr": result.stderr.strip()[:200]}
                )
                if check:
                    raise subprocess.CalledProcessError(
                        result.returncode, cmd, output=result.stdout, stderr=result.stderr
                    )
            else:
                logger.debug(f"Command succeeded in {duration:.4f}s: '{cmd_str}'")
                
            return result
            
        except Exception as e:
            duration = time.perf_counter() - start_time
            logger.error(f"Failed to execute command '{cmd_str}': {e}")
            raise

# Default global executor
executor = ShellExecutor()
