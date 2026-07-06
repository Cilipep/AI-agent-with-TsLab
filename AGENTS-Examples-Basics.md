# Examples & Recipes: Editing TSLab Scripts via Web API `ops`

This file contains concrete "cookbook" scenarios. It is written for agent authors and humans designing tasks for the agent.

Do not use this file for the first graph-design pass on a blank or source-only exact artifact. Before the first real `POST /api/scripts/{name}/ops` batch, stay on the current localhost response, the current artifact, and the minimal fast-path docs. Use examples only after a concrete contract error or after at least one real mutation already exists on that same artifact.

All examples assume you follow the safe workflow:
- `GET /api/scripts/{name}/explain`
- build an `ops` plan
- `POST /api/scripts/{name}/validate`
- `POST /api/scripts/{name}/ops`
- `POST /api/scripts/{name}/build`
- `GET /api/scripts/{name}/messages`


This is part: Basics.
See also: AGENTS-Examples-Quick.md and AGENTS-Examples.md (index).

## Hard rules (for weak/"dumb" models)
- TSLab scripts are server entities; do **not** edit local files unless the user gives a file path.
- Always use `/api/scripts/{name}/explain` to get `blockId` and `CodeName` (never guess).
- Formulas use **CodeName**, not `blockId`.
- Use UTF-8 for ops bodies that contain non-ASCII block IDs.
- Apply ops in small batches and validate/build after edits.


## Context note (large file)
This cookbook is large. For small-context models:
- load only the **one** section you need by heading,
- or use `AGENTS-Examples-Quick.md` first.

---


## 1) Working with scripts where `blockId != CodeName`
Many existing scripts use `EditItem/@CodeName = var0/var1/...` and `Block/@Key` is a human name (often localized or non-ASCII).

Agent rules:
1) Use `blockId` for `Connect/Disconnect`.
2) Use `CodeName` in formula `Expression`.
3) Do not assume that the open/close blocks have CodeName identical to Key.

Concrete example (from `scripts/XchAtrS241124m.xml`):
- `Block Key="Source1"` but `CodeName="var1"`.
If you create a formula that needs "source close", do NOT reference `Source1` in `Expression`. You reference the CodeName of the block that provides the series (e.g. a `Close` handler with `CodeName="Close"`).

Practical tactic:
- When adding new blocks, choose English/ASCII `blockId` so CodeName becomes usable in expressions without escaping.

---


## 2) Minimal "open by market" strategy skeleton
Goal: open a long position when a boolean signal is true.

Blocks:
- instrument source (usually already exists, e.g. `Source1`)
- boolean signal block `LongSignal` (can be a formula or a handler)
- `OpenPositionByMarketItem`

Ops outline:
```json
{
  "ops": [
    { "op": "AddBlock", "blockId": "OpenLong", "blockType": "OpenPositionByMarketItem", "params": { "Long": "true", "Shares": "1" } },
    { "op": "RenameBlock", "blockId": "OpenLong", "visualName": "Entry Long" },
    { "op": "Connect", "fromBlockId": "Source1", "fromPort": "Out", "toBlockId": "OpenLong", "toPort": 0 },
    { "op": "Connect", "fromBlockId": "LongSignal", "fromPort": "Out", "toBlockId": "OpenLong", "toPort": 1 }
  ]
}
```

---


## 3) Formula input hygiene (avoid missing Input0 / broken expressions)
When a formula block references variables, every referenced symbol must be connected as an input.
If you change `Expression`, also add the missing `Connect` for the new symbol.

