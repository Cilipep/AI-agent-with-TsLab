# Examples & Recipes: Editing TSLab Scripts via Web API `ops`

This file contains concrete "cookbook" scenarios. It is written for agent authors and humans designing tasks for the agent.

STOP. If the current exact artifact is still blank or source-only and no real mutation has happened yet, leave this file immediately. The next step must come from the current localhost response on that same artifact, usually `data.suggestedRepairOps[]`, `POST /api/scripts/{name}/repair/authoring-quality`, or the first real `POST /api/scripts/{name}/ops` batch. Do not mine examples for the first scaffold on a blank or source-only exact artifact. Use this file only after a concrete contract error or after at least one real mutation already exists on that same artifact.

All examples assume you follow the safe workflow:
- `GET /api/scripts/{name}/explain`
- build an `ops` plan
- `POST /api/scripts/{name}/validate`
- `POST /api/scripts/{name}/ops`
- `POST /api/scripts/{name}/build`
- `GET /api/scripts/{name}/messages`


This is part: Trading & Patterns.
See also: AGENTS-Examples-Quick.md and AGENTS-Examples.md (index).

## 5) Optimization setup and "stuck job" handling
1) Set ranges with `SetOptimizationRange` (must include `paramInvariantName` and `optimDataType`).
2) Start the job and poll status.
3) If `completedIterations` stays 0 and results are empty for too long, cancel and re-check build/logs.

Example ranges:
```json
{
  "ops": [
    { "op": "SetOptimizationRange", "blockId": "SMA1", "paramInvariantName": "Period", "optimDataType": "IntOptimData", "value": "20", "min": "10", "max": "100", "step": "5" }
  ]
}
```
Cancel:
```
POST /api/scripts/optimizations/{jobId}/cancel
```

---


## 6) SMA crossover entry (correct container selection)
Key point: multi-input handlers must be added as `TwoOrMoreInputsItem`.

```json
{
  "ops": [
    { "op": "AddBlock", "blockId": "Close1", "typeName": "Close", "blockType": "ConverterItem" },
    { "op": "AddBlock", "blockId": "SMAFast", "typeName": "SMA", "blockType": "ConverterItem" },
    { "op": "AddBlock", "blockId": "SMASlow", "typeName": "SMA", "blockType": "ConverterItem" },
    { "op": "AddBlock", "blockId": "CrossOver1", "typeName": "CrossOver", "blockType": "TwoOrMoreInputsItem" },
    { "op": "AddBlock", "blockId": "OpenLong", "blockType": "OpenPositionByMarketItem", "params": { "Long": "true", "Shares": "1" } },

    { "op": "SetParam", "blockId": "SMAFast", "paramName": "Period", "value": "20" },
    { "op": "SetParam", "blockId": "SMASlow", "paramName": "Period", "value": "50" },

    { "op": "Connect", "fromBlockId": "Source1", "fromPort": "Out", "toBlockId": "Close1", "toPort": 0 },
    { "op": "Connect", "fromBlockId": "Close1", "fromPort": "Out", "toBlockId": "SMAFast", "toPort": 0 },
    { "op": "Connect", "fromBlockId": "Close1", "fromPort": "Out", "toBlockId": "SMASlow", "toPort": 0 },
    { "op": "Connect", "fromBlockId": "SMASlow", "fromPort": "Out", "toBlockId": "CrossOver1", "toPort": 0 },
    { "op": "Connect", "fromBlockId": "SMAFast", "fromPort": "Out", "toBlockId": "CrossOver1", "toPort": 1 },

    { "op": "Connect", "fromBlockId": "Source1", "fromPort": "Out", "toBlockId": "OpenLong", "toPort": 0 },
    { "op": "Connect", "fromBlockId": "CrossOver1", "fromPort": "Out", "toBlockId": "OpenLong", "toPort": 1 }
  ]
}
```

Notes:
- Default policy for numeric indicator/constant knobs in new strategies is `SetOptimizationRange` with `value/min/max/step`.
- `SetParam` is for explicitly fixed/non-optimizable parameters.
- If you plan to optimize `Period`, do **not** use `SetParam` for it. Use `SetOptimizationRange` instead (it stores the value/range in mappings and removes the constant node automatically).
- For `min/max/step`, prefer seeding from handler metadata (`GET /api/handlers/SMA`) instead of hard-coding ranges.

---


## 4) Limit entry + dynamic size (pattern from `XchAtrS241124m.xml`)
This script family uses:
- `OpenPositionAtLimitItem` for entry
- `PositionSharesByBar` and `BalancedPrice` handlers for position state
- formulas for `MaxSz`, `StartSizePct`, `SizeStep`, etc.
- `ChangePositionAtPriceItem` / `ClosePositionAtPriceItem` / `ClosePositionByStopItem` for management

### 4.1 Create constants (ConstGen) and a size formula
Assume you want:
- `MaxDepo` (deposit)
- `MarginLevel` (leverage/margin)
- `MaxSz = Round(MaxDepo * MarginLevel / Close, 1)` (as in script)
- `Shares = Round(MaxSz * StartSizePct / 100, 1)`

Recipe:
1) Add constants as `ConstGen` handler blocks (`ConverterItem`, `typeName="ConstGen"`).
2) Add `Close` handler.
3) Add `DoubleCustomHandlerItem` formulas.

Ops sketch:
```json
{
  "ops": [
    { "op": "AddBlock", "blockId": "Close1", "typeName": "Close", "blockType": "ConverterItem" },
    { "op": "Connect", "fromBlockId": "Source1", "fromPort": "Out", "toBlockId": "Close1", "toPort": 0 },

    { "op": "AddBlock", "blockId": "MaxDepo", "typeName": "ConstGen", "blockType": "ConverterItem" },
    { "op": "SetParam", "blockId": "MaxDepo", "paramName": "Value", "value": "1000" },

    { "op": "AddBlock", "blockId": "MarginLevel", "typeName": "ConstGen", "blockType": "ConverterItem" },
    { "op": "SetParam", "blockId": "MarginLevel", "paramName": "Value", "value": "5" },

    { "op": "AddBlock", "blockId": "StartSizePct", "typeName": "ConstGen", "blockType": "ConverterItem" },
    { "op": "SetParam", "blockId": "StartSizePct", "paramName": "Value", "value": "10" },

    { "op": "AddBlock", "blockId": "MaxSz", "blockType": "DoubleCustomHandlerItem", "params": { "Expression": "Math.Round(MaxDepo*MarginLevel/Close1, 1)", "StartIndex": "0" } },
    { "op": "AddBlock", "blockId": "Shares1", "blockType": "DoubleCustomHandlerItem", "params": { "Expression": "Math.Round(MaxSz*StartSizePct/100, 1)", "StartIndex": "0" } }
  ]
}
```

