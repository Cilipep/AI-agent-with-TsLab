# Handlers Reference: Position

For each handler below:
- `typeName` is the string you pass to `/api/handlers/{typeName}` and `AddBlock` (`typeName` field).
- `blockType` is the container you must use for handler-based blocks (not template blocks).
- Input indices are zero-based (`toPort`).
- Hidden handlers (`[HandlerInvisible]`) require `allowHiddenHandler=true` in `AddBlock` (advanced). Some legacy helpers (e.g. `CycleHandler`) may be auto-converted to template blocks.

## AverageExitPrice

- Display name: Average exit price
- typeName: `AverageExitPrice`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The average exit price of a position. If there was only one exit, then it is equal to the exit price. If there have been position changes, it returns the weighted average exit price (taking into account the quantities).

### Inputs
- [0] `POSITIONSource` accepts `POSITION` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "AverageExitPrice1", "typeName": "AverageExitPrice", "blockType": "ConverterItem"
    }
  ]
}
```

## BalancedPrice

- Display name: Average entry price
- typeName: `BalancedPrice`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
An average position entry price.  Inputs/Output: Inputs=POSITIONSource(POSITION); Output=DOUBLE

### Inputs
- [0] `POSITIONSource` accepts `POSITION` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BalancedPrice1", "typeName": "BalancedPrice", "blockType": "ConverterItem"
    }
  ]
}
```

## BalancedPriceBySecurity

- Display name: Average entry price (by security)
- typeName: `BalancedPriceBySecurity`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
An average position exit price.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- `PositionSide` (`BalancePositionSide`), title="Position side", default=`Long`, shown=`True`, optimizable=`True`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BalancedPriceBySecurity1", "typeName": "BalancedPriceBySecurity", "blockType": "ConverterItem"
    }
  ]
}
```

## BarsHeld

- Display name: Bars held
- typeName: `BarsHeld`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Returns the number of bars to hold the position.  Inputs/Output: Inputs=POSITIONSource(POSITION); Output=DOUBLE

### Inputs
- [0] `POSITIONSource` accepts `POSITION` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BarsHeld1", "typeName": "BarsHeld", "blockType": "ConverterItem"
    }
  ]
}
```

## CalcEntryPrice

- Display name: Entry price (estimated)
- typeName: `CalcEntryPrice`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The calculated price of the trade at which the position was opened. In the laboratory mode it is equal to the opening price of the bar following the signal.

### Inputs
- [0] `POSITIONSource` accepts `POSITION` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "CalcEntryPrice1", "typeName": "CalcEntryPrice", "blockType": "ConverterItem"
    }
  ]
}
```

## CloseVirtualFutPosition

- Display name: Close Virtual Pos
- typeName: `CloseVirtualFutPosition`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `Position`
- Output: `UNKNOWN` (outputs: `0`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Close virtual fut position in base asset  Inputs/Output: Inputs=Input0(POSITION); Output=UNKNOWN

### Inputs
- [0] `Input0` accepts `POSITION` (required: `True`, stream-only: `True`)

### Parameters
- `FixedPx` (`Double`), title="Fixed Price", default=`125000`, shown=`True`, optimizable=`True`, help="Exit price for virtual futures position"
- `TimeToLive` (`Double`), title="Time to Live", default=`15`, shown=`True`, optimizable=`True`, help="Position lifetime (in minutes)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "CloseVirtualFutPosition1", "typeName": "CloseVirtualFutPosition", "blockType": "ConverterItem"
    }
  ]
}
```

## DaysInPosition

- Display name: Days in position
- typeName: `DaysInPosition`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The number of days in position.  Inputs/Output: Inputs=POSITIONSource(POSITION); Output=DOUBLE

### Inputs
- [0] `POSITIONSource` accepts `POSITION` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "DaysInPosition1", "typeName": "DaysInPosition", "blockType": "ConverterItem"
    }
  ]
}
```

## DrawdownHandler

- Display name: Drawdown
- typeName: `DrawdownHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Calculations:  Drawdown = Profit - MaxFixProfit  Drawdown% = Drawdown / InitialDeposit * 100  Drawdown duration (days) = Profit < MaxFixProfit ? Duration++ : 0  FixDrawdown = FixProfit - MaxFixProfit  FixDrawdown% = FixDrawdown / InitialDeposit * 100

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- `DrawdownKind` (`DrawdownKind`), title="Drawdown kind", default=`DrawdownAbs`, shown=`True`, optimizable=`True`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "DrawdownHandler1", "typeName": "DrawdownHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## DrowdownCount

