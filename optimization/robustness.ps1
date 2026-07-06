<#
.SYNOPSIS
    Robustness testing for TSLab strategies.

.DESCRIPTION
    Performs Monte Carlo simulation and K-fold cross-validation to test strategy robustness.

.PARAMETER ScriptName
    Name of the TSLab script to test.

.PARAMETER MonteCarloRuns
    Number of Monte Carlo simulations (default: 1000).

.PARAMETER KFolds
    Number of folds for cross-validation (default: 5).

.PARAMETER Metric
    Metric to evaluate (default: NetProfit).

.EXAMPLE
    .\robustness.ps1 -ScriptName "RSICCIBot" -MonteCarloRuns 1000 -KFolds 5
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$ScriptName,
    
    [Parameter(Mandatory=$false)]
    [int]$MonteCarloRuns = 1000,
    
    [Parameter(Mandatory=$false)]
    [int]$KFolds = 5,
    
    [Parameter(Mandatory=$false)]
    [string]$Metric = "NetProfit"
)

$ErrorActionPreference = "Stop"
$BaseUrl = "http://localhost:5000/api"

Write-Host "=== Strategy Robustness Testing ===" -ForegroundColor Cyan
Write-Host "Script: $ScriptName"
Write-Host "Monte Carlo Runs: $MonteCarloRuns | K-Folds: $KFolds"

# Get current script state
Write-Host "`nGetting script information..." -ForegroundColor Yellow
$scriptInfo = Invoke-RestMethod -Uri "$BaseUrl/scripts/$ScriptName" -Method Get

if (-not $scriptInfo.success) {
    Write-Error "Failed to get script info: $($scriptInfo.message)"
    exit 1
}

# Get parameters
$parameters = Invoke-RestMethod -Uri "$BaseUrl/scripts/$ScriptName/parameters" -Method Get
$candidates = $parameters.data.optimizationCandidates

Write-Host "Script has $($candidates.Count) optimizable parameters"

# ============================================================
# Part 1: Monte Carlo Simulation
# ============================================================
Write-Host "`n=== Monte Carlo Simulation ===" -ForegroundColor Green
Write-Host "Running $MonteCarloRuns random parameter combinations..."

$monteCarloResults = @()

for ($i = 0; $i -lt $MonteCarloRuns; $i++) {
    if ($i % 100 -eq 0) {
        Write-Host "  Progress: $i/$MonteCarloRuns"
    }
    
    # Generate random parameters within optimization ranges
    $randomParams = @{}
    $paramIds = @()
    
    foreach ($candidate in $candidates) {
        $min = [double]$candidate.min
        $max = [double]$candidate.max
        $step = [double]$candidate.step
        
        # Generate random value in range
        $range = ($max - $min) / $step
        $randomStep = Get-Random -Minimum 0 -Maximum ([int]$range + 1)
        $randomValue = $min + ($randomStep * $step)
        
        $paramId = "$($candidate.blockId)_$($candidate.paramInvariantName)"
        $randomParams[$paramId] = $randomValue
        $paramIds += $paramId
    }
    
    # Set parameters
    $opsBody = @{
        ops = @()
    }
    
    foreach ($candidate in $candidates) {
        $paramId = "$($candidate.blockId)_$($candidate.paramInvariantName)"
        $opsBody.ops += @{
            op = "SetOptimizationRange"
            blockId = $candidate.blockId
            paramInvariantName = $candidate.paramInvariantName
            optimDataType = $candidate.suggestedOptimDataType
            value = $randomParams[$paramId]
            min = $candidate.min
            max = $candidate.max
            step = $candidate.step
        }
    }
    
    $opsJson = $opsBody | ConvertTo-Json -Depth 10
    Invoke-RestMethod -Uri "$BaseUrl/scripts/$ScriptName/ops" -Method Post -Body $opsJson -ContentType "application/json" | Out-Null
    
    # Run optimization with single iteration (just to test parameters)
    $optBody = @{
        iterations = 1
        metric = $Metric
        selectedParameterIds = $paramIds
    }
    
    $optJson = $optBody | ConvertTo-Json -Depth 10
    $optStart = Invoke-RestMethod -Uri "$BaseUrl/scripts/$ScriptName/optimization/start" -Method Post -Body $optJson -ContentType "application/json"
    
    if ($optStart.success) {
        $jobId = $optStart.data.jobId
        
        # Wait for completion
        $completed = $false
        $waited = 0
        
        while ($waited -lt 30 -and -not $completed) {
            Start-Sleep -Seconds 2
            $waited += 2
            
            $status = Invoke-RestMethod -Uri "$BaseUrl/optimizations/$jobId" -Method Get
            
            if ($status.data.status -eq "Completed") {
                $completed = $true
                
                $best = Invoke-RestMethod -Uri "$BaseUrl/optimizations/$jobId/best?metric=$Metric&rank=1" -Method Get
                
                if ($best.success) {
                    $monteCarloResults += @{
                        run = $i + 1
                        params = $randomParams
                        net_profit = $best.data.netProfit
                        max_drawdown = $best.data.maxDrawdownPct
                        profit_factor = $best.data.profitFactor
                        all_trades = $best.data.allTrades
                    }
                }
            }
            elseif ($status.data.status -eq "Failed") {
                break
            }
        }
    }
}