Notes:
- `ConstGen` parameter name can differ by implementation (some versions use `Value`, others different). Always confirm via `/api/handlers/ConstGen`.
- In formulas, reference block *CodeName* (which equals `blockId` only for blocks created via API).

### 4.2 Use computed shares for entry
Connect `Shares1.Out` into `OpenPositionByMarketItem` input 2 or use it in limit entry input 3.

---


## 5) ValueUpdater as a counter (pattern from `MCB_vSPR_0.1_receiver.xml`)
Real scripts use ValueUpdater to count events like "how many times position size changed".

Pattern:
- `Counter` is a `ValueUpdater`.
- `Counter` input double is `Counter + 1` (formula).
- update condition is `EventOccurred`.
- clear condition is `ResetEvent` (e.g. position closed).

Ops sketch:
```json
{
  "ops": [
    { "op": "AddBlock", "blockId": "Counter", "blockType": "ValueUpdater", "params": { "StartFrom": "0", "ExecutionOrder": "Common" } },
    { "op": "AddBlock", "blockId": "CounterPlusOne", "blockType": "DoubleCustomHandlerItem", "params": { "Expression": "Counter + 1", "StartIndex": "0" } },
    { "op": "Connect", "fromBlockId": "CounterPlusOne", "fromPort": "Out", "toBlockId": "Counter", "toPort": 0 },
    { "op": "Connect", "fromBlockId": "EventOccurred", "fromPort": "Out", "toBlockId": "Counter", "toPort": 1 },
    { "op": "Connect", "fromBlockId": "ResetEvent", "fromPort": "Out", "toBlockId": "Counter", "toPort": 2 }
  ]
}
```

Note:
- `NotClear=false` is intentional in this position-driven pattern because the counter is explicitly cleared by `PosClosed`.
- Outside position context, default to `NotClear=true`.

---


## 6) A complex boolean gate (pattern from `MartinChangeLS_Optim.xml`)
Real strategies often build a single "gate" condition that combines many requirements:
- indicator condition(s)
- time/session filters
- receiver connection flags
- drawdown blocks
- "only if..." switches

In practice, this is best implemented as `BoolCustomHandlerItem`:
`Expression = A && B && C && !D`

Agent guidance:
- Use one formula for the final gate, and keep intermediate booleans as separate named blocks, to make debugging easier.
- Give these blocks stable, code-friendly `blockId` / `CodeName`.

---


## 7) Chart output wiring (via `GraphLink` ops)
In XML, chart outputs are represented by `<GraphLink ...><Data>...</Data></GraphLink>`.

Use cases:
- plot candles for a `SecuritySourceItem` / `TradableSecuritySourceItem`
- plot an indicator on a pane (line/histogram/etc)

Typical ops sequence:
1) Ensure a graph pane exists (`AddPane`).
2) Add a graph link (`AddGraphLink`) from a block to that pane.

Example (add pane + plot candles from `Source1` on the right axis):
```json
{
  "ops": [
    { "op": "AddPane", "paneKey": "Main", "category": "GraphPane", "params": { "Order": "0", "IsVisible": "true" } },
    {
      "op": "AddGraphLink",
      "fromBlockId": "Source1",
      "toBlockId": "Main",
      "fromPort": "Out",
      "toPortName": "RIGHT",
      "category": "ChartCandleLink",
      "dataXml": "<GraphData ListStyle=\"LINE\" CandleStyle=\"BAR_CANDLE\" LineStyle=\"SOLID\" Color=\"255\" AltColor=\"255\" Opacity=\"0\" HideLastValue=\"false\" Thickness=\"1\" PaneSide=\"RIGHT\" Visible=\"true\" ShowTrades=\"true\" ShowPositionStop=\"true\" ShowPositionText=\"true\" ShowPositionIcon=\"true\" />"
    }
  ]
}
```

Example (plot a DOUBLE series as a line on the same pane):
```json
{
  "ops": [
    {
      "op": "AddGraphLink",
      "fromBlockId": "HH100",
      "toBlockId": "Main",
      "fromPort": "Out",
      "toPortName": "RIGHT",
      "category": "ChartLineLink",
      "dataXml": "<GraphData ListStyle=\"LINE\" LineStyle=\"SOLID\" Color=\"-65536\" AltColor=\"-65536\" Opacity=\"0\" HideLastValue=\"false\" Thickness=\"1\" AltThickness=\"1\" PaneSide=\"RIGHT\" Visible=\"true\" Autoscaling=\"true\"><Points /></GraphData>"
    }
  ]
}
```

Notes:
- Prefer `ChartLineLink` for line series (DOUBLE). `ChartLink` may not be recognized consistently.
- If `/api/scripts/{name}/charts/info` returns 409 "no chart windows produced" but you did add panes/graph links, verify your source mapping (`SetSourceMapping`) includes a non-empty `visualTypeName` in `GET /api/scripts/{name}/json` -> `mappings.sources.visualTypeName`.

---


## 8) ATR-based SL/TP management using `EntryPrice` (pattern from `scripts/PerfomanceTest.xml`)
Goal: open by market, then attach SL and TP levels derived from entry price and ATR.

Key building blocks:
- `EntryPrice` handler (`typeName="EntryPrice"`, `blockType="ConverterItem"`) converts `POSITION -> DOUBLE` (price series).
- `AverageTrueRange` (`typeName="AverageTrueRange"`) takes `SECURITY -> DOUBLE` (ATR series).
- SL/TP are best modeled as `DoubleCustomHandlerItem` formulas.

Recipe outline:
1) Build a trend signal (example: EMA rising).
2) Add a time/session filter (example: `Time < 234400`).
3) Combine with `And` into a single entry gate.
4) Open a position by market.
5) Build SL/TP prices from `EntryPrice` and `ATR`.
6) Close by stop/profit using those computed prices.

