# Agent Instructions: Load / Build / Run / Analyze

Use this file for runtime lifecycle, logs, messages, charts, positions, and metrics.
Keep script authoring and graph-editing rules in `AGENTS-FastPath.md` and `AGENTS-ScriptEditing.md`.

## Core rules

- Treat `/api/scripts/{name}` route families as name-based routes. Do not substitute numeric `scriptId` values into them.
- If the current artifact still exposes `mustMutateCurrentArtifact=true`, `requiredNextMutationRoute`, `BlankGraph`, `SourceOnlyGraph`, `DisconnectedGraph`, or only a starter scaffold such as `Src + Close`, stop and return to `AGENTS-FastPath.md` or `AGENTS-ScriptEditing.md`. This file is for post-mutation lifecycle, not for first-scaffold authoring.
- Always `POST /api/scripts/{name}/load` before build or run unless you already proved the script is loaded.
- Always `POST /api/scripts/{name}/build` after any edit before running.
- Do not send `validate; build; load; run` as one shell line just to save steps. Use separate shell steps, or the packaged helper `./run-lifecycle.ps1 "<scriptName>"` / `./run-lifecycle.sh "<scriptName>"`, so every lifecycle result stays observable.
- If `build`, `load`, or `run` replies `Script '{name}' is still initializing`, retry that same route once after a short pause or switch to the packaged `./run-lifecycle.ps1` / `./run-lifecycle.sh` helper. Treat that response as warmup lag on the same artifact, not as proof that you should pivot to `/json`, another host, or a different script.
- If one shell command still produced multiple lifecycle responses, inspect each inner result. Any failed or partial inner `validate`, `build`, `load`, or `run` invalidates the whole chain for acceptance.
- On a strategy prompt, build and run are not substitutes for missing authoring. If the current artifact still has `authoring-quality.data.hasTradeBlocks=false` or `/explain` still does not show a real trade path, go back to mutation first instead of starting lifecycle.
- If `authoring-quality`, `validate`, `build`, `/ops`, or helper output names a structural blocker such as `OpenConditionNotConnected`, `BlocksMissingRequiredInputs`, `Entry1 input not connected`, or another missing required block input, that blocker outranks `run -> metrics-summary`. Repair that exact block/input on the same artifact when mutation is allowed; on analysis-only prompts, final output should say analysis is blocked by that concrete graph error and name the block/input, not keep retrying lifecycle or quote stale metrics.
- Do not open or use this file as the primary guide for a strategy prompt while the current artifact is still only a starter analysis scaffold such as `Src + Close`. Finish the minimal trade scaffold first, then return here for lifecycle and metrics.
- On a strategy prompt, the minimum acceptable pre-lifecycle scaffold is at least one real entry block, `RelativeCommission` on the tradable path, and one protective stop/profit exit. If a compressed higher-timeframe branch feeds the base trade path, require a real return of that branch into the effective base trade/filter path before treating lifecycle output as meaningful. An explicit `Decompress` or `DecompressBool` block is one common way to prove that return, but not the only valid one.
- If the prompt says `Do not change the script now` or otherwise makes the task analysis-only, do not call `/ops`, `/parameterize`, `/optimization/start`, or other mutation routes. The final note must still explicitly classify the current result quality as weak, near-miss, or strong based on the current artifact metrics, and every next action must reference blocks, parameters, or runtime evidence that actually exists on that same artifact.
- Never use `GET` for validate, load, build, or run routes.
- Always surface `warningCount > 0` and the warning list.
- Always call `/charts/info` before `/charts/data`.
- Do not rely on `/run` summary fields such as `hasCharts` or `hasPositions` alone. Confirm them through the dedicated endpoints.
- For any human-facing strategy, also verify `GET /api/scripts/{name}/ui` before delivery.
- `MissingControlPane` is non-blocking unless the prompt explicitly asked for editable runtime controls.
- Blocking visual debt still fails the run-analysis bar even if metrics exist.
- On a read-only analysis or improvement-note task for a known current artifact, stay on that artifact only: use `GET /api/scripts/{name}/metrics-summary`, `GET /api/scripts/{name}/parameters`, `GET /api/scripts/{name}/explain?summary=true`, `GET /api/scripts/{name}/authoring-quality`, `GET /api/scripts/{name}/messages`, `GET /api/scripts/{name}/logs`, and `GET /api/scripts/{name}/ui` as needed. Do not call the unfiltered `GET /api/scripts` list, do not inspect sibling artifacts for ideas, and do not recommend parameter names or blocks that are absent from the current artifact.
- On an improve/test/compare strategy task, do not turn untested ideas into the final answer. Each kept candidate needs a live proof row from this turn: what changed, lifecycle state, trade count, net profit, Profit Factor, and drawdown. If a candidate cannot be tested because the needed handler/template/route is absent, cite that live endpoint response and mark it blocked instead of saying "could try" or "можно попробовать".
- If you voluntarily tested variants during a historical quality check, a final "tested variants" or "optimization results" table must not be followed by untested next-try ideas. Either test those ideas too, mark them blocked with endpoint evidence, or leave them out.

