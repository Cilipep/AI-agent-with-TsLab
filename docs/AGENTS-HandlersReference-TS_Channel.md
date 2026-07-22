# Handlers Reference: TS Channel

For each handler below:
- `typeName` is the string you pass to `/api/handlers/{typeName}` and `AddBlock` (`typeName` field).
- `blockType` is the container you must use for handler-based blocks (not template blocks).
- Input indices are zero-based (`toPort`).
- Hidden handlers (`[HandlerInvisible]`) require `allowHiddenHandler=true` in `AddBlock` (advanced). Some legacy helpers (e.g. `CycleHandler`) may be auto-converted to template blocks.

## BoolReceiverHandler

- Display name: Boolean Decoder
- typeName: `BoolReceiverHandler`
- Namespace: `TSLab.Script.Handlers.TSChannel`
- Assembly: `TSLab.Script.Handlers`
- Category: `TS Channel`
- Output: `BOOL` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `2`
- AddBlock container: `ConverterItem`

### What It Does
No English description is available in handler metadata; treat the name and IO contract as authoritative.

### Inputs
- [0] `SECURITYSource` accepts `STRING` (required: `True`, stream-only: `True`)
- [1] `Prefix` accepts `STRING` (required: `False`, stream-only: `True`)

### Parameters
- `DefaultValue` (`bool`), title="Default value", default=`false`, shown=`True`, optimizable=`True`, help="A value to return as output of a handler when can't load from server"
- `Value` (`bool`), shown=`True`, optimizable=`True`, help="Extracts the value corresponding to the desired key from the received data packet and makes it available for further calculations."

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BoolReceiverHandler1", "typeName": "BoolReceiverHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## ChannelHandler

- Display name: Transmitter
- typeName: `ChannelHandler`
- Namespace: `TSLab.Script.Handlers.TSChannel`
- Assembly: `TSLab.Script.Handlers`
- Category: `TS Channel`
- Output: `STRING` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `2`
- AddBlock container: `ConverterItem`

### What It Does
Transmits all the "key: value" pairs formed by packer blocks to the TSChannel server. The transfer of a batch of values occurs at the time of recalculation of the script.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)
- [1] `On/Off` accepts `BOOL` (required: `False`, stream-only: `True`)

### Parameters
- `ChannelApiKey` (`String`), title="Api Key", shown=`True`, optimizable=`True`, editor=`TransmitterApiKeyEditor`, help="The key that determines which TSChannel the values will be transmitted to. Copy the API Key value from the "Transmitter" of the corresponding channel in your account on signal.tslab.pro"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "ChannelHandler1", "typeName": "ChannelHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## IsReceiverOnline

- Display name: Is Receiver Online
- typeName: `IsReceiverOnline`
- Namespace: `TSLab.Script.Handlers.TSChannel`
- Assembly: `TSLab.Script.Handlers`
- Category: `TS Channel`
- Output: `BOOL` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
No English description is available in handler metadata; treat the name and IO contract as authoritative.

### Inputs
- [0] `SECURITYSource` accepts `STRING` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "IsReceiverOnline1", "typeName": "IsReceiverOnline", "blockType": "ConverterItem"
    }
  ]
}
```

## ParameterSenderHandler

- Display name: Parameter Encoder
- typeName: `ParameterSenderHandler`
- Namespace: `TSLab.Script.Handlers.TSChannel`
- Assembly: `TSLab.Script.Handlers`
- Category: `TS Channel`
- Output: `UNKNOWN` (outputs: `0`, only-value-output: `True`)
- Inputs: min `1`, max `2`
- AddBlock container: `ConverterItem`

### What It Does
Generates a "Key/Value" pair based on a parameter of another block, for example, an indicator. [br]Block's Name defines the key (name) of the value passed to the channel. When it is received in another script, it will be possible to identify the value by this name.

### Inputs
- [0] `SECURITYSource` accepts `STRING` (required: `True`, stream-only: `False`)
- [1] `Prefix` accepts `STRING` (required: `False`, stream-only: `False`)

### Parameters
- `Value` (`Double`), shown=`True`, optimizable=`True`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "ParameterSenderHandler1", "typeName": "ParameterSenderHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## ReceiverHandler

- Display name: Receiver
- typeName: `ReceiverHandler`
- Namespace: `TSLab.Script.Handlers.TSChannel`
- Assembly: `TSLab.Script.Handlers`
- Category: `TS Channel`
- Output: `STRING` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Receives data packets from the TSChannel. A new data packet is received when the script is being recalculated.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `ChannelApiKey` (`String`), title="Channel Api Key", shown=`True`, optimizable=`True`, editor=`ChannelApiKeyEditor`, help="Channel Api Key to test access for channel"
- `ReceiverApiKey` (`String`), title="Api Key", shown=`True`, optimizable=`True`, editor=`ReceiverApiKeyEditor`, help="The key that determines which TSChannel values will be taken from. Copy the API Key value from the "Receiver" of the corresponding channel in your account on signal.tslab.pro"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "ReceiverHandler1", "typeName": "ReceiverHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## ValueReceiverHandler

- Display name: Value Decoder
- typeName: `ValueReceiverHandler`
- Namespace: `TSLab.Script.Handlers.TSChannel`
- Assembly: `TSLab.Script.Handlers`
- Category: `TS Channel`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `2`
- AddBlock container: `ConverterItem`

### What It Does
Receives data packets from the TSChannel. A new data packet is received when the script is being recalculated.

### Inputs
- [0] `SECURITYSource` accepts `STRING` (required: `True`, stream-only: `True`)
- [1] `Prefix` accepts `STRING` (required: `False`, stream-only: `True`)

### Parameters
- `DefaultValue` (`Double`), title="Default value", default=`0`, shown=`True`, optimizable=`True`, help="A value to return as output of a handler when can't load from server"
- `Value` (`Double`), shown=`True`, optimizable=`True`, help="Extracts the value corresponding to the desired key from the received data packet and makes it available for further calculations."

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "ValueReceiverHandler1", "typeName": "ValueReceiverHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## ValueSenderHandler

- Display name: Value Encoder
- typeName: `ValueSenderHandler`
- Namespace: `TSLab.Script.Handlers.TSChannel`
- Assembly: `TSLab.Script.Handlers`
- Category: `TS Channel`
- Output: `UNKNOWN` (outputs: `0`, only-value-output: `True`)
- Inputs: min `2`, max `3`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Generates a "Key/Value" pair based on the value calculated in the script. [br]Block's Name defines the key (name) of the value passed to the channel. When it is received in another script, it will be possible to identify the value by this name.

### Inputs
- [0] `SECURITYSource` accepts `STRING` (required: `True`, stream-only: `False`)
- [1] `Value` accepts `DOUBLE, INT, BOOL` (required: `True`, stream-only: `False`)
- [2] `Prefix` accepts `STRING` (required: `False`, stream-only: `False`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "ValueSenderHandler1", "typeName": "ValueSenderHandler", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

