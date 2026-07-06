---
name: tslab-script-authoring
description: "Phase card for creating or repairing one server-side TSLab script via Web API."
---

# TSLab Script Authoring

Use this as the active phase card for one current server-side script artifact. Server-side TSLab scripts are graph artifacts, not local `.cs` files.

## When to load

- Use when the task is to create, repair, or finish one script.
- Do not use for clone/V2/improve-existing work; open `$tslab-script-clone-edit` first.
- Do not read or create local `scripts/*.cs` files for server-side script authoring.
- Work in the current packaged workspace. Keep request bodies under `./tmp/...`.
- For foldered names, do not guess leaf-only or id-only variants unless that endpoint explicitly advertises them.

## First call

1. Create or resolve the exact current artifact.
2. If the prompt gives datasource/security/timeframe, call `instrument-source` on that artifact.
3. Apply the first meaningful graph mutation with explicit `/ops`.
4. Read `authoring-quality?compact=true`; if prompt-specific features exist, run `intent-check?compact=true`.
5. Prove with `validate -> build -> load -> run -> metrics-summary`, then read `messages` and `logs` before final claims.

- Exact new script: `./create-script.ps1 "<leafName>" ["<parentPath>"]` or `POST /api/script-manager/scripts`.
- Known current artifact: start from `GET /api/scripts/{name}/authoring-quality?compact=true`, `GET /api/scripts/{name}/explain?summary=true`, or the route named by the previous helper summary.
- blank create plus explicit `/ops` is the normal authoring path. A blank-create response is never a finished result for the same turn.

## Next allowed call

- After create: `POST /api/scripts/{name}/instrument-source` when datasource/security/timeframe are known, then `POST /api/scripts/{name}/ops`.
- After `/ops`: `GET /api/scripts/{name}/authoring-quality?compact=true`, `POST /api/scripts/{name}/intent-check?compact=true` when prompt-specific proof exists, then lifecycle proof.
- After a clean lifecycle: `GET /api/scripts/{name}/metrics-summary`, `messages`, and `logs`.

## Fields to read

- `response.scriptName`
- `response.scriptId`
- `response.createMethod`
- `response.workflowHints`
- `response.data.requiresRepair`
- `response.data.requiredNextMutationRoute`
- `response.data.suggestedRepairOps`
- `response.data.readBudgetBeforeMutation`
- `response.data.primaryMutationObjectives`
- `response.data.preferredDiscoveryRoutes`

## Hard Rules

- A first meaningful implementation turn or first working pass must include the first real `/ops` scaffold. Blank-create or instrument-source alone is still not meaningful progress.
- If a helper prints `HELPER_SUMMARY`, `INCOMPLETE_TURN_DO_NOT_ANSWER`, `sameTurnIncomplete=true`, or `apply-next-ops-before-answer`, the next action is the named same-artifact route, not a final answer.
- If the prompt prescribes an exact report shape, reproduce it after proof. Do not answer with only an acknowledgment.
- Do not start optimization unless the prompt explicitly asks. On an optimization follow-up for an already-created artifact, prove the current artifact is clean first; the turn is still open once the script becomes runnable.
- Do not create or mutate `agent-manager/agents` as a workaround for ordinary script authoring, charting, cached proof, or script analysis.
- Do not guess code/content routes such as `/api/scripts/get_code`, `/api/scripts/{name}/runs`, or `/api/agents/{scriptName}/results`.
- When sibling blocks share period, width, or threshold settings, prefer one explicit shared knob/range instead of divergent hidden literals.

## Canonical `/ops` field rules

Keep these exact before the first `/ops`:

- Use canonical `/ops` field names only: `blockId`, `typeName`, `blockType`, `category`, `fromBlockId`, `toBlockId`, `fromPort`, `toPort`, `toInputName`. Do not invent aliases such as `from`, `to`, `block`, `key`, `handlerTypeName`, `fromBlock`, `toBlock`, `blockKey`, or `toPortNum`.
- For handler blocks use the live `suggestedAddBlockOp` / `canonicalAddBlockOp` from `GET /api/handlers/{typeName}`; do not hand-author `ConverterItem` plus `handlerTypeName`. One-input handlers such as `High`, `Low`, `Close` usually resolve to `ConverterItem` plus `typeName`; 2+ input handlers usually resolve to `TwoOrMoreInputsItem` plus `typeName`.
- Treat `Input0`, `Input1`, ... as slot metadata, not real ports. Prove real entry/exit wiring such as `Src`, `Eq`, `Pos`, and `SECURITYSource` instead of trusting `Input0`/`Input1` defaults.
- For trade blocks set a real numeric `Shares` (for example `Shares = 1`) front-loaded; do not leave `Shares` unset or symbolic.
- For optimization ranges use `paramInvariantName`, never `paramName`, and keep a baseline `value` on every ranged param.

## Scope and proof budget

- Web research is bounded: at most 2 web sources for a strategy or research-to-script prompt (one idea/spec source, one reference). After the second source or a `404`, stop browsing and build the artifact with `/ops`.
- For a base-plus-compressed-timeframe prompt, prove both branches: the base interval through `GET /api/scripts/{name}/lab-options`, and the compressed branch through the compression handler actually wired in the graph. Do not claim the compressed branch from lab-options alone.
- Improvement, optimize, or compare requests require tested candidates: run each candidate on the live artifact and report measured before/after metrics. Do not deliver untested `could try` / `можно попробовать` / `not tested` suggestions when the prompt asks for improvements or your own answer claims tested/optimization results.

## References

Read only the narrow reference needed by the current blocker:

- `references/powershell-body-files.md`: PowerShell, curl, UTF-8 JSON body files, helper usage, and path rules.
- `references/runtime-no-data-date-range.md`: `CompletedNoData`, datasource/admin boundaries, cached history, lab-options/date windows.
- `references/graph-ops-contract.md`: `/ops` payload shape, template/handler contract reads, block/link field names, failed writes.
- `references/control-pane-wiring.md`: explicit `AddControlPane` / `AddControlLink` wiring and `dataXml`.
- `references/trade-scaffold-repair.md`: first tradable scaffold, entry/exit families, order price repair, trade-path blockers.

## Stop if failed

- Stop after the first failed write step and inspect the documented response/body contract.
- If `/ops` returns `applied=false`, assume none of that failed batch committed; refresh one compact live view and retry only the first failing family.
- Do not start a clean-slate rebuild, switch scripts, switch providers, or remove required prompt features to make lifecycle pass.
