"""Download multi-timeframe klines from Binance: 1d, 1w, 1m."""
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import pandas as pd


BASE_URL = "https://api.binance.com/api/v3"


def download_klines(symbol: str, interval: str, days: int) -> pd.DataFrame:
    end_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    start_ms = end_ms - days * 24 * 3600 * 1000
    all_frames = []
    current_start = start_ms

    while current_start < end_ms:
        params = {"symbol": symbol, "interval": interval, "limit": 1000, "startTime": current_start}
        resp = requests.get(f"{BASE_URL}/klines", params=params)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        df = pd.DataFrame(data, columns=[
            "Open_time", "Open", "High", "Low", "Close", "Volume",
            "Close_time", "Quote_volume", "Trades", "Taker_buy_base",
            "Taker_buy_quote", "Ignore",
        ])
        df["Open_time"] = pd.to_datetime(df["Open_time"], unit="ms")
        df.set_index("Open_time", inplace=True)
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            df[col] = df[col].astype(float)
        all_frames.append(df[["Open", "High", "Low", "Close", "Volume"]])
        last_time = df.index[-1]
        current_start = int(last_time.timestamp() * 1000) + 1
        time.sleep(0.3)

    if not all_frames:
        return pd.DataFrame()
    full = pd.concat(all_frames)
    full = full[~full.index.duplicated(keep="last")]
    full.sort_index(inplace=True)
    return full


def main():
    Path("data").mkdir(exist_ok=True)
    symbols = {"BTCUSDT": "BTC-USD", "ETHUSDT": "ETH-USD", "SOLUSDT": "SOL-USD"}

    timeframes = {
        "1d": 1820,
        "1w": 1820,
        "1M": 1820,
    }

    for binance_sym, yf_sym in symbols.items():
        for interval, days in timeframes.items():
            fname = f"binance_{yf_sym}_{interval}.csv"
            cache = Path("data") / fname
            print(f"Downloading {binance_sym} {interval}...")
            try:
                df = download_klines(binance_sym, interval, days)
                if len(df) > 0:
                    df.to_csv(cache)
                    print(f"  Saved {len(df)} bars to {cache}")
            except Exception as e:
                print(f"  Error: {e}")

    print("Done!")


if __name__ == "__main__":
    main()
