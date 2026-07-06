# Agent Instructions: Script Editing (Graph / Blocks / Ops)

Use this file only for concrete graph-editing questions through the Web API.
Common routing, phase order, lifecycle gates, multi-timeframe acceptance, visualization acceptance, and control-pane policy live in `AGENTS-FastPath.md` and the shipped authoring skill.

## What stays here

This file is a narrow reference for:
- live contract endpoints for blocks, handlers, and graph shape
- `/ops` payload shape and field names
- graph wiring vs UI-link semantics
- minimal mutation examples

If you are not blocked on one concrete graph-editing question, stay on `AGENTS-FastPath.md` plus live localhost endpoints instead of reading this file end to end.

## API-first boundary

- TSLab scripts are server-side artifacts. Do not edit local XML, JSON, or repo files to change a server-side script.
- The normal write path is `POST /api/scripts/{name}/ops`.
- The normal structural checks are `POST /api/scripts/{name}/validate`, `GET /api/scripts/{name}/authoring-quality`, and `GET /api/scripts/{name}/explain`.
- The only raw-graph exception is the documented comment-block view-model case through `GET/PUT /api/scripts/{name}/json`.
- Keep one current artifact and repair that artifact in place.

## Context-budget rule

- Do not read this whole file unless you are blocked on one graph-editing question.
- For routine work, stay on live `template-blocks`, `handlers`, `explain`, `authoring-quality`, and `ui` reads.
- Search this file for one exact term when you need it.

## Source of truth for contracts

Use the narrowest live endpoint that answers the question:

- `GET /api/template-blocks/{typeName}` for template items such as sources, trade blocks, panes, and value blocks
- `GET /api/template-blocks?query=...&top=20` for targeted template discovery
- `GET /api/handlers/{typeName}` for handler IO and parameters
- `GET /api/handlers/search?q=...&limit=20` for targeted handler discovery
- `GET /api/scripts/{name}/explain` for real block IDs, ports, and graph shape on the current artifact
- `GET /api/scripts/{name}/authoring-quality` for structural issues and suggested repairs
- `GET /api/scripts/{name}/ui` for panes, graph links, control panes, and layout
- On an existing artifact, `/explain` is the source of truth for current `blockId` and port names, and `/ui` is the source of truth for current `paneKey` values. Do not invent `Src`, `pane_price`, `pane_profit`, or copied example IDs unless they already exist on the current artifact or are created earlier in the same batch.
- For ordinary strategy trade/order and multi-timeframe families, prefer `template-blocks` before `handlers`: `OpenPosition*`, `ChangePosition*`, `ClosePosition*`, `RelativeCommission`, and `Compress*` should start from `GET /api/template-blocks/{typeName}` or one filtered template query unless that template route already failed on the current host. For explicit return families such as `Decompress*` / `Decompres*`, do not start the first scaffold with those reads; open them only after the compressed branch already exists on the current artifact and the remaining return-to-base contract is still unclear.
- If a numeric indicator or band family such as Bollinger expects `DOUBLE`, derive `Close`/`Open`/`High`/`Low` first; do not wire the tradable `Src` / `SECURITY` stream directly into that input. For `ChangePosition*`, read the exact template-block inputs before wiring and do not infer the full contract from `OpenPosition*`.
- On ladder, averaging, or scale-in prompts, do not call the artifact complete while it still has only the initial OpenPosition* leg and no real ChangePosition* add-to-position leg. Finish the active add leg before final proof, visualize-only polish, or optimization.
- For human-facing chart output, keep candles, primary price bands, and derived price-level lines such as ladder or entry-price guides on the same candle/main price pane. Use separate panes only for separate-scale series such as profit, oscillators, or thresholds.
- If `authoring-quality` or `intent-check` already names the remaining blocker or returns `suggestedRepairOps[]`, repair that exact blocker on the same artifact before broader catalog discovery.
- On a strategy repair turn, do not send one large speculative `/ops` batch that mixes guessed trade blocks, formulas, panes, and links. Add or fix one missing family at a time on the same artifact, then re-read `authoring-quality` or `intent-check` before the next family.

Do not keep broad-searching once one or two targeted reads gave the missing contract.
If you need a local handler reference file, open the exact file directly, for example `AGENTS-HandlersReference-TradeMath.md`.
Do not grep wildcard handler-reference paths such as `AGENTS-HandlersReference-*.md`.

