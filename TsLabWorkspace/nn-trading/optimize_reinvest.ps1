# Optimize Window/Threshold for all NN instruments + enable reinvestment
$scripts = @("NN_BTC","NN_ETH","NN_SOL","NN_AAVE","NN_LINK","NN_NEAR","NN_UNI","NN_XLM","NN_XRP")

# Enable reinvestment: set UseCommissionInProfit=true via graph edit
# This means commission is deducted from profit, allowing compound growth

foreach ($s in $scripts) {
    Write-Host "`n=== $s ==="

    # Step 1: Set optimization ranges
    try {
        $params = Invoke-RestMethod -Uri "http://localhost:5000/api/scripts/$s/parameters" -Method GET
        $windowParam = $params.data.parameters | Where-Object { $_.name -eq "Window" }
        $thresholdParam = $params.data.parameters | Where-Object { $_.name -eq "Threshold" }

        if (-not $windowParam -or -not $thresholdParam) {
            Write-Host "  SKIP: params not found"
            continue
        }

        $ops = @{
            ops = @(
                @{ op = "SetOptimizationRange"; blockId = $windowParam.blockName; paramInvariantName = "Window"; minValue = 10; maxValue = 100; step = 5 },
                @{ op = "SetOptimizationRange"; blockId = $thresholdParam.blockName; paramInvariantName = "Threshold"; minValue = 0.1; maxValue = 0.9; step = 0.05 }
            )
        } | ConvertTo-Json -Compress
        Invoke-RestMethod -Uri "http://localhost:5000/api/scripts/$s/ops" -Method POST -Body $ops -ContentType "application/json" | Out-Null

        # Step 2: Enable reinvestment via graph settings
        $reinvestOps = @{
            ops = @(
                @{ op = "SetScriptSettings"; settings = @{ UseCommissionInProfit = $true; InitDeposit = 1000 } }
            )
        } | ConvertTo-Json -Compress -Depth 3
        try {
            Invoke-RestMethod -Uri "http://localhost:5000/api/scripts/$s/settings" -Method POST -Body $reinvestOps -ContentType "application/json" | Out-Null
            Write-Host "  Reinvestment enabled"
        } catch {
            Write-Host "  Reinvestment via settings failed, trying alternative..."
        }

        # Step 3: Start optimization
        $optBody = @{
            scriptName = $s
            selectedParameterIds = @($windowParam.id, $thresholdParam.id)
            iterations = 15
        } | ConvertTo-Json -Compress

        $job = Invoke-RestMethod -Uri "http://localhost:5000/api/scripts/$s/optimization/start" -Method POST -Body $optBody -ContentType "application/json"
        $jobId = $job.data.jobId
        Write-Host "  Optimization started: $jobId"

        # Step 4: Wait for completion
        $maxWait = 120
        $waited = 0
        while ($waited -lt $maxWait) {
            Start-Sleep -Seconds 8
            $waited += 8
            $status = Invoke-RestMethod -Uri "http://localhost:5000/api/scripts/optimizations/$jobId" -Method GET
            if ($status.data.status -eq "Completed") {
                Write-Host "  Completed in ${waited}s"
                break
            }
        }

        # Step 5: Get and apply best result
        $best = Invoke-RestMethod -Uri "http://localhost:5000/api/scripts/$s/optimizations/$jobId/best?metric=NetProfit&rank=1" -Method GET
        $w = $best.data.parameterValues.Window
        $t = $best.data.parameterValues.Threshold
        $p = [math]::Round($best.data.netProfitPct * 100, 2)
        $wr = [math]::Round($best.data.winTradesPct, 1)
        $pf = [math]::Round($best.data.profitFactor, 3)

        Write-Host "  BEST: Window=$w Threshold=$t Profit=$p% Win=$wr% PF=$pf"

        Invoke-RestMethod -Uri "http://localhost:5000/api/scripts/$s/optimizations/$jobId/apply?metric=NetProfit&rank=1" -Method POST -Body "{}" -ContentType "application/json" | Out-Null

    } catch {
        Write-Host "  ERROR: $($_.Exception.Message)"
    }
}
