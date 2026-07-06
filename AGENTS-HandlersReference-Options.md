# Handlers Reference: Options

For each handler below:
- `typeName` is the string you pass to `/api/handlers/{typeName}` and `AddBlock` (`typeName` field).
- `blockType` is the container you must use for handler-based blocks (not template blocks).
- Input indices are zero-based (`toPort`).
- Hidden handlers (`[HandlerInvisible]`) require `allowHiddenHandler=true` in `AddBlock` (advanced). Some legacy helpers (e.g. `CycleHandler`) may be auto-converted to template blocks.

## AskSmile

- Display name: Ask smile
- typeName: `AskSmile`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `Options`
- Output: `DOUBLE2N` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Options ask prices. Strike is ignored if there is no offer in it.  Inputs/Output: Inputs=Input0(OPTION, OPTION_SERIES, OPTION_STRIKE); Output=DOUBLE2N

### Inputs
- [0] `Input0` accepts `OPTION, OPTION_SERIES, OPTION_STRIKE` (required: `True`, stream-only: `True`)

### Parameters
- `Shift` (`int`), title="Shift Time", default=`0`, range=`0`..`1000` step `1`, shown=`True`, optimizable=`True`, help="Shift calculations back in time"
- `StrikeType` (`StrikeType`), title="Option Type", shown=`True`, optimizable=`False`, help="Type of option to be used in handler (put, call, any)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "AskSmile1", "typeName": "AskSmile", "blockType": "ConverterItem"
    }
  ]
}
```

## AskStrikes

- Display name: Option Asks
- typeName: `AskStrikes`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `Options`
- Output: `DOUBLE2` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Options ask prices. Price is set to 0 if there is no offer in it. Handler returns a list of Double2.

### Inputs
- [0] `Input0` accepts `OPTION, OPTION_SERIES, OPTION_STRIKE` (required: `True`, stream-only: `True`)

### Parameters
- `StrikeType` (`StrikeType`), title="Option Type", default=`Any`, shown=`True`, optimizable=`True`, help="Type of option to be used in handler (put, call, any)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "AskStrikes1", "typeName": "AskStrikes", "blockType": "ConverterItem"
    }
  ]
}
```

## BasePx

- Display name: Base Price
- typeName: `BasePx`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `Options`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
A base asset price. Various algorithms are applied in calculation (fixed price, the last trade, quote midpoint, etc). It is a stream handler.

### Inputs
- [0] `Input0` accepts `SECURITY, OPTION, OPTION_SERIES` (required: `True`, stream-only: `True`)

### Parameters
- `DisplayPrice` (`OptimProperty`), title="Display Price", default=`0`, shown=`True`, optimizable=`True`, help="Base asset price (only to display at UI)"
- `DisplayUnits` (`FixedValueMode`), title="Display Units", default=`AsIs`, shown=`True`, optimizable=`False`, help="Display units (hundreds, thousands, as is)"
- `FixedPx` (`Double`), title="Price", default=`0`, shown=`True`, optimizable=`False`, help="Price for algorythm FixedPx"
- `PxMode` (`BasePxMode`), title="Algorythm", default=`LastTrade`, shown=`True`, optimizable=`False`, help="Algorythm to get base asset's price (FixedPx, LastTrade, etc)"
- `RepeatLastPx` (`bool`), title="Repeat Last Px", default=`false`, shown=`True`, optimizable=`True`, help="Handler should repeat last known value to avoid further logic errors"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BasePx1", "typeName": "BasePx", "blockType": "ConverterItem"
    }
  ]
}
```

## BidSmile

- Display name: Bid smile
- typeName: `BidSmile`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `Options`
- Output: `DOUBLE2N` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Options bid prices. Strike is ignored if there is no demand in it.  Inputs/Output: Inputs=Input0(OPTION, OPTION_SERIES, OPTION_STRIKE); Output=DOUBLE2N

### Inputs
- [0] `Input0` accepts `OPTION, OPTION_SERIES, OPTION_STRIKE` (required: `True`, stream-only: `True`)

### Parameters
- `Shift` (`int`), title="Shift Time", default=`0`, range=`0`..`1000` step `1`, shown=`True`, optimizable=`True`, help="Shift calculations back in time"
- `StrikeType` (`StrikeType`), title="Option Type", shown=`True`, optimizable=`False`, help="Type of option to be used in handler (put, call, any)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BidSmile1", "typeName": "BidSmile", "blockType": "ConverterItem"
    }
  ]
}
```

