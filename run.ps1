# Media Downloader — PowerShell launcher
# Works on Windows PowerShell 5.1+ and PowerShell 7+ (cross-platform)

Set-Location $PSScriptRoot

# --- Check Python -----------------------------------------------------------
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Host "[ERROR] Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host "        Download from https://www.python.org/downloads/"
    Read-Host  "Press Enter to exit"
    exit 1
}

# --- Create venv if missing --------------------------------------------------
$venvPython = if ($IsLinux -or $IsMacOS) { ".venv/bin/python" } else { ".venv\Scripts\python.exe" }
$venvPip    = if ($IsLinux -or $IsMacOS) { ".venv/bin/pip"    } else { ".venv\Scripts\pip.exe"    }

if (-not (Test-Path $venvPython)) {
    Write-Host "[*] Creating virtual environment..."
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to create virtual environment." -ForegroundColor Red
        Read-Host  "Press Enter to exit"
        exit 1
    }
}

# --- Install / update dependencies -------------------------------------------
Write-Host "[*] Checking dependencies..."
& $venvPip install -q -r requirements.txt

# --- Launch ------------------------------------------------------------------
Write-Host "[*] Starting Media Downloader..."
& $venvPython main.py