Example: update entry condition to use EMA50/EMA200 with a dedicated signal block.
```json
{
  "ops": [
    { "op": "AddBlock", "blockId": "TrendUp", "blockType": "BoolCustomHandlerItem", "params": { "Expression": "EMA50 > EMA200" } },
    { "op": "Connect", "fromBlockId": "EMA50", "fromPort": "Out", "toBlockId": "TrendUp", "toPort": 0 },
    { "op": "Connect", "fromBlockId": "EMA200", "fromPort": "Out", "toBlockId": "TrendUp", "toPort": 1 },
    { "op": "ReplaceInput", "fromBlockId": "TrendUp", "toBlockId": "OpenLong", "toPort": 1 }
  ]
}
```
Notes:
- Keep entry logic in a **dedicated** BoolCustom block to avoid accidental port clashes.
- Use `/explain` to verify `data.links` and avoid duplicate connections into the same `toPort`.
- Remember: formula `Expression` references **CodeName**, not `blockId`.

---


## 4) Restore parameters after restart (generic pattern)
If `/parameters` shows blank/zero values after a restart, re-apply via `/parameters`:
```json
{
  "parameters": [
    { "id": "<ParamId-1>", "value": "1.5" },
    { "id": "<ParamId-2>", "value": "20" }
  ]
}
```
How to get `id`:
- `GET /api/scripts/{name}/parameters` and use `parameters[].id` (stable across restarts).
If a ConstGen block is missing from `/parameters`:
- Use `/explain` to find the block and apply `SetParam` (writes to EditItem parameters directly).

---

## 5) Breakout of previous 100-bar high + exit at midpoint (plot channel)
Goal (common wording): "price crosses the highest high of the last 100 bars -> go long; exit at the midpoint between the highest high and lowest low; plot the instrument plus the high/low lines on the chart".

Key clarifications (do not guess):
- TSLab evaluates only **closed** bars. `High100` includes the last closed bar. For a "breakout of previous high" threshold, use `High100[-1]`.
- If the wording is ambiguous ("crosses the highest high of the last 100 bars"), ask: should the threshold include the last closed bar (`High100`) or be the previous window (`High100[-1]`)?
- For "highest/lowest over N bars" compute from `High`/`Low` unless a human explicitly asks for closes.
- "exit at midpoint" is ambiguous:
  - **limit by price**: close at `Mid` using `ClosePositionAtPriceItem` (this recipe)
  - **market by signal**: close by market on `CrossUnder(Close, Mid)` (alternate variant)