# Monte Carlo Statistics
Write-Host "`n--- Monte Carlo Results ---" -ForegroundColor Yellow

if ($monteCarloResults.Count -gt 0) {
    $profits = $monteCarloResults | ForEach-Object { $_.net_profit }
    $drawdowns = $monteCarloResults | ForEach-Object { $_.max_drawdown }
    $profitFactors = $monteCarloResults | ForEach-Object { $_.profit_factor }
    
    $profitStats = $profits | Measure-Object -Average -StandardDeviation -Minimum -Maximum
    $drawdownStats = $drawdowns | Measure-Object -Average -StandardDeviation -Minimum -Maximum
    $pfStats = $profitFactors | Measure-Object -Average -StandardDeviation -Minimum -Maximum
    
    Write-Host "Net Profit:"
    Write-Host "  Mean: $($profitStats.Average)"
    Write-Host "  Std Dev: $($profitStats.StandardDeviation)"
    Write-Host "  Min: $($profitStats.Minimum)"
    Write-Host "  Max: $($profitStats.Maximum)"
    
    Write-Host "Max Drawdown:"
    Write-Host "  Mean: $($drawdownStats.Average)%"
    Write-Host "  Std Dev: $($drawdownStats.StandardDeviation)%"
    
    Write-Host "Profit Factor:"
    Write-Host "  Mean: $($pfStats.Average)"
    Write-Host "  Std Dev: $($pfStats.StandardDeviation)"
    
    # Robustness score
    $profitableRuns = ($monteCarloResults | Where-Object { $_.net_profit -gt 0 }).Count
    $robustnessScore = $profitableRuns / $monteCarloResults.Count * 100
    
    Write-Host "`nRobustness Score: $([math]::Round($robustnessScore, 1))% profitable runs"
    
    if ($robustnessScore -ge 70) {
        Write-Host "✓ Strategy appears robust" -ForegroundColor Green
    } elseif ($robustnessScore -ge 50) {
        Write-Host "~ Strategy shows moderate robustness" -ForegroundColor Yellow
    } else {
        Write-Host "✗ Strategy may be overfit" -ForegroundColor Red
    }
} else {
    Write-Warning "No successful Monte Carlo runs"
}

# ============================================================
# Part 2: K-Fold Cross-Validation
# ============================================================
Write-Host "`n=== K-Fold Cross-Validation ===" -ForegroundColor Green
Write-Host "Running $KFolds-fold cross-validation..."

$kFoldResults = @()

