# Antigravity Agent Workspace Helper Wrapper for Windows PowerShell
# Forwards arguments to helper.sh running inside Git Bash and auto-loads API keys if dot-sourced.

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

# Detect if the script was run with api-profile subcommand
$isApiProfile = $args -and ($args[0] -eq "api-profile")

if ($isApiProfile) {
    $activeKeysFile = Join-Path (Split-Path $scriptPath) "active_api_keys.ps1"
    
    # Check if script is dot-sourced
    $isDotSourced = $MyInvocation.InvocationName -eq '.' -or $MyInvocation.InvocationName -eq '..'
    
    if ($isDotSourced) {
        if (Test-Path $activeKeysFile) {
            Write-Host "[INFO] Auto-loading active API keys into PowerShell session..."
            . $activeKeysFile
        }
    } else {
        if (Test-Path $activeKeysFile) {
            Write-Host ""
            Write-Host "[INFO] To load these keys into your current PowerShell session, run:" -ForegroundColor Cyan
            Write-Host "       . .agents/active_api_keys.ps1" -ForegroundColor Yellow
            Write-Host ""
        }
    }
}
