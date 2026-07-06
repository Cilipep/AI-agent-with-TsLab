# Handlers Reference: Uncategorized

For each handler below:
- `typeName` is the string you pass to `/api/handlers/{typeName}` and `AddBlock` (`typeName` field).
- `blockType` is the container you must use for handler-based blocks (not template blocks).
- Input indices are zero-based (`toPort`).
- Hidden handlers (`[HandlerInvisible]`) require `allowHiddenHandler=true` in `AddBlock` (advanced). Some legacy helpers (e.g. `CycleHandler`) may be auto-converted to template blocks.

## AddPositionHandler

- Display name: Add position in cycle
- typeName: `AddPositionHandler`
- Namespace: `TSLab.ScriptEngine.Template`
- Assembly: `TSLab.Script.Handlers`
- Visibility: hidden (`[HandlerInvisible]`) - avoid using in new scripts unless you know what you are doing.
- AddBlock requires: `allowHiddenHandler=true` (advanced).
- Category: `Uncategorized`
- Output: `UNKNOWN` (outputs: `0`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
A pass on the bar is performed for all iteration cycles. During the passage, the positions that need to be opened are calculated. As many positions is added, as many iterations returned the result true.

### Inputs
- [0] `Input0` accepts `UNKNOWN` (required: `True`, stream-only: `True`)

### Parameters
- `UseVirtualClosing` (`bool`), title="Use "Virtual Closing"", default=`false`, shown=`True`, optimizable=`False`, help="This parameter is necessary for cases when the position closing signal is missed, so that there are no new gaps. It says that the position signal was issued by the script, but the real application has not yet passed. For example, auto-closing is expected. If the option is enabled, the Cycle will move to the next free iteration, if it is disabled, there will be no new position openings."

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "AddPositionHandler1", "typeName": "AddPositionHandler", "blockType": "ConverterItem", "allowHiddenHandler": true
    }
  ]
}
```

## BuyCount

- Display name: Number of purchase requests
- typeName: `BuyCount`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Uncategorized`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The total current number of purchase orders in the order queue. In quotes, it corresponds to the "Orders to buy" field. Not cached.

### Inputs
- [0] `Input0` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BuyCount1", "typeName": "BuyCount", "blockType": "ConverterItem"
    }
  ]
}
```

## CycleAndHandler

- Display name: Cycle End
- typeName: `CycleAndHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Visibility: hidden (`[HandlerInvisible]`) - avoid using in new scripts unless you know what you are doing.
- AddBlock requires: `allowHiddenHandler=true` (advanced).
- Category: `Uncategorized`
- Output: `BOOL` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
If the Boolean values take the value true on all iterations, then, at the output of the block, the value true is returned on the bar (on recalculation). If one of the Logical Values takes the value false, the value false is returned at the output of the block.

### Inputs
- [0] `Input0` accepts `BOOL` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "CycleAndHandler1", "typeName": "CycleAndHandler", "blockType": "ConverterItem", "allowHiddenHandler": true
    }
  ]
}
```

## CycleBoolResultHandler

- Display name: Cycle logic result
- typeName: `CycleBoolResultHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Visibility: hidden (`[HandlerInvisible]`) - avoid using in new scripts unless you know what you are doing.
- AddBlock requires: `allowHiddenHandler=true` (advanced).
- Prefer template block: `CycleBoolResultItem` (Category `Cycle`). Do not add `CycleBoolResultHandler` directly in new scripts.
- Category: `Uncategorized`
- Output: `BOOL` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Outputs a logical value from the loop to the bar by the iteration number.

### Inputs
- [0] `Input0` accepts `UNKNOWN` (required: `True`, stream-only: `False`)

### Parameters
- `Index` (`int`), default=`0`, range=`0`..`2147483647` step `1`, shown=`True`, optimizable=`True`, help="a logical result based on the iteration number of the cycle"
- `UseLastIndex` (`bool`), title="Use last index", default=`true`, shown=`True`, optimizable=`True`, help="always use the last iteration number of the cycle"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "CycleBoolResultHandler1", "typeName": "CycleBoolResultHandler", "blockType": "ConverterItem", "allowHiddenHandler": true
    }
  ]
}
```

## CycleBoolResultsHandler

- Display name: Cycle logic results
- typeName: `CycleBoolResultsHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Visibility: hidden (`[HandlerInvisible]`) - avoid using in new scripts unless you know what you are doing.
- AddBlock requires: `allowHiddenHandler=true` (advanced).
- Prefer template block: `CycleBoolResultsItem` (Category `Cycle`). Do not add `CycleBoolResultsHandler` directly in new scripts.
- Category: `Uncategorized`
- Output: `BOOL, LIST_OF_LISTS` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Can be displayed on the chart. The chart will display all the iterations of the cycle. The block results can be passed to another Cycle, with the same number of iterations supported. Nested cycles are not supported.

