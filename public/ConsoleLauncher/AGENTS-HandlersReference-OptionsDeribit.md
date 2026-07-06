# Handlers Reference: OptionsDeribit

For each handler below:
- `typeName` is the string you pass to `/api/handlers/{typeName}` and `AddBlock` (`typeName` field).
- `blockType` is the container you must use for handler-based blocks (not template blocks).
- Input indices are zero-based (`toPort`).
- Hidden handlers (`[HandlerInvisible]`) require `allowHiddenHandler=true` in `AddBlock` (advanced). Some legacy helpers (e.g. `CycleHandler`) may be auto-converted to template blocks.

## IvSmileRescaled2

- Display name: IV Smile (Deribit)
- typeName: `IvSmileRescaled2`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsDeribit`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `5`, max `5`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Smile derived from option quotes with scale multiplier (bar handler, for Deribit)  Inputs/Output: Inputs=FutPx(DOUBLE), Time(DOUBLE), OptionSeries(INTERACTIVESPLINE, OPTION_SERIES), ScaleMultiplier(DOUBLE), RiskFreeRate(DOUBLE); Output=INTERACTIVESPLINE

### Inputs
- [0] `FutPx` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Time` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [2] `OptionSeries` accepts `INTERACTIVESPLINE, OPTION_SERIES` (required: `True`, stream-only: `False`)
- [3] `ScaleMultiplier` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [4] `RiskFreeRate` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `MaxSigmaPct` (`Double`), title="Max sigma, %", default=`200`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`False`, help="Maximum volatility (percents)"
- `MaxStrike` (`Double`), title="Max strike", default=`1500000`, range=`0`..`10000000` step `1`, shown=`True`, optimizable=`False`, help="Max strike to be processed by handler"
- `MinStrike` (`Double`), title="Min strike", default=`1`, range=`0`..`10000000` step `1`, shown=`True`, optimizable=`False`, help="Min strike to be processed by handler"
- `OptionType` (`StrikeType`), title="Option type", default=`Any`, shown=`True`, optimizable=`True`, help="Option type to be used by handler (call, put, best volatility)"
- `OptPxMode` (`OptionPxMode`), title="Price mode", default=`Ask`, shown=`True`, optimizable=`False`, help="Algorythm to get option price"
- `ShiftAsk` (`Double`), title="Shift Ask", default=`0`, range=`-10000000`..`10000000` step `1`, shown=`True`, optimizable=`False`, help="Shift Asks up (price steps)"
- `ShiftBid` (`Double`), title="Shift Bid", default=`0`, range=`-10000000`..`10000000` step `1`, shown=`True`, optimizable=`False`, help="Shift Bids down (price steps)"
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `StrikeStep` (`Double`), title="Strike step", default=`2500`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`False`, help="Strike step"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "IvSmileRescaled21", "typeName": "IvSmileRescaled2", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## QuoteIvDeribit

- Display name: Quote volatility (Deribit)
- typeName: `QuoteIvDeribit`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsDeribit`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `3`, max `3`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Quote volatility (special for Deribit)  Inputs/Output: Inputs=Smile(INTERACTIVESPLINE), OptionSeries(OPTION_SERIES), ScaleMultiplier(DOUBLE); Output=INTERACTIVESPLINE

### Inputs
- [0] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [1] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)
- [2] `ScaleMultiplier` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `CancelAllLong` (`bool`), title="Cancel all long", default=`false`, shown=`True`, optimizable=`True`, help="Cancel long quotes in all strikes"
- `CancelAllShort` (`bool`), title="Cancel all short", default=`false`, shown=`True`, optimizable=`True`, help="Cancel short quotes in all strikes"
- `ExecuteCommand` (`bool`), title="Execute", default=`false`, shown=`True`, optimizable=`True`, help="Execute"
- `OptionType` (`StrikeType`), title="Option Type", default=`Any`, shown=`True`, optimizable=`True`, help="Option type (when Any, the handler will choose out-of-the-money security)"
- `Qty` (`int`), title="Size", default=`0`, range=`-1000000`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Trade quantity. Negative value reverts the signal."
- `ShiftIvPct` (`Double`), title="Shift IV", default=`0`, range=`-10000000`..`10000000` step `1`, shown=`True`, optimizable=`True`, help="Shift quote relative to the smile (in percents of volatility)"
- `ShiftPrice` (`int`), title="Shift price", default=`0`, range=`-10000000`..`10000000` step `1`, shown=`True`, optimizable=`True`, help="Shift quote relative to the shifted smile (in price steps)"
- `Strike` (`String`), default=`120 000`, shown=`True`, optimizable=`True`, help="Option strike"
- `StrikeStep` (`Double`), title="Strike step", default=`0`, range=`0`..`10000000` step `1`, shown=`True`, optimizable=`True`, help="Strike step to extract most important options"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "QuoteIvDeribit1", "typeName": "QuoteIvDeribit", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## ShowIvTargetsDeribit

- Display name: Show IV Targets (Deribit)
- typeName: `ShowIvTargetsDeribit`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsDeribit`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `4`, max `4`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Show volatility limit orders (special for Deribit)  Inputs/Output: Inputs=Smile(INTERACTIVESPLINE), OptionSeries(OPTION_SERIES), Quote IV(INTERACTIVESPLINE), ScaleMultiplier(DOUBLE); Output=INTERACTIVESPLINE