```json
{
  "ops": [
    { "op": "AddBlock", "blockId": "Close1", "typeName": "Close", "blockType": "ConverterItem" },
    { "op": "Connect", "fromBlockId": "Source1", "fromPort": "Out", "toBlockId": "Close1", "toPort": 0 },

    { "op": "AddBlock", "blockId": "EMA1", "typeName": "EMA", "blockType": "ConverterItem" },
    { "op": "SetParam", "blockId": "EMA1", "paramName": "Period", "value": "20" },
    { "op": "Connect", "fromBlockId": "Close1", "fromPort": "Out", "toBlockId": "EMA1", "toPort": 0 },

    { "op": "AddBlock", "blockId": "UpTrend", "blockType": "BoolCustomHandlerItem", "params": { "Expression": "EMA1 > EMA1[-1]", "StartIndex": "1" } },
    { "op": "AddBlock", "blockId": "Time1", "typeName": "Time", "blockType": "ConverterItem" },
    { "op": "Connect", "fromBlockId": "Source1", "fromPort": "Out", "toBlockId": "Time1", "toPort": 0 },
    { "op": "AddBlock", "blockId": "AntiGap", "blockType": "BoolCustomHandlerItem", "params": { "Expression": "Time1 < 234400", "StartIndex": "0" } },

    { "op": "AddBlock", "blockId": "EntryGate", "typeName": "And", "blockType": "TwoOrMoreInputsItem" },
    { "op": "Connect", "fromBlockId": "UpTrend", "fromPort": "Out", "toBlockId": "EntryGate", "toPort": 0 },
    { "op": "Connect", "fromBlockId": "AntiGap", "fromPort": "Out", "toBlockId": "EntryGate", "toPort": 1 },

    { "op": "AddBlock", "blockId": "OpenLong", "blockType": "OpenPositionByMarketItem", "params": { "Long": "true", "Shares": "1" } },
    { "op": "RenameBlock", "blockId": "OpenLong", "visualName": "Entry Long (ATR)" },
    { "op": "ConnectByInputName", "fromBlockId": "Source1", "toBlockId": "OpenLong", "toInputName": "Src" },
    { "op": "ConnectByInputName", "fromBlockId": "EntryGate", "toBlockId": "OpenLong", "toInputName": "Eq" },

    { "op": "AddBlock", "blockId": "ATR1", "typeName": "AverageTrueRange", "blockType": "ConverterItem" },
    { "op": "SetParam", "blockId": "ATR1", "paramName": "Period", "value": "20" },
    { "op": "Connect", "fromBlockId": "Source1", "fromPort": "Out", "toBlockId": "ATR1", "toPort": 0 },

    { "op": "AddBlock", "blockId": "EntryPrice1", "typeName": "EntryPrice", "blockType": "ConverterItem" },
    { "op": "Connect", "fromBlockId": "OpenLong", "fromPort": "Out", "toBlockId": "EntryPrice1", "toPort": 0 },

    { "op": "AddBlock", "blockId": "kAtr", "typeName": "ConstGen", "blockType": "ConverterItem" },
    { "op": "SetParam", "blockId": "kAtr", "paramName": "Value", "value": "2" },

    { "op": "AddBlock", "blockId": "SL", "blockType": "DoubleCustomHandlerItem", "params": { "Expression": "EntryPrice1 - ATR1 * kAtr", "StartIndex": "0" } },
    { "op": "AddBlock", "blockId": "TP", "blockType": "DoubleCustomHandlerItem", "params": { "Expression": "EntryPrice1 + ATR1 * kAtr", "StartIndex": "0" } },

    { "op": "AddBlock", "blockId": "Always", "blockType": "BoolCustomHandlerItem", "params": { "Expression": "true", "StartIndex": "0" } },

    { "op": "AddBlock", "blockId": "ExitSL", "blockType": "ClosePositionByStopItem", "params": { "Slippage": "0", "AddOpenName": "false" } },
    { "op": "ConnectByInputName", "fromBlockId": "OpenLong", "toBlockId": "ExitSL", "toInputName": "Pos" },
    { "op": "ConnectByInputName", "fromBlockId": "Always", "toBlockId": "ExitSL", "toInputName": "Eq" },
    { "op": "ConnectByInputName", "fromBlockId": "SL", "toBlockId": "ExitSL", "toInputName": "Prc" },

    { "op": "AddBlock", "blockId": "ExitTP", "blockType": "ClosePositionByProfitItem", "params": { "Slippage": "0", "AddOpenName": "false" } },
    { "op": "ConnectByInputName", "fromBlockId": "OpenLong", "toBlockId": "ExitTP", "toInputName": "Pos" },
    { "op": "ConnectByInputName", "fromBlockId": "Always", "toBlockId": "ExitTP", "toInputName": "Eq" },
    { "op": "ConnectByInputName", "fromBlockId": "TP", "toBlockId": "ExitTP", "toInputName": "Prc" }
  ]
}
```

Notes:
- Many legacy scripts omit `Eq` on open/close blocks; this example wires it explicitly to make intent clear.
- Use `StartIndex=1` for formulas like `EMA1[-1]` to avoid out-of-range on bar 0.

---


## 9) Hi/Lo channel limit entry + scale-in steps + exit at target (pattern from `scripts/KishuHiLo2311.xml`)
Goal: place a limit entry at the rolling Lowest(N), optionally add size at stepped prices, and exit at rolling Highest(N).

