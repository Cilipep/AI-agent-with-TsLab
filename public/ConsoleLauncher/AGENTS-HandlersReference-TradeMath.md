# Handlers Reference: TradeMath

For each handler below:
- `typeName` is the string you pass to `/api/handlers/{typeName}` and `AddBlock` (`typeName` field).
- `blockType` is the container you must use for handler-based blocks (not template blocks).
- Input indices are zero-based (`toPort`).
- Hidden handlers (`[HandlerInvisible]`) require `allowHiddenHandler=true` in `AddBlock` (advanced). Some legacy helpers (e.g. `CycleHandler`) may be auto-converted to template blocks.

## AbsolutCommission

- Display name: Absolute comission
- typeName: `AbsolutCommission`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `UNKNOWN` (outputs: `0`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Absolute commission for one trade (long or short)  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=UNKNOWN

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Commission` (`Double`), title="Comission", default=`0.0002`, range=`0.0002`..`0.01` step `0.0002`, shown=`True`, optimizable=`True`, help="Absolute comission per 1 lot of a security"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "AbsolutCommission1", "typeName": "AbsolutCommission", "blockType": "ConverterItem"
    }
  ]
}
```

## Add

- Display name: Sum up
- typeName: `Add`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `2`, max `10`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Sum a few input values (from 2 to 6 inputs)  Inputs/Output: Output=DOUBLE

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Input1` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [2] `Input2` accepts `DOUBLE` (required: `False`, stream-only: `False`)
- [3] `Input3` accepts `DOUBLE` (required: `False`, stream-only: `False`)
- [4] `Input4` accepts `DOUBLE` (required: `False`, stream-only: `False`)
- [5] `Input5` accepts `DOUBLE` (required: `False`, stream-only: `False`)
- [6] `Input6` accepts `DOUBLE` (required: `False`, stream-only: `False`)
- [7] `Input7` accepts `DOUBLE` (required: `False`, stream-only: `False`)
- [8] `Input8` accepts `DOUBLE` (required: `False`, stream-only: `False`)
- [9] `Input9` accepts `DOUBLE` (required: `False`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Add1", "typeName": "Add", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## And

- Display name: And
- typeName: `And`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `BOOL` (outputs: `1`, only-value-output: `False`)
- Inputs: min `2`, max `30`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Logical conjunction of a few input values (from 2 to 30 inputs). Output is TRUE only if all inputs are TRUE at the same time.

### Inputs
- [0] `Input0` accepts `BOOL` (required: `True`, stream-only: `False`)
- [1] `Input1` accepts `BOOL` (required: `True`, stream-only: `False`)
- [2] `Input2` accepts `BOOL` (required: `False`, stream-only: `False`)
- [3] `Input3` accepts `BOOL` (required: `False`, stream-only: `False`)
- [4] `Input4` accepts `BOOL` (required: `False`, stream-only: `False`)
- [5] `Input5` accepts `BOOL` (required: `False`, stream-only: `False`)
- [6] `Input6` accepts `BOOL` (required: `False`, stream-only: `False`)
- [7] `Input7` accepts `BOOL` (required: `False`, stream-only: `False`)
- [8] `Input8` accepts `BOOL` (required: `False`, stream-only: `False`)
- [9] `Input9` accepts `BOOL` (required: `False`, stream-only: `False`)
- [10] `Input10` accepts `BOOL` (required: `False`, stream-only: `False`)
- [11] `Input11` accepts `BOOL` (required: `False`, stream-only: `False`)
- [12] `Input12` accepts `BOOL` (required: `False`, stream-only: `False`)
- [13] `Input13` accepts `BOOL` (required: `False`, stream-only: `False`)
- [14] `Input14` accepts `BOOL` (required: `False`, stream-only: `False`)
- [15] `Input15` accepts `BOOL` (required: `False`, stream-only: `False`)
- [16] `Input16` accepts `BOOL` (required: `False`, stream-only: `False`)
- [17] `Input17` accepts `BOOL` (required: `False`, stream-only: `False`)
- [18] `Input18` accepts `BOOL` (required: `False`, stream-only: `False`)
- [19] `Input19` accepts `BOOL` (required: `False`, stream-only: `False`)
- [20] `Input20` accepts `BOOL` (required: `False`, stream-only: `False`)
- [21] `Input21` accepts `BOOL` (required: `False`, stream-only: `False`)
- [22] `Input22` accepts `BOOL` (required: `False`, stream-only: `False`)
- [23] `Input23` accepts `BOOL` (required: `False`, stream-only: `False`)
- [24] `Input24` accepts `BOOL` (required: `False`, stream-only: `False`)
- [25] `Input25` accepts `BOOL` (required: `False`, stream-only: `False`)
- [26] `Input26` accepts `BOOL` (required: `False`, stream-only: `False`)
- [27] `Input27` accepts `BOOL` (required: `False`, stream-only: `False`)
- [28] `Input28` accepts `BOOL` (required: `False`, stream-only: `False`)
- [29] `Input29` accepts `BOOL` (required: `False`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "And1", "typeName": "And", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## Ask

- Display name: Ask
- typeName: `Ask`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Best sell price recorded at the end of every bar (if available).  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Ask1", "typeName": "Ask", "blockType": "ConverterItem"
    }
  ]
}
```

## AskQty

- Display name: Total offer
- typeName: `AskQty`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Number of securities in all orders for sale (in lots). [br]  The data for the block is taken from "Quotes". If the broker or exchange does not transmit data, then for the block to work, you need to open the "Depth of Market" window and select the required instrument in it.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "AskQty1", "typeName": "AskQty", "blockType": "ConverterItem"
    }
  ]
}
```

## BarNumber

- Display name: Bar number
- typeName: `BarNumber`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
An index of an element in a list of bars or numeric values.  Inputs/Output: Inputs=Input0(SECURITY, DOUBLE, INT, BOOL); Output=DOUBLE

### Inputs
- [0] `Input0` accepts `SECURITY, DOUBLE, INT, BOOL` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BarNumber1", "typeName": "BarNumber", "blockType": "ConverterItem"
    }
  ]
}
```

