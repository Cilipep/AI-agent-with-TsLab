---
name: tslab-script-clone-edit
description: "Copy an existing TSLab script, edit it safely via graph/json endpoints, then validate/build and stop on the first failed write step."
---

# TSLab Script Clone/Edit

## Do not load unless

- The task is to copy, mutate, or repair a script.
- Load this skill even for an inspect-only planning turn if the next turn will copy or modify a script.
- Do not load this skill for pure read/run, portfolio compare, or optimization-only tasks.
- Do not load this skill for fresh-create authoring or normal repair of the current artifact. Use script-authoring routes there; raw graph JSON is not the default repair path.

## Canonical route family

- Resolve source by name: `GET /api/scripts/{name}`
- Preferred helper: `./copy-script.ps1 "<sourceName>" "<newName>"` or `./copy-script.sh "<sourceName>" "<newName>"`; it pins the copy as `@last-created`.
- Preferred clone route: `POST /api/scripts/{name}/clone`
- Foldered source clone route: `POST /api/scripts/clone/by-name/{**name}`
- Script-manager clone route when the source is only in the body: `POST /api/script-manager/scripts/clone`
- Backward-compatible copy route: `POST /api/scripts/{name}/copy`
- Fallback copy route when you already have the ScriptManager id: `POST /api/script-manager/items/{scriptId}/copy`
- Graph/json reads: `GET /api/scripts/{name}/json`, prefer `/explain?summary=true` before full `/explain`
- Safe edits: prefer `POST /api/scripts/{name}/ops`. Use `PUT /api/scripts/{name}/json?preserveId=true` only for deliberate clone-edit graph replacement after reading the exact copied graph.
- Checks: `POST /api/scripts/{name}/validate`, `/build`

## Hard rules

- `/api/scripts/*` is name-based; `scriptId` is only for `script-manager` copy/tree routes.
- For script copy, prefer `./copy-script.ps1` / `copy-script.sh` or `POST /api/scripts/{name}/clone` with `{ "name": "NewScript" }` or `{ "newName": "NewScript" }`.
- `create-script.ps1 "<source>" "<dest>"` is not cloning; the second argument is parentPath.
- For script-manager clone, use `{ "sourceScriptName": "OldScript", "name": "NewScript" }` or `{ "sourceName": "OldScript", "newName": "NewScript" }`.
- If only family variants remain after discovery (for example `p01/p03/p04/p05`), report the candidate set instead of silently choosing one for mutation work.
- Never search workspace files with `rg`, `glob`, or filesystem scans to discover server-side scripts.
- For `GET /api/scripts/{name}/json`, read the graph from `response.data`.
- For `PUT /api/scripts/{name}/json`, send only the graph object, not the whole envelope.
- Use UTF-8 bytes for JSON, typically `curl --data-binary @file.json`. On Windows PowerShell, call `curl.exe`.
- On trusted localhost, omit `Authorization` unless auth is actually required. Never send an empty `Authorization: Bearer ` header.
- If you use `curl.exe`, do not use PowerShell-only `-Body`.
- In PowerShell, do not chain multiple API calls with `&&`. Use separate tool calls, or `;` only when later commands do not depend on earlier failures.
- Do not use POSIX shell idioms such as `/dev/null` redirection in PowerShell-based tool calls.
- After the first failed write step, stop and inspect the documented route/body instead of guessing alternatives.
- If one bad or duplicate live link on the same artifact is the blocker, `/ops` is not "append-only": refresh one exact live view, remove the bad link with `Disconnect` or returned cleanup ops, then reconnect on the same artifact. Do not pivot to guessed `/graph`, external cache files, or raw XML/viewModel patching just because an earlier `Connect` added another link.
- Read `GET /api/scripts/{name}/explain?summary=true&compact=true` before ops edits. If compact summary is insufficient, fall back to `GET /api/scripts/{name}/explain?summary=true`, and only then to the full `/explain` payload; never guess block ids or `CodeName`.
- Do not invent undocumented routes such as `POST /api/scripts/{name}/graph`, `PUT /api/scripts/{name}/graph`, or `POST /api/script-manager/scripts/clone-script`.
- There is no documented `/graph` mutation route. Even a single-block or single-parameter edit must use `/ops` or `PUT /json`.
- If the task is fresh-create authoring, ordinary AQ/intent/runtime repair, control-pane wiring, datasource mapping, chart visualization, or parameterization, treat `/json` as evidence-only even though clone-edit still documents `PUT .../json?preserveId=true` for deliberate copied-graph replacement.
- In Windows PowerShell, do not pipe `curl.exe` output into nested `powershell -Command` JSON parsing. Use `Invoke-RestMethod`, the packaged helper, or one workspace-local UTF-8 temp file parsed in the same shell.
- Equal `blockCount` and `linkCount` do not prove family variants are equivalent. If summaries still look comparable, inspect `/parameters` or report insufficient evidence instead of promoting the earliest timestamp as the baseline.