## `/ops` request shape

- Send a top-level JSON object shaped like `{ "ops": [ ... ] }`.
- Use canonical field names only: `blockId`, `typeName`, `blockType`, `fromBlockId`, `fromPort`, `toBlockId`, `toPort`, `toInputName`, `category`, `paneKey`.
- Do not use compatibility-looking aliases such as `from`, `to`, `block`, `key`, `fromBlock`, `toBlock`, `handlerType`, `handlerTypeName`, `blockKey`, or `toPortNum` in handcrafted `/ops` bodies. If a live response returns `suggestedRepairOps[]`, `suggestedAddBlockOp`, `canonicalAddBlockOp`, or `suggestedSetOptimizationRangeOp`, post that exact object shape instead of translating it from memory.
- `AddParameter` is not an `/ops` mutation. Keep ordinary numeric knobs as direct block parameters plus `SetOptimizationRange`; use `AddControlPane` / `AddControlLink` only when the prompt explicitly requires editable runtime controls.
- If the prompt says sibling outputs share one knob, such as upper/lower bands or threshold pairs, keep those parameters aligned instead of silently splitting them into unrelated knobs. Multiple parameter ids may still exist, but the graph should still read as one shared logical family.
- For `AddPane`, either omit `position` or pass a structured object like `{ "x": 150, "y": 200 }`. Do not send scalar or string `position` values such as `100` or `"100 100"`.
- Give important new blocks stable `blockId` or `codeName` values in `AddBlock` ops.
- In a manual `/ops` batch, every `Connect` endpoint must either already exist on the current artifact from `/explain` or be added earlier in that same batch. Do not reference guessed example IDs just because they appear in local docs.
- If `suggestedRepairOps[]` already introduced starter IDs, either reuse those exact IDs or rename the whole batch consistently. Do not mix stale suggested IDs with newly renamed blocks in one payload.
- If `suggestedRepairOps[]` already contains `RemoveBlock`, `Disconnect`, `UpdateGraphLink`, `SetParam`, or similar ops, post those exact ops instead of grepping docs for their spelling or request shape.
- If `suggestedRepairOps[]` or `suggestedVisualizationOps[]` already contains escaped `dataXml` or other long XML payloads, keep the request as real JSON in `./tmp/ops.json` inside the current workspace and POST that file through `./api-json.ps1` or `curl.exe --data-binary`. Do not rewrite those payloads as PowerShell hashtables or inline strings.
- `EditBlock` is not a valid `/ops` mutation. To change an existing block parameter, use `SetParam` on the real `blockId` with the exact parameter field `paramName`.
- `SetOptimizationRange` is separate from `SetParam`: it targets an optimization mapping and uses `paramInvariantName`, not `paramName`. New range ops should use the API fields `paramInvariantName`, `optimDataType`, optional `value`, `min`, `max`, `step`, and `usedInOptimization`; do not invent `parameterCodeName`, `optimMinValue`, `optimMaxValue`, or `optimStep` request fields. Do not swap those field names across `SetParam` and `SetOptimizationRange`.
- `RemoveBlock` uses the exact shape `{ "op": "RemoveBlock", "blockId": "<id>" }`.
- Never use `/parameters.itemId` as an `/ops blockId`.
- If `/ops` returns `success=false`, non-empty `errors[]`, or blocking `warnings[]`, repair the same artifact before lifecycle or summary.

## Graph wiring vs UI links

