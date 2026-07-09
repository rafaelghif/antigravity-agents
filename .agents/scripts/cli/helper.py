import sys
import os
import importlib
import time
import json
from datetime import datetime, timezone

# Reconfigure stdout/stderr to support UTF-8 on Windows cp932/etc. terminals
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


def log_cli_execution(cmd: str, args: list, status: str, duration_ms: float, error: str = None) -> None:
    log_dir = ".agents/logs"
    log_file = os.path.join(log_dir, "cli.log")
    try:
        os.makedirs(log_dir, exist_ok=True)
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "command": cmd,
            "args": args,
            "status": status,
            "duration_ms": round(duration_ms, 2),
            "error": error
        }
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_help():
    banner = f"""{CYAN}{BOLD}==========================================================
   Antigravity Agent Core (AAC) V2 CLI Command Helper     
=========================================================={RESET}
{BOLD}Usage:{RESET} ./helper.sh <command> [args...]
       aac <command> [args...] (if global launcher is installed)

{BOLD}Available Commands:{RESET}
  🚀 {GREEN}{BOLD}bootstrap{RESET}       Scaffolds directory structures & stack detection.
  ✅ {GREEN}{BOLD}validate{RESET}        Runs validation guard (audits secrets, board, linting, tests).
  🔄 {GREEN}{BOLD}sync{RESET}            Synchronizes skills index in AGENTS.md & ADR registry.
  🎫 {GREEN}{BOLD}issue{RESET}           Manages local task tracker issues (checkout, close, list).
  🔒 {GREEN}{BOLD}lock{RESET}            Acquires module locks to prevent concurrent modifications.
  👤 {GREEN}{BOLD}profile{RESET}         Configures/switches developer git commit identities.
  📝 {GREEN}{BOLD}changelog{RESET}       Generates conventional commit release notes & bumps SemVer.
  🧠 {GREEN}{BOLD}learn{RESET}           Records developer/agent lessons directly to lessons-learned.md.
  💬 {GREEN}{BOLD}commit{RESET}          Fires safe git commit command gated by validation guard.
  🩺 {GREEN}{BOLD}doctor{RESET}          Runs workspace diagnostics health audits.
  ⬆️ {GREEN}{BOLD}upgrade{RESET}         Upgrades Antigravity Agent Core core scripts & wrappers.
  ⌨️ {GREEN}{BOLD}completion{RESET}      Generates terminal tab-completion scripts (Bash/Zsh).
  🌐 {GREEN}{BOLD}install-global{RESET}  Installs the global 'aac' launcher wrapper to PATH.
  🎯 {GREEN}{BOLD}context{RESET}         Optimizes workspace context scope for active task.
  📊 {GREEN}{BOLD}dashboard{RESET}       Launches the local interactive web-based dashboard dashboard.
  🪙 {GREEN}{BOLD}token{RESET}           Logs and displays LLM token budget usage statistics.
  🔌 {GREEN}{BOLD}mcp{RESET}             Manages MCP tool integration and server registration.
  💓 {GREEN}{BOLD}heartbeat{RESET}       Runs workspace heartbeat diagnostic checks (verifies locks, hooks, budget).

{BOLD}For more information on a command, run:{RESET} ./helper.sh help <command>
"""
    print(banner)