- Display name: Losses running
- typeName: `DrowdownCount`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Calculates the number of consecutive loss positions.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "DrowdownCount1", "typeName": "DrowdownCount", "blockType": "ConverterItem"
    }
  ]
}
```

## EntryDate

- Display name: Entry date
- typeName: `EntryDate`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
A date of position entry presented as number in YYMMDD format.  Inputs/Output: Inputs=POSITIONSource(POSITION); Output=DOUBLE

### Inputs
- [0] `POSITIONSource` accepts `POSITION` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "EntryDate1", "typeName": "EntryDate", "blockType": "ConverterItem"
    }
  ]
}
```

## EntryPrice

- Display name: Entry price
- typeName: `EntryPrice`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
In the laboratory mode, the price of the deal at which the position was opened.  In real trading mode, the average price of transactions for the placed order.  If the transaction prices are unknown, the price is taken from the order. If the order was placed with the "by market" type, then the price of 0 or the price of the upper or lower limit (for futures) for the instrument is taken.

### Inputs
- [0] `POSITIONSource` accepts `POSITION` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "EntryPrice1", "typeName": "EntryPrice", "blockType": "ConverterItem"
    }
  ]
}
```

## EntryTime

- Display name: Entry time
- typeName: `EntryTime`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Time of  position entry presented as number in HHMMSS format.  Inputs/Output: Inputs=POSITIONSource(POSITION); Output=DOUBLE

### Inputs
- [0] `POSITIONSource` accepts `POSITION` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "EntryTime1", "typeName": "EntryTime", "blockType": "ConverterItem"
    }
  ]
}
```

## HasLongPositionActive

- Display name: There is active long position
- typeName: `HasLongPositionActive`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `BOOL` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The Boolean function verifying if there is an active long position.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=BOOL

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "HasLongPositionActive1", "typeName": "HasLongPositionActive", "blockType": "ConverterItem"
    }
  ]
}
```

## HasPositionActive

- Display name: There is active position
- typeName: `HasPositionActive`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `BOOL` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The Boolean function verifying that there is an active position.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=BOOL

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "HasPositionActive1", "typeName": "HasPositionActive", "blockType": "ConverterItem"
    }
  ]
}
```

## HasShortPositionActive

- Display name: There is active short position
- typeName: `HasShortPositionActive`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `BOOL` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The Boolean function verifying that there is an active short position.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=BOOL

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "HasShortPositionActive1", "typeName": "HasShortPositionActive", "blockType": "ConverterItem"
    }
  ]
}
```

## HasTwoLoss

- Display name: 2 losses successively
- typeName: `HasTwoLoss`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `BOOL` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
2 or more consecutive loss positions.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=BOOL

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "HasTwoLoss1", "typeName": "HasTwoLoss", "blockType": "ConverterItem"
    }
  ]
}
```

## HoldSignalForNBars

- Display name: Hold signal for N bars
- typeName: `HoldSignalForNBars`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `BOOL` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Holds a signal TRUE for some number of bars.  Inputs/Output: Inputs=Input0(BOOL); Output=BOOL

### Inputs
- [0] `Input0` accepts `BOOL` (required: `True`, stream-only: `False`)

### Parameters
- `NBars` (`int`), title="Bars count", default=`0`, range=`0`..`10` step `1`, shown=`True`, optimizable=`True`, help="Hold signal for N bars"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "HoldSignalForNBars1", "typeName": "HoldSignalForNBars", "blockType": "ConverterItem"
    }
  ]
}
```

## IsItLossAtLastPosition

- Display name: Last closed position was unprofitable
- typeName: `IsItLossAtLastPosition`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `BOOL` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Check if a closed position was unprofitable.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=BOOL

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "IsItLossAtLastPosition1", "typeName": "IsItLossAtLastPosition", "blockType": "ConverterItem"
    }
  ]
}
```

## LastClosedIsLong

