import requests
import pandas as pd
import numpy as np
from collections import defaultdict


class BinanceOrderBook:
    BASE_URL = "https://api.binance.com"

    def fetch(self, symbol: str, limit: int = 100) -> dict:
        url = f"{self.BASE_URL}/api/v3/depth"
        params = {"symbol": symbol.upper(), "limit": limit}
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        bids = [(float(p), float(q)) for p, q in data.get("bids", [])]
        asks = [(float(p), float(q)) for p, q in data.get("asks", [])]

        return {"bids": bids, "asks": asks}


class BybitOrderBook:
    BASE_URL = "https://api.bybit.com"

    def fetch(self, symbol: str, limit: int = 100) -> dict:
        url = f"{self.BASE_URL}/v5/market/orderbook"
        params = {"category": "linear", "symbol": symbol.upper(), "limit": limit}
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        result = resp.json().get("result", {})

        bids = [(float(p), float(q)) for p, q in result.get("b", [])]
        asks = [(float(p), float(q)) for p, q in result.get("a", [])]

        return {"bids": bids, "asks": asks}


ORDERBOOK_CLIENTS = {
    "binance": BinanceOrderBook,
    "bybit": BybitOrderBook,
}


def analyze_orderbook(book: dict, current_price: float) -> dict:
    bids = book["bids"]
    asks = book["asks"]

    if not bids or not asks:
        return {"error": "Empty orderbook"}

    total_bid_vol = sum(q for _, q in bids)
    total_ask_vol = sum(q for _, q in asks)
    total_vol = total_bid_vol + total_ask_vol

    imbalance = (total_bid_vol - total_ask_vol) / total_vol if total_vol > 0 else 0
    spread = asks[0][0] - bids[0][0]
    spread_pct = (spread / current_price) * 100

    bid_walls = find_walls(bids, current_price, side="bid")
    ask_walls = find_walls(asks, current_price, side="ask")

    bid_clusters = cluster_levels(bids, current_price)
    ask_clusters = cluster_levels(asks, current_price)

    nearby_bid_vol = sum(q for p, q in bids if p >= current_price * 0.99)
    nearby_ask_vol = sum(q for p, q in asks if p <= current_price * 1.01)

    return {
        "total_bid_vol": round(total_bid_vol, 2),
        "total_ask_vol": round(total_ask_vol, 2),
        "imbalance": round(imbalance, 4),
        "imbalance_pct": f"{imbalance * 100:+.2f}%",
        "imbalance_signal": (
            "Сильный бычий" if imbalance > 0.3 else
            "Бычий" if imbalance > 0.1 else
            "Нейтральный" if imbalance > -0.1 else
            "Медвежий" if imbalance > -0.3 else
            "Сильный медвежий"
        ),
        "spread": round(spread, 8),
        "spread_pct": f"{spread_pct:.4f}%",
        "bid_walls": bid_walls[:5],
        "ask_walls": ask_walls[:5],
        "bid_clusters": bid_clusters[:5],
        "ask_clusters": ask_clusters[:5],
        "bid_ask_ratio": round(total_bid_vol / total_ask_vol, 2) if total_ask_vol > 0 else 0,
        "nearby_bid_vol": round(nearby_bid_vol, 2),
        "nearby_ask_vol": round(nearby_ask_vol, 2),
    }


def find_walls(orders: list, current_price: float, side: str, threshold: float = 3.0) -> list:
    if not orders:
        return []

    volumes = [q for _, q in orders]
    avg_vol = np.mean(volumes) if volumes else 0

    walls = []
    for price, qty in orders:
        if qty > avg_vol * threshold:
            walls.append({
                "price": price,
                "volume": round(qty, 4),
                "strength": round(qty / avg_vol, 1) if avg_vol > 0 else 0,
                "type": "bid" if side == "bid" else "ask",
            })

    return sorted(walls, key=lambda x: x["strength"], reverse=True)


def cluster_levels(orders: list, current_price: float, pct: float = 0.1) -> list:
    if not orders:
        return []

    sorted_orders = sorted(orders, key=lambda x: x[0])
    clusters = [[sorted_orders[0]]]

    for order in sorted_orders[1:]:
        last_cluster = clusters[-1]
        avg_price = np.mean([o[0] for o in last_cluster])
        if abs(order[0] - avg_price) / avg_price * 100 <= pct:
            last_cluster.append(order)
        else:
            clusters.append([order])

    result = []
    for cluster in clusters:
        avg_price = np.mean([o[0] for o in cluster])
        total_vol = sum(o[1] for o in cluster)
        result.append({
            "price": round(avg_price, 8),
            "volume": round(total_vol, 2),
            "orders": len(cluster),
        })

    return sorted(result, key=lambda x: x["volume"], reverse=True)


def fetch_volume_profile(df: pd.DataFrame, bins: int = 50) -> dict:
    if len(df) < 10:
        return {"error": "Not enough data"}

    price_min = df["low"].min()
    price_max = df["high"].max()
    price_range = np.linspace(price_min, price_max, bins + 1)

    volume_at_price = np.zeros(bins)

    for _, row in df.iterrows():
        for i in range(bins):
            if price_range[i] <= row["close"] <= price_range[i + 1]:
                volume_at_price[i] += row["volume"]
                break

    poc_idx = np.argmax(volume_at_price)
    poc_price = (price_range[poc_idx] + price_range[poc_idx + 1]) / 2

    total_vol = volume_at_price.sum()
    cumulative = np.cumsum(volume_at_price)
    va_low_idx = np.searchsorted(cumulative, total_vol * 0.15)
    va_high_idx = np.searchsorted(cumulative, total_vol * 0.85)

    va_low = price_range[min(va_low_idx, bins - 1)]
    va_high = price_range[min(va_high_idx, bins - 1)]

    current_price = df["close"].iloc[-1]

    return {
        "poc": round(poc_price, 8),
        "va_low": round(va_low, 8),
        "va_high": round(va_high, 8),
        "price_min": round(price_min, 8),
        "price_max": round(price_max, 8),
        "poc_distance": f"{((current_price / poc_price) - 1) * 100:+.2f}%",
        "in_value_area": va_low <= current_price <= va_high,
        "position": (
            "Выше POC" if current_price > poc_price else
            "Ниже POC"
        ),
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Анализ стакана ордеров")
    parser.add_argument("--symbol", "-s", default="BTCUSDT")
    parser.add_argument("--exchange", "-e", default="binance")
    parser.add_argument("--limit", "-l", type=int, default=100)
    args = parser.parse_args()

    client = ORDERBOOK_CLIENTS[args.exchange]()
    book = client.fetch(args.symbol, args.limit)

    from exchanges import get_client
    market_client = get_client(args.exchange)
    df = market_client.fetch_klines(args.symbol, "1h", 100)
    current_price = df["close"].iloc[-1]

    result = analyze_orderbook(book, current_price)
    print(f"Стакан ордеров {args.symbol}:")
    print(f"  Bid объём: {result['total_bid_vol']}")
    print(f"  Ask объём: {result['total_ask_vol']}")
    print(f"  Дисбаланс: {result['imbalance_pct']} ({result['imbalance_signal']})")
    print(f"  Спред: {result['spread_pct']}")
    print(f"  Bid/Ask: {result['bid_ask_ratio']}")

    if result['bid_walls']:
        print(f"\n  Стены покупок:")
        for w in result['bid_walls']:
            print(f"    {w['price']}: {w['volume']} ({w['strength']}x)")

    if result['ask_walls']:
        print(f"\n  Стены продаж:")
        for w in result['ask_walls']:
            print(f"    {w['price']}: {w['volume']} ({w['strength']}x)")
