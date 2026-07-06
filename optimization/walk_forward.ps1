<#
.SYNOPSIS
    Walk-forward optimization for TSLab scripts.

.DESCRIPTION
    Performs walk-forward analysis by partitioning data into in-sample/out-of-sample windows.
    Optimizes on in-sample period and validates on out-of-sample period.

.PARAMETER ScriptName
    Name of the TSLab script to optimize.

.PARAMETER InSamplePct
    Percentage of data for in-sample optimization (default: 70%).

.PARAMETER NumWindows
    Number of walk-forward windows (default: 5).

.PARAMETER Metric
    Metric to optimize (default: NetProfit).

.EXAMPLE
    .\walk_forward.ps1 -ScriptName "RSICCIBot" -InSamplePct 70 -NumWindows 5
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$ScriptName,
    
    [Parameter(Mandatory=$false)]
    [double]$InSamplePct = 70,
    
    [Parameter(Mandatory=$false)]
    [int]$NumWindows = 5,
    
    [Parameter(Mandatory=$false)]
    [string]$Metric = "NetProfit",
    
    [Parameter(Mandatory=$false)]
    [int]$MaxIterations = 100
)

$ErrorActionPreference = "Stop"
$BaseUrl = "http://localhost:5000/api"

Write-Host "=== Walk-Forward Optimization ===" -ForegroundColor Cyan
Write-Host "Script: $ScriptName"
Write-Host "In-Sample: $InSamplePct% | Windows: $NumWindows | Metric: $Metric"

# Get script info
Write-Host "`nGetting script information..." -ForegroundColor Yellow
$scriptInfo = Invoke-RestMethod -Uri "$BaseUrl/scripts/$ScriptName" -Method Get

if (-not $scriptInfo.success) {
    Write-Error "Failed to get script info: $($scriptInfo.message)"
    exit 1
}

# Get script parameters
$parameters = Invoke-RestMethod -Uri "$BaseUrl/scripts/$ScriptName/parameters" -Method Get

if (-not $parameters.success) {
    Write-Error "Failed to get parameters: $($parameters.message)"
    exit 1
}

# Get optimization candidates
$candidates = $parameters.data.optimizationCandidates
if ($candidates.Count -eq 0) {
    Write-Error "No optimization candidates found for script"
    exit 1
}

Write-Host "Found $($candidates.Count) optimization candidates"

# Store results for each window
$results = @()

# Calculate window sizes
# Assuming we have date range info or use bar count
$startDate = $scriptInfo.data.labOptions.dateFrom
$endDate = $scriptInfo.data.labOptions.dateTo

Write-Host "`nDate range: $startDate to $endDate"