### Inputs
- [0] `Input0` accepts `BOOL` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "CycleBoolResultsHandler1", "typeName": "CycleBoolResultsHandler", "blockType": "ConverterItem", "allowHiddenHandler": true
    }
  ]
}
```

## CycleDoubleResultHandler

- Display name: Cycle result
- typeName: `CycleDoubleResultHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Visibility: hidden (`[HandlerInvisible]`) - avoid using in new scripts unless you know what you are doing.
- AddBlock requires: `allowHiddenHandler=true` (advanced).
- Prefer template block: `CycleDoubleResultItem` (Category `Cycle`). Do not add `CycleDoubleResultHandler` directly in new scripts.
- Category: `Uncategorized`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Returns the value by the iteration number, and outputs the value to the bar.

### Inputs
- [0] `Input0` accepts `UNKNOWN` (required: `True`, stream-only: `False`)

### Parameters
- `Index` (`int`), default=`0`, range=`0`..`2147483647` step `1`, shown=`True`, optimizable=`True`, help="indicates from which iteration it is necessary to copy the real value to output it to the bar."
- `UseLastIndex` (`bool`), title="Use latest index", default=`true`, shown=`True`, optimizable=`True`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "CycleDoubleResultHandler1", "typeName": "CycleDoubleResultHandler", "blockType": "ConverterItem", "allowHiddenHandler": true
    }
  ]
}
```

## CycleDoubleResultsHandler

- Display name: Cycle results
- typeName: `CycleDoubleResultsHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Visibility: hidden (`[HandlerInvisible]`) - avoid using in new scripts unless you know what you are doing.
- AddBlock requires: `allowHiddenHandler=true` (advanced).
- Prefer template block: `CycleDoubleResultsItem` (Category `Cycle`). Do not add `CycleDoubleResultsHandler` directly in new scripts.
- Category: `Uncategorized`
- Output: `DOUBLE, LIST_OF_LISTS` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Can be displayed on a chart. It can be passed to another cycle, with the same number of iterations supported. Nested cycles are not supported. A service connector for displaying the parameter to the control panel.

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "CycleDoubleResultsHandler1", "typeName": "CycleDoubleResultsHandler", "blockType": "ConverterItem", "allowHiddenHandler": true
    }
  ]
}
```

## CycleHandler

- Display name: Cycle
- typeName: `CycleHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Visibility: hidden (`[HandlerInvisible]`) - avoid using in new scripts unless you know what you are doing.
- AddBlock requires: `allowHiddenHandler=true` (advanced).
- Prefer template block: `CycleItem` (Category `Cycle`). Do not add `CycleHandler` directly in new scripts.
- Web API: without `allowHiddenHandler=true`, `AddBlock` may auto-convert to `CycleItem`.
- Category: `Uncategorized`
- Output: `INT` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
At the top of the Cycle block there is a service connector for communication with the blocks of opening positions or updated values (simple and updatable cycle value). Thus, the entry into the cycle is indicated (the beginning of the calculation of the cycle). If this connector is not connected to anything, then the first formula (or logical formula) for which the output from the Cycle block is submitted and in which there is an appeal to the Cycle block by its name is considered to be the beginning of the calculation of the cycle.[br]All the blocks that are connected between the beginning of the cycle and the end of the cycle participate in the calculation of the results of the cycle. All the blocks that are connected between the beginning of the cycle and the end of the cycle participate in the calculation of the results of the cycle and they can't be tied to another cycle.

### Inputs
- [0] `Input0` accepts `UNKNOWN` (required: `True`, stream-only: `False`)

