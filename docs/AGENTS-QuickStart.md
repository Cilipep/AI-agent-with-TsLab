# QuickStart: phase-by-phase TSLab API

Use this file when context is tight.

## Skill loading

- Read `AGENTS.md` or `$tslab` first.
- Open exactly one operation skill:
  - `$tslab-script-authoring`
  - `$tslab-indicator-csharp`
  - `$tslab-indicator-use-in-script`
  - `$tslab-script-read-run`
  - `$tslab-optimization-run`
  - `$tslab-portfolio-compare`
- If the skill tool fails, continue with `AGENTS-FastPath.md`.

## Core rule

- `one phase = one shell step`
- Do not combine `create + run` in one shell step.
- Do not combine `start + best + apply` in one shell step.
- Base URL: `http://localhost:5000/api`
- Bootstrap with `GET /api/status` or `GET /api/status/health`.
- For restart detection, compare `GET /api/status` `response.data.processId` or `response.data.apiInstanceId` before/after. `startTime` and `processStartedAtUtc` are stable process-start values; `serverTimeUtc` is only the response time.
- In packaged `ai-agent` workspaces, if that readiness probe still fails with connection-refused or another direct localhost transport error, run `./start-local-tslab.ps1` on PowerShell or `./start-local-tslab.sh` on POSIX from the current workspace, then retry `GET /api/status` once before any nested shell experiments, local file reads, or alternate-port guesses.
- On Windows PowerShell, use `curl.exe`, `Invoke-RestMethod`, or `./api-json.ps1`; do not use bare `curl`, `&&`, or `cmd /c` for ordinary localhost API calls.
- For JSON mutation bodies in Windows PowerShell, prefer `Invoke-RestMethod`, `./api-json.ps1`, or `curl.exe --data-binary "@body.json"`. Do not use inline `curl.exe -d "{...}"` or bare `-d @body.json`.
- Dangerous desktop lifecycle routes, including `POST /api/system/restart` and `POST /api/scripts/{name}/close-editor`, require desktop `AllowDangerousWebApiOperations=true` and must not be used for ordinary graph repair. If they return `403` or `409`, stop that dangerous action and report the concrete preflight/setting blocker.
- For packaged `./api-json.ps1` / `./api-json.sh`, keep canonical examples in `/api/...` form, but the helpers also normalize localhost-relative `scripts/...` and `/scripts/...` routes back under `/api/` when a model drops that prefix.
- For exact script-scoped routes on one known artifact, prefer `./script-api.ps1 <METHOD> "<scriptName>" <route> [bodyFile]` or `./script-api.sh ...` instead of hand-assembling `/api/scripts/<route>/by-name/...` for foldered names.
- A local `./ops.json`, `./tmp/ops.json`, or similar request-body file is only input for the next API call; it does not change the live server-side artifact until the matching `POST` succeeds.
- If an exact `intent-check` response already gives `suggestedRepairOps[]`, prefer `POST repair/intent-check` on that same artifact with the same request body before manually reposting those ops through `/ops`.
- Do not switch to alternate local ports such as `5001` unless the user explicitly gave that URL.
- If the current artifact already exposes `mustMutateCurrentArtifact`, `mustNotStopBeforeMutation`, `shouldAvoidExtraDiscovery`, or `requiredNextMutationRoute`, treat that as the controlling next-step contract. Do not reopen QuickStart, examples, or handler catalogs before that mutation on the same artifact.
- If blank-create or an exact-name lookup returns a foldered `resolvedArtifactRouteName`, pin that exact full path or the packaged `@last-created` helper for later mutations. Do not drop back to a leaf-only `/api/scripts/{name}/...` route after create, and do not hand-write numeric-id script routes for lifecycle proof unless that exact endpoint explicitly documents id support.

## Phase starts

- Create:
  - if the current artifact already exists and its latest localhost response says `BlankGraph`, `SourceOnlyGraph`, or exposes `requiredNextMutationRoute`, do not re-plan from this section; mutate that same artifact now
  - template discovery: `GET /api/scripts/templates`
  - if an advertised template matches the requested workflow: `POST /api/scripts/templates/{templateName}`
  - for a generic multi-indicator chart/dashboard: `POST /api/script-manager/scripts`, then build panes, graph links, and any runtime controls explicitly with `/ops`
  - otherwise: `POST /api/script-manager/scripts`
- Custom indicator in C#:
  - `GET /api/sdk/contracts/indicator`
  - if present, read `response.data.workflowHints`
  - after upload and when a trading script is needed: `GET /api/handlers/{typeName}`
- Run:
  - `POST /api/scripts/{name}/validate`
