# Handlers Reference: OptionsTickByTick

For each handler below:
- `typeName` is the string you pass to `/api/handlers/{typeName}` and `AddBlock` (`typeName` field).
- `blockType` is the container you must use for handler-based blocks (not template blocks).
- Input indices are zero-based (`toPort`).
- Hidden handlers (`[HandlerInvisible]`) require `allowHiddenHandler=true` in `AddBlock` (advanced). Some legacy helpers (e.g. `CycleHandler`) may be auto-converted to template blocks.

## BasePx2

- Display name: Base Price
- typeName: `BasePx2`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsTickByTick`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Base asset price. Different algorythms are available (fixed price, last trade, quote midpoint, etc). Bar handler.

### Inputs
- [0] `Input0` accepts `SECURITY, OPTION, OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `DisplayPrice` (`OptimProperty`), title="Display Price", default=`0`, shown=`True`, optimizable=`True`, help="Base asset price (only to display at UI)"
- `DisplayUnits` (`FixedValueMode`), title="Display Units", default=`AsIs`, shown=`True`, optimizable=`False`, help="Display units (hundreds, thousands, as is)"
- `FixedPx` (`Double`), title="Price", default=`0`, shown=`True`, optimizable=`False`, help="Price for algorythm FixedPx"
- `PxMode` (`BasePxMode`), title="Algorythm", default=`LastTrade`, shown=`True`, optimizable=`False`, help="Algorythm to get base asset's price (FixedPx, LastTrade, etc)"
- `RepeatLastPx` (`bool`), title="Repeat Last Px", default=`false`, shown=`True`, optimizable=`True`, help="Handler should repeat last known value to avoid further logic errors"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BasePx21", "typeName": "BasePx2", "blockType": "ConverterItem"
    }
  ]
}
```

## BestChartTrading

- Display name: Best Chart Trading
- typeName: `BestChartTrading`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsTickByTick`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Trading with mouse on CanvasPane. Best quotes are accented automatically  Inputs/Output: Inputs=Quotes(INTERACTIVESPLINE), Smile(INTERACTIVESPLINE); Output=INTERACTIVESPLINE

### Inputs
- [0] `Quotes` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [1] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)

### Parameters
- `OptionType` (`StrikeType`), title="Option Type", default=`Call`, shown=`True`, optimizable=`True`, help="Option type (when Any, the handler will choose the best quote)"
- `OptPxMode` (`OptionPxMode`), title="Quote Type", default=`Ask`, shown=`True`, optimizable=`False`, help="Quote type (ask or bid)"
- `OutletDistance` (`Double`), title="Outlet distance", default=`0.02`, range=`-10000000`..`10000000` step `1`, shown=`True`, optimizable=`True`, help="Outlet distance to 'profitable' market order (units of volatility)"
- `OutletSize` (`Double`), title="Outlet size", default=`16`, range=`1`..`10000000` step `1`, shown=`True`, optimizable=`True`, help="Outlet size (pixel)"
- `Qty` (`int`), title="Size", default=`10`, range=`-1000000`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Trade quantity. Negative value reverts the signal."
- `WidthPx` (`Double`), title="Width", default=`100`, range=`0`..`10000000` step `1`, shown=`True`, optimizable=`True`, help="Width of neutral band (price steps)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BestChartTrading1", "typeName": "BestChartTrading", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## BlackScholesConstSmile2

- Display name: Black-Scholes Const
- typeName: `BlackScholesConstSmile2`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsTickByTick`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
A flat smile as in the Black-Scholes option model. Volatility is a constant and is defined by the 'Sigma, %' parameter.

### Inputs
- [0] `FutPx` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Time` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Label` (`String`), default=`IV`, shown=`True`, optimizable=`False`, help="Label to mark a nodes"
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `SigmaMult` (`Double`), title="Width multiplier", default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Width multiplier"
- `SigmaPct` (`Double`), title="Sigma, %", default=`22`, range=`0`..`1000000` step `0.5`, shown=`True`, optimizable=`True`, help="Volatility (percents)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BlackScholesConstSmile21", "typeName": "BlackScholesConstSmile2", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## BlackScholesSmile2

- Display name: Black-Scholes 'Smile'
- typeName: `BlackScholesSmile2`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsTickByTick`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `3`, max `3`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Horizontal line spanning a few Sigma  Inputs/Output: Inputs=FutPx(DOUBLE), Time(DOUBLE), Sigma(DOUBLE); Output=INTERACTIVESPLINE

