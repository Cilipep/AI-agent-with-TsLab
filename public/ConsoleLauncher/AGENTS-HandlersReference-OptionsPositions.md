# Handlers Reference: OptionsPositions

For each handler below:
- `typeName` is the string you pass to `/api/handlers/{typeName}` and `AddBlock` (`typeName` field).
- `blockType` is the container you must use for handler-based blocks (not template blocks).
- Input indices are zero-based (`toPort`).
- Hidden handlers (`[HandlerInvisible]`) require `allowHiddenHandler=true` in `AddBlock` (advanced). Some legacy helpers (e.g. `CycleHandler`) may be auto-converted to template blocks.

## AutoHedger

- Display name: Auto Hedge Delta
- typeName: `AutoHedger`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `4`, max `4`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Hedge delta by time (on every script execution)  Inputs/Output: Inputs=FutPx(DOUBLE), Delta(DOUBLE), OptionSeries(SECURITY, OPTION_SERIES), Permission(BOOL); Output=DOUBLE

### Inputs
- [0] `FutPx` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Delta` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [2] `OptionSeries` accepts `SECURITY, OPTION_SERIES` (required: `True`, stream-only: `False`)
- [3] `Permission` accepts `BOOL` (required: `True`, stream-only: `False`)

### Parameters
- `BuyPrice` (`OptimProperty`), title="Buy price", default=`0`, range=`0`..`1000000.0` step `1.0`, shown=`True`, optimizable=`True`, help="Price of hedge order to buy"
- `BuyShift` (`Double`), title="Buy shift", default=`0`, range=`-1000000.0`..`1000000.0` step `1.0`, shown=`True`, optimizable=`True`, help="Buy shift (price steps)"
- `DownDelta` (`OptimProperty`), title="Down Delta", default=`-1.0`, range=`-1000000.0`..`0` step `1.0`, shown=`True`, optimizable=`True`, help="Possible delta decrease from target level"
- `HedgeDelta` (`bool`), title="Align Delta", default=`False`, shown=`True`, optimizable=`True`, help="Align delta to target level"
- `MinPeriod` (`Double`), title="Period", default=`0`, range=`0`..`1000000.0` step `1.0`, shown=`True`, optimizable=`True`, help="Hedge period (seconds)"
- `SellPrice` (`OptimProperty`), title="Sell price", default=`0`, range=`0`..`1000000.0` step `1.0`, shown=`True`, optimizable=`True`, help="Price of hedge order to sell"
- `SellShift` (`Double`), title="Sell shift", default=`0`, range=`-1000000.0`..`1000000.0` step `1.0`, shown=`True`, optimizable=`True`, help="Sell shift (price steps)"
- `SensitivityPct` (`Double`), title="Sensitivity Pct", default=`66`, range=`50`..`100` step `1`, shown=`True`, optimizable=`True`, help="Delta should pass this percent of distance to next integer value to align"
- `TargetDelta` (`OptimProperty`), title="Target Delta", default=`0.0`, range=`-1000000.0`..`1000000.0` step `1.0`, shown=`True`, optimizable=`True`, help="Target delta"
- `UpDelta` (`OptimProperty`), title="Up Delta", default=`-1.0`, range=`0`..`1000000.0` step `1.0`, shown=`True`, optimizable=`True`, help="Possible delta increase from target level"
- `WorkWithoutOptions` (`bool`), title="Work without options", default=`False`, shown=`True`, optimizable=`True`, help="Permission to work without options"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "AutoHedger1", "typeName": "AutoHedger", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## BlackScholesDelta

- Display name: Single Series Delta (book)
- typeName: `BlackScholesDelta`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `3`, max `3`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Straigtforward calculation of delta (as in books)  Inputs/Output: Inputs=Time(DOUBLE), Smile(INTERACTIVESPLINE), OptionSeries(OPTION_SERIES); Output=INTERACTIVESPLINE

### Inputs
- [0] `Time` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [2] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `MaxStrike` (`Double`), title="Max strike", default=`1500000`, range=`0`..`10000000` step `1`, shown=`True`, optimizable=`False`, help="Max strike to be processed by handler"
- `MinStrike` (`Double`), title="Min strike", default=`1`, range=`0`..`10000000` step `1`, shown=`True`, optimizable=`False`, help="Min strike to be processed by handler"
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `StrikeStep` (`Double`), title="Strike step", default=`2500`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`False`, help="Strike step"
- `TooltipFormat` (`String`), title="Tooltip format", default=`0.00`, shown=`True`, optimizable=`True`, help="Tooltip format (i.e. '0.00', '0.0##' etc)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BlackScholesDelta1", "typeName": "BlackScholesDelta", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## BlackScholesGreeks

- Display name: Single Series Greeks (book)
- typeName: `BlackScholesGreeks`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `3`, max `3`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Straigtforward calculation of greeks (as in books)  Inputs/Output: Inputs=Time(DOUBLE), Smile(INTERACTIVESPLINE), OptionSeries(OPTION_SERIES); Output=INTERACTIVESPLINE

### Inputs
- [0] `Time` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [2] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `Greek` (`Greeks`), default=`Theta`, shown=`True`, optimizable=`True`, help="Greek to be calculated (delta, theta, vega, gamma, etc)"
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `SigmaMult` (`Double`), title="Width multiplier", default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Width multiplier"
- `TooltipFormat` (`String`), title="Tooltip Format", default=`0.000`, shown=`True`, optimizable=`True`, help="Tooltip format (i.e. '0.00', '0.0##' etc)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BlackScholesGreeks1", "typeName": "BlackScholesGreeks", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## BuyOptionGroup

- Display name: Buy option group
- typeName: `BuyOptionGroup`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `8`, max `8`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Buy many options while position risk is 'small'  Inputs/Output: Inputs=Permission(DOUBLE, BOOL), Strike(DOUBLE), Current Risk(DOUBLE), Max Risk(DOUBLE), Smile(INTERACTIVESPLINE), OptionSeries(OPTION_SERIES), Call Risk(DOUBLE), Put Risk(DOUBLE); Output=DOUBLE

### Inputs
- [0] `Permission` accepts `DOUBLE, BOOL` (required: `True`, stream-only: `False`)
- [1] `Strike` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [2] `Current Risk` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [3] `Max Risk` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [4] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [5] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)
- [6] `Call Risk` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [7] `Put Risk` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `EntryShift` (`int`), title="Entry shift", default=`0`, range=`-1000000`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Entry shift to get lower buy price (price step)"
- `ExitShift` (`int`), title="Exit shift", default=`0`, range=`-1000000`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Exit shift to get quick execution (price step)"
- `FixedQty` (`int`), title="Order size", default=`1`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Order size"
- `OptionType` (`StrikeType`), title="Option type", default=`Any`, shown=`True`, optimizable=`True`, help="Limit trading to options of given type (call, put, both)"
- `StrikeAmount` (`int`), title="Strike amount", default=`0`, range=`0`..`10000000` step `1`, shown=`True`, optimizable=`True`, help="Strike amount to set your orders (up and down from the central strike)"
- `StrikeStep` (`Double`), title="Strike step", default=`0`, range=`0`..`10000000` step `1`, shown=`True`, optimizable=`True`, help="Strike step to extract the most important options"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BuyOptionGroup1", "typeName": "BuyOptionGroup", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## BuyOptionGroupDelta

- Display name: Buy option group (delta range)
- typeName: `BuyOptionGroupDelta`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `9`, max `9`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Buy many options while position risk is 'small' (strike range is set in units of delta)  Inputs/Output: Inputs=Permission(DOUBLE, BOOL), Strike(DOUBLE), Current Risk(DOUBLE), Max Risk(DOUBLE), Smile(INTERACTIVESPLINE), OptionSeries(OPTION_SERIES), Call delta(INTERACTIVESPLINE), Call Risk(DOUBLE), Put Risk(DOUBLE); Output=DOUBLE

### Inputs
- [0] `Permission` accepts `DOUBLE, BOOL` (required: `True`, stream-only: `False`)
- [1] `Strike` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [2] `Current Risk` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [3] `Max Risk` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [4] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [5] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)
- [6] `Call delta` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [7] `Call Risk` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [8] `Put Risk` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `CheckAbsDelta` (`bool`), title="Check absolute delta", default=`true`, shown=`True`, optimizable=`True`, help="Check absolute value of option's delta"
- `EntryShift` (`int`), title="Entry shift", default=`0`, range=`-1000000`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Entry shift to get lower buy price (price step)"
- `ExitShift` (`int`), title="Exit shift", default=`0`, range=`-1000000`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Exit shift to get quick execution (price step)"
- `FixedQty` (`int`), title="Order size", default=`1`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Order size"
- `MaxDeltaPct` (`int`), title="Max delta, %", default=`0`, range=`-1000`..`1000` step `1`, shown=`True`, optimizable=`True`, help="The highest working delta we allow to quote (as percents)"
- `MinDeltaPct` (`int`), title="Min delta, %", default=`0`, range=`-1000`..`1000` step `1`, shown=`True`, optimizable=`True`, help="The lowest working delta we allow to quote (as percents)"
- `StrikeStep` (`Double`), title="Strike step", default=`0`, range=`0`..`10000000` step `1`, shown=`True`, optimizable=`True`, help="Strike step to extract the most important options"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BuyOptionGroupDelta1", "typeName": "BuyOptionGroupDelta", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## BuyOptions

- Display name: Buy Options
- typeName: `BuyOptions`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `8`, max `8`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Buy options while position risk is 'small'  Inputs/Output: Inputs=Permission(DOUBLE, BOOL), Strike(DOUBLE), Current Risk(DOUBLE), Max Risk(DOUBLE), Smile(INTERACTIVESPLINE), OptionSeries(OPTION_SERIES), Call Risk(DOUBLE), Put Risk(DOUBLE); Output=DOUBLE

### Inputs
- [0] `Permission` accepts `DOUBLE, BOOL` (required: `True`, stream-only: `False`)
- [1] `Strike` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [2] `Current Risk` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [3] `Max Risk` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [4] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [5] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)
- [6] `Call Risk` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [7] `Put Risk` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `EntryShift` (`int`), title="Entry shift", default=`0`, range=`-1000000`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Entry shift to get lower buy price (price step)"
- `ExitShift` (`int`), title="Exit shift", default=`0`, range=`-1000000`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Exit shift to get quick execution (price step)"
- `FixedQty` (`int`), title="Order size", default=`1`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Order size"
- `OptionType` (`StrikeType`), title="Option type", default=`Call`, shown=`True`, optimizable=`True`, help="Limit trading to options of given type (call, put, both)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BuyOptions1", "typeName": "BuyOptions", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## CloseVirtualPosition

- Display name: Close Virtual Pos (bar)
- typeName: `CloseVirtualPosition`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `UNKNOWN` (outputs: `0`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Close virtual position (bar handler)  Inputs/Output: Inputs=Input0(POSITION); Output=UNKNOWN

### Inputs
- [0] `Input0` accepts `POSITION` (required: `True`, stream-only: `False`)

### Parameters
- `FixedPx` (`Double`), title="Fixed Price", default=`125000`, shown=`True`, optimizable=`True`, help="Exit price for virtual position"
- `TimeToLive` (`Double`), title="Time to Live", default=`15`, shown=`True`, optimizable=`True`, help="Position lifetime (in minutes)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "CloseVirtualPosition1", "typeName": "CloseVirtualPosition", "blockType": "ConverterItem"
    }
  ]
}
```

