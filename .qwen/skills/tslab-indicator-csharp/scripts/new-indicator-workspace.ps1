param(
    [Parameter(Mandatory = $true)]
    [Alias("WorkspacePath", "OutputPath", "Path")]
    [string]$Destination,

    [ValidateSet("one", "security", "three", "four")]
    [string]$Arity = "one",

    [Alias("Name", "HandlerTypeName", "TypeName")]
    [string]$ClassName = "CustomIndicatorHandler"
)

$skillRoot = Split-Path -Parent $PSScriptRoot
$assetsDir = Join-Path $skillRoot "assets"
function Resolve-ExistingPath {
    param(
        [string[]]$Candidates
    )

    foreach ($candidate in $Candidates) {
        if ([string]::IsNullOrWhiteSpace($candidate)) {
            continue
        }

        $expanded = [Environment]::ExpandEnvironmentVariables($candidate)
        $full = [System.IO.Path]::GetFullPath($expanded)
        if (Test-Path -LiteralPath $full) {
            return $full
        }
    }

    return $null
}

function Test-UsableRuntimeAssemblyPath {
    param(
        [string]$Path
    )

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return $false
    }

    $full = [System.IO.Path]::GetFullPath($Path)
    if (-not (Test-Path -LiteralPath $full)) {
        return $false
    }

    # Do not bootstrap against old agent scratch outputs. Those may contain stale
    # assemblies copied from previous runs and can make the compile-fix loop chase
    # APIs that are not present in the current host.
    if ($full -match '[\\/](tmp|ai-agent)[\\/]' -or $full -match '[\\/]agent-ws[\\/]') {
        return $false
    }

    return $true
}

function Resolve-UpwardFile {
    param(
        [string[]]$StartDirectories,
        [string]$FileName,
        [int]$MaxDepth = 8
    )

    foreach ($start in $StartDirectories) {
        if ([string]::IsNullOrWhiteSpace($start)) {
            continue
        }

        $dir = [System.IO.Path]::GetFullPath($start)
        for ($depth = 0; $depth -le $MaxDepth -and -not [string]::IsNullOrWhiteSpace($dir); $depth++) {
            $candidate = Join-Path $dir $FileName
            if (Test-UsableRuntimeAssemblyPath -Path $candidate) {
                return $candidate
            }

            $parent = Split-Path -Parent $dir
            if ([string]::IsNullOrWhiteSpace($parent) -or $parent -eq $dir) {
                break
            }

            $dir = $parent
        }
    }

    return $null
}

function Resolve-BuildOutputFile {
    param(
        [string[]]$StartDirectories,
        [string]$FileName,
        [int]$MaxDepth = 8
    )

    foreach ($start in $StartDirectories) {
        if ([string]::IsNullOrWhiteSpace($start)) {
            continue
        }

        $dir = [System.IO.Path]::GetFullPath($start)
        for ($depth = 0; $depth -le $MaxDepth -and -not [string]::IsNullOrWhiteSpace($dir); $depth++) {
            $publicDir = Join-Path $dir "public"
            if (Test-Path -LiteralPath $publicDir) {
                $match =
                    Get-ChildItem -Path $publicDir -File -Filter $FileName -Recurse -ErrorAction SilentlyContinue |
                    Where-Object {
                        $_.FullName -match '[\\/](ConsoleLauncher|ScriptCommon)[\\/]bin[\\/](Debug|Release)[\\/]net\d+\.\d+[\\/]' -and
                        (Test-UsableRuntimeAssemblyPath -Path $_.FullName)
                    } |
                    Sort-Object {
                        if ($_.FullName -match '[\\/]ConsoleLauncher[\\/]bin[\\/]') { 0 } else { 1 }
                    }, FullName |
                    Select-Object -First 1

                if ($match) {
                    return $match.FullName
                }
            }

            $parent = Split-Path -Parent $dir
            if ([string]::IsNullOrWhiteSpace($parent) -or $parent -eq $dir) {
                break
            }

            $dir = $parent
        }
    }

    return $null
}

New-Item -ItemType Directory -Force -Path $Destination | Out-Null

$projectPath = Join-Path $Destination "IndicatorHandlers.csproj"

$scriptHintPath =
    (Resolve-UpwardFile -StartDirectories @(
        (Get-Location).Path,
        $Destination,
        $skillRoot
    ) -FileName "TSLab.Script.dll")

if (-not $scriptHintPath) {
    $scriptHintPath = Resolve-ExistingPath -Candidates @(
        $env:TSLAB_SCRIPT_HINT_PATH,
        (Join-Path (Get-Location) "TSLab.Script.dll"),
        (Join-Path (Get-Location) "..\TSLab.Script.dll"),
        (Join-Path $Destination "..\..\..\TSLab.Script.dll"),
        (Join-Path $Destination "..\..\TSLab.Script.dll"),
        (Join-Path $Destination "..\TSLab.Script.dll")
    )
    if (-not (Test-UsableRuntimeAssemblyPath -Path $scriptHintPath)) {
        $scriptHintPath = $null
    }
}

