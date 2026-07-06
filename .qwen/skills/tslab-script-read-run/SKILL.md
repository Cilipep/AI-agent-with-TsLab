---
name: tslab-script-read-run
description: "Phase card for running an existing script and reading compact metrics."
---

# TSLab Script Read/Run

## When to load

- An existing script must be run or analyzed.
- If the prompt explicitly asks to load, open, or show an exact script in desktop, first call `POST /api/scripts/{name}/load`; do not substitute validate/run or read-only routes for that desktop-open request. `GET /api/scripts/{name}/lab-options`, `/parameters`, `/explain`, `/graph`, `/ui`, `/messages`, and `/logs` may auto-open the editor in desktop mode as a server fallback, but they are not desktop-open proof for a load/open/show request unless their response message explicitly says the script was opened/refreshed in desktop. only a successful `POST /api/scripts/{name}/load` response closes the load phase; then stop and report it, and do not drift into handler discovery.
- If the prompt asks to run or analyze an exact script, `POST /api/scripts/{name}/run` is allowed; desktop mode auto-loads the editor if needed. For full lifecycle proof, still prefer `./run-lifecycle.ps1 "<scriptName>"` / `./run-lifecycle.sh "<scriptName>"`.
- If the prompt asks to find an existing server-side script by exact name or query pattern, stay in this read/run flow and search the server first. Do not create or template a new script for that task.
- If the prompt asks only for exact settings fields on an existing script, such as DateReload, useDateReload, interval, or other lab options, go straight to GET /api/scripts/{name}/lab-options. Do not treat that read-only settings response as a desktop load/open. Do not grep docs first and do not switch that read-only settings question into /ops or raw graph inspection.
- On a read-only analysis or improvement-note task for one known script, stay on that exact script and read only its compact routes such as `metrics-summary`, `parameters`, `explain?summary=true`, `authoring-quality`, `messages`, `logs`, and `ui` as needed. Do not call the unfiltered `/api/scripts` list, do not inspect sibling artifacts for ideas, and do not recommend parameter names or blocks that are absent from the current artifact.
- On a continuation or exact known-script task, do not start with `/api/status`, the unfiltered `/api/scripts` list, or `/api/scripts/optimizations`. Start directly with that script's compact routes unless a live failure on that same base already proved the API is unavailable.
- Server-side scripts are not live agent instances. Do not use `GET /api/scripts/{name}/runs`, `/api/agents/{scriptName}/results`, `/api/agents/{scriptName}/detail-results`, or `/api/agents/{scriptName}/last-run` for script analysis.
- A read-only exact-settings question on an existing script is not an authoring task. Do not load $tslab-script-authoring or template/create docs before the first GET /api/scripts/{name}/lab-options.
- For existing-script search, start with `GET /api/scripts?query=...&limit=20&type=Script`. Do not fetch the full unfiltered `/api/scripts` list first. If a multi-keyword query returns empty, retry with one keyword at a time and intersect the small result sets locally.
- If the prompt asks how many scripts exist, asks about scripts "in TSLab" or "in its DB", or otherwise refers to scripts without saying workspace files, treat that as a server-side `/api/scripts` listing/counting task first.
- In packaged workspaces, if one follow-up doc is still needed, open the local packaged copy directly as `./AGENTS-FastPath.md` or `./AGENTS-RunAndAnalyze.md`. Do not grep or glob parent/source-tree paths such as `public/ConsoleLauncher/*`.

## First call

- Exact name known:
  - for load/open/desktop-visible requests: `POST /api/scripts/{name}/load`
  - do not call `GET /api/scripts/{name}/lab-options`, `/explain`, `/graph`, `/ui`, `/messages`, or `/logs` before `/load` when the user asked to open/show it in desktop
  - for full proof: `./run-lifecycle.ps1 "<scriptName>"` / `./run-lifecycle.sh "<scriptName>"`
  - for current run metrics/date range only: `POST /api/scripts/{name}/run`
- Exact name unknown:
  - `GET /api/scripts?query=...&limit=20&type=Script`
- In packaged `ai-agent` mode, if a direct exact-script route fails before any successful localhost read in the current session, one compact `GET /api/status` or `GET /api/status/health` probe is enough. If that probe fails, first run `./start-local-tslab.ps1` on PowerShell or `./start-local-tslab.sh` on POSIX from the current workspace and wait for the API to become healthy before treating the server as unavailable.
- If a user explicitly asks for desktop restart recovery, `POST /api/system/restart` is allowed only with desktop `AllowDangerousWebApiOperations=true`; after `202`, poll `GET /api/status` until `processId` or `apiInstanceId` changes. Do not infer restart completion from `serverTimeUtc`.
- If an exact-script route returns `409` with `DesktopManagerNotReady`, `manager is not ready`, or `Retry the same request in 1-2 seconds`, retry the same route with bounded waiting: about 5 attempts at 2 seconds, or up to 60 seconds total when `errorDetails.maxSuggestedWaitMs` is present. Do not spend that wait on unfiltered `/api/scripts`, sibling artifacts, docs, or alternate route families. If the bounded wait expires, inspect the same script's status/list entry; when it is open in the desktop editor, one clean `POST /api/scripts/{name}/close-editor` with no body is the documented recovery. On `403`, report the setting blocker; on `409` unsaved changes or running optimization, ask for manual save/close or explicit save/stop permission.

