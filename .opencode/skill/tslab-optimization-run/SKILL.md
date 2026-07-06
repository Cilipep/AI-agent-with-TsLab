---
name: tslab-optimization-run
description: "Phase card for same-script optimization, best selection, and apply."
---

# TSLab Optimization

## When to load

- The current known script must be optimized.
- Manual comparisons, one-off reruns, or final-text claims do not count as optimization. When the prompt asks to optimize, choose the best row, or apply the best result, use `/optimization/start` plus `/results` or `/best`, then `/apply` when required.
- If the latest `authoring-quality`, `intent-check`, lifecycle result, or `GET /api/scripts/{name}/parameters` still shows an unresolved script, formula, or runtime error on the same artifact, optimization is blocked. Repair the same artifact first instead of changing ranges or retrying `/optimization/start` blindly.
- When you read `GET /api/scripts/{name}/parameters`, inspect the top-level readiness fields such as `response.data.optimizationReady`, `response.data.nextStepHint`, and `response.data.suggestedNextRoutes`, not only `response.data.parameters[]`.
- If `GET /api/scripts/{name}/parameters` already says `optimizationReady=true` and the task explicitly asks to optimize or apply the best result, that is the fresh-job handoff. Do not detour into `GET /api/scripts/optimizations`, `GET /api/scripts/{name}/optimizations`, or historical job reuse; start one fresh `POST /api/scripts/{name}/optimization/start` and continue only the returned `jobId`.
- A `400` from `/optimization/start` that says the current script still has an error is an authoring-repair signal, not a reason to guess another start body.

## Workspace scope

- If you manually open follow-up optimization instructions, stay inside the current workspace and do not assume parent or source-tree files exist outside it.
- On a continuation with an already known script, open the exact local optimization phase card or keep using this skill. Do not start by globbing `AGENTS*.md`, searching `public/ConsoleLauncher/*`, or rediscovering hidden skill paths.
- Keep optimization work in the current session. Do not use Task/explore/subagent tools for optimization continuation.
- If a build/runtime blocker on the current artifact is just one wrong or duplicate link, do not decide that `/ops` is append-only. Refresh one exact live view, remove that link with `Disconnect` or returned cleanup ops, reconnect on the same artifact, and only then return to optimization. Do not switch to guessed `/graph`, raw XML/viewModel patch files, or assistant cache/tool-output files as a substitute repair path.
- If a prompt-required optimization family is missing from `GET /api/scripts/{name}/parameters` only because the current artifact buried that tuning value as a raw literal inside `BoolCustomHandlerItem` / `DoubleCustomHandlerItem` `Expression` text, treat that as unfinished authoring on the same artifact. Unless the user explicitly asked for analysis-only or no more graph changes, externalize that knob into a real numeric parameter or a dedicated constant/value block, add `SetOptimizationRange`, and then continue optimization. Do not stop with a follow-up question and do not switch to codebase search or script-list browsing for that case.
- Do not inspect `GET /api/scripts/optimizations` or `GET /api/scripts/{name}/optimizations`, and do not reuse historical jobIds from older runs as proof for the current task. On a fresh optimization turn for the current artifact, start one fresh `POST /api/scripts/{name}/optimization/start` and only continue the jobId returned by that start response unless the same turn already started the exact job you are continuing.
- On a continuation for one known artifact, do not restart with `/api/status`, the unfiltered `/api/scripts` list, or `/api/scripts/optimizations`. Start from `GET /api/scripts/{name}/parameters`, the exact `/optimizations/{jobId}` route already returned in the same stage, or the direct current-artifact runtime routes.

## First call

