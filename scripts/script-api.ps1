param(
    [Parameter(Mandatory=$true)]
    [string]$Method,
    [Parameter(Mandatory=$true)]
    [string]$ScriptName,
    [Parameter(Mandatory=$true)]
    [string]$Route,
    [string]$BodyFile = ""
)

$ErrorActionPreference = "Stop"
$api = "http://localhost:5000/api"

# Check for @last-created shorthand
if ($ScriptName -eq "@last-created") {
    $artifactFile = "./tmp/last-script-artifact.json"
    if (-not (Test-Path $artifactFile)) {
        Write-Host "No @last-created artifact found. Run create-script.ps1 first." -ForegroundColor Red
        exit 1
    }
    $artifact = Get-Content $artifactFile -Raw | ConvertFrom-Json
    $ScriptName = $artifact.scriptName
    Write-Host "Using last-created: $ScriptName" -ForegroundColor DarkGray
}

# Construct base API path for script
$routeBase = "$api/scripts/$ScriptName"

$uri = "$routeBase/$Route"
Write-Host "$Method $uri" -ForegroundColor Cyan

$params = @{
    Uri = $uri
    Method = $Method
}

# Only add body for methods that support it
if ($Method -in @("POST", "PUT", "PATCH", "DELETE")) {
    $params.ContentType = "application/json"
    if ($BodyFile) {
        if (-not (Test-Path $BodyFile)) {
            Write-Host "Body file not found: $BodyFile" -ForegroundColor Red
            exit 1
        }
        $params.Body = Get-Content -Path $BodyFile -Raw -Encoding utf8
        Write-Host "  Body: $BodyFile" -ForegroundColor DarkGray
    } else {
        $params.Body = "{}"
    }
}

$result = Invoke-RestMethod @params
$result | ConvertTo-Json -Depth 5