## CombinePositionProfiles

- Display name: Combine Series Profiles
- typeName: `CombinePositionProfiles`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Add 2 position profiles  Inputs/Output: Inputs=Profile1(INTERACTIVESPLINE), Profile2(INTERACTIVESPLINE); Output=INTERACTIVESPLINE

### Inputs
- [0] `Profile1` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [1] `Profile2` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "CombinePositionProfiles1", "typeName": "CombinePositionProfiles", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## CurrentFutPx

- Display name: Current Fut Px
- typeName: `CurrentFutPx`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `3`, max `3`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Draws a vertical line in the chart. A vertical position is connected to any given Interactive Series.

### Inputs
- [0] `FutPx` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `ReferenceLine` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [2] `AnyOption` accepts `SECURITY, OPTION, OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `MinHeight` (`Double`), title="Min Height", default=`0.03`, range=`0`..`10000000` step `1`, shown=`True`, optimizable=`False`, help="Minimum height of the marker (absolute units)"
- `OffsetPct` (`Double`), title="Offset, %", default=`10`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`False`, help="Height of the marker (percents)"
- `Qty` (`int`), title="Size", default=`1`, range=`-1000000`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Trade quantity. Negative value reverts the signal."
- `TooltipFormat` (`String`), title="Tooltip format", default=`P2`, shown=`True`, optimizable=`False`, help="Tooltip format (i.e. '0.00', '0.0##', 'P2' etc)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "CurrentFutPx1", "typeName": "CurrentFutPx", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## DropVirtualPositions

- Display name: Clear Virtual Positions
- typeName: `DropVirtualPositions`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `UNKNOWN` (outputs: `0`, only-value-output: `True`)
- Inputs: min `0`, max `0`
- AddBlock container: `ZeroInputItem`

### What It Does
This block allows you to delete virtual positions. Connect Delete positions property to Control Pane and create a button.

### Inputs
- (none)

### Parameters
- `DropPositions` (`bool`), title="Drop Positions", default=`False`, shown=`True`, optimizable=`True`, help="Drop virtual positions"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "DropVirtualPositions1", "typeName": "DropVirtualPositions", "blockType": "ZeroInputItem"
    }
  ]
}
```

## FixedCommission

