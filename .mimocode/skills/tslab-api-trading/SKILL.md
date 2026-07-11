---
name: tslab-api-trading
description: "Work with TSLab realtime trading endpoints (/api/trading/*): list own orders/trades/positions and perform actions like close position or cancel orders. Use for live trading tables/actions."
---

# TSLab Web API: Realtime Trading

## Hard Rules

- Always use `/api/...` prefix and correct HTTP method; HTML means wrong route.
- Use exact `dataSource/account/securityId/portfolioId` from `GET /api/trading/own-positions` for actions; do not use display names or composite `id`.
- Use ISO-8601 timestamps (prefer `...Z`) for `from/to` filters.

## Minimal Workflow

- Inspect current positions:
  - `GET /api/trading/own-positions?take=500&skip=0&nonZeroOnly=true`
- Close a position (market):
  - `POST /api/trading/own-positions/close`
- Cancel orders for a position:
  - `POST /api/trading/own-positions/cancel-orders`

## Docs Pointer

- Full endpoint list + pitfalls: `AGENTS-Trading.md`
