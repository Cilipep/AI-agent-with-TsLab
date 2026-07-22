# Options Scripts (Quick)

Small-context summary of the options pipeline and safe rules.

## Hard rules
- Options graphs are server-side; edit via `/api/scripts/{name}/ops`.
- Always set option source mapping with `isOption: true`.
- Follow the pipeline: `OPTION` -> `OPTION_SERIES` -> `SECURITY`.
- Validate after ops edits.

## Minimal pipeline (concept)
`TradableOptionSourceItem (OPTION)`
-> `OptionSeriesByNumber (OPTION_SERIES)`
-> `CentralStrike` (DOUBLE series, optional)
-> `SingleOption` (SECURITY option contract)
-> regular SECURITY handlers / trading blocks

## Minimal ops skeleton
```json
{
  "ops": [
    { "op": "AddBlock", "blockId": "OptSrc", "blockType": "TradableOptionSourceItem", "category": "TradableOption" },
    { "op": "SetSourceMapping", "blockId": "OptSrc", "dataSourceName": "Provider", "securityId": "OPT-CHAIN", "isOption": true },
    { "op": "AddBlock", "blockId": "Series", "blockType": "ConverterItem",
      "handlerTypeName": "TSLab.Script.Handlers.Options.OptionSeriesByNumber, TSLab.Script.Handlers.Options" },
    { "op": "AddBlock", "blockId": "SingleOpt", "blockType": "TwoOrMoreInputsItem",
      "handlerTypeName": "TSLab.Script.Handlers.Options.SingleOption, TSLab.Script.Handlers.Options" },
    { "op": "Connect", "fromBlockId": "OptSrc", "fromPort": "Out", "toBlockId": "Series", "toPort": 0 },
    { "op": "Connect", "fromBlockId": "Series", "fromPort": "Out", "toBlockId": "SingleOpt", "toPort": 0 }
  ]
}
```

For details (OptionSelector, ControlPane, CanvasPane, strike logic), see `AGENTS-Options.md`.
