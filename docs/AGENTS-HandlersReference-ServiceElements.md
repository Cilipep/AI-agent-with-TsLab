# Handlers Reference: ServiceElements

For each handler below:
- `typeName` is the string you pass to `/api/handlers/{typeName}` and `AddBlock` (`typeName` field).
- `blockType` is the container you must use for handler-based blocks (not template blocks).
- Input indices are zero-based (`toPort`).
- Hidden handlers (`[HandlerInvisible]`) require `allowHiddenHandler=true` in `AddBlock` (advanced). Some legacy helpers (e.g. `CycleHandler`) may be auto-converted to template blocks.

## ControlMessageHandler

- Display name: Control message
- typeName: `ControlMessageHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ServiceElements`
- Output: `UNKNOWN` (outputs: `0`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Outputs control message  Inputs/Output: Inputs=Input0(BOOL); Output=UNKNOWN

### Inputs
- [0] `Input0` accepts `BOOL` (required: `True`, stream-only: `False`)

### Parameters
- `FalseMessage` (`String`), title="False message", shown=`True`, optimizable=`True`, help="False message"
- `Message` (`StringOptimProperty`), shown=`True`, optimizable=`True`, help="Message"
- `TrueMessage` (`String`), title="True message", shown=`True`, optimizable=`True`, help="True message"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "ControlMessageHandler1", "typeName": "ControlMessageHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## EventKindHandler

- Display name: Event
- typeName: `EventKindHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ServiceElements`
- Output: `BOOL` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
During the next recalculation, if the specified event is executed, the Event block will return the value true. This value can be used in the algorithm. [br]The block can be used many times in the editor. The block connects to the source, returns an event for the tool.

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `EventKind` (`EventKind`), title="Event kind", default=`None`, shown=`True`, optimizable=`True`, help="Event type: None, Order rejected, Order filled, Position opening, Position closing, Order quantity changed, Trading is started, Trading is stopped, Order canceled, Pretrade limitation."

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "EventKindHandler1", "typeName": "EventKindHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## ExportValuesHandler

- Display name: Export values
- typeName: `ExportValuesHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ServiceElements`
- Output: `UNKNOWN` (outputs: `0`, only-value-output: `False`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Passes the value by the identifier set by the user.  Inputs/Output: Output=UNKNOWN

### Inputs
- [0] `Input0` accepts `SECURITY` (required: `True`, stream-only: `False`)
- [1] `Input1` accepts `DOUBLE, INT, BOOL` (required: `True`, stream-only: `False`)

### Parameters
- `Id` (`String`), title="Identifier", shown=`True`, optimizable=`True`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "ExportValuesHandler1", "typeName": "ExportValuesHandler", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## FormatMessageHandler

- Display name: Format message
- typeName: `FormatMessageHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ServiceElements`
- Output: `STRING` (outputs: `1`, only-value-output: `True`)
- Inputs: min `2`, max `30`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
When the value appears at the input of the block 'True' outputs a formatted message to the program log.      Formatting:      {Input3} - user input value 3      ...      {Input30} - user input value 30      {DateTime} - date and time      {InitDeposit} - initial deposit      {Symbol} - the name of the instrument      {Interval} - the interval      {lastPrice} - current price      {EntryPrice} - entry price of the last position

### Inputs
- [0] `SECURITYSource` accepts `SECURITY` (required: `True`, stream-only: `False`)
- [1] `Input1` accepts `BOOL` (required: `True`, stream-only: `False`)
- [2] `Input2` accepts `UNKNOWN` (required: `False`, stream-only: `False`)
- [3] `Input3` accepts `UNKNOWN` (required: `False`, stream-only: `False`)
- [4] `Input4` accepts `UNKNOWN` (required: `False`, stream-only: `False`)
- [5] `Input5` accepts `UNKNOWN` (required: `False`, stream-only: `False`)
- [6] `Input6` accepts `UNKNOWN` (required: `False`, stream-only: `False`)
- [7] `Input7` accepts `UNKNOWN` (required: `False`, stream-only: `False`)
- [8] `Input8` accepts `UNKNOWN` (required: `False`, stream-only: `False`)
- [9] `Input9` accepts `UNKNOWN` (required: `False`, stream-only: `False`)
- [10] `Input10` accepts `UNKNOWN` (required: `False`, stream-only: `False`)
- [11] `Input11` accepts `UNKNOWN` (required: `False`, stream-only: `False`)
- [12] `Input12` accepts `UNKNOWN` (required: `False`, stream-only: `False`)
- [13] `Input13` accepts `UNKNOWN` (required: `False`, stream-only: `False`)
- [14] `Input14` accepts `UNKNOWN` (required: `False`, stream-only: `False`)
- [15] `Input15` accepts `UNKNOWN` (required: `False`, stream-only: `False`)
- [16] `Input16` accepts `UNKNOWN` (required: `False`, stream-only: `False`)
- [17] `Input17` accepts `UNKNOWN` (required: `False`, stream-only: `False`)
- [18] `Input18` accepts `UNKNOWN` (required: `False`, stream-only: `False`)
- [19] `Input19` accepts `UNKNOWN` (required: `False`, stream-only: `False`)
- [20] `Input20` accepts `UNKNOWN` (required: `False`, stream-only: `False`)
- [21] `Input21` accepts `UNKNOWN` (required: `False`, stream-only: `False`)
- [22] `Input22` accepts `UNKNOWN` (required: `False`, stream-only: `False`)
- [23] `Input23` accepts `UNKNOWN` (required: `False`, stream-only: `False`)
- [24] `Input24` accepts `UNKNOWN` (required: `False`, stream-only: `False`)
- [25] `Input25` accepts `UNKNOWN` (required: `False`, stream-only: `False`)
- [26] `Input26` accepts `UNKNOWN` (required: `False`, stream-only: `False`)
- [27] `Input27` accepts `UNKNOWN` (required: `False`, stream-only: `False`)
- [28] `Input28` accepts `UNKNOWN` (required: `False`, stream-only: `False`)
- [29] `Input29` accepts `UNKNOWN` (required: `False`, stream-only: `False`)

### Parameters
- `Message` (`String`), default=`{DateTime}: {Input3}`, shown=`True`, optimizable=`False`, editor=`FormatMessageEditor`, help="Message"
- `MessageFormat` (`String`), title="Message format", shown=`True`, optimizable=`False`, help="Message format:  {Trade Name} - agent or script name  {Text} - message"
- `Tag` (`String`), default=`Tag`, shown=`True`, optimizable=`True`, help="Additional user tag"
- `Type` (`MessageType`), title="Importance", default=`Info`, shown=`True`, optimizable=`True`, help="Message importance (Info, Warning, Error)"
- `WriteToLog` (`bool`), title="Write to log", default=`true`, shown=`True`, optimizable=`True`, help="Write message to log"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "FormatMessageHandler1", "typeName": "FormatMessageHandler", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## HeartbeatHandler

- Display name: Heartbeat 2
- typeName: `HeartbeatHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ServiceElements`
- Output: `UNKNOWN` (outputs: `0`, only-value-output: `False`)
- Inputs: min `0`, max `0`
- AddBlock container: `ZeroInputItem`

### What It Does
Automatic forced recalculation of the script after a specified period of time. The forced recalculation is started via the Recalc() method in the API. By default, protection is enabled so that the recalculation does not start more often than 300ms.

### Inputs
- (none)

### Parameters
- `Interval` (`TimeSpan`), default=`0:1:0`, range=`0:0:0`..`1.0:0:0` step `0:0:1`, shown=`True`, optimizable=`True`, help="Interval"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "HeartbeatHandler1", "typeName": "HeartbeatHandler", "blockType": "ZeroInputItem"
    }
  ]
}
```

## ImportBoolValuesHandler

- Display name: Import bool values
- typeName: `ImportBoolValuesHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ServiceElements`
- Output: `BOOL` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Returns a Boolean value, according to the identifier set in the Export values block.  Inputs/Output: Output=UNKNOWN

### Inputs
- [0] `Input0` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Id` (`String`), title="Identifier", shown=`True`, optimizable=`True`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "ImportBoolValuesHandler1", "typeName": "ImportBoolValuesHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## ImportDoubleValuesHandler

