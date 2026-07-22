# Capability Matrix: Live API vs Guidance

Use this file when the current runtime, AGENTS docs, skills, and older notes do not fully agree.

Source of truth order for disputed routes:
1. Live API on the current machine
2. Current controller source in `web/TSLab.WebApi/Controllers/`
3. AGENTS docs and `.opencode/skill/*`

## Script reads (`/api/scripts/*`)

| Route | Current contract for weak models |
|-------|----------------------------------|
| `GET /api/scripts/{name}` | Supported by script name. Treat this family as name-based unless a route explicitly documents id semantics. |
| `GET /api/scripts/{scriptId}` | Do not assume this exists. Portfolio or ScriptManager numeric ids are not interchangeable with script name routes. |
| `GET /api/scripts/{name}/parameters` | Supported by script name. Read this first to obtain stable `parameters[].id` values before `POST /parameters`. |
| `GET /api/scripts/{name}/json` | Supported by script name. |
| `GET /api/scripts/{name}/explain` | Supported by script name. |
| `POST /api/scripts/{name}/copy` | Supported by script name for low-context copy workflows. Accepts `{ "name": "NewName" }` or `{ "newName": "NewName" }`. |

### Identifier semantics
- `data.scripts[].name` from portfolio payloads is the safe follow-up key for `/api/scripts/{name}/*`.
- `data.scripts[].scriptId` in portfolio payloads is the portfolio child script id for nested portfolio routes such as `/api/portfolios/backtesting/{id}/scripts/{scriptId}/...`.
- `parentScriptId` belongs to ScriptManager creation/tree operations and is not a substitute for `/api/scripts/{name}`.

### Search guidance
- If script search or listing is fuzzy, prefer `GET /api/scripts?query=...&limit=50` over fetching the full list, then do a client-side exact match on `name`.
- If several close matches remain, do not pick the first by list order. Report the tied candidates and apply a deterministic exact-name rule.
- Do not plug a numeric id into `/api/scripts/{name}` just because the exact name was not found immediately.

### Mutation anti-hallucination
- Do not invent `POST /api/scripts/{name}/graph`, `PUT /api/scripts/{name}/graph`, or `POST /api/scripts/{name}/clone`.
- If a copy route is needed, prefer `POST /api/scripts/{name}/copy`. The older id-based `POST /api/script-manager/items/{scriptId}/copy` still works when you already have the ScriptManager id.

## Portfolio run results (`/api/portfolios/backtesting/runs/*`)

| Route | Current contract for weak models |
|-------|----------------------------------|
| `GET /api/portfolios/backtesting/runs/{jobId}` | Baseline supported status route. |
| `GET /api/portfolios/backtesting/runs/{jobId}/performance` | Baseline supported analysis route. Prefer this for summary metrics. |
| `GET /api/portfolios/backtesting/runs/{jobId}/profit` | Baseline supported analysis route. |
| `GET /api/portfolios/backtesting/runs/{jobId}/trades` | Optional capability. Confirm on the current runtime before relying on it in automation or guidance. |
| `GET /api/portfolios/backtesting/runs/{jobId}/positions` | Unsupported unless explicitly confirmed on the current runtime. Do not promise it by default. |

### Performance groups
- `data.groups[]` labels `All`, `Long`, `Short`, `Market` are observed output labels.
- Treat `data.all` as the preferred summary object.
- Do not assume `Long`, `Short`, and `Market` are formally documented, additive, or stable across builds unless verified on the current runtime.

### Result scoping
- Portfolio result routes are run-scoped, not portfolio-scoped.
- Use `GET /api/portfolios/backtesting/runs/{jobId}/performance`, `/profit`, and optional `/trades`.
- Do not invent `GET /api/portfolios/backtesting/{id}/performance` or `GET /api/portfolios/backtesting/{id}/profit`.

## Encoding guardrail
- If request JSON contains non-ASCII block ids or names, send UTF-8 bytes.
- On trusted localhost, omit `Authorization` unless auth is actually required. Never send an empty `Authorization: Bearer ` header.

## OpenCode local history
- OpenCode local history on this machine is stored under `C:\Users\nektodron\.local\share\opencode`.
- Useful locations:
  - `opencode.db`
  - `storage/session_diff/`
  - `tool-output/`
