# Antigravity Agent Workspace Helper Wrapper for Windows PowerShell
# Forwards arguments to helper.sh running inside Git Bash

$gitBash = "C:\Program Files\Git\bin\bash.exe"
if (-not (Test-Path $gitBash)) {
    $gitBash = (Get-Command bash.exe -ErrorAction SilentlyContinue).Source
}

if (-not $gitBash) {
    Write-Error "Git Bash is required to run Antigravity helper scripts on Windows. Please install Git for Windows (https://git-scm.com/)."
    exit 1
}

# Resolve target helper.sh script path relative to this script
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$helperSh = Join-Path $scriptPath "helper.sh"

# Format target path for Bash environment (ensure Unix style slashes)
$helperShUnix = $helperSh.Replace('\', '/')

# Execute helper.sh inside Git Bash, forwarding all arguments exactly
if ($args) {
    & $gitBash $helperShUnix @args
} else {
    & $gitBash $helperShUnix
}