```json
{
  "ops": [
    { "op": "AddBlock", "blockId": "Close1", "typeName": "Close", "blockType": "ConverterItem" },
    { "op": "Connect", "fromBlockId": "Source1", "fromPort": "Out", "toBlockId": "Close1", "toPort": 0 },

    { "op": "AddBlock", "blockId": "Lowest1", "typeName": "Lowest", "blockType": "ConverterItem" },
    { "op": "SetParam", "blockId": "Lowest1", "paramName": "Period", "value": "50" },
    { "op": "Connect", "fromBlockId": "Close1", "fromPort": "Out", "toBlockId": "Lowest1", "toPort": 0 },

    { "op": "AddBlock", "blockId": "Highest1", "typeName": "Highest", "blockType": "ConverterItem" },
    { "op": "SetParam", "blockId": "Highest1", "paramName": "Period", "value": "50" },
    { "op": "Connect", "fromBlockId": "Close1", "fromPort": "Out", "toBlockId": "Highest1", "toPort": 0 },

    { "op": "AddBlock", "blockId": "MaxDepo", "typeName": "ConstGen", "blockType": "ConverterItem" },
    { "op": "SetParam", "blockId": "MaxDepo", "paramName": "Value", "value": "1000" },
    { "op": "AddBlock", "blockId": "MarginLevel", "typeName": "ConstGen", "blockType": "ConverterItem" },
    { "op": "SetParam", "blockId": "MarginLevel", "paramName": "Value", "value": "5" },
    { "op": "AddBlock", "blockId": "StartSizePct", "typeName": "ConstGen", "blockType": "ConverterItem" },
    { "op": "SetParam", "blockId": "StartSizePct", "paramName": "Value", "value": "10" },
    { "op": "AddBlock", "blockId": "SizeStep", "typeName": "ConstGen", "blockType": "ConverterItem" },
    { "op": "SetParam", "blockId": "SizeStep", "paramName": "Value", "value": "1.5" },
    { "op": "AddBlock", "blockId": "PriceStepPct", "typeName": "ConstGen", "blockType": "ConverterItem" },
    { "op": "SetParam", "blockId": "PriceStepPct", "paramName": "Value", "value": "0.2" },

    { "op": "AddBlock", "blockId": "MaxSz", "blockType": "DoubleCustomHandlerItem", "params": { "Expression": "Math.Round(MaxDepo*MarginLevel/Close1, 1)", "StartIndex": "0" } },
    { "op": "AddBlock", "blockId": "FirstSz", "blockType": "DoubleCustomHandlerItem", "params": { "Expression": "Math.Round(MaxSz*StartSizePct/100, 1)", "StartIndex": "0" } },

    { "op": "AddBlock", "blockId": "Always", "blockType": "BoolCustomHandlerItem", "params": { "Expression": "true", "StartIndex": "0" } },

    { "op": "AddBlock", "blockId": "OpenLimit", "blockType": "OpenPositionAtLimitItem", "params": { "Long": "true", "Shares": "1" } },
    { "op": "RenameBlock", "blockId": "OpenLimit", "visualName": "Entry Long (HiLo)" },
    { "op": "ConnectByInputName", "fromBlockId": "Source1", "toBlockId": "OpenLimit", "toInputName": "Src" },
    { "op": "ConnectByInputName", "fromBlockId": "Always", "toBlockId": "OpenLimit", "toInputName": "Eq" },
    { "op": "ConnectByInputName", "fromBlockId": "Lowest1", "toBlockId": "OpenLimit", "toInputName": "Prc" },
    { "op": "ConnectByInputName", "fromBlockId": "FirstSz", "toBlockId": "OpenLimit", "toInputName": "Shares" },

    { "op": "AddBlock", "blockId": "PosSz", "typeName": "PositionSharesByBar", "blockType": "ConverterItem" },
    { "op": "Connect", "fromBlockId": "OpenLimit", "fromPort": "Out", "toBlockId": "PosSz", "toPort": 0 },

    { "op": "AddBlock", "blockId": "NextPrc", "blockType": "DoubleCustomHandlerItem", "params": { "Expression": "Lowest1*(1-PriceStepPct/100)", "StartIndex": "0" } },
    { "op": "AddBlock", "blockId": "NextSz", "blockType": "DoubleCustomHandlerItem", "params": { "Expression": "Math.Round(PosSz*SizeStep, 1)", "StartIndex": "0" } },
    { "op": "AddBlock", "blockId": "CanAdd", "blockType": "BoolCustomHandlerItem", "params": { "Expression": "PosSz > 0 && Close1 < Lowest1", "StartIndex": "0" } },

    { "op": "AddBlock", "blockId": "Change1", "blockType": "ChangePositionAtPriceItem", "params": { "AddOpenName": "false" } },
    { "op": "ConnectByInputName", "fromBlockId": "OpenLimit", "toBlockId": "Change1", "toInputName": "Pos" },
    { "op": "ConnectByInputName", "fromBlockId": "CanAdd", "toBlockId": "Change1", "toInputName": "Eq" },
    { "op": "ConnectByInputName", "fromBlockId": "NextSz", "toBlockId": "Change1", "toInputName": "Shares" },
    { "op": "ConnectByInputName", "fromBlockId": "NextPrc", "toBlockId": "Change1", "toInputName": "Prc" },

    { "op": "AddBlock", "blockId": "Exit1", "blockType": "ClosePositionAtPriceItem", "params": { "AddOpenName": "false" } },
    { "op": "ConnectByInputName", "fromBlockId": "OpenLimit", "toBlockId": "Exit1", "toInputName": "Pos" },
    { "op": "ConnectByInputName", "fromBlockId": "Always", "toBlockId": "Exit1", "toInputName": "Eq" },
    { "op": "ConnectByInputName", "fromBlockId": "Highest1", "toBlockId": "Exit1", "toInputName": "Prc" }
  ]
}
```

Notes:
- `PositionSharesByBar` is the simplest way to "read current size" inside the graph for scale-in logic.
- For real money management, clamp `NextSz` by a computed maximum size (`MaxDepo*MarginLevel/price`), as in `scripts/KishuHiLo2311.xml`.

---


## 10) ATR-adjusted limit entry + pyramiding + trailing stop (pattern from `scripts/BinAptL230925m.xml`)
This script family combines:
- a computed limit entry price derived from `Close` and an ATR-like measure
- an add-on (pyramiding) condition when price moves further
- stop management by a trailing stop handler (often external)

Core formulas (as seen in the script):
- `lEntryPrc = Close * (1 - (AtrmCoef2 + Am)/100/AtrmCoef)`
- `long = Am < 1`
- `longAdd = Am < 1 && lEntryPrc < Prc`

Practical agent guidance:
- If a script uses an external handler (e.g. `Dron.Indicators.ATRM` / `Dron.Indicators.ATRTrailStop`), do NOT "recreate it" as a formula unless you are explicitly asked to replace it.
- Use `/api/handlers/search?q=ATRM` and `/api/handlers/search?q=ATRTrailStop` to confirm it exists in the current runtime, then wire it like any other handler.
- If the handler does not exist in the runtime, you must switch to a built-in alternative (e.g. `AverageTrueRange`) and clearly explain the functional difference.