## BarsConstructorHandler

- Display name: Bars Constructor
- typeName: `BarsConstructorHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `SECURITY` (outputs: `1`, only-value-output: `False`)
- Inputs: min `5`, max `5`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Handler converts 5 input numeric series to a synthetic security with bars. Inputs are: open, close, high, low, volume.

### Inputs
- [0] `Open` accepts `DOUBLE` (required: `True`, stream-only: `True`)
- [1] `Close` accepts `DOUBLE` (required: `True`, stream-only: `True`)
- [2] `High` accepts `DOUBLE` (required: `True`, stream-only: `True`)
- [3] `Low` accepts `DOUBLE` (required: `True`, stream-only: `True`)
- [4] `Volume` accepts `DOUBLE` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BarsConstructorHandler1", "typeName": "BarsConstructorHandler", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## BarsTickDataHandler

- Display name: Bars tick data
- typeName: `BarsTickDataHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `SECURITY` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Designed to work with cached data from quotes. Builds bars with the source interval. To work, use the second interval of the source. For example, 60 seconds.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Field` (`BarsTickDataField`), title="Data quotes", default=`BuyCount`, shown=`True`, optimizable=`True`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BarsTickDataHandler1", "typeName": "BarsTickDataHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## Bid

- Display name: Bid
- typeName: `Bid`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Best buy price recorded at the end of every bar (if available).  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Bid1", "typeName": "Bid", "blockType": "ConverterItem"
    }
  ]
}
```

## BidQty

- Display name: Total demand
- typeName: `BidQty`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Number of securities in all purchase orders (in lots). [br]  The data for the block is taken from "Quotes". If the broker or exchange does not transmit data, then for the block to work, you need to open the "Depth of Market" window and select the required instrument in it.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BidQty1", "typeName": "BidQty", "blockType": "ConverterItem"
    }
  ]
}
```

## BoolBreaker

- Display name: Boolean Breaker
- typeName: `BoolBreaker`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `BOOL` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Sets a FALSE value at every candle except the last one. For the last value sets a selected TRUE/FALSE value. This block is used together with the control pane buttons.

### Inputs
- [0] `Input0` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Value` (`bool`), shown=`True`, optimizable=`True`, help="A value to return as output of a handler"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BoolBreaker1", "typeName": "BoolBreaker", "blockType": "ConverterItem"
    }
  ]
}
```

## BoolConst

- Display name: Boolean Constant
- typeName: `BoolConst`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `BOOL` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
This block sets a fixed boolean value for every bar.  Inputs/Output: Output=UNKNOWN

### Inputs
- [0] `Input0` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Value` (`bool`), shown=`True`, optimizable=`True`, help="A value to return as output of a handler"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BoolConst1", "typeName": "BoolConst", "blockType": "ConverterItem"
    }
  ]
}
```

## BuyDeposit

- Display name: Buy Deposit
- typeName: `BuyDeposit`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No English description is available in handler metadata; treat the name and IO contract as authoritative.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BuyDeposit1", "typeName": "BuyDeposit", "blockType": "ConverterItem"
    }
  ]
}
```

## Close

- Display name: Close
- typeName: `Close`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Closing price of the bar.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Close1", "typeName": "Close", "blockType": "ConverterItem"
    }
  ]
}
```

## Compress

- Display name: Compress
- typeName: `Compress`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `SECURITY` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Compresses current bars time range (minutes into minutes, days into days) into a longer one. Only divisible ranges can be used. For example, 15 minutes can be compressed into 15, 30, 45, 60 minutes and so on.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Interval` (`int`), default=`5`, range=`5`..`60` step `5`, shown=`True`, optimizable=`True`, help="Absolute target interval in the same interval base as the source security. It defines the destination interval directly and must be compatible with the source interval."
- `Shift` (`int`), default=`0`, range=`0`..`60` step `5`, shown=`True`, optimizable=`True`, help="Time shift of the compression window."

