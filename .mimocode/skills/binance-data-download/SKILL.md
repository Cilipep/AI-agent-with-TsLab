---
name: binance-data-download
description: Download OHLCV klines from Binance mainnet API for any symbol and timeframe. Handles pagination, rate limiting, and caching.
---

# Binance Data Download

## When to use
- Need historical crypto price data for backtesting or analysis
- User mentions Binance, klines, OHLCV, or crypto data download

## Steps

1. Create download script with `download_klines(symbol, interval, days)` function
2. Use Binance public API: `https://api.binance.com/api/v3/klines`
3. Paginate with `startTime` parameter (max 1000 bars per request)
4. Rate limit: `time.sleep(0.25)` between requests
5. Cache to `data/binance_{SYMBOL}_{interval}.csv`
6. Supported intervals: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M

## Template

```python
import time, requests, pandas as pd
from datetime import datetime, timezone

BASE_URL = "https://api.binance.com/api/v3"

def download_klines(symbol, interval, days):
    end_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    start_ms = end_ms - days * 24 * 3600 * 1000
    all_frames, current = [], start_ms
    while current < end_ms:
        params = {"symbol": symbol, "interval": interval, "limit": 1000, "startTime": current}
        resp = requests.get(f"{BASE_URL}/klines", params=params)
        resp.raise_for_status()
        data = resp.json()
        if not data: break
        df = pd.DataFrame(data, columns=["Open_time","Open","High","Low","Close","Volume","Close_time","Quote_volume","Trades","Taker_buy_base","Taker_buy_quote","Ignore"])
        df["Open_time"] = pd.to_datetime(df["Open_time"], unit="ms")
        df.set_index("Open_time", inplace=True)
        for col in ["Open","High","Low","Close","Volume"]: df[col] = df[col].astype(float)
        all_frames.append(df[["Open","High","Low","Close","Volume"]])
        current = int(df.index[-1].timestamp() * 1000) + 1
        time.sleep(0.25)
    if not all_frames: return pd.DataFrame()
    full = pd.concat(all_frames).drop_duplicates().sort_index()
    return full
```

## Notes
- No API key needed for public klines endpoint
- `1Y` interval does NOT exist on Binance (use `1M` instead)
- SUIUSDT has less history (~1166 days) than older coins
- Always check `cache.exists()` before downloading
