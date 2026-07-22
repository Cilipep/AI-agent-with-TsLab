# AGENTS: Trading Agents (create, configure, trade, diagnose)

This is a practical, API-first guide for LLM/CLI agents that create and operate TSLab trading agents so they **actually trade** (create orders and get fills), not only "produce signals".

## 0) Terms (do not mix up)
- `agentId`: numeric agent id used by `agent-manager/*` endpoints.
- `commandManagerAgentId`: GUID returned by `/api/command-manager/commands[].agentId` (do not confuse with numeric `agentId`).
- `tradeName`: the agent "trading name". It is used as `{agentName}` in `GET /api/agents/{agentName}/*` (charts/performance/positions/logs). It is also the primary correlation key for own orders/trades (`tradeName` filter).
- `customName`: display name in Agent Manager UI.
- `folder`: an Agent Manager tree folder used for grouping and batch operations.

## Hard rules (for weak/"dumb" models)
- Never confuse numeric `agentId` with `commandManagerAgentId` (GUID).
- Always make `tradeName` unique and stable; use it as the join key for orders/trades/commands.
- For every `isTradable=true` source, set a valid `portfolioId` or the agent will not place real orders.
- When updating trade options, always include `defEntryApprove` and `defExitApprove` in the same request.
- **Timeframe rule:** Portfolio Backtesting interval does **not** override script interval for Agents. Agents run on the script's `/api/scripts/{name}/lab-options` interval. Before creating/restarting agents from a portfolio, align each involved script's lab-options interval to the portfolio interval (or clone scripts per timeframe).

## 1) Fast "why the agent does not trade" checklist
If an agent is "running" but you see no orders/trades:
1) Autotrading must be enabled (both):
   - `defEntryApprove=true` (auto-approve entries)
   - `defExitApprove=true` (auto-approve exits)
2) For every `isTradable=true` source mapping, `portfolioId` (trade account) must be set.
3) Exchange constraints must be satisfied: tick size, minimum quantity / minimum notional, available balance, instrument state.
4) Verify broker truth via "Own Orders / Own Trades" API (see section 7).
5) Verify the script is actually generating signals on the current regime (it can be correct to have zero trades in a straight downtrend if the entry logic requires a rebound / specific filter).

## 2) Create an agent from a script (single)
### 2.1 Get mapping template
`GET /api/agent-manager/scripts/{scriptName}/mapping-template`

Use the response to:
- enumerate `sources[]` (script inputs)
- identify which sources are tradable (`isTradable`)
- take defaults (`defaultDataSourceName`, `defaultSecurityId`, `defaultPortfolioId`)
- keep `records[]` if present (record-based source ranges)

### 2.2 Pick a trading account/portfolio for each data source
For each `dataSourceName` you trade on:
`GET /api/agent-manager/portfolios?dataSourceName=...`

Pick `portfolioId` (usually by `accountId` + `currency`).

### 2.3 Create agent
`POST /api/agent-manager/agents`

Minimal correct request:
```json
{
  "parentFolderId": 1,
  "scriptName": "MyScript",
  "customName": "MyScript BTCUSDT",
  "tradeName": "MyScript BTCUSDT",
  "limitType": "Automatically",
  "limit": 0,
  "advancedLogging": false,
  "sources": [
    {
      "name": "Source",
      "isTradable": true,
      "dataSourceName": "<DATA_SOURCE_NAME_FROM_/api/datasources>",
      "securityId": "BTCUSDT",
      "portfolioId": 123,
      "records": null
    }
  ]
}
```

Notes:
- `tradeName` must be unique. Use a suffix like `{securityId}` or `{mappingId}` to avoid collisions.
- If `isTradable=true` but `portfolioId=null`, the agent can still "run" and produce signals, but it will not be able to place real orders.
- `dataSourceName` must match exactly one of `GET /api/datasources` (do not guess/copy from examples).

## 3) Create a group of agents from a portfolio backtest (batch)
Goal: create one agent per `(script + enabled mapping instrument)` from Portfolio Backtesting and place them into a folder named after the portfolio.

### 3.1 Read the portfolio
- `GET /api/portfolios/backtesting`
- `GET /api/portfolios/backtesting/{id}`

Notes:
- Responses are `ApiResponse<...>` (portfolio payload is in `data`).
- Script name is in `data.scripts[].name` (alias: `data.scripts[].scriptName`).

Use `data.scripts[].mappings[]` and keep only `include=true`.

### 3.1.1 Timeframe alignment (critical; prevents "5M portfolio but 1M agents")
Problem:
- Portfolio Backtesting uses `portfolio.options.interval*` only for backtests.
- Agents use the script's lab options: `GET /api/scripts/{scriptName}/lab-options`.
- If a portfolio is configured to 5 minutes but scripts stay at 1 minute, agents will trade 1-minute bars (wrong).