- Display name: Fixed Commission
- typeName: `FixedCommission`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `UNKNOWN` (outputs: `0`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Fixed commission (it can apply 'scalper discount' available in MOEX)  Inputs/Output: Inputs=OPTIONSource(OPTION); Output=UNKNOWN

### Inputs
- [0] `OPTIONSource` accepts `OPTION` (required: `True`, stream-only: `True`)

### Parameters
- `FutCommission` (`Double`), title="Futures commission", default=`0.8`, range=`0`..`10000000` step `1`, shown=`True`, optimizable=`True`, help="Futures commission"
- `OptCommission` (`Double`), title="Option commission", default=`1.6`, range=`0`..`10000000` step `1`, shown=`True`, optimizable=`True`, help="Option commission"
- `ScalpingRule` (`bool`), title="Scalping Discount", default=`true`, shown=`True`, optimizable=`True`, help="Apply 'scalper discount' available in MOEX"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "FixedCommission1", "typeName": "FixedCommission", "blockType": "ConverterItem"
    }
  ]
}
```

## MarketMakerDelta

- Display name: Market maker (delta range)
- typeName: `MarketMakerDelta`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `9`, max `9`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Buy and sell options while position risk is 'small' (strike range is set in units of delta)  Inputs/Output: Inputs=Permission(DOUBLE, BOOL), Strike(DOUBLE), Current Risk(DOUBLE), Max Risk(DOUBLE), Smile(INTERACTIVESPLINE), OptionSeries(OPTION_SERIES), Call delta(INTERACTIVESPLINE), Call Risk(DOUBLE), Put Risk(DOUBLE); Output=DOUBLE

### Inputs
- [0] `Permission` accepts `DOUBLE, BOOL` (required: `True`, stream-only: `False`)
- [1] `Strike` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [2] `Current Risk` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [3] `Max Risk` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [4] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [5] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)
- [6] `Call delta` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [7] `Call Risk` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [8] `Put Risk` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `CheckAbsDelta` (`bool`), title="Check absolute delta", default=`true`, shown=`True`, optimizable=`True`, help="Check absolute value of option's delta"
- `EntryShift` (`int`), title="Shift, p.s.", default=`0`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Shift to get better buy or sell price (price steps)"
- `EntryShiftIvPct` (`Double`), title="Shift, %", default=`0`, range=`0`..`1000000` step `0.5`, shown=`True`, optimizable=`True`, help="Shift to get better buy or sell price (percents of volatility)"
- `FixedQty` (`int`), title="Order size", default=`1`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Order size"
- `LiquidProAlgo` (`bool`), title="Force all quotes", default=`false`, shown=`True`, optimizable=`True`, help="Set all quotes at all strikes (this mode is convinient with the Liquid.Pro service)"
- `MaxContractsOnStrike` (`int`), title="Max contracts at strike", default=`0`, range=`0`..`10000000` step `10`, shown=`True`, optimizable=`True`, help="Maximum amount of contracts at the single strike (absolute value)"
- `MaxDeltaPct` (`int`), title="Max delta, %", default=`0`, range=`-1000`..`1000` step `1`, shown=`True`, optimizable=`True`, help="The highest working delta we allow to quote (as percents)"
- `MinDeltaPct` (`int`), title="Min delta, %", default=`0`, range=`-1000`..`1000` step `1`, shown=`True`, optimizable=`True`, help="The lowest working delta we allow to quote (as percents)"
- `StrikeStep` (`Double`), title="Strike step", default=`0`, range=`0`..`10000000` step `1`, shown=`True`, optimizable=`True`, help="Strike step to extract the most important options"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "MarketMakerDelta1", "typeName": "MarketMakerDelta", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## NumericalDeltaOnF

- Display name: Numerical Delta ATM
- typeName: `NumericalDeltaOnF`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `4`, max `4`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Numerical estimate of delta at-the-money (only one point is processed; bar handler)  Inputs/Output: Inputs=FutPx(DOUBLE), Time(DOUBLE), Smile(INTERACTIVESPLINE), OptionSeries(OPTION_SERIES); Output=DOUBLE

### Inputs
- [0] `FutPx` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Time` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [2] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [3] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `Delta` (`OptimProperty`), default=`0`, shown=`True`, optimizable=`True`, help="Current delta (just to show it on ControlPane)"
- `GreekAlgo` (`NumericalGreekAlgo`), title="Greek Algo", default=`ShiftingSmile`, shown=`True`, optimizable=`True`, help="FrozenSmile - smile is frozen; ShiftingSmile - smile shifts horizontally without modification"
- `HedgeDelta` (`bool`), title="Align Delta", default=`False`, shown=`True`, optimizable=`True`, help="Align delta (just to make button on ControlPane)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "NumericalDeltaOnF1", "typeName": "NumericalDeltaOnF", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## NumericalDeltaOnF2

- Display name: Numerical Delta ATM v2
- typeName: `NumericalDeltaOnF2`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `4`, max `4`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Numerical estimate of delta at-the-money (only one point is processed; stream handler)  Inputs/Output: Inputs=FutPx(DOUBLE), Time(DOUBLE), Smile(INTERACTIVESPLINE), OptionSeries(OPTION_SERIES); Output=DOUBLE

### Inputs
- [0] `FutPx` accepts `DOUBLE` (required: `True`, stream-only: `True`)
- [1] `Time` accepts `DOUBLE` (required: `True`, stream-only: `True`)
- [2] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `True`)
- [3] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `True`)

### Parameters
- `Delta` (`OptimProperty`), default=`0`, shown=`True`, optimizable=`True`, help="Current delta (just to show it on ControlPane)"
- `GreekAlgo` (`NumericalGreekAlgo`), title="Greek Algo", default=`ShiftingSmile`, shown=`True`, optimizable=`True`, help="FrozenSmile - smile is frozen; ShiftingSmile - smile shifts horizontally without modification"
- `HedgeDelta` (`bool`), title="Align Delta", default=`False`, shown=`True`, optimizable=`True`, help="Align delta (just to make button on ControlPane)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "NumericalDeltaOnF21", "typeName": "NumericalDeltaOnF2", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## NumericalDeltaOnF3

- Display name: Numerical Delta ATM (IntSer)
- typeName: `NumericalDeltaOnF3`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Numerical estimate of delta at-the-money (only one point is processed using delta profile)  Inputs/Output: Inputs=DeltaProfile(INTERACTIVESPLINE), OptionSeries(OPTION_SERIES); Output=DOUBLE

### Inputs
- [0] `DeltaProfile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [1] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `Delta` (`OptimProperty`), default=`0`, shown=`True`, optimizable=`True`, help="Current delta (just to show it on ControlPane)"
- `HedgeDelta` (`bool`), title="Align Delta", default=`False`, shown=`True`, optimizable=`True`, help="Align delta (just to make button on ControlPane)"
- `PrintDeltaInLog` (`bool`), title="Print in Log", default=`False`, shown=`True`, optimizable=`True`, help="Print delta in main log"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "NumericalDeltaOnF31", "typeName": "NumericalDeltaOnF3", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## NumericalGammaOnF

- Display name: Numerical Gamma ATM
- typeName: `NumericalGammaOnF`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `4`, max `4`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Numerical estimate of gamma at-the-money (only one point is processed; bar handler)  Inputs/Output: Inputs=FutPx(DOUBLE), Time(DOUBLE), Smile(INTERACTIVESPLINE), OptionSeries(OPTION_SERIES); Output=DOUBLE

### Inputs
- [0] `FutPx` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Time` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [2] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [3] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `Gamma` (`OptimProperty`), default=`0`, shown=`True`, optimizable=`True`, help="Current gamma (just to show it on ControlPane)"
- `GreekAlgo` (`NumericalGreekAlgo`), title="Greek Algo", default=`ShiftingSmile`, shown=`True`, optimizable=`True`, help="FrozenSmile - smile is frozen; ShiftingSmile - smile shifts horizontally without modification"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "NumericalGammaOnF1", "typeName": "NumericalGammaOnF", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## NumericalGammaOnF3

- Display name: Numerical Gamma ATM (IntSer)
- typeName: `NumericalGammaOnF3`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Numerical estimate of gamma at-the-money (only one point is processed using gamma profile)  Inputs/Output: Inputs=GammaProfile(INTERACTIVESPLINE); Output=DOUBLE

### Inputs
- [0] `GammaProfile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)

### Parameters
- `Gamma` (`OptimProperty`), default=`0`, shown=`True`, optimizable=`True`, help="Current gamma (just to show it on ControlPane)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "NumericalGammaOnF31", "typeName": "NumericalGammaOnF3", "blockType": "ConverterItem"
    }
  ]
}
```