### Agent Authoring Notes
- In multi-timeframe strategies, keep the script/base timeframe unchanged and create the higher-timeframe branch with `Compress`.
- `Interval` is the absolute target timeframe in the same base, not a multiplier. It defines the destination interval directly.
- Valid targets must stay compatible with and divisible by the base or source interval.
- `Shift` shifts the compression window. Keep `0` unless the task explicitly requires offset bar boundaries.
- If the compressed branch feeds logic back into the base path, ensure there is an effective return into that base path. An explicit `Decompress` / `DecompressBool` block on the same branch is one common proof when the host requires it.

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Compress1", "typeName": "Compress", "blockType": "ConverterItem"
    }
  ]
}
```

## CompressAdvanced

- Display name: Compress (Advanced)
- typeName: `CompressAdvanced`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `SECURITY` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Compresses a current bars time range (minutes into minutes, days into days) of bars into a longer one. Only divisible ranges can be used. For example, 15 minutes can be compressed into 15, 30, 45, 60 minutes and so on.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `AdjShift` (`int`), default=`600`, range=`0`..`1440` step `60`, shown=`True`, optimizable=`True`, help="Shift of the time-alignment anchor used by Adjustment."
- `Adjustment` (`int`), default=`1440`, range=`60`..`10080` step `60`, shown=`True`, optimizable=`True`, help="Time adjustment or alignment period for compressed bar boundaries."
- `Interval` (`int`), default=`5`, range=`5`..`60` step `5`, shown=`True`, optimizable=`True`, help="Absolute target interval in the selected 'Interval base'. It defines the destination interval directly."
- `IntervalBase` (`DataIntervals`), title="Interval base", default=`MINUTE`, shown=`True`, optimizable=`False`, help="Target timeframe base (DAYS, MINUTE, SECONDS, TICK, VOLUME, PRICERANGE)."
- `Shift` (`int`), default=`0`, range=`0`..`60` step `5`, shown=`True`, optimizable=`True`, help="Time shift of the compression window."

### Agent Authoring Notes
- Prefer `CompressAdvanced` when the compressed branch must stay editable or optimizable while the script itself remains on a fixed base timeframe.
- `IntervalBase` selects the target interval base (`MINUTE`, `DAYS`, `SECONDS`, `TICK`, `VOLUME`, `PRICERANGE`).
- `Interval` is the absolute target timeframe in the chosen base, not a multiplier. It defines the destination interval directly.
- `Shift` shifts compression-window boundaries.
- `Adjustment` controls alignment or anchoring of compressed bar boundaries.
- `AdjShift` shifts that alignment anchor.
- `Shift`, `Adjustment`, and `AdjShift` control boundary placement and alignment; they do not change the requested target interval itself.
- Unless the task explicitly requires non-default alignment, keep `Shift=0` and keep `Adjustment` / `AdjShift` at defaults.
- If several compressed branches must share one higher-timeframe parameter, use `ParameterShareItem` or `OneToManyParametersShareItem` to keep them aligned.
- If compressed-branch outputs are reused on the base trade path, ensure they return effectively into that base path. An explicit `Decompress` / `DecompressBool` block linked to the same compression block is one common proof when the host requires it.

### Parameterized AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock",
      "blockId": "HTF30",
      "typeName": "CompressAdvanced",
      "blockType": "ConverterItem",
      "params": {
        "IntervalBase": "MINUTE",
        "Interval": 30,
        "Shift": 0
      }
    },
    {
      "op": "ConnectByInputName",
      "fromBlockId": "Src",
      "toBlockId": "HTF30",
      "toInputName": "SECURITYSource"
    }
  ]
}
```

## CompressToSeconds

- Display name: Compress into seconds
- typeName: `CompressToSeconds`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `SECURITY` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Compresses current time range of bars into a longer one. Only divisible ranges can be used. For example, 1 minute can be compressed into 60, 120, 180, 240 seconds and so on.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Interval` (`int`), default=`5`, range=`5`..`60` step `5`, shown=`True`, optimizable=`True`, help="Target interval in seconds. I.e. Interval=16 results in timeframe S16. The source must be compatible with a target timeframe."

### Agent Authoring Notes
- Use `CompressToSeconds` when the target base is explicitly seconds and the source is compatible with seconds compression.
- `Interval` is the absolute target interval in seconds, not a multiplier.
- If the compressed seconds branch feeds logic back into the base path, ensure there is an effective return into that base path. An explicit `Decompress` / `DecompressBool` block on that same branch is one common proof when the host requires it.

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "CompressToSeconds1", "typeName": "CompressToSeconds", "blockType": "ConverterItem"
    }
  ]
}
```

## ConstGen

- Display name: Constant
- typeName: `ConstGen`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
A constant value.  Inputs/Output: Output=UNKNOWN

### Inputs
- [0] `Input0` accepts `SECURITY, DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Value` (`Double`), shown=`True`, optimizable=`True`, help="A value to return as output of a handler"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "ConstGen1", "typeName": "ConstGen", "blockType": "ConverterItem"
    }
  ]
}
```

## ControlledBoolBreaker

- Display name: Controlled Boolean Breaker
- typeName: `ControlledBoolBreaker`
- Namespace: `TSLab.Script.Handlers.TradeMath`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `BOOL` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Sets a FALSE value at every candle except the last one. For the last value sets a selected TRUE/FALSE value. This block is used together with the control pane buttons. When signaled, the Value parameter reset automatically.

### Inputs
- [0] `Input0` accepts `BOOL` (required: `True`, stream-only: `False`)

### Parameters
- `Value` (`BoolOptimProperty`), shown=`True`, optimizable=`True`, help="Set true for waiting a signal. Reset automatically when signaled."

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "ControlledBoolBreaker1", "typeName": "ControlledBoolBreaker", "blockType": "ConverterItem"
    }
  ]
}
```

## ControlledBoolConst

- Display name: Controlled Boolean Constant
- typeName: `ControlledBoolConst`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `BOOL` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Controlled boolean constant (switch). If input is TRUE the result is taken from a field 'Value', otherwise the result is taken from a field 'Default value'.

### Inputs
- [0] `Input0` accepts `BOOL` (required: `True`, stream-only: `False`)

### Parameters
- `DefaultValue` (`bool`), title="Default value", shown=`True`, optimizable=`False`, help="A value to return as output of a handler when input is false"
- `Value` (`bool`), shown=`True`, optimizable=`True`, help="A value to return as output of a handler when input is true"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "ControlledBoolConst1", "typeName": "ControlledBoolConst", "blockType": "ConverterItem"
    }
  ]
}
```

## CrossOver

- Display name: Cross over
- typeName: `CrossOver`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `BOOL` (outputs: `1`, only-value-output: `False`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Handler returns true, if second input (signal) crosses down a reference line (first input).  Inputs/Output: Inputs=Input0(DOUBLE), Input1(DOUBLE); Output=BOOL

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Input1` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "CrossOver1", "typeName": "CrossOver", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## CrossUnder

- Display name: Cross under
- typeName: `CrossUnder`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `BOOL` (outputs: `1`, only-value-output: `False`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Handler returns true, if second input (signal) crosses up a reference line (first input).  Inputs/Output: Inputs=Input0(DOUBLE), Input1(DOUBLE); Output=BOOL

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Input1` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "CrossUnder1", "typeName": "CrossUnder", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## Cutter

- Display name: Cut off
- typeName: `Cutter`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `SECURITY` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Cuts High and Low up to a selected value.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=SECURITY

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Decimals` (`int`), default=`2`, shown=`True`, optimizable=`False`, help="Decimals for ceiling"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Cutter1", "typeName": "Cutter", "blockType": "ConverterItem"
    }
  ]
}
```

## Date

- Display name: Date
- typeName: `Date`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Date of every bar is converted to number as yymmdd. I.e. date 12.31.2018 converts to a number 181231.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Date1", "typeName": "Date", "blockType": "ConverterItem"
    }
  ]
}
```

