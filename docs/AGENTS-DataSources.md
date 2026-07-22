# Agent Instructions: Data Sources (Providers)

A **data source** (provider) represents a connection to an external broker or data feed.

## Hard rules (for weak/"dumb" models)

- Always resolve provider names from `GET /api/datasources`; do not guess or silently switch providers.
- Do not read settings/schedule, connect/disconnect, reload, reschedule, switch providers, or modify settings unless the user explicitly asked for live provider administration.
- Offline/cached/backtesting tasks explicitly are not live provider administration. `CompletedNoData`, "No instrument selected", `records=[]`, `isConnected=false`, `instrumentsLoaded=0`, or empty logs/messages do not authorize provider settings/schedule reads or provider mutation; repair the current script's mapping, graph/source wiring, lab-options/date window, or report a data-readiness blocker.
- Some data sources do not support connect/disconnect; expect `400` and handle it gracefully.

## Key concepts

- **Name**: unique identifier used in all API paths (case-insensitive match).
- **dataSourceName rule**: always take the value from `GET /api/datasources` or mapping templates; do not guess/copy from examples.
  - If the user explicitly tells you the provider name (for example, "use provider Bybit"), treat that as a requirement: verify it exists in `/api/datasources` and use it. Do **not** silently switch to a different provider (Spot/Inverse/etc.).
- **ConnectionState**: `Disconnected`, `Connecting`, `Connected`, `Disconnecting`, etc. Check `isConnected` / `isReady` for quick status.
- **SupportsConnection**: some data sources do not support connect/disconnect; the API returns 400 if you try.
- **Settings**: provider-specific configuration. Secret fields never expose their value; use `hasValue` to check if set.
- **Schedule**: optional weekly auto-connect/disconnect timetable. Each day has `isEnabled`, `start` ("HH:mm"), `stop` ("HH:mm"). Overnight intervals (for example, 23:00-07:00) are supported.

## Endpoints

1) List all data sources:
- `GET /api/datasources`

1a) Provider creation catalog (human provider administration only):
- `GET /api/datasources/provider-catalog`
  - Returns historical/offline templates even when the cloud user is not logged in or is offline.
  - Contract/new-contract sections are unavailable unless the current cloud user is online.
- `GET /api/datasources/provider-tariffs?brokerId=...`
  - Reads cloud tariffs for creating a new provider contract.

1b) Create provider contract/provider (human provider administration only):
- `POST /api/datasources/contracts`
- `POST /api/datasources/draft-settings`
- `POST /api/datasources`
- Contract creation and provider creation require header `X-TSLab-Provider-Admin-Confirm: true`.
- These routes are for explicit user-driven provider setup. They are not a script repair, no-data, backtesting, offline/cache proof, or continuation workflow.
- Do not create a provider, contract, or draft settings object because a script has empty bars, missing records, disconnected status, or incomplete mappings.

2) Get detailed info:
- `GET /api/datasources/{name}/info`

3) Get live status:
- `GET /api/datasources/{name}/status`

4) Connect / disconnect (provider administration only):
- `POST /api/datasources/{name}/connect`
- Provider-admin mutation routes require explicit confirmation with header `X-TSLab-Provider-Admin-Confirm: true`. Do not add that confirmation for offline/cached/backtesting script proof; `?confirmProviderAdmin=true` is not sufficient for automation clients.
  - Optional body: `{ "timeoutSeconds": 30, "forceReconnect": false, "waitForCompletion": false }`
  - By default the API does not wait for full connection; poll `/status` afterwards.
- `POST /api/datasources/{name}/disconnect`
  - Optional body: `{ "forceDisconnect": false, "waitForOperationsComplete": true }`

Connection etiquette (agent rule):
- Do **not** auto-connect providers just because you need history/cached data. For offline, cached, local, or backtesting prompts, never read provider `settings`/`schedule`, connect, disconnect, reload, reschedule, wait-loop, switch providers, or add `X-TSLab-Provider-Admin-Confirm` unless the user explicitly asks for live provider access. At most one `GET /api/datasources/{name}/status` is allowed as a diagnostic; `CompletedNoData`, disconnected status, empty `records[]`, `isConnected=false`, empty messages/logs, and `instrumentsLoaded=0` are diagnostics, not permission to mutate provider state.

5) Read settings:
- `GET /api/datasources/{name}/settings`

6) Update settings:
- `PUT /api/datasources/{name}/settings`
- Requires header `X-TSLab-Provider-Admin-Confirm: true`.
  - Body: `{ "values": { "PropertyName": value, ... }, "reconnectIfConnected": false }`
  - Rules: `null` value = "do not change"; empty string for a secret field = "do not change"; unknown/read-only fields are silently skipped.

7) Read schedule:
- `GET /api/datasources/{name}/schedule`

8) Update schedule (provider administration only):
- `PUT /api/datasources/{name}/schedule`
- Requires header `X-TSLab-Provider-Admin-Confirm: true`.
  - Body: `{ "schedule": { "isEnabled": true, "days": [ { "dayOfWeekIndex": 0, "isEnabled": true, "start": "09:00", "stop": "23:50" }, ... ] } }`
  - If the schedule says "should be connected now", the server attempts to connect immediately.

9) Toggle schedule on/off (provider administration only):
- `PUT /api/datasources/{name}/schedule/enabled`
- Requires header `X-TSLab-Provider-Admin-Confirm: true`.
  - Body: `{ "isEnabled": true }`

## Typical provider-admin workflow

```text
# Use this only when the user explicitly asked to administer a live provider.
# Do not use this workflow to fix offline/cached/backtesting script proof.

# 1. List providers and find the one you need
GET /api/datasources

# 2. Check/update settings (e.g. set API key)
GET  /api/datasources/MyBroker/settings
PUT  /api/datasources/MyBroker/settings
     { "values": { "ApiKey": "xxx", "ServerUrl": "prod.broker.com" }, "reconnectIfConnected": false }

# 3. Connect
POST /api/datasources/MyBroker/connect

# 4. Poll status until isConnected=true and isReady=true
GET  /api/datasources/MyBroker/status

# 5. (Optional) Set up a schedule
PUT  /api/datasources/MyBroker/schedule
     { "schedule": { "isEnabled": true, "days": [
         { "dayOfWeekIndex": 0, "isEnabled": true, "start": "09:00", "stop": "23:50" },
         { "dayOfWeekIndex": 1, "isEnabled": true, "start": "09:00", "stop": "23:50" }
     ] } }
```

## Offline/cache script proof workflow

```text
# If the user asked for offline, cached, local, or backtesting data:
# - keep the requested provider/security/timeframe on the current artifact;
# - do not read provider settings/schedule, connect, disconnect, reload, reschedule, switch providers, add the provider-admin header, or wait-loop;
# - use at most one GET /api/datasources/{name}/status diagnostic, then return to current-script repair;
# - do not treat records[], instrumentsCount=0, instrumentsLoaded=0, or isConnected=false as permission to mutate provider state;
# - inspect mappings, authoring-quality, ui/explain, messages/logs, and lab-options on the same artifact;
# - rerun after graph/mapping/lab-options repair;
# - report a data-readiness blocker only after a structurally clean rerun still proves no usable bars.
```
