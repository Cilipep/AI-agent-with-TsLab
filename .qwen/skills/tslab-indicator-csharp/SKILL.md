---
name: tslab-indicator-csharp
description: "Phase card for implementing a custom TSLab indicator in C#, uploading it into TSLab, verifying the handler, then using it from a server-side script."
---

# TSLab Custom Indicator in C#

## When to load

- The user explicitly asked to implement a new indicator in C# and load it into TSLab.

## Workspace scope

- In a sandboxed runner workspace, keep the temporary indicator workspace under `./tmp/<folder>` inside the current directory (PowerShell equivalent: `.\tmp\<folder>`).
- Use that same relative `./tmp/<folder>` path for bootstrap, edit, build, upload, and request bodies. Never switch it to absolute `/tmp/<folder>`, `/workspace/tmp/<folder>`, `C:\tmp\<folder>`, or a parent-directory temp path.
- After bootstrap, read and edit generated indicator files with the current shell and the original relative `./tmp/<folder>/...` path. Do not use generic read/write/editor tools for `./tmp/<folder>/<Class>.cs`, `IndicatorHandlers.csproj`, or `Properties/Resources.resx`; those tools can rewrite the path to `/tmp/...` or another workspace before you notice.
- If a generic read/write tool rewrites a generated indicator file such as `./tmp/<folder>/<Class>.cs` to `/tmp/<folder>/<Class>.cs`, `/workspace/tmp/<folder>/<Class>.cs`, `C:\tmp\<folder>\<Class>.cs`, or another workspace, stop using that tool for the indicator workspace. Retry the same read or edit with the current shell and the original relative `./tmp/<folder>/...` path.
- Request-body files such as `lab-options.json`, upload metadata, starter bodies, and `/ops` payloads are generated in the current workspace. Write them directly under `./tmp/...`; never read, probe, or write `/tmp/*.json`, `/workspace/tmp/*.json`, `/tmp/lab-options.json`, `C:\tmp\*.json`, or parent-workspace temp files.
- Do not target parent or external directories from a sandboxed workspace; they can be rejected as `external_directory` by the model sandbox.
- Keep all scratch code, request bodies, and temp build artifacts under that `./tmp/<folder>` workspace only. Never write temporary files under `./.opencode/skill/`, `./.agents/skills/`, `./.qwen/skills/`, or any docs/instruction directory.

## First call

- `GET /api/sdk/contracts/indicator`
- This route is intentionally compact. Do not call full `/api/sdk/contracts` during the first pass; use the shipped scaffold and call `/api/sdk/types/details?name=...` only for one exact missing type after a concrete build error.

## Fields to read

- runtime handler interfaces from `response.data`
- compact template snippets from `response.data.templates`
- if present, `response.data.workflowHints`
- after upload:
  - `response.data.handlerTypeNames`
  - `response.data.nextStepHint`
  - `response.data.suggestedStarterStrategyRoutes`
  - or `GET /api/indicator-dlls/{name}/handlers`

## Next allowed call

- use at most 2 web sources:
  - one formula explanation
  - one code/reference implementation
- after the second web source or the second source failure/`404`, stop browsing immediately and move to `/api` plus code/bootstrap even if some details remain implicit
- if `response.data.workflowHints` is present, follow that route/order directly
- create a temporary class library outside repo `scripts/`
- after the SDK contract read, the first local filesystem step must run the packaged bootstrap script for the temp indicator workspace. Do not manually create the folder, glob/read the asset templates, or scan host runtime directories first.
- Arity choice is part of the contract, not a style preference:
  - if the prompt/spec needs one instrument's candles, OHLCV, volume, highs/lows, bar metadata, or Pine-style `high/low/close/volume`, use `-Arity security`;
  - use `-Arity four` only when the prompt explicitly provides four independent numeric input streams that are not the OHLCV fields of the same instrument;
  - if unsure between `security` and `four` for market bars, choose `security`.
- bootstrap the temp workspace from:
  - `./.opencode/skill/tslab-indicator-csharp/assets/IndicatorHandlers.csproj` plus one matching `./.opencode/skill/tslab-indicator-csharp/assets/StreamIndicator*.cs` template from the current workspace
  - on Windows cmd-like shells: `./.opencode/skill/tslab-indicator-csharp/scripts/new-indicator-workspace.cmd ./tmp/<folder> security|one|three|four <HandlerTypeName>`
  - on PowerShell: `./.opencode/skill/tslab-indicator-csharp/scripts/new-indicator-workspace.ps1 -Destination ./tmp/<folder> -Arity security|one|three|four -ClassName <HandlerTypeName>`
  - on POSIX shells: `./.opencode/skill/tslab-indicator-csharp/scripts/new-indicator-workspace.sh ./tmp/<folder> security|one|three|four <HandlerTypeName>`
  - the bootstrap also copies `Properties/Resources.resx`; edit it for indicator and parameter display text instead of adding guessed description/display attributes
  - the copied assets themselves are shell-neutral and can be used from macOS/Linux even without PowerShell