## DayOfMonth

- Display name: Day of month
- typeName: `DayOfMonth`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Handler accepts an instrument at the entry and returns a month day as number from 1 31.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "DayOfMonth1", "typeName": "DayOfMonth", "blockType": "ConverterItem"
    }
  ]
}
```

## DayOfWeek

- Display name: Day of week
- typeName: `DayOfWeek`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Handler accepts an instrument at the entry and returns a week day as number from 1 (Monday) to 7 (Sunday).

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "DayOfWeek1", "typeName": "DayOfWeek", "blockType": "ConverterItem"
    }
  ]
}
```

## Decompres

- Display name: Decompress
- typeName: `Decompres`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Decompresses calculated numeric data to be used further with other data in authentic range. The Decompress block should be connected to a block being compressed and to the Compress block linked to a block being decompressed. [br]TSLab has three decompression methods. [br]Attention! The 2nd method cannot be applied to offline data testing, as it results in looking into the future and, as a result, corrupts results significantly.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)
- [1] `Input1` accepts `DOUBLE` (required: `True`, stream-only: `True`)

### Parameters
- `Method` (`DecompressMethodWithDef`), title="Decompress algorythm", default=`Default`, shown=`True`, optimizable=`False`, help="Decompress algorythm"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Decompres1", "typeName": "Decompres", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## DecompresBool

- Display name: Decompress boolean
- typeName: `DecompresBool`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `BOOL` (outputs: `1`, only-value-output: `False`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Decompresses Boolean data which have been calculated in compressed range to be used further with other data in authentic range. The Decompress block should be connected to a block being decompressed and with the Compress block, linked to a block being decompressed.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)
- [1] `Input1` accepts `BOOL` (required: `True`, stream-only: `True`)

### Parameters
- `Method` (`DecompressMethodWithDef`), title="Decompress algorythm", default=`Default`, shown=`True`, optimizable=`False`, help="Decompress algorythm"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "DecompresBool1", "typeName": "DecompresBool", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## EqualHandler

- Display name: Equal
- typeName: `EqualHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `BOOL` (outputs: `1`, only-value-output: `False`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Handler returns true, if input values are equal (with respect to double values precision)  Inputs/Output: Inputs=Input0(DOUBLE), Input1(DOUBLE); Output=BOOL

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Input1` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "EqualHandler1", "typeName": "EqualHandler", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## Flip

- Display name: Flip
- typeName: `Flip`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `BOOL` (outputs: `1`, only-value-output: `False`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Imitates a trigger with 2 entries, when True appears at the first entry, an outgoing value becomes True, until True appears at the second entry. When True appears at the second entry, an indicator value becomes False, until True appears at the first entry. If True appears at two entries simultaneously, then an indicator valye is False, so it means that the first entry is ignored.

### Inputs
- [0] `Input0` accepts `BOOL` (required: `True`, stream-only: `False`)
- [1] `Input1` accepts `BOOL` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Flip1", "typeName": "Flip", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## GreaterHandler

- Display name: Greater
- typeName: `GreaterHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `BOOL` (outputs: `1`, only-value-output: `False`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Handler returns true, if the first input is strictly greater than the second input.  Inputs/Output: Inputs=Input0(DOUBLE), Input1(DOUBLE); Output=BOOL

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Input1` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "GreaterHandler1", "typeName": "GreaterHandler", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## GreaterOrEqualHandler

- Display name: Greater or equal
- typeName: `GreaterOrEqualHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `BOOL` (outputs: `1`, only-value-output: `False`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Handler returns true, if the first input is greater or equal than the second input.  Inputs/Output: Inputs=Input0(DOUBLE), Input1(DOUBLE); Output=BOOL

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Input1` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "GreaterOrEqualHandler1", "typeName": "GreaterOrEqualHandler", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## High

- Display name: High
- typeName: `High`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
A maximum price of a bar.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "High1", "typeName": "High", "blockType": "ConverterItem"
    }
  ]
}
```

## HighBid

- Display name: High bid
- typeName: `HighBid`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No English description is available in handler metadata; treat the name and IO contract as authoritative.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "HighBid1", "typeName": "HighBid", "blockType": "ConverterItem"
    }
  ]
}
```

## HighestPos

- Display name: Bars since last high
- typeName: `HighestPos`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The number of bars since the latest high.  Inputs/Output: Inputs=Input0(DOUBLE); Output=DOUBLE

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `True`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "HighestPos1", "typeName": "HighestPos", "blockType": "ConverterItem"
    }
  ]
}
```

## Hold

- Display name: Hold
- typeName: `Hold`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `BOOL` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Holds an incoming Boolean signal during N candles (the Period parameter). So, if an incoming candle value becomes True, it will be duplicated for N candles.

### Inputs
- [0] `Input0` accepts `BOOL` (required: `True`, stream-only: `False`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Hold1", "typeName": "Hold", "blockType": "ConverterItem"
    }
  ]
}
```

## LessHandler

- Display name: Less
- typeName: `LessHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `BOOL` (outputs: `1`, only-value-output: `False`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Handler returns true, if the first input is strictly less than the second input.  Inputs/Output: Inputs=Input0(DOUBLE), Input1(DOUBLE); Output=BOOL

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Input1` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "LessHandler1", "typeName": "LessHandler", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## LessOrEqualHandler

