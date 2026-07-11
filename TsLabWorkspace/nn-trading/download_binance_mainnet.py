"""Download klines from Binance mainnet (public API, no keys needed)."""
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import pandas as pd


BASE_URL = "https://api.binance.com/api/v3"


def download_klines(symbol: str, interval: str = "1d", limit: int = 1000,
                    start_ms: int = None) -> pd.DataFrame:
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    if start_ms:
        params["startTime"] = start_ms
    resp = requests.get(f"{BASE_URL}/klines", params=params)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data, columns=[
        "Open_time", "Open", "High", "Low", "Close", "Volume",
        "Close_time", "Quote_volume", "Trades", "Taker_buy_base",
        "Taker_buy_quote", "Ignore",
    ])
    df["Open_time"] = pd.to_datetime(df["Open_time"], unit="ms")
    df.set_index("Open_time", inplace=True)
    for col in ["Open", "High", "Low", "Close", "Volume", "Quote_volume"]:
        df[col] = df[col].astype(float)
    return df[["Open", "High", "Low", "Close", "Volume", "Quote_volume"]]


def download_full(symbol: str, interval: str = "1d", days: int = 1820) -> pd.DataFrame:
    end_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    start_ms = end_ms - days * 24 * 3600 * 1000
    all_frames = []
    current_start = start_ms
    while current_start < end_ms:
        df = download_klines(symbol, interval, limit=1000, start_ms=current_start)
        if df.empty:
            break
        all_frames.append(df)
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

    for binance_sym, yf_sym in symbols.items():
        cache = Path("data") / f"binance_{yf_sym}_1d.csv"
        print(f"Downloading {binance_sym} from Binance mainnet...")
        try:
            df = download_full(binance_sym, "1d", days=1820)
            if len(df) > 0:
                df.to_csv(cache)
                print(f"  Saved {len(df)} daily bars")
            else:
                print(f"  No data")
        except Exception as e:
            print(f"  Error: {e}")

    print("Done!")


if __name__ == "__main__":
    main()
