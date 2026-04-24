param(
    [string]$TaskName = "EnterpriseIPAM"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

try {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction Stop
    Write-Host ""
    Write-Host "Scheduled task removed: $TaskName"
}
catch {
    Write-Host ""
    Write-Host "Scheduled task not found: $TaskName"
}