- Display name: Less or equal
- typeName: `LessOrEqualHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `BOOL` (outputs: `1`, only-value-output: `False`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Handler returns true, if the first input is less or equal than the second input.  Inputs/Output: Inputs=Input0(DOUBLE), Input1(DOUBLE); Output=BOOL

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Input1` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "LessOrEqualHandler1", "typeName": "LessOrEqualHandler", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## Ln

- Display name: Ln
- typeName: `Ln`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
A natural logarithm (Ln) for a values series.  Inputs/Output: Inputs=Input0(DOUBLE); Output=DOUBLE

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Add` (`Double`), default=`0`, shown=`True`, optimizable=`True`, help="A result of logarithm (after multiplication) may be shifted by this value ( Mult*LN(x) + Add )"
- `Mult` (`Double`), title="Multiply", default=`1`, shown=`True`, optimizable=`True`, help="A result of logarithm may be multiplied by this coefficient ( Mult*LN(x) + Add )"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Ln1", "typeName": "Ln", "blockType": "ConverterItem"
    }
  ]
}
```

## LotSize

- Display name: Lot size
- typeName: `LotSize`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Lot size of a security. The block returns the number of shares in one lot. This value is shown also in 'Quotes' table.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "LotSize1", "typeName": "LotSize", "blockType": "ConverterItem"
    }
  ]
}
```

## LotTick

- Display name: Lot step
- typeName: `LotTick`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Lot step of a security. This value is shown also in 'Quotes' table.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "LotTick1", "typeName": "LotTick", "blockType": "ConverterItem"
    }
  ]
}
```

## Low

- Display name: Low
- typeName: `Low`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
A minimum price of a bar.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Low1", "typeName": "Low", "blockType": "ConverterItem"
    }
  ]
}
```

## LowestPos

- Display name: Bars since last low
- typeName: `LowestPos`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The number of bars since the latest low.  Inputs/Output: Inputs=Input0(DOUBLE); Output=DOUBLE

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `True`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "LowestPos1", "typeName": "LowestPos", "blockType": "ConverterItem"
    }
  ]
}
```

## LowOffer

- Display name: Low offer
- typeName: `LowOffer`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No English description is available in handler metadata; treat the name and IO contract as authoritative.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "LowOffer1", "typeName": "LowOffer", "blockType": "ConverterItem"
    }
  ]
}
```

## Max

- Display name: Max
- typeName: `Max`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `2`, max `10`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Maximum of a few input values (from 2 to 6 inputs)  Inputs/Output: Output=DOUBLE

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Input1` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [2] `Input2` accepts `DOUBLE` (required: `False`, stream-only: `False`)
- [3] `Input3` accepts `DOUBLE` (required: `False`, stream-only: `False`)
- [4] `Input4` accepts `DOUBLE` (required: `False`, stream-only: `False`)
- [5] `Input5` accepts `DOUBLE` (required: `False`, stream-only: `False`)
- [6] `Input6` accepts `DOUBLE` (required: `False`, stream-only: `False`)
- [7] `Input7` accepts `DOUBLE` (required: `False`, stream-only: `False`)
- [8] `Input8` accepts `DOUBLE` (required: `False`, stream-only: `False`)
- [9] `Input9` accepts `DOUBLE` (required: `False`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Max1", "typeName": "Max", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## Min

- Display name: Min
- typeName: `Min`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `2`, max `10`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Minimum of a few input values (from 2 to 6 inputs)  Inputs/Output: Output=DOUBLE

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Input1` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [2] `Input2` accepts `DOUBLE` (required: `False`, stream-only: `False`)
- [3] `Input3` accepts `DOUBLE` (required: `False`, stream-only: `False`)
- [4] `Input4` accepts `DOUBLE` (required: `False`, stream-only: `False`)
- [5] `Input5` accepts `DOUBLE` (required: `False`, stream-only: `False`)
- [6] `Input6` accepts `DOUBLE` (required: `False`, stream-only: `False`)
- [7] `Input7` accepts `DOUBLE` (required: `False`, stream-only: `False`)
- [8] `Input8` accepts `DOUBLE` (required: `False`, stream-only: `False`)
- [9] `Input9` accepts `DOUBLE` (required: `False`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Min1", "typeName": "Min", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## Multiply

- Display name: Multiply by
- typeName: `Multiply`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Multiplies each item of input by a constant factor.  Inputs/Output: Inputs=Input0(DOUBLE); Output=DOUBLE

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Coef` (`Double`), title="Multiply", default=`2`, range=`0.5`..`5` step `0.5`, shown=`True`, optimizable=`True`, help="Every item of input is multiplied by this coefficient ( Mult*x )"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Multiply1", "typeName": "Multiply", "blockType": "ConverterItem"
    }
  ]
}
```

## Not

- Display name: Not
- typeName: `Not`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `BOOL` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Negation. Incoming logical value is changed to the opposite. TRUE changes to FALSE, FALSE changes to TRUE.

### Inputs
- [0] `Input0` accepts `BOOL` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Not1", "typeName": "Not", "blockType": "ConverterItem"
    }
  ]
}
```

## Open

- Display name: Open
- typeName: `Open`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Opening price of the bar.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Open1", "typeName": "Open", "blockType": "ConverterItem"
    }
  ]
}
```

## OpenInterest

- Display name: Open Interest
- typeName: `OpenInterest`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Open interest as recieved from data feed. This value is shown also in 'Quotes' table.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "OpenInterest1", "typeName": "OpenInterest", "blockType": "ConverterItem"
    }
  ]
}
```

## OptVolatility

