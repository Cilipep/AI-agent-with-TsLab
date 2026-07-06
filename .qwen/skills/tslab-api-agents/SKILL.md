---
name: tslab-api-agents
description: "Manage and analyze live TSLab agents via /api/agent-manager/* and /api/agents/*: create, start, stop, restart, and inspect runtime results."
---

# TSLab Web API: Agents

## Hard rules

- Do not perform mutating agent actions unless explicitly requested.
- Always resolve `dataSourceName` values from live API responses or mapping templates.
- `/api/agents/*` endpoints are only for live agent instances created through `/api/agent-manager/agents`.
- Do not use `/api/agents/{scriptName}/results`, `/api/agents/{scriptName}/detail-results`, or `/api/agents/{scriptName}/last-run` to analyze a server-side script. For script analysis use `/api/scripts/{name}/validate`, build, load, run, metrics-summary, messages, and logs.

## Typical flow

1. `GET /api/agent-manager/scripts/{scriptName}/mapping-template`
2. `POST /api/agent-manager/agents`
3. optional folder placement through the folder endpoints
4. start, stop, or restart only if the user asked for it

## Read endpoints

- `GET /api/agents/{agentName}/charts/info`
- `GET /api/agents/{agentName}/charts/data`
- `GET /api/agents/{agentName}/control-panes`
- `GET /api/agents/{agentName}/performance`
- `GET /api/agents/{agentName}/performance-chart`
- `GET /api/agents/{agentName}/positions`

## Related docs

- `AGENTS-Agents.md`
- `AGENTS-Trading.md`
- `AGENTS-CommandManager.md`
