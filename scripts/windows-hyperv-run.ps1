param(
    [int]$Port = 18000
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    throw "Virtual environment not found. Run .\scripts\windows-hyperv-init.ps1 first."
}

& ".\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port $Port