- if the current shell is already Windows PowerShell, invoke the scaffold script directly in that shell and do not assume `pwsh` exists
- if a cmd-like shell reports that `Copy-Item`, `pwsh`, or other PowerShell-only commands are unavailable, switch to `new-indicator-workspace.cmd` instead of hand-writing a new `.csproj`
- if the current shell is not PowerShell, do not use PowerShell-only commands such as `Copy-Item`, `ConvertFrom-Json`, `Select-Object`, or `Out-Null`; use the shell-matching wrapper (`.cmd` or `.sh`) and the shell's native HTTP/file commands
- in Windows PowerShell 5.1, do not chain commands with `&&`; keep bootstrap, edit, build, upload, and verify in separate shell steps
- before creating or editing any local indicator files, the first local step must be bootstrap from those packaged assets/scripts
- the bootstrap script already writes the `.csproj` with safe runtime reference paths. Do not use `glob`, `ls`, `Get-ChildItem`, or file reads against host/runtime/build-output directories from a sandboxed runner; those paths may be outside the current workspace and can be rejected as `external_directory`.
- if the current workspace already contains `./.opencode/skill/tslab-indicator-csharp/`, use that current-workspace packaged copy and do not switch to a parent or source-tree skill directory outside the workspace
- Do not start from an empty directory and a hand-written `.csproj`; only fall back to manual project scaffolding if the packaged assets are unavailable
- the packaged bootstrap must resolve runtime assemblies through its own helper logic, not through stale `ai-agent/tmp`, `agent-ws`, or old matrix-run scratch DLLs. If the generated `.csproj` points into a scratch folder, rerun the packaged bootstrap from the current workspace or use explicit runtime reference environment variables; do not continue with that project.
- if the prompt also named a workspace-local markdown/spec file, read that exact local copy before coding or scaffolding. If the workspace already contains `./tmp/inputs/<name>`, prefer that local copy over any remembered Desktop/original path.
- do not load full SDK/type dumps before writing the first stream handler; the shipped scaffold plus compact contract are enough for the first build attempt
- unless `/api/sdk/contracts/indicator` or the available assemblies explicitly confirm drawing or canvas APIs for the current runtime, implement the first version as a stream-compatible handler and render it with explicit `/ops` on the target artifact
- for indicators that compute from one instrument's candles, OHLCV, volume, or bar metadata, bootstrap with `-Arity security` and edit `StreamIndicatorSecurityInput.cs`; `ISecurity` exposes `Bars`, `ClosePrices`, `HighPrices`, `LowPrices`, `OpenPrices`, and `Volumes`, so do not split one candle stream into four numeric graph inputs
- use only attributes exposed by `/api/sdk/contracts/indicator`: `HandlerCategory`, `InputsCount`, `Input`, `OutputType`, `OutputsCount`, and `HandlerParameter`. Do not add guessed attributes such as `Description`, `DisplayName`, or `ResourceKey`.
- for Pine/Markdown/local-spec visual indicators, prefer the minimum stream-compatible overlay/control-pane version first; do not begin with drawing-only interfaces or types such as `IIndicator`, `TSLab.Script.Panes`, `Line`, or `LineFill` unless the runtime contract already confirmed them
- handler color/appearance parameters do not draw chart lines by themselves; the script still needs explicit `GraphLink` entries for visible plotted series
- for multi-line or multi-band visual indicators, default to separate handlers per semantic line/group and assemble them with explicit `AddBlock` + `AddGraphLink` `/ops` batches instead of a handler-level visible-line selector
- if the indicator has many possible outputs, do not plot all of them by default; group related outputs by pane and keep helper/diagnostic series hidden or disconnected unless the user explicitly asked to show them
- for the first live proof, keep custom stream handlers bounded. Avoid per-bar nested `rows * lookback` scans across the full history; prefer `O(n * lookback)` or better algorithms, modest safe defaults, and cached rolling calculations. For histogram/profile/binning handlers with `Rows`-like parameters, bound the bins and use rolling or incremental state for the first proof. If build/load/run later says the script is still initializing, repair every plotted/exported handler that still uses the slow algorithm, rebuild/upload the whole DLL, and rerun lifecycle on the same artifact.
- `AddGraphLink` is pane-only wiring. If a destination is a block input such as `Src`, `SECURITYSource`, `High`, `Low`, `Volume`, or `Input0`, use `Connect` / `ConnectByInputName` instead of `AddGraphLink`.
- after DLL upload, if the indicator exposes several outputs or families, prove the exact exported handler/output contract through the upload response, `GET /api/indicator-dlls/{name}/handlers`, and `GET /api/handlers/{typeName}` before inventing separate output blocks or chart lines. Do not assume every plotted line is a standalone block unless the current host already proved that shape.
- if the indicator already runs and the remaining user request is only to expose its real parameters for runtime editing, use explicit `/ops` only: `AddControlPane` plus one `AddControlLink` per real parameter.
- every `AddControlLink` needs concrete `dataXml` with a numeric/bool/enum control type on each `Property`, never `ControlParameterType.NotDefined` or an omitted type, and captions should be short parameter names without narrative/helper labels.
- Minimal control-link shape: `{ "op":"AddControlLink", "blockId":"<parameterBlock>", "toPaneKey":"<paneKey>", "paramName":"<ParameterName>", "dataXml":"<EditItem><Property PropertyName=\"<ParameterName>\" ControlType=\"IntUpDown\" DisplayName=\"<ParameterName>\" /></EditItem>" }`. Use `DoubleUpDown` for double/decimal parameters and `CheckBox` for bool parameters; do not use `<Properties>...</Properties>` wrappers.
- if the prompt asks for runtime-editable controls, editable parameters, or a control pane, final proof must show `authoring-quality` `controlPaneCount > 0` and real `AddControlLink` entries for the handler parameters. Metrics, chart lines, or `controlPaneCount=0` are not completion for that request.
- if the prompt gave an exact destination folder such as `AI`, create the script there on the first create call. Pass the leaf script name and the parent folder path separately; do not first create a root-level artifact with the same leaf name and plan to move or recreate it later.
- if the prompt gives an exact datasource, security, and timeframe such as `ByBit BTCUSDT 5 min`, final proof must reread `GET /api/scripts/{name}/lab-options` and show the same base interval. If it is wrong, update the interval through a short `POST /api/scripts/{name}/lab-options` patch such as `{ "intervalCode": "M5" }`, with the body written directly to `./tmp/lab-options.json` or another workspace-local `./tmp/*.json` file, then rerun lifecycle proof. For slow first proof on a heavy visual indicator, reduce only the active proof window with a short patch containing `DateFrom`, `UseDateFrom`, `DateTo`, and `UseDateTo`; do not rely on `DateReload` or `maxDays`. Do not try to read or check `/tmp/lab-options.json`; create the body you need under `./tmp`.
- Do not use short client-side HTTP timeouts such as `curl --max-time 15` or `--max-time 30` for `build`, `load`, or `run`. If a lifecycle request times out client-side, assume the server may still be working; do not immediately repeat the same lifecycle request in a loop. Wait briefly, read `messages`/`logs`/`metrics-summary` or rerun the next proof route once before deciding on a repair.
- before coding, summarize what the indicator computes, one short formula/algorithm explanation, which plotted outputs are needed, which outputs belong on the main price pane versus separate panes, which pane groups keep the chart readable, which outputs can stay hidden, and which parameters must stay editable
- edit only the handler parameters and `Execute(...)` body; do not reinvent the whole project scaffold
- if later optimization of numeric handler parameters may be needed, keep those `HandlerParameter(...)` attributes optimizable; do not add `NotOptimized = true` unless the parameter is intentionally fixed and must stay out of optimization
- build the DLL
- build from the relative project path that was just generated, for example `dotnet build ./tmp/<folder>/IndicatorHandlers.csproj -c Release -o ./tmp/<folder>/bin/Release`. Do not use `cd /tmp/<folder>` on Windows or in sandboxed workspaces.
- never build with `-o ./tmp/<folder>` or upload `./tmp/<folder>/IndicatorHandlers.dll`; that root file can be stale. Always upload the DLL from the output folder used by the build, normally `./tmp/<folder>/bin/Release/IndicatorHandlers.dll`.
- if the DLL build fails because an interface, market-data type, or handler signature is missing, do not switch to a newly invented interface to "fix" it. Go back to `GET /api/sdk/contracts/indicator` plus the shipped template and implement only interfaces/signatures proven by the current runtime.
- for first-pass candle/price/volume indicators on a single instrument, use the security-input scaffold (`IBar2DoubleHandler`, `ISecurity`) and wire one `SECURITY` source. Use the `IStreamHandler` `IList<double>` templates only for independent numeric streams, not for OHLCV fields of the same instrument.
- for custom-indicator names and docs, use the scaffolded `Properties/Resources.resx` embedded resource file. The Web API reads `{AssemblyName}.Properties.Resources` keys: `<TypeName>.Name`, `<TypeName>.Description`, `<TypeName>.Formula`, `<TypeName>.Meaning`, `<TypeName>.Plot`, `<TypeName>.<ParamName>.Name`, `<TypeName>.<ParamName>.Description`, and `<TypeName>.<ParamName>.Effect`. For bilingual docs in the current single-DLL upload flow, keep the scaffolded resource structure and fill culture-suffixed keys in that same neutral file too: every display/doc key you keep or add must have the unsuffixed English fallback plus `<key>.en` for English and `<key>.ru` for Russian. Replace scaffold placeholder values with concise task-specific English and Russian text before building; placeholders such as `Replace this...`, `Describe...`, `Замените...`, or `Опишите...` are not valid final DLL docs. Do not replace `Resources.resx` with a minimal file that deletes `.en`/`.ru` variants. Do not rely on satellite `Resources.ru.resx` assemblies unless the deployment uploads them with the DLL. Keep C# attributes limited to the runtime-confirmed attribute list.
- If DLL upload returns `code=IncompleteBilingualResourceDocs` or `missingResourceKeys=[...]`, edit `Properties/Resources.resx` once to add every listed base/`.en`/`.ru` key, then rebuild and upload once; do not iterate one missing key per upload.
- canonical upload route: `POST /api/indicator-dlls/{name}`
- compatibility alias also accepted: `POST /api/indicator-dlls` with multipart `file` and optional `name`
- upload the exact DLL you just built, for example `curl -F "file=@<path-to-built-dll>" "http://localhost:5000/api/indicator-dlls/<LibraryName>.dll"`; this is the portable default across Windows, macOS, and Linux, and on Windows PowerShell call `curl.exe`
- `GET /api/indicator-dlls` is discovery only. If the user asked to implement, build, or upload a new custom indicator, an existing DLL with similar handler names is not proof of completion; build and upload the fresh DLL from the current workspace unless the user explicitly asked to reuse the existing DLL.
- read handler names from the upload response or `GET /api/indicator-dlls/{name}/handlers`
- if the prompt explicitly gave a custom indicator class or handler name, this is a hard completion gate: the C# class name, uploaded `handlerTypeNames`, `GET /api/handlers/{typeName}`, and final script blocks must all use that exact exported name byte-for-byte. If upload returns only a near-match or helper name, rename/rebuild/reupload the DLL before any script work; do not continue with a differently named helper or line variant unless the user explicitly allowed it.
- if the upload response exposes `nextStepHint`, read it; treat `suggestedStarterStrategyRoutes` as trading-strategy options, not as the path for visual/analysis indicator scripts
- after DLL upload, do not open extra AGENTS example files before the first starter route or `/ops` batch
- verify only those exact handlers through `/api/handlers/{typeName}`
- Treat `suggestedStarterStrategyRoutes` as trading-strategy options only. If the user asks to show the uploaded indicator on a chart, build a dashboard, add a control pane, or create a visual/analysis script without entry/exit/trading logic, do not use `uploaded-indicator-signal-starter`; blank-create the exact script, call `instrument-source`, then add the uploaded handler, `GraphLink`s, and explicit controls with `/ops`.
- if the user also wants a trading script based on the uploaded indicator, load `$tslab-indicator-use-in-script`; its default first scaffold is `POST /api/scripts/templates/uploaded-indicator-signal-starter`, not blank-create, `instrument-source`, or a hand-built `/ops` scaffold

## Stop if failed

- Do not write the indicator into repo `scripts/`.
- Do not browse a third or fourth source.
- Do not fall back to `ExternalScriptItem` unless the user explicitly provided a server-side file path.
- Do not invent handler signatures; use `/api/sdk/contracts` as the runtime source of truth.
- Do not repair build failures by introducing unverified interfaces or types such as `IPrecalcHandler`. Use `ISecurity`/`IBar2DoubleHandler` only when the current contract or shipped security scaffold exposes them.
- Do not hand-write a replacement `.csproj` or manual DLL hint-path search before trying the packaged bootstrap assets/scripts.
- Do not manually glob/read packaged asset files or host bin assemblies as a substitute for the bootstrap script.
- Do not resolve the bootstrap assets/scripts through a parent repo or source tree when the current workspace already contains `./.opencode/skill/tslab-indicator-csharp/`.
- Do not assume drawing-only interfaces or types such as `IIndicator`, `TSLab.Script.Panes`, `Line`, or `LineFill` exist unless the current runtime contracts or available assemblies already confirmed them.
- Do not assume `Invoke-RestMethod -Form` exists or behaves the same on every shell; on Windows PowerShell 5.1 use `curl.exe -F` for DLL upload.
