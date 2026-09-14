[Console]::InputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$inputJson = [Console]::In.ReadToEnd()
if ([string]::IsNullOrWhiteSpace($inputJson)) {
    Write-Output '{"decision":"allow"}'
    exit 0
}

try {
    $payload = $inputJson | ConvertFrom-Json
    $command = $payload.toolCall.args.CommandLine
} catch {
    Write-Output '{"decision":"allow"}'
    exit 0
}

if (-not $command) {
    Write-Output '{"decision":"allow"}'
    exit 0
}

$dangerousPatterns = @(
    '\bgit\s+push\b',
    '\bgit\s+reset\s+--hard\b',
    '\bgit\s+clean\s+(-[a-zA-Z]*f[a-zA-Z]*)\b',
    '\bgit\s+branch\s+-D\b',
    '\bgit\s+checkout\s+\.',
    '\bgit\s+restore\s+\.',
    '--force',
    'reset\s+--hard'
)

foreach ($pattern in $dangerousPatterns) {
    if ($command -match $pattern) {
        $result = @{
            decision = "deny"
            reason   = "BLOCKED: '$command' matches dangerous git pattern '$pattern'. Execution blocked by Antigravity git-guardrails."
        } | ConvertTo-Json -Compress
        Write-Output $result
        exit 0
    }
}

Write-Output '{"decision":"allow"}'
exit 0