## Portable shell rules

- Use the current shell's native HTTP client directly. Do not wrap ordinary localhost calls in nested `powershell -Command`, `bash -lc`, or `sh -lc`.
- For JSON request bodies, a UTF-8 file plus `curl --data-binary "@file.json"` is the most portable pattern.
- On Windows PowerShell, use curl.exe if you need the real curl binary.
- On Windows PowerShell, do not treat `$?` after `curl.exe` as an HTTP-success gate. `curl.exe` can exit `0` even when the API returned `400` or `404`; inspect the actual response or use `Invoke-RestMethod`, `./api-json.ps1`, or `curl.exe --fail-with-body`.
- On Windows PowerShell, do not rely on jq for ordinary localhost JSON inspection; prefer Invoke-RestMethod, ConvertTo-Json, or direct property reads.
- On Windows PowerShell, for simple read-only localhost GET requests, start with Invoke-RestMethod instead of bare curl or curl.exe unless you specifically need raw bytes or multipart upload behavior.
- If a URL contains query parameters, quote the whole URL so the shell does not split on `&`.
- If you hit block-id or payload corruption, resend the body as explicit UTF-8 bytes or as a UTF-8 file.

## Preconditions

- Many scripts require a valid source mapping. Missing mapping usually leads to `instrument not selected`, `CompletedNoData`, or `barsCount=0` symptoms.
- `barsCount=0` or `CompletedNoData` can come from missing data, an over-narrow date window, or an artifact that still does not materialize runtime bars on the mapped source.
- Do not call the implementation complete or blame missing server-side history unless `messages`, `logs`, datasource diagnostics, or provider routes explicitly confirm missing history, unavailable source, or unresolved instrument.
- `GET /api/datasources` can look disconnected while cached history is still available for a historical backtest.

## Lifecycle

### Load
- `POST /api/scripts/{name}/load`
- Use `?force=true` if you need to refresh stale in-memory state.
- `GET /api/scripts/loaded` lists the currently loaded scripts.
- `DELETE /api/scripts/{name}/unload` unloads the API/runtime-owned script manager state. In desktop mode it does not close an already open visual editor tab.
- `POST /api/scripts/{name}/close-editor` and `POST /api/scripts/close-editor/by-name/{**name}` close an already open desktop visual editor tab. A no-body clean close does not save and is idempotent when the editor is not open; save/stop close options require explicit user permission and dangerous desktop operations. The route returns `409` for unsaved changes or running optimization and must not replace ordinary load/unload/build lifecycle except for the documented editor-409 recovery below.
- If an exact-script route returns `409` with `DesktopManagerNotReady`, `manager is not ready`, or `Retry the same request in 1-2 seconds`, retry the same route with bounded waiting: 5 attempts at about 2 seconds, or at most 60 seconds total when `errorDetails.maxSuggestedWaitMs` is present. Do not probe sibling scripts, broad route families, or docs during that wait. If the bounded wait expires, inspect the same artifact's `GET /api/scripts/{name}/status` or compact list entry. If it shows `isEditing=true` / `status=Editing`, one clean `POST /api/scripts/{name}/close-editor` with no body is the documented recovery; on `403`, report the setting blocker; on `409` unsaved changes or running optimization, stop and ask the user to save/close manually or explicitly allow saving/stopping.

### Build
- `POST /api/scripts/{name}/build`
- Use `?reload=true` for one retry after imports or stale in-memory state.
- If build fails, immediately inspect `/messages` and `/logs`.
- A single warmup failure can be transient. Retry build once after collecting logs, but do not spin.
- If the only failure text is `Script '{name}' is still initializing`, one bounded same-route retry is the default first move before deeper diagnostics.
- If `build.success=false`, the artifact is not final even if `validate` passed. Do not summarize it as verified or complete.
- If the latest `validate`, `build`, or `load` attempt failed because of a wrong method, invalid JSON, request-body parsing, or another `4xx` contract error, do not continue to `run`, metrics, or final summary. Repair that route first.

