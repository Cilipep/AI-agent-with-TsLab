# Optimize Window/Threshold for all NN Trading instruments
$scripts = @("NN_AAVE","NN_ETH","NN_LINK","NN_NEAR","NN_SOL","NN_UNI","NN_XLM","NN_XRP")

foreach ($s in $scripts) {
    Write-Host "`n=== Optimizing $s ==="

    # Get parameters
    try {
        $params = Invoke-RestMethod -Uri "http://localhost:5000/api/scripts/$s/parameters" -Method GET
        $windowParam = $params.data.parameters | Where-Object { $_.name -eq "Window" }
        $thresholdParam = $params.data.parameters | Where-Object { $_.name -eq "Threshold" }

        if (-not $windowParam -or -not $thresholdParam) {
            Write-Host "  SKIP: Window/Threshold params not found"
            continue
        }

        # Set optimization ranges
        $ops = @{
            ops = @(
                @{
                    op = "SetOptimizationRange"
                    blockId = $windowParam.blockName
                    paramInvariantName = "Window"
                    minValue = 10
                    maxValue = 100
                    step = 5
                },
                @{
                    op = "SetOptimizationRange"
                    blockId = $thresholdParam.blockName
                    paramInvariantName = "Threshold"
                    minValue = 0.1
                    maxValue = 0.9
                    step = 0.05
                }
            )
        } | ConvertTo-Json -Compress

        Invoke-RestMethod -Uri "http://localhost:5000/api/scripts/$s/ops" -Method POST -Body $ops -ContentType "application/json" | Out-Null

        # Start optimization
        $optBody = @{
            scriptName = $s
            selectedParameterIds = @($windowParam.id, $thresholdParam.id)
            iterations = 15
        } | ConvertTo-Json -Compress

        $job = Invoke-RestMethod -Uri "http://localhost:5000/api/scripts/$s/optimization/start" -Method POST -Body $optBody -ContentType "application/json"
        $jobId = $job.data.jobId
        Write-Host "  Job started: $jobId"

        # Wait for completion
        $maxWait = 180
        $waited = 0
        while ($waited -lt $maxWait) {
            Start-Sleep -Seconds 10
            $waited += 10
            $status = Invoke-RestMethod -Uri "http://localhost:5000/api/scripts/optimizations/$jobId" -Method GET
            if ($status.data.status -eq "Completed") {
                Write-Host "  Completed in ${waited}s"
                break
            }
            Write-Host "  Waiting... ($waited s)"
        }

        # Get best result
        $best = Invoke-RestMethod -Uri "http://localhost:5000/api/scripts/$s/optimizations/$jobId/best?metric=NetProfit&rank=1" -Method GET
        $window = $best.data.parameterValues.Window
        $threshold = $best.data.parameterValues.Threshold
        $profit = $best.data.netProfitPct * 100
        $winRate = $best.data.winTradesPct
        $pf = $best.data.profitFactor

        Write-Host "  BEST: Window=$window Threshold=$threshold Profit=$profit% Win=$winRate% PF=$pf"

        # Apply best result
        Invoke-RestMethod -Uri "http://localhost:5000/api/scripts/$s/optimizations/$jobId/apply?metric=NetProfit&rank=1" -Method POST -Body "{}" -ContentType "application/json" | Out-Null
        Write-Host "  Applied!"

    } catch {
        Write-Host "  ERROR: $($_.Exception.Message)"
    }
}