- Display name: Import double values
- typeName: `ImportDoubleValuesHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ServiceElements`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Returns a Double value, according to the identifier set in the Export values block.  Inputs/Output: Output=UNKNOWN

### Inputs
- [0] `Input0` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Id` (`String`), title="Identifier", shown=`True`, optimizable=`True`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "ImportDoubleValuesHandler1", "typeName": "ImportDoubleValuesHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## ImportIntValuesHandler

- Display name: Import int values
- typeName: `ImportIntValuesHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ServiceElements`
- Output: `INT` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Returns an integer, according to the Identifier set in the Export values block.  Inputs/Output: Output=UNKNOWN

### Inputs
- [0] `Input0` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Id` (`String`), title="Identifier", shown=`True`, optimizable=`True`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "ImportIntValuesHandler1", "typeName": "ImportIntValuesHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## InstrumentByName

- Display name: Instrument by name
- typeName: `InstrumentByName`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ServiceElements`
- Output: `SECURITY` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Find the instrument by name in the List of instruments. If the instrument is not found by name, it returns the first one in the list.

### Inputs
- [0] `SECURITYSource` accepts `MULTI_SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Name` (`String`), shown=`True`, optimizable=`True`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "InstrumentByName1", "typeName": "InstrumentByName", "blockType": "ConverterItem"
    }
  ]
}
```

