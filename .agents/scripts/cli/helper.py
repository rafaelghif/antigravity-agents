#!/usr/bin/env python3
import sys
import os

# Ensure the cli directory is in the import path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def show_help():
    print("==========================================================")
    print("  Antigravity Agent Core Helper CLI (Python Edition)")
    print("==========================================================")
    print("Usage: helper.py <command> [arguments...]")
    print("")
    print("Core Commands:")
    print("  lock              Acquire a module edit lock (transient lock)")
    print("  unlock            Release a module edit lock")
    print("  validate          Validate workspace compliance, budget, and configurations")
    print("  doctor            Run complete diagnostic validation on the workspace")
    print("  migrate           Upgrade workspaces to V1.9.0 format")
    print("  push              Push local branch to remote repository securely")
    print("  git-profile       Switch Git user config profiles locally")
    print("  api-profile       Switch API configurations locally (use 'rotate' to rotate)")
    print("  log-usage         Log token usage to budget tracker")
    print("  archive           Archive completed sprint checklists to history")
    print("  recon             Run autonomous codebase stack discovery")
    print("  list-skills       List all registered modular skills")
    print("  create-skill      Scaffold a new skill structure")
    print("  list-rules        List all project-specific blueprints and rules")
    print("  create-rule       Scaffold a new project rule blueprint")
    print("  init              Initialize a new workspace with template blueprints")
    print("  autocomplete      Output shell completion code (bash/zsh)")
    print("  adr-wizard        Interactive guided ADR wizard")
    print("  guide             Print step-by-step developer onboarding tutorial")
    print("==========================================================")
    print("Tip: Run 'helper.py guide' for a quick step-by-step developer tutorial!")
    print("==========================================================")

def main():
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
        
    cmd = sys.argv[1]
    
    cmd_map = {
        "lock": "lock",
        "unlock": "lock",
        "validate": "validate",
        "doctor": "doctor",
        "migrate": "migrate",
        "push": "push",
        "git-profile": "git_profile",
        "api-profile": "api_profile",
        "log-usage": "log_usage",
        "archive": "archive",
        "recon": "recon",
        "list-skills": "skills",
        "create-skill": "skills",
        "list-rules": "rules",
        "create-rule": "rules",
        "init": "init",
        "commit": "commit",
        "sync-git": "sync_git",
        "build": "build",
        "lint": "lint",
        "test": "test",
        "sync-api": "sync_api",
        "create-adr": "create_adr",
        "adr-wizard": "adr_wizard",
        "release": "release",
        "autocomplete": "autocomplete",
        "guide": "guide"
    }
    
    if cmd not in cmd_map:
        print(f"Unknown command: '{cmd}'", file=sys.stderr)
        show_help()
        sys.exit(1)
        
    module_name = cmd_map[cmd]
    try:
        # Import the command module dynamically
        cmd_module = __import__(f"commands.{module_name}", fromlist=[module_name])
        # Execute the module's main function
        cmd_module.run(sys.argv[1:])
    except ImportError as e:
        print(f"Failed to load command '{cmd}': {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error executing command '{cmd}': {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
