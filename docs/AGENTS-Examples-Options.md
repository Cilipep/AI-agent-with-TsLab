# Examples & Recipes: Editing TSLab Scripts via Web API `ops`

This file contains concrete "cookbook" scenarios. It is written for agent authors and humans designing tasks for the agent.

All examples assume you follow the safe workflow:
- `GET /api/scripts/{name}/explain`
- build an `ops` plan
- `POST /api/scripts/{name}/validate`
- `POST /api/scripts/{name}/ops`
- `POST /api/scripts/{name}/build`
- `GET /api/scripts/{name}/messages`


This is part: Options.
See also: AGENTS-Examples-Quick.md and AGENTS-Examples.md (index).

## 7) Options: minimal "underlying from option source" (like `OptionBase`)
Goal: start an options script from scratch, map an option instrument, and draw the underlying on a graph pane.

Blocks:
- `TradableOptionSourceItem` (template block, produces `OPTION`)
- `OptionBase` (handler, converts `OPTION` -> underlying `SECURITY`)
- `GraphPane` + `GraphLink` (to display candles)

```json
{
  "ops": [
    { "op": "AddBlock", "blockId": "OptSrc", "blockType": "TradableOptionSourceItem", "category": "TradableOption" },
    { "op": "SetSourceMapping", "blockId": "OptSrc", "dataSourceName": "<DATA_SOURCE_NAME_FROM_/api/datasources>", "securityId": "SOLUSDT-30JAN26", "isOption": true },

    { "op": "AddBlock", "blockId": "Underlying", "typeName": "OptionBase", "blockType": "ConverterItem", "category": "Options" },
    { "op": "Connect", "fromBlockId": "OptSrc", "toBlockId": "Underlying", "toPort": 0 },

    { "op": "AddPane", "paneKey": "Main", "category": "GraphPane" },
    { "op": "AddGraphLink", "fromBlockId": "Underlying", "toBlockId": "Main", "toPortName": "RIGHT", "category": "ChartCandleLink", "dataXml": "<GraphData ListStyle=\"LINE\" CandleStyle=\"BAR_CANDLE\" LineStyle=\"SOLID\" Color=\"255\" AltColor=\"255\" Opacity=\"0\" HideLastValue=\"false\" Thickness=\"1\" PaneSide=\"RIGHT\" Visible=\"true\" ShowTrades=\"true\" ShowPositionStop=\"true\" ShowPositionText=\"true\" ShowPositionIcon=\"true\" />" }
  ]
}
```

Notes:
- If `/api/handlers` does not list `OptionBase`, the server is not loading the options handlers assembly. Check Web API startup logs for handler discovery and verify the options handlers project/assembly is included in the Web API build and runtime load path.

---


## 8) Options: select a series + a single option contract (call/put)
Goal: from an option source select an expiration series and then select one call contract at a fixed strike.

Blocks:
- `OptSrc`: `TradableOptionSourceItem` (`OPTION`)
- `Series`: `OptionSeriesByNumber` (`OPTION_SERIES`)
- `Call`: `SingleOption` (`SECURITY` option contract)

```json
{
  "ops": [
    { "op": "AddBlock", "blockId": "OptSrc", "blockType": "TradableOptionSourceItem", "category": "TradableOption" },
    { "op": "SetSourceMapping", "blockId": "OptSrc", "dataSourceName": "<DATA_SOURCE_NAME_FROM_/api/datasources>", "securityId": "RI-OPTIONS", "isOption": true },

    { "op": "AddBlock", "blockId": "Series", "typeName": "OptionSeriesByNumber", "blockType": "ConverterItem", "category": "Options" },
    { "op": "SetParam", "blockId": "Series", "paramName": "ExpirationMode", "value": "FirstExpiry" },
    { "op": "Connect", "fromBlockId": "OptSrc", "toBlockId": "Series", "toPort": 0 },

    { "op": "AddBlock", "blockId": "Call", "typeName": "SingleOption", "blockType": "TwoOrMoreInputsItem", "category": "Options" },
    { "op": "SetParam", "blockId": "Call", "paramName": "OptionType", "value": "Call" },
    { "op": "SetParam", "blockId": "Call", "paramName": "SelectionMode", "value": "FixedStrike" },
    { "op": "SetParam", "blockId": "Call", "paramName": "FixedStrike", "value": "120000" },
    { "op": "Connect", "fromBlockId": "Series", "toBlockId": "Call", "toPort": 0 }
  ]
}
```