- Display name: Last position has been closed and it was long
- typeName: `LastClosedIsLong`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `BOOL` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The latest position has been closed and it was long.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=BOOL

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "LastClosedIsLong1", "typeName": "LastClosedIsLong", "blockType": "ConverterItem"
    }
  ]
}
```

## LastClosedIsLong2

- Display name: Last closed position was long
- typeName: `LastClosedIsLong2`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `BOOL` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The Boolean function verifying that the latest closed position was long.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=BOOL

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "LastClosedIsLong21", "typeName": "LastClosedIsLong2", "blockType": "ConverterItem"
    }
  ]
}
```

## LastClosedIsShort

- Display name: Last position has been closed and it was short
- typeName: `LastClosedIsShort`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `BOOL` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The latest position has been closed and it was short.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=BOOL

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "LastClosedIsShort1", "typeName": "LastClosedIsShort", "blockType": "ConverterItem"
    }
  ]
}
```

## LastClosedIsShort2

- Display name: Last closed position was short
- typeName: `LastClosedIsShort2`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `BOOL` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The Boolean function verifying that the latest closed position was short.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=BOOL

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "LastClosedIsShort21", "typeName": "LastClosedIsShort2", "blockType": "ConverterItem"
    }
  ]
}
```

## LastClosedNamePositionAvgExitPrice

- Display name: Average exit price last position by name
- typeName: `LastClosedNamePositionAvgExitPrice`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Average exit price last position by name.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- `Name` (`String`), shown=`True`, optimizable=`False`, help="Position opening signal name"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "LastClosedNamePositionAvgExitPrice1", "typeName": "LastClosedNamePositionAvgExitPrice", "blockType": "ConverterItem"
    }
  ]
}
```

## LastClosedNamePositionExitDate

- Display name: Exit date of last closed named position
- typeName: `LastClosedNamePositionExitDate`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The exit date of the latest closed named position (a number with format YYMMDD).  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- `Name` (`String`), shown=`True`, optimizable=`False`, help="Position opening signal name"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "LastClosedNamePositionExitDate1", "typeName": "LastClosedNamePositionExitDate", "blockType": "ConverterItem"
    }
  ]
}
```

## LastClosedNamePositionExitPrice

- Display name: Exit price of last closed named position
- typeName: `LastClosedNamePositionExitPrice`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The exit price of the latest closed named position.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- `Name` (`String`), shown=`True`, optimizable=`False`, help="Position opening signal name"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "LastClosedNamePositionExitPrice1", "typeName": "LastClosedNamePositionExitPrice", "blockType": "ConverterItem"
    }
  ]
}
```

## LastClosedNamePositionExitTime

- Display name: Exit time of last closed named position
- typeName: `LastClosedNamePositionExitTime`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The exit time of the latest closed named position (a number with format HHMMSS).  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- `Name` (`String`), shown=`True`, optimizable=`False`, help="Position opening signal name"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "LastClosedNamePositionExitTime1", "typeName": "LastClosedNamePositionExitTime", "blockType": "ConverterItem"
    }
  ]
}
```

## LastClosedPositionDate

- Display name: Date of last closed position
- typeName: `LastClosedPositionDate`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The date of the latest closed position (a number with format YYMMDD).  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "LastClosedPositionDate1", "typeName": "LastClosedPositionDate", "blockType": "ConverterItem"
    }
  ]
}
```

## LastClosedPositionExitBarNumber

- Display name: Exit bar number of last closed position
- typeName: `LastClosedPositionExitBarNumber`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The exit bar number of the latest closed position.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "LastClosedPositionExitBarNumber1", "typeName": "LastClosedPositionExitBarNumber", "blockType": "ConverterItem"
    }
  ]
}
```

## LastClosedPositionExitDate

- Display name: Exit date of last closed position
- typeName: `LastClosedPositionExitDate`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The exit date of the latest closed position (a number with format YYMMDD).  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "LastClosedPositionExitDate1", "typeName": "LastClosedPositionExitDate", "blockType": "ConverterItem"
    }
  ]
}
```

## LastClosedPositionExitTime

- Display name: Exit time of last closed position
- typeName: `LastClosedPositionExitTime`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The exit time of the latest closed position (a number with format HHMMSS).  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "LastClosedPositionExitTime1", "typeName": "LastClosedPositionExitTime", "blockType": "ConverterItem"
    }
  ]
}
```

## LastClosedPositionTime

