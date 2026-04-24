param(
    [string]$ServiceName = "EnterpriseIPAM",
    [string]$DisplayName = "Enterprise IPAM Service",
    [string]$Description = "Enterprise IPAM internal platform service",
    [int]$Port = 18000,
    [string]$NssmPath = "C:\tools\nssm\nssm.exe"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

$pythonPath = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonPath)) {
    throw "Python virtual environment not found. Run .\scripts\windows-hyperv-init.ps1 first."
}

if (-not (Test-Path $NssmPath)) {
    throw "nssm.exe not found at $NssmPath. Download NSSM first, then rerun this script with -NssmPath."
}

$logsDir = Join-Path $projectRoot "logs"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir | Out-Null
}

$stdoutLog = Join-Path $logsDir "service-stdout.log"
$stderrLog = Join-Path $logsDir "service-stderr.log"
$arguments = "-m uvicorn app.main:app --host 0.0.0.0 --port $Port"

& $NssmPath stop $ServiceName | Out-Null
& $NssmPath remove $ServiceName confirm | Out-Null

& $NssmPath install $ServiceName $pythonPath $arguments
& $NssmPath set $ServiceName AppDirectory $projectRoot
& $NssmPath set $ServiceName DisplayName $DisplayName
& $NssmPath set $ServiceName Description $Description
& $NssmPath set $ServiceName Start SERVICE_AUTO_START
& $NssmPath set $ServiceName AppStdout $stdoutLog
& $NssmPath set $ServiceName AppStderr $stderrLog
& $NssmPath set $ServiceName AppRotateFiles 1
& $NssmPath set $ServiceName AppRotateOnline 1
& $NssmPath set $ServiceName AppRotateBytes 10485760

Start-Service -Name $ServiceName

Write-Host ""
Write-Host "Windows Service installed and started."
Write-Host "Service Name : $ServiceName"
Write-Host "Port         : $Port"
Write-Host "NSSM         : $NssmPath"
Write-Host "Stdout Log   : $stdoutLog"
Write-Host "Stderr Log   : $stderrLog"
Write-Host ""
Write-Host "Check status with: Get-Service $ServiceName"

