# Handlers Reference: GraphPaneHandler

For each handler below:
- `typeName` is the string you pass to `/api/handlers/{typeName}` and `AddBlock` (`typeName` field).
- `blockType` is the container you must use for handler-based blocks (not template blocks).
- Input indices are zero-based (`toPort`).
- Hidden handlers (`[HandlerInvisible]`) require `allowHiddenHandler=true` in `AddBlock` (advanced). Some legacy helpers (e.g. `CycleHandler`) may be auto-converted to template blocks.

## InteractiveConstGen

- Display name: Interactive constant
- typeName: `InteractiveConstGen`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `GraphPaneHandler`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Creates an interactive constant on a chart pane (a horizontal line).  Inputs/Output: Inputs=TemplateLibrary.Pane(GRAPHPANE); Output=DOUBLE

### Inputs
- [0] `TemplateLibrary.Pane` accepts `GRAPHPANE` (required: `True`, stream-only: `True`)

### Parameters
- `Color` (`String`), default=`#ff0000`, shown=`False`, optimizable=`False`, editor=`StringToColorTemplate`, help="Color in hexadecimal RGB format (i.e. #ff0000 - red, #00ff00 - green, #0000ff - blue)"
- `IsNeedRecalculate` (`bool`), title="Recalculate agent?", default=`true`, shown=`False`, optimizable=`False`, help="Recalculate agent when line changes its parameters"
- `PaneSide` (`PaneSides`), title="Pane side", default=`RIGHT`, shown=`False`, optimizable=`False`, help="Pane side (vertical axis)"
- `Thickness` (`Double`), default=`1`, range=`1`..`10` step `1`, shown=`True`, optimizable=`True`, help="Thickness of a line"
- `Value` (`OptimProperty`), default=`100`, shown=`False`, optimizable=`True`, help="Value of a constant"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "InteractiveConstGen1", "typeName": "InteractiveConstGen", "blockType": "ConverterItem"
    }
  ]
}
```

## InteractiveLineGen

- Display name: Interactive line
- typeName: `InteractiveLineGen`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `GraphPaneHandler`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Creates an interactive line on a chart pane.  Inputs/Output: Inputs=TemplateLibrary.Pane(GRAPHPANE), SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `TemplateLibrary.Pane` accepts `GRAPHPANE` (required: `True`, stream-only: `True`)
- [1] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Color` (`String`), default=`#ff0000`, shown=`False`, optimizable=`False`, editor=`StringToColorTemplate`, help="Color in hexadecimal RGB format (i.e. #ff0000 - red, #00ff00 - green, #0000ff - blue)"
- `FirstDateTime` (`DateTimeOptimProperty`), title="First date", default=`0001-01-01T00:00:00.0000000`, shown=`False`, optimizable=`True`, help="Date of a first point"
- `FirstValue` (`OptimProperty`), title="First value", default=`0`, shown=`False`, optimizable=`True`, help="Y value of a first point"
- `IsNeedRecalculate` (`bool`), title="Recalculate agent?", default=`true`, shown=`False`, optimizable=`False`, help="Recalculate agent when line changes its parameters"
- `Mode` (`InteractiveLineMode`), title="Line type", default=`Infinite`, shown=`False`, optimizable=`False`, help="Line type (finit, infinit, ray)"
- `PaneSide` (`PaneSides`), title="Pane side", default=`RIGHT`, shown=`False`, optimizable=`False`, help="Pane side (vertical axis)"
- `SecondDateTime` (`DateTimeOptimProperty`), title="Second date", default=`9999-12-31T23:59:59.9999999`, shown=`False`, optimizable=`True`, help="Date of a second point"
- `SecondValue` (`OptimProperty`), title="Second value", default=`0`, shown=`False`, optimizable=`True`, help="Y value of a second point"
- `Thickness` (`Double`), default=`1`, range=`1`..`10` step `1`, shown=`True`, optimizable=`True`, help="Thickness of a line"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "InteractiveLineGen1", "typeName": "InteractiveLineGen", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

