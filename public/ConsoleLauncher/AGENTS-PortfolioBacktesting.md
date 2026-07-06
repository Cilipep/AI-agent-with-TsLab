# Agent Instructions: Portfolio Backtesting (Web API)

Goal: create and run portfolio backtests via API, inspect results, and optionally optimize parameters across portfolio mappings.

This guide mirrors the desktop Portfolio Backtesting workflow and follows the same API patterns as script optimization.

## Hard rules (for weak/"dumb" models)
- Use only `/api/portfolios/backtesting/*` endpoints for portfolio entities (do not mix with `/api/scripts/*`).
- When updating portfolio options, POST the **full** `options` object and keep exact casing returned by the server.
- Most endpoints return an envelope `{ success, message, data, timestamp }` - read payloads from `data`.
- Use `data.scripts[].name` for follow-up `/api/scripts/{name}/*` calls. Do not substitute portfolio `scriptId` into `/api/scripts/{name}`.
- Portfolio `scriptId` is only for nested portfolio routes such as `/api/portfolios/backtesting/{id}/scripts/{scriptId}/...`.
- `dataSourceName` is canonical; avoid guessing `sourceName` - use the exact `sourceName` from the script mapping/template.
- If API `message` contains escaped Unicode or mojibake, do not use it as the source of truth for logic. Prefer `success`, `data`, endpoint status, and stable typed fields.
- If a run returns `status=CompletedWithErrors`, always read `itemErrors[]` and treat it as a partial failure.
  - Parse `itemErrors[].message` to identify which script/mapping failed.
  - Retry failed mappings with corrected settings, or remove them if unfixable.
  - Do not report success without user confirmation of partial results.
- Default portfolio analysis to `/performance` and `/profit`. Treat `/trades` as an optional capability that must be confirmed on the current runtime, and do not assume a portfolio `/positions` route exists.
- For optimization, disable realtime updates on the script (`options.rtUpdates=false`) and use `SetOptimizationRange`, not `SetParam`.
- **Timeframe rule:** Portfolio `options.interval*` affects only portfolio backtests. It does **not** automatically update script lab-options, and Agents will still run on the script's `/api/scripts/{name}/lab-options` interval. Keep portfolio interval and script interval consistent, or clone scripts per timeframe.

## 1) Create or select a portfolio
- List portfolios:
  - `GET /api/portfolios/backtesting`
  - Response: `ApiResponse<List<...>>` (array is in `data`).
- Read portfolio details:
  - `GET /api/portfolios/backtesting/{id}`
  - Script name is in `data.scripts[].name` (alias: `data.scripts[].scriptName`).
  - `data.scripts[].scriptId` is the nested portfolio script id for `/api/portfolios/backtesting/{id}/scripts/{scriptId}/...`, not a substitute for `/api/scripts/{name}`.
- Create:
  - `POST /api/portfolios/backtesting`
  - body: `{ "name": "MyPortfolio" }`
- Clone:
  - `POST /api/portfolios/backtesting/{id}/clone`
- Rename or update options:
  - `PUT /api/portfolios/backtesting/{id}`

## 2) Configure portfolio options (common settings)
Update common options for the portfolio:
- deposit (`UseDeposit` + `Deposit`)
- interval (`UseInterval` + `Interval` + `IntervalBase`)
- date range (`UseDateFrom`/`UseDateTo` + `DateFrom`/`DateTo`)

### Capital accounting note (paired long/short on same instrument)
If you include the **same `securityId`** in both a long script and a short script (a paired setup), do **not** sum `initDeposit` for long+short when reasoning about required starting capital.

Assumption: positions on the same instrument are **netted** (mutually offset), so effective per-instrument capital is approximately:
- `effectiveCapital(securityId) = max(longInitDeposit, shortInitDeposit)`

