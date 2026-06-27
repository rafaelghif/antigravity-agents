import sys
import os
import importlib

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

{BOLD}Available Commands:{RESET}
  🚀 {GREEN}{BOLD}bootstrap{RESET}   Scaffolds directory structures & stack detection.
  ✅ {GREEN}{BOLD}validate{RESET}    Runs validation guard (audits secrets, board, linting, tests).
  🔄 {GREEN}{BOLD}sync{RESET}        Synchronizes skills index in AGENTS.md & ADR registry.
  🎫 {GREEN}{BOLD}issue{RESET}       Manages local task tracker issues (checkout, close, list).
  🔒 {GREEN}{BOLD}lock{RESET}        Acquires module locks to prevent concurrent modifications.
  👤 {GREEN}{BOLD}profile{RESET}     Configures/switches developer git commit identities.
  📝 {GREEN}{BOLD}changelog{RESET}   Generates conventional commit release notes & bumps SemVer.
  🧠 {GREEN}{BOLD}learn{RESET}       Records developer/agent lessons directly to lessons-learned.md.
  💬 {GREEN}{BOLD}commit{RESET}      Fires safe git commit command gated by validation guard.

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
  - Blocks commit if local validation guard fails."""
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
    
    if cmd in help_args:
        if len(sys.argv) > 2:
            sub_cmd = sys.argv[2].lower()
            print_command_help(sub_cmd)
        else:
            print_help()
        sys.exit(0)
        
    allowed_commands = {'lock', 'validate', 'sync', 'issue', 'commit', 'bootstrap', 'profile', 'changelog', 'learn'}
    
    if len(sys.argv) > 2 and sys.argv[2].lower() in help_args:
        print_command_help(cmd)
        sys.exit(0)
        
    if cmd not in allowed_commands:
        print(f"{RED}Error: Unknown command '{cmd}'.{RESET}")
        print_help()
        sys.exit(1)
        
    try:
        # Resolve command file path dynamically
        cmd_file = os.path.abspath(os.path.join(os.path.dirname(__file__), f"commands/{cmd}.py"))
        if not os.path.exists(cmd_file):
            print(f"{RED}Error: Command module file '{cmd_file}' not found.{RESET}")
            sys.exit(1)
            
        # Inject project root path into sys.path to resolve imports correctly
        root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
        if root_path not in sys.path:
            sys.path.insert(0, root_path)
            
        import importlib.util
        spec = importlib.util.spec_from_file_location(f"cmd_{cmd}", cmd_file)
        if spec is None or spec.loader is None:
            print(f"{RED}Error: Could not load command module spec for '{cmd}'.{RESET}")
            sys.exit(1)
        cmd_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cmd_module)
        if not hasattr(cmd_module, "run"):
            print(f"{RED}Error: Command module '{cmd}' does not implement required 'run(args)' method.{RESET}")
            sys.exit(1)
        cmd_module.run(sys.argv[2:])
    except Exception as e:
        print(f"{RED}Error executing command '{cmd}': {e}{RESET}")
        sys.exit(1)

if __name__ == '__main__':
    main()