- Display name: Option Volatility
- typeName: `OptVolatility`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Theoretical option volatility received from the Exchange. This value is also shown at the Quotes window.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "OptVolatility1", "typeName": "OptVolatility", "blockType": "ConverterItem"
    }
  ]
}
```

## Or

- Display name: Or
- typeName: `Or`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `BOOL` (outputs: `1`, only-value-output: `False`)
- Inputs: min `2`, max `30`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Logical disjunction of a few input values (from 2 to 30 inputs). Output is TRUE if at least one input is TRUE.

### Inputs
- [0] `Input0` accepts `BOOL` (required: `True`, stream-only: `False`)
- [1] `Input1` accepts `BOOL` (required: `True`, stream-only: `False`)
- [2] `Input2` accepts `BOOL` (required: `False`, stream-only: `False`)
- [3] `Input3` accepts `BOOL` (required: `False`, stream-only: `False`)
- [4] `Input4` accepts `BOOL` (required: `False`, stream-only: `False`)
- [5] `Input5` accepts `BOOL` (required: `False`, stream-only: `False`)
- [6] `Input6` accepts `BOOL` (required: `False`, stream-only: `False`)
- [7] `Input7` accepts `BOOL` (required: `False`, stream-only: `False`)
- [8] `Input8` accepts `BOOL` (required: `False`, stream-only: `False`)
- [9] `Input9` accepts `BOOL` (required: `False`, stream-only: `False`)
- [10] `Input10` accepts `BOOL` (required: `False`, stream-only: `False`)
- [11] `Input11` accepts `BOOL` (required: `False`, stream-only: `False`)
- [12] `Input12` accepts `BOOL` (required: `False`, stream-only: `False`)
- [13] `Input13` accepts `BOOL` (required: `False`, stream-only: `False`)
- [14] `Input14` accepts `BOOL` (required: `False`, stream-only: `False`)
- [15] `Input15` accepts `BOOL` (required: `False`, stream-only: `False`)
- [16] `Input16` accepts `BOOL` (required: `False`, stream-only: `False`)
- [17] `Input17` accepts `BOOL` (required: `False`, stream-only: `False`)
- [18] `Input18` accepts `BOOL` (required: `False`, stream-only: `False`)
- [19] `Input19` accepts `BOOL` (required: `False`, stream-only: `False`)
- [20] `Input20` accepts `BOOL` (required: `False`, stream-only: `False`)
- [21] `Input21` accepts `BOOL` (required: `False`, stream-only: `False`)
- [22] `Input22` accepts `BOOL` (required: `False`, stream-only: `False`)
- [23] `Input23` accepts `BOOL` (required: `False`, stream-only: `False`)
- [24] `Input24` accepts `BOOL` (required: `False`, stream-only: `False`)
- [25] `Input25` accepts `BOOL` (required: `False`, stream-only: `False`)
- [26] `Input26` accepts `BOOL` (required: `False`, stream-only: `False`)
- [27] `Input27` accepts `BOOL` (required: `False`, stream-only: `False`)
- [28] `Input28` accepts `BOOL` (required: `False`, stream-only: `False`)
- [29] `Input29` accepts `BOOL` (required: `False`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Or1", "typeName": "Or", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## OrderBookPrice

- Display name: Order book, price
- typeName: `OrderBookPrice`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Price value from a row of the order book.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- `Buy` (`bool`), title="Direction", shown=`True`, optimizable=`True`, help="On - Buy, Off - Sell"
- `Index` (`int`), default=`0`, range=`0`..`` step ``, shown=`True`, optimizable=`True`, help="Index of row starting at 0, from the middle of the order book."

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "OrderBookPrice1", "typeName": "OrderBookPrice", "blockType": "ConverterItem"
    }
  ]
}
```

## OrderBookQty

- Display name: Order book, quantity
- typeName: `OrderBookQty`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Quantity value from a row of the order book.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- `Buy` (`bool`), title="Direction", shown=`True`, optimizable=`True`, help="On - Buy, Off - Sell"
- `Index` (`int`), default=`0`, range=`0`..`` step ``, shown=`True`, optimizable=`True`, help="Index of row starting at 0, from the middle of the order book."

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "OrderBookQty1", "typeName": "OrderBookQty", "blockType": "ConverterItem"
    }
  ]
}
```

## OrderBookTotal

- Display name: Order book, total
- typeName: `OrderBookTotal`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Total ask/bid for the depth of the order book.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)

### Parameters
- `Buy` (`bool`), title="Direction", shown=`True`, optimizable=`True`, help="On - Buy, Off - Sell"
- `NumberRows` (`int`), title="Number of rows", default=`0`, range=`0`..`` step ``, shown=`True`, optimizable=`True`, help="Number of rows from the middle of the order book for which the total"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "OrderBookTotal1", "typeName": "OrderBookTotal", "blockType": "ConverterItem"
    }
  ]
}
```

## PrevValue

- Display name: Previous value
- typeName: `PrevValue`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Returns the previous value N steps back.  Inputs/Output: Inputs=Input0(DOUBLE); Output=DOUBLE

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "PrevValue1", "typeName": "PrevValue", "blockType": "ConverterItem"
    }
  ]
}
```

## PriceMax

- Display name: High limit
- typeName: `PriceMax`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The block returns the upper limit of the instrument from quotes. The maximum possible price for this instrument for this session.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "PriceMax1", "typeName": "PriceMax", "blockType": "ConverterItem"
    }
  ]
}
```

## PriceMin

- Display name: Low limit
- typeName: `PriceMin`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The block returns the lower limit of the instrument from quotes. The minimum possible price for this instrument for this session.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "PriceMin1", "typeName": "PriceMin", "blockType": "ConverterItem"
    }
  ]
}
```

## QuoteByName

- Display name: Quote by name
- typeName: `QuoteByName`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Get the value from the Quote table.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Quote` (`QuotationField`), default=`LastPrice`, shown=`True`, optimizable=`True`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "QuoteByName1", "typeName": "QuoteByName", "blockType": "ConverterItem"
    }
  ]
}
```

## RandomHandler

- Display name: Random number
- typeName: `RandomHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Random number in the specified range.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=UNKNOWN

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `MaxValue` (`Double`), title="Max value", default=`10`, shown=`True`, optimizable=`True`
- `MinValue` (`Double`), title="Min value", default=`1`, shown=`True`, optimizable=`True`
- `Precision` (`int`), default=`0`, shown=`True`, optimizable=`True`, help="The number of decimal places."
- `SaveHistory` (`bool`), title="Save history", default=`true`, shown=`True`, optimizable=`True`
- `Seed` (`int`), default=`0`, shown=`True`, optimizable=`True`, help="A number used to calculate a starting value for the pseudo-random number sequence. (0 - not set)."

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "RandomHandler1", "typeName": "RandomHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## RelativeCommisionWithMinimal

