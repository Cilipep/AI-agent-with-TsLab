# Agent Instructions: Script Runtime Parameters

Use this file for instrument mapping, date range, interval, and related runtime settings.
Do not edit raw XML for these tasks.

## Hard rules

- Treat `/api/scripts/{name}` routes as name-based unless a route explicitly documents ID semantics.
- For timeframe-only repair, POST `/api/scripts/{name}/lab-options` with a short patch such as `{ "intervalCode": "M5" }`, then reread. For bounded proof/runtime windows, post both dates with active flags, for example `{ "DateFrom": "2026-04-01T00:00:00", "UseDateFrom": true, "DateTo": "2026-05-02T00:00:00", "UseDateTo": true }`; `DateReload` and `maxDays` are not proof of the active historical range. For broader runtime changes, `GET /api/scripts/{name}/lab-options` first, then post back only `{ "options": <data.options> }` with the changed fields.
- Keep the exact field casing and value types returned by the server.
- Always keep `useDateFrom` and `useDateTo` consistent with the date values.
- Do not swap `interval` and `intervalBase`.
- For `/parameters`, use the exact parameter IDs returned by the server.
- If the user explicitly names a provider, do not silently switch to another provider family.
- Do not auto-connect providers unless the user explicitly asked for it or the task is blocked on a missing live connection.

## Instrument mapping

Instrument selection is driven by source mappings, not only by block parameters.
Use `SetSourceMapping` through `/ops` when you need to set or repair a source block.

Typical fields:
- `dataSourceName`
- `securityId`
- `isOption`
- `visualTypeName` when the host expects it

If the script reports `instrument not selected`, inspect the persisted mappings and repair them before more lifecycle steps.

## Reload mapped data

Reloading cached/server data is a dangerous desktop operation. Use it only when the user explicitly asks to refresh or re-download data, or when live evidence shows stale/corrupt cache for a specific source mapping. It requires desktop `AllowDangerousWebApiOperations=true`; if the API returns `403`, report that setting blocker and stop the reload attempt.

Do not send `reloadData` to `POST /api/scripts/{name}/run` or `POST /api/scripts/{name}/optimization/start`. The only supported route is the mapping route:

```powershell
./script-api.ps1 GET "<scriptName>" "mappings"
@'
{ "mappingKey": "<sources[].mappingKey from GET mappings>" }
'@ | Set-Content -Encoding utf8 ./tmp/reload-mapping-data.json
./script-api.ps1 POST "<scriptName>" "mappings/reload-data" ./tmp/reload-mapping-data.json
```

## History request and apply

Use history request routes when an LLM/external automation needs to request provider bars, poll status, inspect diagnostics, and optionally apply cleaned bars. This is not the same as `mappings/reload-data`: request/status/bars are read-only and do not mutate the platform cache.

```powershell
./script-api.ps1 GET "<scriptName>" "mappings"
@'
{
  "requestKey": "optional-stable-key",
  "mappingKey": "<sources[].mappingKey from GET mappings>",
  "from": "2026-05-01T00:00:00",
  "to": "2026-05-23T00:00:00",
  "maxBarsCount": 1000,
  "options": {}
}
'@ | Set-Content -Encoding utf8 ./tmp/history-request.json
./script-api.ps1 POST "<scriptName>" "history/requests" ./tmp/history-request.json
./script-api.ps1 GET "<scriptName>" "history/requests/<requestKey>"
./script-api.ps1 GET "<scriptName>" "history/requests/<requestKey>/bars"
```

Only `POST /api/scripts/{name}/history/apply` mutates the cache. By default it replaces the submitted time range and preserves existing cached bars outside that range, so it can apply a controlled backfill/incremental load without clearing the source mapping. For full bars replacement through the same API, send `"options": { "replaceExistingBars": true }`. It requires desktop `AllowDangerousWebApiOperations=true` and should be used only when the user explicitly asked to apply repaired history or corrupt data is proved.

## Lab options

Use `lab-options` for:
- interval and interval base
- date range
- runtime toggles such as realtime updates

Workflow:

1. `GET /api/scripts/{name}/lab-options`
2. modify only the needed fields inside `data.options`
3. `POST /api/scripts/{name}/lab-options` with `{ "options": ... }`
4. for multi-timeframe or exact-timeframe prompts, reread `GET /api/scripts/{name}/lab-options` immediately and confirm the base interval is correct before deep `/ops` authoring
5. rebuild and rerun if needed

## Provider and symbol lookup

- Resolve providers from `GET /api/datasources`.
- Resolve symbols through the dedicated security lookup endpoint for the chosen datasource.
- If the user names a provider that does not exist or is ambiguous on this host, report that explicitly instead of substituting another provider.

## Portfolio alignment rule

Portfolio timeframe does not automatically propagate into a script or agent.
Before building compressed branches or higher-timeframe filters, explicitly fix the script base interval through `lab-options`; do not assume template or create defaults already match the requested timeframe.
Before creating or restarting agents from a portfolio, explicitly align the script `lab-options` interval with the intended portfolio interval.

## Parameters vs lab options

Use `/parameters` for strategy knobs such as periods, thresholds, and risk values.
Use `lab-options` for environment and run settings such as interval or date range.
Do not mix those two surfaces.
