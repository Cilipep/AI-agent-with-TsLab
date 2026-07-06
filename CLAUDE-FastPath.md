# Claude Fast Path

Start with this file in Claude/openclaude.
Use this file together with `AGENTS-FastPath.md`.
Do not open `AGENTS-FastPath.md` end-to-end at startup.
Use `AGENTS-FastPath.md` only after a concrete localhost blocker and only through one small `Read` slice or one exact keyword search.
This file is the bootstrap brief for Claude/openclaude and includes the minimum common rules needed before the first localhost mutation.

## Bootstrap common rules
- Treat canaries as generic regression classes, not as prompt-specific targets. Do not optimize behavior for prompt ids or one canned wording. Pass by following the live API contract on the current artifact.
- Make the first meaningful step a concrete tool call, not a prose-only plan.
- On an exact local-file task, the first step must be an exact `Read` of that file.
- If that file or the local AGENT file already enumerates the next exact local file paths, read those exact paths directly in that declared order. Do not list sibling directories first.
- On an exact existing-script settings task, after `GET /api/status` the first meaningful call must be `GET /api/scripts/{name}/lab-options`.
- On an exact-name create-run task with known datasource, security, and interval, go `POST /api/script-manager/scripts` -> `POST /api/scripts/{name}/instrument-source` -> first real `POST /api/scripts/{name}/ops`.
- For graph-authored blank-create workflows, do not use `POST /api/scripts` as the create step. `POST /api/scripts` is the code-first script route; the ordinary graph-authoring blank-create route is `POST /api/script-manager/scripts`.
- Runtime/date settings such as `DateReload`, `useDateReload`, `DateFrom`, `DateTo`, and `interval` belong to `GET/POST /api/scripts/{name}/lab-options`, never `/ops` and never control-pane mutations.
- Default localhost API base is `http://localhost:5000/api`. Do not probe `8080`, `8081`, or other alternate localhost ports just because one call shape failed. After one successful localhost API call in the current stage, pin that same scheme/host/port for the rest of the stage unless a direct retry on that same base proves the server moved.
- In real PowerShell sessions, use `curl.exe`, `Invoke-RestMethod`, or `./api-json.ps1`; do not use bare `curl`, because PowerShell resolves it to a web alias.
- For `./api-json.ps1`, pass the body file as the plain third positional argument, for example `./api-json.ps1 POST /api/scripts/{name}/ops ./tmp/ops.json`. Do not write `@ops.json` with the helper; the helper itself adds the `@file` syntax when it calls `curl`.
- For exact script-scoped routes on one known artifact, prefer `./script-api.ps1 <METHOD> "<scriptName>" <route> [bodyFile]` or `./script-api.sh ...` instead of hand-assembling `/api/scripts/<route>/by-name/...` for foldered names.
- A local `./ops.json` or `./tmp/*.json` repair body is not a mutation by itself; once it is ready, the very next step must be the matching `POST`, then a live proof route.
- For `/ops` JSON bodies, `ops` must remain a JSON array, not a quoted JSON string. Do not pre-serialize the ops list into a string before `ConvertTo-Json`; keep it as an array or post a UTF-8 body file.
- If `run` returns `CompletedNoData` or another no-data state while sources are already configured, treat the next step as `lab-options` date/runtime repair first. Do not try `UpdateControlPane`, `AddControlPane`, or other `/ops` control-pane edits for date/runtime recovery.
- If `/mappings` already shows datasource/security on every required source block and `run` still reports `instrument not selected`, another source-selection error, or `CompletedNoData`, do not repost the same `instrument-source` body first. Read `/messages`, `/logs`, and `/lab-options` to separate runtime source-resolution problems from an overly narrow date window; only remap or reconnect after those routes show that exact blocker.
- If the current localhost response already exposes `requiredNextMutationRoute`, `suggestedRepairOps[]`, or another concrete repair batch, use that on the same artifact before more discovery.
- If `authoring-quality` on the current artifact still says `SourceOnlyGraph` and already exposes non-empty `suggestedRepairOps[]` or `requiredNextMutationRoute = POST /api/scripts/{name}/repair/authoring-quality`, the very next tool call must be that wrapper repair on the same artifact. Do not stop at the diagnostic read, do not reread docs, and do not handcraft a fresh `/ops` batch before that first scaffold repair.
- `/ops` accepts canonical low-level mutation names only, such as `AddBlock`, `Connect`, `ConnectByInputName`, `Disconnect`, `SetParam`, `AddPane`, `AddGraphLink`, `AddControlPane`, `AddControlLink`, `SetSourceMapping`, and `SetOptimizationRange`. Do not invent pseudo-ops or macros such as `AddTradeBlock`, `AddEntry`, `AddExit`, or `AddIndicator`.
- If `/ops` returns `NoCompatibleInput`, `AmbiguousAutoConnect`, `InvalidConnectByInputName`, or `UnknownInputName`, do one exact contract read for the affected block and then resend a corrected `/ops` batch. Do not continue lifecycle or broad discovery first.
- If `authoring-quality`, `intent-check`, or `run` still says `requiresRepair=true`, `CompletedPartial`, `CompletedNoData`, or another repair state, the artifact is not done.
- For run-based tasks, final proof stays on the same artifact and must include the relevant authoring/intent checks plus `validate -> build -> load -> run -> metrics-summary` when applicable.
- If a tool result includes `persistedOutputPath` or a saved-large-output hint under `.claude/projects/...`, ignore that cache path and issue one narrower live localhost read instead.
## Claude-specific notes