## NumericalThetaOnF

- Display name: Numerical Theta ATM
- typeName: `NumericalThetaOnF`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `4`, max `4`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Numerical estimate of theta at-the-money (only one point is processed)  Inputs/Output: Inputs=FutPx(DOUBLE), Time(DOUBLE), Smile(INTERACTIVESPLINE), OptionSeries(OPTION_SERIES); Output=DOUBLE

### Inputs
- [0] `FutPx` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Time` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [2] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [3] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `DistanceMode` (`TimeRemainMode`), title="Estimation algo", default=`PlainCalendar`, shown=`True`, optimizable=`True`, help="Algorythm to estimate time-to-expiry"
- `GreekAlgo` (`NumericalGreekAlgo`), title="Greek Algo", default=`ShiftingSmile`, shown=`True`, optimizable=`True`, help="FrozenSmile - smile is frozen; ShiftingSmile - smile shifts horizontally without modification"
- `Theta` (`OptimProperty`), default=`0`, shown=`True`, optimizable=`True`, help="Current theta (just to show it on ControlPane)"
- `TStep` (`Double`), title="Time Step", default=`0.00001`, range=`0`..`1000000` step `0.00001`, shown=`True`, optimizable=`True`, help="Time step for numerical derivative"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "NumericalThetaOnF1", "typeName": "NumericalThetaOnF", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## NumericalVegaOnF

- Display name: Numerical Vega ATM
- typeName: `NumericalVegaOnF`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `4`, max `4`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Numerical estimate of vega at-the-money (only one point is processed)  Inputs/Output: Inputs=FutPx(DOUBLE), Time(DOUBLE), Smile(INTERACTIVESPLINE), OptionSeries(OPTION_SERIES); Output=DOUBLE

### Inputs
- [0] `FutPx` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Time` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [2] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [3] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `GreekAlgo` (`NumericalGreekAlgo`), title="Greek algo", default=`ShiftingSmile`, shown=`True`, optimizable=`True`, help="FrozenSmile - smile is frozen; ShiftingSmile - smile shifts horizontally without modification"
- `SigmaStep` (`Double`), title="Sigma step", default=`0.0001`, range=`0.000001`..`1000000` step `0.0001`, shown=`True`, optimizable=`True`, help="Sigma step for numerical derivative"
- `Vega` (`OptimProperty`), default=`0`, shown=`True`, optimizable=`True`, help="Current vega (just to show it on ControlPane)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "NumericalVegaOnF1", "typeName": "NumericalVegaOnF", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## NumericalVommaOnF

- Display name: Numerical Vomma ATM
- typeName: `NumericalVommaOnF`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `4`, max `4`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Numerical estimate of vomma at-the-money (only one point is processed)  Inputs/Output: Inputs=FutPx(DOUBLE), Time(DOUBLE), Smile(INTERACTIVESPLINE), OptionSeries(OPTION_SERIES); Output=DOUBLE

### Inputs
- [0] `FutPx` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Time` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [2] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [3] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `GreekAlgo` (`NumericalGreekAlgo`), title="Greek algo", default=`ShiftingSmile`, shown=`True`, optimizable=`True`, help="FrozenSmile - smile is frozen; ShiftingSmile - smile shifts horizontally without modification"
- `SigmaStep` (`Double`), title="Sigma step", default=`0.0001`, range=`0.000001`..`1000000` step `0.0001`, shown=`True`, optimizable=`True`, help="Sigma step for numerical derivative"
- `Vomma` (`OptimProperty`), default=`0`, shown=`True`, optimizable=`True`, help="Current vomma (just to show it on ControlPane)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "NumericalVommaOnF1", "typeName": "NumericalVommaOnF", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## OpenVirtualFutPosition2

- Display name: Open Virtual Fut Pos (bar)
- typeName: `OpenVirtualFutPosition2`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `POSITION` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Open virtual position in base asset (bar handler)  Inputs/Output: Inputs=AnyOption(SECURITY, OPTION, OPTION_SERIES); Output=POSITION

### Inputs
- [0] `AnyOption` accepts `SECURITY, OPTION, OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `FixedPx` (`Double`), title="Price", default=`120000`, shown=`True`, optimizable=`True`, help="Entry price of this virtual position"
- `FixedQty` (`int`), title="Size", default=`1`, shown=`True`, optimizable=`True`, help="Entry size of this virtual position"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "OpenVirtualFutPosition21", "typeName": "OpenVirtualFutPosition2", "blockType": "ConverterItem"
    }
  ]
}
```

## OpenVirtualOptPosition

- Display name: Open Virtual Opt Pos
- typeName: `OpenVirtualOptPosition`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `POSITION` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Open virtual position in option (stream handler)  Inputs/Output: Inputs=OptionSeries(OPTION_SERIES); Output=POSITION

### Inputs
- [0] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `True`)

### Parameters
- `FixedPx` (`Double`), title="Price", default=`10000`, shown=`True`, optimizable=`True`, help="Entry price of this virtual position"
- `FixedQty` (`int`), title="Size", default=`-1`, shown=`True`, optimizable=`True`, help="Entry size of this virtual position"
- `FixedStrike` (`Double`), title="Strike", default=`120000`, shown=`True`, optimizable=`True`, help="Strike of this virtual position"
- `OptionType` (`StrikeType`), title="Option Type", default=`Call`, shown=`True`, optimizable=`True`, help="Option type (parameter Any is not recommended)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "OpenVirtualOptPosition1", "typeName": "OpenVirtualOptPosition", "blockType": "ConverterItem"
    }
  ]
}
```

## OpenVirtualOptPosition2

- Display name: Open Virtual Opt Pos (bar)
- typeName: `OpenVirtualOptPosition2`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `POSITION` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Open virtual position in options (bar handler)  Inputs/Output: Inputs=OptionSeries(OPTION_SERIES); Output=POSITION

### Inputs
- [0] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `FixedPx` (`Double`), title="Price", default=`10000`, shown=`True`, optimizable=`True`, help="Entry price of this virtual position"
- `FixedQty` (`int`), title="Size", default=`-1`, shown=`True`, optimizable=`True`, help="Entry size of this virtual position"
- `FixedStrike` (`Double`), title="Strike", default=`120000`, shown=`True`, optimizable=`True`, help="Strike of this virtual position"
- `OptionType` (`StrikeType`), title="Option Type", default=`Call`, shown=`True`, optimizable=`True`, help="Option type (parameter Any is not recommended)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "OpenVirtualOptPosition21", "typeName": "OpenVirtualOptPosition2", "blockType": "ConverterItem"
    }
  ]
}
```

## OptionsBoardNumericalDelta

- Display name: Options board numerical delta
- typeName: `OptionsBoardNumericalDelta`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `4`, max `4`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Estimate delta as function of strikes with numerical differentiation  Inputs/Output: Inputs=FutPx(DOUBLE), Time(DOUBLE), Smile(INTERACTIVESPLINE), OptionSeries(OPTION_SERIES); Output=INTERACTIVESPLINE

### Inputs
- [0] `FutPx` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Time` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [2] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [3] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `FixedQty` (`int`), title="Size", default=`100`, shown=`True`, optimizable=`False`, help="Entry size of this virtual position"
- `GreekAlgo` (`NumericalGreekAlgo`), title="Greek algo", default=`ShiftingSmile`, shown=`True`, optimizable=`True`, help="FrozenSmile - smile is frozen; ShiftingSmile - smile shifts horizontally without modification"
- `OptionType` (`StrikeType`), title="Option Type", default=`Call`, shown=`True`, optimizable=`False`, help="Option type (parameter Any is not recommended)"
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `SigmaMult` (`Double`), title="Width multiplier", default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Width multiplier"
- `TooltipFormat` (`String`), title="Tooltip format", default=`0.00`, shown=`True`, optimizable=`False`, help="Tooltip format (i.e. '0.00', '0.0##' etc)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "OptionsBoardNumericalDelta1", "typeName": "OptionsBoardNumericalDelta", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## OptionsBoardNumericalGamma

