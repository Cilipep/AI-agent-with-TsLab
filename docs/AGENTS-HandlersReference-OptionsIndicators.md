# Handlers Reference: OptionsIndicators

For each handler below:
- `typeName` is the string you pass to `/api/handlers/{typeName}` and `AddBlock` (`typeName` field).
- `blockType` is the container you must use for handler-based blocks (not template blocks).
- Input indices are zero-based (`toPort`).
- Hidden handlers (`[HandlerInvisible]`) require `allowHiddenHandler=true` in `AddBlock` (advanced). Some legacy helpers (e.g. `CycleHandler`) may be auto-converted to template blocks.

## CentralStrike

- Display name: Central Strike
- typeName: `CentralStrike`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsIndicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Computes the "central" (ATM-like) strike of an option series per bar by locating where the underlying price sits between adjacent strikes and applying a hysteresis switch (Switch Ratio), optional strike shifting (Shift Strike), and optional Strike Step filtering. Outputs a time series aligned to the underlying bars (stream handler) and caches results by bar time to stabilize switching.

### Inputs
- [0] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `True`)

### Parameters
- `DisplayPrice` (`OptimProperty`), title="Display Price", default=`120000`, shown=`True`, optimizable=`True`, help="Base asset price (only to display at UI)"
- `DisplayUnits` (`FixedValueMode`), title="Display Units", default=`AsIs`, shown=`True`, optimizable=`False`, help="Display units (hundreds, thousands, as is)"
- `ShiftStrike` (`int`), title="Shift strike", default=`0`, range=`-10000000`..`10000000` step `1`, shown=`True`, optimizable=`True`, help="Shift central strike (number of strikes)"
- `StrikeStep` (`Double`), title="Strike step", default=`0`, range=`0`..`10000000` step `1`, shown=`True`, optimizable=`True`, help="Strike step to extract most important options"
- `SwitchRatioPct` (`Double`), title="Switch Ratio Pct", default=`62`, range=`50`..`100` step `1`, shown=`True`, optimizable=`True`, help="Market should pass this percent of distance to next strike to switch central strike"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "CentralStrike1", "typeName": "CentralStrike", "blockType": "ConverterItem"
    }
  ]
}
```

## FixedValue

- Display name: Fixed Value
- typeName: `FixedValue`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsIndicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Fixed value  Inputs/Output: Inputs=AnyOption(SECURITY, OPTION, OPTION_SERIES); Output=DOUBLE

### Inputs
- [0] `AnyOption` accepts `SECURITY, OPTION, OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `DisplayUnits` (`FixedValueMode`), title="Display Units", default=`AsIs`, shown=`True`, optimizable=`False`, help="Display units (hundreds, thousands, as is)"
- `MinValue` (`Double`), title="Minimum", default=`1e-6`, range=`-10000000`..`10000000` step `1`, shown=`True`, optimizable=`False`, help="Minimum for internal representation"
- `Value` (`Double`), default=`120000`, range=`-10000000`..`10000000` step `1`, shown=`True`, optimizable=`True`, help="Constant value (always above the limit 'Minimum')"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "FixedValue1", "typeName": "FixedValue", "blockType": "ConverterItem"
    }
  ]
}
```

## ForwardTheorPx

- Display name: Forward Price
- typeName: `ForwardTheorPx`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsIndicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Base asset price calculated using theretical option prices  Inputs/Output: Inputs=OptionSeries(OPTION_SERIES); Output=DOUBLE

### Inputs
- [0] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `True`)

### Parameters
- `Strike` (`Double`), default=`120000`, shown=`True`, optimizable=`False`, help="Strike to calculate forward price"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "ForwardTheorPx1", "typeName": "ForwardTheorPx", "blockType": "ConverterItem"
    }
  ]
}
```

## GetValueAtm

- Display name: Get Value ATM (IntSer)
- typeName: `GetValueAtm`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsIndicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Numerical estimate of value at-the-money (only one point of profile is returned)  Inputs/Output: Inputs=Profile(INTERACTIVESPLINE), Moneyness(DOUBLE); Output=DOUBLE