## InstrumentByNumber

- Display name: Instrument by number
- typeName: `InstrumentByNumber`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ServiceElements`
- Output: `SECURITY` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Find the instrument by number in the List of instruments.  Inputs/Output: Inputs=SECURITYSource(MULTI_SECURITY); Output=SECURITY

### Inputs
- [0] `SECURITYSource` accepts `MULTI_SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- `Number` (`int`), default=`0`, shown=`True`, optimizable=`True`

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "InstrumentByNumber1", "typeName": "InstrumentByNumber", "blockType": "ConverterItem"
    }
  ]
}
```

## LoadFromGlobalCache2

- Display name: Load from Global Cache
- typeName: `LoadFromGlobalCache2`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ServiceElements`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Load indicator from Global Cache  Inputs/Output: Inputs=AnyOption(SECURITY, OPTION, OPTION_SERIES); Output=DOUBLE

### Inputs
- [0] `AnyOption` accepts `SECURITY, OPTION, OPTION_SERIES` (required: `True`, stream-only: `True`)

### Parameters
- `LoadFromStorage` (`bool`), title="Load from disk", default=`true`, shown=`True`, optimizable=`True`, help="Load from HDD to use indicator values across different program sessions"
- `Name` (`String`), default=`MyCache`, shown=`True`, optimizable=`True`, help="Unique name in the Global Cache"
- `WaitLastValue` (`int`), title="Wait last value (ms)", default=`0`, shown=`True`, optimizable=`True`, help="Wait for the value for the last bar. Only in agent mode. In milliseconds."

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "LoadFromGlobalCache21", "typeName": "LoadFromGlobalCache2", "blockType": "ConverterItem"
    }
  ]
}
```

## MessageHandler

- Display name: Message
- typeName: `MessageHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ServiceElements`
- Output: `UNKNOWN` (outputs: `0`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
When input becomes TRUE a handler sends user message to a TSLab log.  Inputs/Output: Inputs=Input0(BOOL); Output=UNKNOWN

### Inputs
- [0] `Input0` accepts `BOOL` (required: `True`, stream-only: `False`)

### Parameters
- `Message` (`String`), shown=`True`, optimizable=`False`, help="Message"
- `Tag` (`String`), default=`Tag`, shown=`True`, optimizable=`False`, help="Additional user tag"
- `Type` (`MessageType`), title="Importance", default=`Info`, shown=`True`, optimizable=`False`, help="Message importance (Info, Warning, Error)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "MessageHandler1", "typeName": "MessageHandler", "blockType": "ConverterItem"
    }
  ]
}
```

