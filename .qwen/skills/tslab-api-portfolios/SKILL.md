---
name: tslab-api-portfolios
description: "Legacy wrapper. Route portfolio backtest tasks to the smaller compare skill."
---

# Legacy Wrapper: Portfolios

Do not load this skill unless the user explicitly named `$tslab-api-portfolios` or an older prompt referenced it.

Use `$tslab-portfolio-compare` for:
- portfolio clone
- portfolio composition changes
- baseline/candidate runs
- status polling
- supported result comparison

Keep these rules:
- Use `scripts[].name` for follow-up `/api/scripts/{name}/*` calls.
- Portfolio `scriptId` is only for nested portfolio routes.
- Default analysis to `/performance` and `/profit`.
- Treat `/trades` as capability-checked.
- Do not assume a portfolio `/positions` route exists.