### Inputs
- [0] `Profile` accepts `INTERACTIVESPLINE` (required: `True`, stream-only: `False`)
- [1] `Moneyness` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Moneyness` (`Double`), default=`0`, range=`-10000000`..`10000000` step `1`, shown=`True`, optimizable=`True`, help="Moneyness"
- `PrintInLog` (`bool`), title="Print in Log", default=`False`, shown=`True`, optimizable=`True`, help="Print in main log"
- `RepeatLastValue` (`bool`), title="Repeat Last Value", default=`false`, shown=`True`, optimizable=`True`, help="Handler should repeat last known value to avoid further logic errors"
- `Result` (`OptimProperty`), shown=`True`, optimizable=`True`, help="Value ATM"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "GetValueAtm1", "typeName": "GetValueAtm", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## GlobalHv

- Display name: Global HV
- typeName: `GlobalHv`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsIndicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
This block takes precalculated HV from global cache.  Inputs/Output: Inputs=AnyOption(SECURITY, OPTION, OPTION_SERIES); Output=DOUBLE

### Inputs
- [0] `AnyOption` accepts `SECURITY, OPTION, OPTION_SERIES` (required: `True`, stream-only: `True`)

### Parameters
- `AnnualizingMultiplier` (`Double`), title="Annualizing Multiplier", default=`500`, range=`0`..`10000000` step `1`, shown=`True`, optimizable=`True`, help="Multiplier to convert volatility to annualized value"
- `Period` (`int`), default=`990`, range=`2`..`10000000` step `1`, shown=`True`, optimizable=`True`, help="Calculation period"
- `RepeatLastHv` (`bool`), title="Repeat Last HV", default=`false`, shown=`True`, optimizable=`True`, help="When true it will find and repeat last known value in case when current value is unavailable"
- `Timeframe` (`int`), default=`60`, range=`1`..`10000000` step `1`, shown=`True`, optimizable=`True`, help="Timeframe (seconds)"
- `UseAllData` (`bool`), title="Use All Data", default=`false`, shown=`True`, optimizable=`True`, help="Should handler use all data including overnight gaps?"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "GlobalHv1", "typeName": "GlobalHv", "blockType": "ConverterItem"
    }
  ]
}
```

## GlobalIvOnF

- Display name: Global IV ATM
- typeName: `GlobalIvOnF`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsIndicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
This block takes precalculated IvOnF from global cache.  Inputs/Output: Inputs=Security or Option Series(SECURITY, OPTION_SERIES); Output=DOUBLE

### Inputs
- [0] `Security or Option Series` accepts `SECURITY, OPTION_SERIES` (required: `True`, stream-only: `True`)

### Parameters
- `DistanceMode` (`TimeRemainMode`), title="Estimation Algo", default=`PlainCalendar`, shown=`True`, optimizable=`False`, help="Algorythm to estimate time-to-expiry"
- `ExpirationMode` (`ExpiryMode`), title="Search Mode", default=`FixedExpiry`, shown=`True`, optimizable=`False`, help="Algorythm to get expiration date"
- `Expiry` (`String`), default=`2015-03-16`, shown=`True`, optimizable=`True`, help="Expiration date (format yyyy-MM-dd)"
- `IgnoreCacheError` (`bool`), title="Ignore cache error", default=`false`, shown=`True`, optimizable=`False`, help="Handler should ignore cache errors in agent mode"
- `Number` (`int`), default=`1`, range=`1`..`100000` step `1`, shown=`True`, optimizable=`False`, help="Option series index (only alive). Parameter is used in mode ExpiryByNumber."
- `RepeatLastIv` (`bool`), title="Repeat Last IV", default=`false`, shown=`True`, optimizable=`True`, help="Handler should repeat last known value to avoid further logic errors"
- `RescaleTime` (`bool`), title="Rescale Time", default=`false`, shown=`True`, optimizable=`False`, help="Rescale time-to-expiry to our internal?"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "GlobalIvOnF1", "typeName": "GlobalIvOnF", "blockType": "ConverterItem"
    }
  ]
}
```

## GlobalSkewOnF

- Display name: Global Skew ATM
- typeName: `GlobalSkewOnF`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsIndicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
This block takes precalculated skew at the money from global cache.  Inputs/Output: Inputs=Security or Option Series(SECURITY, OPTION_SERIES); Output=DOUBLE

### Inputs
- [0] `Security or Option Series` accepts `SECURITY, OPTION_SERIES` (required: `True`, stream-only: `True`)

### Parameters
- `DistanceMode` (`TimeRemainMode`), title="Estimation algo", default=`PlainCalendar`, shown=`True`, optimizable=`False`, help="Algorythm to estimate time-to-expiry"
- `ExpirationMode` (`ExpiryMode`), title="Search mode", default=`FixedExpiry`, shown=`True`, optimizable=`False`, help="Algorythm to get expiration date"
- `Expiry` (`String`), default=`2015-03-16`, shown=`True`, optimizable=`True`, help="Expiration date (format yyyy-MM-dd)"
- `IgnoreCacheError` (`bool`), title="Ignore cache error", default=`false`, shown=`True`, optimizable=`False`, help="Handler should ignore cache errors in agent mode"
- `Number` (`int`), default=`1`, range=`1`..`100000` step `1`, shown=`True`, optimizable=`False`, help="Option series index (only alive). Parameter is used in mode ExpiryByNumber."
- `RepeatLastSkew` (`bool`), title="Repeat last skew", default=`false`, shown=`True`, optimizable=`True`, help="Handler should repeat last known value to avoid further logic errors"
- `RescaleTime` (`bool`), title="Rescale time", default=`false`, shown=`True`, optimizable=`False`, help="Rescale time-to-expiry to our internal?"
- `SkewMode` (`SmileSkewMode`), title="Skew mode", default=`RescaledSkew`, shown=`True`, optimizable=`False`, help="Algorythm to get smile skew"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "GlobalSkewOnF1", "typeName": "GlobalSkewOnF", "blockType": "ConverterItem"
    }
  ]
}
```

