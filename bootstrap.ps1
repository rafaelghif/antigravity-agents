# Antigravity Agent Workspace Bootstrapper for Windows
# Wrapper script to execute bootstrap.sh inside Git Bash

$gitBash = "C:\Program Files\Git\bin\bash.exe"
if (-not (Test-Path $gitBash)) {
    $gitBash = (Get-Command bash.exe -ErrorAction SilentlyContinue).Source
}

if (-not $gitBash) {
    Write-Error "Git Bash is required to run Antigravity on Windows. Please install Git for Windows (https://git-scm.com/)."
    exit 1
}

# If a local bootstrap.sh exists, run it. Otherwise, download it from GitHub.
if (Test-Path .\bootstrap.sh) {
    Write-Host "Running local bootstrap.sh via Git Bash..."
    & $gitBash -c "./bootstrap.sh"
} else {
    Write-Host "Downloading and running bootstrap.sh via Git Bash..."
    & $gitBash -c "curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/bootstrap.sh | bash"
}

# Self-cleanup if run from root and local bootstrap.ps1 exists
if (Test-Path .\bootstrap.ps1) {
    # If bootstrap.sh was copied and deleted itself, we should also delete bootstrap.ps1
    # Check if .agents directory was successfully created
    if (Test-Path .\.agents) {
        Write-Host "Cleaning up root bootstrapper script bootstrap.ps1..."
        Remove-Item .\bootstrap.ps1 -Force
    }
}