Implications:
- When a user says "250 deposit per instrument" in a paired long/short portfolio, set both mappings to 250, but treat the per-instrument capital as about 250, not 500, for budgeting and DD normalization discussions.
- Portfolio-level `startDepo` reported by the API may still reflect the sum of mapping deposits; this is a UI/API artifact and should not override the netting assumption above when the user explicitly uses netted accounting.

Endpoint:
- `PUT /api/portfolios/backtesting/{id}`
  - body example:
```json
{
  "name": "MyPortfolio",
  "options": {
    "useDeposit": true,
    "deposit": 100000,
    "useInterval": true,
    "interval": 5,
    "intervalBase": "Minute",
    "useDateFrom": true,
    "dateFrom": "2023-01-01",
    "useDateTo": true,
    "dateTo": "2024-01-01"
  }
}
```

## 3) Add scripts and mappings
You can add a script with one or more mappings (securities).

Add script with mappings:
- `POST /api/portfolios/backtesting/{id}/scripts`
- body example:
```json
{
  "scriptName": "MyScript",
  "mappings": [
    { "dataSourceName": "TQBR", "securityId": "SBER", "sourceName": "Source" },
    { "dataSource": "TQBR", "securityId": "GAZP", "sourceName": "Source" }
  ]
}
```
- `dataSourceName` is canonical; `dataSource` is accepted as an alias.

Nested portfolio script routes use the portfolio child `scriptId`:
- `POST /api/portfolios/backtesting/{id}/scripts/{scriptId}/mappings`
- `PUT /api/portfolios/backtesting/{id}/scripts/{scriptId}/mappings/{mappingId}`
- `DELETE /api/portfolios/backtesting/{id}/scripts/{scriptId}/mappings/{mappingId}`
- `DELETE /api/portfolios/backtesting/{id}/scripts/{scriptId}`

Update mapping options example:
```json
{
  "include": true,
  "interval": "M5",
  "initDeposit": 50000,
  "parameterSetId": "{recordId}"
}
```

## 4) Manage parameter sets per mapping
Portfolio mappings point to a parameter set `recordId` (`OptimizationParameters.LastLoadedId`) stored in the script.

Typical flow:
1. Update script optimization parameters (`SetOptimizationRange`) using `/api/scripts/{name}/ops`.
2. Read the current parameter ids via `GET /api/scripts/{name}/parameters`.
3. Update the script parameter set with `POST /api/scripts/{name}/parameters`.
4. Apply the `recordId` to the mapping (`PUT` mapping with `parameterSetId`).

Note: if a block id has non-ASCII characters, send UTF-8 JSON (see `AGENTS-Optimization.md`).

## 5) Run portfolio backtest
Start a run:
- `POST /api/portfolios/backtesting/{id}/runs`

Poll status:
- `GET /api/portfolios/backtesting/runs/{jobId}`
  - status can be `CompletedWithErrors`; check `itemErrors[]` for per-item failures.
  - for diagnostics also fetch:
    - `GET /api/portfolios/backtesting/runs/{jobId}/warnings`
    - `GET /api/portfolios/backtesting/runs/{jobId}/logs`

Cancel:
- `POST /api/portfolios/backtesting/runs/{jobId}/cancel`

Delete job (optional cleanup):
- `DELETE /api/portfolios/backtesting/runs/{jobId}`

## 6) Fetch results
Performance summary:
- `GET /api/portfolios/backtesting/runs/{jobId}/performance`
  - Metrics are grouped in `data.groups[]`. Use `data.all` (preferred) or pick group `name == "All"`.
  - Group names such as `All`, `Long`, `Short`, and `Market` are observed labels. Do not assume their semantics are formally documented, additive, or stable across builds.

