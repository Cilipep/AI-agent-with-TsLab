# Agent Instructions: Realtime Trading (Orders / Trades / Positions)

This document covers "desktop-like" realtime trading tables and actions exposed via Web API:
- own orders
- own trades
- current positions/balances
- actions: close position / cancel orders

Base URL:
- API: `http://localhost:5000/api`

Auth:
- Production typically requires `Authorization: Bearer <token>` (see `AGENTS-Auth.md`).

Response shape (important):
- Most endpoints return `ApiResponse<T>`.
- The actual payload is usually inside `data` (e.g. `(Invoke-RestMethod ...).data`).

## Hard rules (for weak/"dumb" models)
- Always use `/api/...` prefix and correct HTTP method; HTML response means wrong route.
- Use the exact `dataSource/account/securityId/portfolioId` values from `GET /api/trading/own-positions`; never use display names or the composite `id`.
- Use ISO-8601 timestamps with `Z` for `from/to` filters.

## 1) Own Orders

List (paged):
- `GET /api/trading/own-orders?take=200&skip=0&activeOnly=false&provider=...&account=...&security=...&tradeName=...&status=...`

Filter options (for dropdowns):
- `GET /api/trading/own-orders/options`

Notes:
- `provider` matches either provider visual name or data source name (server checks both).
- `account` matches account id or account name.
- `security` matches security name or security id.
- `status` must be a server `OrderStatus` enum name (case-insensitive).

## 2) Own Trades

List (paged, time window):
- `GET /api/trading/own-trades?from=2026-01-01T00:00:00Z&to=2026-01-31T00:00:00Z&take=500&skip=0&provider=...&account=...&security=...&tradeName=...`

Filter options (time-window aware):
- `GET /api/trading/own-trades/options?from=...&to=...`

Notes:
- Use ISO-8601 timestamps; `...Z` (UTC) is recommended for portability.
- If `from > to`, the server swaps them.
- **PowerShell + query strings (OpenClaw exec):** when calling this endpoint from `powershell -NoProfile -Command ...`, an unescaped `&` in the URL can break parsing (treated like a call operator/statement separator).
  - Prefer a `.ps1` file + `powershell -File ...`.
  - Or build the URL without a literal `&`, e.g. `$amp=[char]38` and concatenate.
  - Also avoid assigning to `$pid` (reserved/readonly in some environments); use `$procId` etc.

## 3) Own Positions (current balances)

List (paged):
- `GET /api/trading/own-positions?take=500&skip=0&nonZeroOnly=true&includeMoney=false&provider=...&account=...&security=...&portfolio=...&tradePlace=...`

Filter options:
- `GET /api/trading/own-positions/options`

Key fields:
- Each returned position has:
  - `dataSource` (internal name, used as action key)
  - `account` (account id, used as action key)
  - `securityId` (used as action key)
  - `portfolioId` (used as action key)
- `id` is a convenience composite key: `"{dataSource}|{account}|{securityId}|{portfolioId}"`.
  - API actions below do **not** accept `id` directly; always send the 4 key fields.

Notes:
- `nonZeroOnly=true` filters by `RealRest != 0` (server uses `DoubleUtil.IsZero`).
- `includeMoney=false` excludes money balances (money positions cannot be closed).

## 4) Commands (close position / cancel orders)

These actions are the Web API equivalents of the desktop toolbar/context menu actions in Positions window.

### 4.1 Close position (market order)

Endpoint:
- `POST /api/trading/own-positions/close`

Body:
- required keys: `dataSource`, `account`, `securityId`, `portfolioId`
- optional:
  - `cancelOrdersFirst` (default `true`) - cancels active orders for this instrument before sending a market close
  - `cancelConditionalOrders` (default `false`) - also cancels conditional orders (if provider supports it)
  - `tradeName`, `signal`, `note` - stored in the submitted order comment (if supported by provider)

Behavior notes:
- If position size is 0 and there are no active orders, the server returns `400`.
- If trading is disabled for the instrument, the server returns `409`.

Example (`curl.exe` + JSON file):
- `curl.exe -X POST "http://localhost:5000/api/trading/own-positions/close" -H "Content-Type: application/json" -H "Authorization: Bearer %ACCESS_TOKEN%" --data-binary "@close.json"`

`close.json`:
```json
{
  "dataSource": "Tinkoff2",
  "account": "ACC-1",
  "securityId": "SBER",
  "portfolioId": 42,
  "cancelOrdersFirst": true,
  "cancelConditionalOrders": false,
  "note": "manual close via api"
}
```

### 4.2 Cancel orders for a position

Endpoint:
- `POST /api/trading/own-positions/cancel-orders`

Body:
- required keys: `dataSource`, `account`, `securityId`, `portfolioId`
- optional: `includeConditional` (default `false`)

Example (`curl.exe` + JSON file):
- `curl.exe -X POST "http://localhost:5000/api/trading/own-positions/cancel-orders" -H "Content-Type: application/json" -H "Authorization: Bearer %ACCESS_TOKEN%" --data-binary "@cancel.json"`

`cancel.json`:
```json
{
  "dataSource": "Tinkoff2",
  "account": "ACC-1",
  "securityId": "SBER",
  "portfolioId": 42,
  "includeConditional": false
}
```

## 5) Common pitfalls

- Hitting the SPA fallback (HTML) instead of API:
  - verify you use `/api/...` prefix and correct method (`GET` vs `POST`).
- `dataSource` must be the internal data source name (not the UI display name):
  - take it from `GET /api/trading/own-positions` response `data.items[].dataSource`.
- Key mismatch for actions:
  - Always send the exact `dataSource/account/securityId/portfolioId` from the list response.
