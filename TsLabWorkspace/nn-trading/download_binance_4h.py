"""Download 4h klines from Binance Testnet for more data."""
import os
import time
import hashlib
import hmac
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

import requests
import pandas as pd


API_KEY = "XDIVWx3UNZ2CjfUt8sJBAUMO4gfUfHbXtkfpUjd2KmRomuXY0XINvxg783bPGaPQ"
API_SECRET = "FInObvOBe4i9U1k9tLZhv5ovhHqmjMeLXatRDHcsHApR0oPD7OK2RP3OtJ7RT89J"
BASE_URL = "https://testnet.binance.vision/api/v3"


def download_klines(symbol: str, interval: str = "4h", limit: int = 1000,
                    start_ms: int = None) -> pd.DataFrame:
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    if start_ms:
        params["startTime"] = start_ms
    headers = {"X-MBX-APIKEY": API_KEY}
    resp = requests.get(f"{BASE_URL}/klines", params=params, headers=headers)
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


def download_full(symbol: str, interval: str, days: int) -> pd.DataFrame:
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
        time.sleep(0.2)
    if not all_frames:
        return pd.DataFrame()
    full = pd.concat(all_frames)
    full = full[~full.index.duplicated(keep="last")]
    full.sort_index(inplace=True)
    return full


def to_daily(df_4h: pd.DataFrame) -> pd.DataFrame:
    """Resample 4h klines to daily OHLCV."""
    daily = df_4h.resample("1D").agg({
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum",
        "Quote_volume": "sum",
    }).dropna()
    return daily


def main():
    Path("data").mkdir(exist_ok=True)

    symbols = {"BTCUSDT": "BTC-USD", "ETHUSDT": "ETH-USD", "SOLUSDT": "SOL-USD"}

    for binance_sym, yf_sym in symbols.items():
        print(f"Downloading {binance_sym} (4h)...")
        try:
            df_4h = download_full(binance_sym, "4h", days=1820)
            print(f"  Got {len(df_4h)} 4h bars")
            if len(df_4h) > 0:
                daily = to_daily(df_4h)
                cache = Path("data") / f"binance_{yf_sym}_1d.csv"
                daily.to_csv(cache)
                print(f"  Saved {len(daily)} daily bars to {cache}")
        except Exception as e:
            print(f"  Error: {e}")

    print("Done!")


if __name__ == "__main__":
    main()