Trades (optional capability, paged):
- Confirm the current runtime supports `GET /api/portfolios/backtesting/runs/{jobId}/trades?skip=0&take=200` before relying on it in automation.
- If the route returns 404/501 on the current runtime, treat it as unsupported and fall back to `/performance` + `/profit` instead of retrying or guessing another route.
- When supported, the server clamps `take` to `1..1000`.
- When supported, loop while `skip < Total`; advance `skip += Returned`.
- When supported, if a page call fails (for example 408/500), retry the same `skip/take` with backoff; do not restart from `skip=0`.

Positions:
- Do not promise `GET /api/portfolios/backtesting/runs/{jobId}/positions` unless the current runtime explicitly supports it.

Profit charts:
- `GET /api/portfolios/backtesting/runs/{jobId}/profit`
- `GET /api/portfolios/backtesting/runs/{jobId}/profit-by-items`

Correlations:
- `GET /api/portfolios/backtesting/runs/{jobId}/correlations`

## 7) Optimization (per mapping)
Before optimization:
- disable realtime updates for the script via `POST /api/scripts/{name}/lab-options` (`options.rtUpdates=false`)

Start optimization for a mapping:
- `POST /api/portfolios/backtesting/{id}/optimizations`
- body example:
```json
{
  "scriptName": "MyScript",
  "mode": "Mapping",
  "mappingId": 123,
  "method": "BruteForce",
  "iterations": 1000,
  "keepTop": 500,
  "metrics": ["NetProfit", "MaxDrawdownPct", "ProfitFactor"]
}
```
- `mode` defaults to `"Mapping"` if omitted.

Status + results:
- `GET /api/portfolios/backtesting/optimizations?activeOnly=true|false&portfolioId={id?}&skip=0&take=100`
- `GET /api/portfolios/backtesting/optimizations/{jobId}`
- `GET /api/portfolios/backtesting/optimizations/{jobId}/results?metric=NetProfit&desc=true&skip=0&take=100`
- `POST /api/portfolios/backtesting/optimizations/{jobId}/cancel`

Apply best parameters:
- Use `row.parameters` to update script parameters via `POST /api/scripts/{name}/parameters`.
- Then update mapping `parameterSetId` if you want to persist the selection per mapping.

## 8) Optimization (common across mappings)
Common optimization applies a single parameter set across multiple mappings of the same script.

Start common optimization:
- `POST /api/portfolios/backtesting/{id}/optimizations`
- body example:
```json
{
  "scriptName": "MyScript",
  "mode": "Common",
  "mappingIds": [123, 124, 125],
  "method": "Random",
  "iterations": 500,
  "keepTop": 300,
  "metrics": ["NetProfit", "MaxDrawdownPct", "ProfitFactor"]
}
```

Status + results:
- `GET /api/portfolios/backtesting/optimizations/{jobId}`
- `GET /api/portfolios/backtesting/optimizations/{jobId}/results?metric=NetProfit&desc=true&skip=0&take=100`
- `POST /api/portfolios/backtesting/optimizations/{jobId}/cancel`

Apply best parameters:
- Use `row.parameters` to update script parameters via `POST /api/scripts/{name}/parameters`.
- Optionally update `parameterSetId` for each mapping if you want to store the selection per mapping.

## Gotchas
- Large trade lists can be huge; always page and filter.
- If the current runtime lacks portfolio `/trades`, do not treat that as a license to substitute a guessed `/positions` route.
- Only metrics tracked at job start can be queried.
- Optimization requires parameters to be stored via `SetOptimizationRange` (not `SetParam` constants).
- If search space is too large, use iterations or reduce the number of optimized parameters.
- For partial failures, `status=CompletedWithErrors` and `itemErrors[]` contain per-item diagnostics.
- Creating agents from a portfolio: do a timeframe alignment pass first (see `AGENTS-Agents.md`, "Timeframe alignment").

## Next step: create agents from a portfolio
After you have a stable portfolio configuration (scripts + mappings), you can create a trading agent per included mapping and group them under a folder named after the portfolio.

See:
- `AGENTS-Agents.md` ("Create: group of agents from a portfolio backtest")