### 10.1 External trailing stop available (wire it, do not rewrite)
If (and only if) the runtime exposes these handlers, the block wiring looks like this:
```json
{
  "ops": [
    { "op": "AddBlock", "blockId": "Close1", "typeName": "Close", "blockType": "ConverterItem" },
    { "op": "Connect", "fromBlockId": "Source1", "fromPort": "Out", "toBlockId": "Close1", "toPort": 0 },

    { "op": "AddBlock", "blockId": "Am", "typeName": "ATRM", "blockType": "ConverterItem" },
    { "op": "Connect", "fromBlockId": "Source1", "fromPort": "Out", "toBlockId": "Am", "toPort": 0 },

    { "op": "AddBlock", "blockId": "AtrmCoef", "typeName": "ConstGen", "blockType": "ConverterItem" },
    { "op": "SetParam", "blockId": "AtrmCoef", "paramName": "Value", "value": "1" },
    { "op": "AddBlock", "blockId": "AtrmCoef2", "typeName": "ConstGen", "blockType": "ConverterItem" },
    { "op": "SetParam", "blockId": "AtrmCoef2", "paramName": "Value", "value": "1" },

    { "op": "AddBlock", "blockId": "EntryPrc", "blockType": "DoubleCustomHandlerItem", "params": { "Expression": "Close1 * (1 - (AtrmCoef2 + Am)/100/AtrmCoef)", "StartIndex": "0" } },
    { "op": "AddBlock", "blockId": "LongGate", "blockType": "BoolCustomHandlerItem", "params": { "Expression": "Am < 1", "StartIndex": "0" } },

    { "op": "AddBlock", "blockId": "MaxDepo", "typeName": "ConstGen", "blockType": "ConverterItem" },
    { "op": "SetParam", "blockId": "MaxDepo", "paramName": "Value", "value": "1000" },
    { "op": "AddBlock", "blockId": "MarginLevel", "typeName": "ConstGen", "blockType": "ConverterItem" },
    { "op": "SetParam", "blockId": "MarginLevel", "paramName": "Value", "value": "5" },
    { "op": "AddBlock", "blockId": "StartSizePct", "typeName": "ConstGen", "blockType": "ConverterItem" },
    { "op": "SetParam", "blockId": "StartSizePct", "paramName": "Value", "value": "10" },
    { "op": "AddBlock", "blockId": "MaxSz", "blockType": "DoubleCustomHandlerItem", "params": { "Expression": "Math.Round(MaxDepo*MarginLevel/Close1, 1)", "StartIndex": "0" } },
    { "op": "AddBlock", "blockId": "FirstSz", "blockType": "DoubleCustomHandlerItem", "params": { "Expression": "Math.Round(MaxSz*StartSizePct/100, 1)", "StartIndex": "0" } },

    { "op": "AddBlock", "blockId": "OpenLimit", "blockType": "OpenPositionAtLimitItem", "params": { "Long": "true", "Shares": "1" } },
    { "op": "RenameBlock", "blockId": "OpenLimit", "visualName": "Entry Long (ATRM)" },
    { "op": "ConnectByInputName", "fromBlockId": "Source1", "toBlockId": "OpenLimit", "toInputName": "Src" },
    { "op": "ConnectByInputName", "fromBlockId": "LongGate", "toBlockId": "OpenLimit", "toInputName": "Eq" },
    { "op": "ConnectByInputName", "fromBlockId": "EntryPrc", "toBlockId": "OpenLimit", "toInputName": "Prc" },
    { "op": "ConnectByInputName", "fromBlockId": "FirstSz", "toBlockId": "OpenLimit", "toInputName": "Shares" },

    { "op": "AddBlock", "blockId": "Prc", "typeName": "BalancedPrice", "blockType": "ConverterItem" },
    { "op": "Connect", "fromBlockId": "OpenLimit", "fromPort": "Out", "toBlockId": "Prc", "toPort": 0 },

    { "op": "AddBlock", "blockId": "TrailStop", "typeName": "ATRTrailStop", "blockType": "ConverterItem" },
    { "op": "Connect", "fromBlockId": "OpenLimit", "fromPort": "Out", "toBlockId": "TrailStop", "toPort": 0 },

    { "op": "AddBlock", "blockId": "Always", "blockType": "BoolCustomHandlerItem", "params": { "Expression": "true", "StartIndex": "0" } },
    { "op": "AddBlock", "blockId": "ExitStop", "blockType": "ClosePositionByStopItem", "params": { "Slippage": "0", "AddOpenName": "false" } },
    { "op": "ConnectByInputName", "fromBlockId": "OpenLimit", "toBlockId": "ExitStop", "toInputName": "Pos" },
    { "op": "ConnectByInputName", "fromBlockId": "Always", "toBlockId": "ExitStop", "toInputName": "Eq" },
    { "op": "ConnectByInputName", "fromBlockId": "TrailStop", "toBlockId": "ExitStop", "toInputName": "Prc" }
  ]
}
```

### 10.2 Fallback (no external trailing stop) - ATR-based fixed stop instead
If the external trailing stop handler is unavailable, a minimal fallback is:
- compute `SL = EntryPrice - ATR*kStop`
- close by stop using that price

This is not a trailing stop; it is a fixed ATR stop from entry.

---


## 11) Martingale-style scaling with `ValueUpdater` counters + emergency exit (pattern from `scripts/MartinChangeLS_Optim.xml`)
This script shows three important ideas:
1) The engine can manage multiple independent positions per instrument at the same time (distinguished by SignalName).
2) `ValueUpdater` is used as stateful memory (counters, latches, remembered levels).
3) "Emergency exits" (close by market) are implemented as a separate close block with its own condition.

Minimal long-side pattern:
- `OpenPositionAtLimitItem` (entry)
- `ChangePositionAtPriceItem` (scale in/out)
- `ClosePositionByProfitItem` (take profit)
- `ClosePositionByMarketItem` (emergency exit)
- `ValueUpdater` (counter of changes)

