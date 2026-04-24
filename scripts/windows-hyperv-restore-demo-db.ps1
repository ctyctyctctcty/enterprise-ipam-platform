param(
    [string]$TargetDb = "enterprise_ipam_server.db"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

$sourceDb = Join-Path $projectRoot "demo\enterprise_ipam_demo_seed.db"
$targetPath = Join-Path $projectRoot $TargetDb

if (-not (Test-Path $sourceDb)) {
    throw "Demo seed database not found at $sourceDb"
}

Copy-Item $sourceDb $targetPath -Force

if (Test-Path ".\.env") {
    $envContent = Get-Content ".\.env" -Raw
    $updated = $envContent -replace "DATABASE_URL=.*", "DATABASE_URL=sqlite:///./$TargetDb"
    Set-Content ".\.env" $updated
}

Write-Host ""
Write-Host "Demo seed database restored to $targetPath"
Write-Host "If .env exists, DATABASE_URL was updated to use $TargetDb"
Write-Host "You can now start the server with .\scripts\windows-hyperv-run.ps1"

