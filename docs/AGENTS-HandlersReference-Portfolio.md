# Handlers Reference: Portfolio

For each handler below:
- `typeName` is the string you pass to `/api/handlers/{typeName}` and `AddBlock` (`typeName` field).
- `blockType` is the container you must use for handler-based blocks (not template blocks).
- Input indices are zero-based (`toPort`).
- Hidden handlers (`[HandlerInvisible]`) require `allowHiddenHandler=true` in `AddBlock` (advanced). Some legacy helpers (e.g. `CycleHandler`) may be auto-converted to template blocks.

## AgentCurrentPosition

- Display name: Agent current position
- typeName: `AgentCurrentPosition`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Portfolio`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
This block shows a calculated position of an agent.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "AgentCurrentPosition1", "typeName": "AgentCurrentPosition", "blockType": "ConverterItem"
    }
  ]
}
```

## AgentHandlers

- Display name: Agents lots
- typeName: `AgentHandlers`
- Namespace: `TSLab.Script.Handlers.PortfolioHandlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Portfolio`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No English description is available in handler metadata; treat the name and IO contract as authoritative.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "AgentHandlers1", "typeName": "AgentHandlers", "blockType": "ConverterItem"
    }
  ]
}
```

## AgentsInfo

- Display name: Table Agents
- typeName: `AgentsInfo`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Portfolio`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Designed to work with the Agents table from a script.  Returns a numeric value corresponding to the selected table field.  Depending on the data provider, use the account or the account currency to determine whether the instrument belongs to the market.  For most markets, it is enough to specify a Ticker.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `AccountName` (`String`), title="Account", shown=`True`, optimizable=`True`, help="Account name (optional)."
- `AgentField` (`AgentField`), title="Output value", default=`Profit`, shown=`True`, optimizable=`True`, help="The output value from the table corresponding to the settings."
- `AgentName` (`String`), title="Agent", shown=`True`, optimizable=`True`, help="The name of the agent from the Agents table."
- `CurrencyName` (`String`), title="Currency", shown=`True`, optimizable=`True`, help="Account currency (optional)."
- `SecurityName` (`String`), title="Tiker", shown=`True`, optimizable=`True`, help="Instrument name."

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "AgentsInfo1", "typeName": "AgentsInfo", "blockType": "ConverterItem"
    }
  ]
}
```

## CurrentPosition

- Display name: Current position
- typeName: `CurrentPosition`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Portfolio`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Shows a total position involving an instrument. In laboratory mode this block shows a calculated position of a script. In agent mode this block shows a value of the Current column(in the Positions window) for tradable sources.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "CurrentPosition1", "typeName": "CurrentPosition", "blockType": "ConverterItem"
    }
  ]
}
```

## EstimatedMoney

- Display name: Portfolio estimation
- typeName: `EstimatedMoney`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Portfolio`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Shows your portfolio estimation. In agent mode portfolio estimation is received from your account. In laboratory mode portfolio estimation is calculated according the following formula: Portfolio Estimation = money + positions.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "EstimatedMoney1", "typeName": "EstimatedMoney", "blockType": "ConverterItem"
    }
  ]
}
```

## FreeMoney

- Display name: Free money
- typeName: `FreeMoney`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Portfolio`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Shows free money in your account. In agent mode information about free money is received from your account. In laboratory mode information about free money is calculated according to the following formula: Free Money = money - (minus)positions - (minus)money blocked in orders.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "FreeMoney1", "typeName": "FreeMoney", "blockType": "ConverterItem"
    }
  ]
}
```

## InitialDeposit

- Display name: Initial Deposit
- typeName: `InitialDeposit`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Portfolio`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The initial trading deposit from the script setting  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "InitialDeposit1", "typeName": "InitialDeposit", "blockType": "ConverterItem"
    }
  ]
}
```

## IsDataProviderConnected

- Display name: Data provider connected
- typeName: `IsDataProviderConnected`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Portfolio`
- Output: `BOOL` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The block returns true if the data provider is connected.  The block returns false if the data provider is not connected.  There is a forced delay of N seconds inside the block (configurable field).  That is, after connecting the provider, this block returns true after N seconds.

### Inputs
- [0] `Input0` accepts `SECURITY, OPTION, OPTION_SERIES` (required: `True`, stream-only: `True`)

