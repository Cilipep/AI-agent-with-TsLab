# Agent Instructions: Command Manager (Realtime Commands)

This document describes how to work with realtime "commands" (manual trade actions) via Web API.

Commands are created by the realtime engine when it needs an explicit action (or an alternative execution path) to proceed, for example:
- manual approval is required (auto-approve is disabled)
- a special situation occurs (timeout, stop/take-profit edge case, etc.)

If you are building an automation agent, treat Command Manager as the "manual control queue" for live trading.

## 0) Important IDs
- `commandId` (GUID): unique command identifier used for execution.
- `agentId` (GUID): realtime manager identifier for the command. This is **not** the numeric `agentId` used by `/api/agent-manager/*`.
- `tradeName` (string): the best correlation key between commands and agent activity (also used by Own Orders/Own Trades filters).

## Hard rules (for weak/"dumb" models)
- Execute a command **only once** and only when `isExecuting=false` and `isExecuted=false`.
- Use `{ "byMarket": true }` only when `canExecuteByMarket=true`.
- Always filter by `tradeName` to avoid executing actions for the wrong agent.

## 1) API endpoints
List commands:
- `GET /api/command-manager/commands`

Execute a command:
- `POST /api/command-manager/commands/{commandId}/execute`
  - body is optional:
    - `{ "byMarket": true }` (execute using "by market" fallback if supported)
    - `{ "byMarket": false }` or empty body (normal execute)

Auth:
- All endpoints are protected (`Authorization: Bearer <token>`), unless your server is configured to bypass auth for trusted clients.

## 2) Command DTO fields (what to look at)
From `GET /api/command-manager/commands` you will get a list of commands with fields like:
- identity/routing: `commandId`, `agentId`, `tradeName`, `provider`, `account`, `security`
- classification: `isEntry`, `isStop`, `signal`, `comment`, `notes`
- state: `isApproved`, `isExecuted`, `isExecuting`
- sizing/price: `price`, `priceStr`, `lots`, `quantity`
- capability: `canExecuteByMarket`

Operational interpretation:
- `isExecuting=true`: the command is currently being processed; do not try to execute it again.
- `isExecuted=true`: command is finished; you may still see it until the engine removes it.
- `isApproved=false`: usually indicates that auto-approval is disabled for the relevant path (entry/exit), or an approval-like step is required.

## 3) Execute semantics and status codes
Normal execute:
- `POST /api/command-manager/commands/{commandId}/execute`
  - The server rejects if already executed/executing:
    - `409 Conflict` with "Command already executed or executing"

Execute "by market":
- `POST /api/command-manager/commands/{commandId}/execute` with `{ "byMarket": true }`
  - Allowed only when `canExecuteByMarket=true`:
    - otherwise `400 Bad Request` with "Command does not support 'execute by market'"

Common errors:
- `404 Not Found` if the command does not exist (expired/removed while you were looking at the list).

## 4) When you should see commands (and how to prevent it)
If you want an agent to trade fully automatically, enable both options on the agent:
- `defEntryApprove=true`
- `defExitApprove=true`

See `AGENTS-Agents.md` (Trade options / RealtimeScriptOptions) for how to configure these flags via `/api/agent-manager/agents/{agentId}/trade-options`.

If one of these flags is false, the engine can still produce signals, but the execution flow may require a manual action and a command can appear in this queue.

## 5) Suggested automation loop (LLM/CLI)
1) Poll:
   - `GET /api/command-manager/commands`
   - Optionally, use SignalR `CommandManagerChanged` (UI uses it to avoid polling). For CLI automation, polling every ~1s is usually enough.
2) Filter:
   - by `tradeName` (preferred) and/or by `provider/account/security` if you manage multiple agents.
3) Decide execution mode:
   - If `canExecuteByMarket=true`, you may choose `{ "byMarket": true }` for urgent situations (e.g., stop/take-profit that must be executed immediately, or a stuck lifecycle).
   - Otherwise execute normally.
4) Execute:
   - `POST /api/command-manager/commands/{commandId}/execute`
5) Verify exchange truth:
   - `GET /api/trading/own-orders?activeOnly=true&tradeName=...`
   - `GET /api/trading/own-trades?from=...&to=...&tradeName=...`
6) If you see repeated timeouts:
   - check agent trade options such as `waitExecutionEntryBars`, `waitExecutionExitBars`, `autoEntryBars`, `autoCloseBars`, `orderExpirationDays`, slippage settings
   - consider whether `StopIfTimeout` is enabled (it can stop the agent on a timeout)

## 6) Safety notes
- Do not blindly execute everything. A command can represent an entry, an exit, a stop, or a special corrective action.
- If you run automation for live trading, always implement a risk gate:
  - max position size, max daily loss, max number of executions per time window
  - "dry-run" mode where you only list commands and explain what you would do