def print_command_help(cmd):
    command_help = {
        "bootstrap": f"""{CYAN}{BOLD}Command: bootstrap{RESET}
🚀 Scaffolds directories, detects stack, writes AGENTS.md.

{BOLD}Usage:{RESET} ./helper.sh bootstrap [name] [stack] [arch: clean|layered|mvc]
  - If parameters are omitted, runs interactive setup.
  - arch defaults to 'clean' if not specified.""",

        "validate": f"""{CYAN}{BOLD}Command: validate{RESET}
✅ Runs validation guard locally to audit the workspace before committing.

{BOLD}Usage:{RESET} ./helper.sh validate [--skip-subtasks]
  - Audits critical files, secrets, link integrity, git branch, task board, and locks.
  - Runs local unit test suites automatically.""",

        "sync": f"""{CYAN}{BOLD}Command: sync{RESET}
🔄 Synchronizes local custom skills in AGENTS.md and ADRs in the memory register.

{BOLD}Usage:{RESET} ./helper.sh sync""",

        "issue": f"""{CYAN}{BOLD}Command: issue{RESET}
🎫 Manages local task tracker issues and branches.

{BOLD}Usage:{RESET}
  - ./helper.sh issue create <issue-id> "<title>" : Creates a local issue spec.
  - ./helper.sh issue list                       : Lists all issues in workspace.
  - ./helper.sh issue checkout <issue-id>        : Checks out/creates the issue branch.
  - ./helper.sh issue sync                       : Synchronizes issue status with task board.
  - ./helper.sh issue close <issue-id>           : Closes issue, bumps SemVer, and merges to main.""",

        "lock": f"""{CYAN}{BOLD}Command: lock{RESET}
🔒 Acquires or releases local locks on module files to prevent conflicting parallel edits.

{BOLD}Usage:{RESET} ./helper.sh lock <module-name> [--release]
  - Lock is acquired on the current active feature branch.
  - Locked modules will block validation if edited on another branch.""",

        "profile": f"""{CYAN}{BOLD}Command: profile{RESET}
👤 Manages developer Git identities and switches profiles.

{BOLD}Usage:{RESET}
  - ./helper.sh profile list                   : Lists all configured profiles.
  - ./helper.sh profile switch <profile-name>  : Switches to target profile identity.
  - ./helper.sh profile add                    : Launches wizard to register a new profile.""",

        "changelog": f"""{CYAN}{BOLD}Command: changelog{RESET}
📝 Generates conventional commits release notes and bumps SemVer.

{BOLD}Usage:{RESET} ./helper.sh changelog""",

        "learn": f"""{CYAN}{BOLD}Command: learn{RESET}
🧠 Records developer/agent lessons directly to memory/lessons-learned.md.

{BOLD}Usage:{RESET} ./helper.sh learn "<lesson_text>" [--category <name>]""",

        "commit": f"""{CYAN}{BOLD}Command: commit{RESET}
💬 Gated Conventional Commit wrapper that runs validation first.

{BOLD}Usage:{RESET} ./helper.sh commit -m "<subject>" [-m "<body>"]
  - Blocks commit if local validation guard fails.""",

        "doctor": f"""{CYAN}{BOLD}Command: doctor{RESET}
🩺 Diagnoses local environment configuration, tool versioning, and profiles health.

{BOLD}Usage:{RESET} ./helper.sh doctor""",

        "upgrade": f"""{CYAN}{BOLD}Command: upgrade{RESET}
⬆️ Self-upgrades Antigravity Agent Core templates and CLI command modules to the latest version.

{BOLD}Usage:{RESET} ./helper.sh upgrade""",

        "completion": f"""{CYAN}{BOLD}Command: completion{RESET}
⌨️ Generates tab-completion configuration for the shell terminal.

{BOLD}Usage:{RESET} ./helper.sh completion <bash|zsh>""",

        "install-global": f"""{CYAN}{BOLD}Command: install-global{RESET}
🌐 Installs the global 'aac' launcher command alias into user local path directory.

{BOLD}Usage:{RESET} ./helper.sh install-global""",

        "context": f"""{CYAN}{BOLD}Command: context{RESET}
🎯 Optimizes the workspace active context and locks scope for the active task.

{BOLD}Usage:{RESET} ./helper.sh context optimize""",

        "dashboard": f"""{CYAN}{BOLD}Command: dashboard{RESET}
📊 Launches the local interactive web-based visual dashboard.

{BOLD}Usage:{RESET} ./helper.sh dashboard""",

        "token": f"""{CYAN}{BOLD}Command: token{RESET}
🪙 Manages LLM token usage tracking and daily/monthly budgets.

{BOLD}Usage:{RESET}
  - ./helper.sh token log <prompt> <completion> [--task <id>] : Logs token usage for a task.
  - ./helper.sh token status                                  : Displays budget utilization statistics.
  - ./helper.sh token reset [--daily | --monthly | --all]     : Resets budget counters.""",

        "mcp": f"""{CYAN}{BOLD}Command: mcp{RESET}
🔌 Manages model context protocol (MCP) server integration.

{BOLD}Usage:{RESET}
  - ./helper.sh mcp register : Registers the workspace tools server with Cline/VS Code config.
  - ./helper.sh mcp start    : Starts the zero-dependency JSON-RPC MCP server on stdin/stdout.""",

        "heartbeat": f"""{CYAN}{BOLD}Command: heartbeat{RESET}
💓 Runs workspace heartbeat diagnostic checks to verify locks, hooks, budget status, and git state.

{BOLD}Usage:{RESET}
  - ./helper.sh heartbeat : Runs the diagnostics check."""
    }

    if cmd in command_help:
        print(command_help[cmd])
    else:
        print(f"{RED}Error: Help not available for unknown command '{cmd}'.{RESET}")

