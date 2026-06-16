# Antigravity API Auto-Rotation Command Wrapper for Windows PowerShell
# Wraps execution of any PowerShell script or command, automatically rotating API profiles 
# from '.agents/api_keys' if the command fails with a rate-limit error (exit code 429).
param(
    [Parameter(Mandatory=$true, ValueFromRemainingArguments=$true)]
    [string[]]$Command
)

# Find the helper script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$helperPs1 = Join-Path $scriptPath "helper.ps1"

# Find available API profiles to count max retries
$apiKeysFile = ""
if (Test-Path ".agents/api_keys") {
    $apiKeysFile = ".agents/api_keys"
} elseif (Test-Path "$HOME/.antigravity_api_keys") {
    $apiKeysFile = "$HOME/.antigravity_api_keys"
}

$maxRetries = 1
if ($apiKeysFile -and (Test-Path $apiKeysFile)) {
    # Count unique profiles from key prefix (e.g. name.VAR=val)
    $profiles = Get-Content $apiKeysFile | Where-Object { $_ -match '^[a-zA-Z0-9_\-]+\.[A-Z0-9_]+=' } | ForEach-Object {
        $_.Split('.')[0].Trim()
    } | Select-Object -Unique
    if ($profiles) {
        $maxRetries = @($profiles).Count
    }
}

$retryCount = 0
$success = $false

while ($retryCount -lt $maxRetries) {
    # Ensure active API keys are loaded in current process env
    $activeKeysFile = Join-Path (Split-Path $scriptPath) "active_api_keys.ps1"
    if (Test-Path $activeKeysFile) {
        . $activeKeysFile
    } else {
        # If no profile is active, initialize the first available profile
        Write-Host "No active API profile set. Initializing first available profile..."
        & $helperPs1 api-profile rotate | Out-Null
        if (Test-Path $activeKeysFile) {
            . $activeKeysFile
        }
    }

    Write-Host "[API-WRAPPER] Running wrapped command..."
    
    # Disable exit on error behavior during execution
    $exitCode = 0
    try {
        if ($Command.Count -gt 1) {
            & $Command[0] $Command[1..($Command.Count - 1)]
        } else {
            & $Command[0]
        }
        $exitCode = $LASTEXITCODE
    } catch {
        Write-Warning "Failed to execute command: $_"
        $exitCode = 1
    }

    if ($exitCode -eq 0 -or $null -eq $exitCode) {
        exit 0
    # Catch typical rate limit / exhaustion codes: 
    # - 429: Too Many Requests
    # - 129: Common custom agent rate-limit exit code
    # - 3: Resource exhausted (gRPC status code)
    } elseif ($exitCode -eq 429 -or $exitCode -eq 129 -or $exitCode -eq 173 -or $exitCode -eq 3) {
        $retryCount++
        if ($retryCount -lt $maxRetries) {
            Write-Warning "[API-WRAPPER] Command exited with code $exitCode (Rate Limited/Quota Exhausted)."
            Write-Host "[API-WRAPPER] Rotating API profile and retrying ($retryCount/$maxRetries)..."
            & $helperPs1 api-profile rotate --rate-limited
            Start-Sleep -Seconds 1
        } else {
            Write-Error "[API-WRAPPER] Command exited with code $exitCode. All available API profiles exhausted."
            exit $exitCode
        }
    } else {
        # Exit immediately on other execution failures
        exit $exitCode
    }
}