### Inputs
- [0] `FutPx` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Time` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [2] `Sigma` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Label` (`String`), default=`IV`, shown=`True`, optimizable=`False`, help="Label to mark a nodes"
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `SigmaMult` (`Double`), title="Width multiplier", default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Width multiplier"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BlackScholesSmile21", "typeName": "BlackScholesSmile2", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## ChartTrading

- Display name: Chart Trading
- typeName: `ChartTrading`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsTickByTick`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Trading with mouse on CanvasPane  Inputs/Output: Inputs=Quotes(INTERACTIVESPLINE); Output=INTERACTIVESPLINE

### Inputs
- [0] `Quotes` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)

### Parameters
- `OptionType` (`StrikeType`), title="Option Type", default=`Call`, shown=`True`, optimizable=`True`, help="Option type (when Any, the handler will choose the best quote)"
- `OptPxMode` (`OptionPxMode`), title="Quote Type", default=`Ask`, shown=`True`, optimizable=`False`, help="Quote type (ask or bid)"
- `Qty` (`int`), title="Size", default=`1`, range=`-1000000`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Trade quantity. Negative value reverts the signal."

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "ChartTrading1", "typeName": "ChartTrading", "blockType": "ConverterItem"
    }
  ]
}
```

## ConstSmileLevel2

- Display name: Horizontal line
- typeName: `ConstSmileLevel2`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsTickByTick`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Horizontal line at smile chart. Position is defined by 'Value' parameter.  Inputs/Output: Inputs=FutPx(DOUBLE), Time(DOUBLE); Output=INTERACTIVESPLINE

### Inputs
- [0] `FutPx` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Time` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Label` (`String`), default=`V`, shown=`True`, optimizable=`False`, help="Label to mark a nodes"
- `ShowEdgeLabels` (`bool`), title="Show edge labels", default=`true`, shown=`True`, optimizable=`True`, help="Show edge labels"
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `SigmaMult` (`Double`), title="Width multiplier", default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Width multiplier"
- `SigmaPct` (`Double`), title="Sigma, %", default=`30`, range=`0`..`1000000` step `0.5`, shown=`True`, optimizable=`True`, help="Volatility (percents)"
- `ValuePct` (`Double`), title="Value, %", default=`30`, range=`0`..`1000000` step `0.5`, shown=`True`, optimizable=`True`, help="Value (percents)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "ConstSmileLevel21", "typeName": "ConstSmileLevel2", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## EditTemplateSmile

- Display name: Edit Template Smile
- typeName: `EditTemplateSmile`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsTickByTick`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Edit template smile  Inputs/Output: Inputs=Time(DOUBLE), Smile(INTERACTIVESPLINE); Output=INTERACTIVESPLINE

### Inputs
- [0] `Time` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)

### Parameters
- `FrozenSmileID` (`String`), title="Frozen Smile ID", default=`FrozenSmile`, shown=`True`, optimizable=`False`, help="Smile ID to be used with Local Cache"
- `GlobalSmileID` (`int`), title="Global Smile ID", default=`0`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Smile ID to be used with Global Cache"
- `LoadSplineCoeffs` (`bool`), title="Load spline", default=`false`, shown=`True`, optimizable=`True`, help="Load spline coefficients from Global Cache"
- `NodeStep` (`Double`), title="Node Step", default=`1.5`, range=`0`..`100000` step `1`, shown=`True`, optimizable=`True`, help="Node step"
- `NumberOfNodes` (`int`), title="Number of Nodes", default=`11`, range=`3`..`100000` step `1`, shown=`True`, optimizable=`True`, help="Number of nodes to edit"
- `PasteGlobal` (`bool`), title="Paste", default=`false`, shown=`True`, optimizable=`True`, help="Get spline from clipboard"
- `PrepareSplineCoeffs` (`bool`), title="Prepare Spline", default=`false`, shown=`True`, optimizable=`True`, help="Prepare spline coefficients"
- `ResetSmile` (`bool`), title="Reset", default=`false`, shown=`True`, optimizable=`True`, help="Button to reset smile to initial state"
- `ShapePct` (`Double`), title="Shape", default=`0.0`, range=`-100000`..`100000` step `1`, shown=`True`, optimizable=`True`, help="Shape"
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `SigmaMult` (`Double`), title="Width multiplier", default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Width multiplier"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "EditTemplateSmile1", "typeName": "EditTemplateSmile", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## ExchangeTheorSigma3

