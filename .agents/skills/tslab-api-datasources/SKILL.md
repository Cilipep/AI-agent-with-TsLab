---
name: tslab-api-datasources
description: "Inspect or configure TSLab data sources via /api/datasources: list, info, settings, connect, disconnect, and schedules."
---

# TSLab Web API: Data Sources

## Hard rules

- Always resolve provider names from `GET /api/datasources`; do not guess or silently switch providers.
- Do not connect, disconnect, reload, reschedule, switch providers, or modify settings unless live provider administration was explicitly requested.
- Offline/cached/backtesting prompts explicitly do not request live provider mutation. For those tasks, `CompletedNoData`, "No instrument selected", `isConnected=false`, `records=[]`, empty logs/messages, or `instrumentsLoaded=0` is diagnostic only; return to the current script's mapping/graph/lab-options repair and rerun instead of connecting, disconnecting, rescheduling, reloading, waiting, or switching providers.
- Some data sources do not support connect or disconnect; expect `400` and handle it gracefully.

## Key endpoints

- `GET /api/datasources`
- `GET /api/datasources/provider-catalog`
- `GET /api/datasources/provider-tariffs?brokerId=...`
- `POST /api/datasources/contracts`
- `POST /api/datasources/draft-settings`
- `POST /api/datasources`
- `GET /api/datasources/{name}/info`
- `GET /api/datasources/{name}/status`
- `GET /api/datasources/{name}/settings`
- `PUT /api/datasources/{name}/settings`
- `POST /api/datasources/{name}/connect`
- `POST /api/datasources/{name}/disconnect`
- `GET /api/datasources/{name}/schedule`
- `PUT /api/datasources/{name}/schedule`
- `PUT /api/datasources/{name}/schedule/enabled`

## Provider-admin confirmation

- Mutating provider-admin routes require explicit confirmation through header `X-TSLab-Provider-Admin-Confirm: true`.
- Provider contract/provider creation routes are human provider-admin setup routes. They are not a script repair, no-data, backtesting, offline/cache proof, or continuation workflow.
- Do not use `?confirmProviderAdmin=true`; automation clients must send the header, and the query flag is intentionally not enough.
- Do not add that confirmation for offline/cached/backtesting script proof. If the API returns `ProviderAdminConfirmationRequired`, go back to the current script's mappings, graph/source wiring, lab-options/date window, messages/logs, and rerun proof.

## Notes

- Do not auto-connect a provider just because you need cached history or a run returned `CompletedNoData`.
- Do not report "no cached history" from datasource status alone. Require a same-artifact run/messages/logs/lab-options proof after graph/source repair.
- If the workflow truly requires a live connection, ask or report that explicitly.
- Detailed field notes live in `AGENTS-DataSources.md`.