if (-not $scriptHintPath) {
    $scriptHintPath = Resolve-BuildOutputFile -StartDirectories @(
        (Get-Location).Path,
        $Destination,
        $skillRoot
    ) -FileName "TSLab.Script.dll"
}

if (-not $scriptHintPath) {
    throw "Could not resolve TSLab.Script.dll for indicator workspace bootstrap. Set TSLAB_SCRIPT_HINT_PATH or run the bootstrap from a packaged agent workspace with runtime references available."
}

$scriptDir = Split-Path -Parent $scriptHintPath
$utilityHintPath = Resolve-ExistingPath -Candidates @(
    $env:TSLAB_UTILITY_HINT_PATH,
    (Join-Path $scriptDir "TSLab.Utility.dll"),
    (Join-Path (Get-Location) "TSLab.Utility.dll")
)
if (-not (Test-UsableRuntimeAssemblyPath -Path $utilityHintPath)) {
    $utilityHintPath = $null
}

if (-not $utilityHintPath) {
    $utilityHintPath = Resolve-BuildOutputFile -StartDirectories @(
        (Get-Location).Path,
        $Destination,
        $skillRoot
    ) -FileName "TSLab.Utility.dll"
}

if (-not $utilityHintPath) {
    throw "Could not resolve TSLab.Utility.dll for indicator workspace bootstrap. Set TSLAB_UTILITY_HINT_PATH or run the bootstrap from a packaged agent workspace with runtime references available."
}

$dataSourceHintPath = Resolve-ExistingPath -Candidates @(
    $env:TSLAB_DATASOURCE_HINT_PATH,
    (Join-Path $scriptDir "TSLab.DataSource.dll"),
    (Join-Path (Get-Location) "TSLab.DataSource.dll")
)
if (-not (Test-UsableRuntimeAssemblyPath -Path $dataSourceHintPath)) {
    $dataSourceHintPath = $null
}

if (-not $dataSourceHintPath) {
    $dataSourceHintPath = Resolve-BuildOutputFile -StartDirectories @(
        (Get-Location).Path,
        $Destination,
        $skillRoot
    ) -FileName "TSLab.DataSource.dll"
}

if (-not $dataSourceHintPath) {
    throw "Could not resolve TSLab.DataSource.dll for indicator workspace bootstrap. Set TSLAB_DATASOURCE_HINT_PATH or run the bootstrap from a packaged agent workspace with runtime references available."
}

$projectTemplate = Get-Content -Path (Join-Path $assetsDir "IndicatorHandlers.csproj") -Raw -Encoding UTF8
$projectTemplate = $projectTemplate.Replace("__TSLAB_SCRIPT_HINT_PATH__", $scriptHintPath)
$projectTemplate = $projectTemplate.Replace("__TSLAB_UTILITY_HINT_PATH__", $utilityHintPath)
$projectTemplate = $projectTemplate.Replace("__TSLAB_DATASOURCE_HINT_PATH__", $dataSourceHintPath)
Set-Content -Path $projectPath -Value $projectTemplate -Encoding UTF8

$templateName =
    if ($Arity -eq "four") { "StreamIndicatorFourInputs.cs" }
    elseif ($Arity -eq "security") { "StreamIndicatorSecurityInput.cs" }
    elseif ($Arity -eq "three") { "StreamIndicatorThreeInputs.cs" }
    else { "StreamIndicatorOneInput.cs" }

$sourceTemplate = Join-Path $assetsDir $templateName
$sourcePath = Join-Path $Destination "$ClassName.cs"

$content = Get-Content -Path $sourceTemplate -Raw -Encoding UTF8
$content = $content.Replace("__CLASS_NAME__", $ClassName)
Set-Content -Path $sourcePath -Value $content -Encoding UTF8

$resourceAssetsDir = Join-Path $assetsDir "Properties"
if (Test-Path -LiteralPath $resourceAssetsDir) {
    $resourceDestinationDir = Join-Path $Destination "Properties"
    New-Item -ItemType Directory -Force -Path $resourceDestinationDir | Out-Null

    Get-ChildItem -Path $resourceAssetsDir -File -Filter "*.resx" | ForEach-Object {
        $resourceContent = Get-Content -Path $_.FullName -Raw -Encoding UTF8
        $resourceContent = $resourceContent.Replace("__CLASS_NAME__", $ClassName)
        Set-Content -Path (Join-Path $resourceDestinationDir $_.Name) -Value $resourceContent -Encoding UTF8
    }
}

Write-Output "Created:"
Write-Output "  $projectPath"
Write-Output "  $sourcePath"
if (Test-Path -LiteralPath (Join-Path $Destination "Properties\Resources.resx")) {
    Write-Output "  $(Join-Path $Destination "Properties\Resources.resx")"
}
Write-Output "Runtime references resolved by bootstrap."