- Display name: Options board numerical gamma
- typeName: `OptionsBoardNumericalGamma`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `UNKNOWN` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Estimate gamma as function of strikes with numerical differentiation  Inputs/Output: Output=UNKNOWN

### Inputs
- [0] `Input0` accepts `UNKNOWN` (required: `True`, stream-only: `False`)

### Parameters
- `FixedQty` (`int`), default=`100`, shown=`True`, optimizable=`False`
- `GreekAlgo` (`NumericalGreekAlgo`), title="Greek algo", default=`ShiftingSmile`, shown=`True`, optimizable=`True`, help="FrozenSmile - smile is frozen; ShiftingSmile - smile shifts horizontally without modification"
- `OptionType` (`StrikeType`), title="Option Type", default=`Call`, shown=`True`, optimizable=`False`, help="Option type (parameter Any is not recommended)"
- `ShowNodes` (`bool`), title="Show Nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `SigmaMult` (`Double`), title="Width Multiplier", default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Width Multiplier"
- `TooltipFormat` (`String`), title="Tooltip format", default=`0.000000`, shown=`True`, optimizable=`False`, help="Tooltip format (i.e. '0.00', '0.0##' etc)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "OptionsBoardNumericalGamma1", "typeName": "OptionsBoardNumericalGamma", "blockType": "ConverterItem"
    }
  ]
}
```

## OwnOrders

- Display name: Own orders
- typeName: `OwnOrders`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `4`, max `4`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Own active orders  Inputs/Output: Inputs=FutPx(DOUBLE), Time(DOUBLE), OptionSeries(OPTION_SERIES), RiskFreeRate(DOUBLE); Output=INTERACTIVESPLINE

### Inputs
- [0] `FutPx` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Time` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [2] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)
- [3] `RiskFreeRate` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `ShowLongOrders` (`bool`), title="Show long", default=`false`, shown=`True`, optimizable=`True`, help="Show long or short orders"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "OwnOrders1", "typeName": "OwnOrders", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## OwnPositionIv

- Display name: Own position IV (num)
- typeName: `OwnPositionIv`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `5`, max `5`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Own position IV (effective volatility that makes current profit to become zero)  Inputs/Output: Inputs=FutPx(DOUBLE), Time(DOUBLE), Smile(INTERACTIVESPLINE), OptionSeries(OPTION_SERIES), RiskFreeRate(DOUBLE); Output=DOUBLE

### Inputs
- [0] `FutPx` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Time` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [2] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [3] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)
- [4] `RiskFreeRate` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `DisplayIv` (`OptimProperty`), title="Display IV", default=`0`, shown=`True`, optimizable=`True`, help="Effective position volatility (only to display at UI)"
- `DisplayUnits` (`FixedValueMode`), title="Display units", default=`AsIs`, shown=`True`, optimizable=`False`, help="Display units (hundreds, thousands, as is)"
- `ShowLongPositions` (`bool`), title="Show long", default=`false`, shown=`True`, optimizable=`True`, help="Show long or short positions"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "OwnPositionIv1", "typeName": "OwnPositionIv", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## OwnPositionIvLine

- Display name: Own position IV (line)
- typeName: `OwnPositionIvLine`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `5`, max `5`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Own position IV (effective volatility that makes current profit to become zero)  Inputs/Output: Inputs=FutPx(DOUBLE), Time(DOUBLE), Smile(INTERACTIVESPLINE), OptionSeries(OPTION_SERIES), RiskFreeRate(DOUBLE); Output=INTERACTIVESPLINE

### Inputs
- [0] `FutPx` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Time` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [2] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [3] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)
- [4] `RiskFreeRate` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `DisplayIv` (`OptimProperty`), title="Display IV", default=`0`, shown=`True`, optimizable=`True`, help="Effective position volatility (only to display at UI)"
- `DisplayUnits` (`FixedValueMode`), title="Display units", default=`AsIs`, shown=`True`, optimizable=`False`, help="Display units (hundreds, thousands, as is)"
- `ShowLongPositions` (`bool`), title="Show long", default=`false`, shown=`True`, optimizable=`True`, help="Show long or short positions"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "OwnPositionIvLine1", "typeName": "OwnPositionIvLine", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## PositionsManager

- Display name: Positions Manager
- typeName: `PositionsManager`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `OPTION` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Manager for virtual and real positions  Inputs/Output: Inputs=OPTIONSource(OPTION); Output=OPTION

### Inputs
- [0] `OPTIONSource` accepts `OPTION` (required: `True`, stream-only: `False`)

### Parameters
- `AgregatePositions` (`bool`), title="Agregate positions", default=`True`, shown=`True`, optimizable=`True`, help="When true it will agregate positions of similar directions in one"
- `BlockTrading` (`bool`), title="Block Trading", default=`True`, shown=`True`, optimizable=`True`, help="When true trading is completely blocked to avoid user misclick errors"
- `CheckSecurityTime` (`bool`), title="Check security time", default=`False`, shown=`True`, optimizable=`False`, help="When true it will validate security time before sending order to market"
- `DropVirtualPos` (`bool`), title="Drop Virtual Positions", default=`False`, shown=`True`, optimizable=`True`, help="Drop virtual positions"
- `ImportRealPos` (`bool`), title="Import Real Pos", default=`False`, shown=`True`, optimizable=`True`, help="Button to import real positions"
- `UseGlobalCache` (`bool`), title="Use Global Cache", default=`false`, shown=`True`, optimizable=`True`, help="Use global cache"
- `UseVirtualPositions` (`bool`), title="Virtual Positions", default=`True`, shown=`True`, optimizable=`True`, help="When true it will create only virtual positions without sending orders in market"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "PositionsManager1", "typeName": "PositionsManager", "blockType": "ConverterItem"
    }
  ]
}
```

## PositionsManagerSingle

- Display name: Positions Manager (single security)
- typeName: `PositionsManagerSingle`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `SECURITY` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Manager for virtual and real positions (single security)  Inputs/Output: Inputs=Security(SECURITY); Output=SECURITY

### Inputs
- [0] `Security` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- `AgregatePositions` (`bool`), title="Agregate positions", default=`True`, shown=`True`, optimizable=`True`, help="When true it will agregate positions of similar directions in one"
- `BlockTrading` (`bool`), title="Block Trading", default=`True`, shown=`True`, optimizable=`True`, help="When true trading is completely blocked to avoid user misclick errors"
- `CheckSecurityTime` (`bool`), title="Check security time", default=`False`, shown=`True`, optimizable=`False`, help="When true it will validate security time before sending order to market"
- `DropVirtualPos` (`bool`), title="Drop Virtual Positions", default=`False`, shown=`True`, optimizable=`True`, help="Drop virtual positions"
- `ImportRealPos` (`bool`), title="Import Real Pos", default=`False`, shown=`True`, optimizable=`True`, help="Button to import real positions"
- `UseGlobalCache` (`bool`), title="Use Global Cache", default=`false`, shown=`True`, optimizable=`True`, help="Use global cache"
- `UseVirtualPositions` (`bool`), title="Virtual Positions", default=`True`, shown=`True`, optimizable=`True`, help="When true it will create only virtual positions without sending orders in market"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "PositionsManagerSingle1", "typeName": "PositionsManagerSingle", "blockType": "ConverterItem"
    }
  ]
}
```

