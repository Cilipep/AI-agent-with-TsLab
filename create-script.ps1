param(
    [Parameter(Mandatory=$true)]
    [string]$LeafName,
    [string]$ParentPath = ""
)

$ErrorActionPreference = "Stop"
$api = "http://localhost:5000/api"

Write-Host "=== Creating script: $LeafName ===" -ForegroundColor Cyan

# Ensure folder exists if parent path given
if ($ParentPath) {
    Write-Host "Ensuring folder: $ParentPath" -ForegroundColor Yellow
    $folderBody = @{ path = $ParentPath } | ConvertTo-Json -Compress
    Invoke-RestMethod -Uri "$api/script-manager/folders/ensure-path" -Method POST -ContentType "application/json" -Body $folderBody -ErrorAction SilentlyContinue | Out-Null
    Start-Sleep -Milliseconds 500
}

# Create script
Write-Host "Creating script..." -ForegroundColor Yellow
$createBody = @{ request = @{ name = $LeafName; parentPath = $ParentPath } } | ConvertTo-Json -Compress
$result = Invoke-RestMethod -Uri "$api/script-manager/scripts" -Method POST -ContentType "application/json" -Body $createBody -ErrorAction Stop

$name = $result.scriptName
$route = $result.resolvedArtifactRouteName
$id = $result.scriptId

Write-Host "  Created: $name (id=$id)" -ForegroundColor Green
Write-Host "  Route: $route" -ForegroundColor DarkGray

# Persist for downstream helpers
@{ scriptName = $name; scriptId = $id; resolvedArtifactRouteName = $route } | ConvertTo-Json -Compress | Set-Content -Encoding utf8 "./tmp/last-script-artifact.json"
Write-Host "  Saved to ./tmp/last-script-artifact.json" -ForegroundColor DarkGray

return $result