Key note:
- Signal identity comes from the *open block's* `VisualName`. If you need two independent long positions on the same instrument, use two open blocks with different `VisualName`.

### 11.1 Minimal long-side scale-in with `ValueUpdater` counter
```json
{
  "ops": [
    { "op": "AddBlock", "blockId": "Close1", "typeName": "Close", "blockType": "ConverterItem" },
    { "op": "Connect", "fromBlockId": "Source1", "fromPort": "Out", "toBlockId": "Close1", "toPort": 0 },

    { "op": "AddBlock", "blockId": "Always", "blockType": "BoolCustomHandlerItem", "params": { "Expression": "true", "StartIndex": "0" } },

    { "op": "AddBlock", "blockId": "OpenLong", "blockType": "OpenPositionAtLimitItem", "params": { "Long": "true", "Shares": "1" } },
    { "op": "RenameBlock", "blockId": "OpenLong", "visualName": "Long_MCLS" },
    { "op": "ConnectByInputName", "fromBlockId": "Source1", "toBlockId": "OpenLong", "toInputName": "Src" },
    { "op": "ConnectByInputName", "fromBlockId": "Always", "toBlockId": "OpenLong", "toInputName": "Eq" },
    { "op": "ConnectByInputName", "fromBlockId": "Close1", "toBlockId": "OpenLong", "toInputName": "Prc" },

    { "op": "AddBlock", "blockId": "PosSz", "typeName": "PositionSharesByBar", "blockType": "ConverterItem" },
    { "op": "Connect", "fromBlockId": "OpenLong", "fromPort": "Out", "toBlockId": "PosSz", "toPort": 0 },

    { "op": "AddBlock", "blockId": "AddCount", "blockType": "ValueUpdater", "params": { "StartFrom": "0", "ExecutionOrder": "Common", "NotClear": "false" } },
    { "op": "AddBlock", "blockId": "AddCountPlusOne", "blockType": "DoubleCustomHandlerItem", "params": { "Expression": "AddCount + 1", "StartIndex": "0" } },
    { "op": "AddBlock", "blockId": "DidChange", "blockType": "BoolCustomHandlerItem", "params": { "Expression": "PosSz != PosSz[-1] && PosSz != 0", "StartIndex": "1" } },
    { "op": "AddBlock", "blockId": "PosClosed", "blockType": "BoolCustomHandlerItem", "params": { "Expression": "PosSz == 0", "StartIndex": "0" } },
    { "op": "Connect", "fromBlockId": "AddCountPlusOne", "fromPort": "Out", "toBlockId": "AddCount", "toPort": 0 },
    { "op": "Connect", "fromBlockId": "DidChange", "fromPort": "Out", "toBlockId": "AddCount", "toPort": 1 },
    { "op": "Connect", "fromBlockId": "PosClosed", "fromPort": "Out", "toBlockId": "AddCount", "toPort": 2 },

    { "op": "AddBlock", "blockId": "AvgOpen", "typeName": "BalancedPrice", "blockType": "ConverterItem" },
    { "op": "Connect", "fromBlockId": "OpenLong", "fromPort": "Out", "toBlockId": "AvgOpen", "toPort": 0 },

    { "op": "AddBlock", "blockId": "ProfitTargetPct", "typeName": "ConstGen", "blockType": "ConverterItem" },
    { "op": "SetParam", "blockId": "ProfitTargetPct", "paramName": "Value", "value": "0.2" },
    { "op": "AddBlock", "blockId": "TP", "blockType": "DoubleCustomHandlerItem", "params": { "Expression": "AvgOpen*(1 + ProfitTargetPct/100)", "StartIndex": "0" } },
    { "op": "AddBlock", "blockId": "ExitTP", "blockType": "ClosePositionByProfitItem", "params": { "Slippage": "0", "AddOpenName": "false" } },
    { "op": "ConnectByInputName", "fromBlockId": "OpenLong", "toBlockId": "ExitTP", "toInputName": "Pos" },
    { "op": "ConnectByInputName", "fromBlockId": "Always", "toBlockId": "ExitTP", "toInputName": "Eq" },
    { "op": "ConnectByInputName", "fromBlockId": "TP", "toBlockId": "ExitTP", "toInputName": "Prc" },

    { "op": "AddBlock", "blockId": "MaxLossPct", "typeName": "ConstGen", "blockType": "ConverterItem" },
    { "op": "SetParam", "blockId": "MaxLossPct", "paramName": "Value", "value": "1.0" },
    { "op": "AddBlock", "blockId": "PnlPct", "typeName": "ProfitPct", "blockType": "ConverterItem" },
    { "op": "Connect", "fromBlockId": "OpenLong", "fromPort": "Out", "toBlockId": "PnlPct", "toPort": 0 },
    { "op": "AddBlock", "blockId": "Emergency", "blockType": "BoolCustomHandlerItem", "params": { "Expression": "PnlPct < -MaxLossPct", "StartIndex": "0" } },
    { "op": "AddBlock", "blockId": "ExitDD", "blockType": "ClosePositionByMarketItem", "params": { "Execution": "Normal", "AddOpenName": "false" } },
    { "op": "ConnectByInputName", "fromBlockId": "OpenLong", "toBlockId": "ExitDD", "toInputName": "Pos" },
    { "op": "ConnectByInputName", "fromBlockId": "Emergency", "toBlockId": "ExitDD", "toInputName": "Eq" }
  ]
}
```

---


## 12) Organizing large graphs with `SubGraphKey` (pattern from `scripts/MartinChangeLS_Optim.xml`)
Real scripts set `Block/@SubGraphKey` heavily to keep the graph readable (e.g. "StartPosLong", "CounterPositionLong", "Parameters").

You can set it via ops:
```json
{
  "ops": [
    { "op": "SetBlockAttribute", "blockId": "OpenLong", "attributeName": "SubGraphKey", "attributeValue": "StartPosLong" },
    { "op": "SetBlockAttribute", "blockId": "ExitSL", "attributeName": "SubGraphKey", "attributeValue": "Risk" }
  ]
}
```

---


## 13) Parameter linking: one master period -> many indicators (pattern from `tests/LabView.Tests/Data/ftest1.xml`)
Goal: make several blocks share a single parameter value (e.g. a common `Period`) without manually updating each block.