## BidStrikes

- Display name: Option Bids
- typeName: `BidStrikes`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `Options`
- Output: `DOUBLE2` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Options bid prices. Price is set to 0 if there is no demand in it. Handler returns a list of Double2.

### Inputs
- [0] `Input0` accepts `OPTION, OPTION_SERIES, OPTION_STRIKE` (required: `True`, stream-only: `True`)

### Parameters
- `StrikeType` (`StrikeType`), title="Option Type", default=`Any`, shown=`True`, optimizable=`True`, help="Type of option to be used in handler (put, call, any)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "BidStrikes1", "typeName": "BidStrikes", "blockType": "ConverterItem"
    }
  ]
}
```

## ExchangeTheorPx

- Display name: Exchange Theor Px
- typeName: `ExchangeTheorPx`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `Options`
- Output: `DOUBLE2` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Theoretical option price provided by exchange. Additional linear transformation is allowed.  Inputs/Output: Inputs=Input0(OPTION_SERIES); Output=DOUBLE2

### Inputs
- [0] `Input0` accepts `OPTION_SERIES` (required: `True`, stream-only: `True`)

### Parameters
- `Multiplier` (`Double`), default=`1`, range=`-1000000`..`1000000` step `1`, shown=`True`, optimizable=`False`, help="Price multiplier"
- `ShiftPx` (`Double`), title="Shift", default=`0`, range=`-1000000`..`1000000` step `1`, shown=`True`, optimizable=`False`, help="Price shift (price steps)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "ExchangeTheorPx1", "typeName": "ExchangeTheorPx", "blockType": "ConverterItem"
    }
  ]
}
```

## ExchangeTheorSigma2

- Display name: Exchange Smile
- typeName: `ExchangeTheorSigma2`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `Options`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Exchange smile (stream handler)  Inputs/Output: Inputs=OptionSeries(OPTION_SERIES), RiskFreeRate(DOUBLE); Output=INTERACTIVESPLINE

### Inputs
- [0] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `True`)
- [1] `RiskFreeRate` accepts `DOUBLE` (required: `True`, stream-only: `True`)

### Parameters
- `ExpiryTime` (`String`), title="Expiry Time", default=`18:45`, shown=`True`, optimizable=`False`, help="Exact expiration time of day (HH:mm)"
- `MultiplierPx` (`Double`), title="Multiplier", default=`1`, range=`-1000000`..`1000000` step `1`, shown=`True`, optimizable=`False`, help="Price multiplier"
- `OptionType` (`StrikeType`), title="Option Type", default=`Call`, shown=`True`, optimizable=`False`, help="Option type (parameter Any is not recommended)"
- `ShiftPx` (`Double`), title="Shift", default=`0`, range=`-1000000`..`1000000` step `1`, shown=`True`, optimizable=`False`, help="Price shift (price steps)"
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `SigmaMult` (`Double`), title="Width multiplier", default=`7`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`True`, help="Width multiplier"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "ExchangeTheorSigma21", "typeName": "ExchangeTheorSigma2", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## Heartbeat

- Display name: Heartbeat
- typeName: `Heartbeat`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers`
- Category: `Options`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `2`, max `2`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Recalculate script by timer  Inputs/Output: Inputs=Input0(SECURITY, OPTION, OPTION_SERIES), Input1(BOOL); Output=DOUBLE

### Inputs
- [0] `Input0` accepts `SECURITY, OPTION, OPTION_SERIES` (required: `True`, stream-only: `False`)
- [1] `Input1` accepts `BOOL` (required: `True`, stream-only: `False`)

### Parameters
- `DelayMs` (`int`), title="Delay", default=`30000`, shown=`True`, optimizable=`True`, help="Delay between calls (ms)"
- `OnlyAtTradingSession` (`bool`), title="Trading session only", default=`true`, shown=`True`, optimizable=`True`, help="If the flag is set, handler initiates execution only in agent mode at trading time when data provider is connected to market and the instrument is actually traded."

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "Heartbeat1", "typeName": "Heartbeat", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## IvSmile

- Display name: IV Smile
- typeName: `IvSmile`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `Options`
- Output: `INTERACTIVESPLINE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `4`, max `4`
- AddBlock container: `TwoOrMoreInputsItem`