- Display name: Exchange Smile
- typeName: `ExchangeTheorSigma3`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsTickByTick`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Exchange smile (bar handler)  Inputs/Output: Inputs=OptionSeries(OPTION_SERIES), RiskFreeRate(DOUBLE); Output=INTERACTIVESPLINE

### Inputs
- [0] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)
- [1] `RiskFreeRate` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `ExpiryTime` (`String`), title="Expiry Time", default=`18:45`, shown=`True`, optimizable=`False`, help="Exact expiration time of day (HH:mm)"
- `MultiplierPx` (`Double`), title="Multiplier", default=`1`, range=`-1000000`..`1000000` step `1`, shown=`True`, optimizable=`False`, help="Price multiplier"
- `OptionType` (`StrikeType`), title="Option Type", default=`Call`, shown=`True`, optimizable=`False`, help="Option type (parameter Any is not recommended)"
- `ShiftPx` (`Double`), title="Shift", default=`0`, range=`-1000000`..`1000000` step `1`, shown=`True`, optimizable=`False`, help="Price shift (price steps)"
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `SigmaMult` (`Double`), title="Width multiplier", default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Width multiplier"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "ExchangeTheorSigma31", "typeName": "ExchangeTheorSigma3", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## ExchangeTheorSigma5

- Display name: Exchange Smile (Rescaled)
- typeName: `ExchangeTheorSigma5`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsTickByTick`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `4`, max `4`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Exchange smile rescaled to our internal time-to-expiry  Inputs/Output: Inputs=FutPx(DOUBLE), Time(DOUBLE), OptionSeries(OPTION_SERIES), RiskFreeRate(DOUBLE); Output=INTERACTIVESPLINE

### Inputs
- [0] `FutPx` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Time` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [2] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)
- [3] `RiskFreeRate` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `ExpiryTime` (`String`), title="Expiry Time", default=`18:45`, shown=`True`, optimizable=`False`, help="Exact expiration time of day (HH:mm)"
- `OptionType` (`StrikeType`), title="Option Type", default=`Call`, shown=`True`, optimizable=`False`, help="Option type (parameter Any is not recommended)"
- `RescaleTime` (`bool`), title="Rescale Time", default=`true`, shown=`True`, optimizable=`False`, help="Rescale time-to-expiry to our internal?"
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `SigmaMult` (`Double`), title="Width multiplier", default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Width multiplier"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "ExchangeTheorSigma51", "typeName": "ExchangeTheorSigma5", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## GaussSmile

- Display name: Gauss 'Smile'
- typeName: `GaussSmile`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsTickByTick`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `3`, max `3`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Arbitrary function with 3 parameters similar to observed smile  Inputs/Output: Inputs=FutPx(DOUBLE), Time(DOUBLE), OptionSeries(OPTION_SERIES); Output=INTERACTIVESPLINE

### Inputs
- [0] `FutPx` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Time` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [2] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `DepthPct` (`Double`), title="Depth", default=`50.0`, range=`0.0`..`10000.0` step `0.01`, shown=`True`, optimizable=`True`, help="Depth (percents)"
- `GenerateTails` (`bool`), title="Generate Tails", default=`true`, shown=`True`, optimizable=`False`, help="Prepare invisible tails to extend working range"
- `IsVisiblePoints` (`bool`), title="Show nodes", default=`True`, shown=`True`, optimizable=`False`, help="Show nodes"
- `IvAtmPct` (`Double`), title="IV ATM", default=`30.0`, range=`0.000001`..`10000.0` step `0.01`, shown=`True`, optimizable=`True`, help="IV ATM (percents)"
- `MaxStrike` (`Double`), title="Max strike", default=`1500000`, range=`0`..`10000000` step `1`, shown=`True`, optimizable=`False`, help="Max strike to be processed by handler"
- `MinStrike` (`Double`), title="Min strike", default=`1`, range=`0`..`10000000` step `1`, shown=`True`, optimizable=`False`, help="Min strike to be processed by handler"
- `ShiftPct` (`Double`), title="Shift", default=`30.0`, range=`-100000.0`..`100000.0` step `0.01`, shown=`True`, optimizable=`True`, help="Shift (percents)"
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `StrikeStep` (`Double`), title="Strike step", default=`2500`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`False`, help="Strike step"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "GaussSmile1", "typeName": "GaussSmile", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## IvSmile2

- Display name: IV Smile
- typeName: `IvSmile2`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsTickByTick`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `4`, max `4`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Smile derived from option quotes (bar handler)  Inputs/Output: Inputs=FutPx(DOUBLE), Time(DOUBLE), OptionSeries(INTERACTIVESPLINE, OPTION_SERIES), RiskFreeRate(DOUBLE); Output=INTERACTIVESPLINE