Pitfall:
- If the strike is missing in the series, `SingleOption` logs a warning in Lab mode and returns `null`; in Agent mode it may throw a `ScriptException`.

---


## 9) Options: bind `SingleOption.FixedStrike` to a `ConstGen.Value` via `ParameterShareItem`
This pattern is used in real scripts (e.g. the "LinkedParam" blocks in option examples).

Goal: drive `SingleOption.FixedStrike` from a numeric constant block, so you can later:
- change the constant,
- or expose the constant via ControlPane,
- and keep the option selection synchronized.

Key idea:
- `ParameterShareItem.ParameterName1` is the *Master* parameter to update.
- `ParameterShareItem.ParameterName2` is the *Slave* parameter to read.
- Connect `SingleOption` -> `ParameterShareItem` as `Master`.
- Connect `ConstGen` -> `ParameterShareItem` as `Slave`.

```json
{
  "ops": [
    { "op": "AddBlock", "blockId": "StrikeConst", "typeName": "ConstGen", "blockType": "ConverterItem", "category": "Const" },
    { "op": "SetParam", "blockId": "StrikeConst", "paramName": "Value", "value": "120000" },

    { "op": "AddBlock", "blockId": "Call", "typeName": "SingleOption", "blockType": "TwoOrMoreInputsItem", "category": "Options" },
    { "op": "SetParam", "blockId": "Call", "paramName": "OptionType", "value": "Call" },
    { "op": "SetParam", "blockId": "Call", "paramName": "SelectionMode", "value": "FixedStrike" },

    { "op": "AddBlock", "blockId": "BindStrike", "blockType": "ParameterShareItem", "category": "Usual" },
    { "op": "SetEditItemAttribute", "blockId": "BindStrike", "attributeName": "ParameterName1", "attributeValue": "FixedStrike" },
    { "op": "SetEditItemAttribute", "blockId": "BindStrike", "attributeName": "ParameterName2", "attributeValue": "Value" },

    { "op": "ConnectByInputName", "fromBlockId": "Call", "toBlockId": "BindStrike", "toInputName": "Master" },
    { "op": "ConnectByInputName", "fromBlockId": "StrikeConst", "toBlockId": "BindStrike", "toInputName": "Slave" }
  ]
}
```

---


## 7) Options: choose among multiple option sources (`OptionSelector`)
Goal: connect 2+ option sources and pick one with `OptionSelector` based on base prefix + series parameters.

```json
{
  "ops": [
    { "op": "AddBlock", "blockId": "OptA", "blockType": "TradableOptionSourceItem", "category": "TradableOption" },
    { "op": "SetSourceMapping", "blockId": "OptA", "dataSourceName": "FeedA", "securityId": "RI-OPTIONS", "isOption": true },

    { "op": "AddBlock", "blockId": "OptB", "blockType": "TradableOptionSourceItem", "category": "TradableOption" },
    { "op": "SetSourceMapping", "blockId": "OptB", "dataSourceName": "FeedB", "securityId": "SI-OPTIONS", "isOption": true },

    { "op": "AddBlock", "blockId": "PickOpt", "typeName": "OptionSelector", "blockType": "TwoOrMoreInputsItem", "category": "Options" },
    { "op": "SetParam", "blockId": "PickOpt", "paramName": "BaseSecPrefix", "value": "RI" },
    { "op": "SetParam", "blockId": "PickOpt", "paramName": "OptionSeries", "value": "RIM7" },

    { "op": "Connect", "fromBlockId": "OptA", "toBlockId": "PickOpt", "toPort": 0 },
    { "op": "Connect", "fromBlockId": "OptB", "toBlockId": "PickOpt", "toPort": 1 }
  ]
}
```



## 8) Options + CanvasPane: wire `SetViewport` to a Canvas pane
Goal: create a Canvas pane and connect it into an options "viewport controller" block (`SetViewport`), which expects a `CANVASPANE` input.

Important model detail:
- A Canvas pane is a `<Pane Category="CanvasPane">...`, not a `<Block>`.
- The pane key can be used as `fromBlockId` in a regular `Connect` op (the Web API validation supports this).