### What It Does
Smile derived from option quotes (stream handler)  Inputs/Output: Inputs=FutPx(DOUBLE), Time(DOUBLE), OptionSeries(OPTION_SERIES), RiskFreeRate(DOUBLE); Output=INTERACTIVESPLINE

### Inputs
- [0] `FutPx` accepts `DOUBLE` (required: `True`, stream-only: `True`)
- [1] `Time` accepts `DOUBLE` (required: `True`, stream-only: `True`)
- [2] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `True`)
- [3] `RiskFreeRate` accepts `DOUBLE` (required: `True`, stream-only: `True`)

### Parameters
- `MaxSigmaPct` (`Double`), title="Max Sigma Pct", default=`200`, range=`-10000000`..`10000000` step `1`, shown=`True`, optimizable=`False`, help="Max volatility limit (percents)"
- `MaxStrike` (`Double`), title="Max strike", default=`1500000`, range=`0`..`10000000` step `1`, shown=`True`, optimizable=`False`, help="Max strike to be processed by handler"
- `MinStrike` (`Double`), title="Min strike", default=`1`, range=`0`..`10000000` step `1`, shown=`True`, optimizable=`False`, help="Min strike to be processed by handler"
- `OptionType` (`StrikeType`), title="Option Type", default=`Any`, shown=`True`, optimizable=`True`, help="Option type to be used by handler (call, put, best volatility)"
- `OptPxMode` (`OptionPxMode`), title="Price Mode", default=`Ask`, shown=`True`, optimizable=`False`, help="Algorythm to get option price"
- `ShiftAsk` (`Double`), title="Shift Ask", default=`0`, range=`-10000000`..`10000000` step `1`, shown=`True`, optimizable=`False`, help="Shift Asks up (price steps)"
- `ShiftBid` (`Double`), title="Shift Bid", default=`0`, range=`-10000000`..`10000000` step `1`, shown=`True`, optimizable=`False`, help="Shift Bids down (price steps)"
- `ShowNodes` (`bool`), title="Show nodes", default=`false`, shown=`True`, optimizable=`True`, help="Nodes are shown when true"
- `StrikeStep` (`Double`), title="Strike step", default=`2500`, range=`0`..`1000000` step `1`, shown=`True`, optimizable=`False`, help="Strike step"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "IvSmile1", "typeName": "IvSmile", "blockType": "TwoOrMoreInputsItem"
    }
  ]
}
```

## OptionBase

- Display name: Base asset
- typeName: `OptionBase`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `Options`
- Output: `SECURITY` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Returns the underlying (base) security for an option or option series. Use it to feed OHLC/indicator blocks or to plot the underlying when the input is an option source (stream handler).

### Inputs
- [0] `Input0` accepts `OPTION, OPTION_SERIES` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "OptionBase1", "typeName": "OptionBase", "blockType": "ConverterItem"
    }
  ]
}
```

## OptionSelector

- Display name: Option Selector
- typeName: `OptionSelector`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `Options`
- Output: `OPTION` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `8`
- AddBlock container: `ConverterItem`

### What It Does
Selects one OPTION source from up to 8 connected inputs based on two string parameters: Base asset prefix (e.g. "RI") and Option Series (e.g. "RIM7"). On each execution it scans the available series of the connected sources, builds/updates dropdown lists for these parameters, and returns the first option source matching both prefix and series; otherwise returns null (stream handler).

### Inputs
- [0] `Option 1` accepts `OPTION` (required: `True`, stream-only: `True`)
- [1] `Option 2` accepts `OPTION` (required: `False`, stream-only: `True`)
- [2] `Option 3` accepts `OPTION` (required: `False`, stream-only: `True`)
- [3] `Option 4` accepts `OPTION` (required: `False`, stream-only: `True`)
- [4] `Option 5` accepts `OPTION` (required: `False`, stream-only: `True`)
- [5] `Option 6` accepts `OPTION` (required: `False`, stream-only: `True`)
- [6] `Option 7` accepts `OPTION` (required: `False`, stream-only: `True`)
- [7] `Option 8` accepts `OPTION` (required: `False`, stream-only: `True`)