### Inputs
- [0] `FutPx` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Time` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [2] `OptionSeries` accepts `INTERACTIVESPLINE, OPTION_SERIES` (required: `True`, stream-only: `False`)
- [3] `RiskFreeRate` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `MaxSigmaPct` (`Double`), title="Max Sigma, %", default=`200`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`False`, help="Maximum volatility (percents)"
- `MaxStrike` (`Double`), title="Max strike", default=`1500000`, range=`0`..`10000000` step `1`, shown=`True`, optimizable=`False`, help="Max strike to be processed by handler"
- `MinStrike` (`Double`), title="Min strike", default=`1`, range=`0`..`10000000` step `1`, shown=`True`, optimizable=`False`, help="Min strike to be processed by handler"
- `OptionType` (`StrikeType`), title="Option Type", default=`Any`, shown=`True`, optimizable=`True`, help="Option type to be used by handler (call, put, best volatility)"
- `OptPxMode` (`OptionPxMode`), title="Price Mode", default=`Ask`, shown=`True`, optimizable=`False`, help="Algorythm to get option price"
- `ShiftAsk` (`Double`), title="Shift Ask", default=`0`, range=`-10000000`..`10000000` step `1`, shown=`True`, optimizable=`False`, help="Shift Asks up (price steps)"
- `ShiftBid` (`Double`), title="Shift Bid", default=`0`, range=`-10000000`..`10000000` step `1`, shown=`True`, optimizable=`False`, help="Shift Bids down (price steps)"
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `StrikeStep` (`Double`), title="Strike step", default=`2500`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`False`, help="Strike step"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "IvSmile21", "typeName": "IvSmile2", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## LinearTransform

- Display name: Linear transform (a*x+b)
- typeName: `LinearTransform`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsTickByTick`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Linear transform (a*x+b)  Inputs/Output: Inputs=Input0(DOUBLE); Output=DOUBLE

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Add` (`Double`), title="Summand", default=`0.0`, range=`-5000000.0`..`5000000.0` step `1`, shown=`True`, optimizable=`True`, help="Summand"
- `Mult` (`Double`), title="Multiplier", default=`1.0`, range=`-5000000.0`..`5000000.0` step `1`, shown=`True`, optimizable=`True`, help="Multiplier"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "LinearTransform1", "typeName": "LinearTransform", "blockType": "ConverterItem"
    }
  ]
}
```

## OptionBase2

- Display name: Base asset
- typeName: `OptionBase2`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsTickByTick`
- Output: `SECURITY` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Base asset (bar handler)  Inputs/Output: Inputs=Input0(OPTION, OPTION_SERIES); Output=SECURITY

### Inputs
- [0] `Input0` accepts `OPTION, OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "OptionBase21", "typeName": "OptionBase2", "blockType": "ConverterItem"
    }
  ]
}
```

## OptionSeriesByNumber2

- Display name: Option Series by Number
- typeName: `OptionSeriesByNumber2`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsTickByTick`
- Output: `OPTION_SERIES` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Handler to get option series by its index. Series are sorted ascending from near (index 1) to further. It's bar handler.

### Inputs
- [0] `Input0` accepts `OPTION` (required: `True`, stream-only: `False`)

### Parameters
- `ExpirationMode` (`ExpiryMode`), title="Expiration Algo", default=`FixedExpiry`, shown=`True`, optimizable=`True`, help="Algorythm to determine expiration date"
- `Expiry` (`String`), default=`17-11-2014 18:45`, shown=`True`, optimizable=`True`, help="Expiration datetime (including time of a day) for algorythm FixedExpiry"
- `Number` (`int`), title="Series index", default=`1`, range=`1`..`` step ``, shown=`True`, optimizable=`True`, help="Series index (only alive series) for algorythm ExpiryByNumber"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "OptionSeriesByNumber21", "typeName": "OptionSeriesByNumber2", "blockType": "ConverterItem"
    }
  ]
}
```

## QuoteIv

- Display name: Quote volatility
- typeName: `QuoteIv`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsTickByTick`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Quote volatility  Inputs/Output: Inputs=Smile(INTERACTIVESPLINE), OptionSeries(OPTION_SERIES); Output=INTERACTIVESPLINE