### Run
- `POST /api/scripts/{name}/run`
- The run response exposes `warningCount`, `warnings`, `resultState`, `barsCount`, `firstBarDate`, `lastBarDate`, `hasCharts`, `hasPerformance`, `hasPositions`, and optional issue fields.
- If the latest observable lifecycle state still contains `CompletedPartial`, `requiresRepair=true`, `mustRerunAfterRepair=true`, or `mustNotReadMetricsYet=true`, the lifecycle proof is still open even when an earlier `validate`, `build`, or `load` in the same session succeeded.
- If the task only asks for the current run range or last bar date on an existing script, prefer `GET /api/scripts/{name}/performance?format=named` or the `POST /api/scripts/{name}/run` response. Do not open the large generic `GET /api/scripts/{name}` details payload just to recover `firstBarDate` or `lastBarDate`.
- Treat `CompletedNoData`, `CompletedPartial`, `requiresRepair=true`, `mustRerunAfterRepair=true`, `mustNotReadMetricsYet=true`, or a concrete `nextRepairHint` as incomplete.
- If the prompt expects metrics or a working strategy and `CompletedNoData` persists, the final classification stays fail or near-miss. An `intent-check` pass plus `authoring-quality.requiresRepair=false` is not enough to call the artifact complete.
- If `run` reports `CompletedPartial` or `hasCharts=false` while the same artifact already has visible panes and GraphLinks, do not assume the remaining problem is only missing panes. Re-read `/explain` and runtime `messages`/`logs` for graph-linked handlers with invalid inputs, broken formulas, or only partially materialized shown parameters; repair those blocks on the same artifact, then rerun.
- If `run.success=false`, the artifact is not final even if other endpoints still return charts or metrics.
- If required verification routes such as `intent-check`, `authoring-quality`, or `ui` failed with wrong method, invalid JSON, request-body parsing, or another `4xx`, the artifact is still unverified even if `run` succeeded. Repair that failed verification route and rerun it before delivery.
- On a multi-timeframe prompt, a successful `validate -> build -> load -> run` is only provisional. Before final success on that same artifact, re-read `GET /api/scripts/{name}/lab-options`, `GET /api/scripts/{name}/authoring-quality`, `GET /api/scripts/{name}/ui`, and the exact `POST /api/scripts/{name}/intent-check` body for that prompt.
- If those post-run checks still show the wrong base interval, orphaned higher-timeframe blocks, missing `effectiveCompressedIntervals`, missing `decompression-to-base-path`, or a missing required `separate-pane`, repair the same artifact, rerun lifecycle, and only then report final success. Here `decompression-to-base-path` is shorthand for an effective return of higher-timeframe outputs into the base trade/filter path, not necessarily a direct `Decompress*` block.
- If `intent-check` still misses higher-timeframe trade features while `authoring-quality` shows orphaned compression blocks, treat that as one unfinished MTF branch. Reconnect or recreate one effective branch on the current artifact; do not keep adding duplicate orphaned `Compress*` / `Decompress*` blocks.
- For automation, prefer `save=false` unless you intentionally want to persist the current in-memory graph state.

Example body:
```json
{
  "timeoutMs": 600000,
  "populateCaches": true,
  "save": false
}
```

## Fast stale-results check

When a task includes script changes through `/ops`, do one canary check before a long repair loop:

1. Apply one tiny behavior-changing edit.
2. Run `validate -> build -> run`.
3. Confirm that a measurable result changed, for example trade count or positions.