def main():
    help_args = {'help', '-h', '--help'}
    
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)
    
    cmd = sys.argv[1].lower()
    
    # Check if an upgrade is available and notify the user
    if cmd not in ('upgrade', 'help', '-h', '--help') and cmd not in help_args:
        try:
            state_file = ".agents/upgrade_state.json"
            if os.path.exists(state_file):
                with open(state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                if state.get("upgrade_available"):
                    print(f"\033[93m[WARN] A new version of Antigravity Agent Core is available! Run './helper.sh upgrade' to apply it.\033[0m\n")
        except Exception:
            pass
            
    if cmd in help_args:
        if len(sys.argv) > 2:
            sub_cmd = sys.argv[2].lower()
            print_command_help(sub_cmd)
        else:
            print_help()
        sys.exit(0)
        
    allowed_commands = {'lock', 'validate', 'sync', 'issue', 'commit', 'bootstrap', 'profile', 'changelog', 'learn', 'skill', 'doctor', 'upgrade', 'completion', 'install-global', 'context', 'dashboard', 'token', 'mcp', 'heartbeat'}
    
    if len(sys.argv) > 2 and sys.argv[2].lower() in help_args:
        print_command_help(cmd)
        sys.exit(0)
        
    if cmd not in allowed_commands:
        print(f"{RED}Error: Unknown command '{cmd}'.{RESET}")
        print_help()
        sys.exit(1)
        
    start_time = time.perf_counter()
    status = "success"
    error_msg = None
    
    try:
        # Resolve command file path dynamically (hyphens mapped to underscores)
        module_name = cmd.replace('-', '_')
        cmd_file = os.path.abspath(os.path.join(os.path.dirname(__file__), f"commands/{module_name}.py"))
        if not os.path.exists(cmd_file):
            print(f"{RED}Error: Command module file '{cmd_file}' not found.{RESET}")
            status = "failed"
            error_msg = f"Command module file '{cmd_file}' not found"
            sys.exit(1)
            
        # Inject project root path into sys.path to resolve imports correctly
        root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
        if root_path not in sys.path:
            sys.path.insert(0, root_path)
            
        import importlib.util
        spec = importlib.util.spec_from_file_location(f"cmd_{module_name}", cmd_file)
        if spec is None or spec.loader is None:
            print(f"{RED}Error: Could not load command module spec for '{cmd}'.{RESET}")
            status = "failed"
            error_msg = f"Could not load command module spec for '{cmd}'"
            sys.exit(1)
        cmd_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cmd_module)
        if not hasattr(cmd_module, "run"):
            print(f"{RED}Error: Command module '{cmd}' does not implement required 'run(args)' method.{RESET}")
            status = "failed"
            error_msg = f"Command module '{cmd}' does not implement required 'run(args)' method"
            sys.exit(1)
        cmd_module.run(sys.argv[2:])
    except SystemExit as se:
        if se.code != 0:
            status = "failed"
            error_msg = f"SystemExit: {se.code}"
        raise
    except Exception as e:
        status = "failed"
        error_msg = str(e)
        print(f"{RED}Error executing command '{cmd}': {e}{RESET}")
        sys.exit(1)
    finally:
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        log_cli_execution(cmd, sys.argv[2:], status, duration_ms, error_msg)
        try:
            if cmd not in ('upgrade', 'dashboard'):
                state_file = ".agents/upgrade_state.json"
                now = time.time()
                should_check = True
                try:
                    if os.path.exists(state_file):
                        with open(state_file, 'r', encoding='utf-8') as f:
                            state = json.load(f)
                        last_check = state.get("last_check_timestamp", 0)
                        if now - last_check < 1800:
                            should_check = False
                except Exception:
                    pass

                if should_check and os.environ.get("AAC_DISABLE_AUTO_UPDATE") != "true" and os.environ.get("IN_AUDIT_TEST") != "true":
                    import subprocess
                    helper_path = os.path.abspath(__file__)
                    cmd_args = [sys.executable, helper_path, "upgrade", "--background-check"]
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

class FileLockMutex:
    """A cross-platform zero-dependency atomic mutex using filesystem directories."""
    def __init__(self, filepath: str, timeout: float = 5.0, delay: float = 0.05) -> None:
        self.lock_dir: str = filepath + ".lock"
        self.timeout: float = timeout
        self.delay: float = delay
        self.acquired: bool = False

    def __enter__(self) -> 'FileLockMutex':
        start_time: float = time.time()
        while time.time() - start_time < self.timeout:
            try:
                os.mkdir(self.lock_dir)
                self.acquired = True
                return self
            except FileExistsError:
                time.sleep(self.delay)
        raise TimeoutError(f"Could not acquire mutex lock on {self.lock_dir} within {self.timeout}s.")

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        if self.acquired:
            try:
                os.rmdir(self.lock_dir)
            except Exception:
                pass
            self.acquired = False

if __name__ == '__main__':
    main()