This uses the template block `ParameterShareItem`:
- It has **two inputs**: master (index 0) and slave (index 1)
- It has **EditItem attributes**: `ParameterName1` (master param) and `ParameterName2` (slave param)
- It has **no output**

Example: link `SMA_Slow.Period` to `SMA_Fast.Period` so that changing the master period changes both.
```json
{
  "ops": [
    { "op": "AddBlock", "blockId": "SMA_Master", "typeName": "SMA", "blockType": "ConverterItem" },
    { "op": "AddBlock", "blockId": "SMA_Slave", "typeName": "SMA", "blockType": "ConverterItem" },

    { "op": "SetParam", "blockId": "SMA_Master", "paramName": "Period", "value": "50" },

    { "op": "AddBlock", "blockId": "LinkPeriod", "blockType": "ParameterShareItem" },
    { "op": "SetEditItemAttribute", "blockId": "LinkPeriod", "attributeName": "ParameterName1", "attributeValue": "Period" },
    { "op": "SetEditItemAttribute", "blockId": "LinkPeriod", "attributeName": "ParameterName2", "attributeValue": "Period" },

    { "op": "Connect", "fromBlockId": "SMA_Master", "fromPort": "ControlOut", "toBlockId": "LinkPeriod", "toPort": 0 },
    { "op": "Connect", "fromBlockId": "SMA_Slave", "fromPort": "ControlOut", "toBlockId": "LinkPeriod", "toPort": 1 }
  ]
}
```

Notes:
- The link affects code generation: when the slave's `Period` is requested, it is read from the master.
- Always use `fromPort="ControlOut"` for parameter-linking blocks (`ParameterShareItem`, `OneToManyParametersShareItem`). These are not data-flow links.
- You can chain many `ParameterShareItem` blocks, or (if/when used) use `OneToManyParametersShareItem` for one master and many slaves.

---


## 14) "How many bars back do we need?" using `BarsCountForValuesSumHandler`
Goal: compute a dynamic "lookback length" based on "sum of last values >= threshold".

`BarsCountForValuesSumHandler` takes a DOUBLE series and returns a DOUBLE series:
- output at bar `i` is the smallest `k` such that `sum(values[i] + ... + values[i-k+1]) >= ValuesSum`
- returns `0` if never reached

Concrete example: "how many bars back until total volume reaches 10,000?"
```json
{
  "ops": [
    { "op": "AddBlock", "blockId": "Volume1", "typeName": "Volume", "blockType": "ConverterItem" },
    { "op": "Connect", "fromBlockId": "Source1", "fromPort": "Out", "toBlockId": "Volume1", "toPort": 0 },

    { "op": "AddBlock", "blockId": "BarsForVol", "typeName": "BarsCountForValuesSumHandler", "blockType": "ConverterItem" },
    { "op": "SetParam", "blockId": "BarsForVol", "paramName": "ValuesSum", "value": "10000" },
    { "op": "Connect", "fromBlockId": "Volume1", "fromPort": "Out", "toBlockId": "BarsForVol", "toPort": 0 }
  ]
}
```

Notes:
- The output is a DOUBLE but semantically is an integer count; cast/round in formulas when needed.
- This is useful to drive adaptive logic (but do not assume every handler accepts dynamic period; most period-based handlers require an integer parameter, not a series).

---


## 15) Timeframe resets: cumulative sum per bucket using `SumForTimeFrameHandler`
Goal: compute a cumulative sum that resets at timeframe boundaries (e.g. per hour/day/week).

`SumForTimeFrameHandler`:
- uses the script's first security bar timestamps
- resets the running sum when the bar time crosses a timeframe boundary

Example: per-hour cumulative volume.
```json
{
  "ops": [
    { "op": "AddBlock", "blockId": "Volume1", "typeName": "Volume", "blockType": "ConverterItem" },
    { "op": "Connect", "fromBlockId": "Source1", "fromPort": "Out", "toBlockId": "Volume1", "toPort": 0 },

    { "op": "AddBlock", "blockId": "VolPerHour", "typeName": "SumForTimeFrameHandler", "blockType": "ConverterItem" },
    { "op": "SetParam", "blockId": "VolPerHour", "paramName": "TimeFrame", "value": "0.01:00:00" },
    { "op": "Connect", "fromBlockId": "Volume1", "fromPort": "Out", "toBlockId": "VolPerHour", "toPort": 0 }
  ]
}
```

---


## 16) Two independent positions on the same instrument (SignalName discipline)
Goal: run two long strategies in parallel on the same instrument without them interfering.

Key idea:
- Each open block uses its VisualName to derive a signal name.
- Close/change blocks must target the intended signal name. The reliable approach is:
  - set `AddOpenName=true` on close blocks
  - set stable VisualNames for both open and close blocks

Minimal pattern:
```json
{
  "ops": [
    { "op": "AddBlock", "blockId": "Always", "blockType": "BoolCustomHandlerItem", "params": { "Expression": "true", "StartIndex": "0" } },

    { "op": "AddBlock", "blockId": "OpenA", "blockType": "OpenPositionByMarketItem", "params": { "Long": "true", "Shares": "1", "Execution": "Normal" } },
    { "op": "RenameBlock", "blockId": "OpenA", "visualName": "Entry A" },
    { "op": "ConnectByInputName", "fromBlockId": "Source1", "toBlockId": "OpenA", "toInputName": "Src" },
    { "op": "ConnectByInputName", "fromBlockId": "Always", "toBlockId": "OpenA", "toInputName": "Eq" },

    { "op": "AddBlock", "blockId": "OpenB", "blockType": "OpenPositionByMarketItem", "params": { "Long": "true", "Shares": "1", "Execution": "Normal" } },
    { "op": "RenameBlock", "blockId": "OpenB", "visualName": "Entry B" },
    { "op": "ConnectByInputName", "fromBlockId": "Source1", "toBlockId": "OpenB", "toInputName": "Src" },
    { "op": "ConnectByInputName", "fromBlockId": "Always", "toBlockId": "OpenB", "toInputName": "Eq" },

    { "op": "AddBlock", "blockId": "ExitAny", "blockType": "BoolCustomHandlerItem", "params": { "Expression": "false", "StartIndex": "0" } },

    { "op": "AddBlock", "blockId": "CloseA", "blockType": "ClosePositionByMarketItem", "params": { "Execution": "Normal", "AddOpenName": "true" } },
    { "op": "RenameBlock", "blockId": "CloseA", "visualName": "Exit A" },
    { "op": "ConnectByInputName", "fromBlockId": "OpenA", "toBlockId": "CloseA", "toInputName": "Pos" },
    { "op": "ConnectByInputName", "fromBlockId": "ExitAny", "toBlockId": "CloseA", "toInputName": "Eq" },

    { "op": "AddBlock", "blockId": "CloseB", "blockType": "ClosePositionByMarketItem", "params": { "Execution": "Normal", "AddOpenName": "true" } },
    { "op": "RenameBlock", "blockId": "CloseB", "visualName": "Exit B" },
    { "op": "ConnectByInputName", "fromBlockId": "OpenB", "toBlockId": "CloseB", "toInputName": "Pos" },
    { "op": "ConnectByInputName", "fromBlockId": "ExitAny", "toBlockId": "CloseB", "toInputName": "Eq" }
  ]
}
```

