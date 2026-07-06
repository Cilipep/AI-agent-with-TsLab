<#
.SYNOPSIS
    Drawdown circuit breaker for TSLab strategies.

.DESCRIPTION
    Monitors strategy drawdown and triggers alerts or stops when thresholds are breached.
    Can be run as a monitoring script or integrated into live trading.

.PARAMETER ScriptName
    Name of the TSLab script to monitor.

.PARAMETER MaxDrawdownPct
    Maximum allowed drawdown percentage (default: 20%).

.PARAMETER WarningDrawdownPct
    Warning threshold percentage (default: 15%).

.PARAMETER CheckInterval
    Interval in seconds between checks (default: 60).

.PARAMETER AlertMethod
    Method for alerts: 'log', 'console', 'file' (default: 'console').

.EXAMPLE
    .\circuit_breaker.ps1 -ScriptName "RSICCIBot" -MaxDrawdownPct 20
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$ScriptName,
    
    [Parameter(Mandatory=$false)]
    [double]$MaxDrawdownPct = 20,
    
    [Parameter(Mandatory=$false)]
    [double]$WarningDrawdownPct = 15,
    
    [Parameter(Mandatory=$false)]
    [int]$CheckInterval = 60,
    
    [Parameter(Mandatory=$false)]
    [string]$AlertMethod = "console",
    
    [Parameter(Mandatory=$false)]
    [string]$AlertLogFile = "./circuit_breaker_alerts.log",
    
    [Parameter(Mandatory=$false)]
    [switch]$AutoStop
)

$ErrorActionPreference = "Stop"
$BaseUrl = "http://localhost:5000/api"

# State tracking
$script:peakEquity = 0
$script:currentDrawdown = 0
$script:alerts = @()
$script:isStopped = $false

