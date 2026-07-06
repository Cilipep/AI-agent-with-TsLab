# Optimization FastPath

Use this file only for an optimization turn on an already known script.

## Phase rule

- `one phase = one shell step`
- Do not combine start, poll, best, and apply in one shell step.
- On a continuation with an already known script, open this exact file or load the local optimization skill directly. Do not start by globbing `AGENTS*.md`, searching `public/ConsoleLauncher/*`, or rediscovering hidden skill paths.
- Stay on the optimization routes: `/parameters`, `/optimization/start`, status, `best`, `apply`, `metrics-summary`, `messages`, and `logs`. Do not replace those with large `GET /api/scripts/{name}` dumps or guessed routes such as `GET /api/scripts/{name}/metrics`.
- Do not inspect `GET /api/scripts/optimizations` or reuse historical jobIds from older runs as proof for the current task. On a fresh optimization turn for the current artifact, start one fresh `POST /api/scripts/{name}/optimization/start` and only continue the jobId returned by that start response unless the same turn already started the exact job you are continuing.
- If `GET /api/scripts/{name}/parameters` already says `optimizationReady=true`, that is the fresh-job handoff for the fresh optimization flow. If the task explicitly asks to optimize or apply the best result, do not detour into `/lab-options`, list routes, or historical jobs first; start one fresh `/optimization/start` on the same artifact and keep only the returned `jobId`.
- Do not use Task/explore/subagent tools during optimization continuation. Keep the work in the current session and current artifact.

## Phase 1: Start

- First call:
  - if the prompt limits the optimization to specific parameter families or gives a run cap, call `GET /api/scripts/{name}/parameters` first and decide the exact `selectedParameterIds` before `optimization/start`
  - if the prompt asks for optimization but does not request exhaustive full search, include a bounded `iterations` value in `/optimization/start` (usually 50-100 for a first pass); do not let the job default to the full search space in an interactive turn
  - use canonical `iterations` for the run cap; `maxIterations` is only a tolerated low-context alias
  - do not send a top-level `ranges` array or `parameterCodeName` list to `POST /api/scripts/{name}/optimization/start`; that shape belongs to earlier range configuration via `POST /api/scripts/{name}/ops` with `SetOptimizationRange`
  - if the latest `authoring-quality`, `intent-check`, lifecycle result, or `GET /api/scripts/{name}/parameters` still shows an unresolved script, formula, or runtime error on the same artifact, repair it first instead of starting optimization
  - when reading `GET /api/scripts/{name}/parameters`, inspect the top-level readiness fields such as `response.data.optimizationReady`, `response.data.nextStepHint`, and `response.data.suggestedNextRoutes`, not only `response.data.parameters[]`
  - when `optimizationReady=true`, choose `selectedParameterIds` only from the exact current `response.data.parameters[].id` values and keep sibling logical families aligned through `response.data.selectionHints[]`
  - if the create/template response included `defaultOptimizationRequest`, use:
    - `POST /api/scripts/{name}/optimization/start`
    - body example for a single-parameter job:
      - `{ "parameterName": "lookbackBars", "min": 20, "max": 200, "step": 20, "keepTop": 5 }`
    - body example for an exact selected subset:
      - `{ "selectedParameterIds": ["<parameter-id>"], "keepTop": 5 }`
  - otherwise:
    - `GET /api/scripts/{name}/lab-options`
    - read `response.data.options`
    - post the full `options` object back with `rtUpdates=false`
    - `POST /api/scripts/{name}/optimization/start`
- Read from the start response:
  - `response.jobId`
  - `response.scriptName`
  - `response.status`
  - `response.selectedParameterCount`
  - `response.configuredRangeParameterCount`
- Treat configured ranges and the current selected subset as different things.

## Phase 2: Poll

- Call:
  - `GET /api/scripts/optimizations/{jobId}`
- Stop polling only when the job is completed.
- If `searchSpace` or `plannedIterations` exceed the user-stated cap, cancel the same job with `POST /api/scripts/optimizations/{jobId}/cancel`, narrow ranges or `selectedParameterIds`, and start one new job. Do not keep polling an over-budget job.
- If `plannedIterations` is unexpectedly large for this interactive turn, cancel the same job and restart with a smaller `iterations` cap and/or narrower `selectedParameterIds`; do not wait through a long full-space run.
- If status stays `Running` with `completedIterations = 0` for too long, or the later `best` route returns `404`, treat that as a stalled or no-result optimization. Read `GET /api/scripts/{name}/messages` and `GET /api/scripts/{name}/logs`, cancel the same job, then either retry once with a narrower subset/range or report failure or near-miss honestly.
- Do not use `while true` shell loops when the status route already exists.

## Phase 3: Best

- Call:
  - `GET /api/scripts/{name}/optimizations/{jobId}/best?metric=NetProfit&rank=1`
- Read:
  - `response.parameterValues`
  - `response.suggestedValue`
- Do not infer the winner from `runId` or table order.

## Phase 4: Apply and confirm

- Call:
  - `POST /api/scripts/{name}/optimizations/{jobId}/apply?metric=NetProfit&rank=1`
- Then:
  - `POST /api/scripts/{name}/build`
  - `POST /api/scripts/{name}/run`
  - `GET /api/scripts/{name}/metrics-summary`
  - `GET /api/scripts/{name}/messages`
  - `GET /api/scripts/{name}/logs`
- Final fields:
  - `response.data.netProfit`
  - `response.data.allTrades`
  - `response.data.profitFactor`
  - `response.data.maxDrawdownPct`

## Guardrails

- Reuse the current script name.
- Do not create or copy scripts during optimization.
- Do not guess `/api/optimization` or other undocumented routes.
- `usedInOptimization` is persisted default selection only; it does not mean every range-configured parameter must participate in this job.
- If the prompt asks whether the result cleared a bar, state the final optimization verdict explicitly as pass, near-miss, or fail. Do not hide that verdict behind softer words such as successful or acceptable.