- Display name: Time of last closed position
- typeName: `LastClosedPositionTime`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The time of the latest closed position (a number with format HHMMSS).  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "LastClosedPositionTime1", "typeName": "LastClosedPositionTime", "blockType": "ConverterItem"
    }
  ]
}
```

## LastExitAvgPrice

- Display name: Average exit price last position
- typeName: `LastExitAvgPrice`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Average exit price last position.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "LastExitAvgPrice1", "typeName": "LastExitAvgPrice", "blockType": "ConverterItem"
    }
  ]
}
```

## LastExitPrice

- Display name: Last exit price
- typeName: `LastExitPrice`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The price of the latest exit.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "LastExitPrice1", "typeName": "LastExitPrice", "blockType": "ConverterItem"
    }
  ]
}
```

## MAE

- Display name: MAE
- typeName: `MAE`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Maximum Adverse Excursion per one contract/lot.  Inputs/Output: Inputs=POSITIONSource(POSITION); Output=DOUBLE

### Inputs
- [0] `POSITIONSource` accepts `POSITION` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "MAE1", "typeName": "MAE", "blockType": "ConverterItem"
    }
  ]
}
```

## MAEPct

- Display name: MAE %
- typeName: `MAEPct`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Maximum Adverse Excursion per one contract/lot (as percents).  Inputs/Output: Inputs=POSITIONSource(POSITION); Output=DOUBLE

### Inputs
- [0] `POSITIONSource` accepts `POSITION` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "MAEPct1", "typeName": "MAEPct", "blockType": "ConverterItem"
    }
  ]
}
```

## Median

- Display name: Equity Drawdown
- typeName: `Median`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Shows deviation of the income curved line from the median.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Median1", "typeName": "Median", "blockType": "ConverterItem"
    }
  ]
}
```

## MFE

- Display name: MFE
- typeName: `MFE`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Maximum Favorable Excursion per one contract/lot.  Inputs/Output: Inputs=POSITIONSource(POSITION); Output=DOUBLE

### Inputs
- [0] `POSITIONSource` accepts `POSITION` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "MFE1", "typeName": "MFE", "blockType": "ConverterItem"
    }
  ]
}
```

## MFEPct

- Display name: MFE %
- typeName: `MFEPct`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Maximum Favorable Excursion per one contract/lot (as percents).  Inputs/Output: Inputs=POSITIONSource(POSITION); Output=DOUBLE

### Inputs
- [0] `POSITIONSource` accepts `POSITION` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "MFEPct1", "typeName": "MFEPct", "blockType": "ConverterItem"
    }
  ]
}
```

## MinutesInPosition

- Display name: Minutes in position
- typeName: `MinutesInPosition`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The number of minutes in position.  Inputs/Output: Inputs=POSITIONSource(POSITION); Output=DOUBLE

### Inputs
- [0] `POSITIONSource` accepts `POSITION` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "MinutesInPosition1", "typeName": "MinutesInPosition", "blockType": "ConverterItem"
    }
  ]
}
```

## OpenVirtualFutPosition

- Display name: Open Virtual Pos
- typeName: `OpenVirtualFutPosition`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `Position`
- Output: `POSITION` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Open virtual position in base asset (stream handler)  Inputs/Output: Inputs=AnyOption(SECURITY, OPTION, OPTION_SERIES); Output=POSITION

### Inputs
- [0] `AnyOption` accepts `SECURITY, OPTION, OPTION_SERIES` (required: `True`, stream-only: `True`)

### Parameters
- `FixedPx` (`Double`), title="Price", default=`120000`, shown=`True`, optimizable=`True`, help="Entry price of this virtual position"
- `FixedQty` (`int`), title="Size", default=`1`, shown=`True`, optimizable=`True`, help="Entry size of this virtual position"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "OpenVirtualFutPosition1", "typeName": "OpenVirtualFutPosition", "blockType": "ConverterItem"
    }
  ]
}
```

## PosActiveNameExit

- Display name: Last exit has such name
- typeName: `PosActiveNameExit`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `BOOL` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The parameter allows to give name the block Position Close. The value of this block is true if the last close for the instrument had this name.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- `Name` (`String`), shown=`True`, optimizable=`False`, help="Close signal name"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "PosActiveNameExit1", "typeName": "PosActiveNameExit", "blockType": "ConverterItem"
    }
  ]
}
```

## PositionChangeEntryBarNumber

- Display name: Changed Position Entry Bar Number
- typeName: `PositionChangeEntryBarNumber`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Shows entry bar number of a changed complex position.  Inputs/Output: Inputs=POSITIONSource(POSITION); Output=DOUBLE

### Inputs
- [0] `POSITIONSource` accepts `POSITION` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "PositionChangeEntryBarNumber1", "typeName": "PositionChangeEntryBarNumber", "blockType": "ConverterItem"
    }
  ]
}
```