## HV

- Display name: HV (from book)
- typeName: `HV`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsIndicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Estimate HV with classic method  Inputs/Output: Inputs=AnyOption(SECURITY, OPTION, OPTION_SERIES); Output=DOUBLE

### Inputs
- [0] `AnyOption` accepts `SECURITY, OPTION, OPTION_SERIES` (required: `True`, stream-only: `True`)

### Parameters
- `AllowGlobalReadWrite` (`bool`), title="Allow Global Write", default=`false`, shown=`True`, optimizable=`True`, help="Permission to write to Global Cache"
- `AnnualizingMultiplier` (`Double`), title="Annualizing Multiplier", default=`500`, range=`0`..`10000000` step `1`, shown=`True`, optimizable=`True`, help="Multiplier to convert volatility to annualized value"
- `GlobalSavePeriod` (`int`), title="Global Save Period", default=`2`, range=`1`..`10000000` step `1`, shown=`True`, optimizable=`True`, help="Period to write to Global Cache"
- `Period` (`int`), default=`990`, range=`2`..`10000000` step `1`, shown=`True`, optimizable=`True`, help="Calculation period"
- `Reset` (`bool`), title="Repeat", default=`true`, shown=`True`, optimizable=`True`, help="Repeat calculation for all bars every execution"
- `UseAllData` (`bool`), title="Use All Data", default=`false`, shown=`True`, optimizable=`True`, help="Should handler use all data including overnight gaps?"
- `UseGlobalCache` (`bool`), title="Use Global Cache", default=`false`, shown=`True`, optimizable=`True`, help="Use global cache"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "HV1", "typeName": "HV", "blockType": "ConverterItem"
    }
  ]
}
```

## IvOnF

- Display name: IV ATM
- typeName: `IvOnF`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsIndicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Implied Volatility at-the-money  Inputs/Output: Inputs=OptionSeries(OPTION_SERIES); Output=DOUBLE

### Inputs
- [0] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `True`)

### Parameters
- `AllowGlobalReadWrite` (`bool`), title="Allow Global Write", default=`false`, shown=`True`, optimizable=`True`, help="Permission to write to Global Cache"
- `DistanceMode` (`TimeRemainMode`), title="Estimation Algo", default=`PlainCalendar`, shown=`True`, optimizable=`False`, help="Algorythm to estimate time-to-expiry"
- `ExpiryTime` (`String`), title="Expiry Time", default=`18:45`, shown=`True`, optimizable=`True`, help="Exact expiration time of day (HH:mm)"
- `GlobalSavePeriod` (`int`), title="Global Save Period", default=`2`, range=`1`..`10000000` step `1`, shown=`True`, optimizable=`True`, help="Period to write to Global Cache"
- `MaxStrike` (`Double`), title="Max strike", default=`1500000`, range=`0`..`10000000` step `1`, shown=`True`, optimizable=`False`, help="Max strike to be processed by handler"
- `MinStrike` (`Double`), title="Min strike", default=`1`, range=`0`..`10000000` step `1`, shown=`True`, optimizable=`False`, help="Min strike to be processed by handler"
- `RepeatLastIv` (`bool`), title="Repeat Last IV", default=`false`, shown=`True`, optimizable=`True`, help="Handler should repeat last known value to avoid further logic errors"
- `RescaleTime` (`bool`), title="Rescale Time", default=`false`, shown=`True`, optimizable=`False`, help="Rescale time-to-expiry to our internal?"
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `StrikeStep` (`Double`), title="Strike step", default=`2500`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`False`, help="Strike step"
- `UseGlobalCache` (`bool`), title="Use Global Cache", default=`false`, shown=`True`, optimizable=`True`, help="Use global cache"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "IvOnF1", "typeName": "IvOnF", "blockType": "ConverterItem"
    }
  ]
}
```