Ops outline (create blocks + plot + trade):
```json
{
  "ops": [
    { "op": "AddBlock", "blockId": "Src", "blockType": "TradableSecuritySourceItem", "category": "TradableSecurity" },
    { "op": "SetSourceMapping", "blockId": "Src", "dataSourceName": "ByBit", "securityId": "BTCUSDT", "isOption": false, "visualTypeName": "Tradable instrument" },

    { "op": "AddBlock", "blockId": "Close1", "typeName": "Close", "blockType": "ConverterItem" },
    { "op": "AddBlock", "blockId": "High1", "typeName": "High", "blockType": "ConverterItem" },
    { "op": "AddBlock", "blockId": "Low1", "typeName": "Low", "blockType": "ConverterItem" },

    { "op": "Connect", "fromBlockId": "Src", "fromPort": "Out", "toBlockId": "Close1", "toPort": 0 },
    { "op": "Connect", "fromBlockId": "Src", "fromPort": "Out", "toBlockId": "High1", "toPort": 0 },
    { "op": "Connect", "fromBlockId": "Src", "fromPort": "Out", "toBlockId": "Low1", "toPort": 0 },

    { "op": "AddBlock", "blockId": "High100", "typeName": "Highest", "blockType": "ConverterItem" },
    { "op": "AddBlock", "blockId": "Low100", "typeName": "Lowest", "blockType": "ConverterItem" },
    { "op": "SetParam", "blockId": "High100", "paramName": "Period", "value": "100" },
    { "op": "SetParam", "blockId": "Low100", "paramName": "Period", "value": "100" },
    { "op": "Connect", "fromBlockId": "High1", "fromPort": "Out", "toBlockId": "High100", "toPort": 0 },
    { "op": "Connect", "fromBlockId": "Low1", "fromPort": "Out", "toBlockId": "Low100", "toPort": 0 },

    { "op": "AddBlock", "blockId": "PrevHigh100", "blockType": "DoubleCustomHandlerItem", "params": { "Expression": "High100[-1]" } },
    { "op": "Connect", "fromBlockId": "High100", "fromPort": "Out", "toBlockId": "PrevHigh100", "toPort": 0 },

    { "op": "AddBlock", "blockId": "Mid", "blockType": "DoubleCustomHandlerItem", "params": { "Expression": "(High100 + Low100) / 2" } },
    { "op": "Connect", "fromBlockId": "High100", "fromPort": "Out", "toBlockId": "Mid", "toPort": 0 },
    { "op": "Connect", "fromBlockId": "Low100", "fromPort": "Out", "toBlockId": "Mid", "toPort": 1 },

    { "op": "AddBlock", "blockId": "Entry", "typeName": "CrossOver", "blockType": "TwoOrMoreInputsItem" },
    { "op": "Connect", "fromBlockId": "PrevHigh100", "fromPort": "Out", "toBlockId": "Entry", "toPort": 0 },
    { "op": "Connect", "fromBlockId": "Close1", "fromPort": "Out", "toBlockId": "Entry", "toPort": 1 },

    { "op": "AddBlock", "blockId": "Exit", "typeName": "CrossUnder", "blockType": "TwoOrMoreInputsItem" },
    { "op": "Connect", "fromBlockId": "Mid", "fromPort": "Out", "toBlockId": "Exit", "toPort": 0 },
    { "op": "Connect", "fromBlockId": "Close1", "fromPort": "Out", "toBlockId": "Exit", "toPort": 1 },

    { "op": "AddBlock", "blockId": "OpenLong", "blockType": "OpenPositionByMarketItem", "params": { "Long": "true", "Shares": "1" } },
    { "op": "Connect", "fromBlockId": "Src", "fromPort": "Out", "toBlockId": "OpenLong", "toPort": 0 },
    { "op": "Connect", "fromBlockId": "Entry", "fromPort": "Out", "toBlockId": "OpenLong", "toPort": 1 },

    { "op": "AddBlock", "blockId": "CloseAtMid", "blockType": "ClosePositionAtPriceItem" },
    { "op": "Connect", "fromBlockId": "OpenLong", "fromPort": "Out", "toBlockId": "CloseAtMid", "toPort": 0 },
    { "op": "Connect", "fromBlockId": "Exit", "fromPort": "Out", "toBlockId": "CloseAtMid", "toPort": 1 },
    { "op": "Connect", "fromBlockId": "Mid", "fromPort": "Out", "toBlockId": "CloseAtMid", "toPort": 2 },

    { "op": "AddPane", "paneKey": "Main", "category": "GraphPane", "params": { "Order": "0", "IsVisible": "true" } },
    { "op": "AddGraphLink", "fromBlockId": "Src", "fromPort": "Out", "toBlockId": "Main", "toPortName": "RIGHT", "category": "ChartCandleLink", "dataXml": "<GraphData ListStyle=\"LINE\" CandleStyle=\"BAR_CANDLE\" LineStyle=\"SOLID\" Color=\"255\" AltColor=\"255\" Opacity=\"0\" HideLastValue=\"false\" Thickness=\"1\" PaneSide=\"RIGHT\" Visible=\"true\" ShowTrades=\"true\" ShowPositionStop=\"true\" ShowPositionText=\"true\" ShowPositionIcon=\"true\" />" },
    { "op": "AddGraphLink", "fromBlockId": "High100", "fromPort": "Out", "toBlockId": "Main", "toPortName": "RIGHT", "category": "ChartLineLink" },
    { "op": "AddGraphLink", "fromBlockId": "Low100", "fromPort": "Out", "toBlockId": "Main", "toPortName": "RIGHT", "category": "ChartLineLink" }
  ]
}
```
Notes:
- Always provide explicit `dataXml` for `ChartCandleLink` to avoid default black candle style.
- After ops: `POST /validate` -> `POST /build` -> `POST /run`, then check `/charts/info` and `/performance?format=named`.

---