### Inputs
- [0] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [1] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)

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
      "op": "AddBlock", "blockId": "QuoteIv1", "typeName": "QuoteIv", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## SetViewport

- Display name: Set Viewport
- typeName: `SetViewport`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsTickByTick`
- Output: `UNKNOWN` (outputs: `0`, only-value-output: `True`)
- Inputs: min `4`, max `4`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Configures a CanvasPane viewport (axes ranges, dividers and grid steps) for option-profile style charts. Uses current underlying price (Fut Px), time to expiry (dT), and a volatility input (sigma / smile / option series) to estimate a meaningful visible region and keep it stable across updates (tick-by-tick handler).

### Inputs
- [0] `Fut Px` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `dT` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [2] `Option Series or Sigma or Smile` accepts `DOUBLE, INTERACTIVESPLINE, OPTION_SERIES` (required: `True`, stream-only: `False`)
- [3] `Canvas pane` accepts `CANVASPANE` (required: `True`, stream-only: `False`)

### Parameters
- `ApplyVisualSettings` (`bool`), title="Apply settings", default=`false`, shown=`True`, optimizable=`True`, help="Apply visual settings"
- `ManageX` (`bool`), title="Manage X", default=`true`, shown=`True`, optimizable=`False`, help="Manage horizontal axis"
- `ManageXGridStep` (`bool`), title="Manage X grid step", default=`false`, shown=`True`, optimizable=`False`, help="Manage horizontal axis grid step"
- `ManageY` (`bool`), title="Manage Y", default=`false`, shown=`True`, optimizable=`False`, help="Manage vertical axis"
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `SigmaMult` (`Double`), title="Width multiplier", default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Width multiplier"
- `VerticalMultiplier` (`Double`), title="Height Multiplier", default=`1.8`, range=`0.001`..`10000000` step `1`, shown=`True`, optimizable=`True`, help="Multiplier to estimate viewport height"
- `XAxisDivisor` (`Double`), title="X axis divisor", default=`1000`, range=`0.000000001`..`10000000` step `1`, shown=`True`, optimizable=`True`, help="X axis divisor"
- `XAxisStep` (`Double`), title="X axis step", default=`5000`, range=`0.000000001`..`10000000` step `1`, shown=`True`, optimizable=`True`, help="X axis grid step"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SetViewport1", "typeName": "SetViewport", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## ShowIvTargets

- Display name: Show IV Targets
- typeName: `ShowIvTargets`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsTickByTick`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `3`, max `3`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Show volatility limit orders  Inputs/Output: Inputs=Smile(INTERACTIVESPLINE), OptionSeries(OPTION_SERIES), Quote IV(INTERACTIVESPLINE); Output=INTERACTIVESPLINE

### Inputs
- [0] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [1] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)
- [2] `Quote IV` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)

### Parameters
- `IsLong` (`bool`), title="Long", default=`false`, shown=`True`, optimizable=`True`, help="Show long orders"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "ShowIvTargets1", "typeName": "ShowIvTargets", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## SingleOption2

- Display name: Single Option
- typeName: `SingleOption2`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsTickByTick`
- Output: `SECURITY` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `2`
- AddBlock container: `ConverterItem`

### What It Does
Extracts a single option security (Call or Put) from an option series. The strike can be fixed (FixedStrike) or supplied as a time series (the last value is used). SelectionMode defines how the strike pair is chosen (FixedStrike/Min/Max/NearestATM). If the required strike is missing: logs a warning in Lab mode; in Agent mode throws a ScriptException to prevent silent nulls (stream handler).

### Inputs
- [0] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)
- [1] `Strike` accepts `DOUBLE` (required: `False`, stream-only: `False`)

### Parameters
- `FixedStrike` (`Double`), title="Strike", default=`120000`, shown=`True`, optimizable=`True`, help="Strike used when SelectionMode=FixedStrike and no strike series input is provided."
- `OptionType` (`StrikeType`), title="Option Type", default=`Call`, shown=`True`, optimizable=`True`, help="Option type (parameter Any is not recommended)"
- `SelectionMode` (`StrikeSelectionMode`), title="Search Algo", default=`FixedStrike`, shown=`True`, optimizable=`True`, help="How to choose the strike pair: FixedStrike uses the Strike parameter; Min/Max choose boundary strikes; NearestATM chooses the pair closest to the underlying last price."

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SingleOption21", "typeName": "SingleOption2", "blockType": "ConverterItem"
    }
  ]
}
```

