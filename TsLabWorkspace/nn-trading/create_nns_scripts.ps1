# Create NN Trading scripts for missing instruments
$instruments = @(
    @{name="NN_SUI"; security="SUIUSDT_PERP"},
    @{name="NN_BCH"; security="BCHUSDT_PERP"},
    @{name="NN_TRX"; security="TRXUSDT_PERP"}
)

foreach ($inst in $instruments) {
    $body = @{
        name = $inst.name
        parentPath = "NN_Trading"
    } | ConvertTo-Json -Compress

    Write-Host "Creating $($inst.name)..."
    $r = Invoke-RestMethod -Uri "http://localhost:5000/api/script-manager/scripts" -Method POST -Body $body -ContentType "application/json"
    Write-Host "  Created: $($r.data.scriptName) (id=$($r.data.scriptId))"

    # Set instrument source
    $sourceBody = @{
        dataSourceName = "BinanceCoin-MFutures"
        securityId = $inst.security
        interval = "M15"
    } | ConvertTo-Json -Compress

    $r2 = Invoke-RestMethod -Uri "http://localhost:5000/api/scripts/$($inst.name)/instrument-source" -Method POST -Body $sourceBody -ContentType "application/json"
    Write-Host "  Mapped to $($inst.security) M15"
}