## SellOptionGroup

- Display name: Sell option group
- typeName: `SellOptionGroup`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `8`, max `8`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Sell many options while position risk is 'small'  Inputs/Output: Inputs=Permission(DOUBLE, BOOL), Strike(DOUBLE), Current Risk(DOUBLE), Max Risk(DOUBLE), Smile(INTERACTIVESPLINE), OptionSeries(OPTION_SERIES), Call Risk(DOUBLE), Put Risk(DOUBLE); Output=DOUBLE

### Inputs
- [0] `Permission` accepts `DOUBLE, BOOL` (required: `True`, stream-only: `False`)
- [1] `Strike` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [2] `Current Risk` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [3] `Max Risk` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [4] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [5] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)
- [6] `Call Risk` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [7] `Put Risk` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `EntryShift` (`int`), title="Entry shift", default=`0`, range=`-1000000`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Entry shift to get higher sell price (price step)"
- `ExitShift` (`int`), title="Exit shift", default=`0`, range=`-1000000`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Exit shift to get quick execution (price step)"
- `FixedQty` (`int`), title="Order size", default=`1`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Order size"
- `OptionType` (`StrikeType`), title="Option type", default=`Call`, shown=`True`, optimizable=`True`, help="Limit trading to options of given type (call, put, both)"
- `StrikeAmount` (`int`), title="Strike amount", default=`0`, range=`0`..`10000000` step `1`, shown=`True`, optimizable=`True`, help="Strike amount to set your orders (up and down from the central strike)"
- `StrikeStep` (`Double`), title="Strike step", default=`0`, range=`0`..`10000000` step `1`, shown=`True`, optimizable=`True`, help="Strike step to extract the most important options"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SellOptionGroup1", "typeName": "SellOptionGroup", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## SellOptionGroupDelta

- Display name: Sell option group (delta range)
- typeName: `SellOptionGroupDelta`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `9`, max `9`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Sell many options while position risk is 'small' (strike range is set in units of delta)  Inputs/Output: Inputs=Permission(DOUBLE, BOOL), Strike(DOUBLE), Current Risk(DOUBLE), Max Risk(DOUBLE), Smile(INTERACTIVESPLINE), OptionSeries(OPTION_SERIES), Call delta(INTERACTIVESPLINE), Call Risk(DOUBLE), Put Risk(DOUBLE); Output=DOUBLE

### Inputs
- [0] `Permission` accepts `DOUBLE, BOOL` (required: `True`, stream-only: `False`)
- [1] `Strike` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [2] `Current Risk` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [3] `Max Risk` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [4] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [5] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)
- [6] `Call delta` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [7] `Call Risk` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [8] `Put Risk` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `CheckAbsDelta` (`bool`), title="Check absolute delta", default=`true`, shown=`True`, optimizable=`True`, help="Check absolute value of option's delta"
- `EntryShift` (`int`), title="Entry shift", default=`0`, range=`-1000000`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Entry shift to get higher sell price (price step)"
- `ExitShift` (`int`), title="Exit shift", default=`0`, range=`-1000000`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Exit shift to get quick execution (price step)"
- `FixedQty` (`int`), title="Order size", default=`1`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Order size"
- `MaxDeltaPct` (`int`), title="Max delta, %", default=`0`, range=`-1000`..`1000` step `1`, shown=`True`, optimizable=`True`, help="The highest working delta we allow to quote (as percents)"
- `MinDeltaPct` (`int`), title="Min delta, %", default=`0`, range=`-1000`..`1000` step `1`, shown=`True`, optimizable=`True`, help="The lowest working delta we allow to quote (as percents)"
- `StrikeStep` (`Double`), title="Strike step", default=`0`, range=`0`..`10000000` step `1`, shown=`True`, optimizable=`True`, help="Strike step to extract the most important options"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SellOptionGroupDelta1", "typeName": "SellOptionGroupDelta", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## SellOptions

- Display name: Sell Options
- typeName: `SellOptions`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `8`, max `8`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Sell options while position risk is 'small'  Inputs/Output: Inputs=Permission(DOUBLE, BOOL), Strike(DOUBLE), Current Risk(DOUBLE), Max Risk(DOUBLE), Smile(INTERACTIVESPLINE), OptionSeries(OPTION_SERIES), Call Risk(DOUBLE), Put Risk(DOUBLE); Output=DOUBLE

### Inputs
- [0] `Permission` accepts `DOUBLE, BOOL` (required: `True`, stream-only: `False`)
- [1] `Strike` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [2] `Current Risk` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [3] `Max Risk` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [4] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [5] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)
- [6] `Call Risk` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [7] `Put Risk` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `EntryShift` (`int`), title="Entry shift", default=`0`, range=`-1000000`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Entry shift to get higher sell price (price step)"
- `ExitShift` (`int`), title="Exit shift", default=`0`, range=`-1000000`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Exit shift to get quick execution (price step)"
- `FixedQty` (`int`), title="Order size", default=`1`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Order size"
- `OptionType` (`StrikeType`), title="Option type", default=`Call`, shown=`True`, optimizable=`True`, help="Limit trading to options of given type (call, put, both)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SellOptions1", "typeName": "SellOptions", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## ShowTrades