## IvOnF2

- Display name: IV ATM (by tick)
- typeName: `IvOnF2`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsIndicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Implied Volatility at-the-money  Inputs/Output: Inputs=OptionSeries(OPTION_SERIES); Output=DOUBLE

### Inputs
- [0] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `AllowGlobalReadWrite` (`bool`), title="Allow Global Write", default=`false`, shown=`True`, optimizable=`True`, help="Permission to write to Global Cache"
- `DistanceMode` (`TimeRemainMode`), title="Estimation Algo", default=`PlainCalendar`, shown=`True`, optimizable=`False`, help="Algorythm to estimate time-to-expiry"
- `ExpiryTime` (`String`), title="Expiry Time", default=`18:45`, shown=`True`, optimizable=`True`, help="Exact expiration time of day (HH:mm)"
- `GlobalSavePeriod` (`int`), title="Global Save Period", default=`2`, range=`1`..`10000000` step `1`, shown=`True`, optimizable=`True`, help="Period to write to Global Cache"
- `RepeatLastIv` (`bool`), title="Repeat Last IV", default=`false`, shown=`True`, optimizable=`True`, help="Handler should repeat last known value to avoid further logic errors"
- `RescaleTime` (`bool`), title="Rescale Time", default=`false`, shown=`True`, optimizable=`False`, help="Rescale time-to-expiry to our internal?"
- `UseGlobalCache` (`bool`), title="Use Global Cache", default=`false`, shown=`True`, optimizable=`True`, help="Use global cache"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "IvOnF21", "typeName": "IvOnF2", "blockType": "ConverterItem"
    }
  ]
}
```

## IvOnFAllSeries

- Display name: IV ATM (all series)
- typeName: `IvOnFAllSeries`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsIndicators`
- Output: `UNKNOWN` (outputs: `0`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Implied Volatility at-the-money (all option series are processed)  Inputs/Output: Inputs=OPTIONSource(OPTION); Output=UNKNOWN

### Inputs
- [0] `OPTIONSource` accepts `OPTION` (required: `True`, stream-only: `True`)

### Parameters
- `DistanceMode` (`TimeRemainMode`), title="Estimation Algo", default=`PlainCalendar`, shown=`True`, optimizable=`False`, help="Algorythm to estimate time-to-expiry"
- `ExpiryTime` (`String`), title="Expiry Time", default=`18:45`, shown=`True`, optimizable=`False`, help="Exact expiration time of day (HH:mm)"
- `RescaleTime` (`bool`), title="Rescale Time", default=`false`, shown=`True`, optimizable=`False`, help="Rescale time-to-expiry to our internal?"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "IvOnFAllSeries1", "typeName": "IvOnFAllSeries", "blockType": "ConverterItem"
    }
  ]
}
```

## LastValueToParameter

- Display name: Last Value
- typeName: `LastValueToParameter`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsIndicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Convert last value in series to parameter  Inputs/Output: Inputs=Input0(DOUBLE); Output=DOUBLE

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `LastValue` (`Double`), title="Last value", default=`0`, shown=`True`, optimizable=`False`, help="Last value"
- `Result` (`OptimProperty`), title="Display value", default=`0`, shown=`True`, optimizable=`True`, help="Display value (just to show it on ControlPane)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "LastValueToParameter1", "typeName": "LastValueToParameter", "blockType": "ConverterItem"
    }
  ]
}
```

## LoadFromGlobalCache

- Display name: Load from Global Cache (old)
- typeName: `LoadFromGlobalCache`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsIndicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Load indicator from Global Cache  Inputs/Output: Inputs=AnyOption(SECURITY, OPTION, OPTION_SERIES); Output=DOUBLE

### Inputs
- [0] `AnyOption` accepts `SECURITY, OPTION, OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `AgentName` (`String`), title="Agent name", shown=`True`, optimizable=`True`, help="Name of the agent that writes to Global Cache"
- `LoadFromStorage` (`bool`), title="Load from disk", default=`true`, shown=`True`, optimizable=`True`, help="Load from HDD to use indicator values across different program sessions"
- `OverrideSymbol` (`String`), title="Override security", shown=`True`, optimizable=`True`, help="Override security (use this ticker instead of handler's input)"
- `RepeatLastValue` (`bool`), title="Repeat last value", default=`false`, shown=`True`, optimizable=`True`, help="Handler should repeat last known value to avoid further logic errors"
- `ValuesName` (`String`), title="Values name", shown=`True`, optimizable=`True`, help="Unique indicator name to be used to store values in Global Cache"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "LoadFromGlobalCache1", "typeName": "LoadFromGlobalCache", "blockType": "ConverterItem"
    }
  ]
}
```