- Display name: Relative comission with minimum
- typeName: `RelativeCommisionWithMinimal`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `UNKNOWN` (outputs: `0`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Relative commission for one trade (long or short) as percents. Minumum absolute comission for a trade is additionally applied.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `CommissionPct` (`Double`), title="Comission, %", default=`0.05`, range=`0.05`..`0.1` step `0.01`, shown=`True`, optimizable=`True`, help="Commission as a percent of volume"
- `MarginPct` (`Double`), title="Margin, %", default=`10.0`, range=`0.0`..`100` step `1.0`, shown=`True`, optimizable=`True`, help="Margin to open or to keep position (as percents)"
- `MinimalCommission` (`Double`), title="Minimal comission", default=`30.0`, range=`30.0`..`100` step `1.0`, shown=`True`, optimizable=`True`, help="Minimal absolute comission for a trade"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "RelativeCommisionWithMinimal1", "typeName": "RelativeCommisionWithMinimal", "blockType": "ConverterItem"
    }
  ]
}
```

## RelativeCommission

- Display name: Relative comission
- typeName: `RelativeCommission`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `UNKNOWN` (outputs: `0`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Relative commission for one trade (long or short) as percents. Cost of money: is used to get a price of a borrowed funds.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `CommissionPct` (`Double`), title="Comission, %", default=`0.05`, range=`0.05`..`0.1` step `0.01`, shown=`True`, optimizable=`True`, help="Commission as a percent of volume"
- `MarginPct` (`Double`), title="Margin, %", default=`10.0`, range=`0.0`..`100` step `1.0`, shown=`True`, optimizable=`True`, help="Margin to open or to keep position (as percents)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "RelativeCommission1", "typeName": "RelativeCommission", "blockType": "ConverterItem"
    }
  ]
}
```

### Parameterized Wiring Example
```json
{
  "ops": [
    {
      "op": "AddBlock",
      "blockId": "Commission",
      "typeName": "RelativeCommission",
      "blockType": "ConverterItem",
      "params": {
        "CommissionPct": 0.05,
        "MarginPct": 10.0
      }
    },
    {
      "op": "ConnectByInputName",
      "fromBlockId": "Src",
      "toBlockId": "Commission",
      "toInputName": "SECURITYSource"
    }
  ]
}
```

## ResettableControlledBoolConst

- Display name: Resettable Controlled Boolean Constant
- typeName: `ResettableControlledBoolConst`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `BOOL` (outputs: `1`, only-value-output: `False`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Resettable controlled boolean constant (switch). If input is TRUE the result is taken from a field 'Value', otherwise the result is taken from a field 'Default value'. Second input determines 'Value'. If it contains more TRUE, then 'Value' is set to 'Default value'.

### Inputs
- [0] `Input0` accepts `BOOL` (required: `True`, stream-only: `False`)
- [1] `Input1` accepts `BOOL` (required: `True`, stream-only: `False`)

### Parameters
- `DefaultValue` (`bool`), title="Default value", shown=`True`, optimizable=`False`, help="A value to return as output of a handler when input is false"
- `Value` (`BoolOptimProperty`), shown=`True`, optimizable=`True`, help="A value to return as output of a handler when input is true"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "ResettableControlledBoolConst1", "typeName": "ResettableControlledBoolConst", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## ResultForOptimization

- Display name: Result for optimization
- typeName: `ResultForOptimization`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `UNKNOWN` (outputs: `0`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Value for showing in the "Result from script" column in the optimization results grid.  Inputs/Output: Inputs=Input0(DOUBLE); Output=UNKNOWN

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "ResultForOptimization1", "typeName": "ResultForOptimization", "blockType": "ConverterItem"
    }
  ]
}
```

## SecDivideWith

- Display name: Divide with
- typeName: `SecDivideWith`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `SECURITY` (outputs: `1`, only-value-output: `False`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Handler converts bars of an input to a synthetic security (each incoming bar is divided by an individual weight from a second input).

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)
- [1] `Input1` accepts `DOUBLE` (required: `True`, stream-only: `True`)

### Parameters
- `Coef` (`Double`), title="Multiply", default=`1`, shown=`True`, optimizable=`True`, help="Every bar of input is multiplied by this coefficient ( Mult * x / Source2 )"
- `Decimals` (`int`), default=`2`, shown=`True`, optimizable=`False`, help="Decimals for ceiling"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SecDivideWith1", "typeName": "SecDivideWith", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## SecMultiply

- Display name: Multiply (CB) by
- typeName: `SecMultiply`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `SECURITY` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Handler converts bars of an input to a synthetic security (all prices of incoming bars are multiplied by a given coefficient).

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Coef` (`Double`), title="Multiply", default=`10`, shown=`True`, optimizable=`True`, help="Every bar of input is multiplied by this coefficient ( Mult*x )"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SecMultiply1", "typeName": "SecMultiply", "blockType": "ConverterItem"
    }
  ]
}
```

## SecMultiplyWith

- Display name: Multiply by
- typeName: `SecMultiplyWith`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `SECURITY` (outputs: `1`, only-value-output: `False`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Handler converts bars of an input to a synthetic security (each incoming bar is multiplied by an individual weight from a second input).

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)
- [1] `Input1` accepts `DOUBLE` (required: `True`, stream-only: `True`)

### Parameters
- `Coef` (`Double`), title="Multiply", default=`1`, shown=`True`, optimizable=`True`, help="Every bar of input is multiplied by this coefficient ( Mult * Source2 * x )"
- `Decimals` (`int`), default=`2`, shown=`True`, optimizable=`False`, help="Decimals for ceiling"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SecMultiplyWith1", "typeName": "SecMultiplyWith", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## SellDeposit

- Display name: Sell Deposit
- typeName: `SellDeposit`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No English description is available in handler metadata; treat the name and IO contract as authoritative.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SellDeposit1", "typeName": "SellDeposit", "blockType": "ConverterItem"
    }
  ]
}
```

