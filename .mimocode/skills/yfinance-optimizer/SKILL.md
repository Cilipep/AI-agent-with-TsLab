---
name: yfinance-optimizer
description: "Download crypto data via yfinance, calculate indicators, run backtests with SL/TP, and optimize parameters across multiple instruments. Use when the user asks to test/optimize a strategy on live market data without pre-existing CSV files."
---

# YFinance Multi-Instrument Optimizer

## When to use

- User wants to backtest a strategy using live market data (not CSV)
- User asks to optimize strategy parameters across multiple crypto instruments
- User wants to compare strategy performance on different timeframes (H1, M15, D1)
- User provides a strategy concept and wants to find optimal parameters

## Workflow

### 1. Download data via yfinance

```python
import yfinance as yf

def download_data(symbol, interval='1h', period='3mo'):
    fmt = f"{symbol}-USD"  # Correct format for crypto
    t = yf.Ticker(fmt)
    d = t.history(period=period, interval=interval)
    if not d.empty and len(d) > 100:
        d = d.reset_index()
        d.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        d['symbol'] = symbol
        return d
    return None
```

**Important notes:**
- Use `SYMBOL-USD` format for crypto (e.g., `BTC-USD`, `SOL-USD`)
- 15m data limited to 60 days maximum
- H1 data available for 3+ months
- yfinance returns 7-8 columns: select only needed ones

### 2. Implement indicators

Common indicators used in strategies:
```python
def smma(series, period):  # Smoothed MA
def williams_r(high, low, close, period=14):  # Williams %R
def ema(series, period):  # Exponential MA
```

### 3. Run backtest with SL/TP

```python
def run_backtest(df, sl, tp, indicator_params, commission=0.001):
    # Calculate indicators
    # Generate signals
    # Check SL/TP before signal exits
    # Track equity curve
    # Return metrics dict
```

### 4. Optimize parameters

```python
from itertools import product

def optimize(df, sl_range, tp_range, param_ranges):
    best = None
    for sl, tp, *params in product(sl_range, tp_range, *param_ranges):
        if tp <= sl: continue
        r = run_backtest(df.copy(), sl, tp, params)
        if r and (best is None or r['ret'] > best['ret']):
            best = r
    return best
```

### 5. Multi-instrument loop

```python
instruments = ['SOL', 'DOGE', 'LINK', 'ETH', 'FET', 'BTC']
results = []
for sym in instruments:
    df = download_data(sym, interval='1h', period='3mo')
    if df is not None:
        best = optimize(df, ...)
        if best:
            best['sym'] = sym
            results.append(best)
results.sort(key=lambda x: x['ret'], reverse=True)
```

### 6. Save and present results

```python
pd.DataFrame(results).to_csv('tmp/optimization_results.csv', index=False)
# Print comparison table
```

## Output format

Print table with columns:
- Symbol, SL%, TP%, Indicator Params, Trades, Win Rate%, Return%, Max Drawdown%

## Common patterns

### SL/TP check in backtest loop
```python
if position == 1:  # Long
    sl_price = entry * (1 - sl)
    tp_price = entry * (1 + tp)
    if low <= sl_price:  # SL hit
    elif high >= tp_price:  # TP hit
```

### EMA trend filter
```python
if ema_period:
    ema_val = ema(close, ema_period)
    if buy_signal and close > ema_val:  # Long only above EMA
    if sell_signal and close < ema_val:  # Short only below EMA
```

## Dependencies

- `pandas`, `numpy`, `yfinance`

## File locations

- Scripts: `TsLabWorkspace/<strategy_name>/*.py`
- Results: `tmp/optimization_results.csv`

## Pitfalls

- yfinance 15m data limited to 60 days
- Use `SYMBOL-USD` format, not `SYMBOLUSD`
- Column names after reset_index: `Datetime, Open, High, Low, Close, Volume` (capitalized)
- Always check `len(df) > 100` before backtesting
- Commission of 0.1% round-trip is standard for crypto
