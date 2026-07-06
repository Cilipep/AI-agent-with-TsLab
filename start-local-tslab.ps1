$ErrorActionPreference = "Stop"
$tslabExe = "C:\Program Files\TSLab\TSLab 3.0\TSLabConsole.exe"
$workDir = "C:\Program Files\TSLab\TSLab 3.0"
$api = "http://localhost:5000/api"

# Check if already running
$existing = Get-Process -Name "TSLab*" -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "TSLab already running (PID $($existing[0].Id)). Checking API..." -ForegroundColor Yellow
    try {
        $status = Invoke-RestMethod -Uri "$api/status" -Method GET -TimeoutSec 3
        Write-Host "API healthy. processId=$($status.data.processId)" -ForegroundColor Green
        return
    } catch {
        Write-Host "API not responding. Existing process may be stale." -ForegroundColor Yellow
    }
}

if (-not (Test-Path $tslabExe)) {
    Write-Host "TSLab not found at $tslabExe" -ForegroundColor Red
    exit 1
}

Write-Host "Starting TSLab..." -ForegroundColor Cyan
Start-Process $tslabExe -ArgumentList "-WorkingDirectory `"$workDir`""

# Wait for API
Write-Host "Waiting for API..." -ForegroundColor Yellow
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Seconds 2
    try {
        $status = Invoke-RestMethod -Uri "$api/status" -Method GET -TimeoutSec 3
        Write-Host "API ready. processId=$($status.data.processId)" -ForegroundColor Green
        return
    } catch {
        Write-Host "." -NoNewline
    }
}
Write-Host ""
Write-Host "API did not become ready in 60 seconds." -ForegroundColor Red
exit 1