## PrepareLineForCanvasPane

- Display name: Prepare line
- typeName: `PrepareLineForCanvasPane`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsIndicators`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Merge two series of numbers to InteractiveSeries  Inputs/Output: Inputs=X(DOUBLE), Y(DOUBLE); Output=INTERACTIVESPLINE

### Inputs
- [0] `X` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Y` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "PrepareLineForCanvasPane1", "typeName": "PrepareLineForCanvasPane", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## SaveToGlobalCache

- Display name: Save to Global Cache (old)
- typeName: `SaveToGlobalCache`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsIndicators`
- Output: `UNKNOWN` (outputs: `0`, only-value-output: `False`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Save any indicator to Global Cache  Inputs/Output: Inputs=AnyOption(SECURITY, OPTION, OPTION_SERIES), Indicator(DOUBLE); Output=UNKNOWN

### Inputs
- [0] `AnyOption` accepts `SECURITY, OPTION, OPTION_SERIES` (required: `True`, stream-only: `False`)
- [1] `Indicator` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `MaxValues` (`int`), title="Maximum numbers", default=`0`, shown=`True`, optimizable=`True`, help="Maximum number of stored values. If 0, then it will be limited by the number of bars"
- `RepeatLastValue` (`bool`), title="Repeat last value", default=`false`, shown=`True`, optimizable=`True`, help="Handler should repeat last known value to avoid further logic errors"
- `SaveToStorage` (`bool`), title="Save to disk", default=`true`, shown=`True`, optimizable=`True`, help="Save to HDD to use indicator values across different program sessions"
- `ValuesName` (`String`), title="Values name", shown=`True`, optimizable=`True`, help="Unique indicator name to be used to store values in Global Cache"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SaveToGlobalCache1", "typeName": "SaveToGlobalCache", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## TimeToExpiry

- Display name: Time to expiry
- typeName: `TimeToExpiry`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsIndicators`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Time to expiry in year fractions. Various algorithms are applied (fixed time, plain calendar time, plain calendar time including days off and so on).

### Inputs
- [0] `AnyOption` accepts `SECURITY, OPTION, OPTION_SERIES` (required: `True`, stream-only: `True`)

### Parameters
- `CurDateMode` (`CurrentDateMode`), title="Current date algo", default=`CurrentDate`, shown=`True`, optimizable=`True`, help="Current date algorythm"
- `CurrentDateShift` (`TimeSpan`), title="Current date shift", default=`0:0:0`, range=``..`` step `24:0:0`, shown=`True`, optimizable=`True`, help="Shift current date by calendar time interval"
- `DistanceMode` (`TimeRemainMode`), title="Estimation algo", default=`PlainCalendar`, shown=`True`, optimizable=`True`, help="Algorythm to estimate time-to-expiry"
- `ExpirationMode` (`ExpiryMode`), title="Expiration algo", default=`FixedExpiry`, shown=`True`, optimizable=`True`, help="Algorythm to determine expiration date"
- `Expiry` (`String`), default=`17-11-2014 18:45`, shown=`True`, optimizable=`True`, help="Expiration datetime (including time of a day) for algorythm FixedExpiry"
- `ExpiryTime` (`String`), title="Expiry time", default=`18:45`, shown=`True`, optimizable=`True`, help="Expiration time (including time of a day) for algorythms EXCEPT FixedExpiry"
- `FixedDate` (`String`), title="Frozen 'today'", default=`17-11-2014 18:45`, shown=`True`, optimizable=`True`, help="Today datetime (including time of a day) for algorythm FixedDate"
- `SeriesIndex` (`int`), title="Series index", default=`1`, shown=`True`, optimizable=`True`, help="Series index (only alive series) for algorythm ExpiryByNumber"
- `Time` (`OptimProperty`), default=`0.08`, shown=`True`, optimizable=`True`, help="Time to expiry (just to show it on ControlPane)"
- `UseDays` (`bool`), title="Use days", default=`false`, shown=`True`, optimizable=`False`, help="When true, handler calculates time to expiry as days"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TimeToExpiry1", "typeName": "TimeToExpiry", "blockType": "ConverterItem"
    }
  ]
}
```