- `Connect` and `ConnectByInputName` are graph wiring between graph blocks.
- `AddGraphLink` and `AddControlLink` are UI links.
- Create chart panes with `AddPane`.
- Create visible chart series with `AddGraphLink`.
- Create editable runtime controls with `AddControlPane` plus `AddControlLink` only when the prompt explicitly requires editable controls.
- `paneKey` values created by `AddPane` are UI pane identifiers, not graph block IDs. Do not target a pane with `Connect`, `ConnectByInputName`, or ordinary block-input wiring.
- If `visualName` is omitted on `AddBlock`, Web API persists `VisualName` from the final `CodeName`, matching desktop behavior. Send `visualName` only when a different human display caption is intentional.
- If `/explain` shows unnamed or duplicate compatible inputs on a multi-input block, do not guess `Input1` / `Input2` and do not use `ConnectAuto`. Use `Connect` with the exact zero-based `toPort` index.
- For `BoolCustomHandlerItem` / `DoubleCustomHandlerItem` expressions, default to stable upstream `blockId` / `codeName` tokens such as `Close1`, `bb_lower`, `EntryPrice1`, or `PositionShares1`. Keep explicit upstream `Connect` links when they help the graph stay readable or when the same upstream outputs also feed other consumers, but do not depend on `Input0`, `Input1`, ... as the default runtime contract on this host. If the intended value is just a literal knob such as `0.02`, `100`, `true`, or `false`, or another fixed scalar like a stop percent or threshold, prefer a direct block parameter or an exact host-proved constant/value template block instead of a standalone custom formula block. Do not invent `NumericConstantValueItem`, `BoolConstantValueItem`, or `Value*SourceItem` names from memory. Do not wire `Src` / `SECURITY` into a custom formula block just to carry that scalar. If `/explain` or runtime reports `UnknownExpressionReference`, treat it as a blocking expression repair on the same artifact.
- Treat undocumented aliases such as `Arg1`, `Arg2`, `Arg`, `X`, `Y`, `In0`, `In1`, and generic slot placeholders such as `Input0`, `Input1`, ... as non-preferred defaults. Unless the current host already proved a different executable syntax on the same artifact, repair formulas toward real upstream `blockId` / `codeName` references.
- `GraphPaneSourceItem` and `CanvasPaneSourceItem` are not a substitute for real pane creation.
- Do not use BoolCustomHandlerItem / DoubleCustomHandlerItem as semantic stand-ins for standard handler families, and do not stuff `handlerTypeName` into those custom-item params to mimic a real block. Families such as `Close`, `EMA`, `RSI`, `BollingerBands*`, `Compress*`, `RelativeCommission`, and `OpenPosition*` / `ChangePosition*` / `ClosePosition*` must use the real template or handler-backed block type that the current host advertises. If the prompt or intent-check requires those families, add the real block and keep custom formulas only for derived arithmetic or glue. When replacing a placeholder formula with the real handler, remove or rename the old placeholder in the same repair loop.

## What stays in FastPath

Keep these decisions in `AGENTS-FastPath.md` and the shipped authoring skill instead of duplicating them here:

- route selection between read-run and authoring
- minimal trade scaffold requirements
- formula requirements
- multi-timeframe base-interval and decompression proof
- visualization acceptance
- control-pane optionality
- repair prioritization
- final delivery acceptance

## Minimal examples

### Set one parameter
```json
{
  "ops": [
    { "op": "SetParam", "blockId": "EMA1", "paramName": "Period", "value": "30" }
  ]
}
```

### Remove one broken block
```json
{
  "ops": [
    { "op": "RemoveBlock", "blockId": "Always" }
  ]
}
```

### Safe trade-block wiring by input name
```json
{
  "ops": [
    { "op": "ConnectByInputName", "fromBlockId": "Src", "toBlockId": "LE", "toInputName": "Src" },
    { "op": "ConnectByInputName", "fromBlockId": "Cond", "toBlockId": "LE", "toInputName": "Eq" },
    { "op": "ConnectByInputName", "fromBlockId": "Price", "toBlockId": "LE", "toInputName": "Prc" }
  ]
}
```

### Safe positional wiring for unnamed multi-input ports
```json
{
  "ops": [
    { "op": "Connect", "fromBlockId": "Close30", "toBlockId": "Greater30", "toPort": 0 },
    { "op": "Connect", "fromBlockId": "EMA30", "toBlockId": "Greater30", "toPort": 1 }
  ]
}
```

### Add a visible price pane with candles
```json
{
  "ops": [
    {
      "op": "AddPane",
      "paneKey": "pane_price",
      "category": "GraphPane",
      "position": { "x": 150, "y": 200 },
      "params": { "Order": 0, "IsVisible": true }
    },
    {
      "op": "AddGraphLink",
      "fromBlockId": "Src",
      "fromPort": "Out",
      "toPaneKey": "pane_price",
      "toPortName": "RIGHT",
      "category": "ChartCandleLink"
    }
  ]
}
```