function Write-Alert {
    param(
        [string]$Level,
        [string]$Message
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $alert = "[$timestamp] [$Level] $Message"
    
    switch ($AlertMethod) {
        "console" {
            $color = switch ($Level) {
                "WARNING" { "Yellow" }
                "CRITICAL" { "Red" }
                "INFO" { "Green" }
                default { "White" }
            }
            Write-Host $alert -ForegroundColor $color
        }
        "file" {
            Add-Content -Path $AlertLogFile -Value $alert
        }
        "log" {
            Write-Output $alert
        }
    }
    
    $script:alerts += $alert
}

function Get-StrategyMetrics {
    param([string]$ScriptName)
    
    try {
        $metrics = Invoke-RestMethod -Uri "$BaseUrl/scripts/$ScriptName/metrics-summary" -Method Get
        
        if ($metrics.success) {
            return $metrics.data
        }
    }
    catch {
        Write-Alert "WARNING" "Failed to get metrics: $_"
    }
    
    return $null
}

function Check-Drawdown {
    param(
        [string]$ScriptName,
        [double]$MaxDD,
        [double]$WarningDD
    )
    
    $metrics = Get-StrategyMetrics -ScriptName $ScriptName
    
    if ($null -eq $metrics) {
        return
    }
    
    # Calculate current drawdown from metrics
    $netProfit = $metrics.netProfit
    $maxDrawdown = $metrics.maxDrawdownPct
    
    # Update peak equity (simplified - in real implementation track actual equity)
    if ($netProfit -gt $script:peakEquity) {
        $script:peakEquity = $netProfit
    }
    
    # Calculate drawdown
    if ($script:peakEquity -gt 0) {
        $script:currentDrawdown = (($script:peakEquity - $netProfit) / $script:peakEquity) * 100
    }
    
    # Check thresholds
    if ($script:currentDrawdown -ge $MaxDD) {
        Write-Alert "CRITICAL" "MAX DRAWDOWN BREACHED: $($script:currentDrawdown)% >= $MaxDD%"
        
        if ($AutoStop) {
            Write-Alert "CRITICAL" "Auto-stopping strategy due to max drawdown breach"
            Stop-Strategy -ScriptName $ScriptName
            $script:isStopped = $true
        }
        
        return "CRITICAL"
    }
    elseif ($script:currentDrawdown -ge $WarningDD) {
        Write-Alert "WARNING" "Drawdown warning: $($script:currentDrawdown)% >= $WarningDD%"
        return "WARNING"
    }
    else {
        if ($script:currentDrawdown -lt 1) {
            Write-Alert "INFO" "Drawdown normal: $($script:currentDrawdown)%"
        }
        return "OK"
    }
}

function Stop-Strategy {
    param([string]$ScriptName)
    
    try {
        # Close any open positions
        $closeResult = Invoke-RestMethod -Uri "$BaseUrl/scripts/$ScriptName/close-editor" -Method Post
        
        if ($closeResult.success) {
            Write-Alert "INFO" "Strategy $ScriptName stopped successfully"
        }
        else {
            Write-Alert "WARNING" "Failed to stop strategy: $($closeResult.message)"
        }
    }
    catch {
        Write-Alert "WARNING" "Error stopping strategy: $_"
    }
}

function Monitor-Strategy {
    param(
        [string]$ScriptName,
        [int]$Interval,
        [double]$MaxDD,
        [double]$WarningDD
    )
    
    Write-Alert "INFO" "Starting circuit breaker monitoring for $ScriptName"
    Write-Alert "INFO" "Max Drawdown: $MaxDD% | Warning: $WarningDD% | Interval: ${Interval}s"
    
    while (-not $script:isStopped) {
        $status = Check-Drawdown -ScriptName $ScriptName -MaxDD $MaxDD -WarningDD $WarningDD
        
        if ($status -eq "CRITICAL" -and $AutoStop) {
            Write-Alert "INFO" "Circuit breaker triggered - stopping monitoring"
            break
        }
        
        Start-Sleep -Seconds $Interval
    }
}

function Get-MonitoringSummary {
    return @{
        script_name = $ScriptName
        max_drawdown_pct = $MaxDrawdownPct
        warning_drawdown_pct = $WarningDrawdownPct
        check_interval = $CheckInterval
        auto_stop = $AutoStop.IsPresent
        peak_equity = $script:peakEquity
        current_drawdown = $script:currentDrawdown
        is_stopped = $script:isStopped
        alert_count = $script:alerts.Count
        alerts = $script:alerts
    }
}

# Main execution
Write-Host "=== Drawdown Circuit Breaker ===" -ForegroundColor Cyan
Write-Host "Script: $ScriptName"
Write-Host "Max Drawdown: $MaxDrawdownPct% | Warning: $WarningDrawdownPct%"
Write-Host "Auto-Stop: $AutoStop"

# Initial metrics check
Write-Host "`nChecking initial strategy state..."
$initialMetrics = Get-StrategyMetrics -ScriptName $ScriptName

if ($null -ne $initialMetrics) {
    Write-Host "Current Net Profit: $($initialMetrics.netProfit)"
    Write-Host "Current Max Drawdown: $($initialMetrics.maxDrawdownPct)%"
    $script:peakEquity = $initialMetrics.netProfit
}

# Start monitoring
Monitor-Strategy -ScriptName $ScriptName -Interval $CheckInterval -MaxDD $MaxDrawdownPct -WarningDD $WarningDrawdownPct

# Output summary
Write-Host "`n=== Monitoring Summary ===" -ForegroundColor Cyan
$summary = Get-MonitoringSummary
Write-Host "Total Alerts: $($summary.alert_count)"
Write-Host "Final Drawdown: $($summary.current_drawdown)%"
Write-Host "Stopped: $($summary.is_stopped)"

# Save summary
$summaryPath = "./circuit_breaker_summary_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$summary | ConvertTo-Json -Depth 10 | Out-File -FilePath $summaryPath
Write-Host "`nSummary saved to: $summaryPath"

return $summary
