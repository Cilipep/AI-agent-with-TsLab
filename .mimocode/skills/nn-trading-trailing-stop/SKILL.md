# Skill: NN Trading Trailing Stop Setup

## When to use
- Adding trailing stop to TSLab trading scripts
- Configuring stop loss and take profit levels
- Setting up protective exits

## Workflow

### 1. Remove old stop blocks
```powershell
@{
    ops = @(
        @{op = "RemoveBlock"; blockId = "StopFormula"},
        @{op = "RemoveBlock"; blockId = "ProfitFormula"},
        @{op = "RemoveBlock"; blockId = "StopLoss"},
        @{op = "RemoveBlock"; blockId = "TakeProfit"},
        @{op = "RemoveBlock"; blockId = "Close"}
    )
} | ConvertTo-Json -Depth 3 | Set-Content "./tmp/ops.json"
./script-api.ps1 POST $script ops "./tmp/ops.json"
```

### 2. Add trailing stop blocks
```powershell
@{
    ops = @(
        @{op = "AddBlock"; blockId = "Close"; typeName = "Close"},
        @{op = "AddBlock"; blockId = "EntryPrice"; typeName = "EntryPrice"},
        @{op = "AddBlock"; blockId = "StopLevel"; typeName = "DoubleCustomHandlerItem";
         params = @{Expression = "EntryPrice * 0.97"}},
        @{op = "AddBlock"; blockId = "TrailLevel"; typeName = "DoubleCustomHandlerItem";
         params = @{Expression = "Close * 0.985"}},
        @{op = "AddBlock"; blockId = "ProfitLevel"; typeName = "DoubleCustomHandlerItem";
         params = @{Expression = "EntryPrice * 1.04"}},
        @{op = "AddBlock"; blockId = "StopLoss"; blockType = "ClosePositionByStopItem"},
        @{op = "AddBlock"; blockId = "TakeProfit"; blockType = "ClosePositionByProfitItem"}
    )
} | ConvertTo-Json -Depth 3 | Set-Content "./tmp/ops.json"
./script-api.ps1 POST $script ops "./tmp/ops.json"
```

### 3. Connect blocks
```powershell
@{
    ops = @(
        @{op = "ConnectByInputName"; fromBlockId = "OpenLong"; toBlockId = "StopLoss"; toInputName = "Pos"},
        @{op = "ConnectByInputName"; fromBlockId = "StopLevel"; fromPort = "Value"; toBlockId = "StopLoss"; toInputName = "Prc"},
        @{op = "ConnectByInputName"; fromBlockId = "OpenLong"; toBlockId = "TakeProfit"; toInputName = "Pos"},
        @{op = "ConnectByInputName"; fromBlockId = "ProfitLevel"; fromPort = "Value"; toBlockId = "TakeProfit"; toInputName = "Prc"},
        @{op = "ConnectByInputName"; fromBlockId = "OpenLong"; toBlockId = "EntryPrice"; toInputName = "Position"},
        @{op = "ConnectByInputName"; fromBlockId = "EntryPrice"; fromPort = "Value"; toBlockId = "StopLevel"; toInputName = "Input0"},
        @{op = "ConnectByInputName"; fromBlockId = "EntryPrice"; fromPort = "Value"; toBlockId = "ProfitLevel"; toInputName = "Input0"}
    )
} | ConvertTo-Json -Depth 3 | Set-Content "./tmp/ops.json"
./script-api.ps1 POST $script ops "./tmp/ops.json"
```

### 4. Repair and build
```powershell
./script-api.ps1 POST $script repair/authoring-quality
./script-api.ps1 POST $script build
./script-api.ps1 POST $script load
```

## Stop Levels
| Level | Formula | Description |
|-------|---------|-------------|
| StopLevel | EntryPrice * 0.97 | Stop loss at -3% from entry |
| ProfitLevel | EntryPrice * 1.04 | Take profit at +4% from entry |
| TrailLevel | Close * 0.985 | Trailing stop at -1.5% from current |

## Graph Structure
```
OpenLong ──▶ EntryPrice ──▶ StopLevel (Entry * 0.97) ──▶ StopLoss
                           ProfitLevel (Entry * 1.04) ──▶ TakeProfit
Close ──▶ TrailLevel (Close * 0.985)
```

## Common Errors
- `MissingFormulaInput` → Connect EntryPrice to StopLevel/ProfitLevel Input0
- `IncompatibleTypes` → Use Close block (not Src) for DOUBLE inputs
