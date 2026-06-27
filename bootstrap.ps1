# Bootstrap Antigravity Agent Core (AAC) V2 for Windows PowerShell
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Bootstrapping Antigravity Agent Core (AAC) V2...   " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Create directories
$Dirs = @(
    ".agents/memory/decisions",
    ".agents/tasks",
    ".agents/issues"
)

foreach ($Dir in $Dirs) {
    if (-not (Test-Path $Dir)) {
        New-Item -ItemType Directory -Force -Path $Dir | Out-Null
    }
}

# 1.1 Copy template memory files
$SrcTemplates = ".agents/memory/templates"
if (Test-Path $SrcTemplates) {
    $Templates = Get-ChildItem -Path $SrcTemplates -Filter "*.template"
    foreach ($T in $Templates) {
        $DestName = $T.BaseName
        $DestPath = ".agents/memory/$DestName"
        if (-not (Test-Path $DestPath)) {
            Copy-Item -Path $T.FullName -Destination $DestPath -Force | Out-Null
        }
    }
}

# 2. Synchronize Version if AGENTS.md exists
if (Test-Path "AGENTS.md") {
    if (Get-Command python -ErrorAction SilentlyContinue) {
        python -c "import re, os; f=open('AGENTS.md', 'r', encoding='utf-8'); content=f.read(); f.close(); content=re.sub(r'-\s+\*\*Version:\*\*.*', '- **Version:** 2.46.0', content) if '- **Version:**' in content else re.sub(r'(-\s+\*\*Product:\*\*.*)', r'\1\n- **Version:** 2.46.0', content); f=open('AGENTS.md', 'w', encoding='utf-8'); f.write(content); f.close()" | Out-Null
        Write-Host "Synchronized AGENTS.md version."
    } elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
        python3 -c "import re, os; f=open('AGENTS.md', 'r', encoding='utf-8'); content=f.read(); f.close(); content=re.sub(r'-\s+\*\*Version:\*\*.*', '- **Version:** 2.46.0', content) if '- **Version:**' in content else re.sub(r'(-\s+\*\*Product:\*\*.*)', r'\1\n- **Version:** 2.46.0', content); f=open('AGENTS.md', 'w', encoding='utf-8'); f.write(content); f.close()" | Out-Null
        Write-Host "Synchronized AGENTS.md version."
    }
}

# 3. Trigger auto-reconnaissance
if (Test-Path ".agents/scripts/recon.py") {
    Write-Host "Running auto-reconnaissance scan..."
    if (Get-Command python -ErrorAction SilentlyContinue) {
        python .agents/scripts/recon.py
    } elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
        python3 .agents/scripts/recon.py
    } else {
        Write-Host "Warning: Python not found. Please run .agents/scripts/recon.py manually after installing Python." -ForegroundColor Yellow
    }
} else {
    Write-Host "Warning: .agents/scripts/recon.py not found. Skipping auto-reconnaissance." -ForegroundColor Yellow
}

# 4. Set up local Git hooks
if (Test-Path ".git") {
    $PreCommitContent = @"
#!/usr/bin/env bash
if command -v python3 &>/dev/null; then
  python3 .agents/scripts/validate.py
elif command -v python &>/dev/null; then
  python .agents/scripts/validate.py
else
  echo "Warning: Python not found. Skipping commit validation check."
fi
"@
    $PreCommitPath = [System.IO.Path]::GetFullPath(".git/hooks/pre-commit")
    [System.IO.File]::WriteAllText($PreCommitPath, $PreCommitContent.Replace("`r`n", "`n"))
    Write-Host "Installed local Git pre-commit hook."

    $CommitMsgContent = @"
#!/usr/bin/env bash
COMMIT_MSG_FILE="`$1"
COMMIT_MSG=`$(cat "`$COMMIT_MSG_FILE")
CONVENTIONAL_REGEX="^(feat|fix|chore|refactor|docs|test|style|perf|ci)(\([a-z0-9_-]+\))?: .+"

if [[ ! "`$COMMIT_MSG" =~ `$CONVENTIONAL_REGEX ]]; then
  echo "=========================================================="
  echo "[FAIL] Non-compliant commit message format!"
  echo "=========================================================="
  echo "Commit messages must follow Conventional Commits standard:"
  echo "  Format: <type>(<scope>): <subject>"
  echo "  Example: feat(auth): add login endpoint"
  echo "=========================================================="
  exit 1
fi

ID_REGEX="(task-|issue-|chore-)[a-zA-Z0-9_-]+"
if [[ ! "`$COMMIT_MSG" =~ `$ID_REGEX ]]; then
  echo "=========================================================="
  echo "[FAIL] Missing Task/Issue ID reference!"
  echo "=========================================================="
  echo "Commit messages must include an active task or issue ID reference."
  echo "  Example body: Task ID: issue-123"
  echo "=========================================================="
  exit 1
fi
"@
    $CommitMsgPath = [System.IO.Path]::GetFullPath(".git/hooks/commit-msg")
    [System.IO.File]::WriteAllText($CommitMsgPath, $CommitMsgContent.Replace("`r`n", "`n"))
    Write-Host "Installed local Git commit-msg hook."
}

Write-Host "==========================================================" -ForegroundColor Green
Write-Host "   AAC V2 Bootstrap Completed Successfully!             " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
