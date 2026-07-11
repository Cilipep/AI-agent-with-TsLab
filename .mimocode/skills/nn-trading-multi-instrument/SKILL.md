# Skill: NN Trading Multi-Instrument Setup

## When to use
- Setting up TSLab scripts for multiple instruments
- Configuring money management across instruments
- Batch configuring lab-options

## Workflow

### 1. Create scripts for all instruments
```powershell
$instruments = @("NEARUSDT", "XLMUSDT", "SOLUSDT", "AAVEUSDT")
foreach ($inst in $instruments) {
    $name = "NN_$($inst.Replace('USDT',''))"
    ./create-script.ps1 $name
}
```

### 2. Set instrument source
```powershell
$scripts = @("NN_NEAR", "NN_XLM", "NN_SOL", "NN_AAVE")
$symbols = @("NEARUSD_PERP", "XLMUSD_PERP", "SOLUSD_PERP", "AAVEUSD_PERP")
for ($i=0; $i -lt $scripts.Length; $i++) {
    @{
        dataSourceName = "BinanceCoin-MFutures"
        securityId = $symbols[$i]
        interval = "15m"
    } | ConvertTo-Json | Set-Content "./tmp/src.json"
    ./script-api.ps1 POST $scripts[$i] instrument-source "./tmp/src.json"
}
```

### 3. Configure money management
```powershell
$scripts = @("NN_AAVE", "NN_SOL", "NN_XLM", "NN_NEAR")
foreach ($script in $scripts) {
    @{
        initDeposit = 70
        tradeMode = 1
        rtUpdates = $true
        useDateFrom = $false
        useDateTo = $false
    } | ConvertTo-Json | Set-Content "./tmp/money.json"
    ./script-api.ps1 POST $script lab-options "./tmp/money.json"
}
```

### 4. Add trading blocks (NN_Prediction, Greater, Less, etc.)
Use batch ops to add all blocks at once.

### 5. Repair and build
```powershell
foreach ($script in $scripts) {
    ./script-api.ps1 POST $script repair/authoring-quality
    ./script-api.ps1 POST $script build
    ./script-api.ps1 POST $script load
}
```

## Money Management Parameters
| Parameter | Value | Description |
|-----------|-------|-------------|
| initDeposit | 70 | USDT |
| tradeMode | 1 | Live |
| Risk per trade | 1%-20% | Configurable in UI |
| Leverage | 1x-30x | Configurable in UI |
| Reinvest | 10-50% | Configurable in UI |

## Files
- Script names: NN_{SYMBOL} (e.g., NN_AAVE, NN_SOL)
- Data source: BinanceCoin-MFutures
- Security format: {SYMBOL}USD_PERP (e.g., AAVEUSD_PERP)