## SmileImitation3

- Display name: Smile Imitation v3
- typeName: `SmileImitation3`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsTickByTick`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `5`, max `5`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Smile imitation using arbitrary function with 3 parameters  Inputs/Output: Inputs=FutPx(DOUBLE), Time(DOUBLE), Smile(INTERACTIVESPLINE), OptionSeries(OPTION_SERIES), RiskFreeRate(DOUBLE); Output=INTERACTIVESPLINE

### Inputs
- [0] `FutPx` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Time` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [2] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [3] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)
- [4] `RiskFreeRate` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `DepthPct` (`OptimProperty`), title="Depth, %", default=`50.0`, range=`0.0`..`10000.0` step `0.01`, shown=`True`, optimizable=`True`, help="Depth (percents)"
- `GenerateTails` (`bool`), title="Generate Tails", default=`true`, shown=`True`, optimizable=`False`, help="Generate invisible tails"
- `IvAtmPct` (`OptimProperty`), title="IV ATM, %", default=`30.0`, range=`0.000001`..`10000.0` step `0.01`, shown=`True`, optimizable=`True`, help="IV ATM (percents)"
- `SetIvByHands` (`bool`), title="Set IV", default=`false`, shown=`True`, optimizable=`True`, help="Set IV manually"
- `SetSlopeByHands` (`bool`), title="Set Skew Manually", default=`false`, shown=`True`, optimizable=`True`, help="Set skew manually"
- `ShiftPct` (`Double`), title="Shift, %", default=`30.0`, range=`-10000.0`..`10000.0` step `0.01`, shown=`True`, optimizable=`True`, help="Shift (percents)"
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `SigmaMult` (`Double`), title="Width multiplier", default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Width multiplier"
- `SlopeAtmPct` (`OptimProperty`), title="Skew, %", default=`10.0`, range=`-10000.0`..`10000.0` step `0.01`, shown=`True`, optimizable=`True`, help="Skew (percents)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SmileImitation31", "typeName": "SmileImitation3", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## SmileImitation5

- Display name: Smile Imitation v5
- typeName: `SmileImitation5`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsTickByTick`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `5`, max `5`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Smile imitation using application-wide user function in Global Cache  Inputs/Output: Inputs=FutPx(DOUBLE), Time(DOUBLE), Smile(INTERACTIVESPLINE), OptionSeries(OPTION_SERIES), RiskFreeRate(DOUBLE); Output=INTERACTIVESPLINE

### Inputs
- [0] `FutPx` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Time` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [2] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [3] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)
- [4] `RiskFreeRate` accepts `DOUBLE` (required: `True`, stream-only: `False`)

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
      "op": "AddBlock", "blockId": "SmileImitation51", "typeName": "SmileImitation5", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## SmileSelector

- Display name: Select smile
- typeName: `SmileSelector`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsTickByTick`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `2`, max `3`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Select one of several available smiles using handler parameter  Inputs/Output: Inputs=Market(INTERACTIVESPLINE), Model(INTERACTIVESPLINE), Exchange(INTERACTIVESPLINE); Output=INTERACTIVESPLINE

### Inputs
- [0] `Market` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [1] `Model` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [2] `Exchange` accepts `INTERACTIVESPLINE` (required: `False`, stream-only: `False`)

### Parameters
- `SmileIndex` (`int`), title="Input index", default=`1`, range=`1`..`3` step `1`, shown=`True`, optimizable=`True`, help="Input index (start from 1)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SmileSelector1", "typeName": "SmileSelector", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## TimeToExpiry2

- Display name: Time to expiry
- typeName: `TimeToExpiry2`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsTickByTick`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Time to expiry in year fractions. Various algorithms are applied (fixed time, plain calendar time, plain calendar time including days off and so on).

