---
name: multi-instrument-test
description: "Clone a TSLab strategy to multiple instruments or timeframes, run lifecycle on each, and produce a comparison table. Use when the user asks to test a strategy on different instruments, timeframes, or compare variants."
---

# Multi-Instrument / Multi-Timeframe Testing

## When to use

- User wants to test the same strategy on different instruments (e.g., DOGE vs SOL vs AVAX)
- User wants to compare the same strategy across timeframes (e.g., 15H vs 1H vs 4H)
- User wants to find the best instrument for an existing strategy

## Workflow

### Phase 1 — Discover instruments

```
GET /api/agent-manager/securities?dataSourceName={datasource}&query=PERP&limit=100
```

Filter to `_PERP` contracts only (exclude `.FundingRate`, `.MarkPrice`).

### Phase 2 — Clone and configure each variant

For each target instrument/timeframe:

1. **Copy** the source script:
   ```
   POST /api/scripts/{sourceName}/copy  body: {"name":"{newName}"}
   ```

2. **Set source mapping** (if changing instrument):
   ```json
   POST /api/scripts/{newName}/ops
   body: {"ops":[{"op":"SetSourceMapping","blockId":"Src","dataSourceName":"{datasource}","securityId":"{instrumentId}"}]}
   ```

3. **Set interval** (if changing timeframe):
   ```
   POST /api/scripts/{newName}/lab-options  body: {"intervalBase":1,"interval":{minutes}}
   ```
   Common intervals: 15 (15H), 60 (1H), 240 (4H), 1440 (D).

### Phase 3 — Lifecycle each variant

For each configured script, use `./run-lifecycle.ps1 "{scriptName}"` or the manual chain:

```
POST /api/scripts/{name}/validate
POST /api/scripts/{name}/build
POST /api/scripts/{name}/load
POST /api/scripts/{name}/run
GET  /api/scripts/{name}/metrics-summary
```

If validate returns errors, fix before build. If run hangs, check status and logs.

### Phase 4 — Compare results

Collect from each metrics-summary:
- `netProfit`, `netProfitPct`
- `allTrades`
- `profitFactor`
- `maxDrawdownPct`
- `winTradesPct`
- `fixedRecoveryFactor`

Present as a ranked comparison table sorted by `netProfitPct` or `fixedRecoveryFactor`.

### Phase 5 — Cleanup (optional)

Delete test variants if user doesn't need them:
```
DELETE /api/scripts/{name}
```

## Naming convention

Use `{sourceName}_{suffix}` for clones:
- Instruments: `BB_RSI_Strategy_DOGE`, `BB_RSI_Strategy_SOL`
- Timeframes: `BB_RSI_Strategy_1H`, `BB_RSI_Strategy_4H`

## Pitfalls

- `SetSourceMapping` requires both `dataSourceName` and `securityId`
- `lab-options` POST expects `intervalBase` as integer (1=MINUTE), not string
- Some instruments have sparse data — check `barsCount` in run results
- A script with 1-5 trades is not statistically significant
- PowerShell `curl.exe` is preferred over `Invoke-RestMethod` for long timeouts