### Parameters
- `MaxCount` (`int`), title="Maximum number", default=`1`, range=`1`..`2147483647` step `1`, shown=`True`, optimizable=`True`, help="specifies the maximum number of iterations."

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "CycleHandler1", "typeName": "CycleHandler", "blockType": "ConverterItem", "allowHiddenHandler": true
    }
  ]
}
```

## CycleOrHandler

- Display name: Cycle Or
- typeName: `CycleOrHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Visibility: hidden (`[HandlerInvisible]`) - avoid using in new scripts unless you know what you are doing.
- AddBlock requires: `allowHiddenHandler=true` (advanced).
- Category: `Uncategorized`
- Output: `BOOL` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
If in one of the iterations the logical value takes the value true, then the block output returns the value true on the bar (on recalculation), otherwise the value false is returned. At the input, the results of the logical values of the cycle work, for example, a logical formula.

### Inputs
- [0] `Input0` accepts `BOOL` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "CycleOrHandler1", "typeName": "CycleOrHandler", "blockType": "ConverterItem", "allowHiddenHandler": true
    }
  ]
}
```

## CycleValueUpdaterHandler

- Display name: Cycle updatable value
- typeName: `CycleValueUpdaterHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Visibility: hidden (`[HandlerInvisible]`) - avoid using in new scripts unless you know what you are doing.
- AddBlock requires: `allowHiddenHandler=true` (advanced).
- Prefer template block: `CycleValueUpdaterItem` (Category `CycleValueUpdater`). Do not add `CycleValueUpdaterHandler` directly in new scripts.
- Web API: without `allowHiddenHandler=true`, `AddBlock` may auto-convert to `CycleValueUpdaterItem`.
- Category: `Uncategorized`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The usual updated value in the cycle moves from the old iteration to the value of the new iteration. The updated cycle value works with an array of iteration values. The output is a list of real values. For each iteration of the cycle, its own separate, independently updated value is maintained.

### Inputs
- [0] `Input0` accepts `UNKNOWN` (required: `True`, stream-only: `False`)

### Parameters
- `ExecutionOrder` (`ValueUpdaterExecutionOrder`), title="Execution order", default=`AtTheEnd`, shown=`False`, optimizable=`False`, help="Determines the queue for calculating the Updated value in the algorithm, in the general order (by default), at the end of the algorithm (in the queue of this calculation branch) or after leaving the position."
- `StartFrom` (`Double`), title="Initial", default=`0`, shown=`False`, optimizable=`False`, help="The initial value of the block."

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "CycleValueUpdaterHandler1", "typeName": "CycleValueUpdaterHandler", "blockType": "ConverterItem", "allowHiddenHandler": true
    }
  ]
}
```

## EmptyDoubleHandler

- Display name: EmptyDoubleHandler
- typeName: `EmptyDoubleHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Visibility: hidden (`[HandlerInvisible]`) - avoid using in new scripts unless you know what you are doing.
- AddBlock requires: `allowHiddenHandler=true` (advanced).
- Category: `Uncategorized`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No English description is available in handler metadata; treat the name and IO contract as authoritative.