Fix (recommended before creating agents):
1) Read portfolio interval:
   - `GET /api/portfolios/backtesting/{id}` -> `options.intervalBase` + `options.intervalValue` (or `options.interval` string like `5M`)
2) For each unique script name used in that portfolio (`data.scripts[].name` / `data.scripts[].scriptName`):
   - `GET /api/scripts/{scriptName}/lab-options`
   - set `intervalBase` + `interval` to match the portfolio
   - `POST /api/scripts/{scriptName}/lab-options` with `{ "options": <full options> }`
3) Restart existing agents for those scripts (so they pick up the new lab-options):
   - `POST /api/agent-manager/agents/restart` with `{ "agentIds": [...] }`

Rule of thumb:
- Do not mix multiple timeframes by reusing the same script name. If you need both 1M and 5M, clone the script and keep one timeframe per script.

### 3.2 Create or resolve a target folder
1) Create:
   - `POST /api/agent-manager/folders` (with `parentFolderId` and `name`)
2) Resolve its `itemId`:
   - `GET /api/agent-manager/tree`

### 3.3 Create one agent per included mapping
For each mapping row `(scriptName, sourceName, dataSourceName, securityId)`:
1) `GET /api/agent-manager/scripts/{scriptName}/mapping-template`
2) Build `sources[]`:
   - for the selected `sourceName`: set `dataSourceName/securityId` from the portfolio mapping
   - for all other sources: keep template defaults
   - for every tradable source: set a valid `portfolioId` (trade account) for that `dataSourceName`
3) `POST /api/agent-manager/agents` into the folder

Recommended agent naming:
- `{scriptName} {sourceName} {securityId}`

## 4) Start/Stop/Restart (including batch)
Batch operations use `agentIds[]`:
- start: `POST /api/agent-manager/agents/start` -> `{ "agentIds": [1,2,3] }`
- stop: `POST /api/agent-manager/agents/stop`
- restart: `POST /api/agent-manager/agents/restart`
- forget errors: `POST /api/agent-manager/agents/forget-errors`

## 4.1 TSCloud translation (separate from entry/exit approvals)
Some deployments use TSCloud to translate agent activity to an external environment. This is controlled by:
- `POST /api/agent-manager/agents/translation` -> `{ "agentId": 123, "enabled": true|false }`

Notes:
- This is not a replacement for `defEntryApprove/defExitApprove` (those flags control whether entries/exits are auto-approved).
- If you are not using TSCloud translation, leave it disabled to avoid confusion.

Folder-as-a-unit workflow:
1) `GET /api/agent-manager/tree`
2) recursively collect all `agentId` under a folder
3) call start/stop/restart with that list

## 5) Agent configuration (what actually affects trading)
### 5.1 Common settings
- `GET /api/agent-manager/agents/{agentId}/settings`
- `POST /api/agent-manager/agents/{agentId}/settings`

Fields:
- `customName`, `tradeName`
- `limitType` (`Automatically|LimitInLots|LimitInMoney|LimitInPercent`) and `limit`
- `advancedLogging`
- `comment`

### 5.2 Mappings
- `GET /api/agent-manager/agents/{agentId}/mappings`
- `POST /api/agent-manager/agents/{agentId}/mappings`

Rules:
- for `isTradable=true` sources you must set `dataSourceName`, `securityId`, `portfolioId`
- `records[]` (if used) impacts what history/ranges the source provides; this can affect when/if signals appear

### 5.3 Parameters
- `GET /api/agent-manager/agents/{agentId}/parameters`
- `POST /api/agent-manager/agents/{agentId}/parameters`
  - body: `{ "parameters": [{ "id": "...", "value": "..." }] }`

### 5.4 Trade options (RealtimeScriptOptions)
- `GET /api/agent-manager/agents/{agentId}/trade-options`
- `POST /api/agent-manager/agents/{agentId}/trade-options`
- `GET /api/agent-manager/trade-options/metadata` (discover available keys, categories, and value types)

Update semantics (safe rule):
- Behavior differs across builds (merge vs replace). To be safe, always `GET` current trade options and `POST` a **full** `options` object.
- Always include `defEntryApprove` and `defExitApprove` even if you are changing a different field.

#### 5.4.1 Autotrading prerequisite: auto-approve entry & exit
To make an agent trade **automatically** (without manual confirmations in the order/command workflow), enable both:
- `defEntryApprove=true` - auto-approve entries
- `defExitApprove=true` - auto-approve exits

