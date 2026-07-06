---
name: tslab-indicator-use-in-script
description: "Phase card for using a known uploaded stream indicator handler inside a server-side TSLab script."
---

# TSLab Indicator Use In Script

## When to load

- The uploaded indicator handler type is already known and the user wants a server-side trading script that uses it.
- Do not load this card for visual/analysis indicator scripts, chart overlays, dashboards, or prompts that only ask to show the uploaded indicator with runtime controls. Those use blank create, `instrument-source`, and explicit `/ops` instead.

## First call

- `GET /api/handlers/{typeName}`

## Fields to read

- `response.data.typeName`
- `response.data.fullTypeName`
- `response.data.minInputCount`
- `response.data.maxInputCount`
- `response.data.parameters`
- if present from the upload step:
  - `response.data.nextStepHint`
  - `response.data.suggestedStarterStrategyRoutes`

## Next allowed call

- after `GET /api/handlers/{typeName}`, if the user wants a trading script or strategy with entry/exit/trade logic from the uploaded handler, the preferred next shell step is `POST /api/scripts/templates/uploaded-indicator-signal-starter`
- if the task is visual/analysis-only, chart-overlay, dashboard, or "add this indicator with controls" without entry/exit/trading logic, do not call `uploaded-indicator-signal-starter`; create the exact script, map source data, and use explicit `/ops`
- use manual script create/source/`/ops` when `uploaded-indicator-signal-starter` rejects the handler as unsupported, the user explicitly requires a custom graph, or the task is visual/analysis-only rather than a starter trading strategy
- do not open extra AGENTS example files before the first starter route or `/ops` batch
- for the starter route, provide `name`, `handlerTypeName`, `dataSourceName`, `securityId`, `interval`, and `starterKind` such as `Auto` or one of the exact supported kinds returned by the server
- the starter create route creates the named script and maps source data itself; do not blank-create or call `instrument-source` before it
- send the starter route body as direct JSON, not `{ "request": { ... } }`
- on PowerShell, write the body to `./tmp/starter.json` and call `./api-json.ps1 POST /api/scripts/templates/uploaded-indicator-signal-starter ./tmp/starter.json`; do not inline JSON through `curl.exe -d` and do not pass `@` as a separate quoted token
- after the starter route succeeds, continue with `validate -> build -> load -> run -> metrics-summary`, then use explicit `/ops` only for prompt-specific refinements that the starter did not cover
- create a new server-side script with `POST /api/script-manager/scripts`
- if the user prompt gives an exact target script/artifact name, use that name byte-for-byte in the first create call and all proof routes; do not create a shorter helper artifact or friendlier alias
- use the current shell directly; if a doc or API hint shows a PowerShell example, translate the same route/body into the current shell's native client when running on macOS/Linux
- for JSON mutation bodies in PowerShell, prefer `Invoke-RestMethod` or a UTF-8 file with `curl --data-binary`; avoid inline `curl -d "{...}"` because quoting can corrupt the body
- if you send the JSON body from a file with `curl`, use exactly one request-body flag, for example `curl --data-binary "@ops.json" ...`; Do not combine `-d @ops.json` with `--data-binary` in the same command
- for `/ops`, send a top-level object shaped like `{ "ops": [ ... ] }`, not a bare array and not a pre-escaped JSON string
- configure the tradable instrument with `POST /api/scripts/{name}/instrument-source`
- request body accepts `dataSourceName` aliases `provider`/`sourceType` and `securityId` aliases `symbol`/`instrument`/`security`/`ticker`
- if the user already named the instrument, reuse it directly as `securityId`
- only if the exact `securityId` is still unknown, query `GET /api/agent-manager/securities?dataSourceName=...&query=...&limit=20`
- after `instrument-source`, the next shell step must be the first `POST /api/scripts/{name}/ops`
- send the `/ops` request body as a JSON object shaped like `{ "ops": [ ... ] }`, not as a bare array
- if the exact requested target script already exists, update or reuse that exact artifact instead of minting `_v2`, `_new`, or other suffix variants unless the user explicitly asked for a second copy
- if the prompt requires placing a script into a specific folder such as `AI`, treat folder placement separately from the script leaf name: resolve the folder node through `GET /api/script-manager/tree` and create with `parentScriptId = <folderId>` plus the plain leaf `name`
- do not encode folder placement by stuffing `AI/...` into the script `name` unless the user explicitly wants a literal slash in the stored name
- if you already have an existing slash-containing script name, prefer the documented `.../by-name/{**name}` routes when they are advertised for that phase. If no `by-name` route exists for the required phase, stop and report the ambiguity instead of mutating a guessed artifact
- inside `/ops`, use canonical field names only: `blockId`, `typeName`, `blockType`, `category`, `fromBlockId`, `fromPort`, `toBlockId`, `toPort`, `toInputName`; do not invent aliases such as `from`, `to`, `block`, `key`, `handlerTypeName`, `blockKey`, `fromBlock`, `toBlock`, or `toPortNum`
- use `SetParam` for handler parameters, not `SetParameter`
- use `Connect` with `fromBlockId`, `toBlockId`, `fromPort`, and `toPort`
- use the live `suggestedAddBlockOp` / `canonicalAddBlockOp` for handler blocks; one-input handlers such as `High`, `Low`, and `Close` usually resolve to `ConverterItem` plus `typeName`
- use the live advertised carrier for 2+ input handlers such as the uploaded indicator, `CrossOver`, and `CrossUnder`, often `TwoOrMoreInputsItem` plus `typeName`
- if the handler is a DOUBLE stream indicator and the starter route is unavailable or rejected as unsupported, manual fallback for a reasonable starter strategy is:
  - use a simple long-only `price crosses indicator` pattern
  - add `High`, `Low`, `Close`
  - add the indicator block with `typeName = {handlerTypeName}`
  - wire price inputs in the exact order required by `/api/handlers/{typeName}`
  - use `CrossOver` for entry and `CrossUnder` for exit
  - use `OpenPositionByMarketItem` for entry and set `Shares = 1`
