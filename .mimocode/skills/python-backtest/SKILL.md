---
name: python-backtest
description: Run Python backtests on historical CSV data for trading strategies. Calculate indicators, generate signals, simulate trades, compute metrics, and save results.
---

# Python Backtest Skill

## When to use

- User asks to backtest a strategy on historical CSV data
- User provides a CSV file with OHLCV data and wants to analyze strategy performance
- User wants to optimize parameters (SL/TP, indicator periods) across multiple instruments
- User asks for metrics like win rate, profit factor, max drawdown, Sharpe ratio

## Workflow

### 1. Read and validate CSV

```python
import pandas as pd
df = pd.read_csv(csv_path)
# Expected columns: symbol, timestamp, open, high, low, close, volume
symbols = sorted(df['symbol'].unique())
```

### 2. Define strategy parameters

```python
# Example: SMA crossover
SMA_SHORT = 5
SMA_LONG = 20
SL_PCT = 0.02  # Stop Loss 2%
TP_PCT = 0.04  # Take Profit 4%
COMMISSION_PCT = 0.05 / 100
INITIAL_CAPITAL = 100000
```

### 3. Implement backtest loop

Key elements:
- Sort by timestamp
- Calculate indicators (rolling windows)
- Detect signals (crossovers, threshold breaches)
- Check SL/TP before signal exits
- Track position state (flat/long/short)
- Record trades with entry/exit prices and times
- Build equity curve for drawdown calculation

### 4. Calculate metrics

Required metrics:
- `total_return_pct`: ((final - initial) / initial) * 100
- `win_rate`: (wins / total_trades) * 100
- `profit_factor`: gross_profit / gross_loss
- `max_drawdown_pct`: max((peak - equity) / peak) * 100
- `sharpe`: (mean_return / std_return) * sqrt(252)

### 5. Multi-instrument loop

```python
results = []
for symbol in symbols:
    df_sym = df_all[df_all['symbol'] == symbol].copy()
    result = run_backtest(df_sym, symbol)
    if result:
        results.append(result)
results.sort(key=lambda x: x['total_return_pct'], reverse=True)
```

### 6. Save results

```python
df_results = pd.DataFrame(results)
df_results.to_csv(output_path, index=False)
```

## Output format

Print summary table with columns:
- Symbol, Trades, Return%, Win Rate%, Profit Factor, Max Drawdown%, Sharpe

Print top 5 profitable and bottom 5 losing instruments.

## Common patterns

### SL/TP check logic

```python
if position == 1:
    sl_price = entry_price * (1 - sl_pct)
    tp_price = entry_price * (1 + tp_pct)
    if df.iloc[i]['low'] <= sl_price:
        # Stop Loss hit
        pnl = (sl_price - entry_price) / entry_price - COMMISSION_PCT * 2
    elif df.iloc[i]['high'] >= tp_price:
        # Take Profit hit
        pnl = (tp_price - entry_price) / entry_price - COMMISSION_PCT * 2
```

### SMA crossover signals

```python
golden_cross = (sma1_t > sma2_t) and (sma1_y <= sma2_y)
death_cross = (sma1_t < sma2_t) and (sma1_y >= sma2_y)
```

### Parameter optimization

```python
from itertools import product
for sl, tp in product(SL_RANGE, TP_RANGE):
    if tp <= sl:
        continue
    result = run_backtest(df_sym.copy(), sl, tp)
    # Track best result
```

## Dependencies

- `pandas` (install: `pip install pandas`)
- `numpy` (install: `pip install numpy`)

## File locations

- Scripts: `tmp/skred_backtest*.py`
- Results: `tmp/skred_backtest*.csv`
- Data: `tmp/market_data/*.csv`