If the graph clearly changed but runtime results do not change at all, treat that as stale in-memory state or stale results.
Try one unload/load-force/build-reload cycle. If the user explicitly asked to refresh/re-download market data, or stale/corrupt source cache is proved for a specific source, read `GET /api/scripts/{name}/mappings` and call `POST /api/scripts/{name}/mappings/reload-data` with `{ "mappingKey": "<sources[].mappingKey>" }`; this requires desktop `AllowDangerousWebApiOperations=true` and a `403` is a setting blocker. Do not put `reloadData` on `run` or `optimization/start`. If the user needs LLM-visible provider bars for diagnostics or cleanup, use the separate read-only history workflow: `POST /api/scripts/{name}/history/requests`, poll `GET /api/scripts/{name}/history/requests/{requestKey}`, then read `GET /api/scripts/{name}/history/requests/{requestKey}/bars`; only `history/apply` mutates cache and requires dangerous-operation approval. After that, try one desktop `POST /api/system/restart` only if the task explicitly allows it or the user asked for restart control, and stop there. Restart requires desktop `AllowDangerousWebApiOperations=true`; if it returns `403` or `409`, report that blocker. If restart is accepted, poll `GET /api/status` until `response.data.processId` or `response.data.apiInstanceId` changes, then wait for healthy status before continuing. Do not use `serverTimeUtc` as process start proof.

## Troubleshooting no-data runs

If `run` reports `barsCount=0`, `CompletedNoData`, or mapping-related messages:

1. Read `GET /api/scripts/{name}/mappings`, `GET /api/scripts/{name}/authoring-quality?compact=true`, `GET /api/scripts/{name}/ui`, and `GET /api/scripts/{name}/explain?summary=true` on the same artifact.
2. If mappings already show the requested datasource/security but runtime says `No instrument selected`, treat it as source materialization or graph/source-link repair first, not provider/cache proof.
3. If `/explain` or `/graph` shows a missing, duplicated, disconnected, or wrong source block, repair that same source/link path with `/ops` or the exact `instrument-source` body, then rerun.
4. Do not convert an ordinary historical source to `NotTradableSecuritySourceItem` only because the task is non-trading or visual analysis. Non-trading visual analysis still needs runtime bars from the mapped source.
5. Treat `records=[]`, `isTradable=false`, disconnected datasource status, and `instrumentsLoaded=0` as diagnostics only. They do not prove cached history is missing by themselves.
6. If the user explicitly asked for a data refresh or the latest messages prove stale/corrupt cached data for one source, use the dangerous mapping reload route: `GET /api/scripts/{name}/mappings`, then `POST /api/scripts/{name}/mappings/reload-data` with the exact `mappingKey`. Do not use provider reloads, datasource admin routes, or `reloadData` fields on lifecycle routes.
7. If the task is to inspect, backfill, or repair provider bars before applying them, use `history/requests` status/bars first. Apply cleaned bars only through `POST /api/scripts/{name}/history/apply`, and only with desktop `AllowDangerousWebApiOperations=true`; default apply replaces the submitted time range and preserves existing cached bars outside that range. For full bars replacement through the same API, send `options.replaceExistingBars=true`.
8. Read `GET /api/scripts/{name}/messages` and `GET /api/scripts/{name}/logs`.
9. Verify interval and date range through `GET /api/scripts/{name}/lab-options`.
10. If the task asked for all available history or the first trading days, disable `useDateFrom` and `useDateTo` unless the prompt explicitly asked for a bounded date window. Evaluate the active historical range only from `useDateFrom`/`DateFrom` and `useDateTo`/`DateTo`; `useDateReload` and `DateReload` are reload settings, not proof of a selected historical range.
11. When you repair date/runtime settings, do not invent `SetLabOption` pseudo-ops or an `{ "ops": [...] }` payload for `/lab-options`. For timeframe-only repair, POST a short patch such as `{ "intervalCode": "M5" }`; for bounded proof/runtime windows, POST both dates with active flags, for example `{ "DateFrom": "2026-04-01T00:00:00", "UseDateFrom": true, "DateTo": "2026-05-02T00:00:00", "UseDateTo": true }`. `DateReload` and `maxDays` are not proof of the selected historical range. For broader settings, read `GET /api/scripts/{name}/lab-options`, keep `response.data.options`, change only needed fields, POST `{ "options": <full data.options> }`, then reread `GET /api/scripts/{name}/lab-options` and rerun.
12. Only after graph/source, messages/logs, and lab-options stay clean, you may run at most one exact diagnostic for the already-mapped datasource/security. Do not call unfiltered `GET /api/datasources`, do not switch to `test`/`text`, and do not choose another provider to escape `CompletedNoData`.

If `GET /api/scripts/{name}/mappings` already shows datasource/security on every required source block, do not loop `instrument-source` again just because runtime still says `instrument not selected`. Inspect `/explain`, `/graph`, `messages`, and `logs` first. On an ordinary single-instrument artifact, do not answer that runtime warning by adding a second source block, switching to `NotTradableSecuritySourceItem`, switching to `test`/`text`, or remapping a new provider through `Src_New`; repair or reconnect the existing source branch first. If the mapped datasource shows `isConnected=false` or `isReady=false`, treat that runtime connection state as diagnostic unless the task explicitly asks for live provider access. Only after graph/source diagnostics stay clean should you widen the date window through `lab-options`.

