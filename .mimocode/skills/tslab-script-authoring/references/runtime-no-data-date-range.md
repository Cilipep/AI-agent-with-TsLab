# Runtime, No Data, and Date Range

- For offline/cached/backtesting prompts, never call datasource `settings`, `schedule`, unfiltered `GET /api/datasources`, `connect`, `disconnect`, or `reload`, and never add `X-TSLab-Provider-Admin-Confirm`.
- `CompletedNoData`, `No instrument selected`, `isConnected=false`, empty logs/messages, `records=[]`, or `instrumentsLoaded=0` is diagnostic only until the same artifact's mapping, graph, lab-options/date window, messages/logs, and rerun proof are clean.
- Use at most one datasource readiness check for the already mapped/requested datasource. Do not switch providers and do not switch to `test`/`text` after a mapped provider returns `CompletedNoData`.
- `instrument-source` always persists datasource/security mapping. If the body also includes `interval` or `timeframe`, reread `GET /api/scripts/{name}/lab-options` to prove the base interval.
- `securityQuery` belongs to `GET /api/agent-manager/securities`, not to `POST /api/scripts/{name}/instrument-source`.
- Do not display-normalize exchange ids before `instrument-source`; keep the prompt's exact `securityId`.
- For date windows, prove the active range with `UseDateFrom`/`DateFrom` and `UseDateTo`/`DateTo`. `DateReload`, `useDateReload`, and `maxDays` are reload settings, not selected historical range proof.
- Never read, probe, or write `/tmp/lab-options.json`. Write `./tmp/lab-options.json`, post a short patch when possible, reread lab-options, rerun, then only report a data-readiness blocker after current-graph repair is exhausted.
- offline/cached/backtesting responses never point to provider-admin mutation. Do not change the requested interval/timeframe to make a run faster.
- Do not switch to `test`/`text` after a mapped provider returns `CompletedNoData` or `No instrument selected`.
- do not change the requested interval/timeframe.
- do not create or mutate `agent-manager/agents`.
- Do not use short client-side HTTP timeouts during build/load/run or data-loading proof.
- do not end with `I will fix...`; the next action is the same-artifact repair route.
- Runtime repair after a successful build should start from the latest `run` fields plus `/ui`, `/graph`, and `/explain`.
