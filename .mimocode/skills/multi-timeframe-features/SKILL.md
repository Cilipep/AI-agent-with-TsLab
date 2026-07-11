---
name: multi-timeframe-features
description: Merge technical indicators from multiple timeframes (1d, 1w, 1M, etc.) into a single daily DataFrame via forward-fill alignment.
---

# Multi-Timeframe Feature Engineering

## When to use
- Need to combine indicators from different timeframes into one dataset
- User asks for "multi-timeframe", "multiple TF", or "1d + 1w + 1M features"
- Models need context from higher/lower timeframes

## Steps

1. Compute indicators on each timeframe independently
2. Align higher TF data to daily index via `reindex(method="ffill")`
3. Drop duplicate Close columns (keep only daily Close)
4. Forward-fill and backfill NaN
5. Remove duplicate column names

## Template

```python
import numpy as np, pandas as pd, talib

def compute_indicators(df, prefix):
    df = df.copy()
    c, h, l = df["Close"].values.astype(np.float64), df["High"].values.astype(np.float64), df["Low"].values.astype(np.float64)
    df[f"{prefix}ema10"] = talib.EMA(c, 10)
    df[f"{prefix}ema20"] = talib.EMA(c, 20)
    df[f"{prefix}rsi"] = talib.RSI(c, 14)
    macd, sig, hist = talib.MACD(c)
    df[f"{prefix}macd"] = macd
    bu, bm, bl = talib.BBANDS(c, 20)
    df[f"{prefix}bb_w"] = (bu - bl) / bm
    df[f"{prefix}atr"] = talib.ATR(h, l, c, 14)
    df[f"{prefix}adx"] = talib.ADX(h, l, c, 14)
    df[f"{prefix}ret"] = df["Close"].pct_change()
    keep = [col for col in df.columns if col.startswith(prefix) or col == "Close"]
    return df[keep]

def merge_timeframes(daily, tf_data):
    result = daily.copy()
    for tf_name, tf_df in tf_data.items():
        ind = compute_indicators(tf_df, f"{tf_name}_")
        aligned = ind.reindex(result.index, method="ffill")
        close_cols = [c for c in aligned.columns if "Close" in c or c == "Close"]
        if close_cols: aligned = aligned.drop(columns=close_cols)
        result = pd.concat([result, aligned], axis=1)
    result = result.ffill().bfill()
    result = result.loc[:, ~result.columns.duplicated()]
    return result
```

## Key gotchas
- Higher TFs (1w, 1M) have few bars → many NaN at start → use ffill/bfill
- Always drop Close from non-daily timeframes to avoid column conflicts
- `pd.concat` creates duplicate columns if names collide → deduplicate after
- Compute indicators BEFORE alignment (indicators need proper time series)
