# Agent Instructions: TSLab AI Agent

## Quick start

```powershell
# Start TSLab (if not running)
./start-local-tslab.ps1

# Verify API
curl.exe -s http://localhost:5000/api/status

# Create and run a script
./create-script.ps1 "MyStrategy"
./run-lifecycle.ps1 "MyStrategy"
```

## Project structure

- **TSLab API workspace** (root): PowerShell helpers, AGENTS docs, local skills
- **TsLabWorkspace/nn-trading/**: Python NN trading models (PyTorch, TA-Lib, walk-forward)
- **analytics/**: Advanced metrics (Sortino, Calmar, regime detection)
- **optimization/**: Walk-forward, Monte Carlo, grid search
- **risk/**: Position sizing, circuit breaker
- **chart-analyzer/**: 3D crypto charts (Plotly)

## Prerequisites

- TSLab 3.0 installed at `C:\Program Files\TSLab\TSLab 3.0\`
- Python 3.10+ with `pip install -r requirements.txt`
- TSLab Desktop or Console running (API at `http://localhost:5000/api`)

## Instruction boundary

- stay inside the current workspace
- for localhost request-body JSON, do not use generic `write`/editor tools; write bodies with the current shell under `./tmp/...`, then post with `./api-json.ps1`, `./script-api.ps1`, or `./run-lifecycle.ps1`
- never create request bodies under `/tmp`, `/workspace/tmp`, `C:\tmp`, a repo root, or a parent workspace
- source of truth for common operational rules is `AGENTS-FastPath.md`
- manually open follow-up AGENTS/skill files only when the current step really needs them
- do not assume parent/source-tree copies exist outside it
- in packaged workspaces, resolve local docs and local skills first
- in packaged workspaces, open local follow-up docs directly as `./AGENTS-FastPath.md`, `./AGENTS-RunAndAnalyze.md`, or local shipped skills; do not glob or search parent/source-tree paths before trying the local packaged copy
- in packaged exact-artifact tasks, do not list or glob `AGENTS*.md` just to see what is available; open `./AGENTS-FastPath.md` directly and continue from there
- if the prompt names a workspace-local relative path, read that exact current-directory file first. Never add a leading slash, `/workspace` prefix, drive root, repo root, parent path, or `C:\tmp`.
- if a file read/write is rejected as `external_directory`, absolute-rooted, or permission-denied, treat the path shape as wrong and immediately retry the same operation with the workspace-local `./...` path. If a generic read/write tool rewrites `./name` or `./tmp/<folder>/...` to `/name`, `/tmp/...`, `/workspace/tmp/...`, or another workspace, use the current shell with the relative `./...` path instead of switching to API guesses, old artifact names, or absolute temp paths. For generated custom-indicator files under `./tmp/<folder>/`, avoid generic read/write tools entirely; inspect and edit them through the current shell so the path stays inside the packaged workspace.
- if a PowerShell JSON-body attempt fails due to hashtable/quoting syntax, keep the fallback inside the same workspace: write `./tmp/<name>.json` with a UTF-8 here-string and post it with `./api-json.ps1` or `curl.exe --data-binary`; never move the body to `/tmp`, `/workspace/tmp`, or `C:\tmp`.

## Global invariants

- `one phase = one shell step`
- do not use nested shell invocations unless the current shell wrapper explicitly requires them
- on Windows PowerShell, use `curl.exe`, `Invoke-RestMethod`, or `./api-json.ps1` for localhost HTTP; do not use bare `curl`, do not use `&&`, and do not jump into `cmd /c` or `pwsh` just to work around quoting
- for JSON body routes such as `POST /api/script-manager/scripts`, template create/apply, and `/ops`, prefer `Invoke-RestMethod`, `./api-json.ps1`, or `curl.exe --data-binary "@body.json"`; do not use inline `curl.exe -d "{...}"`, and do not use bare `-d @body.json` in PowerShell
- if the user prompt gives an exact script/artifact name, the first create call must use that name byte-for-byte. Do not shorten it, translate it, normalize underscores, invent a friendlier alias, or create a helper script under a different name.
- for an ordinary exact-name create-run in Windows PowerShell, prefer `./create-script.ps1 "<leafName>" ["<parentPath>"]` or `./api-json.ps1 POST /api/script-manager/scripts <bodyFile>` as the first create call; do not start that create phase with raw `Invoke-RestMethod POST /api/scripts`. The helper canonically prefers separate leaf + parent arguments, but when `parentPath` is omitted it also tolerates one foldered full name and auto-splits the last path segment as a forgiving fallback.
- for script-scoped routes on one known artifact, prefer `./script-api.ps1 <METHOD> "<scriptName>" <route> [bodyFile]` or `./script-api.sh ...` so foldered names automatically use the correct ordinary-vs-`/by-name` route shape; this is the default helper for `ops`, `intent-check`, `authoring-quality`, `ui`, `explain`, and similar exact-artifact calls
- for foldered scripts or scripts with spaces, do not hand-build `/by-name/...` URLs and do not inspect graph JSON with fragile PowerShell projections like `$r.`. Use `./script-api.ps1 GET @last-created explain?summary=true`, `ui`, `graph`, or other exact helper routes.
- a local request-body file such as `./ops.json` or `./tmp/ops.json` does not mutate the server artifact by itself; once that file is ready, the very next step must be the matching `POST` on the same artifact, then a fresh live proof route
- if `/ops` or a helper summary says `mustRepairBeforeLifecycle`, `lifecycleAllowed=false`, or `OpenConditionNotConnected`, the next step is the advertised repair route on that same artifact. Do not call `validate`, `build`, `load`, `run`, `metrics-summary`, or optimization before that repair.
- if blank-create or exact-name lookup returns a foldered `resolvedArtifactRouteName`, pin that full server-side path or the packaged `@last-created` helper for later mutations; do not fall back to leaf-only `/api/scripts/{name}/...` routes after create, and do not hand-write numeric-id script routes for lifecycle proof unless that exact endpoint explicitly documents id support
- after one filtered `GET /api/template-blocks?query=...&top=20`, `GET /api/handlers?query=...&top=20`, or `GET /api/handlers/search?...` result already surfaces the likely family, treat it as one focused contract read and mutate the current artifact now instead of repeating broader or synonym searches
- if `/explain` or authoring warnings still show `UnknownExpressionReference`, generic formula aliases, or missing formula inputs, repair the current formula Expression/upstream code names on that same artifact before more handler/template discovery or lifecycle
- for ordinary source/indicator handlers such as `Close`, `Open`, `High`, `Low`, `Bollinger*`, `Highest`, `Lowest`, `StDev`, and `EMA`, use the live `canonicalAddBlockOp` or let `/ops` resolve the handler container; do not persist the raw family name as `blockType`
- if the prompt already gave an exact `intent-check` body and that same body still returns `requiresRepair=true`, `requiredNextMutationRoute`, or non-empty `suggestedRepairOps[]`, the current stage is not complete; keep mutating the same artifact
- if that exact `intent-check` response already exposes non-empty `suggestedRepairOps[]`, prefer `POST /api/scripts/{name}/repair/intent-check` with that same request body before manually copying those ops into `/ops`
- if that exact prompt-specific `intent-check` already shows the required feature families as present but `authoringQualityRequiresRepair=true` or `authoring-quality` still reports finishing blockers such as `NoOptimizationMappings` or `DuplicateGraphColors`, the current artifact is still unfinished; follow `requiredNextMutationRoute` on the same artifact before final proof
- if the prompt says parameters should be optimization-ready, convenient for later optimization, or that a later phase will optimize the same artifact, treat `NoOptimizationMappings` as a blocking task-level gap even when `MissingControlPane` is non-blocking
- if the prompt says offline, cached, local, or backtesting data, provider connection state is diagnostic only. Do not read datasource `settings`/`schedule`, do not connect, disconnect, reload, reschedule, wait-loop, switch providers, or add `X-TSLab-Provider-Admin-Confirm`; use at most one `GET /api/datasources/{name}/status` if datasource readiness must be checked, then repair the current artifact's graph/mapping/lab-options first. Do not claim missing cache from `CompletedNoData`, `records=[]`, `isConnected=false`, or `instrumentsLoaded=0` alone.
- avoid inline `curl -d` for JSON mutation routes
- Do not combine `-d @ops.json` with `--data-binary`
- use `./tmp/<folder>` for local temp files
- at most 2 web sources
- After the second web source, stop browsing and use the live API plus current-workspace docs
- Dangerous desktop lifecycle routes are opt-in and not part of ordinary script authoring. Do not call `POST /api/system/restart` unless the user explicitly asked for desktop lifecycle control or a documented stale-runtime recovery step reached its single restart allowance. Do not call `POST /api/scripts/{name}/close-editor` unless the user explicitly asked to close the desktop editor or a documented desktop-manager/editor-409 recovery step reached one clean close attempt. A no-body clean close does not save; save/stop close options require explicit user permission and desktop `AllowDangerousWebApiOperations=true`. If the API returns `403` or an unsaved/running-editor `409`, report that blocker instead of retrying, killing the host, or forcing a close.
- Mapping data reload is also a dangerous desktop operation. Use only `POST /api/scripts/{name}/mappings/reload-data` with a `mappingKey` from `GET /api/scripts/{name}/mappings`, only when the user explicitly asks to refresh/re-download data or a stale/corrupt cache is proved, and only when desktop `AllowDangerousWebApiOperations=true`. Do not send `reloadData` to `run` or `optimization/start`.
- History request workflow is separate from `mappings/reload-data`: use `POST /api/scripts/{name}/history/requests`, `GET /api/scripts/{name}/history/requests/{requestKey}`, and `GET /api/scripts/{name}/history/requests/{requestKey}/bars` to request/poll/read provider bars for diagnostics, controlled backfill, or LLM cleanup. Only `POST /api/scripts/{name}/history/apply` mutates the platform cache; by default it replaces the submitted time range without clearing cached bars outside that range. Send `options.replaceExistingBars=true` for full bars replacement through the same API. It requires desktop `AllowDangerousWebApiOperations=true`.

## Key gotchas agents miss

- **TSLab Console vs Desktop**: Console (`TSLabConsole.exe`) runs headless API only. Desktop (`TSLabApp.exe`) loads instruments and shows charts. Scripts created via API may not show trades if Console has `instrumentsLoaded=0`.
- **Handler binding**: When creating blocks via `/ops`, the `handlerTypeName` in `AddBlock` may not persist. If `explain` shows wrong handler, use `PUT /api/scripts/{name}/json` with fixed XML `HandlerTypeName` attribute in the viewModel.
- **GreaterHandler/LessHandler ports**: Use port names `"Input0"` and `"Input1"` (not `"1"` and `"2"`). The handler contract shows `name: ""` but the actual port names are `Input0`/`Input1`.
- **TwoOrMoreInputsItem**: Use `typeName="GreaterHandler"` with `blockType="TwoOrMoreInputsItem"` for comparison blocks. Do not use `typeName="TwoOrMoreInputsItem"` alone.
- **Graph XML handler fix**: If `explain` shows wrong `HandlerTypeName`, get graph via `GET /api/scripts/{name}/graph`, fix the XML string, then `PUT /api/scripts/{name}/json` with the corrected JSON.
- **NNFormulaIndicator**: Must have `HandlerTypeName="NNFormulaIndicator, NNFormulaIndicator"` in the EditItem XML. Generic `ConverterItem` handler will not work.
- **Lab options not persisting**: Set via `POST /api/scripts/{name}/lab-options` with `{ "options": { "initDeposit": 60, "tradeMode": 1 } }`. Verify via `GET /api/scripts/{name}/graph` → `options.initDeposit`.
- **Datasource instruments**: `instrumentsLoaded=0` means no instruments are cached. In Desktop, manually add instruments via UI. In Console, instruments may not load without schedule enabled.
- **Python NN trading**: Use `python train_solusdt.py` for single-instrument walk-forward, or `python run_all_instruments.py` for multi-instrument. Requires `data/binance_*_3tf.csv` files.
- **3D visualization**: Self-contained HTML files in `TsLabWorkspace/nn-trading/`. Open via `file:///` protocol. Three.js r128 CDN required.

## Status first

- API base: `http://localhost:5000/api`
- first health check: `GET /api/status`
- `GET /api/status` uses stable process identity fields. Compare `response.data.processId` or `response.data.apiInstanceId` across calls to detect a real restart; `response.data.startTime` and `response.data.processStartedAtUtc` are process start times, while `response.data.serverTimeUtc` is only the response timestamp.

## Canonical first call by operation

- authoring: for an ordinary exact-name create-run, make at most one narrow `GET /api/scripts/templates` projection only when the requested workflow may exactly match a listed non-disabled template. Use the advertised template route only on an exact workflow match; otherwise create the artifact with the exact requested name via `./create-script.ps1 "<leafName>" ["<parentPath>"]` or `POST /api/script-manager/scripts`, then use `POST /api/scripts/{name}/instrument-source` on the current artifact. If the prompt points to an exact workspace-local spec/input file, read that file before create/mutate instead of substituting memory or an external copy.
- indicator-csharp: `GET /api/sdk/contracts/indicator`
- indicator-use-in-script: `GET /api/handlers/{typeName}` and `GET /api/agent-manager/securities?dataSourceName=...&query=...&limit=20`
- read-run: open the read-run phase card
- exact read-only settings on an existing server-side script: after GET /api/status, call GET /api/scripts/{name}/lab-options first; do not open authoring docs or grep source-tree paths before that first read
- optimization: open the optimization phase card
- portfolio: open the portfolio compare phase card

## Fields to read

- `workflowHints`
- `createMethod`
- `response.scriptName`
- `response.defaultOptimizationRequest`
- `response.jobId`

## Indicator route notes

- use `$tslab-indicator-csharp` for the custom indicator in C# route
- Do not start from an empty directory and a hand-written `.csproj`
- Use a template route only when `GET /api/scripts/templates` clearly exposes a matching workflow template. Do not use near-match templates.
- For a trading script based on an uploaded/custom indicator handler, prefer `POST /api/scripts/templates/uploaded-indicator-signal-starter` as the first scaffold after handler verification. That create route creates/maps the artifact; do not blank-create first. Send a direct JSON body with `name`, `dataSourceName`, `securityId`, `interval`, `handlerTypeName`, and `starterKind`, not a `{ "request": ... }` wrapper. For visual/analysis indicator scripts, chart overlays, dashboards, or "show this indicator with controls" prompts without entry/exit/trading logic, do not use that trading starter; blank-create, map source data, and add the handler, graph links, and controls with explicit `/ops`.
- control-pane authoring is explicit `/ops` work; do not assume helper panel templates will build runtime controls for you
- for control panes, choose concrete control types explicitly and never use `ControlParameterType.NotDefined`, implicit types, or narrative/helper labels inside the pane
- Do not spend more than 3 handler reads before the first real graph mutation

## Shell and helper rules

- use example commands from the current workspace when the shell syntax is unclear
- prefer local helpers over ad hoc quoting experiments
- keep all work in the same packaged workspace root
- keep shell `workdir` at `.` or the exact last successful packaged-workspace path; do not hand-type timestamped absolute workspace paths from memory
- use workspace-local relative paths for all prompt inputs and request bodies. Keep request bodies under `./tmp/...` or `./ops.json`; never use absolute temp roots, drive roots, repo roots, `/workspace/tmp/...`, `C:\tmp\...`, or parent-workspace paths.