- On a continuation where the current script was just created or mutated in the previous step, first call `GET /api/scripts/{name}/authoring-quality?compact=true` unless the same session already read a clean authoring-quality result after the last mutation/run.
- If that response has `data.requiresRepair=true`, do not start optimization yet. Follow `data.requiredNextMutationRoute` first, usually `POST /api/scripts/{name}/repair/authoring-quality`, then re-run `validate -> build -> load -> run -> metrics-summary`, reread `GET /api/scripts/{name}/parameters`, and only then start one fresh optimization job.
- If the prompt limits the optimization to specific parameter families or gives a run cap, call `GET /api/scripts/{name}/parameters` first and decide the exact `selectedParameterIds` before `optimization/start`.
- If the prompt asks to optimize but does not request exhaustive full search, include a bounded `iterations` value in `/optimization/start` (usually 50-100 for a first pass). Do not default to the full search space in an interactive agent turn.
- Use canonical `iterations` for the run cap. `maxIterations` is tolerated as a low-context alias, but examples and new request bodies should use `iterations`.
- Do not send a top-level `ranges` array or `parameterCodeName` list to `POST /api/scripts/{name}/optimization/start`. That body shape belongs to prior range configuration through `POST /api/scripts/{name}/ops` with `SetOptimizationRange`, not to job start.
- After ranges are configured, reread `GET /api/scripts/{name}/parameters` and copy the exact current `response.data.parameters[].id` values for `selectedParameterIds`. `selectionHints` only tell you which ids belong together; do not synthesize ids from block GUIDs, block names, or invariant names.
- If `response.data.parameters[]` is still empty, `optimizationCandidates[]` are still range-configuration hints rather than a ready job-scoped selection set. Finish ranges and reread `/parameters` before `optimization/start`.
- If `response.data.optimizationReady=true`, do not fall back to list routes or `/lab-options` just to rediscover the same start path. Stay on the same artifact, keep the current `response.data.parameters[].id` set, and start one fresh job.

- if the create/template response included `defaultOptimizationRequest`, use:
  - `POST /api/scripts/{name}/optimization/start`
- otherwise:
  - `GET /api/scripts/{name}/lab-options`

## Fields to read

- Start response:
  - `response.jobId`
  - `response.scriptName`
  - `response.status`
  - `response.selectedParameterCount`
  - `response.configuredRangeParameterCount`
- Status response:
  - read `response.data.status` and `response.data.completedIterations` first
  - `response.status` and `response.completedIterations` are only poll-friendly mirrors/fallbacks
  - in Windows PowerShell, use `$s = if ($response.data) { $response.data.status } else { $response.status }`; do not poll `$response.status` alone against older hosts
  - a single `Running` status response is not a stopping point; use a bounded polling loop until `Completed`, `Failed`, or `Canceled`
- Parameters fallback:
  - `response.data.authoringQualityRequiresRepair`
  - `response.data.authoringQualityRequiredNextMutationRoute`
  - `response.data.optimizationCandidates[*].suggestedSetOptimizationRangeOp`
  - `response.data.selectionHints[]`
- Best response:
  - `response.parameterValues`
  - `response.suggestedValue`
  - `response.data.netProfit`
  - `response.data.profitFactor`
  - `response.data.maxDrawdownPct`
  - `response.data.allTrades`
- Apply response:
  - read `response.data.warning` and `response.data.nextStepHint`
  - if desktop reinitialization is still running after `/apply`, wait briefly or call `POST /api/scripts/{name}/run`, which waits for initialization
  - if the follow-up route returns `409` with `DesktopManagerNotReady`, `manager is not ready`, or `Retry the same request in 1-2 seconds`, retry that same route with bounded waiting: about 5 attempts at 2 seconds, or up to 60 seconds total when `errorDetails.maxSuggestedWaitMs` is present. If it still fails and script status shows the editor open, one clean `POST /api/scripts/{name}/close-editor` with no body is the documented recovery; stop on `403` or unsaved/running-editor `409`.
- Final metrics:
  - `response.data.netProfit`
  - `response.data.allTrades`
  - `response.data.profitFactor`

## Next allowed call

- if using the fallback `lab-options` branch:
  - post full lab options back with `rtUpdates=false`
  - `POST /api/scripts/{name}/optimization/start`
- if start says optimization is not ready:
  - `GET /api/scripts/{name}/parameters`
  - if configured ranges are missing for the selected subset: `POST /api/scripts/{name}/ops` using `response.data.optimizationCandidates[*].suggestedSetOptimizationRangeOp`
