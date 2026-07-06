#!/usr/bin/env python3
"""Получение списка всех доступных инструментов с бирж."""

import requests


class BinanceSymbols:
    BASE_URL = "https://api.binance.com"

    def get_all(self, quote: str = "USDT") -> list:
        url = f"{self.BASE_URL}/api/v3/exchangeInfo"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        symbols = []
        for s in data.get("symbols", []):
            if (s["quoteAsset"] == quote and
                s["status"] == "TRADING" and
                s["isSpotTradingAllowed"]):
                symbols.append({
                    "symbol": s["symbol"],
                    "base": s["baseAsset"],
                    "quote": s["quoteAsset"],
                    "precision": s["baseAssetPrecision"],
                })

        return sorted(symbols, key=lambda x: x["symbol"])


class BybitSymbols:
    BASE_URL = "https://api.bybit.com"

    def get_all(self, quote: str = "USDT") -> list:
        url = f"{self.BASE_URL}/v5/market/tickers"
        params = {"category": "linear"}
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        result = resp.json().get("result", {})

        symbols = []
        for item in result.get("list", []):
            if item.get("quoteCoin") == quote:
                symbols.append({
                    "symbol": item["symbol"],
                    "base": item.get("baseCoin", ""),
                    "quote": quote,
                    "price": float(item.get("lastPrice", 0)),
                    "volume_24h": float(item.get("turnover24h", 0)),
                })

        return sorted(symbols, key=lambda x: x["symbol"])


SYMBOL_CLIENTS = {
    "binance": BinanceSymbols,
    "bybit": BybitSymbols,
}


def get_all_symbols(exchange: str = "binance", quote: str = "USDT") -> list:
    client = SYMBOL_CLIENTS[exchange]()
    return client.get_all(quote)


def get_top_by_volume(exchange: str = "binance", quote: str = "USDT", limit: int = 50) -> list:
    client = SYMBOL_CLIENTS[exchange]()
    symbols = client.get_all(quote)

    if exchange == "bybit":
        symbols.sort(key=lambda x: x.get("volume_24h", 0), reverse=True)
        return symbols[:limit]

    return symbols[:limit]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Список инструментов")
    parser.add_argument("--exchange", "-e", default="binance", choices=["binance", "bybit"])
    parser.add_argument("--quote", "-q", default="USDT")
    parser.add_argument("--top", "-t", type=int, default=0, help="Топ по объёму (0 = все)")
    args = parser.parse_args()

    if args.top > 0:
        symbols = get_top_by_volume(args.exchange, args.quote, args.top)
    else:
        symbols = get_all_symbols(args.exchange, args.quote)

    print(f"Доступные инструменты ({args.exchange}, {args.quote}): {len(symbols)}")
    for s in symbols:
        vol = f" | Объём: {s.get('volume_24h', 0):,.0f}" if "volume_24h" in s else ""
        print(f"  {s['symbol']}{vol}")
