import sys

def get_bash_completion():
    return """_helper_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    opts="lock unlock validate doctor migrate git-profile api-profile log-usage archive recon list-skills create-skill list-rules create-rule init commit sync-git build lint test sync-api create-adr release"

    if [[ ${cur} == * ]] ; then
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi
}
complete -F _helper_completion helper.sh
complete -F _helper_completion ./.agents/scripts/helper.sh
"""

def get_zsh_completion():
    return """#compdef helper.sh ./.agents/scripts/helper.sh

_helper_completion() {
    local -a commands
    commands=(
        'lock:Acquire a module edit lock'
        'unlock:Release a module edit lock'
        'validate:Validate workspace compliance, budget, and configurations'
        'doctor:Run complete diagnostic validation on the workspace'
        'migrate:Upgrade workspaces to V1.7.4 format'
        'git-profile:Switch Git user config profiles locally'
        'api-profile:Switch API configurations locally'
        'log-usage:Log token usage to budget tracker'
        'archive:Archive completed sprint checklists to history'
        'recon:Run autonomous codebase stack discovery'
        'list-skills:List all registered modular skills'
        'create-skill:Scaffold a new skill structure'
        'list-rules:List all project-specific blueprints and rules'
        'create-rule:Scaffold a new project rule blueprint'
        'init:Initialize a new workspace with template blueprints'
        'commit:Execute conventional commit and verification checks'
        'sync-git:Synchronize local repository configuration with Git'
        'build:Run project build verification'
        'lint:Run project workspace linter'
        'test:Run project unit tests'
        'sync-api:Synchronize API schemas and configurations'
        'create-adr:Create a new Architectural Decision Record'
        'release:Perform a project semantic release bump'
    )
    _describe -t commands 'helper command' commands
}

_helper_completion "$@"
"""

def run(args):
    if len(args) < 2:
        print("Usage: helper.sh autocomplete [bash|zsh]")
        print("To load autocomplete, run:")
        print("  source <(./.agents/scripts/helper.sh autocomplete bash)")
        sys.exit(1)
        
    shell = args[1].lower()
    if shell == "bash":
        print(get_bash_completion())
    elif shell == "zsh":
        print(get_zsh_completion())
    else:
        print(f"Unsupported shell: {shell}. Only 'bash' and 'zsh' are supported.", file=sys.stderr)
        sys.exit(1)
