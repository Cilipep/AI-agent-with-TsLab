#!/usr/bin/env python3
"""Бэктестинг стратегий на исторических данных."""

import sys
import time
from datetime import datetime
from exchanges import get_client
from indicators import compute_all
import pandas as pd
import numpy as np


class Backtester:
    def __init__(self, df: pd.DataFrame, initial_capital: float = 10000):
        self.df = df.copy()
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position = 0
        self.trades = []
        self.equity_curve = []

    def run_sma_cross(self, fast: int = 20, slow: int = 50, sl_pct: float = 2.0, tp_pct: float = 4.0):
        df = self.df.copy()
        df["sma_fast"] = df["close"].rolling(window=fast).mean()
        df["sma_slow"] = df["close"].rolling(window=slow).mean()
        df.dropna(inplace=True)

        for i in range(1, len(df)):
            price = df["close"].iloc[i]

            if self.position == 0:
                if df["sma_fast"].iloc[i] > df["sma_slow"].iloc[i] and df["sma_fast"].iloc[i-1] <= df["sma_slow"].iloc[i-1]:
                    self.position = 1
                    self.entry_price = price
                    self.entry_time = df["timestamp"].iloc[i]
                    self.sl = price * (1 - sl_pct / 100)
                    self.tp = price * (1 + tp_pct / 100)

            elif self.position == 1:
                if price <= self.sl:
                    pnl = (price - self.entry_price) / self.entry_price * self.capital
                    self.capital += pnl
                    self.trades.append({"type": "long", "entry": self.entry_price, "exit": price, "pnl": pnl, "result": "SL", "time": str(self.entry_time)})
                    self.position = 0
                elif price >= self.tp:
                    pnl = (price - self.entry_price) / self.entry_price * self.capital
                    self.capital += pnl
                    self.trades.append({"type": "long", "entry": self.entry_price, "exit": price, "pnl": pnl, "result": "TP", "time": str(self.entry_time)})
                    self.position = 0

            self.equity_curve.append(self.capital)

        return self._stats()

    def run_rsi(self, period: int = 14, oversold: int = 30, overbought: int = 70, sl_pct: float = 2.0, tp_pct: float = 4.0):
        df = self.df.copy()
        delta = df["close"].diff()
        gain = delta.clip(lower=0).ewm(alpha=1/period).mean()
        loss = (-delta.clip(upper=0)).ewm(alpha=1/period).mean()
        df["rsi"] = 100 - (100 / (1 + gain / loss))
        df.dropna(inplace=True)

        for i in range(1, len(df)):
            price = df["close"].iloc[i]

            if self.position == 0:
                if df["rsi"].iloc[i] < oversold:
                    self.position = 1
                    self.entry_price = price
                    self.entry_time = df["timestamp"].iloc[i]
                    self.sl = price * (1 - sl_pct / 100)
                    self.tp = price * (1 + tp_pct / 100)

            elif self.position == 1:
                if price <= self.sl or price >= self.tp or df["rsi"].iloc[i] > overbought:
                    pnl = (price - self.entry_price) / self.entry_price * self.capital
                    self.capital += pnl
                    result = "SL" if price <= self.sl else ("TP" if price >= self.tp else "RSI_EXIT")
                    self.trades.append({"type": "long", "entry": self.entry_price, "exit": price, "pnl": pnl, "result": result, "time": str(self.entry_time)})
                    self.position = 0

            self.equity_curve.append(self.capital)

        return self._stats()

    def run_macd(self, fast: int = 12, slow: int = 26, signal: int = 9, sl_pct: float = 2.0, tp_pct: float = 4.0):
        df = self.df.copy()
        ema_fast = df["close"].ewm(span=fast).mean()
        ema_slow = df["close"].ewm(span=slow).mean()
        df["macd"] = ema_fast - ema_slow
        df["macd_signal"] = df["macd"].ewm(span=signal).mean()
        df.dropna(inplace=True)

        for i in range(1, len(df)):
            price = df["close"].iloc[i]

            if self.position == 0:
                if df["macd"].iloc[i] > df["macd_signal"].iloc[i] and df["macd"].iloc[i-1] <= df["macd_signal"].iloc[i-1]:
                    self.position = 1
                    self.entry_price = price
                    self.entry_time = df["timestamp"].iloc[i]
                    self.sl = price * (1 - sl_pct / 100)
                    self.tp = price * (1 + tp_pct / 100)

            elif self.position == 1:
                if price <= self.sl:
                    pnl = (price - self.entry_price) / self.entry_price * self.capital
                    self.capital += pnl
                    self.trades.append({"type": "long", "entry": self.entry_price, "exit": price, "pnl": pnl, "result": "SL", "time": str(self.entry_time)})
                    self.position = 0
                elif price >= self.tp:
                    pnl = (price - self.entry_price) / self.entry_price * self.capital
                    self.capital += pnl
                    self.trades.append({"type": "long", "entry": self.entry_price, "exit": price, "pnl": pnl, "result": "TP", "time": str(self.entry_time)})
                    self.position = 0
                elif df["macd"].iloc[i] < df["macd_signal"].iloc[i] and df["macd"].iloc[i-1] >= df["macd_signal"].iloc[i-1]:
                    pnl = (price - self.entry_price) / self.entry_price * self.capital
                    self.capital += pnl
                    self.trades.append({"type": "long", "entry": self.entry_price, "exit": price, "pnl": pnl, "result": "EXIT", "time": str(self.entry_time)})
                    self.position = 0

            self.equity_curve.append(self.capital)

        return self._stats()

    def _stats(self):
        if not self.trades:
            return {"error": "No trades"}

        wins = [t for t in self.trades if t["pnl"] > 0]
        losses = [t for t in self.trades if t["pnl"] <= 0]

        total_pnl = sum(t["pnl"] for t in self.trades)
        win_rate = len(wins) / len(self.trades) * 100 if self.trades else 0
        avg_win = np.mean([t["pnl"] for t in wins]) if wins else 0
        avg_loss = np.mean([abs(t["pnl"]) for t in losses]) if losses else 0
        profit_factor = sum(t["pnl"] for t in wins) / sum(abs(t["pnl"]) for t in losses) if losses else float("inf")

        max_dd = 0
        peak = self.initial_capital
        for eq in self.equity_curve:
            if eq > peak:
                peak = eq
            dd = (peak - eq) / peak * 100
            if dd > max_dd:
                max_dd = dd

        return {
            "initial_capital": self.initial_capital,
            "final_capital": round(self.capital, 2),
            "total_pnl": round(total_pnl, 2),
            "pnl_pct": f"{(total_pnl / self.initial_capital) * 100:+.2f}%",
            "total_trades": len(self.trades),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": f"{win_rate:.1f}%",
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
            "profit_factor": round(profit_factor, 2),
            "max_drawdown": f"{max_dd:.2f}%",
            "trades": self.trades,
        }