## PositionChangeEntryPrice

- Display name: Changed Position Entry Price
- typeName: `PositionChangeEntryPrice`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Shows last entry price of a changed complex position. If none handler returns zero.  Inputs/Output: Inputs=POSITIONSource(POSITION); Output=DOUBLE

### Inputs
- [0] `POSITIONSource` accepts `POSITION` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "PositionChangeEntryPrice1", "typeName": "PositionChangeEntryPrice", "blockType": "ConverterItem"
    }
  ]
}
```

## PositionChangeExitBarNumber

- Display name: Changed Position Exit Bar Number
- typeName: `PositionChangeExitBarNumber`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Shows exit bar number of a changed complex position.  Inputs/Output: Inputs=POSITIONSource(POSITION); Output=DOUBLE

### Inputs
- [0] `POSITIONSource` accepts `POSITION` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "PositionChangeExitBarNumber1", "typeName": "PositionChangeExitBarNumber", "blockType": "ConverterItem"
    }
  ]
}
```

## PositionChangeExitPrice

- Display name: Changed Position Exit Price
- typeName: `PositionChangeExitPrice`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Shows last exit price of a changed complex position. If none handler returns zero.  Inputs/Output: Inputs=POSITIONSource(POSITION); Output=DOUBLE

### Inputs
- [0] `POSITIONSource` accepts `POSITION` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "PositionChangeExitPrice1", "typeName": "PositionChangeExitPrice", "blockType": "ConverterItem"
    }
  ]
}
```

## PositionEntryBarNumber

- Display name: Position Entry Bar Number
- typeName: `PositionEntryBarNumber`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Shows a complex position entry bar number.  Inputs/Output: Inputs=POSITIONSource(POSITION); Output=DOUBLE

### Inputs
- [0] `POSITIONSource` accepts `POSITION` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "PositionEntryBarNumber1", "typeName": "PositionEntryBarNumber", "blockType": "ConverterItem"
    }
  ]
}
```

## PositionExitBarNumber

- Display name: Position Entry Current Bar Number
- typeName: `PositionExitBarNumber`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Visibility: hidden (`[HandlerInvisible]`) - avoid using in new scripts unless you know what you are doing.
- AddBlock requires: `allowHiddenHandler=true` (advanced).
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Returns the number of the current bar when opening positions (in the history of all position openings)

### Inputs
- [0] `POSITIONSource` accepts `POSITION` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "PositionExitBarNumber1", "typeName": "PositionExitBarNumber", "blockType": "ConverterItem", "allowHiddenHandler": true
    }
  ]
}
```

## PositionIsVirtualClosedHandler

- Display name: Position Is Virtually Closed
- typeName: `PositionIsVirtualClosedHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `BOOL` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Is position has virtual close (calculated only)?  Inputs/Output: Inputs=POSITIONSource(POSITION); Output=BOOL

### Inputs
- [0] `POSITIONSource` accepts `POSITION` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "PositionIsVirtualClosedHandler1", "typeName": "PositionIsVirtualClosedHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## PositionIsVirtualHandler

- Display name: Position Is Virtual
- typeName: `PositionIsVirtualHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `BOOL` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
A handler returns TRUE if input position is virtual.  Inputs/Output: Inputs=POSITIONSource(POSITION); Output=BOOL

### Inputs
- [0] `POSITIONSource` accepts `POSITION` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "PositionIsVirtualHandler1", "typeName": "PositionIsVirtualHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## PositionShares

- Display name: Position size (initial)
- typeName: `PositionShares`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Returns initial position size  Inputs/Output: Inputs=POSITIONSource(POSITION); Output=DOUBLE

### Inputs
- [0] `POSITIONSource` accepts `POSITION` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "PositionShares1", "typeName": "PositionShares", "blockType": "ConverterItem"
    }
  ]
}
```

## PositionSharesByBar