- Keep one current artifact; the common artifact-continuity workflow itself still lives in `AGENTS-FastPath.md`.



- Stay inside the current packaged workspace.

- Do not assume local `.opencode/skill/*` is auto-loaded. The local markdown docs are the primary instruction surface.

- Detect the active shell from tool behavior, not from the OS. Claude can expose a Bash or POSIX shell even on Windows.

- If the active shell is Bash or POSIX, do not use PowerShell-only syntax such as `Out-String`, `ConvertTo-Json`, `Invoke-RestMethod`, or `powershell -Command` wrappers for ordinary localhost API calls.

- In Bash or POSIX mode, prefer the shell-matching helpers `./api-json.sh`, `./create-script.sh`, and `./run-lifecycle.sh` plus workspace-relative body files under `./tmp/`. Default to relative `/api/...` routes so the helper normalizes them to `http://localhost:5000`; do not guess `8080`.
- For `./api-json.sh`, pass the body file as the plain third positional argument, for example `./api-json.sh POST /api/scripts/{name}/ops ./tmp/ops.json`. Do not write `@ops.json` with the helper; the helper itself adds the `@file` syntax when it calls `curl`.

- In Bash or POSIX mode, do not invoke `powershell.exe` or `.ps1` wrappers just to call localhost API routes. Use the `.sh` helper directly with its documented positional form, for example `./api-json.sh GET /api/...`, `./api-json.sh POST /api/...`, or `./api-json.sh POST /api/... <bodyFile>`, and do not invent wrapper flags such as `-BodyFile`.

- In real PowerShell sessions, prefer `./api-json.ps1`, `./create-script.ps1`, `./run-lifecycle.ps1`, or `Invoke-RestMethod`.
- In real PowerShell sessions, if you use `./create-script.ps1`, pass the leaf script name and parent folder path as separate arguments, for example `./create-script.ps1 "My Script" "AI/KaufmanStrategies"`. Do not pass `AI/KaufmanStrategies/My Script` as one `<leafName>` argument.
- In real PowerShell sessions, for `/by-name/{**name}` routes with spaces or `/`, quote the whole route argument once, for example `./api-json.ps1 GET "/api/scripts/ui/by-name/AI/KaufmanStrategies/My Script"`. The packaged `api-json` helper normalizes URI spaces for that quoted route string. Do not write `/by-name/"AI/KaufmanStrategies/My Script"` and do not guess leaf-only or id-only variants unless that endpoint explicitly advertises them.
- If a create/search/by-name response returns multiple rows sharing one leaf name, the exact foldered artifact is the row whose `data[*].name` exactly equals the requested full server-side path. Do not reconstruct "exactness" from `parentFolder` plus the leaf name.
- Once the exact full-path artifact is known, pin the full route name or packaged `@last-created` helper for later mutation routes in the same stage. Do not hand-write numeric-id script routes for lifecycle proof unless that exact endpoint explicitly documents id support, do not keep re-searching by leaf name, and do not pivot to a shorter duplicate.

- In Bash or POSIX mode, use workspace-relative `@./tmp/body.json` or `@tmp/body.json` with forward slashes. Avoid absolute `@C:\...` body-file paths.

- In Claude built-in tools, `Glob` requires an explicit `pattern`. If you do not already know the pattern, do not call `Glob` with only `path`; switch to `Read`, `Bash`, or the localhost API.

- In Claude built-in tools, `Grep` requires an explicit `pattern`. If the pattern is still unknown, do not loop invalid `Grep` calls just to discover one.

- In Claude/openclaude, once one exact `Read` or one live localhost blocker on the current artifact has already succeeded in the current stage, do not restart that stage with `Glob`, `ls`, or broad workspace discovery. Continue from that exact file or live blocker instead.

- In Claude/openclaude create-phase work for an exact new script name, if one filtered /api/scripts?query=... call returned only near-match names and not the exact target, do not repeat that query or inspect those near-match scripts. Create the exact artifact immediately.
- In that same exact-name create phase, do not guess routes such as /api/scripts/create or /api/scripts/template for ordinary blank-create. Use the documented POST /api/script-manager/scripts route from the common fast path.

- In Claude `Read`, `limit` is a line-count guard, not a token budget. On large local docs such as `AGENTS-FastPath.md`, start with a small slice such as `offset=0, limit=80` or `limit=120`, not `500`, `1000`, or `5000`.

