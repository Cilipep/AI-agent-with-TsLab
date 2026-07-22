# Handlers Reference: RusAlgo

For each handler below:
- `typeName` is the string you pass to `/api/handlers/{typeName}` and `AddBlock` (`typeName` field).
- `blockType` is the container you must use for handler-based blocks (not template blocks).
- Input indices are zero-based (`toPort`).
- Hidden handlers (`[HandlerInvisible]`) require `allowHiddenHandler=true` in `AddBlock` (advanced). Some legacy helpers (e.g. `CycleHandler`) may be auto-converted to template blocks.

## TickTestHandler

- Display name: TickTestHandler
- typeName: `TickTestHandler`
- Namespace: `TSLab.Helper.Handlers`
- Assembly: `TSLab.Script.Handlers`
- HandlerName attribute: `Ticks Test` (folder: ``, dynamic: `False`)
- Category: `RusAlgo`
- Output: `SECURITY` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No English description is available in handler metadata; treat the name and IO contract as authoritative.

### Inputs
- [0] `Instrument` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `MaxError` (`UInt32`), default=`10`, shown=`True`, optimizable=`False`
- `TickDate` (`bool`), default=`true`, shown=`True`, optimizable=`False`
- `TickPrice` (`bool`), default=`true`, shown=`True`, optimizable=`False`
- `TickVolume` (`bool`), default=`true`, shown=`True`, optimizable=`False`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TickTestHandler1", "typeName": "TickTestHandler", "blockType": "ConverterItem"
    }
  ]
}
```

