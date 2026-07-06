#!/usr/bin/env python3
"""Delta/CVD анализ — давление покупателей/продавцов."""

import requests
import numpy as np
import pandas as pd
from datetime import datetime


class DeltaAnalyzer:
    BASE_URL = "https://api.binance.com"

    def fetch_trades(self, symbol: str, limit: int = 1000) -> list:
        url = f"{self.BASE_URL}/api/v3/trades"
        params = {"symbol": symbol.upper(), "limit": limit}
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def fetch_klines(self, symbol: str, interval: str = "1m", limit: int = 100) -> pd.DataFrame:
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

        for col in ["open", "high", "low", "close", "volume", "quote_volume", "taker_buy_volume", "taker_buy_quote_volume"]:
            df[col] = df[col].astype(float)

        df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms")
        return df

    def calculate_delta(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["taker_sell_volume"] = df["volume"] - df["taker_buy_volume"]
        df["taker_sell_quote"] = df["quote_volume"] - df["taker_buy_quote_volume"]
        df["delta"] = df["taker_buy_volume"] - df["taker_sell_volume"]
        df["delta_quote"] = df["taker_buy_quote_volume"] - df["taker_sell_quote"]
        df["cvd"] = df["delta"].cumsum()
        df["cvd_quote"] = df["delta_quote"].cumsum()
        df["delta_ratio"] = df["taker_buy_volume"] / df["volume"].replace(0, np.nan)
        return df

    def analyze(self, symbol: str, interval: str = "1m", limit: int = 100) -> dict:
        df = self.fetch_klines(symbol, interval, limit)
        df = self.calculate_delta(df)

        current_price = df["close"].iloc[-1]
        total_delta = df["delta"].iloc[-1]
        total_volume = df["volume"].sum()
        buy_volume = df["taker_buy_volume"].sum()
        sell_volume = df["taker_sell_volume"].sum()

        delta_pct = (total_delta / total_volume * 100) if total_volume > 0 else 0
        buy_pct = (buy_volume / total_volume * 100) if total_volume > 0 else 0
        sell_pct = (sell_volume / total_volume * 100) if total_volume > 0 else 0

        recent_10 = df.tail(10)
        recent_delta = recent_10["delta"].sum()
        recent_cvd_change = df["cvd"].iloc[-1] - df["cvd"].iloc[-10] if len(df) >= 10 else 0

        cvd_trend = "Восходящий" if df["cvd"].iloc[-1] > df["cvd"].iloc[-min(20, len(df))] else "Нисходящий"

        large_trades = df[df["volume"] > df["volume"].mean() * 2]
        large_buy = large_trades["taker_buy_volume"].sum() if not large_trades.empty else 0
        large_sell = large_trades["taker_sell_volume"].sum() if not large_trades.empty else 0
        large_delta = large_buy - large_sell

        return {
            "symbol": symbol,
            "interval": interval,
            "price": round(current_price, 8),
            "total_delta": round(total_delta, 4),
            "delta_quote": round(df["delta_quote"].iloc[-1], 2),
            "delta_pct": f"{delta_pct:+.2f}%",
            "delta_signal": (
                "Сильный бычий" if delta_pct > 10 else
                "Бычий" if delta_pct > 2 else
                "Нейтральный" if delta_pct > -2 else
                "Медвежий" if delta_pct > -10 else
                "Сильный медвежий"
            ),
            "buy_volume": round(buy_volume, 2),
            "sell_volume": round(sell_volume, 2),
            "buy_pct": f"{buy_pct:.1f}%",
            "sell_pct": f"{sell_pct:.1f}%",
            "cvd": round(df["cvd"].iloc[-1], 2),
            "cvd_trend": cvd_trend,
            "cvd_change": round(recent_cvd_change, 2),
            "recent_delta": round(recent_delta, 4),
            "large_trades": {
                "count": len(large_trades),
                "buy": round(large_buy, 2),
                "sell": round(large_sell, 2),
                "delta": round(large_delta, 2),
                "signal": "Бычий" if large_delta > 0 else "Медвежий",
            },
            "absorption": self._detect_absorption(df),
        }

    def _detect_absorption(self, df: pd.DataFrame) -> dict:
        if len(df) < 20:
            return {"detected": False}

        recent = df.tail(10)
        price_change = recent["close"].iloc[-1] - recent["close"].iloc[0]
        delta_sum = recent["delta"].sum()

        if abs(price_change) < recent["close"].mean() * 0.001 and abs(delta_sum) > recent["volume"].mean() * 5:
            return {
                "detected": True,
                "type": "Бычий" if delta_sum > 0 else "Медвежий",
                "description": "Большой дельта при малом движении цены",
            }

        return {"detected": False}


def format_delta(result: dict) -> str:
    lines = []
    lines.append(f"{'=' * 60}")
    lines.append(f"  DELTA/CVD АНАЛИЗ: {result['symbol']} ({result['interval']})")
    lines.append(f"{'=' * 60}")
    lines.append(f"")
    lines.append(f"  Цена:           {result['price']}")
    lines.append(f"  Delta:          {result['total_delta']:+.4f} ({result['delta_pct']}) [{result['delta_signal']}]")
    lines.append(f"  Delta (quote):  {result['delta_quote']:+,.2f}")
    lines.append(f"")
    lines.append(f"  Taker Buy:      {result['buy_volume']:,.2f} ({result['buy_pct']})")
    lines.append(f"  Taker Sell:     {result['sell_volume']:,.2f} ({result['sell_pct']})")
    lines.append(f"")
    lines.append(f"  CVD:            {result['cvd']:+,.2f}")
    lines.append(f"  CVD тренд:      {result['cvd_trend']}")
    lines.append(f"  CVD изменение:  {result['cvd_change']:+,.2f}")
    lines.append(f"  Delta (10 свечей): {result['recent_delta']:+.4f}")
    lines.append(f"")

    lt = result["large_trades"]
    lines.append(f"  Крупные сделки (>2x avg):")
    lines.append(f"    Кол-во:   {lt['count']}")
    lines.append(f"    Buy:      {lt['buy']:,.2f}")
    lines.append(f"    Sell:     {lt['sell']:,.2f}")
    lines.append(f"    Delta:    {lt['delta']:+,.2f} [{lt['signal']}]")

    if result["absorption"]["detected"]:
        lines.append(f"")
        lines.append(f"  ⚠️ АБСОРБЦИЯ ОБНАРУЖЕНА: {result['absorption']['type']}")
        lines.append(f"    {result['absorption']['description']}")

    lines.append(f"{'=' * 60}")
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Delta/CVD анализ")
    parser.add_argument("--symbol", "-s", default="BTCUSDT")
    parser.add_argument("--interval", "-i", default="1m")
    parser.add_argument("--limit", "-l", type=int, default=100)
    parser.add_argument("--json", "-j", action="store_true")
    args = parser.parse_args()

    analyzer = DeltaAnalyzer()
    result = analyzer.analyze(args.symbol, args.interval, args.limit)

    if args.json:
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_delta(result))
