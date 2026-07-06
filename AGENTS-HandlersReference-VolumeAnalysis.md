# Handlers Reference: VolumeAnalysis

For each handler below:
- `typeName` is the string you pass to `/api/handlers/{typeName}` and `AddBlock` (`typeName` field).
- `blockType` is the container you must use for handler-based blocks (not template blocks).
- Input indices are zero-based (`toPort`).
- Hidden handlers (`[HandlerInvisible]`) require `allowHiddenHandler=true` in `AddBlock` (advanced). Some legacy helpers (e.g. `CycleHandler`) may be auto-converted to template blocks.

## BuysHandler

- Display name: Buys
- typeName: `BuysHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `VolumeAnalysis`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
A handler calculates statistics (amount or total volume) of a long trades  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `QuantityMode` (`QuantityMode`), title="Quantity units", default=`Quantity`, shown=`True`, optimizable=`True`, help="Market volume quantity units (shares, lots, trades count)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BuysHandler1", "typeName": "BuysHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## BuysMinusSellsHandler

- Display name: Buys Minus Sells
- typeName: `BuysMinusSellsHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `VolumeAnalysis`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
A handler calculates statistics difference (amount or total volume) of a long and short trades  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `QuantityMode` (`QuantityMode`), title="Quantity units", default=`Quantity`, shown=`True`, optimizable=`True`, help="Market volume quantity units (shares, lots, trades count)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BuysMinusSellsHandler1", "typeName": "BuysMinusSellsHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## SellsHandler

- Display name: Sells
- typeName: `SellsHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `VolumeAnalysis`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
A handler calculates statistics (amount or total volume) of a short trades  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `QuantityMode` (`QuantityMode`), title="Quantity units", default=`Quantity`, shown=`True`, optimizable=`True`, help="Market volume quantity units (shares, lots, trades count)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SellsHandler1", "typeName": "SellsHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## VolumeForPeriodHandler

- Display name: Volume for period
- typeName: `VolumeForPeriodHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `VolumeAnalysis`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Volume for period (total or average)  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `TimeFrame` (`int`), default=`1`, range=`1`..`365` step `1`, shown=`True`, optimizable=`True`, help="Timeframe (integer value in units of parameter 'Timeframe units')"
- `TimeFrameUnit` (`TimeFrameUnit`), title="Timeframe units", default=`Hour`, shown=`True`, optimizable=`True`, help="Timeframe units (second, minute, hour, day)"
- `ValueMode` (`ValueForPeriodMode`), title="Processing algo", default=`Sum`, shown=`True`, optimizable=`True`, help="Processing algo (sum or average)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "VolumeForPeriodHandler1", "typeName": "VolumeForPeriodHandler", "blockType": "ConverterItem"
    }
  ]
}
```