- If a doc `Read` returns a token-limit error, immediately retry with a smaller line slice on that same file. Do not repeat larger `Read` calls and do not switch into broad `Glob` or `Grep` discovery just because the first doc read was too large.

- For ordinary text or markdown files, `Read` should normally use only `file_path`, `offset`, and `limit`; omit `pages` entirely unless the tool explicitly needs page ranges. If `Read` fails because of an invalid `pages` value, the immediate retry on that same file must omit the `pages` field entirely instead of repeating the same invalid shape or switching to `Glob`, `Grep`, or a larger page range.

- After one successful `Read` of `AGENTS-FastPath.md` or `CLAUDE-FastPath.md` in the current stage, do not reread those files again before the next concrete localhost mutation or verification step unless the latest live error is still a tool-shape/schema error that those docs directly answer.

- After two identical tool schema or validation errors on the same call shape, stop repeating that loop. Switch to another call shape or the direct localhost API route.

- On short localhost API tasks, do not spend the first assistant turn on a prose-only plan. Make the first meaningful output a concrete tool call in the current Claude runtime.

- For localhost API JSON, use full structured reads as the source of truth. Do not use `grep`, `head`, or partial line scraping as the decision source.

- In Claude Bash or POSIX shells, do not assume `jq`, Python, Node, Perl, or other extra JSON-processing helpers are available just to inspect localhost JSON. Prefer one raw `curl` response plus direct reasoning, or save the payload under `./tmp/` and inspect it with `Read`.

- If a live `/explain`, `/graph`, `/authoring-quality`, or similar localhost JSON payload is too large to inspect directly, save it once under `./tmp/*.json` and inspect that local file with `Read` slices. Do not keep retrying live `grep` or pipe variants against the same large payload.

- If one `grep`, `head`, or other partial-shell extraction on a live localhost JSON payload returns no match or a shell error, stop repeating near-identical extraction attempts. Switch to one narrower localhost route or to `Read` on a workspace-local saved payload instead.

- If one raw localhost JSON response already proves the needed field or blocker, do not spend another shell step reparsing that same payload with `jq`, Python, or other helper binaries.

- Do not read `.claude/projects/...`, `tool-results/*.txt`, temp logs, transcript caches, or other internal assistant cache files as source-of-truth when the live localhost API exists.

- If a tool result includes `persistedOutputPath` or any saved-large-output hint under `.claude/projects/...`, ignore that cache path and issue one narrower live localhost read instead.

- Internal assistant cache files under `.claude/projects/...`, including `tool-results/*.txt`, are never a supported follow-up input for TSLab decisions. Even if a tool saved a huge payload there, follow the live localhost route again with a smaller projection instead of reading or grepping that cache.

- In the Claude `Bash` tool, use Bash syntax only. Do not paste PowerShell assignment or `Invoke-RestMethod` snippets into a Bash command. If you need PowerShell-only syntax, switch to a direct localhost API shape that fits the current shell instead of mixing shells.

- Do not use shell `while true` polling loops when a discrete status endpoint already exists.

- `GET /api/scripts/{name}/explain` must prove the exact required block family before a final success claim.

- Keep one current artifact and verify that same artifact through `validate -> build -> load -> run -> metrics-summary` when the task is run-based.

- On continuation turns, do not restart with `ls`, `/api/status`, broad AGENTS rereads, or vague handler hunts if the current artifact already exists. Start from the latest live `authoring-quality`, `/explain`, `validate`, `build`, or `run` blocker on that same artifact.

- If that blocker is not already fresh in hand, refresh it first with `GET /api/scripts/{name}/authoring-quality` on the same artifact. If the latest blocker already names a concrete block, input, or incompatible link, repair that exact defect or read one exact handler family for it. Do not broaden into searches like `Logic`, `Compare`, or other category guesses first.

- If `authoring-quality`, `intent-check`, or another live response on the current artifact already exposes `requiredNextMutationRoute`, `suggestedRepairOps[]`, `suggestedVisualizationOps[]`, or another concrete repair batch, the next step must stay on that same artifact and use that repair route or a direct `/ops` batch derived from it. Do not pivot to `/api/scripts/templates...`, template by-name apply routes, or helper-template discovery while that concrete repair path is still open.

- If the current artifact already exists and the latest blocker is structural on that same artifact, do not try to solve it by applying a different template over the same name. Repair the existing artifact first; only switch to a different template when the prompt explicitly asked for that template workflow or when no current-artifact repair route exists.

- If a mutation response on the current artifact already reports BlockExists, PaneExists, LinkExists, or another duplicate/additive replay error, stop resending the same broad batch. Refresh one exact live view of the current artifact and send one smaller repair/update/disconnect batch instead.

- If the user gives a numeric acceptance bar, report fail or near-miss until the actual metric clears that numeric acceptance bar.