- Optimization:
  - if `defaultOptimizationRequest` is already known: `POST /api/scripts/{name}/optimization/start`
  - otherwise: `GET /api/scripts/{name}/lab-options`
- Portfolio:
  - `POST /api/portfolios/backtesting/{id}/clone`

## Fields to read before continuing

- Create:
  - if the current artifact already exists and its latest localhost response says `BlankGraph`, `SourceOnlyGraph`, or exposes `requiredNextMutationRoute`, do not re-plan from this section; mutate that same artifact now
  - `response.scriptName`
  - `response.scriptId`
  - if present, `response.defaultOptimizationRequest`
  - fallback: `response.name`, `response.id`
- Run:
  - `response.data.netProfit`
  - `response.data.allTrades`
  - `response.data.profitFactor`
  - `response.data.maxDrawdownPct`
- Optimization start:
  - `response.jobId`
  - `response.scriptName`
  - `response.status`
- Best:
  - `response.parameterValues`
  - `response.suggestedValue`
- Apply:
  - `response.appliedParameters`

## Must-keep rules

- Treat `/api/scripts/*` as name-based.
- Use `GET /api/scripts?query=...&limit=20` for discovery.
- Do not scan repo files to discover server-side scripts.
- If the prompt points to a workspace-local spec, prompt file, or other local input artifact, read that exact local file before create/mutate. Do not substitute memory, an external copy, or a guessed sibling path.
- After that exact local-file read, keep the authored artifact anchored to the file contents. Do not continue as if the file were unread, and do not finalize while the required indicator/logic still ignores the named local spec.
- Do not read or create local `scripts/*.cs` files for server-side authoring.
- If the user explicitly asked for a custom indicator in C#, use a temporary build workspace and upload the DLL. Do not place indicator source files in repo `scripts/`.
- For a custom indicator in C#, use at most 2 web sources before moving to code: one formula explanation and one code/reference implementation.
- After the second web source, stop browsing even if one or both sources failed.
- If `/api/sdk/contracts/indicator` returns `workflowHints`, follow them directly instead of additional discovery.
- Bootstrap the temp workspace from `./.opencode/skill/tslab-indicator-csharp/assets/`; the copied assets themselves are shell-neutral, and when PowerShell or `pwsh` is available `./.opencode/skill/tslab-indicator-csharp/scripts/new-indicator-workspace.ps1` can scaffold them automatically.
- Before creating or editing any local indicator files, the first local step must be bootstrap from those packaged assets/scripts.
- If the current workspace already contains `./.opencode/skill/tslab-indicator-csharp/`, use that packaged copy and do not switch to a parent/source-tree skill directory outside the workspace.
- Do not start from an empty directory and a hand-written `.csproj`; only fall back to manual project scaffolding if the packaged assets are unavailable.
- Unless `/api/sdk/contracts/indicator` or the available assemblies explicitly confirm drawing or canvas APIs for the current runtime, implement the first version as a stream-compatible handler and render it with explicit `/ops` on the target artifact.
- For Pine/Markdown/local-spec visual indicators, prefer the minimum stream-compatible overlay/control-pane version first; do not begin with drawing-only interfaces or types such as `IIndicator`, `TSLab.Script.Panes`, `Line`, or `LineFill` unless the runtime contract already confirmed them.
- Handler color/appearance parameters do not draw chart lines by themselves. The script still needs explicit `GraphLink` entries for visible plotted series.
- For multi-line or multi-band visual indicators, default to separate handlers per semantic line/group and assemble them through explicit `AddBlock` + `AddGraphLink` `/ops` batches instead of a handler-level visible-line selector.
- If the indicator has many possible outputs, do not plot all of them by default. Group related outputs by pane and keep helper/diagnostic series hidden or disconnected unless the user explicitly asked to show them.
- For the first live proof, keep custom stream handlers bounded. Avoid per-bar nested `rows * lookback` scans across the full history; prefer `O(n * lookback)` or better algorithms, modest safe defaults, and cached rolling calculations. For histogram/profile/binning handlers with `Rows`-like parameters, bound the bins and use rolling or incremental state for the first proof. If build/load/run later says the script is still initializing, repair every plotted/exported handler that still uses the slow algorithm, rebuild/upload the whole DLL, and rerun lifecycle on the same artifact.
- Before coding, summarize what the indicator computes, one short formula/algorithm explanation, which plotted outputs are needed, which outputs belong on the main price pane versus separate panes, which pane groups keep the chart readable, which outputs can stay hidden, and which parameters must stay editable.
- Put custom-indicator display names and docs into the scaffolded `Properties/Resources.resx`: `<TypeName>.Name`, `<TypeName>.Description`, `<TypeName>.Formula`, `<TypeName>.Meaning`, `<TypeName>.Plot`, `<TypeName>.<ParamName>.Name`, `<TypeName>.<ParamName>.Description`, and `<TypeName>.<ParamName>.Effect`. For bilingual Russian/English docs in single-DLL upload, keep the scaffolded resource structure, fill `<key>.en` and `<key>.ru` in this same neutral resource file, and keep the unsuffixed key as English fallback. Every display/doc key you keep or add must have base + `.en` + `.ru`; replace scaffold placeholder values with task-specific English and Russian text before building. Do not leave `Replace this...`, `Describe...`, `Замените...`, or `Опишите...` placeholder docs in the final DLL. Do not replace `Resources.resx` with a minimal file that deletes `.en`/`.ru` variants. Do not rely on satellite culture resources unless they are deployed with the DLL. Do not add guessed `Description`, `DisplayName`, or `ResourceKey` attributes.
- If DLL upload returns `code=IncompleteBilingualResourceDocs` or `missingResourceKeys=[...]`, edit `Properties/Resources.resx` once to add every listed base/`.en`/`.ru` key, then rebuild and upload once; do not iterate one missing key per upload.
- If later optimization of numeric custom-indicator parameters may be needed, keep those `HandlerParameter(...)` attributes optimizable; do not add `NotOptimized=true` unless the parameter is intentionally fixed.
- In a sandboxed runner workspace, place the temporary indicator workspace under `./tmp/<folder>` inside the current directory (PowerShell equivalent: `.\tmp\<folder>`) instead of any parent or external directory.
- After bootstrap, inspect and edit generated indicator files with the current shell and relative `./tmp/<folder>/...` paths. Do not use generic read/write/editor tools on `./tmp/<folder>/<Class>.cs`, `IndicatorHandlers.csproj`, or `Properties/Resources.resx`, because they can rewrite the file to `/tmp/...`, `/workspace/tmp/...`, `C:\tmp\...`, or another workspace.
- Canonical DLL upload route is `POST /api/indicator-dlls/{name}`. A compatibility alias `POST /api/indicator-dlls` is also accepted with multipart `file` and optional `name`.
- After DLL upload, read `response.data.handlerTypeNames` or `GET /api/indicator-dlls/{name}/handlers`.
- If upload response also exposes `response.data.nextStepHint`, read it. Treat `response.data.suggestedStarterStrategyRoutes` as trading-strategy options only.
- If the user wants a trading script or strategy from the uploaded handler, prefer `POST /api/scripts/templates/uploaded-indicator-signal-starter` as the first scaffold after `GET /api/handlers/{typeName}`. The create route creates the named script and maps source data itself; do not blank-create or call `instrument-source` first. Use a direct JSON body with `name`, `dataSourceName`, `securityId`, `interval`, `handlerTypeName`, and `starterKind`, not a `{ "request": ... }` wrapper. On PowerShell, write `./tmp/starter.json` and call `./api-json.ps1 POST /api/scripts/templates/uploaded-indicator-signal-starter ./tmp/starter.json`. For visual/analysis indicator scripts, chart overlays, dashboards, or "add this indicator with controls" prompts without entry/exit/trading logic, do not use this starter; blank-create, map source data, and add handler blocks, graph links, and controls with explicit `/ops`.
- After DLL upload, do not open extra AGENTS example files before the first starter route or `/ops` batch.
- If the user also wants a trading script from the uploaded indicator, load `$tslab-indicator-use-in-script`.
- For that trading script, configure the tradable instrument with `POST /api/scripts/{name}/instrument-source`, not `/source`.
- If the prompt already names the instrument, reuse it directly as `securityId` or the request alias `symbol`; only if the exact id is still unknown, query `GET /api/agent-manager/securities?dataSourceName=...&query=...&limit=20`. For offline/cached proof, keep that exact provider/cache id; do not display-normalize ids by adding separators or translating them. Do not send `securityQuery` to `instrument-source`; `securityQuery` belongs to that GET lookup route, not to the mapping POST.
- `POST /api/scripts/{name}/instrument-source` always persists datasource/security mapping. If the body also includes `interval` or `timeframe`, the same call persists the script base interval in `lab-options` too. If you omit `interval` / `timeframe`, instrument-source by itself does not guarantee the script base interval. If the prompt names an exact base timeframe, send it in the instrument-source body when possible; otherwise post a short `/lab-options` patch such as `{ "intervalCode": "M5" }`, then confirm the interval before the first large `/ops` batch.
- During performance repair, keep the requested datasource/security/base timeframe fixed. You may reduce history length, date window, or indicator defaults, but do not switch the artifact from the prompt timeframe to a faster interval.
- For offline/cached visual indicator or analysis proof, stay on script routes (`validate -> build -> load -> run`, then `metrics-summary`, `ui`, `authoring-quality`, and required `intent-check`). Do not create or mutate `agent-manager/agents` unless the user explicitly asked for a runtime agent.
- Immediately after `instrument-source` on a blank or source-only artifact, the default next step is the first real `POST /api/scripts/{name}/ops` batch. Do not spend that first scaffold turn on unfiltered `GET /api/handlers`, unfiltered `GET /api/template-blocks`, `GET /api/handlers/search`, or other broad catalog browsing; allow at most one exact/focused contract read first when one still-missing family is genuinely unclear.
- After one filtered `template-blocks?query=...`, `handlers?query=...`, or `handlers/search?...` result already shows the likely family, stop the synonym hunt and mutate the current artifact now.
- If `/explain` or authoring checks still report `UnknownExpressionReference`, generic formula aliases, or missing formula inputs, repair the current formula Expression/upstream code names on that same artifact before more handler/template browsing or lifecycle.
- Use the current shell's native HTTP client for small JSON bodies. If a doc or API hint shows a PowerShell example, treat it as one shell variant and send the same route/body with `curl` or another native client on macOS/Linux.
- Do not wrap API calls in nested shell invocations such as `powershell -Command`, `bash -lc`, or `sh -lc` when the current shell can call the route directly.
- When a `curl` URL contains query parameters such as `?query=...&limit=20`, quote the whole URL so shells do not split on `&`.
- For JSON mutation bodies in PowerShell, prefer `Invoke-RestMethod` or a UTF-8 file with `curl --data-binary`; avoid inline `curl -d "{...}"` because quoting can corrupt the body.
- If you send a JSON body from a file with `curl`, use exactly one request-body flag, for example `curl --data-binary "@ops.json" ...`. Do not combine `-d @ops.json` with `--data-binary` in the same command.
- If a template discovery response includes example commands, reuse the advertised route/body directly. PowerShell examples can be used verbatim only when the current shell is PowerShell; otherwise translate the same route/body into the current shell's native client.
- If `curl` is needed on Windows PowerShell, use `curl.exe`, not the `curl` alias.
- Omit `Authorization` on trusted localhost unless auth is actually required.
- During optimization, never create or copy scripts.
- If the server exposes a non-disabled template route that exactly matches the requested workflow, prefer that route over rebuilding the same structure with low-level `/ops`.
- If `GET /api/scripts/templates` returns `nextStepHint` or example request bodies, use the advertised `POST` route immediately.
- If `GET /api/scripts/{name}/parameters` already says `optimizationReady=true` and the current task explicitly asks to optimize, choose `selectedParameterIds` only from the exact current `response.data.parameters[].id` values, start one fresh `POST /api/scripts/{name}/optimization/start`, and continue only the returned `jobId`. Do not detour into `GET /api/scripts/optimizations` or `GET /api/scripts/{name}/optimizations`.
- After blank create, the next shell step must be either a matching template-apply route or the first `POST /api/scripts/{name}/ops`.
- Do not spend more than 3 handler reads before the first graph mutation on a brand-new blank script.
- Do not call `/explain` on a brand-new blank script before the first `/ops` batch.
- For ordinary source/indicator handlers such as `Close`, `Open`, `High`, `Low`, `Bollinger*`, `Highest`, `Lowest`, `StDev`, and `EMA`, do not persist the raw family name as `blockType`; use live `canonicalAddBlockOp` or let `/ops` resolve the handler container.
- If several blocks must share one editable and optimizable parameter, use `ParameterShareItem` or `OneToManyParametersShareItem`, wire it with `Connect` or `ConnectByInputName`, and expose it through `AddControlPane` plus `AddControlLink`.
- If the prompt explicitly requires parameters on a control pane, the task is not complete until the artifact has a real control pane plus real control links to the intended parameters. `AddControlPane` by itself, an empty pane, or a pane that is not wired to any real parameter does not satisfy that requirement.
- If the prompt names an exact custom handler/class, the uploaded handler and final script blocks must use that exact name byte-for-byte; a near-match helper name is not completion proof.
- For every control link, choose a concrete control type explicitly: numeric/int/double -> numeric up-down, bool -> checkbox/toggle, enum/allowed values -> combo/list. Never send `ControlParameterType.NotDefined`, `Type="NotDefined"`, or an omitted/implicit control type.
- Keep control captions short and literal. Do not add helper/narrative pane text such as `Master control from ...`, `Shared ... period`, `Block: Parameter`, or template explanation labels unless the user explicitly asked for those labels.
- Prefer `GET /api/scripts/{name}/metrics-summary` for final numbers.
