# Handlers Reference: OptionsPublic

For each handler below:
- `typeName` is the string you pass to `/api/handlers/{typeName}` and `AddBlock` (`typeName` field).
- `blockType` is the container you must use for handler-based blocks (not template blocks).
- Input indices are zero-based (`toPort`).
- Hidden handlers (`[HandlerInvisible]`) require `allowHiddenHandler=true` in `AddBlock` (advanced). Some legacy helpers (e.g. `CycleHandler`) may be auto-converted to template blocks.

## BasePxPublic

- Display name: Base Price
- typeName: `BasePxPublic`
- Namespace: `TSLab.Script.Handlers.OptionsPublic`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPublic`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Base asset price. Different algorythms are available (fixed price, last trade, quote midpoint, etc). Bar handler.

### Inputs
- [0] `Input0` accepts `SECURITY, OPTION, OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `DisplayPrice` (`OptimProperty`), default=`120000`, shown=`True`, optimizable=`True`
- `DisplayUnits` (`FixedValueMode`), default=`AsIs`, shown=`True`, optimizable=`False`
- `FixedPx` (`Double`), default=`120000`, shown=`True`, optimizable=`False`
- `PxMode` (`BasePxMode`), default=`LastTrade`, shown=`True`, optimizable=`False`
- `RepeatLastPx` (`bool`), default=`false`, shown=`True`, optimizable=`True`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BasePxPublic1", "typeName": "BasePxPublic", "blockType": "ConverterItem"
    }
  ]
}
```

## BuyOptionsPublic

- Display name: Buy Options
- typeName: `BuyOptionsPublic`
- Namespace: `TSLab.Script.Handlers.OptionsPublic`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPublic`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `8`, max `8`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Buy options while position risk is 'small'

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
- `EntryShift` (`int`), default=`0`, range=`-1000000`..`1000000` step `1`, shown=`True`, optimizable=`True`
- `ExitShift` (`int`), default=`0`, range=`-1000000`..`1000000` step `1`, shown=`True`, optimizable=`True`
- `FixedQty` (`int`), default=`1`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`
- `OptionType` (`StrikeType`), default=`Call`, shown=`True`, optimizable=`True`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BuyOptionsPublic1", "typeName": "BuyOptionsPublic", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## GlobalHvPublic

- Display name: Global HV
- typeName: `GlobalHvPublic`
- Namespace: `TSLab.Script.Handlers.OptionsPublic`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPublic`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
This block takes precalculated HV from global cache.

### Inputs
- [0] `AnyOption` accepts `SECURITY, OPTION, OPTION_SERIES` (required: `True`, stream-only: `True`)

### Parameters
- `AnnualizingMultiplier` (`Double`), default=`452`, range=`0`..`10000000` step `1`, shown=`True`, optimizable=`True`
- `Period` (`int`), default=`810`, range=`2`..`10000000` step `1`, shown=`True`, optimizable=`True`
- `RepeatLastHv` (`bool`), default=`false`, shown=`True`, optimizable=`True`
- `Timeframe` (`int`), default=`60`, range=`1`..`10000000` step `1`, shown=`True`, optimizable=`True`
- `UseAllData` (`bool`), default=`false`, shown=`True`, optimizable=`True`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "GlobalHvPublic1", "typeName": "GlobalHvPublic", "blockType": "ConverterItem"
    }
  ]
}
```

## HVPublic

- Display name: HV (from book)
- typeName: `HVPublic`
- Namespace: `TSLab.Script.Handlers.OptionsPublic`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPublic`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Estimate HV with classic method

### Inputs
- [0] `AnyOption` accepts `SECURITY, OPTION, OPTION_SERIES` (required: `True`, stream-only: `True`)

### Parameters
- `AllowGlobalReadWrite` (`bool`), default=`false`, shown=`True`, optimizable=`True`
- `AnnualizingMultiplier` (`Double`), default=`452`, range=`0`..`10000000` step `1`, shown=`True`, optimizable=`True`
- `GlobalSavePeriod` (`int`), default=`2`, range=`1`..`10000000` step `1`, shown=`True`, optimizable=`True`
- `Period` (`int`), default=`810`, range=`2`..`10000000` step `1`, shown=`True`, optimizable=`True`
- `Reset` (`bool`), default=`true`, shown=`True`, optimizable=`True`
- `UseAllData` (`bool`), default=`false`, shown=`True`, optimizable=`True`
- `UseGlobalCache` (`bool`), default=`false`, shown=`True`, optimizable=`True`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "HVPublic1", "typeName": "HVPublic", "blockType": "ConverterItem"
    }
  ]
}
```

## SmileImitation3Public

- Display name: Smile Imitation v3
- typeName: `SmileImitation3Public`
- Namespace: `TSLab.Script.Handlers.OptionsPublic`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPublic`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `4`, max `4`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Smile imitation using arbitrary function with 3 parameters

### Inputs
- [0] `FutPx` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Time` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [2] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `False`)
- [3] `RiskFreeRate` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `DepthPct` (`OptimProperty`), default=`50.0`, range=`0.0`..`10000.0` step `0.01`, shown=`True`, optimizable=`True`
- `GenerateTails` (`bool`), default=`true`, shown=`True`, optimizable=`False`
- `IvAtmPct` (`OptimProperty`), default=`30.0`, range=`0.000001`..`10000.0` step `0.01`, shown=`True`, optimizable=`True`
- `ShiftPct` (`Double`), default=`30.0`, range=`-10000.0`..`10000.0` step `0.01`, shown=`True`, optimizable=`True`
- `ShowNodes` (`bool`), default=`false`, shown=`True`, optimizable=`True`
- `SigmaMult` (`Double`), default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`
- `SlopeAtmPct` (`OptimProperty`), default=`10.0`, range=`-10000.0`..`10000.0` step `0.01`, shown=`True`, optimizable=`True`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SmileImitation3Public1", "typeName": "SmileImitation3Public", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## TimeToExpiryPublic

- Display name: Time to expiry
- typeName: `TimeToExpiryPublic`
- Namespace: `TSLab.Script.Handlers.OptionsPublic`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsPublic`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Time to expiry as a fraction of year. Different algorythms are available.

### Inputs
- [0] `Input0` accepts `SECURITY, OPTION, OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `CurDateMode` (`CurrentDateMode`), default=`CurrentDate`, shown=`True`, optimizable=`True`
- `DistanceMode` (`TimeRemainMode`), default=`PlainCalendar`, shown=`True`, optimizable=`True`
- `ExpirationMode` (`ExpiryMode`), default=`FixedExpiry`, shown=`True`, optimizable=`True`
- `Expiry` (`String`), default=`17-11-2014 18:45`, shown=`True`, optimizable=`True`
- `ExpiryTime` (`String`), default=`18:45`, shown=`True`, optimizable=`True`
- `FixedDate` (`String`), default=`17-11-2014 18:45`, shown=`True`, optimizable=`True`
- `SeriesIndex` (`int`), default=`1`, shown=`True`, optimizable=`True`
- `Time` (`OptimProperty`), default=`0.08`, shown=`True`, optimizable=`True`
- `UseDays` (`bool`), default=`false`, shown=`True`, optimizable=`False`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TimeToExpiryPublic1", "typeName": "TimeToExpiryPublic", "blockType": "ConverterItem"
    }
  ]
}
```