## RecalcScheduler

- Display name: Recalc Scheduler
- typeName: `RecalcScheduler`
- Namespace: `TSLab.Script.Handlers.Service`
- Assembly: `TSLab.Script.Handlers`
- Category: `ServiceElements`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Execute a script by schedule.  Inputs/Output: Inputs=Input0(SECURITY, OPTION, OPTION_SERIES); Output=DOUBLE

### Inputs
- [0] `Input0` accepts `SECURITY, OPTION, OPTION_SERIES` (required: `True`, stream-only: `True`)

### Parameters
- `RecalcTime` (`TimeSpan`), title="Time", default=`9:59:58`, shown=`True`, optimizable=`True`, editor=`TimeSpanEditor`, help="Executing time."

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "RecalcScheduler1", "typeName": "RecalcScheduler", "blockType": "ConverterItem"
    }
  ]
}
```

## SaveToGlobalCache2

- Display name: Save to Global Cache
- typeName: `SaveToGlobalCache2`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ServiceElements`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `True`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Save any indicator to Global Cache. The last value is recorded.  Inputs/Output: Inputs=AnyOption(SECURITY, OPTION, OPTION_SERIES), Indicator(DOUBLE); Output=DOUBLE

### Inputs
- [0] `AnyOption` accepts `SECURITY, OPTION, OPTION_SERIES` (required: `True`, stream-only: `False`)
- [1] `Indicator` accepts `DOUBLE` (required: `True`, stream-only: `False`)

### Parameters
- `IsTraceToFile` (`bool`), title="Log to file", default=`false`, shown=`True`, optimizable=`True`, help="Log data to file Temp\GlobalCache_{name}.txt"
- `MaxValues` (`int`), title="Maximum numbers", default=`0`, shown=`True`, optimizable=`True`, help="The maximum number of values. If 0, then it will be limited by the number of bars"
- `Name` (`String`), default=`MyCache`, shown=`True`, optimizable=`True`, help="Unique name in the Global Cache"
- `NotTrim` (`bool`), title="Do not trim", default=`false`, shown=`True`, optimizable=`True`, help="When saving, do not limit the data. When enabling this setting, the 'Maximum numbers' setting will not be taken into account"
- `SaveToNextBar` (`bool`), title="Save to next bar", default=`true`, shown=`True`, optimizable=`True`, help="Save the new value to the next bar. If disabled, it will save to the current bar."
- `SaveToStorage` (`bool`), title="Save to disk", default=`true`, shown=`True`, optimizable=`True`, help="Save to HDD to use indicator values across different program sessions"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SaveToGlobalCache21", "typeName": "SaveToGlobalCache2", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## TimestampHandler

- Display name: Timestamp
- typeName: `TimestampHandler`
- Namespace: `TSLab.Script.Handlers`
- Assembly: `TSLab.Script.Handlers`
- Category: `ServiceElements`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Time in Unix Time Stamp format with milliseconds. [br]Feature: the block returns a number without conversions, regardless of the "Local Time" settings in the data provider. The block gives the corresponding UTC time/date in the UTS format on the bar.

### Inputs
- [0] `Input0` accepts `SECURITY` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "TimestampHandler1", "typeName": "TimestampHandler", "blockType": "ConverterItem"
    }
  ]
}
```

