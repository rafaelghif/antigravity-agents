import sys
import utils

# ANSI color codes
C_HEADER = '\033[95m'
C_BLUE = '\033[94m'
C_CYAN = '\033[96m'
C_GREEN = '\033[92m'
C_YELLOW = '\033[93m'
C_BOLD = '\033[1m'
C_END = '\033[0m'

def color(text, ansi_code):
    if sys.stdout.isatty():
        return f"{ansi_code}{text}{C_END}"
    return text

def run(args):
    print(color("=====================================================================", C_BLUE))
    print(color("   🚀 Welcome to Antigravity Agent Core Onboarding Guide 🚀", C_BOLD + C_HEADER))
    print(color("=====================================================================", C_BLUE))
    print("Antigravity Agent Core (AAC) is a developer protocol and workspace")
    print("layout designed to coordinate human-agent pair-programming safely,")
    print("cost-effectively, and securely.")
    print("")
    
    print(color("💡 THE 3-STEP DAILY WORKFLOW FOR DEVELOPERS & AGENTS", C_BOLD + C_CYAN))
    print(color("---------------------------------------------------------------------", C_BLUE))
    print("When modifying code in this workspace, follow this atomic sequence:")
    print("")
    
    print(f"{color('1. LOCK', C_BOLD + C_GREEN)} the module you want to edit:")
    print(f"   $ {color('./.agents/scripts/helper.sh lock <module-directory>', C_CYAN)}")
    print(f"   Example: {color('./.agents/scripts/helper.sh lock cli', C_GRAY if not sys.stdout.isatty() else '\033[90m')}")
    print("   (This tells other developers/agents not to modify this module.)")
    print("")
    
    print(f"{color('2. WRITE', C_BOLD + C_GREEN)} your code and tests (TDD is highly recommended).")
    print("")
    
    print(f"{color('3. COMMIT', C_BOLD + C_GREEN)} your changes using the helper commit command:")
    print(f"   $ {color('./.agents/scripts/helper.sh commit <type> <scope> \"description\" [files...]', C_CYAN)}")
    print(f"   Example: {color('./.agents/scripts/helper.sh commit feat cli \"add push subcommand\"', C_GRAY if not sys.stdout.isatty() else '\033[90m')}")
    print("   (This runs validation checks, rotates SSH keys/Git profiles, commits,")
    print("   and automatically releases your lock).")
    print("")
    
    print(color("🩺 KEY DIAGNOSTICS & SYSTEM COMMANDS", C_BOLD + C_CYAN))
    print(color("---------------------------------------------------------------------", C_BLUE))
    
    print(f"- {color('Run Health Checks', C_BOLD)}: {color('./.agents/scripts/helper.sh doctor', C_CYAN)}")
    print("  (Checks Git hooks, execution permissions, and workspace validation status.)")
    print("")
    
    print(f"- {color('Validate Compliance', C_BOLD)}: {color('./.agents/scripts/helper.sh validate', C_CYAN)}")
    print("  (Audits workspace for hardcoded secrets, environment purity, and budget limits.)")
    print("")
    
    print(f"- {color('Setup Profile Rotation', C_BOLD)}: {color('./.agents/scripts/helper.sh git-profile', C_CYAN)}")
    print("  (Manages multiple local git config identities and rotates SSH key bindings.)")
    print("")
    
    print(color("📚 DOCUMENTATION & RESOURCES", C_BOLD + C_CYAN))
    print(color("---------------------------------------------------------------------", C_BLUE))
    print("Detailed guides are located inside the root 'docs/' directory:")
    print(f"- Setup Guide:        {color('docs/setup_guide.md', C_GREEN)}")
    print(f"- CLI Reference:      {color('docs/cli_guide.md', C_GREEN)}")
    print(f"- Agent Workflows:    {color('docs/agent_workflow.md', C_GREEN)}")
    print(f"- Directory Layout:   {color('docs/directory_blueprint.md', C_GREEN)}")
    print(color("=====================================================================", C_BLUE))
