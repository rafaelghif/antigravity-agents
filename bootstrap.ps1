# Bootstrap Antigravity Agent Core (AAC) V3 for Windows PowerShell
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Bootstrapping Antigravity Agent Core (AAC) V3...   " -ForegroundColor Cyan
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

# 1.2 Detect Python 3 executable
$PythonExec = ""
$OldPreference = $ErrorActionPreference
$ErrorActionPreference = "SilentlyContinue"
try {
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $Version = [string](& python --version 2>&1)
        if ($Version -match "Python 3") {
            $PythonExec = "python"
        }
    }
    if (-not $PythonExec -and (Get-Command python3 -ErrorAction SilentlyContinue)) {
        $Version = [string](& python3 --version 2>&1)
        if ($Version -match "Python 3") {
            $PythonExec = "python3"
        }
    }
} catch {}
$ErrorActionPreference = $OldPreference

# 2. Synchronize Version if AGENTS.md exists
if ((Test-Path "AGENTS.md") -and $PythonExec) {
    & $PythonExec -c "import re, os; f=open('AGENTS.md', 'r', encoding='utf-8'); content=f.read(); f.close(); content=re.sub(r'-\s+\*\*Version:\*\*.*', '- **Version:** 3.2.1', content) if '- **Version:**' in content else re.sub(r'(-\s+\*\*Product:\*\*.*)', r'\1\n- **Version:** 3.2.1', content); f=open('AGENTS.md', 'w', encoding='utf-8'); f.write(content); f.close()" | Out-Null
    Write-Host "Synchronized AGENTS.md version."
}

# 3. Trigger auto-reconnaissance
if (Test-Path ".agents/scripts/recon.py") {
    Write-Host "Running auto-reconnaissance scan..."
    if ($PythonExec) {
        & $PythonExec .agents/scripts/recon.py
    } else {
        Write-Host "Warning: Python 3 not found. Please run .agents/scripts/recon.py manually after installing Python 3." -ForegroundColor Yellow
    }
} else {
    Write-Host "Warning: .agents/scripts/recon.py not found. Skipping auto-reconnaissance." -ForegroundColor Yellow
}

# 4. Set up local Git hooks via validate.py
$IsGit = $false
try {
    $OldPref = $ErrorActionPreference
    $ErrorActionPreference = "SilentlyContinue"
    $GitCheck = & git rev-parse --is-inside-work-tree 2>&1
    $ErrorActionPreference = $OldPref
    if ($LASTEXITCODE -eq 0 -and $GitCheck -eq "true") {
        $IsGit = $true
    }
} catch {}

if ($IsGit) {
    if ($PythonExec) {
        Write-Host "Installing and validating local Git hooks..."
        $HelperScript = ".agents/scripts/validate.py"
        $OldPref = $ErrorActionPreference
        $ErrorActionPreference = "SilentlyContinue"
        & $PythonExec $HelperScript 2>$null | Out-Null
        $ErrorActionPreference = $OldPref
        Write-Host "Installed local Git hooks."
    } else {
        Write-Host "Warning: Python 3 not found. Skipping Git hooks auto-installation." -ForegroundColor Yellow
    }
}

# 5. Run the python bootstrap setup wizard
if ($PythonExec -and (Test-Path ".agents/scripts/cli/helper.py")) {
    Write-Host "Running project setup wizard..."
    $OldPref = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    & $PythonExec .agents/scripts/cli/helper.py bootstrap @args
    $ErrorActionPreference = $OldPref
}

Write-Host "==========================================================" -ForegroundColor Green
Write-Host "   AAC V3 Bootstrap Completed Successfully!             " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
