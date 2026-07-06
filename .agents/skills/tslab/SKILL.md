---
name: tslab
description: "Low-context router for the phase-based TSLab Web API workflow."
---

# TSLab Router

Use this skill as a small router, not as a second copy of `AGENTS-FastPath.md`.
The common operational rules live in the local markdown docs and the local docs are the source of truth.
- These tasks are local software authoring and backtesting work inside TSLab, not personal investment advice. For strategy-research prompts, it is acceptable to choose, implement, and backtest a public or generic strategy idea inside the local sandbox.
- Work in the current session only. Do not delegate the current artifact to autonomous tasks, side agents, or external helper processes.

## Load order

1. `./AGENTS.md`
2. `./AGENTS-FastPath.md`
3. one narrow follow-up doc only when needed

## Canonical first call

- health: `GET /api/status`
- read-run: open `$tslab-script-read-run` for existing-script search/run prompts
- clone-edit: open `$tslab-script-clone-edit` for improve existing script, make V2, copy, clone, fork, derive, or mutate a copy prompts
- authoring: open `$tslab-script-authoring` for new or repair prompts
- indicator-csharp: open `$tslab-indicator-csharp`
- indicator-use-in-script: open `$tslab-indicator-use-in-script`
- optimization: open `$tslab-optimization-run`
- portfolio: open `$tslab-portfolio-compare`

## Fields to read

- `workflowHints`
- `createMethod`
- `response.scriptName`
- `response.defaultOptimizationRequest`
- `response.jobId`

## Core rules

