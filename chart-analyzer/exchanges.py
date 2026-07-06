import requests
import pandas as pd
from datetime import datetime, timedelta


class BinanceClient:
    BASE_URL = "https://api.binance.com"

    INTERVALS = {
        "1m": "1m", "3m": "3m", "5m": "5m", "15m": "15m",
        "30m": "30m", "1h": "1h", "2h": "2h", "4h": "4h",
        "6h": "6h", "8h": "8h", "12h": "12h", "1d": "1d",
        "3d": "3d", "1w": "1w", "1M": "1M",
    }

    def fetch_klines(self, symbol: str, interval: str = "1h", limit: int = 200) -> pd.DataFrame:
        url = f"{self.BASE_URL}/api/v3/klines"
        params = {"symbol": symbol.upper(), "interval": interval, "limit": limit}
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        df = pd.DataFrame(data, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_volume", "trades", "taker_buy_volume",
            "taker_buy_quote_volume", "ignore"
        ])

        for col in ["open", "high", "low", "close", "volume", "quote_volume"]:
            df[col] = df[col].astype(float)

        df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms")
        df = df[["timestamp", "open", "high", "low", "close", "volume", "quote_volume", "trades"]]
        return df


class BybitClient:
    BASE_URL = "https://api.bybit.com"

    INTERVALS = {
        "1m": "1", "3m": "3", "5m": "5", "15m": "15",
        "30m": "30", "1h": "60", "2h": "120", "4h": "240",
        "6h": "360", "8h": "480", "12h": "720", "1d": "D",
        "3d": "3D", "1w": "W", "1M": "M",
    }

    def fetch_klines(self, symbol: str, interval: str = "1h", limit: int = 200) -> pd.DataFrame:
        bybit_interval = self.INTERVALS.get(interval, "60")
        url = f"{self.BASE_URL}/v5/market/kline"
        params = {
            "category": "linear",
            "symbol": symbol.upper(),
            "interval": bybit_interval,
            "limit": limit,
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        result = resp.json().get("result", {})
        raw = result.get("list", [])

        rows = []
        for item in raw:
            rows.append({
                "timestamp": pd.to_datetime(int(item[0]), unit="ms"),
                "open": float(item[1]),
                "high": float(item[2]),
                "low": float(item[3]),
                "close": float(item[4]),
                "volume": float(item[5]),
            })

        df = pd.DataFrame(rows)
        if not df.empty:
            df = df.sort_values("timestamp").reset_index(drop=True)
        return df


EXCHANGES = {
    "binance": BinanceClient,
    "bybit": BybitClient,
}


def get_client(name: str):
    cls = EXCHANGES.get(name.lower())
    if not cls:
        raise ValueError(f"Unknown exchange: {name}. Available: {list(EXCHANGES.keys())}")
    return cls()