- if `response.data.selectionHints[]` groups sibling ids into one logical family, keep that shared family aligned instead of inflating `selectedParameterIds` beyond the prompt's stated family count
- if ranges already exist but the current job selected nothing: rerun `POST /api/scripts/{name}/optimization/start` with `selectedParameterIds`
- if `plannedIterations` is unexpectedly large, cancel the same job and restart with a smaller `iterations` cap and/or narrower `selectedParameterIds`; do not wait through a long full-space run
- if you still need to define ranges manually:
  - seed them from `GET /api/handlers/{typeName}` or a copied `suggestedSetOptimizationRangeOp`
  - narrower ranges are allowed only as explicit narrowing around the current baseline or a user-stated hypothesis
- `GET /api/scripts/optimizations/{jobId}`
- if `searchSpace` or `plannedIterations` exceed the user-stated cap:
  - `POST /api/scripts/optimizations/{jobId}/cancel`
  - narrow ranges or `selectedParameterIds`
  - `POST /api/scripts/{name}/optimization/start`
- if `completedIterations` stays `0` for too long, or `best` later returns `404`:
  - `GET /api/scripts/{name}/messages`
  - `GET /api/scripts/{name}/logs`
  - `POST /api/scripts/optimizations/{jobId}/cancel`
  - then either retry once with a narrower job or report a stalled/no-result failure honestly
- `GET /api/scripts/{name}/optimizations/{jobId}/best?metric=NetProfit&rank=1`
- `POST /api/scripts/{name}/optimizations/{jobId}/apply?metric=NetProfit&rank=1`
- After `/apply`, do not chain `build; load; run; metrics-summary` into one shell command. Read the apply response first, then run the proof steps separately so any desktop reinitialization warning is visible.
- In Windows PowerShell, quote the whole URL when it contains `&`, for example `./api-json.ps1 GET "/api/scripts/{name}/optimizations/{jobId}/best?metric=NetProfit&rank=1"`. Unquoted `&rank=1` is a shell operator, not part of the URL.
- `POST /api/scripts/{name}/build`
- `POST /api/scripts/{name}/run`
- `GET /api/scripts/{name}/metrics-summary`
- `GET /api/scripts/{name}/messages`
- `GET /api/scripts/{name}/logs`
- for JSON mutation bodies, prefer the current shell's native HTTP client or a UTF-8 file plus `curl --data-binary`; if the current shell is Windows PowerShell, call `curl.exe` when you need the real curl binary
- In Windows PowerShell, do not pipe `curl.exe` output into a nested `powershell -Command` JSON parse such as `$input | ConvertFrom-Json`. Use `Invoke-RestMethod`, `./api-json.ps1`, or save the raw JSON to a file and parse it in the same shell instead.

## Stop if failed

- Do not create or copy scripts.
- Do not infer the winner from `runId` or table order.
- Do not default to `SharpeRatio`; use only metrics proved by the current `/results` or `/best` response. When unsure, use `NetProfit`.
- Do not invent `SetOptimizationRange` field names: use `paramInvariantName`, not `paramName`.
- Do not treat `usedInOptimization` as "all configured parameters for every job". It is only the persisted default selection.
- Do not treat `rank=1` as success by itself; reject best rows with `allTrades=0`, negative `NetProfit`, `profitFactor < 1`, absurd drawdown, or explicit task guardrail failure.
- If the prompt asks whether the result cleared a bar, state the final optimization verdict explicitly as pass, near-miss, or fail. Do not replace that acceptance verdict with softer wording such as successful or acceptable.
- Improvement, optimize, or compare requests require tested candidates: every candidate you propose must be applied and rerun on the live artifact with measured before/after metrics. Do not deliver untested `could try` / `можно попробовать` / `not tested` suggestions when the prompt asks for improvements or your own answer claims tested/optimization results.
- Do not finish an optimization lane without `metrics-summary`, `messages`, and `logs` from the applied live artifact.
- Do not use shell `while true` polling when the explicit status route already exists.
- Do not use `GET /api/scripts/{name}/metrics`; use `GET /api/scripts/{name}/metrics-summary`.
