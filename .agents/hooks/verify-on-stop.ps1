[Console]::InputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$inputJson = [Console]::In.ReadToEnd()

# Default to allow if no input or parsing failure
if ([string]::IsNullOrWhiteSpace($inputJson)) {
    Write-Output '{"decision":"allow"}'
    exit 0
}

try {
    $payload = $inputJson | ConvertFrom-Json
} catch {
    Write-Output '{"decision":"allow"}'
    exit 0
}

# Run quality checks only on model stop
if ($payload.terminationReason -eq "model_stop") {
    $rootDir = if ($payload.workspacePaths -and $payload.workspacePaths.Count -gt 0) { $payload.workspacePaths[0] } else { Split-Path -Parent $PSScriptRoot }
    $testFile = Join-Path $rootDir "tests/memory-system.test.mjs"
    if (Test-Path $testFile) {
        Push-Location $rootDir
        try {
            $testOutput = node --test tests/memory-system.test.mjs 2>&1
            if ($LASTEXITCODE -ne 0) {
                $result = @{
                    decision = "continue"
                    reason   = "Quality Gate Failed: Unit tests in tests/memory-system.test.mjs are failing. Please fix regressions before concluding."
                } | ConvertTo-Json -Compress
                Write-Output $result
                exit 0
            }
        } finally {
            Pop-Location
        }
    }
}

Write-Output '{"decision":"allow"}'
exit 0