## Canonical `/ops` field rules

When you mutate the copied graph with `/ops`, keep these exact:

- Use canonical `/ops` field names only: `blockId`, `typeName`, `blockType`, `category`, `fromBlockId`, `toBlockId`, `fromPort`, `toPort`, `toInputName`. Do not invent aliases such as `from`, `to`, `block`, `key`, `handlerTypeName`, `fromBlock`, `toBlock`, `blockKey`, or `toPortNum`.
- For handler blocks use the live `suggestedAddBlockOp` / `canonicalAddBlockOp` from `GET /api/handlers/{typeName}`; do not hand-author `ConverterItem` plus `handlerTypeName`.
- Treat `Input0`, `Input1`, ... as slot metadata, not real ports. Prove real entry/exit wiring such as `Src`, `Eq`, `Pos`, and `SECURITYSource` instead of trusting `Input0`/`Input1` defaults.
- For trade blocks set a real numeric `Shares` (for example `Shares = 1`) front-loaded; do not leave `Shares` unset or symbolic.
- For optimization ranges use `paramInvariantName`, never `paramName`, and keep a baseline `value` on every ranged param.

## Happy path

1. Resolve the exact source script by name, preferably via `GET /api/scripts?query=...&limit=20`, and read its details.
2. Copy it via `./copy-script.ps1 "<sourceName>" "<newName>"` or `POST /api/scripts/{sourceName}/clone` with `{ "name": "<newName>" }` or `{ "newName": "<newName>" }`.
3. Read `GET /api/scripts/{newName}/json`.
4. Read `GET /api/scripts/{newName}/explain?summary=true&compact=true` before deciding on an edit.
5. Prefer `/ops` for targeted mutations. Use `PUT /api/scripts/{newName}/json?preserveId=true` only when this clone-edit task truly requires replacing the copied graph object, and never for ordinary AQ/control-pane/mapping repair.
6. `POST /api/scripts/{newName}/validate`
7. `POST /api/scripts/{newName}/build`

## Common failure modes

- Copy fails: you used `create-script.ps1` as a clone helper, guessed `/api/script-manager/scripts/clone-script`, or tried `/graph` mutation instead of the documented helper/clone/json routes.
- JSON restore fails: you sent `{ success, message, data }` instead of raw `data`.
- Garbled block ids: request body was not UTF-8.
- Discovery drift: you omitted `limit` on `GET /api/scripts?query=...` and pulled a larger list than needed.
- Heavy inspect drift: you fetched the full `/explain` payload even though `?summary=true` would have been enough.
- Shell drift: you chained `curl.exe` commands with `&&` in PowerShell and the shell failed before the API call itself.
- Variant drift: you prepared a mutation plan for `p01` even though discovery still showed a family of comparable variants.
- Follow-up guesses spiral: a write step failed and you started inventing undocumented endpoints.

## References

- `AGENTS-ScriptEditing.md`
- `AGENTS-ScriptRuntimeParameters.md`