```json
{
  "ops": [
    { "op": "AddBlock", "blockId": "OptSrc", "blockType": "TradableOptionSourceItem", "category": "TradableOption" },
    { "op": "SetSourceMapping", "blockId": "OptSrc", "dataSourceName": "test", "securityId": "OPT.TEST", "isOption": true },

    { "op": "AddBlock", "blockId": "Underlying", "typeName": "OptionBase", "blockType": "ConverterItem", "category": "Options" },
    { "op": "Connect", "fromBlockId": "OptSrc", "toBlockId": "Underlying", "toPort": 0 },

    { "op": "AddBlock", "blockId": "Close1", "typeName": "Close", "blockType": "ConverterItem" },
    { "op": "Connect", "fromBlockId": "Underlying", "toBlockId": "Close1", "toPort": 0 },

    { "op": "AddBlock", "blockId": "Series", "typeName": "OptionSeriesByNumber", "blockType": "ConverterItem", "category": "Options" },
    { "op": "SetParam", "blockId": "Series", "paramName": "ExpirationMode", "value": "FirstExpiry" },
    { "op": "Connect", "fromBlockId": "OptSrc", "toBlockId": "Series", "toPort": 0 },

    { "op": "AddBlock", "blockId": "dT", "typeName": "TimeToExpiry", "blockType": "ConverterItem", "category": "OptionsTickByTick" },
    { "op": "Connect", "fromBlockId": "Series", "toBlockId": "dT", "toPort": 0 },

    { "op": "AddPane", "paneKey": "Canvas", "category": "CanvasPane" },
    { "op": "AddBlock", "blockId": "Viewport", "typeName": "SetViewport", "blockType": "TwoOrMoreInputsItem", "category": "OptionsTickByTick" },

    { "op": "Connect", "fromBlockId": "Close1", "toBlockId": "Viewport", "toPort": 0 },
    { "op": "Connect", "fromBlockId": "dT", "toBlockId": "Viewport", "toPort": 1 },
    { "op": "Connect", "fromBlockId": "Series", "toBlockId": "Viewport", "toPort": 2 },
    { "op": "Connect", "fromBlockId": "Canvas", "toBlockId": "Viewport", "toPort": 3 }
  ]
}
```

---


## 9) Options + ControlPane: expose option parameters for interactive tuning
Goal: create a control pane and link option-domain blocks into it so their parameters become interactive controls.

Typical blocks to link:
- `OptionSelector` (`BaseSecPrefix`, `OptionSeries`)
- `OptionSeriesByNumber` (`ExpirationMode`, `Number`, `Expiry`)
- `SingleOption` (`OptionType`, `SelectionMode`, `FixedStrike`)

```json
{
  "ops": [
    { "op": "AddControlPane", "paneKey": "Controls", "visualName": "Options Controls" },

    { "op": "AddBlock", "blockId": "PickOpt", "typeName": "OptionSelector", "blockType": "TwoOrMoreInputsItem", "category": "Options" },
    { "op": "AddBlock", "blockId": "Series", "typeName": "OptionSeriesByNumber", "blockType": "ConverterItem", "category": "Options" },
    { "op": "AddBlock", "blockId": "Call", "typeName": "SingleOption", "blockType": "TwoOrMoreInputsItem", "category": "Options" },

    {
      "op": "AddControlLink",
      "fromBlockId": "PickOpt",
      "toBlockId": "Controls",
      "dataXml": "<EditItem><Property PropertyName=\"SelectionMode\" ControlType=\"7\" Type=\"EnumComboBoxControlEditData\"><EnumComboBoxControlEditData><ControlDisplayName>SelectionMode</ControlDisplayName></EnumComboBoxControlEditData></Property></EditItem>"
    },
    {
      "op": "AddControlLink",
      "fromBlockId": "Series",
      "toBlockId": "Controls",
      "dataXml": "<EditItem><Property PropertyName=\"Number\" ControlType=\"3\" Type=\"IntUpDownControlEditData\"><IntUpDownControlEditData><ControlDisplayName>Number</ControlDisplayName></IntUpDownControlEditData></Property></EditItem>"
    },
    {
      "op": "AddControlLink",
      "fromBlockId": "Call",
      "toBlockId": "Controls",
      "dataXml": "<EditItem><Property PropertyName=\"OptionType\" ControlType=\"7\" Type=\"EnumComboBoxControlEditData\"><EnumComboBoxControlEditData><ControlDisplayName>OptionType</ControlDisplayName></EnumComboBoxControlEditData></Property></EditItem>"
    }
  ]
}
```