### Parameters
- `Delay` (`int`), default=`20`, shown=`True`, optimizable=`True`, help="Delay (seconds)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "IsDataProviderConnected1", "typeName": "IsDataProviderConnected", "blockType": "ConverterItem"
    }
  ]
}
```

## IsPortfolioReady

- Display name: Portfolio is ready
- typeName: `IsPortfolioReady`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Portfolio`
- Output: `BOOL` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The portfolio is ready to trade (The data source is connected and the data is loaded)  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=BOOL

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "IsPortfolioReady1", "typeName": "IsPortfolioReady", "blockType": "ConverterItem"
    }
  ]
}
```

## NetValueByAccount

- Display name: Net value by account
- typeName: `NetValueByAccount`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Portfolio`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Get the total net value of the account. If the account is not specified, the account name is taken from the agent (only in agent mode).

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Account` (`String`), shown=`True`, optimizable=`True`, help="Account name (optional)."

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "NetValueByAccount1", "typeName": "NetValueByAccount", "blockType": "ConverterItem"
    }
  ]
}
```

## NumDaysProfit

- Display name: Profit (in N days)
- typeName: `NumDaysProfit`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Portfolio`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Calculates profit involving an instrument received during a specified number of days.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"
- `ProfitKind` (`ProfitKind`), title="Profit kind", default=`Unfixed`, shown=`True`, optimizable=`True`, help="Profit kind (fixed or unfixed)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "NumDaysProfit1", "typeName": "NumDaysProfit", "blockType": "ConverterItem"
    }
  ]
}
```

## NumMinutesProfit

- Display name: Profit (in N minutes)
- typeName: `NumMinutesProfit`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Portfolio`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Calculates profit involving an instrument received during a specified number of minutes.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"
- `ProfitKind` (`ProfitKind`), title="Profit kind", default=`Unfixed`, shown=`True`, optimizable=`True`, help="Profit kind (fixed or unfixed)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "NumMinutesProfit1", "typeName": "NumMinutesProfit", "blockType": "ConverterItem"
    }
  ]
}
```

## NumPositionsProfit

- Display name: Profit (in N positions)
- typeName: `NumPositionsProfit`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Portfolio`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Calculates profit involving an instrument received during a specified number of positions.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"
- `ProfitKind` (`ProfitKind`), title="Profit kind", default=`Unfixed`, shown=`True`, optimizable=`True`, help="Profit kind (fixed or unfixed)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "NumPositionsProfit1", "typeName": "NumPositionsProfit", "blockType": "ConverterItem"
    }
  ]
}
```

## PositionByName

- Display name: Position by name
- typeName: `PositionByName`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Portfolio`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Get the position value from the Positions table.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Account` (`String`), shown=`True`, optimizable=`True`, help="Account name (optional)."
- `Currency` (`String`), shown=`True`, optimizable=`True`, help="Currency name (optional)."
- `PositionField` (`PositionField`), title="Position field", default=`RealRest`, shown=`True`, optimizable=`True`, help="Output position field."
- `Symbol` (`String`), shown=`True`, optimizable=`True`, help="Symbol from the position table."

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "PositionByName1", "typeName": "PositionByName", "blockType": "ConverterItem"
    }
  ]
}
```

## WholeDayProfit

- Display name: Profit (one day period)
- typeName: `WholeDayProfit`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Portfolio`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Calculates profit involving an instrument received in all trades of the day.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- `ProfitKind` (`ProfitKind`), title="Profit kind", default=`Unfixed`, shown=`True`, optimizable=`True`, help="Profit kind (fixed or unfixed)"
- `SessionStart` (`TimeSpan`), title="Session start", default=`0:0:0`, range=`0:0:0`..`23:59:59` step `1:0:0`, shown=`True`, optimizable=`True`, help="Trading session start (format 1h 30m 00s)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "WholeDayProfit1", "typeName": "WholeDayProfit", "blockType": "ConverterItem"
    }
  ]
}
```

## WholeTimeProfit

- Display name: Profit (whole period)
- typeName: `WholeTimeProfit`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Portfolio`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Calculates profit involving an instrument received in all trades of the whole period.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- `Direction` (`TradeDirection2`), title="Direction trades", default=`All`, shown=`True`, optimizable=`True`
- `ProfitKind` (`ProfitKind`), title="Profit kind", default=`Unfixed`, shown=`True`, optimizable=`True`, help="Profit kind (fixed or unfixed)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "WholeTimeProfit1", "typeName": "WholeTimeProfit", "blockType": "ConverterItem"
    }
  ]
}
```