### Inputs
- [0] `AnyOption` accepts `SECURITY, OPTION, OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `CurDateMode` (`CurrentDateMode`), title="Current date algo", default=`CurrentDate`, shown=`True`, optimizable=`True`, help="Current date algorythm"
- `CurrentDateShift` (`TimeSpan`), title="Current date shift", default=`0:0:0`, range=``..`` step `24:0:0`, shown=`True`, optimizable=`True`, help="Shift current date by calendar time interval"
- `DistanceMode` (`TimeRemainMode`), title="Estimation algo", default=`PlainCalendar`, shown=`True`, optimizable=`True`, help="Algorythm to estimate time-to-expiry"
- `ExpirationMode` (`ExpiryMode`), title="Expiration algo", default=`FixedExpiry`, shown=`True`, optimizable=`True`, help="Algorythm to determine expiration date"
- `Expiry` (`String`), default=`17-11-2014 18:45`, shown=`True`, optimizable=`True`, help="Expiration datetime (including time of a day) for algorythm FixedExpiry"
- `ExpiryTime` (`String`), title="Expiry time", default=`18:45`, shown=`True`, optimizable=`True`, help="Expiration time (including time of a day) for algorythms except FixedExpiry"
- `FixedDate` (`String`), title="Frozen 'today'", default=`17-11-2014 18:45`, shown=`True`, optimizable=`True`, help="Today datetime (including time of a day) for algorythm FixedDate"
- `SeriesIndex` (`int`), title="Series index", default=`1`, shown=`True`, optimizable=`True`, help="Series index (only alive series) for algorythm ExpiryByNumber"
- `Time` (`OptimProperty`), default=`0.08`, shown=`True`, optimizable=`True`, help="Time to expiry (just to show it on ControlPane)"
- `UseDays` (`bool`), title="Use days", default=`false`, shown=`True`, optimizable=`False`, help="When true, handler calculates time to expiry as days"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TimeToExpiry21", "typeName": "TimeToExpiry2", "blockType": "ConverterItem"
    }
  ]
}
```

## TransformSmile

- Display name: Transform Smile
- typeName: `TransformSmile`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsTickByTick`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Transform smile as requested in parameters  Inputs/Output: Inputs=Smile(INTERACTIVESPLINE); Output=INTERACTIVESPLINE

### Inputs
- [0] `Smile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)

### Parameters
- `OptPxMode` (`OptionPxMode`), title="Price Mode", default=`Mid`, shown=`True`, optimizable=`False`, help="Algorythm to get option price"
- `ShiftIvPct` (`Double`), title="Shift IV, %", default=`0.0`, range=`-10000.0`..`10000.0` step `0.01`, shown=`True`, optimizable=`True`, help="Additional vertical smile shift (in percents)"
- `SimmWeight` (`Double`), title="Weight", default=`0.5`, range=`-10000.0`..`10000.0` step `0.01`, shown=`True`, optimizable=`True`, help="Weight (0 -- initial function; 0.5 -- simmetrised; 1 -- mirrored)"
- `Transformation` (`SmileTransformation`), default=`LogSimmetrise`, shown=`True`, optimizable=`True`, help="Algorythm to transform smile (LogSimmetrise, Simmetrise, None)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TransformSmile1", "typeName": "TransformSmile", "blockType": "ConverterItem"
    }
  ]
}
```

## VerticalLine2

- Display name: Vertical Line
- typeName: `VerticalLine2`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsTickByTick`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Vertical line for CanvasPane. It is possible to trade base asset using this control.  Inputs/Output: Inputs=FutPx(DOUBLE), AnyOption(SECURITY, OPTION, OPTION_SERIES); Output=INTERACTIVESPLINE

### Inputs
- [0] `FutPx` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `AnyOption` accepts `SECURITY, OPTION, OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `Qty` (`int`), title="Size", default=`1`, range=`-1000000`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Trade quantity. Negative value reverts the signal."
- `SigmaHighPct` (`Double`), title="Sigma high, %", default=`50`, range=`0`..`10000000` step `0.01`, shown=`True`, optimizable=`False`, help="High level of this marker (in percents)"
- `SigmaLowPct` (`Double`), title="Sigma low, %", default=`10`, range=`0`..`10000000` step `0.01`, shown=`True`, optimizable=`False`, help="Low level of this marker (in percents)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "VerticalLine21", "typeName": "VerticalLine2", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