Important:
- If you only want to change one field, do: `GET trade-options` -> modify -> `POST` full `options`.

If any of them is false:
- the script can still emit entry/exit signals
- but order execution can be routed into a manual-control path and wait for a user action
- typical symptom: signals exist, but "Own Trades" stays empty; "Own Orders" may show items waiting/being blocked by control flow
- manual actions are exposed via `/api/command-manager/*` (see `AGENTS-CommandManager.md`)

Example:
```json
POST /api/agent-manager/agents/{agentId}/trade-options
{ "options": { "defEntryApprove": true, "defExitApprove": true } }
```

#### 5.4.2 Order execution mental model (diagram)
The real engine has many branches, but this simplified model is enough for API-driven operations:
```mermaid
flowchart TD
  A[Signal from script] --> B{Needs manual approval?}
  B -- yes --> C[Wait for manual action\n(order/command workflow)]
  B -- no --> D[Create order request]
  D --> E[Send to provider/exchange]
  E --> F{Order status}
  F -- Active/Pending --> G[Wait for execution\n(can be partial)]
  F -- Executed --> H[Update position state]
  F -- Rejected/Failed --> I[Error + special situation]
  G --> H
  G --> J{Timed out?}
  J -- yes --> I
  J -- no --> G
```

Trade options that influence key branches:
- `defEntryApprove` / `defExitApprove`: direct execution vs manual-control path.
- `slippage` / `slippagePct`: affects effective prices and can change "executable vs rejected/stuck".
- `byMarketAsLimt`: represent "market" as limit with a fixed price (venue-dependent).
- `orderExpirationDays`: how long orders can remain valid/kept before expiry logic.
- `waitExecutionEntryBars` / `waitExecutionExitBars`: how long (in bars) the system waits for an *active but unfilled* order before treating it as timed out.
- `autoEntryBars` / `autoCloseBars`: fallback behavior ("auto-open/auto-close") to avoid being stuck when a limit order is not filling.
- `takeProfitNoSlippage` / `openPositionNoSlippage`: disables slippage for these paths.
- `invalidStopsByMarket`: fallback behavior for problematic stop orders.

#### 5.4.3 Order lifetime: timeouts, expiry, and auto-open/auto-close
Think of "order lifetime" as three different mechanisms:
1) **Execution wait timeout (bars)**: if an order becomes active but does not fill, the engine waits `waitExecutionEntryBars` / `waitExecutionExitBars` bars. After that it treats the situation as "timed out".
2) **Expiry (days)**: `orderExpirationDays` is a coarse "how long to keep orders around" control (especially relevant for pending/working orders).
3) **Fallback behavior**: `autoEntryBars` / `autoCloseBars` can trigger a replacement/alternative execution path to avoid a stuck position lifecycle.

How to tune without causing surprises:
- Keep `waitExecution*Bars` and `auto*Bars` consistent. If fallback is enabled, ensure you understand whether fallback happens before/after timeout for your use-case.
- On illiquid instruments, increase wait time and/or allow fallback.
- For venues with strict market-order behavior, consider `byMarketAsLimt`.

#### 5.4.4 Typical order statuses (interpretation)
You will generally see statuses like:
- `Pending`: created but not fully active yet
- `Active`: working on exchange / can still fill
- `Executed`: fully filled
- `Canceled`: canceled
- `Rejected`: rejected by venue/provider
- `Failed`: internal/provider error

## 6) Partial fills and "linked" orders
### 6.1 Partial fill
In own orders, partial fill typically looks like:
- `quantity > restQuantity > 0`
- status often remains `Active` until the remainder is filled/canceled/expired

Recommended diagnostic steps:
1) `GET /api/trading/own-orders?activeOnly=true&tradeName=...`
2) find the order(s) where `restQuantity > 0`
3) `GET /api/trading/own-trades?from=...&to=...&tradeName=...` and correlate by `orderId`
4) decide policy: wait vs cancel remainder vs adjust strategy (depends on risk model)

### 6.2 Linked orders (entry + protective stop/take)
Entry and protective orders can have different lifetimes and failure modes. During reconnects or manual actions you can end up with:
- an entry filled but protective order missing
- a protective order left behind after position is already closed

Rule: always verify broker truth via own orders/trades before taking "automation" actions like restart.

## 7) "Own Orders" and "Own Trades" (broker truth) + API mapping
These endpoints are the primary way to validate that the exchange/provider actually has your orders and fills.

### 7.1 Own Orders
`GET /api/trading/own-orders`

Key query params:
- `activeOnly=true`
- `provider`, `account`, `security`, `tradeName`, `status`
- paging: `skip`, `take`