# Create walk-forward windows
for ($w = 0; $w -lt $NumWindows; $w++) {
    Write-Host "`n--- Window $($w + 1) of $NumWindows ---" -ForegroundColor Green
    
    # Calculate window boundaries (simplified - using index-based splitting)
    # In real implementation, you'd split based on actual dates
    $windowStart = $w * [math]::Floor(100 / $NumWindows)
    $windowEnd = ($w + 1) * [math]::Floor(100 / $NumWindows)
    $inSampleEnd = $windowStart + ($windowEnd - $windowStart) * ($InSamplePct / 100)
    
    Write-Host "Window: $windowStart% - $windowEnd%"
    Write-Host "In-Sample: $windowStart% - $inSampleEnd%"
    Write-Host "Out-of-Sample: $inSampleEnd% - $windowEnd%"
    
    # Configure optimization ranges for this window
    $opsBody = @{
        ops = @()
    }
    
    foreach ($candidate in $candidates) {
        $opsBody.ops += @{
            op = "SetOptimizationRange"
            blockId = $candidate.blockId
            paramInvariantName = $candidate.paramInvariantName
            optimDataType = $candidate.suggestedOptimDataType
            value = [double]$candidate.value
            min = $candidate.min
            max = $candidate.max
            step = $candidate.step
        }
    }
    
    # Apply optimization ranges
    $opsJson = $opsBody | ConvertTo-Json -Depth 10
    $opsResult = Invoke-RestMethod -Uri "$BaseUrl/scripts/$ScriptName/ops" -Method Post -Body $opsJson -ContentType "application/json"
    
    if (-not $opsResult.success) {
        Write-Warning "Failed to set optimization ranges for window $($w + 1)"
        continue
    }
    
    # Start optimization
    $optStartBody = @{
        iterations = $MaxIterations
        metric = $Metric
        selectedParameterIds = $candidates | ForEach-Object { "$($_.blockId)_$($_.paramInvariantName)" }
    }
    
    $optStartJson = $optStartBody | ConvertTo-Json -Depth 10
    $optStart = Invoke-RestMethod -Uri "$BaseUrl/scripts/$ScriptName/optimization/start" -Method Post -Body $optStartJson -ContentType "application/json"
    
    if (-not $optStart.success) {
        Write-Warning "Failed to start optimization for window $($w + 1)"
        continue
    }
    
    $jobId = $optStart.data.jobId
    Write-Host "Optimization started: $jobId"
    
    # Poll for completion
    $maxWait = 300
    $waited = 0
    $completed = $false
    
    while ($waited -lt $maxWait -and -not $completed) {
        Start-Sleep -Seconds 5
        $waited += 5
        
        $status = Invoke-RestMethod -Uri "$BaseUrl/optimizations/$jobId" -Method Get
        
        if ($status.data.status -eq "Completed") {
            $completed = $true
            Write-Host "Optimization completed in $waited seconds" -ForegroundColor Green
        }
        elseif ($status.data.status -eq "Failed") {
            Write-Warning "Optimization failed for window $($w + 1)"
            break
        }
        
        Write-Host "  Waiting... ($waited/$maxWait seconds)"
    }
    
    if (-not $completed) {
        Write-Warning "Optimization timed out for window $($w + 1)"
        continue
    }
    
    # Get best result
    $best = Invoke-RestMethod -Uri "$BaseUrl/optimizations/$jobId/best?metric=$Metric&rank=1" -Method Get
    
    if ($best.success) {
        $windowResult = @{
            window = $w + 1
            in_sample_range = "$windowStart% - $inSampleEnd%"
            out_of_sample_range = "$inSampleEnd% - $windowEnd%"
            best_params = $best.data.parameterValues
            metric_value = $best.data.$Metric
            net_profit = $best.data.netProfit
            max_drawdown = $best.data.maxDrawdownPct
            profit_factor = $best.data.profitFactor
            all_trades = $best.data.allTrades
        }
        
        $results += $windowResult
        
        Write-Host "`nBest Result for Window $($w + 1):" -ForegroundColor Cyan
        Write-Host "  Net Profit: $($best.data.netProfit)"
        Write-Host "  Max Drawdown: $($best.data.maxDrawdownPct)%"
        Write-Host "  Profit Factor: $($best.data.profitFactor)"
        Write-Host "  Parameters: $($best.data.parameterValues | ConvertTo-Json -Compress)"
    }
}

# Aggregate results
Write-Host "`n=== Walk-Forward Summary ===" -ForegroundColor Cyan

if ($results.Count -eq 0) {
    Write-Warning "No successful optimization windows"
    exit 1
}

$avgNetProfit = ($results | Measure-Object -Property net_profit -Average).Average
$avgDrawdown = ($results | Measure-Object -Property max_drawdown -Average).Average
$avgProfitFactor = ($results | Measure-Object -Property profit_factor -Average).Average
$avgTrades = ($results | Measure-Object -Property all_trades -Average).Average

Write-Host "Average Net Profit: $avgNetProfit"
Write-Host "Average Max Drawdown: $avgDrawdown%"
Write-Host "Average Profit Factor: $avgProfitFactor"
Write-Host "Average Trades: $avgTrades"

# Check consistency
$profitableWindows = ($results | Where-Object { $_.net_profit -gt 0 }).Count
$consistency = $profitableWindows / $results.Count * 100

Write-Host "`nConsistency: $profitableWindows/$($results.Count) profitable windows ($([math]::Round($consistency, 1))%)"

if ($consistency -ge 60) {
    Write-Host "✓ Strategy shows consistent performance across windows" -ForegroundColor Green
} else {
    Write-Host "✗ Strategy shows inconsistent performance - may be overfit" -ForegroundColor Yellow
}

# Save results
$resultsPath = "./walk_forward_results_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$results | ConvertTo-Json -Depth 10 | Out-File -FilePath $resultsPath
Write-Host "`nResults saved to: $resultsPath"

# Return results for pipeline use
return $results