- Display name: Show all trades
- typeName: `ShowTrades`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `UNKNOWN` (outputs: `0`, only-value-output: `False`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Show all security trades on the Chart Pane  Inputs/Output: Inputs=Security or Option(SECURITY, OPTION), Chart Pane(GRAPHPANE); Output=UNKNOWN

### Inputs
- [0] `Security or Option` accepts `SECURITY, OPTION` (required: `True`, stream-only: `False`)
- [1] `Chart Pane` accepts `GRAPHPANE` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "ShowTrades1", "typeName": "ShowTrades", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## SingleSeriesNumericalDelta

- Display name: Single Series Numerical Delta
- typeName: `SingleSeriesNumericalDelta`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `3`, max `3`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Estimates a delta profile with numerical differentiation (build a delta profile)  Inputs/Output: Inputs=Time(DOUBLE), Smile(INTERACTIVESPLINE), OptionSeries(OPTION_SERIES); Output=INTERACTIVESPLINE

### Inputs
- [0] `Time` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [2] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `GreekAlgo` (`NumericalGreekAlgo`), title="Greek Algo", default=`ShiftingSmile`, shown=`True`, optimizable=`True`, help="FrozenSmile - smile is frozen; ShiftingSmile - smile shifts horizontally without modification"
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `SigmaMult` (`Double`), title="Width multiplier", default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Width multiplier"
- `TooltipFormat` (`String`), title="Tooltip Format", default=`0.00`, shown=`True`, optimizable=`False`, help="Tooltip format (i.e. '0.00', '0.0##' etc)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SingleSeriesNumericalDelta1", "typeName": "SingleSeriesNumericalDelta", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## SingleSeriesNumericalDelta3

- Display name: Numerical Delta (IntSer)
- typeName: `SingleSeriesNumericalDelta3`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Estimates a delta using a position profile  Inputs/Output: Inputs=Position Profile(INTERACTIVESPLINE); Output=INTERACTIVESPLINE

### Inputs
- [0] `Position Profile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)

### Parameters
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `SigmaMult` (`Double`), title="Width multiplier", default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Width multiplier"
- `TooltipFormat` (`String`), title="Tooltip Format", default=`0.000`, shown=`True`, optimizable=`False`, help="Tooltip format (i.e. '0.00', '0.0##' etc)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SingleSeriesNumericalDelta31", "typeName": "SingleSeriesNumericalDelta3", "blockType": "ConverterItem"
    }
  ]
}
```

## SingleSeriesNumericalGamma

- Display name: Single Series Numerical Gamma
- typeName: `SingleSeriesNumericalGamma`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `3`, max `3`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Estimates a gamma profile with numerical differentiation  Inputs/Output: Inputs=Time(DOUBLE), Smile(INTERACTIVESPLINE), OptionSeries(OPTION_SERIES); Output=INTERACTIVESPLINE

### Inputs
- [0] `Time` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [2] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `GreekAlgo` (`NumericalGreekAlgo`), title="Greek Algo", default=`ShiftingSmile`, shown=`True`, optimizable=`True`, help="FrozenSmile - smile is frozen; ShiftingSmile - smile shifts horizontally without modification"
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `SigmaMult` (`Double`), title="Width multiplier", default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Width multiplier"
- `TooltipFormat` (`String`), title="Tooltip Format", default=`0.000000`, shown=`True`, optimizable=`False`, help="Tooltip format (i.e. '0.00', '0.0##' etc)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SingleSeriesNumericalGamma1", "typeName": "SingleSeriesNumericalGamma", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## SingleSeriesNumericalGamma3

- Display name: Numerical Gamma (IntSer)
- typeName: `SingleSeriesNumericalGamma3`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Estimates a gamma position using its delta profile  Inputs/Output: Inputs=DeltaProfile(INTERACTIVESPLINE); Output=INTERACTIVESPLINE

### Inputs
- [0] `DeltaProfile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)

### Parameters
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `SigmaMult` (`Double`), title="Width multiplier", default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Width multiplier"
- `TooltipFormat` (`String`), title="Tooltip Format", default=`0.0000000`, shown=`True`, optimizable=`False`, help="Tooltip format (i.e. '0.00', '0.0##' etc)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SingleSeriesNumericalGamma31", "typeName": "SingleSeriesNumericalGamma3", "blockType": "ConverterItem"
    }
  ]
}
```

## SingleSeriesNumericalSpeed

- Display name: Single Series Numerical Speed
- typeName: `SingleSeriesNumericalSpeed`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `3`, max `3`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Estimate 'Speed' profile with numerical differentiation

### Inputs
- [0] `Time` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [2] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `GreekAlgo` (`NumericalGreekAlgo`), title="Greek Algo", default=`ShiftingSmile`, shown=`True`, optimizable=`True`, help="FrozenSmile - smile is frozen; ShiftingSmile - smile shifts horizontally without modification"
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `SigmaMult` (`Double`), title="Width multiplier", default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Width multiplier"
- `TooltipFormat` (`String`), title="Tooltip Format", default=`0.000000`, shown=`True`, optimizable=`False`, help="Tooltip format (i.e. '0.00', '0.0##' etc)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SingleSeriesNumericalSpeed1", "typeName": "SingleSeriesNumericalSpeed", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## SingleSeriesNumericalTheta

- Display name: Single Series Numerical Theta
- typeName: `SingleSeriesNumericalTheta`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `3`, max `3`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Estimates a theta profile with numerical differentiation (build a theta profile)  Inputs/Output: Inputs=Time(DOUBLE), Smile(INTERACTIVESPLINE), OptionSeries(OPTION_SERIES); Output=INTERACTIVESPLINE

### Inputs
- [0] `Time` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [2] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `DistanceMode` (`TimeRemainMode`), title="Estimation algo", default=`PlainCalendar`, shown=`True`, optimizable=`True`, help="Algorythm to estimate time-to-expiry"
- `GreekAlgo` (`NumericalGreekAlgo`), title="Greek Algo", default=`FrozenSmile`, shown=`True`, optimizable=`True`, help="FrozenSmile - smile is frozen; ShiftingSmile - smile shifts horizontally without modification"
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `SigmaMult` (`Double`), title="Width multiplier", default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Width multiplier"
- `TooltipFormat` (`String`), title="Tooltip Format", default=`0.00`, shown=`True`, optimizable=`False`, help="Tooltip format (i.e. '0.00', '0.0##' etc)"
- `TStep` (`Double`), title="Time Step", default=`0.00001`, range=`0`..`1000000` step `0.00001`, shown=`True`, optimizable=`True`, help="Time step for numerical derivative"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SingleSeriesNumericalTheta1", "typeName": "SingleSeriesNumericalTheta", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## SingleSeriesNumericalVega

- Display name: Single Series Numerical Vega
- typeName: `SingleSeriesNumericalVega`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `3`, max `3`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Estimates a vega profile with numerical differentiation (build a vega profile)  Inputs/Output: Inputs=Time(DOUBLE), Smile(INTERACTIVESPLINE), OptionSeries(OPTION_SERIES); Output=INTERACTIVESPLINE

### Inputs
- [0] `Time` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [2] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `GreekAlgo` (`NumericalGreekAlgo`), title="Greek Algo", default=`ShiftingSmile`, shown=`True`, optimizable=`True`, help="FrozenSmile - smile is frozen; ShiftingSmile - smile shifts horizontally without modification"
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `SigmaMult` (`Double`), title="Width multiplier", default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Width multiplier"
- `SigmaStep` (`Double`), title="Sigma Step", default=`0.0001`, range=`0`..`1000000` step `0.0001`, shown=`True`, optimizable=`True`, help="Sigma step for numerical derivative"
- `TooltipFormat` (`String`), title="Tooltip Format", default=`0.00`, shown=`True`, optimizable=`False`, help="Tooltip format (i.e. '0.00', '0.0##' etc)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SingleSeriesNumericalVega1", "typeName": "SingleSeriesNumericalVega", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## SingleSeriesPositionCommissions

- Display name: Single Series Position Commission
- typeName: `SingleSeriesPositionCommissions`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Grid of entire option position commissions  Inputs/Output: Inputs=OptionSeries(OPTION_SERIES); Output=INTERACTIVESPLINE

### Inputs
- [0] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `CountFutures` (`bool`), title="Count Futures", default=`false`, shown=`True`, optimizable=`True`, help="Count base asset"
- `LongPositions` (`bool`), title="Long positions", default=`true`, shown=`True`, optimizable=`True`, help="Prices of long positions"
- `OptionType` (`StrikeType`), title="Option Type", default=`Any`, shown=`True`, optimizable=`True`, help="Option type to be used by handler (call, put, sum of both)"
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `SigmaMult` (`Double`), title="Width multiplier", default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Width multiplier"
- `TooltipFormat` (`String`), title="Tooltip Format", default=`0`, shown=`True`, optimizable=`True`, help="Tooltip format (i.e. '0.00', '0.0##' etc)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SingleSeriesPositionCommissions1", "typeName": "SingleSeriesPositionCommissions", "blockType": "ConverterItem"
    }
  ]
}
```

## SingleSeriesPositionGrid

- Display name: Single Series Position Grid
- typeName: `SingleSeriesPositionGrid`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `3`, max `3`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Grid of entire option position (count semistraddles)  Inputs/Output: Inputs=Time(DOUBLE), Smile(INTERACTIVESPLINE), OptionSeries(OPTION_SERIES); Output=INTERACTIVESPLINE

### Inputs
- [0] `Time` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [2] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `CountFutures` (`bool`), title="Count Futures", default=`false`, shown=`True`, optimizable=`True`, help="Count base asset"
- `OptionType` (`StrikeType`), title="Option Type", default=`Any`, shown=`True`, optimizable=`True`, help="Option type to be used by handler (call, put, sum of both)"
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `SigmaMult` (`Double`), title="Width multiplier", default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Width multiplier"
- `TooltipFormat` (`String`), title="Tooltip Format", default=`0`, shown=`True`, optimizable=`True`, help="Tooltip format (i.e. '0.00', '0.0##' etc)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SingleSeriesPositionGrid1", "typeName": "SingleSeriesPositionGrid", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## SingleSeriesPositionList

- Display name: Single Series Position List
- typeName: `SingleSeriesPositionList`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
A list of all user's trades in one option series  Inputs/Output: Inputs=OptionSeries(OPTION_SERIES); Output=INTERACTIVESPLINE

### Inputs
- [0] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `CountFutures` (`bool`), title="Count Futures", default=`false`, shown=`True`, optimizable=`True`, help="Count base asset"
- `DisplayMode` (`PositionGridDisplayMode`), title="Display Property", default=`Symbol`, shown=`True`, optimizable=`True`, help="Position property to be displayed"
- `MaxPositions` (`int`), title="Max Positions", default=`100`, range=`1`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Limit number of positions to show"
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `SigmaMult` (`Double`), title="Width multiplier", default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Width multiplier"
- `TooltipFormat` (`String`), title="Tooltip Format", default=`0`, shown=`True`, optimizable=`False`, help="Tooltip format (i.e. '0.00', '0.0##' etc)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SingleSeriesPositionList1", "typeName": "SingleSeriesPositionList", "blockType": "ConverterItem"
    }
  ]
}
```

