# Handlers Reference: OptionsBugs

For each handler below:
- `typeName` is the string you pass to `/api/handlers/{typeName}` and `AddBlock` (`typeName` field).
- `blockType` is the container you must use for handler-based blocks (not template blocks).
- Input indices are zero-based (`toPort`).
- Hidden handlers (`[HandlerInvisible]`) require `allowHiddenHandler=true` in `AddBlock` (advanced). Some legacy helpers (e.g. `CycleHandler`) may be auto-converted to template blocks.

## RaiseException

- Display name: Raise exception
- typeName: `RaiseException`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsBugs`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Raise exception

### Inputs
- [0] `AnyOption` accepts `SECURITY, OPTION, OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `Raise` (`bool`), default=`false`, shown=`True`, optimizable=`True`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "RaiseException1", "typeName": "RaiseException", "blockType": "ConverterItem"
    }
  ]
}
```

## Random

- Display name: Random
- typeName: `Random`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsBugs`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Random numbers generator

### Inputs
- [0] `AnyOption` accepts `SECURITY, OPTION, OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `AllLogTypes` (`bool`), default=`false`, shown=`True`, optimizable=`True`
- `BlockTrading` (`BoolOptimProperty`), default=`true`, shown=`True`, optimizable=`True`
- `ExpirationMode` (`ExpiryMode`), default=`FixedExpiry`, shown=`True`, optimizable=`True`
- `Rnd` (`OptimProperty`), default=`3.1415`, shown=`True`, optimizable=`True`
- `TextString` (`String`), default=`Change Me!`, shown=`True`, optimizable=`True`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Random1", "typeName": "Random", "blockType": "ConverterItem"
    }
  ]
}
```

## RandomPersistent

- Display name: Random Persistent
- typeName: `RandomPersistent`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `OptionsBugs`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Random numbers generator stores its history in Global cache

### Inputs
- [0] `AnyOption` accepts `SECURITY, OPTION, OPTION_SERIES` (required: `True`, stream-only: `False`)

### Parameters
- `AllowGlobalReadWrite` (`bool`), default=`false`, shown=`True`, optimizable=`True`
- `BlockTrading` (`BoolOptimProperty`), default=`true`, shown=`True`, optimizable=`True`
- `GlobalSavePeriod` (`int`), default=`1`, shown=`True`, optimizable=`True`
- `Rnd` (`OptimProperty`), default=`3.1415`, shown=`True`, optimizable=`True`
- `UseGlobalCache` (`bool`), default=`false`, shown=`True`, optimizable=`True`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "RandomPersistent1", "typeName": "RandomPersistent", "blockType": "ConverterItem"
    }
  ]
}
```