def run_backtest(symbol: str, interval: str, strategy: str = "sma", exchange: str = "binance", limit: int = 500) -> dict:
    client = get_client(exchange)
    df = client.fetch_klines(symbol, interval, limit)

    if df.empty or len(df) < 50:
        return {"error": "Not enough data"}

    bt = Backtester(df)

    if strategy == "sma":
        stats = bt.run_sma_cross()
    elif strategy == "rsi":
        stats = bt.run_rsi()
    elif strategy == "macd":
        stats = bt.run_macd()
    else:
        stats = bt.run_sma_cross()

    stats["symbol"] = symbol
    stats["interval"] = interval
    stats["strategy"] = strategy
    stats["candles"] = len(df)

    return stats


def format_backtest(stats: dict) -> str:
    if "error" in stats:
        return f"Ошибка: {stats['error']}"

    lines = []
    lines.append(f"{'=' * 60}")
    lines.append(f"  БЭКТЕСТ: {stats['symbol']} ({stats['interval']})")
    lines.append(f"  Стратегия: {stats['strategy'].upper()} | Свечей: {stats['candles']}")
    lines.append(f"{'=' * 60}")
    lines.append(f"")
    lines.append(f"  Капитал:    {stats['initial_capital']:,.2f} → {stats['final_capital']:,.2f}")
    lines.append(f"  PnL:        {stats['total_pnl']:+,.2f} ({stats['pnl_pct']})")
    lines.append(f"  Сделок:     {stats['total_trades']} (Win: {stats['wins']}, Loss: {stats['losses']})")
    lines.append(f"  Win Rate:   {stats['win_rate']}")
    lines.append(f"  Avg Win:    {stats['avg_win']:+,.2f}")
    lines.append(f"  Avg Loss:   {stats['avg_loss']:,.2f}")
    lines.append(f"  Profit Factor: {stats['profit_factor']}")
    lines.append(f"  Max Drawdown:  {stats['max_drawdown']}")
    lines.append(f"")
    lines.append(f"{'=' * 60}")

    if stats["trades"]:
        lines.append(f"  Последние 5 сделок:")
        for t in stats["trades"][-5:]:
            emoji = "🟢" if t["pnl"] > 0 else "🔴"
            lines.append(f"    {emoji} {t['time'][:16]} | Entry: {t['entry']:,.2f} → Exit: {t['exit']:,.2f} | PnL: {t['pnl']:+,.2f} ({t['result']})")

    return "\n".join(lines)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Бэктестинг стратегий")
    parser.add_argument("--symbol", "-s", default="BTCUSDT")
    parser.add_argument("--interval", "-i", default="1h")
    parser.add_argument("--strategy", "-t", choices=["sma", "rsi", "macd"], default="sma")
    parser.add_argument("--exchange", "-e", default="binance")
    parser.add_argument("--limit", "-l", type=int, default=500)
    parser.add_argument("--json", "-j", action="store_true")
    args = parser.parse_args()

    stats = run_backtest(args.symbol, args.interval, args.strategy, args.exchange, args.limit)

    if args.json:
        import json
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    else:
        print(format_backtest(stats))
