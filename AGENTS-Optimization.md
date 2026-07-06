# Agent Instructions: Optimization

Use this file when the prompt explicitly asks to optimize, compare optimization rows, or apply a best result.
Do not enter this phase just because the script is optimization-ready.

## Hard rules

- Optimization is same-script and same-graph. Do not emulate it by cloning scripts or templating a new script per candidate value.
- `SetOptimizationRange` configures the baseline value and optimization range for a parameter.
- `SetOptimizationRange` uses `paramInvariantName`, not `paramName`.
- `usedInOptimization` is a persisted default selection flag, not a synonym for "this parameter must participate in every future job".
- For a concrete optimization run, prefer `selectedParameterIds` on `POST /api/scripts/{name}/optimization/start` so the job uses only the exact subset requested by the user.
- For foldered scripts, use the folder-safe routes: `POST /api/scripts/optimization/start/by-name/{**name}`, `GET /api/scripts/optimizations/{jobId}/best/by-name/{**name}`, and `POST /api/scripts/optimizations/{jobId}/apply/by-name/{**name}`. The packaged `script-api` helpers produce this shape automatically when the script name contains `/`.
- For interactive agent optimization when the user did not explicitly request an exhaustive full search, include a bounded `iterations` value in `/optimization/start` (usually 50-100 for a first pass) and keep `selectedParameterIds` narrow. Do not start an unbounded full search space just because ranges exist.
- The canonical run-cap field is `iterations`. `maxIterations` is tolerated as a low-context alias, but prefer `iterations` in examples and request bodies.
- `POST /api/scripts/{name}/optimization/start` is not the place for a top-level `ranges` array or `parameterCodeName` list. Configure ranges first through `POST /api/scripts/{name}/ops` with `SetOptimizationRange`, then start the job with `selectedParameterIds` or another supported start selector.
- If the prompt asks to optimize only one or two parameters, do not run every range-configured knob. Keep the job-scoped selected set narrow.
- If you only need to configure ranges, `SetOptimizationRange` may omit `usedInOptimization`; do not force it to `true` unless you intentionally want to change the persisted default selection.
- Never hardcode a parameter again with `SetParam` after marking that same parameter for optimization.
- Seed ranges from handler metadata or from server-provided `suggestedSetOptimizationRangeOp` candidates when available.
- `MissingControlPane` is irrelevant unless the prompt explicitly requires editable runtime controls.
- A `rank=1` row is not success by itself. Check trade count, profit factor, drawdown, and prompt-specific guardrails.
- When the prompt asks whether the optimization cleared a bar, the final verdict must explicitly use one of these labels: pass, near-miss, or fail. Do not substitute softer wording such as successful, good, or acceptable for that acceptance verdict.
- After `apply`, always rerun the artifact and fetch `metrics-summary`, `messages`, and `logs`.
- On an optimization continuation, do not start with `glob AGENTS*.md`, full script XML/details dumps, or Task/explore/subagent tools. Stay on the exact optimization routes and the current artifact.
- Do not inspect `GET /api/scripts/optimizations` or reuse historical jobIds from older runs as proof for the current task. On a fresh optimization turn for the current artifact, start one fresh `POST /api/scripts/{name}/optimization/start` and only continue the jobId returned by that start response unless the same turn already started the exact job you are continuing.
- Do not use `GET /api/scripts/{name}/metrics` as a substitute for `GET /api/scripts/{name}/metrics-summary`.
- If the started job exceeds the user-stated run cap, cancel that same job with `POST /api/scripts/optimizations/{jobId}/cancel`, narrow the selected subset or ranges, and start one new job.
- If `plannedIterations` is unexpectedly large for an interactive turn, cancel that same job, restart with a smaller `iterations` cap and/or narrower `selectedParameterIds`, then continue through `best` and `apply`.
- If the job stays at `completedIterations = 0` and later yields no best row, treat it as stalled or no-result: read `messages` and `logs`, then cancel/retry once or report failure honestly.
- Manual comparisons, one-off reruns, or final-text claims do not count as optimization. When the prompt asks to optimize, choose the best row, or apply the best result, you must use the server optimization workflow: `/optimization/start` plus `/results` or `/best`, then `/apply` when required.
- If the latest `authoring-quality`, `intent-check`, `validate`, `build`, `run`, or `GET /api/scripts/{name}/parameters` still shows an unresolved script, formula, or runtime error on the same artifact, optimization is blocked. Repair the current artifact first; do not widen ranges, change `selectedParameterIds`, or retry `/optimization/start` blindly.
- When you call `GET /api/scripts/{name}/parameters`, inspect the top-level readiness fields such as `response.data.optimizationReady`, `response.data.nextStepHint`, and `response.data.suggestedNextRoutes`, not only `response.data.parameters[]`.
- If the same parameters response includes `response.data.selectionHints[]`, treat those hints as advisory grouping for sibling parameter ids that may represent one shared logical knob. When the prompt asks for shared upper/lower bands, paired thresholds, or one logical family, keep those ids aligned instead of counting each sibling id as a separate optimization family.
- If a prompt-required optimization family is missing from `GET /api/scripts/{name}/parameters` only because the current artifact buried that tuning value as a raw literal inside `BoolCustomHandlerItem` / `DoubleCustomHandlerItem` `Expression` text, treat that as unfinished authoring on the same artifact. Unless the user explicitly asked for analysis-only or no more graph changes, externalize that knob into a real numeric parameter or a dedicated constant/value block, add `SetOptimizationRange`, and then continue the server optimization workflow. Do not stop with a follow-up question and do not silently optimize unrelated fallback parameters instead.
- A `400` from `/optimization/start` saying the current script has an unresolved error is an authoring-repair signal, not a prompt to guess a different request body or a broader optimization subset.