### Parameters
- `BaseSecPrefix` (`String`), title="Base asset", default=`RI`, shown=`True`, optimizable=`True`, help="Select base asset prefix used to filter connected option sources (e.g. "RI", "Si", "Eu"). This also drives the dynamic Option Series dropdown list built from connected sources."
- `OptionSeries` (`String`), title="Option Series", default=`RIM7`, shown=`True`, optimizable=`True`, help="Select option series identifier (e.g. "RIH5", "SiG5"). The list of available series is built dynamically from the connected option sources each time the script executes."

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "OptionSelector1", "typeName": "OptionSelector", "blockType": "ConverterItem"
    }
  ]
}
```

## OptionSeriesByNumber

- Display name: Option Series by Number
- typeName: `OptionSeriesByNumber`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `Options`
- Output: `OPTION_SERIES` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Selects an option series (expiration) from an OPTION source. Supports multiple modes: FixedExpiry (exact date), FirstExpiry, LastExpiry, and ExpiryByNumber (N-th alive series ordered by expiration). "Alive" is evaluated against the last bar date of the underlying. Throws if no matching series is available (stream handler).

### Inputs
- [0] `OPTIONSource` accepts `OPTION` (required: `True`, stream-only: `True`)

### Parameters
- `ExpirationMode` (`ExpiryMode`), title="Expiration Algo", default=`FixedExpiry`, shown=`True`, optimizable=`True`, help="Algorythm to determine expiration date"
- `Expiry` (`String`), default=`17-11-2014 18:45`, shown=`True`, optimizable=`True`, help="Expiration datetime (including time of a day) for algorythm FixedExpiry"
- `Number` (`int`), title="Series index", default=`1`, range=`1`..`` step ``, shown=`True`, optimizable=`True`, help="Series index (only alive series) for algorythm ExpiryByNumber"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "OptionSeriesByNumber1", "typeName": "OptionSeriesByNumber", "blockType": "ConverterItem"
    }
  ]
}
```

## OptionSeriesSelector

- Display name: Option Series Selector
- typeName: `OptionSeriesSelector`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `Options`
- Output: `OPTION_SERIES` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Choose one of several option series from single OPTION source  Inputs/Output: Inputs=Option(OPTION, OPTION_SERIES); Output=OPTION_SERIES

### Inputs
- [0] `Option` accepts `OPTION, OPTION_SERIES` (required: `True`, stream-only: `True`)

### Parameters
- `AliveOnly` (`bool`), title="Alive Only", default=`true`, shown=`True`, optimizable=`True`, help="Handler will use only alive option series"
- `OptionSeries` (`String`), title="Option Series", default=`RIM7`, shown=`True`, optimizable=`True`, help="Select option series (RIH5, SiG5, ESM6, ...)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "OptionSeriesSelector1", "typeName": "OptionSeriesSelector", "blockType": "ConverterItem"
    }
  ]
}
```

## OptionStrikeCount

- Display name: Count Options
- typeName: `OptionStrikeCount`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `Options`
- Output: `INT` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Number of options in the source  Inputs/Output: Inputs=OPTIONSource(OPTION); Output=INT

### Inputs
- [0] `OPTIONSource` accepts `OPTION` (required: `True`, stream-only: `True`)

### Parameters
- (none)

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "OptionStrikeCount1", "typeName": "OptionStrikeCount", "blockType": "ConverterItem"
    }
  ]
}
```

## SelectStrike

- Display name: Select strike
- typeName: `SelectStrike`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `Options`
- Output: `DOUBLE` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Use drop-down control to select single strike from option series. To use it link 'Strike' property to Control pane.

### Inputs
- [0] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `True`)