## SessionClose

- Display name: Session close
- typeName: `SessionClose`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Shows a session close trade price.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Session` (`int`), default=`1`, range=`0`..`10` step `1`, shown=`True`, optimizable=`True`, help="Session"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SessionClose1", "typeName": "SessionClose", "blockType": "ConverterItem"
    }
  ]
}
```

## SessionHeld

- Display name: Current Session Bar
- typeName: `SessionHeld`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
A current bar index from start of current trading day.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SessionHeld1", "typeName": "SessionHeld", "blockType": "ConverterItem"
    }
  ]
}
```

## SessionHigh

- Display name: Session high
- typeName: `SessionHigh`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Shows the session highest trade price.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Session` (`int`), default=`1`, range=`0`..`10` step `1`, shown=`True`, optimizable=`True`, help="Session"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SessionHigh1", "typeName": "SessionHigh", "blockType": "ConverterItem"
    }
  ]
}
```

## SessionLow

- Display name: Session low
- typeName: `SessionLow`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Shows the session lowest trade price.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Session` (`int`), default=`1`, range=`0`..`10` step `1`, shown=`True`, optimizable=`True`, help="Session"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SessionLow1", "typeName": "SessionLow", "blockType": "ConverterItem"
    }
  ]
}
```

## SessionOpen

- Display name: Session open
- typeName: `SessionOpen`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Shows a session opening trade price.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Session` (`int`), default=`1`, range=`0`..`10` step `1`, shown=`True`, optimizable=`True`, help="Session"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SessionOpen1", "typeName": "SessionOpen", "blockType": "ConverterItem"
    }
  ]
}
```

## Shift

- Display name: Shift
- typeName: `Shift`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Moves values for N candles to the right.  Inputs/Output: Inputs=Input0(DOUBLE); Output=DOUBLE

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `Period` (`int`), default=`20`, range=`10`..`100` step `5`, shown=`True`, optimizable=`True`, help="Indicator period (processing window)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Shift1", "typeName": "Shift", "blockType": "ConverterItem"
    }
  ]
}
```

## StepPrice

- Display name: Step price
- typeName: `StepPrice`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
A step price recorded at the end of every bar (if available).  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "StepPrice1", "typeName": "StepPrice", "blockType": "ConverterItem"
    }
  ]
}
```

## StringConst

- Display name: String Constant
- typeName: `StringConst`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `STRING` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
This block sets a fixed string value for every bar.  Inputs/Output: Output=UNKNOWN

### Inputs
- [0] `Input0` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Value` (`String`), shown=`True`, optimizable=`True`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "StringConst1", "typeName": "StringConst", "blockType": "ConverterItem"
    }
  ]
}
```

## Sub

- Display name: Subtract
- typeName: `Sub`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Subtract second number from the first one  Inputs/Output: Output=DOUBLE

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `False`)
- [1] `Input1` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Sub1", "typeName": "Sub", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## TextHandler

- Display name: Text
- typeName: `TextHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `STRING` (outputs: `1`, only-value-output: `False`)
- Inputs: min `0`, max `0`
- AddBlock container: `ZeroInputItem`

### What It Does
This block has no entries. It has an editable text parameter which returns as a result of its work.  Inputs/Output: Output=UNKNOWN

### Inputs
- (none)

### Parameters
- `Text` (`String`), default=`*`, shown=`True`, optimizable=`True`, help="Text (string)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TextHandler1", "typeName": "TextHandler", "blockType": "ZeroInputItem"
    }
  ]
}
```

## TheoreticalPrice

- Display name: Theoretical price
- typeName: `TheoreticalPrice`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Theoretical instrument price received from the Exchange. This value is also shown at the Quotes window.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TheoreticalPrice1", "typeName": "TheoreticalPrice", "blockType": "ConverterItem"
    }
  ]
}
```

## Tick

- Display name: Price step
- typeName: `Tick`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Price step of a security. This value is shown also in 'Quotes' table.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Tick1", "typeName": "Tick", "blockType": "ConverterItem"
    }
  ]
}
```

## Time

- Display name: Time
- typeName: `Time`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Time of every bar is converted to number as hhmmss.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Time1", "typeName": "Time", "blockType": "ConverterItem"
    }
  ]
}
```

## TimeInMins

- Display name: Time in minutes
- typeName: `TimeInMins`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Time of the bar from midnight in minutes. I.e. time 10:31 converts to a number 631.  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TimeInMins1", "typeName": "TimeInMins", "blockType": "ConverterItem"
    }
  ]
}
```

## Volume

- Display name: Volume
- typeName: `Volume`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Volume of the bar  Inputs/Output: Inputs=SECURITYSource(SECURITY); Output=DOUBLE

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Volume1", "typeName": "Volume", "blockType": "ConverterItem"
    }
  ]
}
```

## WeightedAveragePrice

- Display name: Weighted average bar price
- typeName: `WeightedAveragePrice`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `TradeMath`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
The block contains the weighted average price of a bar, about on trades on the instrument. For correct work, use the second chart. 1 min = 60 sec.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Direction` (`TradeDirection2`), title="Direction trades", default=`All`, shown=`True`, optimizable=`True`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "WeightedAveragePrice1", "typeName": "WeightedAveragePrice", "blockType": "ConverterItem"
    }
  ]
}
```


