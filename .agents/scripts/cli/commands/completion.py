import sys
from typing import List

RED = "\033[91m"
RESET = "\033[0m"

def print_err(msg: str) -> None:
    print(f"{RED}[FAIL] {msg}{RESET}", file=sys.stderr)

def get_bash_completion() -> str:
    return """# bash completion for Antigravity Agent Core (aac/helper.sh)
_aac_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    opts="lock validate sync issue commit bootstrap profile changelog learn skill doctor upgrade completion install-global ui"

    case "${prev}" in
        profile)
            COMPREPLY=( $(compgen -W "list switch add credential-helper" -- ${cur}) )
            return 0
            ;;
        issue)
            COMPREPLY=( $(compgen -W "create list checkout close sync" -- ${cur}) )
            return 0
            ;;
        skill)
            COMPREPLY=( $(compgen -W "list install uninstall" -- ${cur}) )
            return 0
            ;;
        completion)
            COMPREPLY=( $(compgen -W "bash zsh" -- ${cur}) )
            return 0
            ;;
        *)
            ;;
    esac

    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    return 0
}
complete -F _aac_completion aac
complete -F _aac_completion helper.sh
"""

def get_zsh_completion() -> str:
    return """#compdef aac helper.sh

_aac_completion() {
    local context state state_descr line
    typeset -A opt_args

    _arguments -C \
        '1: :->cmds' \
        '*:: :->args'

    case "$state" in
        cmds)
            _values "aac command" \
                'lock[Acquire module lock]' \
                'validate[Execute validation audits]' \
                'sync[Synchronize registries]' \
                'issue[Manage remote/local issues]' \
                'commit[Validate and commit changes]' \
                'bootstrap[Scaffold target project]' \
                'profile[Rotate Git credentials & profiles]' \
                'changelog[Generate auto-changelog and SemVer]' \
                'learn[Persist session learnings]' \
                'skill[Manage custom agent skills]' \
                'doctor[Run diagnostics audits]' \
                'upgrade[Upgrade core scripts]' \
                'completion[Generate tab-completion scripts]' \
                'install-global[Install global launcher alias]' \
                'ui[Launch local Web UI Dashboard]'
            ;;
        args)
            case "$words[1]" in
                profile)
                    _values "profile subcommand" \
                        'list[List registered profiles]' \
                        'switch[Switch active profile]' \
                        'add[Register a new profile]' \
                        'credential-helper[Git HTTPS credentials rotation]'
                    ;;
                issue)
                    _values "issue subcommand" \
                        'create[Create local issue]' \
                        'list[List active issues]' \
                        'checkout[Checkout feature branch]' \
                        'close[Commit changes and merge issue]' \
                        'sync[Sync remote issues]'
                    ;;
                skill)
                    _values "skill subcommand" \
                        'list[List installed skills]' \
                        'install[Install custom skill]' \
                        'uninstall[Uninstall custom skill]'
                    ;;
                completion)
                    _values "shell" \
                        'bash[Generate Bash completion]' \
                        'zsh[Generate Zsh completion]'
                    ;;
            esac
            ;;
    esac
}
"""

def get_powershell_completion() -> str:
    return """# PowerShell completion for Antigravity Agent Core (aac/helper.ps1)
$AacCompleter = {
    param($commandName, $parameterName, $wordToComplete, $commandAst, $fakeBoundParameters)
    
    $opts = @("lock", "validate", "sync", "issue", "commit", "bootstrap", "profile", "changelog", "learn", "skill", "doctor", "upgrade", "completion", "install-global", "ui")
    $profile_subcmds = @("list", "switch", "add", "credential-helper")
    $issue_subcmds = @("create", "list", "checkout", "close", "sync")
    $skill_subcmds = @("list", "install", "uninstall")
    $completion_subcmds = @("bash", "zsh", "powershell")
    
    $tokens = $commandAst.CommandElements
    if ($tokens.Count -le 1) {
        return
    }
    
    $cmdWord = $tokens[1].Value
    if ($tokens.Count -eq 2 -or ($tokens.Count -eq 3 -and $wordToComplete)) {
        # Completing the main command
        $opts | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
        }
    } elseif ($tokens.Count -eq 3 -or ($tokens.Count -eq 4 -and $wordToComplete)) {
        # Completing a subcommand
        $subcmds = @()
        if ($cmdWord -eq "profile") { $subcmds = $profile_subcmds }
        elseif ($cmdWord -eq "issue") { $subcmds = $issue_subcmds }
        elseif ($cmdWord -eq "skill") { $subcmds = $skill_subcmds }
        elseif ($cmdWord -eq "completion") { $subcmds = $completion_subcmds }
        
        $subcmds | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
        }
    }
}

Register-ArgumentCompleter -CommandName aac -ScriptBlock $AacCompleter
Register-ArgumentCompleter -CommandName helper.ps1 -ScriptBlock $AacCompleter
Register-ArgumentCompleter -CommandName .\\helper.ps1 -ScriptBlock $AacCompleter
"""

def run(args: List[str]) -> None:
    if not args:
        print("Usage: helper.py completion <bash|zsh|powershell>")
        sys.exit(1)
        
    shell = args[0].lower()
    if shell == "bash":
        print(get_bash_completion())
    elif shell == "zsh":
        print(get_zsh_completion())
    elif shell == "powershell":
        print(get_powershell_completion())
    else:
        print_err(f"Unsupported shell '{shell}'. Supported: bash, zsh, powershell")
        sys.exit(1)
        
    sys.exit(0)