- Display name: Quantity
- typeName: `PositionSharesByBar`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Returns current size of position in lots at every bar.  Inputs/Output: Inputs=POSITIONSource(POSITION); Output=DOUBLE

### Inputs
- [0] `POSITIONSource` accepts `POSITION` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "PositionSharesByBar1", "typeName": "PositionSharesByBar", "blockType": "ConverterItem"
    }
  ]
}
```

## Profit

- Display name: Profit
- typeName: `Profit`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Profit (loss) given by the position in absolute values. Calculated per one contract/lot.  Inputs/Output: Inputs=POSITIONSource(POSITION); Output=DOUBLE

### Inputs
- [0] `POSITIONSource` accepts `POSITION` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Profit1", "typeName": "Profit", "blockType": "ConverterItem"
    }
  ]
}
```

## ProfitPct

- Display name: Profit %
- typeName: `ProfitPct`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Profit (loss) given by the position in percentage valu.Calculated per one contract/lot.  Inputs/Output: Inputs=POSITIONSource(POSITION); Output=DOUBLE

### Inputs
- [0] `POSITIONSource` accepts `POSITION` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "ProfitPct1", "typeName": "ProfitPct", "blockType": "ConverterItem"
    }
  ]
}
```

## ProfitsCount

- Display name: Profits running
- typeName: `ProfitsCount`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Calculates the number of consecutive profit positions.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "ProfitsCount1", "typeName": "ProfitsCount", "blockType": "ConverterItem"
    }
  ]
}
```

## TrailStop

- Display name: Trail stop
- typeName: `TrailStop`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
This block is identical to 'Trailing stop absolute', but its parameters are in the percentage value.

### Inputs
- [0] `POSITIONSource` accepts `POSITION` (required: `True`, stream-only: `False`)

### Parameters
- `StopLoss` (`Double`), title="Stop loss", default=`1.5`, range=`0.1`..`5` step `0.1`, shown=`True`, optimizable=`True`, help="Initial stop loss"
- `TrailEnable` (`Double`), title="Trail enable", default=`0.5`, range=`0.1`..`3` step `0.1`, shown=`True`, optimizable=`True`, help="Where to start actual trailing"
- `TrailLoss` (`Double`), title="Trail loss", default=`0.5`, range=`0.1`..`3` step `0.1`, shown=`True`, optimizable=`True`, help="Trail loss"
- `UseCalcPrice` (`bool`), title="Use calc price", default=`false`, shown=`True`, optimizable=`False`, help="Use calculated price"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TrailStop1", "typeName": "TrailStop", "blockType": "ConverterItem"
    }
  ]
}
```

## TrailStopAbs

- Display name: Trail stop absolute
- typeName: `TrailStopAbs`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Position`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The trailing stop, the values are given in absolute numbers. The block has 3 parameters describing 2 modes of functioning. [br]The 1st mode: Stop-loss is described as stop-loss, which sets the maximum fall (in case of short - growth) of the price you can accept. This fall is set in numbers. [br]The 2nd mode is selected if the price grows (in case of short the price falls) according to the value set in the parameter 'Enable Trail'. In other word he profit is being trailed. [br]The parameter 'Use the Calculated Price' allows to calculate Stop from the calculated opening price. In the Laboratory mode this is the opening price of the bar following the signal. In the real trade mode this is the price of position opening. Disabling this parameter causes using the real price received during the trading session. [br]The calculated price cannot be calculated if the box 'By Market at Fixed Price' is selected and slippage higher than 0 is set.

### Inputs
- [0] `POSITIONSource` accepts `POSITION` (required: `True`, stream-only: `False`)

### Parameters
- `StopLoss` (`Double`), title="Stop loss", default=`150`, range=`10`..`500` step `5`, shown=`True`, optimizable=`True`, help="Initial stop loss"
- `TrailEnable` (`Double`), title="Trail enable", default=`50`, range=`10`..`500` step `5`, shown=`True`, optimizable=`True`, help="Where to start actual trailing"
- `TrailLoss` (`Double`), title="Trail loss", default=`50`, range=`10`..`500` step `5`, shown=`True`, optimizable=`True`, help="Trail loss"
- `UseCalcPrice` (`bool`), title="Use calc price", default=`false`, shown=`True`, optimizable=`False`, help="Use calculated price"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TrailStopAbs1", "typeName": "TrailStopAbs", "blockType": "ConverterItem"
    }
  ]
}
```

