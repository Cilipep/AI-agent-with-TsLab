param(
    [Parameter(Mandatory=$true)]
    [string]$ScriptName
)

$ErrorActionPreference = "Stop"
$api = "http://localhost:5000/api"

Write-Host "=== TSLab Lifecycle: $ScriptName ===" -ForegroundColor Cyan

# Validate
Write-Host "[1/5] Validating..." -ForegroundColor Yellow
$valid = Invoke-RestMethod -Uri "$api/scripts/$ScriptName/validate" -Method POST -ContentType "application/json" -Body "{}" -ErrorAction Stop
if ($valid.data.isValid -ne $true) {
    Write-Host "  VALIDATION FAILED" -ForegroundColor Red
    $valid.data.errors | ConvertTo-Json -Depth 3
    exit 1
}
Write-Host "  Validate OK" -ForegroundColor Green

# Build
Write-Host "[2/5] Building..." -ForegroundColor Yellow
$build = Invoke-RestMethod -Uri "$api/scripts/$ScriptName/build" -Method POST -ContentType "application/json" -Body "{}" -ErrorAction Stop
if ($build.success -ne $true) { Write-Host "BUILD FAILED" -ForegroundColor Red; $build | ConvertTo-Json -Depth 3; exit 1 }
Write-Host "  Build OK" -ForegroundColor Green

Start-Sleep -Seconds 2

# Load
Write-Host "[3/5] Loading..." -ForegroundColor Yellow
$load = Invoke-RestMethod -Uri "$api/scripts/$ScriptName/load" -Method POST -ContentType "application/json" -Body "{}" -ErrorAction Stop
Write-Host "  Load OK" -ForegroundColor Green

Start-Sleep -Seconds 2

# Run
Write-Host "[4/5] Running..." -ForegroundColor Yellow
$run = Invoke-RestMethod -Uri "$api/scripts/$ScriptName/run" -Method POST -ContentType "application/json" -Body "{}" -ErrorAction Stop
Write-Host "  Run OK" -ForegroundColor Green

Start-Sleep -Seconds 3

# Metrics
Write-Host "[5/5] Metrics..." -ForegroundColor Yellow
$metrics = Invoke-RestMethod -Uri "$api/scripts/$ScriptName/metrics-summary" -Method GET -ErrorAction Stop
Write-Host "=== Results ===" -ForegroundColor Cyan
$metrics.data | Select-Object netProfit, allTrades, profitFactor, maxDrawdownPct | Format-Table -AutoSize