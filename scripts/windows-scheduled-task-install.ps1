param(
    [string]$TaskName = "EnterpriseIPAM",
    [int]$Port = 18000,
    [string]$RunAsUser = "",
    [switch]$StartNow
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

$pythonPath = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonPath)) {
    throw "Python virtual environment not found. Run .\scripts\windows-hyperv-init.ps1 first."
}

$logsDir = Join-Path $projectRoot "logs"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir | Out-Null
}

$stdoutLog = Join-Path $logsDir "scheduled-task-stdout.log"
$stderrLog = Join-Path $logsDir "scheduled-task-stderr.log"

$command = "`"$pythonPath`" -m uvicorn app.main:app --host 0.0.0.0 --port $Port >> `"$stdoutLog`" 2>> `"$stderrLog`""
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -WindowStyle Hidden -Command $command"
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -StartWhenAvailable

try {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction Stop
}
catch {
}

if ([string]::IsNullOrWhiteSpace($RunAsUser)) {
    $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
}
else {
    $principal = New-ScheduledTaskPrincipal -UserId $RunAsUser -LogonType Password -RunLevel Highest
}

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "Enterprise IPAM startup task"

if ($StartNow) {
    Start-ScheduledTask -TaskName $TaskName
}

Write-Host ""
Write-Host "Scheduled task installed."
Write-Host "Task Name   : $TaskName"
Write-Host "Port        : $Port"
Write-Host "Stdout Log  : $stdoutLog"
Write-Host "Stderr Log  : $stderrLog"
Write-Host ""
Write-Host "Check with: Get-ScheduledTask -TaskName $TaskName"
Write-Host "Start with: Start-ScheduledTask -TaskName $TaskName"