If `barsCount > 0` but a strategy run still has `positionsTotal=0`, `hasPositions=false`, `mustNotReadMetricsYet=true`, or `requiresRepair=true`, stop treating it as a no-history problem. That is usually a trade-path blocker on the current graph. Inspect compact `authoring-quality`, compact `intent-check` when the prompt supplied one, and `/explain?summary=true`; then repair reachable non-market prices, activation gates, formula-derived entry/exit/size branches, and threshold parameters before rerunning. Do not switch to datasource, date-window, optimization, or control-pane edits unless the current live response explicitly names that as the blocker.


Only after those checks are clean should you treat the problem as an API or host issue.
If those checks remain inconclusive and bars still stay at `0`, report an unresolved runtime blocker on the same artifact. Do not rewrite that state as a successful implementation with missing server-side data unless the runtime evidence explicitly says so.

## Logs and messages

- `GET /api/scripts/{name}/messages?maxMessages=50&since=...`
- `GET /api/scripts/{name}/logs`
- `GET /api/scripts/{name}/explain?summary=true` when you need a compact structural view

Warnings are actionable even when build or run returned `success=true`.

## Result endpoints

### Charts
- `GET /api/scripts/{name}/charts/info`
- `GET /api/scripts/{name}/charts/data?maxBars=1000&skipBars=0`
- Keep `maxBars` within `1..10000`.
- Use `GET /api/scripts/{name}/ui` to inspect configured panes and graph links.

### Performance
- `GET /api/scripts/{name}/performance`
- `GET /api/scripts/{name}/performance?format=named`
- `GET /api/scripts/{name}/profit?summary=true`
- `GET /api/scripts/{name}/performance-chart?maxPoints=500`

### Positions
- `GET /api/scripts/{name}/positions?maxPositions=50&skipPositions=0`
- Primary request parameters are `maxPositions` and `skipPositions`.

### UI extras
- `GET /api/scripts/{name}/control-panes`
- `GET /api/scripts/{name}/canvas-panes`

## Human-facing chart acceptance

A human-facing strategy is not done until the chart is readable:

- visible candles on the main price pane
- primary price-scale indicators or signal levels readable on the main pane
- separate-scale indicators on their own panes
- threshold lines visible when they explain an oscillator-driven signal
- non-main panes must contain at least one visible graph link

Do not explain missing charts away as a generic headless limitation while the same artifact still has graph or pane debt.

## Evaluation order

1. No unresolved errors in `/messages` or `/logs`.
2. Data exists when data is expected.
3. On strategy prompts, the current artifact already proves a real trade path before you treat lifecycle output as meaningful.
4. Human-readable plots exist when the prompt is visual or human-facing.
5. Trades, positions, and performance exist when the prompt expects trading behavior.
6. Metrics are sane enough to interpret.

If the prompt expects no trades, zero trades can be valid, but the charts and runtime state must still be correct.

## Minimal run-analysis sequence

1. `GET /api/scripts/{name}/explain?summary=true`
2. `POST /load -> POST /build -> POST /run`
3. `GET /api/scripts/{name}/messages`
4. `GET /api/scripts/{name}/logs`
5. `GET /api/scripts/{name}/performance?format=named`
6. `GET /api/scripts/{name}/profit?summary=true`
7. `GET /api/scripts/{name}/positions?maxPositions=200&skipPositions=0`
8. `GET /api/scripts/{name}/ui` when the prompt is human-facing

If the run is structurally clean but the visual acceptance fails, fetch `authoring-quality` plus `ui`, repair through `visualize` or `autolayout`, rerun, and only then treat the artifact as final.

Do not use a `metrics-summary` with `allTrades=0`, `netProfit=0`, or similar flat zero output as evidence of success when the current `build` or `run` call already failed or explicitly requested repair. On a strategy prompt, zero trades are only acceptable when the prompt explicitly allows or expects no trades; otherwise treat them as a logic or parameter failure on the current artifact and repair before final success.
Do not use `metrics-summary` or a stale earlier `intent-check` pass as a substitute for a failed current-session verification call.
