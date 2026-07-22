# Handlers Reference: CanvasPaneHandler

For each handler below:
- `typeName` is the string you pass to `/api/handlers/{typeName}` and `AddBlock` (`typeName` field).
- `blockType` is the container you must use for handler-based blocks (not template blocks).
- Input indices are zero-based (`toPort`).
- Hidden handlers (`[HandlerInvisible]`) require `allowHiddenHandler=true` in `AddBlock` (advanced). Some legacy helpers (e.g. `CycleHandler`) may be auto-converted to template blocks.

## TestCanvasPaneHandler

- Display name: Test Canvas Pane Handler
- typeName: `TestCanvasPaneHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `CanvasPaneHandler`
- Output: `CANVASPANE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Test handler to check interaction with a CanvasPane. It is visible in developer build only.

### Inputs
- [0] `CanvasPaneHandler` accepts `CANVASPANE` (required: `True`, stream-only: `True`)

### Parameters
- `Value` (`OptimProperty`), default=`100`, shown=`True`, optimizable=`True`, help="Value of a constant"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TestCanvasPaneHandler1", "typeName": "TestCanvasPaneHandler", "blockType": "ConverterItem"
    }
  ]
}
```