## Preparation

Before starting optimization:

1. `GET /api/scripts/{name}/parameters`
2. `GET /api/scripts/{name}/lab-options`
3. Set `rtUpdates=false` in `lab-options`
4. Ensure the intended numeric parameters have real optimization ranges
5. Decide which exact parameter ids should participate in this job

If `optimization/start` reports `optimizationReady=false`, stop and repair either the missing ranges or the missing job-scoped selection first.

## Range selection

Use one of these sources of truth:

- `GET /api/handlers/{typeName}`
- `optimizationCandidates[*].suggestedSetOptimizationRangeOp`

Manual narrowing is allowed only as an intentional narrowing around the current baseline or a user-stated hypothesis.
Do not invent wide ranges from memory.

## Selected subset vs configured ranges

Treat these as different concepts:

- configured ranges: parameters that already have `min`, `max`, and `step`
- selected subset: parameters that should participate in the current job

When `selectedParameterIds` is omitted, the server may fall back to persisted `UsedInOptimization`.
If `response.data.selectionHints[]` groups several ids under one handler family plus invariant, use that as a hint for shared logical knobs. It is advisory, not a mandate, but when the prompt asks for one shared family you should not inflate the job just because sibling ids exist.
When the prompt is explicit about the optimization subset, send `selectedParameterIds` and do not rely on the persisted defaults.
After ranges are configured, reread `GET /api/scripts/{name}/parameters` and copy the exact current `response.data.parameters[].id` values. `selectionHints` are grouping hints for those ids, not replacement ids, so do not synthesize `selectedParameterIds` from block GUIDs, block names, or invariant names.
If `response.data.parameters[]` is still empty, the job-scoped selection is not ready yet even if `optimizationCandidates[]` exist. Finish range configuration and reread `/parameters` before `optimization/start`.

## Start and monitor

Typical flow:

1. `POST /api/scripts/{name}/optimization/start`
2. poll job status
3. read top rows through the results endpoint
4. read the best row through the best endpoint
5. apply the chosen row
6. rerun the same artifact
7. read final metrics and logs

Do not request all rows. Always use paged or top-K result queries.
Do not use shell `while true` polling when the status route already exists; poll one discrete status step at a time.

## Best-row evaluation

Reject a best row when it clearly fails the bar:

- `allTrades = 0`
- `netProfit < 0`
- `profitFactor < 1`
- absurd drawdown
- explicit prompt guardrail failure

In that case, report that the searched region or the hypothesis did not clear the bar.
Do not present it as a successful optimization just because it is `rank=1`.
If the user gave a numeric acceptance bar, a near-miss is still a fail or near-miss until the actual metrics clear that number.

## Final verification

After `apply`:

1. `POST /api/scripts/{name}/build`
2. `POST /api/scripts/{name}/run`
3. `GET /api/scripts/{name}/metrics-summary`
4. `GET /api/scripts/{name}/messages`
5. `GET /api/scripts/{name}/logs`

If final economics are poor, report the optimization as completed but unsuccessful.
