param(
    [Parameter(Mandatory=$true)]
    [string]$Method,
    [Parameter(Mandatory=$true)]
    [string]$Route,
    [string]$BodyFile = ""
)

$ErrorActionPreference = "Stop"
$api = "http://localhost:5000/api"
$uri = "$api/$Route"

Write-Host "$Method $uri" -ForegroundColor Cyan

$params = @{
    Uri = $uri
    Method = $Method
    ContentType = "application/json"
}

if ($BodyFile) {
    if (-not (Test-Path $BodyFile)) {
        Write-Host "Body file not found: $BodyFile" -ForegroundColor Red
        exit 1
    }
    $params.Body = Get-Content -Path $BodyFile -Raw -Encoding utf8
    Write-Host "  Body: $BodyFile" -ForegroundColor DarkGray
}

$result = Invoke-RestMethod @params
$result | ConvertTo-Json -Depth 5