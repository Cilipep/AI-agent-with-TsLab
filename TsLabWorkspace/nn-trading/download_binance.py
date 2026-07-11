"""Download klines data from Binance Testnet API."""
import os
import time
import hashlib
import hmac
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path

import requests
import pandas as pd


API_KEY = "XDIVWx3UNZ2CjfUt8sJBAUMO4gfUfHbXtkfpUjd2KmRomuXY0XINvxg783bPGaPQ"
API_SECRET = "FInObvOBe4i9U1k9tLZhv5ovhHqmjMeLXatRDHcsHApR0oPD7OK2RP3OtJ7RT89J"
BASE_URL = "https://testnet.binance.vision/api/v3"


def _sign(params: dict) -> dict:
    """Sign request with HMAC-SHA256."""
    params["timestamp"] = int(time.time() * 1000)
    query = urllib.parse.urlencode(params)
    signature = hmac.new(API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()
    params["signature"] = signature
    return params


def download_klines(symbol: str, interval: str = "1d", limit: int = 1000,
                    start_ms: int = None) -> pd.DataFrame:
    """Download klines from Binance Testnet."""
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit,
    }
    if start_ms:
        params["startTime"] = start_ms

    headers = {"X-MBX-APIKEY": API_KEY}
    resp = requests.get(f"{BASE_URL}/klines", params=params, headers=headers)
    resp.raise_for_status()
    data = resp.json()

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
    """Download full history by paginating klines."""
    end_ms = int(datetime.utcnow().timestamp() * 1000)
    start_ms = end_ms - days * 24 * 3600 * 1000

    all_frames = []
    current_start = start_ms

    while current_start < end_ms:
        df = download_klines(symbol, interval, limit=1000, start_ms=current_start)
        if df.empty:
            break
        all_frames.append(df)
        # Next page starts after last bar
        last_time = df.index[-1]
        current_start = int(last_time.timestamp() * 1000) + 1
        time.sleep(0.2)  # rate limit

    if not all_frames:
        return pd.DataFrame()

    full = pd.concat(all_frames)
    full = full[~full.index.duplicated(keep="last")]
    full.sort_index(inplace=True)
    return full


def main():
    Path("data").mkdir(exist_ok=True)

    symbols = {
        "BTCUSDT": "BTC-USD",
        "ETHUSDT": "ETH-USD",
        "SOLUSDT": "SOL-USD",
    }

    for binance_sym, yf_sym in symbols.items():
        cache = Path("data") / f"binance_{yf_sym}_1d.csv"
        print(f"Downloading {binance_sym}...")
        try:
            df = download_full(binance_sym, interval="1d", days=1820)
            if len(df) > 0:
                df.to_csv(cache)
                print(f"  Saved {len(df)} bars to {cache}")
            else:
                print(f"  No data returned for {binance_sym}")
        except Exception as e:
            print(f"  Error: {e}")

    print("Done!")


if __name__ == "__main__":
    main()
