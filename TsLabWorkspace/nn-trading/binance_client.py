"""Binance Futures Testnet REST + WebSocket client."""
import time
import hmac
import hashlib
import json
from urllib.parse import urlencode
from typing import Optional

import requests
import pandas as pd
import numpy as np
from websocket import WebSocketApp

from binance_config import BinanceConfig


class BinanceClient:
    def __init__(self, config: BinanceConfig):
        self.cfg = config
        self.base = config.base_url
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": config.api_key})

    def _sign(self, params: dict) -> dict:
        params["timestamp"] = int(time.time() * 1000)
        query = urlencode(params)
        sig = hmac.new(
            self.cfg.api_secret.encode(), query.encode(), hashlib.sha256
        ).hexdigest()
        params["signature"] = sig
        return params

    def _get(self, path: str, params: dict = None, signed: bool = False) -> dict:
        params = params or {}
        if signed:
            params = self._sign(params)
        r = self.session.get(f"{self.base}{path}", params=params)
        r.raise_for_status()
        return r.json()

    def _post(self, path: str, params: dict = None, signed: bool = True) -> dict:
        params = params or {}
        if signed:
            params = self._sign(params)
        r = self.session.post(f"{self.base}{path}", params=params)
        r.raise_for_status()
        return r.json()

    def _delete(self, path: str, params: dict = None) -> dict:
        params = params or {}
        params = self._sign(params)
        r = self.session.delete(f"{self.base}{path}", params=params)
        r.raise_for_status()
        return r.json()

    # ---- Market data (public) ----

    def get_klines(self, symbol: str = None, interval: str = None,
                   limit: int = 1000) -> pd.DataFrame:
        symbol = symbol or self.cfg.symbol
        interval = interval or self.cfg.kline_interval
        data = self._get("/fapi/v1/klines", {
            "symbol": symbol, "interval": interval, "limit": limit
        })
        df = pd.DataFrame(data, columns=[
            "Open_time", "Open", "High", "Low", "Close", "Volume",
            "Close_time", "Quote_volume", "Trades", "Taker_buy_vol",
            "Taker_buy_quote_vol", "Ignore"
        ])
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            df[col] = df[col].astype(float)
        df["Open_time"] = pd.to_datetime(df["Open_time"], unit="ms")
        df.set_index("Open_time", inplace=True)
        return df

    def get_price(self, symbol: str = None) -> float:
        symbol = symbol or self.cfg.symbol
        data = self._get("/fapi/v1/ticker/price", {"symbol": symbol})
        return float(data["price"])

    def get_exchange_info(self, symbol: str = None) -> dict:
        symbol = symbol or self.cfg.symbol
        data = self._get("/fapi/v1/exchangeInfo")
        for s in data["symbols"]:
            if s["symbol"] == symbol:
                return s
        return {}

    def get_step_size(self, symbol: str = None) -> tuple:
        info = self.get_exchange_info(symbol)
        for f in info.get("filters", []):
            if f["filterType"] == "LOT_SIZE":
                return float(f["stepSize"]), float(f["minQty"]), float(f["maxQty"])
        return 0.001, 0.001, 1000

    def get_tick_size(self, symbol: str = None) -> float:
        info = self.get_exchange_info(symbol)
        for f in info.get("filters", []):
            if f["filterType"] == "PRICE_FILTER":
                return float(f["tickSize"])
        return 0.1

    # ---- Account (signed) ----

    def get_balance(self) -> float:
        data = self._get("/fapi/v2/account", signed=True)
        for asset in data["assets"]:
            if asset["asset"] == "USDT":
                return float(asset["availableBalance"])
        return 0.0

    def get_positions(self, symbol: str = None) -> list:
        symbol = symbol or self.cfg.symbol
        data = self._get("/fapi/v2/positionRisk", signed=True)
        return [p for p in data if p["symbol"] == symbol and float(p["positionAmt"]) != 0]

    def get_position_amt(self, symbol: str = None) -> float:
        positions = self.get_positions(symbol)
        if not positions:
            return 0.0
        return float(positions[0]["positionAmt"])

    # ---- Trading ----

    def set_leverage(self, leverage: int = None, symbol: str = None):
        leverage = leverage or self.cfg.leverage
        symbol = symbol or self.cfg.symbol
        return self._post("/fapi/v1/leverage", {"symbol": symbol, "leverage": leverage})

    def set_margin_type(self, margin_type: str = None, symbol: str = None):
        margin_type = margin_type or self.cfg.margin_type
        symbol = symbol or self.cfg.symbol
        try:
            return self._post("/fapi/v1/marginType", {
                "symbol": symbol, "marginType": margin_type
            })
        except requests.exceptions.HTTPError as e:
            # -4046: No need to change margin type
            if "-4046" in str(e):
                return {"msg": "already set"}
            raise

    def market_open_long(self, qty: float, symbol: str = None) -> dict:
        symbol = symbol or self.cfg.symbol
        step, min_qty, max_qty = self.get_step_size(symbol)
        qty = self._round_step(qty, step)
        qty = max(min_qty, min(qty, max_qty))
        return self._post("/fapi/v1/order", {
            "symbol": symbol, "side": "BUY", "type": "MARKET",
            "quantity": qty,
        })

    def market_open_short(self, qty: float, symbol: str = None) -> dict:
        symbol = symbol or self.cfg.symbol
        step, min_qty, max_qty = self.get_step_size(symbol)
        qty = self._round_step(qty, step)
        qty = max(min_qty, min(qty, max_qty))
        return self._post("/fapi/v1/order", {
            "symbol": symbol, "side": "SELL", "type": "MARKET",
            "quantity": qty,
        })

    def market_close_long(self, qty: float = None, symbol: str = None) -> dict:
        symbol = symbol or self.cfg.symbol
        if qty is None:
            qty = abs(self.get_position_amt(symbol))
        if qty <= 0:
            return {"msg": "no position"}
        step, _, _ = self.get_step_size(symbol)
        qty = self._round_step(qty, step)
        return self._post("/fapi/v1/order", {
            "symbol": symbol, "side": "SELL", "type": "MARKET",
            "quantity": qty, "reduceOnly": "true",
        })

    def market_close_short(self, qty: float = None, symbol: str = None) -> dict:
        symbol = symbol or self.cfg.symbol
        if qty is None:
            qty = abs(self.get_position_amt(symbol))
        if qty <= 0:
            return {"msg": "no position"}
        step, _, _ = self.get_step_size(symbol)
        qty = self._round_step(qty, step)
        return self._post("/fapi/v1/order", {
            "symbol": symbol, "side": "BUY", "type": "MARKET",
            "quantity": qty, "reduceOnly": "true",
        })

    def close_all(self, symbol: str = None):
        amt = self.get_position_amt(symbol)
        if amt > 0:
            return self.market_close_long(symbol=symbol)
        elif amt < 0:
            return self.market_close_short(symbol=symbol)
        return {"msg": "no position"}

    def cancel_all(self, symbol: str = None):
        symbol = symbol or self.cfg.symbol
        return self._delete("/fapi/v1/allOpenOrders", {"symbol": symbol})

    # ---- Helpers ----

    @staticmethod
    def _round_step(qty: float, step: float) -> float:
        precision = len(str(step).rstrip('0').split('.')[-1])
        return round(qty - (qty % step), precision)

    def setup(self):
        """Set leverage and margin type. Call once at startup."""
        print(f"[exchange] Setting leverage={self.cfg.leverage}x")
        self.set_leverage()
        print(f"[exchange] Setting margin type={self.cfg.margin_type}")
        self.set_margin_type()
        balance = self.get_balance()
        print(f"[exchange] Balance: {balance:.2f} USDT")
        return balance
