# Human-in-the-loop reproduction loop for Windows PowerShell.
# Copy this file, edit the steps below, and run it.
# The agent runs the script; the user follows prompts in their terminal.
#
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File hitl-loop.template.ps1

function Step([string]$instruction) {
    Write-Host "`n>>> $instruction" -ForegroundColor Cyan
    Read-Host "    [Press Enter when done]"
}

function Capture([string]$question) {
    Write-Host "`n>>> $question" -ForegroundColor Yellow
    return Read-Host "    > "
}

# --- edit below ---------------------------------------------------------

Step "Open the app at http://localhost:3000 and sign in."

$ERRORED = Capture "Click the 'Export' button. Did it throw an error? (y/n)"
$ERROR_MSG = Capture "Paste the error message (or 'none'):"

# --- edit above ---------------------------------------------------------

Write-Host "`n--- Captured ---" -ForegroundColor Green
Write-Host "ERRORED=$ERRORED"
Write-Host "ERROR_MSG=$ERROR_MSG"