### Parameters
- `Strike` (`String`), default=`120000`, shown=`True`, optimizable=`True`, help="Option strike"
- `StrikeStep` (`Double`), title="Strike step", default=`0`, range=`0`..`10000000` step `1`, shown=`True`, optimizable=`True`, help="Strike step to extract most important options"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SelectStrike1", "typeName": "SelectStrike", "blockType": "ConverterItem"
    }
  ]
}
```

## SeriesSelector

- Display name: Series Selector
- typeName: `SeriesSelector`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `Options`
- Output: `OPTION_SERIES` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `9`
- AddBlock container: `ConverterItem`

### What It Does
Choose one of several option series  Inputs/Output: Inputs=Option 1(OPTION_SERIES), Option 2(OPTION_SERIES), Option 3(OPTION_SERIES), Option 4(OPTION_SERIES), Option 5(OPTION_SERIES), Option 6(OPTION_SERIES), Option 7(OPTION_SERIES), Option 8(OPTION_SERIES), Option 9(OPTION_SERIES); Output=OPTION_SERIES

### Inputs
- [0] `Option 1` accepts `OPTION_SERIES` (required: `True`, stream-only: `True`)
- [1] `Option 2` accepts `OPTION_SERIES` (required: `False`, stream-only: `True`)
- [2] `Option 3` accepts `OPTION_SERIES` (required: `False`, stream-only: `True`)
- [3] `Option 4` accepts `OPTION_SERIES` (required: `False`, stream-only: `True`)
- [4] `Option 5` accepts `OPTION_SERIES` (required: `False`, stream-only: `True`)
- [5] `Option 6` accepts `OPTION_SERIES` (required: `False`, stream-only: `True`)
- [6] `Option 7` accepts `OPTION_SERIES` (required: `False`, stream-only: `True`)
- [7] `Option 8` accepts `OPTION_SERIES` (required: `False`, stream-only: `True`)
- [8] `Input8` accepts `UNKNOWN` (required: `False`, stream-only: `True`)

### Parameters
- `AliveOnly` (`bool`), title="Alive Only", default=`true`, shown=`True`, optimizable=`True`, help="Handler will use only alive option series"
- `OptionSeries` (`String`), title="Option Series", default=`NULL`, shown=`True`, optimizable=`True`, help="Select option series (RIH5, SiG5, ESM6, ...)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SeriesSelector1", "typeName": "SeriesSelector", "blockType": "ConverterItem"
    }
  ]
}
```

## SingleOption

- Display name: Single Option
- typeName: `SingleOption`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `Options`
- Output: `SECURITY` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `2`
- AddBlock container: `ConverterItem`

### What It Does
Extracts a single option security (Call or Put) from an option series. The strike can be fixed (FixedStrike) or supplied as a time series (the last value is used). SelectionMode defines how the strike pair is chosen (FixedStrike/Min/Max/NearestATM). If the required strike is missing: logs a warning in Lab mode; in Agent mode throws a ScriptException to prevent silent nulls (stream handler).

### Inputs
- [0] `OptionSeries` accepts `OPTION_SERIES` (required: `True`, stream-only: `True`)
- [1] `Strike` accepts `DOUBLE` (required: `False`, stream-only: `True`)

### Parameters
- `FixedStrike` (`Double`), title="Strike", default=`120000`, shown=`True`, optimizable=`True`, help="Strike used when SelectionMode=FixedStrike and no strike series input is provided."
- `OptionType` (`StrikeType`), title="Option Type", default=`Call`, shown=`True`, optimizable=`True`, help="Option type (parameter Any is not recommended)"
- `SelectionMode` (`StrikeSelectionMode`), title="Search Algo", default=`FixedStrike`, shown=`True`, optimizable=`True`, help="How to choose the strike pair: FixedStrike uses the Strike parameter; Min/Max choose boundary strikes; NearestATM chooses the pair closest to the underlying last price."

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "SingleOption1", "typeName": "SingleOption", "blockType": "ConverterItem"
    }
  ]
}
```

## VerticalLine

- Display name: Vertical Line
- typeName: `VerticalLine`
- Namespace: `TSLab.Script.Handlers.Options`
- Assembly: `TSLab.Script.Handlers.Options`
- Category: `Options`
- Output: `DOUBLE2` (outputs: `1`, only-value-output: `False`)
- Inputs: min `1`, max `1`
- AddBlock container: `ConverterItem`

### What It Does
Vertical line for CanvasPane (no interaction with user)  Inputs/Output: Inputs=Input0(DOUBLE); Output=DOUBLE2

### Inputs
- [0] `Input0` accepts `DOUBLE` (required: `True`, stream-only: `True`)

### Parameters
- `SigmaHighPct` (`Double`), title="Sigma High, %", default=`50`, range=`0`..`10000000` step `0.01`, shown=`True`, optimizable=`False`, help="High level of this marker (in percents)"
- `SigmaLowPct` (`Double`), title="Sigma Low, %", default=`10`, range=`0`..`10000000` step `0.01`, shown=`True`, optimizable=`False`, help="Low level of this marker (in percents)"

### AddBlock Example
```json
{
  "ops": [
    {
      "op": "AddBlock", "blockId": "VerticalLine1", "typeName": "VerticalLine", "blockType": "ConverterItem"
    }
  ]
}
```

