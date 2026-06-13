# Antigravity Agent Workspace Bootstrapper for Windows
# Wrapper script to execute bootstrap.sh inside Git Bash

param (
    [string]$Version = "main",
    [switch]$Force = $false,
    [switch]$Update = $false
)

$gitBash = "C:\Program Files\Git\bin\bash.exe"
if (-not (Test-Path $gitBash)) {
    $gitBash = (Get-Command bash.exe -ErrorAction SilentlyContinue).Source
}

if (-not $gitBash) {
    Write-Error "Git Bash is required to run Antigravity on Windows. Please install Git for Windows (https://git-scm.com/)."
    exit 1
}

# Collect and join any additional arguments to forward
$bashArgs = @()
if ($Force) {
    $bashArgs += "-f"
}
if ($Update) {
    $bashArgs += "-u"
}
if ($args) {
    $bashArgs += $args
}
$bashArgsStr = [string]::Join(" ", $bashArgs)

# If a local bootstrap.sh exists, run it. Otherwise, download it from GitHub.
if (Test-Path .\bootstrap.sh) {
    Write-Host "Running local bootstrap.sh via Git Bash..."
    & $gitBash -c "./bootstrap.sh $bashArgsStr"
} else {
    Write-Host "Downloading and running bootstrap.sh (version: $Version) via Git Bash..."
    & $gitBash -c "curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents/$Version/bootstrap.sh | bash -s -- $bashArgsStr"
}


# Self-cleanup if run from root and local bootstrap.ps1 exists (unless we are in the template development repository)
if (Test-Path .\bootstrap.ps1) {
    # If bootstrap.sh was copied and deleted itself, we should also delete bootstrap.ps1
    # Check if .agents directory was successfully created
    if (Test-Path .\.agents) {
        $isDev = $false
        if (Test-Path .\.git) {
            $origin = (git config --get remote.origin.url) 2>$null
            if ($origin -like "*antigravity-agents*") {
                $isDev = $true
            }
        }
        if (-not $isDev) {
            Write-Host "Cleaning up root bootstrapper script bootstrap.ps1..."
            Remove-Item .\bootstrap.ps1 -Force
        }
    }
}