## SingleSeriesPositionPrices

- Display name: Single Series Position Prices
- typeName: `SingleSeriesPositionPrices`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Grid of average position prices (single option series)  Inputs/Output: Inputs=OptionSeries(OPTION_SERIES); Output=INTERACTIVESPLINE

### Inputs
- [0] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `CountFutures` (`bool`), title="Count Futures", default=`false`, shown=`True`, optimizable=`True`, help="Count base asset"
- `CountQty` (`bool`), title="Count lot size", default=`false`, shown=`True`, optimizable=`True`, help="Count lot size"
- `LongPositions` (`bool`), title="Long positions", default=`true`, shown=`True`, optimizable=`True`, help="Prices of long positions"
- `OptionType` (`StrikeType`), title="Option Type", default=`Call`, shown=`True`, optimizable=`True`, help="Option type to be used by handler (call, put, sum of both)"
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `SigmaMult` (`Double`), title="Width multiplier", default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Width multiplier"
- `TooltipFormat` (`String`), title="Tooltip Format", default=`0`, shown=`True`, optimizable=`True`, help="Tooltip format (i.e. '0.00', '0.0##' etc)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SingleSeriesPositionPrices1", "typeName": "SingleSeriesPositionPrices", "blockType": "ConverterItem"
    }
  ]
}
```

## SingleSeriesProfile

- Display name: Single Series Profile
- typeName: `SingleSeriesProfile`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `3`, max `3`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
A single series position profile (change of currency rate is not included) as a function of BA price

### Inputs
- [0] `Time` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [2] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `GreekAlgo` (`NumericalGreekAlgo`), title="Greek Algo", default=`ShiftingSmile`, shown=`True`, optimizable=`True`, help="FrozenSmile - smile is frozen; ShiftingSmile - smile shifts horizontally without modification"
- `NodesCount` (`int`), title="Nodes Count", default=`0`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Number of additional nodes near money"
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `SigmaMult` (`Double`), title="Width multiplier", default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Width multiplier"
- `TooltipFormat` (`String`), title="Tooltip Format", default=`0`, shown=`True`, optimizable=`True`, help="Tooltip format (i.e. '0.00', '0.0##' etc)"
- `TwoSideDelta` (`bool`), title="Two side delta", default=`false`, shown=`True`, optimizable=`True`, help="Calculate delta to the left and to the right from the strike"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SingleSeriesProfile1", "typeName": "SingleSeriesProfile", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## TotalCommission

- Display name: Total Commission
- typeName: `TotalCommission`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Total commission including closed positions  Inputs/Output: Inputs=AnyOption(SECURITY, OPTION, OPTION_SERIES); Output=DOUBLE

### Inputs
- [0] `AnyOption` accepts `SECURITY, OPTION, OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TotalCommission1", "typeName": "TotalCommission", "blockType": "ConverterItem"
    }
  ]
}
```

## TotalProfit

- Display name: Profit ATM (IntSer)
- typeName: `TotalProfit`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Numerical estimate of profit at-the-money (only one point is processed using position profile)  Inputs/Output: Inputs=Position Profile or Security(SECURITY, INTERACTIVESPLINE); Output=DOUBLE

### Inputs
- [0] `Position Profile or Security` accepts `SECURITY, INTERACTIVESPLINE` (required: `True`, stream-only: `False`)

### Parameters
- `PrintProfitInLog` (`bool`), title="Print in Log", default=`False`, shown=`True`, optimizable=`True`, help="Print profit in main log"
- `Profit` (`OptimProperty`), default=`0`, shown=`True`, optimizable=`True`, help="Current position profit"
- `ProfitAlgo` (`TotalProfitAlgo`), title="Profit algo", default=`AllPositions`, shown=`True`, optimizable=`True`, help="Profit calculation algorytm"
- `ScaleMultiplier` (`Double`), title="Scale multiplier", default=`1`, shown=`True`, optimizable=`True`, help="Scale multiplier to convert profit from price units to money (i.e. dollars or euros)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TotalProfit1", "typeName": "TotalProfit", "blockType": "ConverterItem"
    }
  ]
}
```

## TotalQty

- Display name: Total Open Qty
- typeName: `TotalQty`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Pure open position in a given security  Inputs/Output: Inputs=Security(SECURITY); Output=DOUBLE

### Inputs
- [0] `Security` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- `OpenQty` (`OptimProperty`), title="Open Qty", default=`0`, shown=`True`, optimizable=`True`, help="Total open quantity"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TotalQty1", "typeName": "TotalQty", "blockType": "ConverterItem"
    }
  ]
}
```

## TotalRiskN2

- Display name: Total Risk N2
- typeName: `TotalRiskN2`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPositions`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Total risk of position as number of semistraddles  Inputs/Output: Inputs=Position Manager(OPTION); Output=DOUBLE

### Inputs
- [0] `Position Manager` accepts `OPTION` (required: `True`, stream-only: `False`)

### Parameters
- `DisplayRisk` (`OptimProperty`), title="Risk", default=`0`, range=`-1000000`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Risk (just to display at UI)"
- `DisplayUnits` (`FixedValueMode`), title="Display Units", default=`AsIs`, shown=`True`, optimizable=`False`, help="Display units (hundreds, thousands, as is)"
- `RepeatLastValue` (`bool`), title="Repeat Last Value", default=`false`, shown=`True`, optimizable=`True`, help="Handler should repeat last known value to avoid further logic errors"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TotalRiskN21", "typeName": "TotalRiskN2", "blockType": "ConverterItem"
    }
  ]
}
```