- use `ClosePositionByMarketItem` for exit
- add `RelativeCommission` on the trade surface unless the user explicitly excluded costs
- add protective stop/profit exits unless the user explicitly asked for signal-only exits
- wire `Src -> OpenPositionByMarketItem.Src`, `Entry -> OpenPositionByMarketItem.Eq`, `OpenPosition -> ClosePositionByMarketItem.Pos`, and `Exit -> ClosePositionByMarketItem.Eq`
- add a candle graph link for the instrument with `Category=ChartCandleLink` and styled candle `dataXml`; do not add a second `ChartLineLink` from the source block
- add a styled line graph link for the indicator output with explicit `dataXml`
- if the prompt explicitly requires editable runtime controls for the uploaded indicator parameters, use explicit `/ops` on the same target artifact; every control link needs concrete `dataXml` with a numeric/bool/enum type on each `Property`, never `ControlParameterType.NotDefined` or narrative/helper pane labels
- then continue with `validate -> build -> load -> run -> metrics-summary -> authoring-quality?compact=true`
- if authoring-quality returns `requiresRepair=true`, follow `requiredNextMutationRoute` on the same artifact and rerun the proof loop before the final answer
- if the prompt requires an exact final script name or folder, do not stop at a helper script with a different name; the exact requested server-side script must be the one that reaches `validate -> build -> load -> run`

## Stop if failed

- Do not invent the handler input order.
- Do not guess block IDs or parameter names without `/api/handlers/{typeName}`.
- Do not use `POST /api/scripts/{name}/source` for instrument mapping; use `/instrument-source`.
- Do not send a bare JSON array to `/ops`; wrap operations under top-level `ops`.
- Do not fall back to repo `scripts/*.cs`.
- Do not keep browsing the internet at this stage; the next step is graph wiring and run.
