"""Download multi-timeframe data for BTC + 10 instruments from Binance."""
import time
from datetime import datetime, timezone
from pathlib import Path
import requests
import pandas as pd

BASE_URL = "https://api.binance.com/api/v3"


def download_klines(symbol, interval, days):
    end_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    start_ms = end_ms - days * 24 * 3600 * 1000
    all_frames = []
    current = start_ms
    while current < end_ms:
        params = {"symbol": symbol, "interval": interval, "limit": 1000, "startTime": current}
        resp = requests.get(f"{BASE_URL}/klines", params=params)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        df = pd.DataFrame(data, columns=[
            "Open_time", "Open", "High", "Low", "Close", "Volume",
            "Close_time", "Quote_volume", "Trades", "Taker_buy_base", "Taker_buy_quote", "Ignore",
        ])
        df["Open_time"] = pd.to_datetime(df["Open_time"], unit="ms")
        df.set_index("Open_time", inplace=True)
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            df[col] = df[col].astype(float)
        all_frames.append(df[["Open", "High", "Low", "Close", "Volume"]])
        current = int(df.index[-1].timestamp() * 1000) + 1
        time.sleep(0.25)
    if not all_frames:
        return pd.DataFrame()
    full = pd.concat(all_frames)
    full = full[~full.index.duplicated(keep="last")]
    full.sort_index(inplace=True)
    return full


def main():
    Path("data").mkdir(exist_ok=True)

    # BTC: 9 timeframes
    btc_tfs = {
        "5m": 18, "15m": 18, "30m": 18,
        "1h": 90, "4h": 360,
        "1d": 1820, "1w": 1820, "1M": 1820,
    }
    print("=== BTC 9 timeframes ===")
    for tf, days in btc_tfs.items():
        cache = Path("data") / f"binance_BTCUSDT_{tf}.csv"
        if cache.exists():
            print(f"  {tf}: cached")
            continue
        print(f"  Downloading BTC {tf} ({days}d)...")
        df = download_klines("BTCUSDT", tf, days)
        if len(df) > 0:
            df.to_csv(cache)
            print(f"    Saved {len(df)} bars")
        time.sleep(0.3)

    # 10 instruments: 1d + 1w + 1M
    instruments = ["NEARUSDT", "XLMUSDT", "SOLUSDT", "AAVEUSDT", "LINKUSDT",
                   "SUIUSDT", "ADAUSDT", "BCHUSDT", "TRXUSDT", "UNIUSDT"]
    inst_tfs = {"1d": 1820, "1w": 1820, "1M": 1820}

    print("\n=== 10 instruments (1d/1w/1M) ===")
    for sym in instruments:
        for tf, days in inst_tfs.items():
            cache = Path("data") / f"binance_{sym}_{tf}.csv"
            if cache.exists():
                continue
            print(f"  {sym} {tf}...")
            try:
                df = download_klines(sym, tf, days)
                if len(df) > 0:
                    df.to_csv(cache)
                    print(f"    {len(df)} bars")
            except Exception as e:
                print(f"    Error: {e}")
            time.sleep(0.3)

    print("\nDone!")


if __name__ == "__main__":
    main()
