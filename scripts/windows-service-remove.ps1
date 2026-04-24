param(
    [string]$ServiceName = "EnterpriseIPAM",
    [string]$NssmPath = "C:\tools\nssm\nssm.exe"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not (Test-Path $NssmPath)) {
    throw "nssm.exe not found at $NssmPath."
}

& $NssmPath stop $ServiceName | Out-Null
& $NssmPath remove $ServiceName confirm

Write-Host ""
Write-Host "Windows Service removed: $ServiceName"

