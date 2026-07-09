"""Live trading on Binance Futures Testnet using trained model.

Usage:
  1. Set API keys in environment or binance_config.py
  2. Ensure models/model.pt exists (train first)
  3. Run: python live_trading.py
"""
import sys
import time
import signal
import json
import numpy as np
import pandas as pd
import torch
from pathlib import Path
from datetime import datetime

from binance_config import BinanceConfig
from binance_client import BinanceClient
from config import Config
from model import build_model
from features import add_indicators, make_label
from dataset import FEATURE_COLS, TimeSeriesDataset


class LiveTrader:
    def __init__(self):
        self.cfg = Config()
        self.binance_cfg = BinanceConfig()
        self.client = BinanceClient(self.binance_cfg)
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.scaler = None
        self.running = True
        self.log_file = Path("results/live_trades.jsonl")

    def load_model(self) -> bool:
        model_path = Path("models/model.pt")
        if not model_path.exists():
            print(f"[!] Model not found: {model_path}")
            print("    Run: python main.py  (to train)")
            return False

        self.model = build_model(self.cfg, len(FEATURE_COLS))
        self.model.load_state_dict(torch.load(model_path, map_location=self.device, weights_only=True))
        self.model.to(self.device)
        self.model.eval()
        print(f"[model] Loaded {self.cfg.model_type} model on {self.device}")
        return True

    def fit_scaler(self, df: pd.DataFrame):
        """Fit scaler on recent data for consistent feature scaling."""
        from sklearn.preprocessing import StandardScaler
        cols = [c for c in FEATURE_COLS if c in df.columns]
        raw = df[cols].values.astype(np.float32)
        self.scaler = StandardScaler()
        self.scaler.fit(raw)
        print(f"[scaler] Fitted on {len(raw)} bars, {len(cols)} features")

    def get_signal(self) -> tuple:
        """
        Returns (signal, confidence, price):
          signal: 1=long, -1=short, 0=no trade
          confidence: 0-1
        """
        # Fetch recent klines
        df = self.client.get_klines(limit=self.cfg.lookback_bars)
        if len(df) < self.cfg.window + 10:
            return 0, 0, df["Close"].iloc[-1]

        # Add indicators
        df = add_indicators(df)
        df = df.dropna()

        if len(df) < self.cfg.window:
            return 0, 0, df["Close"].iloc[-1]

        # Fit scaler on this batch (in production, use pre-fitted scaler)
        if self.scaler is None:
            self.fit_scaler(df)

        # Prepare features
        cols = [c for c in FEATURE_COLS if c in df.columns]
        raw = df[cols].values.astype(np.float32)
        scaled = self.scaler.transform(raw)

        # Take last window
        window = scaled[-self.cfg.window:]
        x = torch.tensor(window, dtype=torch.float32).unsqueeze(0).to(self.device)

        # Predict
        with torch.no_grad():
            logit = self.model(x)
            prob = torch.sigmoid(logit).item()

        price = df["Close"].iloc[-1]

        if prob > self.binance_cfg.signal_threshold:
            return 1, prob, price  # long
        elif prob < (1 - self.binance_cfg.signal_threshold):
            return -1, 1 - prob, price  # short
        else:
            return 0, max(prob, 1 - prob), price

    def calc_position_size(self, balance: float, price: float) -> float:
        risk_amount = balance * self.binance_cfg.risk_per_trade
        qty = risk_amount / (self.binance_cfg.stop_loss_pct * price)
        # Cap at max_position_pct
        max_qty = (balance * self.binance_cfg.max_position_pct * self.binance_cfg.leverage) / price
        return min(qty, max_qty)

    def log_trade(self, action: str, details: dict):
        entry = {
            "time": datetime.utcnow().isoformat(),
            "action": action,
            **details,
        }
        self.log_file.parent.mkdir(exist_ok=True)
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def execute_signal(self, signal: int, confidence: float, price: float):
        current_amt = self.client.get_position_amt()
        balance = self.client.get_balance()

        # Close existing position if signal changes
        if current_amt > 0 and signal != 1:
            print(f"[trade] Closing LONG {current_amt:.4f}")
            result = self.client.close_all()
            self.log_trade("close_long", {"amt": current_amt, "result": result})

        elif current_amt < 0 and signal != -1:
            print(f"[trade] Closing SHORT {current_amt:.4f}")
            result = self.client.close_all()
            self.log_trade("close_short", {"amt": current_amt, "result": result})

        # Open new position
        if signal == 1 and current_amt <= 0:
            qty = self.calc_position_size(balance, price)
            if qty > 0:
                print(f"[trade] LONG {qty:.4f} @ ~{price:.2f} (conf={confidence:.3f})")
                result = self.client.market_open_long(qty)
                self.log_trade("open_long", {
                    "qty": qty, "price": price, "confidence": confidence,
                    "balance": balance, "result": result,
                })

        elif signal == -1 and current_amt >= 0:
            qty = self.calc_position_size(balance, price)
            if qty > 0:
                print(f"[trade] SHORT {qty:.4f} @ ~{price:.2f} (conf={confidence:.3f})")
                result = self.client.market_open_short(qty)
                self.log_trade("open_short", {
                    "qty": qty, "price": price, "confidence": confidence,
                    "balance": balance, "result": result,
                })

    def status_report(self):
        balance = self.client.get_balance()
        pos = self.client.get_position_amt()
        price = self.client.get_price()
        pos_label = "LONG" if pos > 0 else ("SHORT" if pos < 0 else "FLAT")
        print(f"[status] {datetime.now().strftime('%H:%M:%S')} | "
              f"Balance: {balance:.2f} | Position: {pos_label} {pos:.4f} | "
              f"Price: {price:.2f}")

    def run(self):
        print("=" * 60)
        print("  BINANCE FUTURES TESTNET — LIVE TRADING")
        print("=" * 60)

        if not self.binance_cfg.validate():
            return

        if not self.load_model():
            return

        # Setup exchange
        try:
            self.client.setup()
        except Exception as e:
            print(f"[!] Exchange setup failed: {e}")
            return

        # Handle Ctrl+C
        def stop(sig, frame):
            print("\n[!] Stopping...")
            self.running = False
        signal.signal(signal.SIGINT, stop)
        signal.signal(signal.SIGTERM, stop)

        print(f"[live] Starting loop ({self.binance_cfg.polling_interval_sec}s interval)")
        print(f"[live] Symbol: {self.binance_cfg.symbol}")
        print(f"[live] Threshold: {self.binance_cfg.signal_threshold}")
        print(f"[live] Leverage: {self.binance_cfg.leverage}x")
        print()

        cycle = 0
        while self.running:
            cycle += 1
            try:
                signal_val, confidence, price = self.get_signal()
                signal_label = {1: "LONG", -1: "SHORT", 0: "FLAT"}[signal_val]

                print(f"[#{cycle:04d}] Signal: {signal_label} "
                      f"(conf={confidence:.3f}) Price={price:.2f}")

                self.execute_signal(signal_val, confidence, price)
                self.status_report()

            except Exception as e:
                print(f"[!] Error in cycle {cycle}: {e}")

            # Wait for next interval
            for _ in range(self.binance_cfg.polling_interval_sec):
                if not self.running:
                    break
                time.sleep(1)

        # Cleanup
        print("[live] Closing all positions...")
        self.client.close_all()
        self.client.cancel_all()
        print("[live] Stopped.")


if __name__ == "__main__":
    trader = LiveTrader()
    trader.run()