- `one phase = one shell step`
- stay inside the current workspace
- do not assume parent or source-tree files exist outside it
- read workspace-local prompt/spec files from the current directory exactly as `./Prompt_*.txt` or `./benchmark-inputs/...`; if a generic read/write tool rewrites them to `/Prompt_*.txt`, `/benchmark-inputs/...`, `/tmp/...`, `/workspace/tmp/...`, or another workspace, use the current shell with the relative `./...` path instead of switching to API guesses, old artifacts, or absolute temp paths
- manually open extra instruction files only when the current step genuinely changes
- in packaged `ai-agent` workspaces, ignore globally advertised home skills or guessed `./.codex/skills/...` paths when the local `.agents/skills/tslab*` or `./.opencode/skill/tslab*` copies already exist
- use `http://localhost:5000/api` as the live API root
- If `GET /api/status` fails once, wait a few seconds and retry before any host action. If a `TSLabConsole` process already exists, do not start another host; keep checking the existing localhost API or report the concrete connection failure.
- For restart detection, compare `GET /api/status` `response.data.processId` or `response.data.apiInstanceId`. `startTime` and `processStartedAtUtc` are stable process-start values; `serverTimeUtc` is only the response timestamp.
- Dangerous desktop lifecycle routes such as `POST /api/system/restart` require desktop `AllowDangerousWebApiOperations=true` and explicit user intent or the single documented stale-runtime recovery allowance. If they return `403`, report the blocker instead of retrying, killing the host, or forcing a close.
- If an exact-script route returns `409` with `DesktopManagerNotReady`, `manager is not ready`, or `Retry the same request in 1-2 seconds`, retry the same route with bounded waiting: about 5 attempts at 2 seconds, or up to `errorDetails.maxSuggestedWaitMs` when present. If the bounded wait expires, inspect that script's status/list entry; when it is open in the desktop editor, one clean `POST /api/scripts/{name}/close-editor` with no body is the documented recovery.
- `POST /api/scripts/{name}/close-editor` is desktop lifecycle control. Use it only when the user explicitly asked to close the desktop editor or a documented recovery step reached that close. Clean/not-open close is allowed without saving and should be attempted at most once for a manager/editor 409. If the user explicitly allows closing with saved state, send body `{ "saveIfModified": true }`; a `403` after that means the safe clean-close path could not complete and saving/stopping still requires desktop `AllowDangerousWebApiOperations=true`. Without explicit save permission, a `409` unsaved-changes response is a blocker to report, not permission to save.
- History request routes are for LLM/external diagnostics, controlled backfill, and cleanup, not normal lifecycle repair: `POST /api/scripts/{name}/history/requests`, `GET /api/scripts/{name}/history/requests/{requestKey}`, and `GET /api/scripts/{name}/history/requests/{requestKey}/bars` are read-only provider-history operations. Only `POST /api/scripts/{name}/history/apply` mutates cache; by default it replaces the submitted time range without clearing existing cached bars outside that range. Send `options.replaceExistingBars=true` for full bars replacement through the same API. It requires desktop `AllowDangerousWebApiOperations=true`.
- do not read `.claude/projects/...`, `tool-results/*.txt`, temp logs, or transcript caches as source-of-truth when the live localhost API exists
- use `./tmp/<folder>` inside the current directory for temp files
- at most one datasource readiness check
- do not use nested shell invocations unless the current wrapper requires them
- avoid inline `curl -d` for JSON mutation routes
- on Windows PowerShell, use `curl.exe`, `Invoke-RestMethod`, or `./api-json.ps1`; do not use bare `curl`, `&&`, `cmd /c`, or `pwsh` for ordinary localhost API calls
- for create/template/ops JSON bodies in PowerShell, prefer `Invoke-RestMethod`, `./api-json.ps1`, or `curl.exe --data-binary "@body.json"`; do not use inline `curl.exe -d "{...}"` or bare `-d @body.json`
- if a PowerShell hashtable or inline JSON command fails, retry by writing a UTF-8 body under `./tmp/<name>.json` in the current workspace and posting that file; do not use `/tmp`, `/workspace/tmp`, `C:\tmp`, or a generic external write helper for localhost request bodies. Prefer a direct shell write such as `@{request=@{dataSourceName='ByBit';securityId='BTCUSDT';interval='5m'}} | ConvertTo-Json -Compress | Set-Content -Encoding utf8 ./tmp/instrument-source.json` over one-line here-strings.
- Do not combine `-d @ops.json` with `--data-binary`
- use example commands from the current workspace when shell quoting is unclear
- do not treat `MissingControlPane` as blocking unless the prompt explicitly requires editable runtime controls
- on strategy/trading prompts, do not switch to `$tslab-script-read-run` or `AGENTS-RunAndAnalyze.md` while the current artifact still has `hasTradeBlocks=false` or only a starter scaffold such as `Src + Close`; stay in authoring until the minimal trade path exists
- do not add a control pane only to silence `MissingControlPane` or to make unrelated `intent-check` / `authoring-quality` output look cleaner
- for generic non-trading analysis or dashboard prompts, route to a minimal visible scaffold first: base candles, one standard price overlay, and one standard separate-pane series. Do not spend the first authoring steps mining handler references for alternative indicator families or candle-type names.
- on Windows PowerShell, avoid raw wildcard path arguments like `rg AGENTS*.md`; resolve the exact file with `rg --files | rg` or `Get-ChildItem -Filter`
- do not start optimization unless the prompt explicitly asks for optimization work
- in optimization work, keep configured ranges separate from the current selected subset; prefer `selectedParameterIds` when the prompt limits the job to one exact subset
- Do not start from an empty directory and a hand-written `.csproj`
- for uploaded indicator visualization work, prefer explicit `/ops` authoring over disabled helper panel templates
- if the prompt asks to find or run an existing script by exact name or query pattern, choose $tslab-script-read-run first; do not open $tslab-script-authoring or create a new script
- if the prompt asks to improve an existing script, make a V2, copy, clone, fork, derive, or mutate a variant, choose `$tslab-script-clone-edit` first; do not call `create-script.ps1` with the destination name as the second argument
- server-side scripts are graph artifacts under `/api/scripts/*`; live `/api/agents/*` routes are only for already-created agent-manager agent instances and do not replace script validate/build/load/run/metrics-summary
- if any `/api/*` call returns `401`, open `$tslab-api-auth` and run the Bearer/CLI flow; do not keep retrying unauthenticated or guess another route
- for option graphs (IOption/IOptionSeries, option source mapping with `isOption: true`), keep the active authoring/clone-edit card and open `$tslab-api-options` for the option pipeline and handler IO
- for live realtime trading tables or actions (own orders/trades/positions, close position, cancel orders), open `$tslab-api-trading`; this is not script backtesting and is not a no-data repair path
- on a `CompletedNoData` / `No instrument selected` / empty-records blocker for an offline/cache/backtesting prompt, stay on the current artifact's mapping/graph/lab-options repair; only open `$tslab-api-datasources` when the user explicitly asked for live provider administration
- improvement, optimize, or compare requests require tested candidates: prove each candidate on the live artifact with measured before/after metrics; do not deliver untested `could try` / `можно попробовать` / `not tested` suggestions when the prompt asks for improvements or your own answer claims tested/optimization results
- do not guess routes such as `GET /api/scripts/{name}/runs`, `GET /api/agents/{scriptName}/results`, `GET /api/agents/{scriptName}/detail-results`, `POST /api/scripts/{name}/graph`, `PUT /api/scripts/{name}/graph`, `POST /api/script-manager/scripts/clone-script`, or `POST /api/script-manager/scripts/clone` without the documented body
- if the prompt names one existing server-side script and only asks to read exact settings fields such as DateReload, useDateReload, interval, or other lab options, choose $tslab-script-read-run first and go straight to GET /api/scripts/{name}/lab-options after health; do not open $tslab-script-authoring or grep docs first
- if the prompt asks how many scripts exist, asks about scripts "in TSLab" or "in its DB", or otherwise refers to scripts without saying workspace files, treat that as a server-side `/api/scripts` task and choose `$tslab-script-read-run` first
- for server-side script list/count tasks, prefer filtered `/api/scripts?query=...&limit=...&type=Script` reads or compact projections over downloading the entire list when the user only needs a small answer
- if the prompt first asks to upload or wire an indicator and then asks for a separate trading script based on it, do not stop on the uploaded indicator or starter viewer artifact; continue into the final strategy/script artifact
- a generic template or starter route is only valid when it clearly matches the requested workflow; do not treat a helper template name as the final deliverable by default
- if an ordinary create-run prompt already gives the exact final script name plus datasource, security, and interval, do not inspect sibling scripts or their ids first; at most one narrow template-catalog projection is allowed only to catch an exact non-disabled workflow match, otherwise blank-create that exact artifact and continue with instrument-source on the same artifact
- for `POST /api/scripts/{name}/instrument-source`, send the concrete mapping body, not a lookup query: `{ "dataSourceName": "ByBit", "securityId": "BTCUSDT", "interval": "5m" }` or `{ "provider": "ByBit", "symbol": "BTCUSDT", "timeframe": "5m" }`; do not send `securityQuery` there
- semantic verification payloads with `requiredTradeFeatures`, `requiredVisualFeatures`, `requiredCompressedIntervals`, `requiredHandlerTypes`, or `requiredBlockTypes` belong to `POST /api/scripts/{name}/intent-check`, not to `POST /api/scripts/{name}/run`

## Choose one operation

- `tslab-script-authoring`
- `tslab-script-clone-edit`
- `tslab-script-read-run`
- `tslab-optimization-run`
- `tslab-portfolio-compare`
- `tslab-indicator-csharp`
- `tslab-indicator-use-in-script`

## Notes

- For common authoring, repair, and delivery rules, rely on `AGENTS-FastPath.md`.
- For one graph-editing question, open `AGENTS-ScriptEditing.md`.
- For lifecycle and metrics, open `AGENTS-RunAndAnalyze.md`.
- For one indicator bootstrap task, use `$tslab-indicator-csharp`.