## Fields to read

- when the user explicitly asked for script details before run:
  - `GET /api/scripts/{name}`
- when the user explicitly asked for script structure or parameters before run:
  - `GET /api/scripts/{name}/explain`
  - `GET /api/scripts/{name}/parameters`
- `response.data.netProfit`
- `response.data.allTrades`
- `response.data.profitFactor`
- `response.data.maxDrawdownPct`
- On list/read endpoints, inspect one real payload item and use the exact field names returned by that host. Do not assume aliases such as `createdAt` when the live payload uses names like `creationDate`.
- A successful read-only route response does not by itself mean the script is visible in desktop UI. For desktop-visible load/open/show requests, only a successful `POST /api/scripts/{name}/load` response or an explicit response message saying `opened in desktop` / `refreshed in desktop` closes the load phase.
- After `GET /api/scripts/{name}/explain`, do not verify invented handler names such as `GreaterThan` or `HighHandler`. If a handler contract is genuinely needed, use only exact `handlerType`, exact `handlerTypeName`, or a `detailRoute` returned by `/api/handlers/search`.
- If the question asks for `firstBarDate`, `lastBarDate`, `barsCount`, or the current run date range on an existing script, use `GET /api/scripts/{name}/performance?format=named` or `POST /api/scripts/{name}/run` and read those fields directly. Do not open the large generic `GET /api/scripts/{name}` details payload for that question.
- For count/list tasks, keep the server response compact: count the filtered results or project only the few fields you need. Do not paste a full large script list into context when the user only asked for a count or top matches.
- If the prompt is analysis-only and asks what to improve next, explicitly state whether the current artifact result is weak, near-miss, or strong using the current artifact metrics, then tie each suggested next action to parameters, blocks, warnings, or runtime evidence that actually exists on that same artifact.
- If `authoring-quality`, `validate`, `build`, `/ops`, messages, or logs already name a structural blocker such as `Entry1 input not connected`, `OpenConditionNotConnected`, or missing required inputs, do not keep trying `run -> metrics-summary`. On analysis-only prompts, report that the strategy analysis is blocked by that exact graph error and name the block/input; when mutation is allowed, switch to the repair/authoring flow for that same artifact.
- A read-only analysis turn may list untested next ideas, but the moment the prompt asks to improve, optimize, or compare (not analysis-only) the requests require tested candidates: every improvement candidate must be tested on the live artifact with measured before/after metrics. Do not deliver untested `could try` / `можно попробовать` / `not tested` suggestions when the prompt asks for improvements or your own answer claims tested/optimization results; switch to the clone-edit or optimization flow and prove the candidate first.
- On PowerShell, use `Invoke-RestMethod` or a parsed `curl.exe` pipeline so the final stdout is only the compact count/projection you need, not the raw full `/api/scripts` JSON payload.
- On Windows PowerShell, for simple read-only localhost GET requests, start with `Invoke-RestMethod` instead of bare `curl` or `curl.exe` unless you specifically need raw bytes or multipart upload behavior.

## Next allowed call

- `POST /api/scripts/{name}/build`
- `POST /api/scripts/{name}/load`
- `POST /api/scripts/{name}/run`
- `GET /api/scripts/{name}/metrics-summary`
- if a `curl` URL contains query parameters such as `?query=...&limit=20&type=Script`, quote the whole URL so shells do not split on `&`

## Stop if failed

- Do not scan the repo to discover server-side scripts.
- If server search returns no matching script, report that no server-side match was found. Do not switch to authoring to fabricate a replacement unless the user explicitly changes the task.
- `CompletedNoData` or `No instrument selected` on an offline/cache/backtesting prompt is a same-artifact source/materialization repair state, not permission to change providers.
- Do not call unfiltered `GET /api/datasources`, do not switch to `test`/`text`, and do not connect, disconnect, reload, reschedule, or mutate datasource settings unless the user explicitly asked for live provider administration.
- Stay on the mapped/requested datasource, security, and interval. Inspect this script's mappings, authoring-quality, UI/explain/graph, messages/logs, and lab-options; repair the same source branch or exact instrument-source mapping, rerun, then report only after proof.