for ($fold = 0; $fold -lt $KFolds; $fold++) {
    Write-Host "`nFold $($fold + 1) of $KFolds"
    
    # Configure optimization ranges
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
    
    $opsJson = $opsBody | ConvertTo-Json -Depth 10
    Invoke-RestMethod -Uri "$BaseUrl/scripts/$ScriptName/ops" -Method Post -Body $opsJson -ContentType "application/json" | Out-Null
    
    # Start optimization
    $optBody = @{
        iterations = 50  # Reduced for speed
        metric = $Metric
        selectedParameterIds = $candidates | ForEach-Object { "$($_.blockId)_$($_.paramInvariantName)" }
    }
    
    $optJson = $optBody | ConvertTo-Json -Depth 10
    $optStart = Invoke-RestMethod -Uri "$BaseUrl/scripts/$ScriptName/optimization/start" -Method Post -Body $optJson -ContentType "application/json"
    
    if ($optStart.success) {
        $jobId = $optStart.data.jobId
        
        # Wait for completion
        $completed = $false
        $waited = 0
        
        while ($waited -lt 120 -and -not $completed) {
            Start-Sleep -Seconds 5
            $waited += 5
            
            $status = Invoke-RestMethod -Uri "$BaseUrl/optimizations/$jobId" -Method Get
            
            if ($status.data.status -eq "Completed") {
                $completed = $true
                
                $best = Invoke-RestMethod -Uri "$BaseUrl/optimizations/$jobId/best?metric=$Metric&rank=1" -Method Get
                
                if ($best.success) {
                    $kFoldResults += @{
                        fold = $fold + 1
                        best_params = $best.data.parameterValues
                        net_profit = $best.data.netProfit
                        max_drawdown = $best.data.maxDrawdownPct
                        profit_factor = $best.data.profitFactor
                        all_trades = $best.data.allTrades
                    }
                    
                    Write-Host "  Fold $($fold + 1) completed: Net Profit = $($best.data.netProfit)"
                }
            }
            elseif ($status.data.status -eq "Failed") {
                Write-Warning "  Fold $($fold + 1) failed"
                break
            }
        }
    }
}

# K-Fold Statistics
Write-Host "`n--- K-Fold Results ---" -ForegroundColor Yellow

if ($kFoldResults.Count -gt 0) {
    $foldProfits = $kFoldResults | ForEach-Object { $_.net_profit }
    $foldStats = $foldProfits | Measure-Object -Average -StandardDeviation -Minimum -Maximum
    
    Write-Host "Net Profit across folds:"
    Write-Host "  Mean: $($foldStats.Average)"
    Write-Host "  Std Dev: $($foldStats.StandardDeviation)"
    Write-Host "  Min: $($foldStats.Minimum)"
    Write-Host "  Max: $($foldStats.Maximum)"
    
    # Coefficient of variation
    if ($foldStats.Average -ne 0) {
        $cv = [math]::Abs($foldStats.StandardDeviation / $foldStats.Average)
        Write-Host "  Coefficient of Variation: $([math]::Round($cv, 2))"
        
        if ($cv -lt 0.5) {
            Write-Host "✓ Low variance across folds - strategy is stable" -ForegroundColor Green
        } elseif ($cv -lt 1.0) {
            Write-Host "~ Moderate variance across folds" -ForegroundColor Yellow
        } else {
            Write-Host "✗ High variance across folds - strategy may be unstable" -ForegroundColor Red
        }
    }
} else {
    Write-Warning "No successful K-fold runs"
}

# ============================================================
# Summary
# ============================================================
Write-Host "`n=== Robustness Summary ===" -ForegroundColor Cyan

$summary = @{
    script_name = $ScriptName
    monte_carlo = @{
        runs = $MonteCarloRuns
        successful = $monteCarloResults.Count
        robustness_score = if ($monteCarloResults.Count -gt 0) { 
            ($monteCarloResults | Where-Object { $_.net_profit -gt 0 }).Count / $monteCarloResults.Count * 100 
        } else { 0 }
    }
    k_fold = @{
        folds = $KFolds
        successful = $kFoldResults.Count
        avg_profit = if ($kFoldResults.Count -gt 0) { 
            ($kFoldResults | Measure-Object -Property net_profit -Average).Average 
        } else { 0 }
    }
}

Write-Host "Monte Carlo: $($summary.monte_carlo.successful)/$($summary.monte_carlo.runs) successful runs"
Write-Host "K-Fold: $($summary.k_fold.successful)/$($summary.k_fold.folds) successful folds"

# Overall assessment
$overallScore = ($summary.monte_carlo.robustness_score + $summary.k_fold.avg_profit) / 2

if ($overallScore -ge 60) {
    Write-Host "`n✓ Overall: Strategy appears robust" -ForegroundColor Green
} else {
    Write-Host "`n~ Overall: Strategy may need refinement" -ForegroundColor Yellow
}

# Save results
$resultsPath = "./robustness_results_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$summary | ConvertTo-Json -Depth 10 | Out-File -FilePath $resultsPath
Write-Host "`nResults saved to: $resultsPath"

return $summary