### Inputs
- [0] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [1] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)
- [2] `Quote IV` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [3] `ScaleMultiplier` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `IsLong` (`bool`), title="Long", default=`false`, shown=`True`, optimizable=`True`, help="Show long orders"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "ShowIvTargetsDeribit1", "typeName": "ShowIvTargetsDeribit", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## SingleSeriesNumericalDeltaDeribit3

- Display name: Numerical delta Deribit (IntSer)
- typeName: `SingleSeriesNumericalDeltaDeribit3`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsDeribit`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Estimates a delta using a position profile  Inputs/Output: Inputs=Position Profile(INTERACTIVESPLINE); Output=INTERACTIVESPLINE

### Inputs
- [0] `Position Profile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)

### Parameters
- `FutNominal` (`Double`), title="Futures nominal", default=`10`, shown=`True`, optimizable=`True`, help="Nominal value of Deribit futures (by default is 10 USD)"
- `ProfileAsBtc` (`bool`), title="Profile in BTC?", default=`false`, shown=`True`, optimizable=`True`, help="Calculate profile as bitcoins"
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `SigmaMult` (`Double`), title="Width multiplier", default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Width multiplier"
- `TooltipFormat` (`String`), title="Tooltip Format", default=`0.000`, shown=`True`, optimizable=`False`, help="Tooltip format (i.e. '0.00', '0.0##' etc)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SingleSeriesNumericalDeltaDeribit31", "typeName": "SingleSeriesNumericalDeltaDeribit3", "blockType": "ConverterItem"
    }
  ]
}
```

## SingleSeriesProfileDeribit

- Display name: Single series profile (Deribit)
- typeName: `SingleSeriesProfileDeribit`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsDeribit`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `4`, max `4`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
A single series position profile (change of currency rate is not included) as a function of BA price (special for Deribit)

### Inputs
- [0] `Time` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [2] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)
- [3] `ScaleMultiplier` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `FutNominal` (`Double`), title="Futures nominal", default=`10`, shown=`True`, optimizable=`True`, help="Nominal value of Deribit futures (by default is 10 USD)"
- `GreekAlgo` (`NumericalGreekAlgo`), title="Greek Algo", default=`ShiftingSmile`, shown=`True`, optimizable=`True`, help="FrozenSmile - smile is frozen; ShiftingSmile - smile shifts horizontally without modification"
- `ProfileAsBtc` (`bool`), title="Profile in BTC?", default=`false`, shown=`True`, optimizable=`True`, help="Calculate profile as bitcoins"
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `SigmaMult` (`Double`), title="Width multiplier", default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Width multiplier"
- `TooltipFormat` (`String`), title="Tooltip Format", default=`0`, shown=`True`, optimizable=`True`, help="Tooltip format (i.e. '0.00', '0.0##' etc)"
- `TwoSideDelta` (`bool`), title="Two side delta", default=`false`, shown=`True`, optimizable=`True`, help="Calculate delta to the left and to the right from the strike"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SingleSeriesProfileDeribit1", "typeName": "SingleSeriesProfileDeribit", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## SmileImitationDeribit5

- Display name: Smile Imitation v5 (Deribit)
- typeName: `SmileImitationDeribit5`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsDeribit`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `6`, max `6`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Smile imitation using application-wide user function in Global Cache  Inputs/Output: Inputs=FutPx(DOUBLE), Time(DOUBLE), Smile(INTERACTIVESPLINE), OptionSeries(OPTION_SERIES), ScaleMultiplier(DOUBLE), RiskFreeRate(DOUBLE); Output=INTERACTIVESPLINE

### Inputs
- [0] `FutPx` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Time` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [2] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [3] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)
- [4] `ScaleMultiplier` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [5] `RiskFreeRate` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `FrozenSmileID` (`String`), title="Frozen Smile ID", default=`FrozenSmile`, shown=`True`, optimizable=`False`, help="Smile ID to be used with Local Cache"
- `GenerateTails` (`bool`), title="Generate Tails", default=`true`, shown=`True`, optimizable=`False`, help="Generate invisible tails"
- `GlobalSmileID` (`String`), title="Global Smile ID", default=`GlobalSmile`, shown=`True`, optimizable=`False`, help="Smile ID to be used with Global Cache"
- `IvAtmPct` (`OptimProperty`), title="IV ATM, %", default=`30.0`, range=`0.000001`..`10000.0` step `0.01`, shown=`True`, optimizable=`True`, help="IV ATM (percents)"
- `SetIvByHands` (`bool`), title="Set IV", default=`false`, shown=`True`, optimizable=`True`, help="Set IV manually"
- `SetShapeByHands` (`bool`), title="Set Shape Manually", default=`false`, shown=`True`, optimizable=`True`, help="Set shape manually"
- `SetSlopeByHands` (`bool`), title="Set Skew Manually", default=`false`, shown=`True`, optimizable=`True`, help="Set skew manually"
- `ShapePct` (`OptimProperty`), title="Shape, %", default=`0.0`, range=`-10000.0`..`10000.0` step `0.01`, shown=`True`, optimizable=`True`, help="Shape (percents)"
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `SigmaMult` (`Double`), title="Width multiplier", default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Width multiplier"
- `SlopePct` (`OptimProperty`), title="Skew, %", default=`-10.0`, range=`-10000.0`..`10000.0` step `0.01`, shown=`True`, optimizable=`True`, help="Skew (percents)"
- `UseLocalTemplate` (`bool`), title="Use Local Template", default=`false`, shown=`True`, optimizable=`True`, help="Use template from global or from local cache"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SmileImitationDeribit51", "typeName": "SmileImitationDeribit5", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

