---
name: tslab-portfolio-compare
description: "Phase card for cloning and comparing portfolio backtest runs."
---

# TSLab Portfolio Compare

## When to load

- A portfolio backtest must be cloned, run, or compared.

## First call

- `POST /api/portfolios/backtesting/{id}/clone`

## Fields to read

- Status:
  - `response.data.status`
- Results:
  - `response.data` from run-scoped `/performance`
  - `response.data` from run-scoped `/profit`

## Next allowed call

- `POST /api/portfolios/backtesting/{id}/runs`
- `GET /api/portfolios/backtesting/runs/{jobId}`
- `GET /api/portfolios/backtesting/runs/{jobId}/performance`
- `GET /api/portfolios/backtesting/runs/{jobId}/profit`

## Stop if failed

- Do not use portfolio-level `/performance` or `/profit`.
- Do not assume `/positions`.