Suggested workflow:
1) Start with `activeOnly=true` to see what is currently working.
2) Filter by `tradeName` to isolate a single agent or a group.
3) Inspect:
   - pricing: `price`, `stopPrice`, `takePrice`
   - fill state: `quantity`, `restQuantity`
   - lifetime: `firstDate`, `lastDate`, `endDate`
   - execution flags: `isActive`, `isExecuted`, `status`

Filter helpers:
`GET /api/trading/own-orders/options`

### 7.2 Own Trades
`GET /api/trading/own-trades`

Key query params:
- `from`, `to` (choose a time window)
- `provider`, `account`, `security`, `tradeName`
- paging: `skip`, `take`

Important fields:
- `orderId`: correlate to `own-orders.id`
- `isFictitious`: non-market / internal/technical entry (do not treat as a real exchange fill)
- `isAlignPosition`: alignment trade (used to reconcile state)

Filter helpers:
`GET /api/trading/own-trades/options`

### 7.3 Correlation rules: agent <-> own orders/trades
Use `tradeName` as the main join key:
- the agent's `tradeName` should appear in `own-orders.tradeName` and `own-trades.tradeName`
- some DTOs also include `agentName`, but `tradeName` is the reliable grouping handle

## 8) Virtual position (what it is and how to handle it)
A "virtual position" is a divergence between:
- what TSLab *thinks* the position state is (agent positions / internal lifecycle)
- what the exchange/provider actually has (own orders/trades / broker positions)

### 8.1 Common causes
- agent restart after downtime/reconnect (missed fills/exits)
- manual orders/trades outside the agent
- order rejected/failed after the script already advanced its internal logic
- autotrading flags disabled (`defEntryApprove/defExitApprove=false`): signals were emitted but never executed
- exchange constraints causing systematic rejects

### 8.2 Limiting how long a virtual position is tolerated
`maxBarsForSignal` (trade option) limits how long (in bars) the system tolerates a virtual position context before surfacing it as a problem requiring intervention.

Example:
```json
POST /api/agent-manager/agents/{agentId}/trade-options
{ "options": { "maxBarsForSignal": 50 } }
```

### 8.3 How to diagnose
1) Agent view:
   - `GET /api/agents/{agentName}/positions`
2) Broker truth:
   - `GET /api/trading/own-orders?activeOnly=true&tradeName=...`
   - `GET /api/trading/own-trades?from=...&to=...&tradeName=...`
3) If you see `isFictitious=true` or `isAlignPosition=true`, treat those records as internal/alignment artifacts, not real exchange fills.

### 8.4 Safe remediation algorithm
1) Stop the agent (batch stop via `agentId`).
2) Cancel/close at the exchange/provider side first (ensure no live working orders remain).
3) Reconcile what the exchange position is vs what TSLab thinks.
4) Restart the agent only after state is aligned.
5) If it keeps happening, fix strategy logic: enforce "one position-changing action per bar", reduce conflicting signals, validate order sizing/rounding.

## 9) Messages and special situations: operational response
Treat trading messages and special situations as actionable signals about:
- rejects/timeouts
- approvals/manual-control blocks
- state divergence (virtual position)
- conflicting actions on the same bar

Universal response algorithm:
1) Do not "restart by reflex".
2) Verify broker truth with `own-orders` / `own-trades`.
3) Only then: tune trade options, cancel remainders, restart, or realign position.

### 9.1 Common scenarios and concrete actions (API-first)
1) TSLab positions are empty but the agent "acts like it has a position" (or vice versa).
   - typical cause: manual actions or state divergence.
   - safe approach: stop agent -> change `tradeName` (resets grouping/history) -> start again.
     - stop: `POST /api/agent-manager/agents/stop`
     - rename: `POST /api/agent-manager/agents/{agentId}/settings` (update `tradeName` and optionally `customName`)
2) Double-exit / conflicting exits on the same bar.
   - effect: automatic order processing can stall for safety.
   - options:
     - stop -> manually align broker state -> change `tradeName` -> start again
     - or clear errors for a batch:
       - `POST /api/agent-manager/agents/forget-errors`
3) Orders become active but do not fill (liquidity).
   - tune `waitExecution*Bars` + `auto*Bars`, and consider increasing `slippage/slippagePct`.

### 9.2 Slippage as a root cause of "not executing"
If slippage is too small:
- an order can "touch" the price but not fill (especially with low liquidity/partial fills)
- the system can keep it active until timeout and then cancel/mark as timed out

Recommendations:
- increase `slippage` / `slippagePct`
- tune `waitExecution*Bars` together with `auto*Bars`
- for problematic stop execution paths consider `invalidStopsByMarket=true`
