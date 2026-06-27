# Windows PowerShell wrapper for Antigravity Agent Core CLI

if (Get-Command python -ErrorAction SilentlyContinue) {
    python .agents/scripts/cli/helper.py $args
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    python3 .agents/scripts/cli/helper.py $args
} else {
    Write-Error "Error: Python 3 runtime is required to execute Antigravity CLI commands."
    Exit 1
}