---


## 17) Breakout with Highest/Lowest + optimization ranges (pattern from `scripts/KishuHiLo2311.xml`)
Goal: a simple breakout system that can be optimized over lookback periods.

Core idea:
- Compute `Highest(High, Period)` and `Lowest(Low, Period)` (or use `Highest(Close, Period)` / `Lowest(Close, Period)` depending on your rule).
- Enter when `Close` crosses above `Highest`.
- Exit (or stop) when `Close` crosses below `Lowest`.

Minimal op outline (single long position):
```json
{
  "ops": [
    { "op": "AddBlock", "blockId": "Src", "blockType": "TradableSecuritySourceItem", "category": "TradableSecurity" },
    { "op": "SetSourceMapping", "blockId": "Src", "dataSourceName": "test", "securityId": "TEST.SEC", "isOption": false },

    { "op": "AddBlock", "blockId": "Close1", "typeName": "Close", "blockType": "ConverterItem" },
    { "op": "AddBlock", "blockId": "High1", "typeName": "High", "blockType": "ConverterItem" },
    { "op": "AddBlock", "blockId": "Low1", "typeName": "Low", "blockType": "ConverterItem" },

    { "op": "Connect", "fromBlockId": "Src", "toBlockId": "Close1", "toPort": 0 },
    { "op": "Connect", "fromBlockId": "Src", "toBlockId": "High1", "toPort": 0 },
    { "op": "Connect", "fromBlockId": "Src", "toBlockId": "Low1", "toPort": 0 },

    { "op": "AddBlock", "blockId": "Hi", "typeName": "Highest", "blockType": "ConverterItem" },
    { "op": "SetParam", "blockId": "Hi", "paramName": "Period", "value": "35" },
    { "op": "Connect", "fromBlockId": "High1", "toBlockId": "Hi", "toPort": 0 },

    { "op": "AddBlock", "blockId": "Lo", "typeName": "Lowest", "blockType": "ConverterItem" },
    { "op": "SetParam", "blockId": "Lo", "paramName": "Period", "value": "60" },
    { "op": "Connect", "fromBlockId": "Low1", "toBlockId": "Lo", "toPort": 0 },

    { "op": "AddBlock", "blockId": "Enter", "blockType": "BoolCustomHandlerItem", "params": { "Expression": "Close1>Hi", "StartIndex": "0" } },
    { "op": "AddBlock", "blockId": "Exit", "blockType": "BoolCustomHandlerItem", "params": { "Expression": "Close1<Lo", "StartIndex": "0" } },

    { "op": "AddBlock", "blockId": "OpenL", "blockType": "OpenPositionByMarketItem", "params": { "Long": "true", "Shares": "1", "Execution": "Normal" } },
    { "op": "Connect", "fromBlockId": "Src", "toBlockId": "OpenL", "toPort": 0 },
    { "op": "Connect", "fromBlockId": "Enter", "toBlockId": "OpenL", "toPort": 1 },

    { "op": "AddBlock", "blockId": "CloseL", "blockType": "ClosePositionByMarketItem", "params": { "AddOpenName": "true", "Execution": "Normal" } },
    { "op": "Connect", "fromBlockId": "OpenL", "toBlockId": "CloseL", "toPort": 0 },
    { "op": "Connect", "fromBlockId": "Exit", "toBlockId": "CloseL", "toPort": 1 }
  ]
}
```

Make periods optimizable:
```json
{
  "ops": [
    { "op": "SetOptimizationRange", "blockId": "Hi", "paramInvariantName": "Period", "optimDataType": "IntOptimData", "value": "35", "min": "10", "max": "150", "step": "5" },
    { "op": "SetOptimizationRange", "blockId": "Lo", "paramInvariantName": "Period", "optimDataType": "IntOptimData", "value": "60", "min": "10", "max": "150", "step": "5" }
  ]
}
```

---


## 19) External/3rd-party handlers inside scripts (pattern from `scripts/BinAptL230925m.xml`)
Some scripts reference handlers from assemblies that are not part of TSLab core (example: `Dron.Indicators.ATRM, Dron.Indicators`).

Agent guidance:
- `/api/handlers` only lists handlers that are loaded into the current Web API process.
- If a script contains a `HandlerTypeName` from an unknown assembly, you can still *inspect* and *rewire* it, but you may not be able to *create* such a block by `typeName` unless the assembly is loaded and registered.
- Prefer replacing external indicators with built-in equivalents when possible, or ask the user to install/load that handler assembly.

---


## 20) Subgraphs/groups for readability (pattern from `scripts/PerfomanceTest.xml`)
Large scripts often create "Group" items (visual only) and then assign `Block/@SubGraphKey` on blocks to organize the canvas.

Important:
- `Group` blocks typically have `Category="Group"` and empty `TypeName`. They are **not required** for compilation/execution.
- The operational feature is `SubGraphKey` on normal blocks.

Minimal usage:
```json
{
  "ops": [
    { "op": "SetBlockAttribute", "blockId": "OpenLong", "attributeName": "SubGraphKey", "attributeValue": "Signals" },
    { "op": "SetBlockAttribute", "blockId": "CloseLong", "attributeName": "SubGraphKey", "attributeValue": "Risk" }
  ]
}
```


