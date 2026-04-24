Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

if (-not (Test-Path ".\.venv")) {
    py -m venv .venv
}

& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt

if (-not (Test-Path ".\.env")) {
    Copy-Item ".\.env.hyperv.example" ".\.env"
}

& ".\.venv\Scripts\python.exe" -m alembic upgrade head
& ".\.venv\Scripts\python.exe" ".\scripts\init_db.py"

Write-Host ""
Write-Host "Hyper-V Windows server initialization complete."
Write-Host "Review .env before exposing the service to colleagues."
Write-Host "Start with: .\scripts\windows-hyperv-run.ps1"

