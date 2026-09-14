# Repository health check sidecar for Google Antigravity
# Periodically monitors git branch cleanliness and reports status.

$status = git status --porcelain 2>$null
if ($LASTEXITCODE -eq 0) {
    if ([string]::IsNullOrWhiteSpace($status)) {
        Write-Output "HealthCheck: Working tree clean."
    } else {
        $count = ($status -split "`n").Count
        Write-Output "HealthCheck: $count uncommitted changes detected."
    }
} else {
    Write-Output "HealthCheck: Not inside a git repository or git command failed."
}