### Inputs
- [0] `Input0` accepts `UNKNOWN` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "EmptyDoubleHandler1", "typeName": "EmptyDoubleHandler", "blockType": "ConverterItem", "allowHiddenHandler": true
    }
  ]
}
```

## OptionsBoardHandler

- Display name: OptionsBoardHandler
- typeName: `OptionsBoardHandler`
- Namespace: `TSLab.ScriptEngine.Handlers`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `Uncategorized`
- Output: `UNKNOWN` (outputs: `0`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No English description is available in handler metadata; treat the name and IO contract as authoritative.

### Inputs
- [0] `Input0` accepts `UNKNOWN` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "OptionsBoardHandler1", "typeName": "OptionsBoardHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## OptionsBoardNumericalTheta

- Display name: OptionsBoardNumericalTheta
- typeName: `OptionsBoardNumericalTheta`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Visibility: hidden (`[HandlerInvisible]`) - avoid using in new scripts unless you know what you are doing.
- AddBlock requires: `allowHiddenHandler=true` (advanced).
- Category: `Uncategorized`
- Output: `UNKNOWN` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Estimate theta as function of strikes with numerical differentiation

### Inputs
- [0] `Input0` accepts `UNKNOWN` (required: `True`, stream-only: `False`)

### Parameters
- `FixedQty` (`int`), default=`100`, shown=`True`, optimizable=`False`
- `GreekAlgo` (`NumericalGreekAlgo`), default=`FrozenSmile`, shown=`True`, optimizable=`True`
- `OptionType` (`StrikeType`), default=`Call`, shown=`True`, optimizable=`False`
- `ShowNodes` (`bool`), default=`false`, shown=`True`, optimizable=`True`
- `SigmaMult` (`Double`), default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`
- `TooltipFormat` (`String`), default=`0.00`, shown=`True`, optimizable=`False`
- `TStep` (`Double`), default=`0.00001`, range=`0`..`1000000` step `0.00001`, shown=`True`, optimizable=`True`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "OptionsBoardNumericalTheta1", "typeName": "OptionsBoardNumericalTheta", "blockType": "ConverterItem", "allowHiddenHandler": true
    }
  ]
}
```

## OptionsBoardNumericalVega

- Display name: OptionsBoardNumericalVega
- typeName: `OptionsBoardNumericalVega`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Visibility: hidden (`[HandlerInvisible]`) - avoid using in new scripts unless you know what you are doing.
- AddBlock requires: `allowHiddenHandler=true` (advanced).
- Category: `Uncategorized`
- Output: `UNKNOWN` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Estimate theta as function of strikes with numerical differentiation

### Inputs
- [0] `Input0` accepts `UNKNOWN` (required: `True`, stream-only: `False`)

### Parameters
- `FixedQty` (`int`), default=`100`, shown=`True`, optimizable=`False`
- `GreekAlgo` (`NumericalGreekAlgo`), default=`ShiftingSmile`, shown=`True`, optimizable=`True`
- `OptionType` (`StrikeType`), default=`Call`, shown=`True`, optimizable=`False`
- `ShowNodes` (`bool`), default=`false`, shown=`True`, optimizable=`True`
- `SigmaMult` (`Double`), default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`
- `SigmaStep` (`Double`), default=`0.0001`, range=`0`..`1000000` step `0.0001`, shown=`True`, optimizable=`True`
- `TooltipFormat` (`String`), default=`0.00`, shown=`True`, optimizable=`False`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "OptionsBoardNumericalVega1", "typeName": "OptionsBoardNumericalVega", "blockType": "ConverterItem", "allowHiddenHandler": true
    }
  ]
}
```

## OptionsBoardPrice

- Display name: OptionsBoardPrice
- typeName: `OptionsBoardPrice`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Visibility: hidden (`[HandlerInvisible]`) - avoid using in new scripts unless you know what you are doing.
- AddBlock requires: `allowHiddenHandler=true` (advanced).
- Category: `Uncategorized`
- Output: `UNKNOWN` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Option price as function of strikes

### Inputs
- [0] `Input0` accepts `UNKNOWN` (required: `True`, stream-only: `False`)

### Parameters
- `FixedQty` (`int`), default=`1`, shown=`True`, optimizable=`False`
- `OptionType` (`StrikeType`), default=`Call`, shown=`True`, optimizable=`False`
- `ShowNodes` (`bool`), default=`false`, shown=`True`, optimizable=`True`
- `SigmaMult` (`Double`), default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`
- `TooltipFormat` (`String`), default=`0.00`, shown=`True`, optimizable=`False`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "OptionsBoardPrice1", "typeName": "OptionsBoardPrice", "blockType": "ConverterItem", "allowHiddenHandler": true
    }
  ]
}
```

## OptionsBoardVolatility

- Display name: OptionsBoardVolatility
- typeName: `OptionsBoardVolatility`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Visibility: hidden (`[HandlerInvisible]`) - avoid using in new scripts unless you know what you are doing.
- AddBlock requires: `allowHiddenHandler=true` (advanced).
- Category: `Uncategorized`
- Output: `UNKNOWN` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Option volatility as function of strikes

### Inputs
- [0] `Input0` accepts `UNKNOWN` (required: `True`, stream-only: `False`)

### Parameters
- `OptionType` (`StrikeType`), default=`Call`, shown=`True`, optimizable=`False`
- `ShowNodes` (`bool`), default=`false`, shown=`True`, optimizable=`True`
- `SigmaMult` (`Double`), default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`
- `TooltipFormat` (`String`), default=`0.0`, shown=`True`, optimizable=`False`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "OptionsBoardVolatility1", "typeName": "OptionsBoardVolatility", "blockType": "ConverterItem", "allowHiddenHandler": true
    }
  ]
}
```

## SellCount

- Display name: Number of requests for sale
- typeName: `SellCount`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `Uncategorized`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The total current number of sell orders in the order queue. In quotes, it corresponds to the "Orders to sell" field. Not cached

### Inputs
- [0] `Input0` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SellCount1", "typeName": "SellCount", "blockType": "ConverterItem"
    }
  ]
}
```