Notes:
- `AddControlLink` uses `FromPort="ControlOut"` by default (that is what UI expects for parameter publishing).
- `AddControlLink` now requires explicit `dataXml`. Use canonical payloads with numeric `ControlType`, concrete `Type`, and a matching edit-data element such as `IntUpDownControlEditData`, `UpDownControlEditData`, `CheckBoxControlEditData`, or `EnumComboBoxControlEditData`.
- Friendly aliases such as `IntUpDown`, `DoubleUpDown`, `CheckBox`, `ComboBox`, or nested `<ControlType>NumericUpDown</ControlType>` may be server-normalized, but canonical authoring should still send the real numeric `ControlType` plus the concrete edit-data element.
- Fine-grained control element layout (slider ranges, grouping, custom labels) still requires additional API work; see roadmap.


## 18) Options ControlPane in practice: publish handler parameters to a UI panel (pattern from `scripts/10.5.tscript`)
This pattern is common in options scripts where you want interactive tuning (strike selection, option type, algorithm mode, etc.).

Key entities in graph XML:
- a "ControlPane" is a *block* with `Category="ControlPane"` and an `<EditItem Name="...">` child (no `TypeName`).
- publishing is done via `<ControlLink From="{block}" To="{controlPaneKey}" FromPort="ControlOut" Category="ControlPaneLink">`
- the link can include an `<EditItem>` payload describing UI controls and their layout; the Web API represents this as `dataXml`.

Minimal API ops:
```json
{
  "ops": [
    { "op": "AddControlPane", "paneKey": "Controls", "visualName": "Options Controls" },

    { "op": "AddBlock", "blockId": "OptSrc", "blockType": "TradableOptionSourceItem", "category": "TradableOption" },
    { "op": "SetSourceMapping", "blockId": "OptSrc", "dataSourceName": "test", "securityId": "OPT.TEST", "isOption": true },

    { "op": "AddBlock", "blockId": "Series", "typeName": "OptionSeriesByNumber", "blockType": "ConverterItem", "category": "Options" },
    { "op": "Connect", "fromBlockId": "OptSrc", "toBlockId": "Series", "toPort": 0 },

    { "op": "AddBlock", "blockId": "PickOpt", "typeName": "SingleOption", "blockType": "ConverterItem", "category": "Options" },
    { "op": "Connect", "fromBlockId": "Series", "toBlockId": "PickOpt", "toPort": 0 },

    {
      "op": "AddControlLink",
      "fromBlockId": "Series",
      "toBlockId": "Controls",
      "dataXml": "<EditItem><Property PropertyName=\"Number\" ControlType=\"3\" Type=\"IntUpDownControlEditData\"><IntUpDownControlEditData><ControlDisplayName>Number</ControlDisplayName></IntUpDownControlEditData></Property></EditItem>"
    },
    {
      "op": "AddControlLink",
      "fromBlockId": "PickOpt",
      "toBlockId": "Controls",
      "dataXml": "<EditItem><Property PropertyName=\"OptionType\" ControlType=\"7\" Type=\"EnumComboBoxControlEditData\"><EnumComboBoxControlEditData><ControlDisplayName>OptionType</ControlDisplayName></EnumComboBoxControlEditData></Property></EditItem>"
    }
  ]
}
```

Adding a custom UI payload (layout + display names) is done with `UpdateControlLink` and a `dataXml` that matches the `<ControlLink>` inner structure from real scripts.
Practical approach:
1) Start with a minimal explicit `AddControlLink` payload for each published property.
2) Keep captions short. Use the exact parameter name or one short caption such as `Length`, `Period`, `Enabled`, or `OptionType`. Do not add narrative helper labels such as `Master control from ...`.
3) If you need layout or richer control metadata, update the same link with an `<EditItem>` that contains canonical `<Property ...>` definitions and the matching edit-data elements.

---



