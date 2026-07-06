#!/usr/bin/env python3
"""WebSocket мониторинг — лайв-данные и алерты."""

import json
import time
import threading
from datetime import datetime
from collections import deque

try:
    import websocket
    HAS_WS = True
except ImportError:
    HAS_WS = False


class LiveMonitor:
    def __init__(self, symbol: str = "BTCUSDT"):
        self.symbol = symbol.upper()
        self.prices = deque(maxlen=1000)
        self.volumes = deque(maxlen=1000)
        self.trades = deque(maxlen=500)
        self.alerts = []
        self.running = False
        self.callbacks = []

    def add_alert(self, price_above: float = None, price_below: float = None,
                  volume_spike: float = None, callback=None):
        alert = {}
        if price_above:
            alert["price_above"] = price_above
        if price_below:
            alert["price_below"] = price_below
        if volume_spike:
            alert["volume_spike"] = volume_spike
        if callback:
            alert["callback"] = callback
        self.alerts.append(alert)

    def on_message(self, ws, message):
        data = json.loads(message)

        if "p" in data:
            price = float(data["p"])
            qty = float(data["q"])
            is_buy = data["m"]
            ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]

            self.prices.append(price)
            self.volumes.append(qty)
            self.trades.append({
                "time": ts,
                "price": price,
                "qty": qty,
                "side": "BUY" if is_buy else "SELL",
            })

            self._check_alerts(price, qty)

            if len(self.prices) % 10 == 0:
                self._print_status()

    def _check_alerts(self, price: float, qty: float):
        for alert in self.alerts:
            if "price_above" in alert and price >= alert["price_above"]:
                print(f"\n🔔 АЛЕРТ: Цена {price} >= {alert['price_above']}")
                alert.pop("price_above")
                if "callback" in alert:
                    alert["callback"](price)

            if "price_below" in alert and price <= alert["price_below"]:
                print(f"\n🔔 АЛЕРТ: Цена {price} <= {alert['price_below']}")
                alert.pop("price_below")
                if "callback" in alert:
                    alert["callback"](price)

            if "volume_spike" in alert and qty >= alert["volume_spike"]:
                print(f"\n🔔 АЛЕРТ: Объём {qty} >= {alert['volume_spike']}")

    def _print_status(self):
        if len(self.prices) < 2:
            return

        current = self.prices[-1]
        high = max(self.prices)
        low = min(self.prices)
        change = (self.prices[-1] - self.prices[0]) / self.prices[0] * 100

        buy_vol = sum(v for t, v in zip(self.prices, self.volumes) if self.trades and self.trades[-1]["side"] == "BUY")
        total_vol = sum(self.volumes)

        recent = list(self.trades)[-10:]
        buys = sum(1 for t in recent if t["side"] == "BUY")

        print(f"\r  {self.symbol} | {current:,.2f} | H: {high:,.2f} L: {low:,.2f} | {change:+.3f}% | Trades: {len(self.prices)} | Buy/Sell: {buys}/{10-buys}", end="", flush=True)

    def _on_error(self, ws, error):
        print(f"\nОшибка: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        print(f"\nСоединение закрыто")

    def _on_open(self, ws):
        print(f"✅ Подключено к {self.symbol} (Live)")
        print(f"   Нажмите Ctrl+C для остановки")

    def start(self, alerts: list = None):
        if not HAS_WS:
            print("Установите websocket-client: pip install websocket-client")
            return

        for alert in (alerts or []):
            self.add_alert(**alert)

        self.running = True
        stream = f"{self.symbol.lower()}@trade"
        url = f"wss://stream.binance.com:9443/ws/{stream}"

        ws = websocket.WebSocketApp(
            url,
            on_message=self.on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open,
        )

        try:
            ws.run_forever()
        except KeyboardInterrupt:
            print(f"\nОстановлено")
            self.running = False

    def start_multi(self, symbols: list, alerts: dict = None):
        if not HAS_WS:
            print("Установите websocket-client: pip install websocket-client")
            return

        self.running = True
        streams = "/".join([f"{s.lower()}@trade" for s in symbols])
        url = f"wss://stream.binance.com:9443/stream?streams={streams}"

        print(f"✅ Подключено к {len(symbols)} символам (Live)")

        ws = websocket.WebSocketApp(
            url,
            on_message=self._on_multi_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open,
        )

        try:
            ws.run_forever()
        except KeyboardInterrupt:
            print(f"\nОстановлено")
            self.running = False

    def _on_multi_message(self, ws, message):
        data = json.loads(message)
        stream_data = data.get("data", {})

        if "p" in stream_data:
            symbol = data.get("stream", "").split("@")[0].upper()
            price = float(stream_data["p"])
            qty = float(stream_data["q"])
            is_buy = stream_data["m"]
            ts = datetime.now().strftime("%H:%M:%S")

            side = "🟢" if is_buy else "🔴"
            print(f"  {ts} {symbol:<12} {side} {price:>12,.2f}  qty: {qty:.4f}")


def get_live_price(symbol: str) -> dict:
    import requests
    url = f"https://api.binance.com/api/v3/ticker/24hr"
    params = {"symbol": symbol.upper()}
    resp = requests.get(url, params=params, timeout=5)
    data = resp.json()

    return {
        "symbol": data["symbol"],
        "price": float(data["lastPrice"]),
        "change_24h": float(data["priceChangePercent"]),
        "high_24h": float(data["highPrice"]),
        "low_24h": float(data["lowPrice"]),
        "volume_24h": float(data["volume"]),
        "quote_volume_24h": float(data["quoteVolume"]),
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="WebSocket мониторинг")
    parser.add_argument("--symbol", "-s", default="BTCUSDT")
    parser.add_argument("--multi", "-m", nargs="+", help="Несколько символов")
    parser.add_argument("--alert-above", type=float, help="Алерт при цене выше")
    parser.add_argument("--alert-below", type=float, help="Алерт при цене ниже")
    parser.add_argument("--price", "-p", action="store_true", help="Показать текущую цену и выйти")
    args = parser.parse_args()

    if args.price:
        info = get_live_price(args.symbol)
        print(f"{info['symbol']}: {info['price']:,.2f} ({info['change_24h']:+.2f}%)")
        print(f"  24h High: {info['high_24h']:,.2f} Low: {info['low_24h']:,.2f}")
        print(f"  24h Volume: {info['volume_24h']:,.2f} ({info['quote_volume_24h']:,.2f} USDT)")
    elif args.multi:
        monitor = LiveMonitor()
        monitor.start_multi(args.multi)
    else:
        monitor = LiveMonitor(args.symbol)
        alerts = []
        if args.alert_above:
            alerts.append({"price_above": args.alert_above})
        if args.alert_below:
            alerts.append({"price_below": args.alert_below})
        monitor.start(alerts)
